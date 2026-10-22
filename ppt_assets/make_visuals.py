import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon
import os
OUT = os.path.dirname(os.path.abspath(__file__))
G, LG, W, MUT, RED, BLU, AMB = "#4af66d", "#7ed957", "#ffffff", "#b9c7bd", "#ff6b6b", "#7fb2ff", "#ffc857"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": W, "axes.labelcolor": W,
                     "xtick.color": MUT, "ytick.color": MUT, "axes.edgecolor": MUT})

def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, transparent=True, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)

# 1. Unalarmed window (illustrative)
t = [0,10,20,30,40,50,60,75,90,105,120,135,150,165,180,195,210,225,240]
T = [4,5,3.2,4.8,3.1,4.6,3,2.4,1.6,.9,.3,-.2,-.6,-.9,-1.1,-1.25,-1.35,-1.42,-1.48]
fig, ax = plt.subplots(figsize=(9, 5.6))
ax.axhspan(2, 8, color=G, alpha=.13); ax.axhspan(-2, 0, color=BLU, alpha=.18)
ax.plot([x/60 for x in t], T, color=W, lw=3)
ax.axvline(68/60, color=G, lw=3); ax.axvline(206/60, color=RED, lw=3, ls="--")
ax.plot(129/60, 0, "o", color=RED, ms=11)
ax.annotate("", xy=(206/60, 8.9), xytext=(68/60, 8.9), arrowprops=dict(arrowstyle="<->", color=AMB, lw=2.5))
ax.text(137/60, 9.25, "2 h 18 min earlier", color=AMB, ha="center", fontsize=15, weight="bold")
ax.text(70/60, 6.9, "ThermoTwin warns\n\"freezing in ~60 min\"", color=G, fontsize=13, weight="bold")
ax.text(203/60, 6.9, "Standard WHO\nfreeze alarm", color=RED, fontsize=13, weight="bold", ha="right")
ax.text(133/60, .55, "vaccine hits 0 °C", color=BLU, fontsize=12, weight="bold")
ax.text(.05, 7.3, "safe zone +2 to +8 °C", color=LG, fontsize=12)
ax.text(.05, -1.75, "freezing zone: damage you can't see", color=BLU, fontsize=12)
ax.set_xlim(0, 4); ax.set_ylim(-2, 10)
ax.set_xticks([0,1,2,3,4]); ax.set_xticklabels(["0 h","1 h","2 h","3 h","4 h"], fontsize=12)
ax.set_yticks([-2,0,2,5,8,10]); ax.set_yticklabels(["−2","0","+2","+5","+8","+10 °C"], fontsize=12)
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.set_title("A fridge drifting toward freezing (illustrative)", color=W, fontsize=15, loc="left", pad=28)
save(fig, "01_unalarmed_window.png")

def box(ax, x, y, w, h, text, fc="#0e2a17", ec=G, fs=13, bold=False, tc=W):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, lw=2.2))
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs, color=tc, weight="bold" if bold else "normal", wrap=True)

def arrow(ax, a, b, c=LG):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=22, color=c, lw=2.2))

# 2. Workflow
fig, ax = plt.subplots(figsize=(8, 8.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 10.6); ax.axis("off")
box(ax, 1.6, 9.3, 6.8, 1.0, "Fridge readings every 5 min\ntemperature · door · power · compressor", fs=12, bold=True)
box(ax, 1.6, 7.75, 6.8, 1.0, "Digital twin of this fridge\nestimates vaccine temperature", fs=12, fc="#123d22")
box(ax, 1.6, 6.2, 6.8, 1.0, "ML forecast\nchance of leaving 2–8 °C in 30–60 min", fs=12)
ax.add_patch(Polygon([[5,5.8],[7.1,4.85],[5,3.9],[2.9,4.85]], closed=True, fc="#2a2410", ec=AMB, lw=2.2))
ax.text(5, 4.85, "Real risk?\nphysics + ML agree,\nor a measured alarm", ha="center", va="center", fontsize=11.5, color=W)
box(ax, 0.2, 2.2, 4.3, 1.1, "Stay quiet\nlog it, keep watching", fs=12, ec=MUT)
box(ax, 5.5, 2.2, 4.3, 1.1, "Alert with a countdown\n+ cause + next steps", fs=12, ec=G, bold=True)
box(ax, 5.5, 0.4, 4.3, 1.1, "Fix and check\ntwin confirms recovery", fs=12, ec=LG)
for a, b in [((5,9.3),(5,8.75)), ((5,7.75),(5,7.2)), ((5,6.2),(5,5.8)), ((2.9,4.85),(2.35,3.3)), ((7.1,4.85),(7.65,3.3)), ((7.65,2.0),(7.65,1.5))]:
    arrow(ax, a, b)
ax.text(1.75, 4.3, "no", color=MUT, fontsize=12); ax.text(7.9, 4.3, "yes", color=G, fontsize=12, weight="bold")
ax.text(2.35, 1.4, "SMS · voice call · WhatsApp\nin Hindi / Marathi / English", ha="center", fontsize=11, color=LG)
save(fig, "02_workflow.png")

# 3. Architecture (layers)
fig, ax = plt.subplots(figsize=(10, 7.4)); ax.set_xlim(0, 13.1); ax.set_ylim(0.8, 9.6); ax.axis("off")
layers = [("SENSE", "Fridge sensors or existing loggers (eVIN, WHO DS01.2)", "#0e2a17", MUT),
          ("TWIN", "Physics model per fridge · Virtual Vial · health vitals", "#123d22", G),
          ("PREDICT", "LightGBM breach forecast · cause finder · sensor trust", "#0e2a17", MUT),
          ("DECIDE", "Rule-based alert policy · never an AI guess", "#0e2a17", MUT),
          ("EXPLAIN", "Bounded AI copilot: cause card in local language", "#2a2410", AMB),
          ("ACT", "Staff app · SMS/voice · technician ticket · district map", "#0e2a17", MUT)]
y = 8.3
for i, (k, d, fc, ec) in enumerate(layers):
    ax.add_patch(FancyBboxPatch((0.2, y), 9.4, 1.0, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, lw=2.2))
    ax.text(0.55, y+0.5, k, va="center", fontsize=13, weight="bold", color=G)
    ax.text(2.2, y+0.5, d, va="center", fontsize=11, color=W)
    if i < 5: arrow(ax, (4.7, y), (4.7, y-0.42))
    y -= 1.42
for (yy, t1, t2) in [(8.3, "Simulator", "faults, power cuts,\ndoors, seasons"), (5.46, "Benchmark", "4 alert policies,\nsame data"), (2.62, "Feedback", "staff tags teach\nthe model")]:
    ax.add_patch(FancyBboxPatch((10.0, yy-0.1), 2.9, 1.25, boxstyle="round,pad=0.02,rounding_size=0.12", fc="#0b1f12", ec=LG, lw=1.6, ls="--"))
    ax.text(11.45, yy+0.78, t1, ha="center", fontsize=12, weight="bold", color=LG)
    ax.text(11.45, yy+0.02, t2, ha="center", fontsize=10, color=MUT)
    arrow(ax, (10.0, yy+0.5), (9.65, yy+0.5), c=LG)
save(fig, "03_architecture.png")

# 4. Roadmap
fig, ax = plt.subplots(figsize=(13, 3.6)); ax.set_xlim(0, 13); ax.set_ylim(1.2, 4.8); ax.axis("off")
ax.plot([0.4, 12.6], [3.6, 3.6], color=G, lw=4)
steps = [("TODAY · 11 OCT", "Research done\nDesign + PRD\nbuild plan ready", G),
         ("BY 18 OCT", "Core path working:\nsimulator, twin,\nforecast, alerts,\nbenchmark", LG),
         ("TO 24 OCT", "Full product:\ncause cards in Hindi/\nMarathi, repair check,\ndistrict map", LG),
         ("24 OCT FINALE", "Organisers' data,\nlive fault demo,\npublished scorecard", AMB),
         ("AFTER", "Pilot beside a real\nclinic logger,\nfield calibration", MUT)]
for i, (h, b, c) in enumerate(steps):
    x = 1.0 + i*2.75
    ax.plot(x, 3.6, "o", ms=20, color=c, mec="#062010", mew=3)
    ax.text(x, 4.3, h, ha="center", fontsize=13, weight="bold", color=c)
    ax.text(x, 2.9, b, ha="center", va="top", fontsize=12, color=W, linespacing=1.4)
save(fig, "04_roadmap.png")

# 5. Impact chart (illustrative scenario)
fig, ax = plt.subplots(figsize=(8.4, 5.6))
names = ["WHO standard\nalarm", "Early-warning\nrules (Nexleaf-style)", "ThermoTwin"]
vals = [-77, 16.5, 61]
cols = [RED, AMB, G]
bars = ax.bar(names, vals, color=cols, width=0.6)
ax.axhline(0, color=W, lw=1.5)
for b, v in zip(bars, vals):
    lab = f"{int(round(-v))} min after" if v < 0 else f"{int(round(v))} min before"
    ax.text(b.get_x()+b.get_width()/2, v + (4 if v > 0 else -9), lab, ha="center", fontsize=13, weight="bold", color=W)
ax.set_ylabel("Warning before vaccine reaches 0 °C (min)", fontsize=12)
ax.set_ylim(-95, 80)
ax.tick_params(axis="x", labelsize=12, colors=W)
for s in ["top","right"]: ax.spines[s].set_visible(False)
ax.set_title("Same freezing event, three alarms (illustrative)", fontsize=15, loc="left", color=W, pad=14)
save(fig, "05_warning_time.png")
print("done")
