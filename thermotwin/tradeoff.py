"""Warning time at matched false-alert rates: ThermoTwin vs the LSTM baseline, from saved test risk grids."""
import sys

import numpy as np
import pandas as pd

from thermotwin.benchmark import policy_signals, score

rows = []
for seed in (0, 1):
    for kind in ("freeze", "heat"):
        try:
            z = np.load(f"outputs/risk_{kind}_seed{seed}.npz")
        except FileNotFoundError:
            continue
        ev = pd.read_csv(f"outputs/events_{kind}_seed{seed}.csv")
        fm = z["air"].shape[0] * 21 / 30
        for model in ("thermotwin", "lstm"):
            for th in np.round(np.arange(0.05, 0.96, 0.05), 2):
                s = score(policy_signals(z["air"], z[model], th, kind)["P3 ThermoTwin"], ev, fm)
                rows.append(dict(seed=seed, kind=kind, model=model, threshold=th, recall=s["recall"],
                                 lead=s["lead_median_min"], false=s["false_alerts_per_fridge_month"]))
df = pd.DataFrame(rows)
df.to_csv("outputs/tradeoff.csv", index=False)
out = []
for (seed, kind, model), g in df.groupby(["seed", "kind", "model"]):
    for budget in (0.25, 0.5, 1.0):
        ok = g[(g["false"] <= budget) & (g["recall"] >= 0.9)]
        best = ok.sort_values("lead", ascending=False).head(1)
        out.append(dict(seed=seed, kind=kind, model=model, budget=budget,
                        lead=float(best["lead"].iloc[0]) if len(best) else np.nan,
                        recall=float(best["recall"].iloc[0]) if len(best) else np.nan))
res = pd.DataFrame(out).pivot_table(index=["kind", "budget", "seed"], columns="model", values="lead")
print("Best median warning (min) with recall >= 90% and false alerts <= budget, on held-out fridges:")
print(res.round(0).to_string())
