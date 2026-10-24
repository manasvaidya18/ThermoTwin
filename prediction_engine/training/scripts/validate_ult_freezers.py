"""Real-failure check of the slow loop on ultra-low temperature freezers (Danish National Biobank, Revco, -80 °C).

For each gradual fault from the service records (refrigerant leaks, compressor faults) we take the chamber temperature
for the ~2 months before the service date, resample it to 10-minute readings like a logger, and run the same
pipeline: twin -> features -> rolling 24 h window features vs the freezer's own first-week baseline -> Cooling
Health Index and the degradation model's score. Healthy freezer months (no fault within 6 months) are the comparison.

The degradation model was trained on simulated 2-8 °C vaccine fridges and is applied unchanged, so this tests whether
the "running warmer than its own normal" signal transfers to real equipment, not a tuned freezer model.
Fault dates are service-request dates, so the true fault start can be earlier.

Usage:  python prediction_engine/training/scripts/validate_ult_freezers.py
Writes: results/ult_freezer_validation.json, results/ult_freezer_days.csv
"""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

ML_ROOT = Path(__file__).resolve().parents[2]          # prediction_engine/
sys.path.insert(0, str(ML_ROOT.parent))               # repo root, so "import prediction_engine" works
RESULTS, ARTIFACTS = ML_ROOT / "results", ML_ROOT / "models"

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from prediction_engine.training.datasets import ULT_ROOT, load_ult_window  # noqa: E402
from prediction_engine.services.maintenance_service import DAY, window_features  # noqa: E402
from prediction_engine.ingestion.preprocessing import build_features  # noqa: E402
from prediction_engine.digital_twin.virtual_vial import twin_frame  # noqa: E402

BASELINE_DAYS = 7
PRE_DAYS = 14


def files_for(plan_files, freezer, months):
    return [f for f in plan_files if f"/Revco/{freezer}/" in f and f[-10:-4] in months]


def daily_scores(series: pd.DataFrame, model, unit: int) -> pd.DataFrame:
    s = series.dropna(subset=["Datetime"]).reset_index(drop=True)
    log = pd.DataFrame({"unit": 0, "tick": np.arange(len(s)), "minute": (np.arange(len(s)) + 1) * 10,
                        "air_meas": s["RTD"].astype(float)})
    units = pd.DataFrame({"unit": [0], "cls": ["ILR"]})
    feat = build_features(log, twin_frame(log, units), units)
    w = window_features(feat, baseline_days=BASELINE_DAYS)
    d = w[(w["tick"] % DAY == DAY - 1) & (w["tick"] >= BASELINE_DAYS * DAY - 1)].copy()
    d = d[d["w_mean"].notna()]
    if d.empty:
        return pd.DataFrame()
    p = model.predict(d)
    return pd.DataFrame({"unit": unit, "date": s.loc[d["tick"].to_numpy(), "Datetime"].to_numpy(),
                         "health": p["health"].to_numpy(), "score7": p["score7"].to_numpy(),
                         "alert": p["alert"].to_numpy(), "mean_dev": d["w_mean_dev"].to_numpy(),
                         "p90_dev": d["w_p90_dev"].to_numpy()})


def auc(pos: np.ndarray, neg: np.ndarray) -> float | None:
    pos, neg = pos[~np.isnan(pos)], neg[~np.isnan(neg)]
    if not len(pos) or not len(neg):
        return None
    r = pd.Series(np.concatenate([pos, neg])).rank().to_numpy()
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main() -> None:
    plan = json.load(open(ULT_ROOT / "plan.json"))
    model = pickle.load(open(ARTIFACTS / "models.pkl", "rb"))["degradation"]
    rows, used_f, used_c = [], 0, 0
    for i, x in enumerate(plan["faults"]):
        s = load_ult_window(files_for(plan["files"], x["freezer"], x["months"]))
        if len(s) < (BASELINE_DAYS + PRE_DAYS + 7) * DAY:
            continue
        s = s[s["Datetime"] < pd.Timestamp(x["date"])]
        d = daily_scores(s, model, i)
        if d.empty:
            continue
        d["kind"], d["freezer"], d["fault"] = "fault", x["freezer"], x["fault"]
        d["days_before"] = (pd.Timestamp(x["date"]) - pd.to_datetime(d["date"])).dt.days
        rows.append(d)
        used_f += 1
    for j, c in enumerate(plan["controls"]):
        s = load_ult_window(files_for(plan["files"], c["freezer"], c["months"]))
        if len(s) < (BASELINE_DAYS + PRE_DAYS + 7) * DAY:
            continue
        d = daily_scores(s, model, 1000 + j)
        if d.empty:
            continue
        d["kind"], d["freezer"], d["fault"], d["days_before"] = "control", c["freezer"], "", np.nan
        rows.append(d)
        used_c += 1
    if not rows:
        print("no complete windows downloaded yet")
        return
    days = pd.concat(rows, ignore_index=True)
    pre = days[(days["kind"] == "fault") & (days["days_before"].between(0, PRE_DAYS))]
    early = days[(days["kind"] == "fault") & (days["days_before"] > 30)]
    ctrl = days[days["kind"] == "control"]

    # Fair comparison: the last 14 days before each service vs every 14-day stretch of the healthy windows
    blocks = []
    for _, g in ctrl.sort_values(["unit", "date"]).groupby("unit"):
        g = g.reset_index(drop=True)
        blocks += [bool(g.iloc[s:s + PRE_DAYS]["alert"].any()) for s in range(0, len(g) - PRE_DAYS + 1, PRE_DAYS)]
    by_type = pre.groupby(["unit", "fault"])["alert"].any().reset_index()
    by_type["type"] = np.where(by_type["fault"].str.contains("Refrigerant"), "refrigerant_leak", "compressor")

    per_fault = pre.groupby("unit").agg(min_health=("health", "min"), any_alert=("alert", "any"))
    ctrl_win = ctrl.groupby("unit").agg(min_health=("health", "min"), any_alert=("alert", "any"))
    out = dict(
        fault_windows=used_f, healthy_windows=used_c,
        health_median_last_14_days_before_service=float(pre["health"].median()),
        health_median_same_freezers_30plus_days_before=float(early["health"].median()) if len(early) else None,
        health_median_healthy_freezers=float(ctrl["health"].median()),
        auc_health_last14_vs_healthy=auc(100 - pre["health"].to_numpy(), 100 - ctrl["health"].to_numpy()),
        auc_model_score_last14_vs_healthy=auc(pre["score7"].to_numpy(), ctrl["score7"].to_numpy()),
        faults_with_health_below_85_in_last_14_days=f"{int((per_fault['min_health'] < 85).sum())}/{len(per_fault)}",
        healthy_windows_with_health_below_85_anytime=f"{int((ctrl_win['min_health'] < 85).sum())}/{len(ctrl_win)}",
        faults_with_model_alert_in_last_14_days=f"{int(per_fault['any_alert'].sum())}/{len(per_fault)}",
        healthy_windows_with_model_alert=f"{int(ctrl_win['any_alert'].sum())}/{len(ctrl_win)}",
        share_faults_alerted_last_14_days=float(per_fault["any_alert"].mean()),
        share_healthy_14_day_stretches_alerted=float(np.mean(blocks)) if blocks else None,
        healthy_14_day_stretches=len(blocks),
        alerted_by_type={t: f"{int(g['alert'].sum())}/{len(g)}" for t, g in by_type.groupby("type")},
        note="Model trained on simulated 2-8 °C fridges and applied unchanged to -80 °C freezers; fault dates are "
             "service-request dates. AUC 0.5 = no signal, 1.0 = perfect separation.")
    RESULTS.mkdir(exist_ok=True)
    days.to_csv(RESULTS / "ult_freezer_days.csv", index=False)
    (RESULTS / "ult_freezer_validation.json").write_text(json.dumps(out, indent=2))
    for k, v in out.items():
        print(f"{k:50s} {v}")


if __name__ == "__main__":
    main()
