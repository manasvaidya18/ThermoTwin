"""Deep-learning baseline vs ThermoTwin on the same fleet, splits, calibration, budget and benchmark.

Usage:  python run_baselines.py [--seed 0] [--kinds freeze heat]
"""
from __future__ import annotations

import argparse
import os
import pickle
import time
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from thermotwin.benchmark import pick_threshold, run_benchmark  # noqa: E402
from thermotwin.deep import LSTMBaseline, time_inference  # noqa: E402
from thermotwin.labels import find_events, ticks_to_next_onset  # noqa: E402
from thermotwin.pipeline import build_fleet, train_risk  # noqa: E402
from thermotwin.simulator import FleetConfig  # noqa: E402

OUT = Path(__file__).parent / "outputs"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--kinds", nargs="+", default=["freeze", "heat"])
    ap.add_argument("--epochs", type=int, default=4)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    pd.set_option("display.width", 200)

    fleet = build_fleet(FleetConfig(n_units=240, days=21, seed=args.seed))
    n, T, days = fleet.n, fleet.T, fleet.cfg.days
    air = fleet.log.sort_values(["unit", "tick"])["air_meas"].to_numpy().reshape(n, T)
    is_dom = fleet.units["cls"].eq("DOMESTIC").to_numpy()
    rows = []
    for kind in args.kinds:
        events = find_events(fleet.log.attrs["prod_min"], kind)
        to_next, in_event = ticks_to_next_onset(events, n, T)
        st, sv = fleet.split["test"], fleet.split["val"]

        # ThermoTwin (twin + LightGBM)
        t0 = time.time()
        tt = train_risk(fleet, kind, args.seed)
        lgb_train = time.time() - t0
        tt_row = tt["bench"][tt["bench"]["policy"] == "P3 ThermoTwin"].iloc[0].to_dict()
        test = fleet.part("test")
        lgb_infer = time_inference(tt["model"].predict, test)
        lgb_size = len(pickle.dumps(tt["model"]))

        # LSTM on raw air
        rng = np.random.default_rng(args.seed)
        lstm = LSTMBaseline(seed=args.seed, epochs=args.epochs).fit(air, is_dom, fleet.split["train"], to_next, in_event, rng)
        raw_v = lstm.raw_risk(air, is_dom, sv)
        lstm.calibrate(raw_v, sv, to_next, in_event)
        th = pick_threshold(air[sv], fleet.remap(events, sv), lstm.risk(raw_v), days, budget=0.8, kind=kind)
        raw_t = lstm.raw_risk(air, is_dom, st)
        b = run_benchmark(air[st], fleet.remap(events, st), lstm.risk(raw_t), th, days, kind)
        lstm_row = b[b["policy"] == "P3 ThermoTwin"].iloc[0].to_dict()
        np.savez_compressed(OUT / f"risk_{kind}_seed{args.seed}.npz", lstm=lstm.risk(raw_t),
                            thermotwin=fleet.grid(tt["pred_test"], "risk12", st), air=air[st])
        fleet.remap(events, st).to_csv(OUT / f"events_{kind}_seed{args.seed}.csv", index=False)
        lstm_infer = time_inference(lstm.raw_risk, air, is_dom, st, repeats=1)
        lstm_size = len(pickle.dumps(lstm.net.state_dict()))

        base = tt["bench"][tt["bench"]["policy"].str.startswith(("P1", "P2"))]
        for _, r in base.iterrows():
            rows.append(dict(kind=kind, model=r["policy"], caught=f"{int(r['caught'])}/{int(r['events'])}",
                             lead_median_min=r["lead_median_min"], false_per_fridge_month=r["false_alerts_per_fridge_month"],
                             train_s=np.nan, infer_s=np.nan, size_kb=np.nan))
        rows.append(dict(kind=kind, model="LSTM (raw air, no physics)", caught=f"{int(lstm_row['caught'])}/{int(lstm_row['events'])}",
                         lead_median_min=lstm_row["lead_median_min"], false_per_fridge_month=lstm_row["false_alerts_per_fridge_month"],
                         train_s=lstm.train_seconds, infer_s=lstm_infer, size_kb=lstm_size / 1024))
        rows.append(dict(kind=kind, model="ThermoTwin (twin + LightGBM)", caught=f"{int(tt_row['caught'])}/{int(tt_row['events'])}",
                         lead_median_min=tt_row["lead_median_min"], false_per_fridge_month=tt_row["false_alerts_per_fridge_month"],
                         train_s=lgb_train, infer_s=lgb_infer, size_kb=lgb_size / 1024))
        print(f"[{kind}] done; LSTM {lstm.n_params:,} parameters, threshold {th:.2f}")

    res = pd.DataFrame(rows)
    print("\n=== Model comparison: held-out fridges (simulated data, seed %d) ===" % args.seed)
    print(res.round(2).to_string(index=False))
    res.to_csv(OUT / f"baselines_seed{args.seed}.csv", index=False)
    print(f"\nSaved outputs/baselines_seed{args.seed}.csv")


if __name__ == "__main__":
    main()
