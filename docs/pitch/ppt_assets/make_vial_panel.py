"""Slide 5 panel: how the digital twin and Virtual Vial work -> 08_virtual_vial_panel.png (fits 440x598 slot)"""
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "mathtext.fontset": "dejavusans"})
G, LG, W, MUT, AMB, BLU, ORG = "#4af66d", "#7ed957", "#ffffff", "#b9c7bd", "#ffc857", "#7fb2ff", "#ff9f43"

fig = plt.figure(figsize=(4.45, 6.05), dpi=200)
bg = fig.add_axes([0, 0, 1, 1]); bg.axis("off"); bg.set_xlim(0, 1); bg.set_ylim(0, 1)
bg.add_patch(FancyBboxPatch((0.012, 0.008), 0.976, 0.984, boxstyle="round,pad=0,rounding_size=0.035",
                            fc="#0b2414", ec=G, lw=2.2, alpha=0.95))


def node(x, y, w, h, label, sub, c):
    bg.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.015", fc="#10291c", ec=c, lw=1.4))
    bg.text(x + w / 2, y + h * 0.64, label, fontsize=7.6, weight="bold", color=c, ha="center", va="center")
    bg.text(x + w / 2, y + h * 0.28, sub, fontsize=6.4, color=MUT, ha="center", va="center")


def arrow(p, q, c=MUT, both=True):
    bg.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=7, color=c, lw=1.1,
                                 shrinkA=0, shrinkB=0))


bg.text(0.06, 0.955, "How the digital twin works", fontsize=13, weight="bold", color=G, va="center")

# 1. Three heat nodes
bg.text(0.06, 0.905, "1  Each fridge = 3 heat parts", fontsize=8.6, weight="bold", color=W, va="center")
node(0.05, 0.795, 0.26, 0.075, "Walls + cooling", "compressor, ice lining", BLU)
node(0.37, 0.795, 0.26, 0.075, "Air", "what the sensor reads", W)
node(0.69, 0.795, 0.26, 0.075, "Vaccine", "Virtual Vial", G)
arrow((0.31, 0.8325), (0.37, 0.8325))
arrow((0.63, 0.8325), (0.69, 0.8325))
bg.text(0.5, 0.775, "room heat, door openings and power cuts push heat in", fontsize=6.6, color=MUT,
        ha="center", va="center")
bg.text(0.5, 0.735, r"$C_i\,\dfrac{dT_i}{dt} = \sum_j \dfrac{T_j - T_i}{R_{ij}} + Q_i$", fontsize=10.5, color=W,
        ha="center", va="center")
bg.text(0.5, 0.692, "heat capacity × warming rate = heat in from neighbours + cooling",
        fontsize=6.6, color=MUT, ha="center", va="center")

# 2. Kalman loop
bg.text(0.06, 0.648, "2  Every 10 min: Kalman filter", fontsize=8.6, weight="bold", color=W, va="center")
for i, (lab, c) in enumerate([("Predict", LG), ("Compare\nwith sensor", AMB), ("Correct\n+ error bar", G)]):
    x = 0.06 + i * 0.31
    bg.add_patch(FancyBboxPatch((x, 0.575), 0.25, 0.05, boxstyle="round,pad=0,rounding_size=0.012",
                                fc="#10291c", ec=c, lw=1.2))
    bg.text(x + 0.125, 0.6, lab, fontsize=6.8, color=c, weight="bold", ha="center", va="center", linespacing=1.0)
    if i < 2:
        arrow((x + 0.25, 0.6), (x + 0.31, 0.6), MUT, both=False)
bg.text(0.5, 0.553, "run forward with no new data → the 1–2 h forecast", fontsize=6.6, color=MUT,
        ha="center", va="center")

# 3. Virtual Vial
bg.text(0.06, 0.51, "3  Virtual Vial = the vaccine part", fontsize=8.6, weight="bold", color=W, va="center")
bg.text(0.36, 0.455, r"$\dfrac{dT_{vial}}{dt} = \dfrac{T_{air} - T_{vial}}{\tau}$", fontsize=11, color=W,
        ha="center", va="center")
bg.text(0.79, 0.455, r"$\tau = \dfrac{m\,c}{h\,A}$", fontsize=10, color=AMB, ha="center", va="center")
bg.text(0.5, 0.405, "Newton's law of cooling · τ learned per fridge", fontsize=6.6, color=MUT,
        ha="center", va="center")

t = list(range(0, 31))
air = [4 if m < 5 else 11 if m < 7 else max(4.0, 11 - 1.6 * (m - 6)) for m in t]
vial, v = [], 4.0
for a in air:
    v = a + (v - a) * math.exp(-1 / 60)
    vial.append(v)
ax = fig.add_axes([0.13, 0.1, 0.81, 0.235])
ax.set_facecolor("none")
ax.axhspan(2, 8, color=G, alpha=0.1)
ax.plot(t, air, color=BLU, lw=1.8, label="Air (measured)")
ax.plot(t, vial, color=G, lw=2.2, ls="--", label="Virtual Vial (estimated)")
ax.set_ylim(0, 12.5); ax.set_xlim(0, 30)
ax.set_xticks([0, 10, 20, 30]); ax.set_xticklabels(["0", "10", "20", "30 min"], fontsize=6.5, color=MUT)
ax.set_yticks([2, 8, 12]); ax.set_yticklabels(["2", "8", "12 °C"], fontsize=6.5, color=MUT)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(MUT)
ax.tick_params(colors=MUT, length=2)
ax.legend(loc="upper right", fontsize=6.2, frameon=False, labelcolor=W)
bg.text(0.06, 0.365, "Door open 2 min: air +7 °C, vial +0.4 °C → no false alarm",
        fontsize=7.4, color=AMB, weight="bold", va="center")

bg.text(0.5, 0.04, "Validation: water-bottle probe (demo kit) + simulator ground truth",
        fontsize=6.8, color=MUT, ha="center", va="center", style="italic")

fig.savefig(os.path.join(OUT, "08_virtual_vial_panel.png"), transparent=True)
print("done")
