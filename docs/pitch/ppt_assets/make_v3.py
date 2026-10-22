"""Round 1 deck v3 visuals: swimlane architecture + revised impact chart."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Wedge, Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
FILL, INK, MUTED = "#0d2016", "#ffffff", "#b9c7bd"
GREEN, LIME, AMBER, ORANGE, BLUE, PURPLE, RED = (
    "#4af66d", "#7ed957", "#ffc857", "#ff9f43", "#7fb2ff", "#b388ff", "#ff6b6b")

# ---------------------------------------------------------------- architecture
fig = plt.figure(figsize=(16, 10), dpi=150)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160); ax.set_ylim(0, 100); ax.axis("off")


def box(x, y, w, h, edge, fill=FILL, lw=2.2, r=1.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fill, ec=edge, lw=lw))


def t(x, y, s, size=12, color=INK, weight="normal", ha="left", va="center", **kw):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, linespacing=1.25, **kw)


def arrow(p, q, color=MUTED, dashed=False, rad=0.0, lw=1.8):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=15, color=color, lw=lw,
                                 ls=(0, (4, 3)) if dashed else "-", connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=0, shrinkB=0))


def line(xs, ys, color=MUTED, dashed=False, lw=1.8):
    ax.plot(xs, ys, color=color, lw=lw, ls=(0, (4, 3)) if dashed else "-", solid_capstyle="round")


# --- icons (cx, cy = centre, s = size) ---
def ic_thermo(cx, cy, s, c):
    ax.add_patch(FancyBboxPatch((cx - .22 * s, cy - .2 * s), .44 * s, 1.0 * s,
                                boxstyle=f"round,pad=0,rounding_size={.22 * s}", fc="none", ec=c, lw=2))
    ax.add_patch(Circle((cx, cy - .35 * s), .36 * s, fc=c, ec=c))
    ax.add_patch(Rectangle((cx - .08 * s, cy - .3 * s), .16 * s, .75 * s, fc=c, ec="none"))


def ic_doc(cx, cy, s, c):
    ax.add_patch(Polygon([(cx - .5 * s, cy - .7 * s), (cx - .5 * s, cy + .7 * s), (cx + .25 * s, cy + .7 * s),
                          (cx + .5 * s, cy + .45 * s), (cx + .5 * s, cy - .7 * s)], closed=True, fc="none", ec=c, lw=2))
    for k in range(3):
        line([cx - .3 * s, cx + .3 * s], [cy + .3 * s - k * .32 * s] * 2, c, lw=1.6)


def ic_chip(cx, cy, s, c):
    ax.add_patch(Rectangle((cx - .45 * s, cy - .45 * s), .9 * s, .9 * s, fc="none", ec=c, lw=2))
    ax.add_patch(Rectangle((cx - .18 * s, cy - .18 * s), .36 * s, .36 * s, fc=c, ec="none"))
    for k in (-.25, 0, .25):
        line([cx + k * s] * 2, [cy + .45 * s, cy + .7 * s], c, lw=1.6)
        line([cx + k * s] * 2, [cy - .45 * s, cy - .7 * s], c, lw=1.6)
        line([cx - .45 * s, cx - .7 * s], [cy + k * s] * 2, c, lw=1.6)
        line([cx + .45 * s, cx + .7 * s], [cy + k * s] * 2, c, lw=1.6)


def ic_funnel(cx, cy, s, c):
    ax.add_patch(Polygon([(cx - .6 * s, cy + .6 * s), (cx + .6 * s, cy + .6 * s), (cx + .12 * s, cy - .05 * s),
                          (cx + .12 * s, cy - .65 * s), (cx - .12 * s, cy - .5 * s), (cx - .12 * s, cy - .05 * s)],
                         closed=True, fc="none", ec=c, lw=2))


def ic_twin(cx, cy, s, c):  # house-like fridge with a wave = thermal twin
    ax.add_patch(FancyBboxPatch((cx - .45 * s, cy - .7 * s), .9 * s, 1.4 * s,
                                boxstyle=f"round,pad=0,rounding_size={.12 * s}", fc="none", ec=c, lw=2))
    line([cx - .45 * s, cx + .45 * s], [cy + .2 * s] * 2, c, lw=1.6)
    line([cx + .28 * s] * 2, [cy + .35 * s, cy + .55 * s], c, lw=2)
    line([cx + .28 * s] * 2, [cy - .05 * s, cy - .35 * s], c, lw=2)
    ax.add_patch(Circle((cx + .85 * s, cy - .45 * s), .32 * s, fc="none", ec=c, lw=2))
    ax.add_patch(Circle((cx + .85 * s, cy - .45 * s), .1 * s, fc=c, ec="none"))


def ic_bars(cx, cy, s, c):
    for k, hgt in enumerate((.6, 1.0, 1.4)):
        ax.add_patch(Rectangle((cx - .65 * s + k * .45 * s, cy - .7 * s), .32 * s, hgt * s, fc=c, ec="none"))
    line([cx - .75 * s, cx + .7 * s], [cy - .72 * s] * 2, c, lw=1.6)


def ic_phone(cx, cy, s, c):
    ax.add_patch(FancyBboxPatch((cx - .38 * s, cy - .7 * s), .76 * s, 1.4 * s,
                                boxstyle=f"round,pad=0,rounding_size={.14 * s}", fc="none", ec=c, lw=2))
    ax.add_patch(Circle((cx, cy - .52 * s), .07 * s, fc=c, ec="none"))
    ax.add_patch(Wedge((cx, cy + .05 * s), .3 * s, 0, 180, fc=c, ec="none"))  # bell
    ax.add_patch(Rectangle((cx - .3 * s, cy - .12 * s), .6 * s, .17 * s, fc=c, ec="none"))


def ic_chat(cx, cy, s, c):
    ax.add_patch(FancyBboxPatch((cx - .65 * s, cy - .35 * s), 1.3 * s, .95 * s,
                                boxstyle=f"round,pad=0,rounding_size={.2 * s}", fc="none", ec=c, lw=2))
    ax.add_patch(Polygon([(cx - .35 * s, cy - .35 * s), (cx - .5 * s, cy - .75 * s), (cx - .05 * s, cy - .35 * s)],
                         closed=True, fc=c, ec=c))
    for k in (-.3, 0, .3):
        ax.add_patch(Circle((cx + k * s, cy + .12 * s), .08 * s, fc=c, ec="none"))


def ic_wrench(cx, cy, s, c):
    line([cx - .5 * s, cx + .3 * s], [cy - .5 * s, cy + .3 * s], c, lw=4.5)
    ax.add_patch(Wedge((cx + .42 * s, cy + .42 * s), .36 * s, 80, 370, width=.16 * s, fc=c, ec="none"))


def ic_ai(cx, cy, s, c):
    ax.add_patch(FancyBboxPatch((cx - .7 * s, cy - .45 * s), 1.4 * s, 1.0 * s,
                                boxstyle=f"round,pad=0,rounding_size={.22 * s}", fc="none", ec=c, lw=2))
    t(cx, cy + .05 * s, "AI", size=11, color=c, weight="bold", ha="center")
    ax.add_patch(Polygon([(cx + .2 * s, cy - .45 * s), (cx + .45 * s, cy - .8 * s), (cx + .5 * s, cy - .45 * s)],
                         closed=True, fc=c, ec=c))


def ic_person(cx, cy, s, c):
    ax.add_patch(Circle((cx, cy + .55 * s), .38 * s, fc=c, ec="none"))
    ax.add_patch(Wedge((cx, cy - .55 * s), .75 * s, 0, 180, fc=c, ec="none"))


def card(x, y, w, h, edge, icon, title, sub, isize=2.6):
    box(x, y, w, h, edge)
    icon(x + 5, y + h / 2, isize, edge)
    t(x + 10, y + h / 2 + 2.0, title, 15, INK, "bold")
    t(x + 10, y + h / 2 - 2.2, sub, 10.5, MUTED)


# lanes
lanes = [(80, 99, "Data in"), (52, 78, "Physics twin\n& risk ML"), (32, 50, "Alert policy\n(rules, not AI)"),
         (2, 30, "Notifications\n& actions")]
for y0, y1, name in lanes:
    t(2, (y0 + y1) / 2, name, 17, GREEN, "bold")
for yy in (79, 51, 31):
    line([1, 159], [yy, yy], "#3c5a46", dashed=True, lw=1.4)

# lane 1: data sources
card(26, 84, 38, 12, BLUE, ic_thermo, "Fridge loggers", "Existing RTMD / 30-DTR probes")
card(70, 84, 38, 12, BLUE, ic_doc, "eVIN logs", "WHO DS01.2 JSON · 10-min data")
card(114, 84, 38, 12, BLUE, ic_chip, "Optional demo rig", "ESP32 · door switch · current clamp")
for cx in (45, 89, 133):
    line([cx, cx], [84, 81.5], BLUE)
line([45, 133], [81.5, 81.5], BLUE)
arrow((89, 81.5), (89, 72), BLUE)

# lane 2: ingest, twin, risk
card(70, 58, 38, 14, GREEN, ic_funnel, "Ingest + trust gate", "Gaps, stuck + drifting probes\n(anomaly check on twin errors)")
card(22, 58, 42, 14, GREEN, ic_twin, "Digital twin", "3-node RC + EKF, fleet priors\nVirtual Vial: est. vaccine temp")
card(114, 58, 40, 14, LIME, ic_bars, "LightGBM risk engine", "Learns what the twin misses\nRisk 60–120 min · P10–P90 · SHAP")
arrow((70, 65), (64, 65), GREEN)
arrow((108, 65), (114, 65), GREEN)
line([43, 43, 124], [58, 54.5, 54.5], LIME)
arrow((124, 54.5), (124, 58), LIME)
t(83, 52.9, "twin forecast + its errors feed the model  ·  benchmarked vs LSTM/TCN and Chronos/TimesFM", 10, LIME, ha="center")

# lane 3: tiers
box(22, 40, 22, 7.5, PURPLE)
t(33, 43.75, "Sensor check", 14, PURPLE, "bold", ha="center")
t(33, 38.3, "from the trust gate", 9.5, PURPLE, ha="center")
tiers = [("Normal", GREEN, 48), ("Advisory", BLUE, 74), ("Early warning", AMBER, 100), ("Critical", RED, 126)]
for name, c, x in tiers:
    box(x, 40, 22, 7.5, c, fill=FILL if name != "Critical" else "#3a1414")
    t(x + 11, 43.75, name, 14, c, "bold", ha="center")
for (_, _, x) in tiers[:-1]:
    arrow((x + 22, 43.75), (x + 26, 43.75), MUTED)
arrow((142, 58), (142, 47.5), LIME)
t(140.8, 50.2, "risk sets the tier", 9.5, LIME, ha="right")
t(48, 35.2, "Observed alarms are never gated by a forecast  ·  suppression ends if\nrecovery doesn't match  ·  escalation timers", 10, MUTED)

# lane 4: channels
outs = [(22, LIME, ic_phone, "Staff app", "Countdown, Cause Card,\nacknowledge"),
     (54, AMBER, ic_chat, "SMS + voice", "DLT-registered,\nescalates if ignored"),
     (86, GREEN, ic_wrench, "Technician ticket", "Likely fault +\nevidence attached"),
     (118, ORANGE, ic_ai, "Bounded copilot", "Rewords Cause Cards in\nHindi/Marathi; off alert path")]
line([36.5, 132.5], [28, 28], MUTED)
arrow((111, 40), (111, 28), MUTED)
for x, c, ic, title, sub in outs:
    arrow((x + 14.5, 28), (x + 14.5, 22), MUTED, dashed=(c == ORANGE))
    box(x, 8, 29, 14, c)
    ic(x + 5, 15, 2.4, c)
    t(x + 9.5, 17.2, title, 14, INK, "bold")
    t(x + 9.5, 12.2, sub, 9.5, MUTED)

# feedback loop
ic_person(153.5, 15, 2.2, MUTED)
t(153.5, 9.2, "Technician\ncloses loop", 9.5, INK, "bold", ha="center", va="top")
for xx in (36.5, 68.5, 100.5, 132.5):
    line([xx, xx], [8, 5], MUTED)
line([36.5, 147], [5, 5], MUTED); arrow((147, 5), (150.5, 11), MUTED)
line([157.5, 157.5], [19, 65], AMBER, dashed=True)
arrow((157.5, 65), (154, 65), AMBER, dashed=True)
t(155.6, 40, "repair + cause confirmed → recalibrate", 9.5, AMBER, ha="center", rotation=90)

fig.savefig(os.path.join(OUT, "06_architecture_v3.png"), transparent=True)
plt.close(fig)

# ---------------------------------------------------------------- impact chart
fig, ax = plt.subplots(figsize=(8.4, 5.8), dpi=150)
names = ["WHO threshold-\nbased alarm", "Early-warning\nbaseline", "ThermoTwin\n(proposed)"]
vals = [-77, 16, 61]
bars = ax.bar(names, vals, color=[RED, AMBER, GREEN], width=0.58)
ax.axhline(0, color=INK, lw=1.5)
for b, v in zip(bars, vals):
    lab = f"{-v} min after" if v < 0 else f"{v} min before"
    ax.text(b.get_x() + b.get_width() / 2, v + (4 if v > 0 else -10), lab, ha="center",
            fontsize=15, weight="bold", color=INK)
ax.set_ylabel("Minutes before (+) or after (−) estimated\nvaccine temperature reaches 0 °C", fontsize=12, color=INK)
ax.set_ylim(-98, 82)
ax.tick_params(axis="x", labelsize=13, colors=INK)
ax.tick_params(axis="y", labelsize=12, colors=MUTED)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(MUTED)
ax.set_title("Illustrative warning lead time before\nestimated vaccine freezing", fontsize=16, loc="left",
             color=INK, weight="bold", pad=12)
fig.savefig(os.path.join(OUT, "05_warning_time_v2.png"), transparent=True, bbox_inches="tight", pad_inches=0.15)
plt.close(fig)
print("done")
