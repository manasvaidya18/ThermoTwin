"""Door-opening recovery check (rule, not ML).

From temperature alone, a normal door opening is a sharp rise in one reading that falls back within 30 minutes while
the vaccine estimate barely moves. A fault is a trend that does not recover. This rule labels the first pattern so the
UI can say "Door opening, recovering, no action needed" instead of staying silent.

Per tick (causal: uses only readings up to that tick):
  0 = nothing
  1 = spike seen, watching (up to 3 readings)
  2 = recovered: the air came back within RECOVER_BAND of its pre-spike level within 3 readings
      (shown at the recovery reading and the next two)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SPIKE_RISE = 1.5        # °C rise in one 10-minute reading
SPIKE_INNOV = 1.0       # or: the twin was surprised by at least this much upwards
VIAL_STILL = 0.3        # the vaccine estimate moved less than this during the spike
RECOVER_BAND = 1.0      # back within this of the pre-spike air temperature
WINDOW = 3              # readings allowed for recovery (30 min)
SHOW = 3                # readings the "recovered" note stays visible

NONE, WATCHING, RECOVERED = 0, 1, 2
LABELS = {NONE: "", WATCHING: "Sudden rise: watching for recovery",
          RECOVERED: "Door opening, recovering: no action needed"}


def recovery_states(air: np.ndarray, innov: np.ndarray, vial: np.ndarray) -> np.ndarray:
    """air, innov, vial: (n_units, n_ticks). Returns int states of the same shape."""
    n, T = air.shape
    a = pd.DataFrame(air.T).ffill().to_numpy().T
    d1 = np.diff(a, axis=1, prepend=a[:, :1])
    dv = np.abs(np.diff(vial, axis=1, prepend=vial[:, :1]))
    spike = ((d1 >= SPIKE_RISE) | (np.nan_to_num(innov) >= SPIKE_INNOV)) & (dv < VIAL_STILL)
    state = np.zeros((n, T), dtype=np.int8)
    for u in range(n):
        for s in np.flatnonzero(spike[u]):
            if s == 0:
                continue
            pre = a[u, s - 1]
            end = min(T, s + WINDOW + 1)
            back = np.flatnonzero(a[u, s + 1:end] <= pre + RECOVER_BAND)
            if back.size:
                r = s + 1 + back[0]
                state[u, s:r] = np.maximum(state[u, s:r], WATCHING)
                state[u, r:min(T, r + SHOW)] = RECOVERED
            else:
                state[u, s:end] = np.maximum(state[u, s:end], WATCHING)
    return state


def frame_states(feat: pd.DataFrame) -> np.ndarray:
    """recovery_states for a feature frame sorted by unit, tick (one row per unit-tick, equal lengths)."""
    f = feat.sort_values(["unit", "tick"])
    n = f["unit"].nunique()
    shape = (n, len(f) // n)
    st = recovery_states(f["air"].to_numpy().reshape(shape), f["innov"].to_numpy().reshape(shape),
                         f["vial"].to_numpy().reshape(shape))
    out = np.zeros(len(feat), dtype=np.int8)
    out[f.index.to_numpy()] = st.ravel()
    return out
