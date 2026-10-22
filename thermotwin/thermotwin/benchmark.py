"""Alert policies and the Replay Benchmark.

All policies see only the logged air temperature (plus, for P3, the twin and model built from it).
  P0  simple threshold: one reading <= 0 °C
  P1  WHO PQS freeze alarm: air <= -0.5 °C for 60 minutes (6 consecutive readings)
  P2  early-warning rule (Nexleaf-style): air <= 2 °C for 30 minutes (3 readings)
  P3  ThermoTwin: calibrated 2-hour freeze risk >= threshold
Lead time is measured against the reference event: the true vaccine temperature crossing 0 °C before a freeze.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

WINDOW_BEFORE = 36   # ticks (6 h): an alert this far before the reference counts as an early warning for it
WINDOW_AFTER = 12    # ticks (2 h): an alert up to 2 h late still counts as catching the event (late)


def _consecutive(mask: np.ndarray, n: int) -> np.ndarray:
    """True where the last n values (per row) are all True."""
    out = np.zeros_like(mask)
    run = np.zeros(mask.shape[0], dtype=int)
    for t in range(mask.shape[1]):
        run = np.where(mask[:, t], run + 1, 0)
        out[:, t] = run >= n
    return out


def policy_signals(air: np.ndarray, risk12: np.ndarray | None = None, threshold: float = 0.5,
                   kind: str = "freeze") -> dict[str, np.ndarray]:
    """Boolean alarm-active arrays (n_units, n_ticks) for each policy."""
    a = np.nan_to_num(air, nan=5.0)
    if kind == "freeze":
        sig = {
            "P0 threshold <= 0 °C": a <= 0.0,
            "P1 WHO (<= -0.5 °C for 60 min)": _consecutive(a <= -0.5, 6),
            "P2 early rule (<= 2 °C for 30 min)": _consecutive(a <= 2.0, 3),
        }
    else:
        sig = {
            "P0 threshold > 8 °C": a > 8.0,
            "P1 WHO (> 8 °C for 10 h)": _consecutive(a > 8.0, 60),
            "P2 early rule (> 8 °C for 30 min)": _consecutive(a > 8.0, 3),
        }
    if risk12 is not None:
        on = _consecutive(risk12 >= threshold, 2)   # debounce: two readings in a row above the threshold
        hold = _consecutive(risk12 < threshold / 2, 3)   # switch off after 30 min well below the threshold
        state = np.zeros_like(on)
        cur = np.zeros(on.shape[0], dtype=bool)
        for t in range(on.shape[1]):
            cur = np.where(on[:, t], True, np.where(hold[:, t], False, cur))
            state[:, t] = cur
        sig["P3 ThermoTwin"] = state
    return sig


REPEAT_GAP = 36   # ticks (6 h): a new alert on the same fridge within this gap is the same incident (one SMS)


def episodes(active: np.ndarray) -> list[tuple[int, int]]:
    """(unit, start_tick) for each alert incident. Applied identically to every policy."""
    starts = np.argwhere(active[:, 1:] & ~active[:, :-1])
    raw = sorted([(int(u), 0) for u in np.nonzero(active[:, 0])[0]] + [(int(u), int(t) + 1) for u, t in starts])
    out, last = [], {}
    for u, t in raw:
        if u in last and t - last[u] < REPEAT_GAP:
            continue
        out.append((u, t))
        last[u] = t
    return out


def score(active: np.ndarray, events: pd.DataFrame, fridge_months: float) -> dict:
    eps = episodes(active)
    by_unit: dict[int, list[int]] = {}
    for u, t in eps:
        by_unit.setdefault(u, []).append(t)
    leads, caught, matched = [], 0, set()
    for ev in events.itertuples():
        starts = [t for t in by_unit.get(ev.unit, []) if ev.ref_tick - WINDOW_BEFORE <= t <= ev.ref_tick + WINDOW_AFTER]
        # An alert already active when the window opens also counts
        if active[ev.unit, max(ev.ref_tick - WINDOW_BEFORE, 0)]:
            starts.append(max(ev.ref_tick - WINDOW_BEFORE, 0))
        if starts:
            first = min(starts)
            caught += 1
            leads.append((ev.ref_tick - first) * 10)
            matched.update((ev.unit, t) for t in starts)
    false_eps = [e for e in eps if e not in matched and not any(
        ev.unit == e[0] and ev.ref_tick - WINDOW_BEFORE <= e[1] <= ev.end_tick + 18 for ev in events.itertuples())]
    leads = np.array(leads)
    return {
        "events": len(events),
        "caught": caught,
        "recall": caught / max(len(events), 1),
        "lead_median_min": float(np.median(leads)) if leads.size else np.nan,
        "lead_p25_min": float(np.percentile(leads, 25)) if leads.size else np.nan,
        "warned_before_share": float((leads > 0).mean()) if leads.size else np.nan,
        "false_alerts_per_fridge_month": len(false_eps) / fridge_months,
    }


def run_benchmark(air: np.ndarray, events: pd.DataFrame, risk12: np.ndarray | None, threshold: float,
                  days: float, kind: str = "freeze") -> pd.DataFrame:
    fm = air.shape[0] * days / 30.0
    rows = []
    for name, active in policy_signals(air, risk12, threshold, kind).items():
        rows.append({"policy": name, **score(active, events, fm)})
    return pd.DataFrame(rows)


def pick_threshold(air: np.ndarray, events: pd.DataFrame, risk12: np.ndarray, days: float,
                   budget: float = 1.0, kind: str = "freeze") -> float:
    """Highest-recall threshold whose false alerts stay within the budget (false alerts per fridge-month)."""
    best, best_key = 0.9, (-1.0, -1.0)
    fm = air.shape[0] * days / 30.0
    for th in np.round(np.arange(0.05, 0.95, 0.05), 2):
        s = score(policy_signals(air, risk12, th, kind)["P3 ThermoTwin"], events, fm)
        if s["false_alerts_per_fridge_month"] <= budget:
            key = (s["recall"], np.nan_to_num(s["lead_median_min"], nan=-1e9))
            if key > best_key:
                best, best_key = float(th), key
    return best
