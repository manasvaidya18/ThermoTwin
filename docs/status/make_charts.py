"""Charts for the status report (light theme) from ml/results/benchmark.csv."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
bench = pd.read_csv(os.path.join(HERE, "..", "..", "ml", "results", "benchmark.csv"))
plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 10})
names = ["P0 one reading\n≤ 0 °C", "P1 WHO rule", "P2 early rule\n≤ 2 °C, 30 min", "P3 ThermoTwin"]
cols = ["#94a3b8", "#b91c1c", "#b45309", "#0f766e"]

fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4), dpi=200)
ax = axes[0]
v = bench["lead_median_min"].to_numpy()
bars = ax.bar(names, v, color=cols, width=0.6)
ax.axhline(0, color="#14211c", lw=1)
for b, x in zip(bars, v):
    ax.text(b.get_x() + b.get_width() / 2, x + (6 if x >= 0 else -16), f"{x:+.0f}", ha="center", fontweight="bold")
ax.set_title("Median warning (min) before the vaccine reaches 0 °C", loc="left", fontsize=10.5, fontweight="bold")
ax.set_ylim(-60, 230)

ax = axes[1]
v = bench["false_alerts_per_fridge_month"].to_numpy()
bars = ax.bar(names, v, color=cols, width=0.6)
ax.axhline(1.0, color="#b45309", ls="--", lw=1)
ax.text(3.45, 1.08, "budget 1.0", color="#b45309", ha="right", fontsize=8.5)
for b, x in zip(bars, v):
    ax.text(b.get_x() + b.get_width() / 2, x + 0.1, f"{x:.2f}", ha="center", fontweight="bold")
ax.set_title("False alerts per fridge-month (lower is better)", loc="left", fontsize=10.5, fontweight="bold")
ax.set_ylim(0, 5.8)
for a in axes:
    a.tick_params(axis="x", labelsize=8)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "benchmark.png"))
print("ok")
