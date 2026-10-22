"""Slide 2 chart v2: same illustrative scenario as 01_unalarmed_window.png, cleaner type -> 01_unalarmed_window_v2.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))
G, LG, W, MUT, RED, BLU, AMB = "#4af66d", "#7ed957", "#ffffff", "#b9c7bd", "#ff6b6b", "#7fb2ff", "#ffc857"
plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "text.color": W,
                     "xtick.color": MUT, "ytick.color": MUT, "axes.edgecolor": MUT})

t = [0, 10, 20, 30, 40, 50, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240]
T = [4, 5, 3.2, 4.8, 3.1, 4.6, 3, 2.4, 1.6, .9, .3, -.2, -.6, -.9, -1.1, -1.25, -1.35, -1.42, -1.48]
h = [x / 60 for x in t]

fig, ax = plt.subplots(figsize=(9, 5.6), dpi=150)
ax.axhspan(2, 8, color=G, alpha=.12)
ax.axhspan(-2, 0, color=BLU, alpha=.16)
ax.plot(h, T, color=W, lw=3.2, solid_capstyle="round")
ax.axvline(68 / 60, color=G, lw=3)
ax.axvline(206 / 60, color=RED, lw=3, ls=(0, (5, 4)))
ax.plot(129 / 60, 0, "o", color=RED, ms=11, zorder=5)

ax.annotate("", xy=(206 / 60, 9.0), xytext=(68 / 60, 9.0),
            arrowprops=dict(arrowstyle="<->", color=AMB, lw=2.5))
ax.text(137 / 60, 9.35, "2 h 18 min earlier", color=AMB, ha="center", fontsize=17, weight="bold")
ax.text(73 / 60, 7.45, "ThermoTwin warns", color=G, fontsize=14.5, weight="bold", va="top")
ax.text(73 / 60, 6.65, "“freezing in ~60 min”", color=G, fontsize=13.5, va="top")
ax.text(201 / 60, 7.45, "Standard WHO", color=RED, fontsize=14.5, weight="bold", ha="right", va="top")
ax.text(201 / 60, 6.65, "freeze alarm", color=RED, fontsize=14.5, weight="bold", ha="right", va="top")
ax.text(134 / 60, 0.45, "est. vaccine temp\nreaches 0 °C", color=BLU, fontsize=13, weight="bold", linespacing=1.15)
ax.text(0.06, 7.45, "Safe zone +2 to +8 °C", color=LG, fontsize=13, va="top")
ax.text(0.06, -1.85, "Freezing zone:\nhidden damage", color=BLU, fontsize=13, linespacing=1.15)

ax.set_xlim(0, 4); ax.set_ylim(-2, 10)
ax.set_xticks([0, 1, 2, 3, 4]); ax.set_xticklabels(["0 h", "1 h", "2 h", "3 h", "4 h"], fontsize=13)
ax.set_yticks([-2, 0, 2, 5, 8, 10]); ax.set_yticklabels(["−2", "0", "+2", "+5", "+8", "+10 °C"], fontsize=13)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title("A fridge drifting toward freezing (illustrative)", color=W, fontsize=17, weight="bold",
             loc="left", pad=30)
fig.savefig(os.path.join(OUT, "01_unalarmed_window_v2.png"), transparent=True, bbox_inches="tight", pad_inches=0.15)
print("done")
