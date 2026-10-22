"""Slide 6 roadmap v2 (adds model upgrades and baselines) -> 04_roadmap_v2.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
G, LG, W, MUT, AMB = "#4af66d", "#7ed957", "#ffffff", "#b9c7bd", "#ffc857"

fig, ax = plt.subplots(figsize=(13, 3.6))
ax.set_xlim(0, 13); ax.set_ylim(1.2, 4.8); ax.axis("off")
ax.plot([0.4, 12.6], [3.6, 3.6], color=G, lw=4)
steps = [("TODAY · 11 OCT", "Research done\nDesign + PRD\nbuild plan ready", G),
         ("BY 18 OCT", "Core path working:\nsimulator, twin, forecast,\nalerts, benchmark\n+ LSTM baseline", LG),
         ("TO 24 OCT", "Fleet priors, residual ML,\nChronos/TimesFM baseline,\nHindi/Marathi cause cards,\ndistrict map", LG),
         ("24 OCT FINALE", "Organisers' data,\nlive fault demo,\npublished scorecard", AMB),
         ("AFTER", "Pilot beside a real\nclinic logger, probe-drift\ndetector, field calibration", MUT)]
for i, (h, b, c) in enumerate(steps):
    x = 1.0 + i * 2.75
    ax.plot(x, 3.6, "o", ms=20, color=c, mec="#062010", mew=3)
    ax.text(x, 4.3, h, ha="center", fontsize=14, weight="bold", color=c)
    ax.text(x, 2.9, b, ha="center", va="top", fontsize=12.5, color=W, linespacing=1.35)
fig.savefig(os.path.join(OUT, "04_roadmap_v2.png"), dpi=150, transparent=True, bbox_inches="tight", pad_inches=0.15)
print("done")
