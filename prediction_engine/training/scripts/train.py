"""Run the ThermoTwin core path end to end and save the trained models.

simulate a fleet -> digital twin -> features -> freeze and heat hazard models (calibrated, thresholds under the
false-alert budget) -> cause classifier -> Replay Benchmark on held-out fridges.

Usage:  python prediction_engine/training/scripts/train.py [--units 240] [--days 21] [--seed 0]
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import time
from pathlib import Path

import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[2]          # prediction_engine/
sys.path.insert(0, str(ML_ROOT.parent))               # repo root, so "import prediction_engine" works
RESULTS = ML_ROOT / "results"
ARTIFACTS = ML_ROOT / "models"
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import pandas as pd  # noqa: E402

from prediction_engine.training.pipeline import build_fleet, train_cause, train_risk  # noqa: E402
from prediction_engine.digital_twin.thermal_model import FleetConfig  # noqa: E402

OUT = RESULTS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", type=int, default=240)
    ap.add_argument("--days", type=int, default=21)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    ARTIFACTS.mkdir(exist_ok=True)
    t0 = time.time()
    pd.set_option("display.width", 180)

    fleet = build_fleet(FleetConfig(n_units=args.units, days=args.days, seed=args.seed))
    print(f"[1] simulated {fleet.n} fridges x {args.days} days, twin + features ready ({time.time() - t0:.0f}s)")

    res = {}
    for kind in ("freeze", "heat"):
        r = train_risk(fleet, kind, args.seed)
        res[kind] = r
        print(f"[2] {kind}: {r['events']} events, trained on {r['rows']:,} rows, threshold {r['threshold']:.2f} "
              f"({time.time() - t0:.0f}s)")

    cause = train_cause(fleet, args.seed)
    print(f"[3] cause classifier trained ({time.time() - t0:.0f}s)")

    bench = pd.concat([res["freeze"]["bench"], res["heat"]["bench"]], ignore_index=True)
    print("\n=== Replay Benchmark: held-out fridges (simulated data) ===")
    print(bench.round(2).to_string(index=False))

    tw = fleet.feat[fleet.feat["unit"].isin(fleet.split["test"])][["unit", "tick", "vial", "vial_sd"]]
    tm = tw.merge(fleet.log[["unit", "tick", "prod_true", "air_meas"]], on=["unit", "tick"])
    vial_mae = float((tm["vial"] - tm["prod_true"]).abs().mean())
    air_mae = float((tm["air_meas"] - tm["prod_true"]).abs().mean())
    cover = float(((tm["prod_true"] - tm["vial"]).abs() <= 2 * tm["vial_sd"]).mean())
    print(f"\nVirtual Vial error: {vial_mae:.2f} °C (raw air {air_mae:.2f} °C), 2-sigma coverage {cover:.0%}")
    print(f"Cause classifier accuracy on held-out fridges: {cause['accuracy']:.0%}")
    print("Confusion (rows = true cause, share of ticks):")
    print(cause["confusion"].round(2).to_string())
    print(f"Sensor-check rule: catches {cause['sensor_rule_recall']:.0%} of sensor-fault ticks, "
          f"fires on {cause['sensor_rule_false_rate']:.2%} of normal ticks")

    bench.to_csv(OUT / "benchmark.csv", index=False)
    summary = dict(fridges=fleet.n, days=args.days, virtual_vial_mae=vial_mae, raw_air_mae=air_mae,
                   vial_2sigma_coverage=cover, cause_accuracy=cause["accuracy"],
                   sensor_rule_recall=cause["sensor_rule_recall"], sensor_rule_false_rate=cause["sensor_rule_false_rate"],
                   thresholds={k: res[k]["threshold"] for k in res},
                   events={k: res[k]["events"] for k in res}, test_events={k: res[k]["test_events"] for k in res},
                   benchmark=bench.to_dict(orient="records"),
                   cause_confusion=cause["confusion"].round(3).to_dict())
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    models = {"freeze": res["freeze"]["model"], "heat": res["heat"]["model"], "cause": cause["model"],
              "thresholds": summary["thresholds"]}
    old_path = ARTIFACTS / "models.pkl"
    if old_path.exists():                     # keep the slow-loop model (trained separately by train_degradation.py)
        with open(old_path, "rb") as f:
            prev = pickle.load(f)
        if "degradation" in prev:
            models["degradation"] = prev["degradation"]
    with open(ARTIFACTS / "models.pkl", "wb") as f:
        pickle.dump(models, f)
    print(f"\nSaved results/benchmark.csv, results/summary.json, models/models.pkl  (total {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
