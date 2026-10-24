"""Check the Virtual Vial on 123 real household fridges (Bangkok dataset).

The twin sees only the middle-shelf air temperature, exactly as it would see a logger. Its vaccine-temperature
estimate is compared with the measured product temperature (meat-simulating gel probe, recorded in 0.5 °C steps).
Also fits each fridge's own product time constant tau, to check the 60-minute fleet prior.

Usage:  python scripts/validate_bangkok.py
Writes: results/bangkok_validation.json, results/bangkok_per_fridge.csv
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_ROOT))
RESULTS = ML_ROOT / "results"

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from thermotwin.datasets import load_bangkok  # noqa: E402
from thermotwin.twin import TAU_PRIOR, run_twin  # noqa: E402

WARMUP = 18          # ignore the first 3 h while the twin settles
TAUS = np.array([10, 20, 30, 45, 60, 90, 120, 180, 240, 360, 480, 720], dtype=float)


def grid(log: pd.DataFrame, col: str) -> np.ndarray:
    return log.pivot(index="unit", columns="tick", values=col).to_numpy()


def main() -> None:
    log, units = load_bangkok()
    air, prod = grid(log, "air_meas"), grid(log, "prod_true")
    n = air.shape[0]
    print(f"{n} fridges, {air.shape[1]} readings each (10-minute steps)")

    # 1) Twin with the fleet prior, as deployed
    tw = run_twin(air, np.full(n, TAU_PRIOR["DOMESTIC"]))
    sl = slice(WARMUP, None)
    err_vial = np.abs(tw["vial"][:, sl] - prod[:, sl])
    err_air = np.abs(air[:, sl] - prod[:, sl])
    z = (prod[:, sl] - tw["vial"][:, sl]) / np.sqrt(tw["vial_sd"][:, sl] ** 2 + 0.145 ** 2)   # 0.145 = 0.5 °C step

    # 2) Best tau per fridge (grid search on the same twin)
    maes = np.stack([np.nanmean(np.abs(run_twin(air, np.full(n, t))["vial"][:, sl] - prod[:, sl]), axis=1) for t in TAUS], 1)
    best = TAUS[maes.argmin(1)]
    best_mae = maes.min(1)

    # 3) Where the product sits relative to the air on average (shelf position offset)
    offset = np.nanmean(prod[:, sl] - tw["vial"][:, sl], axis=1)

    # 4) One-day calibration at installation: learn the offset on day 1, score days 2-5 only
    day1 = slice(WARMUP, 144)
    rest = slice(144, None)
    off1 = np.nanmean(prod[:, day1] - tw["vial"][:, day1], axis=1, keepdims=True)
    cal_vial = tw["vial"][:, rest] + off1
    err_cal = np.abs(cal_vial - prod[:, rest])
    err_air_rest = np.abs(air[:, rest] - prod[:, rest])
    err_vial_rest = np.abs(tw["vial"][:, rest] - prod[:, rest])
    z_cal = (prod[:, rest] - cal_vial) / np.sqrt(tw["vial_sd"][:, rest] ** 2 + 0.145 ** 2 + 0.3 ** 2)  # + position noise

    per = pd.DataFrame({"fridge": units["name"], "type": units["fridge_type"],
                        "mae_vial_prior": np.nanmean(err_vial, 1), "mae_raw_air": np.nanmean(err_air, 1),
                        "best_tau_min": best, "mae_vial_best_tau": best_mae, "mean_offset": offset})
    summary = dict(
        fridges=int(n), readings_per_fridge=int(air.shape[1]), tau_prior_min=TAU_PRIOR["DOMESTIC"],
        mae_vial_prior=float(np.nanmean(err_vial)), mae_raw_air=float(np.nanmean(err_air)),
        median_fridge_mae_vial=float(per.mae_vial_prior.median()), median_fridge_mae_air=float(per.mae_raw_air.median()),
        fridges_where_vial_beats_air=int((per.mae_vial_prior < per.mae_raw_air).sum()),
        within_2sd_share=float(np.nanmean(np.abs(z) <= 2)),
        mae_vial_best_tau=float(np.nanmean(best_mae)),
        best_tau_median_min=float(np.median(best)), best_tau_iqr_min=[float(np.percentile(best, 25)), float(np.percentile(best, 75))],
        mean_abs_offset=float(np.nanmean(np.abs(offset))),
        days2to5_mae_raw_air=float(np.nanmean(err_air_rest)),
        days2to5_mae_vial=float(np.nanmean(err_vial_rest)),
        days2to5_mae_vial_after_day1_calibration=float(np.nanmean(err_cal)),
        days2to5_median_fridge_mae_calibrated=float(np.median(np.nanmean(err_cal, 1))),
        days2to5_within_2sd_calibrated=float(np.nanmean(np.abs(z_cal) <= 2)),
        quantisation_floor=0.145,
        note="Product probe recorded in 0.5 °C steps; errors below ~0.15 °C are not resolvable.")
    RESULTS.mkdir(exist_ok=True)
    per.to_csv(RESULTS / "bangkok_per_fridge.csv", index=False)
    (RESULTS / "bangkok_validation.json").write_text(json.dumps(summary, indent=2))
    for k, v in summary.items():
        print(f"{k:32s} {v}")


if __name__ == "__main__":
    main()
