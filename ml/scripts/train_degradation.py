"""Train the slow-loop degradation model (days until service) and add it to artifacts/models.pkl.

Simulates a longer fleet (default 300 fridges x 60 days) so gradual compressor wear and door-seal leaks have time to
develop, trains on 60% of fridges, calibrates and picks the alert threshold on 20%, and scores the last 20%.
The freeze, heat and cause models already in models.pkl are left unchanged.

Usage:  python scripts/train_degradation.py [--units 300] [--days 60] [--seed 21]
Writes: artifacts/models.pkl (adds "degradation"), results/degradation.json
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys
import time
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_ROOT))
RESULTS, ARTIFACTS = ML_ROOT / "results", ML_ROOT / "artifacts"
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import numpy as np  # noqa: E402

from thermotwin.degradation import DEG_FAULTS, DegradationModel, daily_rows, failure_days, window_features  # noqa: E402
from thermotwin.features import build_features  # noqa: E402
from thermotwin.labels import find_events  # noqa: E402
from thermotwin.simulator import FleetConfig, simulate_fleet  # noqa: E402
from thermotwin.twin import twin_frame  # noqa: E402

BUDGET = 0.5      # false maintenance alerts per unit-month
LOOKAHEAD = 14    # an alert counts as true if a degradation failure follows within this many days


def degradation_active(faults, n_units: int, n_days: int) -> np.ndarray:
    """(units, days): True from the day a compressor-wear or door-seal fault starts."""
    act = np.zeros((n_units, n_days), dtype=bool)
    for u, fl in enumerate(faults):
        for f in fl:
            if f["kind"] in DEG_FAULTS:
                act[u, f["start"] // 1440: min(n_days, f["end"] // 1440 + 1)] = True
    return act


def evaluate(days, pred, fail_day, deg, th, n_units, n_days):
    """Failures caught (and days of warning), how soon wear is flagged, and false maintenance alerts.

    A maintenance alert is false only if the unit has no degradation at all that day: flagging a wearing compressor
    that has not failed yet is the purpose of the alert.
    """
    d = days[["unit", "day"]].copy()
    d["alert"] = pred["score7"].to_numpy() >= th
    caught, warn, false_eps, failures, flagged, delay, wear_units = 0, [], 0, 0, 0, [], 0
    for u, g in d.groupby("unit"):
        g = g.sort_values("day")
        fd = fail_day[u]
        if np.isfinite(fd) and fd >= 4:
            failures += 1
            win = g[(g["day"] >= fd - LOOKAHEAD) & (g["day"] < fd)]
            if win["alert"].any():
                caught += 1
                warn.append(fd - win.loc[win["alert"], "day"].min())
        act = deg[u, g["day"].to_numpy()]
        if act.any():
            wear_units += 1
            onset = g["day"].to_numpy()[act].min()
            hits = g[(g["day"] >= onset) & g["alert"]]
            if len(hits):
                flagged += 1
                delay.append(hits["day"].min() - onset)
        false_days = g["alert"] & ~act
        starts = false_days & ~false_days.shift(1, fill_value=False)
        false_eps += int(starts.sum())
    months = n_units * n_days / 30
    return dict(failures=failures, caught=caught, median_warning_days=float(np.median(warn)) if warn else None,
                units_with_wear=wear_units, wear_flagged=flagged,
                median_days_from_wear_start_to_flag=float(np.median(delay)) if delay else None,
                false_alerts_per_unit_month=false_eps / months)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=int, default=300)
    ap.add_argument("--days", type=int, default=60)
    ap.add_argument("--seed", type=int, default=21)
    a = ap.parse_args()
    t0 = time.time()
    log, units, faults = simulate_fleet(FleetConfig(n_units=a.units, days=a.days, seed=a.seed))
    feat = build_features(log, twin_frame(log, units), units)
    w = window_features(feat)
    days = daily_rows(w)
    heat = find_events(log.attrs["prod_min"], "heat")
    fail_day = failure_days(heat, faults, a.units)
    deg = degradation_active(faults, a.units, a.days)
    print(f"simulated + features in {time.time() - t0:.0f}s; {np.isfinite(fail_day).sum()} units with a degradation failure")

    rng = np.random.default_rng(a.seed)
    perm = rng.permutation(a.units)
    split = {"train": perm[: int(0.6 * a.units)], "val": perm[int(0.6 * a.units): int(0.8 * a.units)],
             "test": perm[int(0.8 * a.units):]}
    part = {k: days[days["unit"].isin(v)].reset_index(drop=True) for k, v in split.items()}
    last_day = a.days - 1

    m = DegradationModel().fit(part["train"], fail_day, last_day)
    m.calibrate(part["val"], fail_day, last_day)
    pv = m.predict(part["val"])
    best = None
    for th in np.unique(np.round(np.quantile(pv["score7"], np.linspace(0.5, 0.995, 40)), 4)):
        r = evaluate(part["val"], pv, fail_day, deg, th, len(split["val"]), a.days)
        print(f"  val th={th:.4f} failures caught {r['caught']}/{r['failures']} warn {r['median_warning_days']} d | "
              f"wear flagged {r['wear_flagged']}/{r['units_with_wear']} after {r['median_days_from_wear_start_to_flag']} d | "
              f"false {r['false_alerts_per_unit_month']:.2f}")
        if r["false_alerts_per_unit_month"] <= BUDGET:
            key = (r["caught"], r["median_warning_days"] or 0)
            if best is None or key > best[0]:
                best = (key, th)
    m.threshold = float(best[1]) if best else 0.5
    pt = m.predict(part["test"])
    res = evaluate(part["test"], pt, fail_day, deg, m.threshold, len(split["test"]), a.days)

    # Health index: at 3-7 days before a failure vs healthy unit-days
    t = part["test"].assign(health=pt["health"].to_numpy())
    dtf = fail_day[t["unit"].to_numpy()] - t["day"].to_numpy()
    pre = t.loc[(dtf >= 3) & (dtf <= 7), "health"]
    healthy = t.loc[~deg[t["unit"].to_numpy(), t["day"].to_numpy()], "health"]
    summary = dict(units=a.units, days=a.days, threshold=m.threshold, budget_false_per_unit_month=BUDGET,
                   test=res, health_median_3to7_days_before_failure=float(pre.median()) if len(pre) else None,
                   health_median_healthy_unit_days=float(healthy.median()),
                   seconds=round(time.time() - t0))
    print(json.dumps(summary, indent=2))

    path = ARTIFACTS / "models.pkl"
    models = pickle.load(open(path, "rb"))
    models["degradation"] = m
    pickle.dump(models, open(path, "wb"))
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "degradation.json").write_text(json.dumps(summary, indent=2))
    print(f"added 'degradation' to {path}")


if __name__ == "__main__":
    main()
