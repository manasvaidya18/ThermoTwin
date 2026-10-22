"""Slide 7 chart from the measured Replay Benchmark (simulated, held-out fridges) -> 05_warning_time_measured.png"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
csv = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "ml", "results", "baselines_seed0_ep6_freeze-heat.csv")
df = pd.read_csv(csv)
df = df[df["kind"] == "freeze"].set_index("model")
plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
W, MUT, RED, AMB, BLU, G = "#ffffff", "#b9c7bd", "#ff6b6b", "#ffc857", "#7fb2ff", "#4af66d"

order = [("P1 WHO (<= -0.5 °C for 60 min)", "WHO alarm\nrule", RED),
         ("P2 early rule (<= 2 °C for 30 min)", "Simple early\nrule (≤ 2 °C)", AMB),
         ("LSTM (raw air, no physics)", "Deep learning\n(LSTM, no physics)", BLU),
         ("ThermoTwin (twin + LightGBM)", "ThermoTwin\n(twin + LightGBM)", G)]
names, vals, cols, notes = [], [], [], []
for key, label, c in order:
    if key not in df.index:
        continue
    r = df.loc[key]
    names.append(label)
    vals.append(r["lead_median_min"] if r["lead_median_min"] == r["lead_median_min"] else 0)
    cols.append(c)
    notes.append(f"caught {r['caught']}\n{r['false_per_fridge_month']:.2f} false alerts\nper fridge-month")

fig, ax = plt.subplots(figsize=(8.6, 6.2), dpi=150)
bars = ax.bar(names, vals, color=cols, width=0.6)
ax.axhline(0, color=W, lw=1.4)
for b, v, nt in zip(bars, vals, notes):
    lab = f"{-v:.0f} min after" if v < 0 else f"{v:.0f} min before"
    ax.text(b.get_x() + b.get_width() / 2, v + (6 if v >= 0 else -14), lab, ha="center", fontsize=14, weight="bold", color=W)
    ax.text(b.get_x() + b.get_width() / 2, -78, nt, ha="center", va="top", fontsize=10, color=MUT, linespacing=1.25)
ax.set_ylim(-125, 215)
ax.set_yticks([-60, 0, 60, 120, 180])
ax.set_ylabel("Minutes before (+) / after (−) the vaccine reaches 0 °C", fontsize=11, color=W)
ax.tick_params(axis="x", labelsize=11, colors=W)
ax.tick_params(axis="y", labelsize=10, colors=MUT)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(MUT)
ax.set_title("Measured warning time before freezing\n41 freeze events on 48 held-out fridges (simulated)", fontsize=15,
             loc="left", color=W, weight="bold", pad=10)
fig.savefig(os.path.join(HERE, "05_warning_time_measured.png"), transparent=True, bbox_inches="tight", pad_inches=0.15)
print("ok")
