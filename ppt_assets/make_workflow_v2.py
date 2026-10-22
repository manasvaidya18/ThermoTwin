"""Slide 3 workflow v2 (matches architecture v3: ~10-min readings, 1-2 h forecast) -> 02_workflow_v2.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
G, LG, W, MUT, AMB, PUR = "#4af66d", "#7ed957", "#ffffff", "#b9c7bd", "#ffc857", "#b388ff"


def box(ax, x, y, w, h, text, fc="#0d2016", ec=G, fs=13, bold=False, tc=W):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.14", fc=fc, ec=ec, lw=2.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            weight="bold" if bold else "normal", linespacing=1.3)


def arrow(ax, a, b, c=LG):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=22, color=c, lw=2.2, shrinkA=0, shrinkB=0))


fig, ax = plt.subplots(figsize=(8, 8.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 10.6); ax.axis("off")
box(ax, 1.6, 9.3, 6.8, 1.0, "New logger reading (about every 10 min)\ntemperature · door / power if available", fs=12.5, bold=True)
box(ax, 1.6, 7.75, 6.8, 1.0, "Digital twin: starts from fleet priors, learns this fridge\nestimates the vaccine's own temperature", fs=12.5, fc="#123d22")
box(ax, 1.6, 6.2, 6.8, 1.0, "ML forecast: learns what the physics misses\nrisk of leaving 2–8 °C in the next 1–2 h", fs=12.5)
ax.add_patch(Polygon([[5, 5.8], [7.2, 4.85], [5, 3.9], [2.8, 4.85]], closed=True, fc="#2a2410", ec=AMB, lw=2.2))
ax.text(5, 4.85, "Real risk?\nmeasured alarm, or\ncalibrated risk too high", ha="center", va="center", fontsize=11.5, color=W)
box(ax, 0.2, 2.2, 4.3, 1.1, "Stay quiet\nlog it, keep watching", fs=12.5, ec=MUT)
box(ax, 5.5, 2.2, 4.3, 1.1, "Alert: tier + countdown\n+ likely cause + next steps", fs=12.5, ec=G, bold=True)
box(ax, 5.5, 0.4, 4.3, 1.1, "Fix and check\nrecovery tracked, a person confirms", fs=12, ec=LG)
for a, b in [((5, 9.3), (5, 8.75)), ((5, 7.75), (5, 7.2)), ((5, 6.2), (5, 5.8)),
             ((2.8, 4.85), (2.35, 3.3)), ((7.2, 4.85), (7.65, 3.3)), ((7.65, 2.2), (7.65, 1.5))]:
    arrow(ax, a, b)
ax.text(1.75, 4.3, "no", color=MUT, fontsize=12.5)
ax.text(7.95, 4.3, "yes", color=G, fontsize=12.5, weight="bold")
ax.text(2.35, 1.45, "Measured alarms are never silenced\nby a forecast", ha="center", fontsize=11, color=AMB)
ax.text(2.35, 0.55, "SMS · voice · WhatsApp\nHindi / Marathi / English", ha="center", fontsize=11, color=LG)
fig.savefig(os.path.join(OUT, "02_workflow_v2.png"), dpi=150, transparent=True, bbox_inches="tight", pad_inches=0.15)
print("done")
