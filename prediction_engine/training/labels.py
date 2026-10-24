"""Event labels from simulator ground truth (never from ThermoTwin's own rules).

Freeze event: true vaccine temperature <= -0.5 °C for at least 60 minutes. Onset = first minute of that run.
Reference time for lead time: the minute the true vaccine temperature last crossed 0 °C before onset.
Heat event: true vaccine temperature > 8 °C for at least 60 minutes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LOG_EVERY = 10


def _runs(mask: np.ndarray, min_len: int) -> list[tuple[int, int]]:
    """(start, end) index pairs of True runs at least min_len long."""
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    return [(s, e) for s, e in zip(starts, ends) if e - s >= min_len]


def find_events(prod_min: np.ndarray, kind: str = "freeze", min_len: int = 60) -> pd.DataFrame:
    """Events per unit from the 1-minute true vaccine temperature array (n_units, n_minutes)."""
    rows = []
    for u in range(prod_min.shape[0]):
        p = prod_min[u]
        mask = p <= -0.5 if kind == "freeze" else p > 8.0
        for s, e in _runs(mask, min_len):
            if kind == "freeze":
                above = np.nonzero(p[:s] > 0.0)[0]
                ref = int(above[-1] + 1) if above.size else s
            else:
                below = np.nonzero(p[:s] <= 8.0)[0]
                ref = int(below[-1] + 1) if below.size else s
            rows.append(dict(unit=u, kind=kind, onset_min=int(s), end_min=int(e), ref_min=ref,
                             onset_tick=int(s) // LOG_EVERY, end_tick=int(e) // LOG_EVERY, ref_tick=ref // LOG_EVERY))
    return pd.DataFrame(rows, columns=["unit", "kind", "onset_min", "end_min", "ref_min",
                                       "onset_tick", "end_tick", "ref_tick"])


def ticks_to_next_onset(events: pd.DataFrame, n_units: int, n_ticks: int) -> tuple[np.ndarray, np.ndarray]:
    """For every (unit, tick): ticks until the next event onset (inf if none), and whether an event is in progress."""
    to_next = np.full((n_units, n_ticks), np.inf)
    in_event = np.zeros((n_units, n_ticks), dtype=bool)
    for u, g in events.groupby("unit"):
        nxt = np.inf
        onsets = dict(zip(g.onset_tick, g.end_tick))
        for t in range(n_ticks - 1, -1, -1):
            if t in onsets:
                nxt = t
            to_next[u, t] = nxt - t
        for s, e in onsets.items():
            in_event[u, s:e + 18] = True   # event plus a 3-hour recovery window
    return to_next, in_event


# ---- Cause labels (from the injected fault) -----------------------------------------------------------------
import pandas as pd  # noqa: E402

GROUP = {"thermostat_cold": "cooling_too_hard", "relay_stuck_on": "cooling_too_hard", "power_cut": "power_cut",
         "compressor_wear": "weak_cooling", "gasket_leak": "weak_cooling", "sensor_stuck": "sensor_fault",
         "sensor_drift": "sensor_fault"}


def active_fault(faults: list[list[dict]], n_units: int, n_ticks: int) -> np.ndarray:
    """(n_units, n_ticks) array of the injected fault group active at each tick ('none' if none)."""
    lab = np.full((n_units, n_ticks), "none", dtype=object)
    for u, fl in enumerate(faults):
        for f in fl:
            s, e = f["start"] // LOG_EVERY, min(f["end"] // LOG_EVERY, n_ticks)
            lab[u, s:e] = GROUP[f["kind"]]
    return lab


def manifest_mask(feat: pd.DataFrame, lab: np.ndarray) -> np.ndarray:
    """Ticks where a fault is visible in the data (or clearly normal), so the classifier learns real signatures."""
    u, t = feat["unit"].to_numpy(), feat["tick"].to_numpy()
    y = lab[u, t]
    dev = feat["mean36_dev"].abs().fillna(0).to_numpy()
    visible = (y != "none") & ((dev > 0.8) | (y == "sensor_fault") | (feat["d18"].abs().fillna(0).to_numpy() > 1.5))
    normal = (y == "none") & (dev < 0.5)
    return visible | normal
