"""ThermoTwin system architecture v2 (dark theme, 16:9) -> 06_architecture_v2.png"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]

BG, PANEL, INK, MUTED = "#07130c", "#0d2016", "#ffffff", "#b9c7bd"
GREEN, LIME, AMBER, ORANGE, BLUE, PURPLE, RED = (
    "#4af66d", "#7ed957", "#ffc857", "#ff9f43", "#5ab0ff", "#b388ff", "#ff6b6b")

fig = plt.figure(figsize=(16, 9), dpi=150)
fig.patch.set_facecolor(BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160); ax.set_ylim(0, 90); ax.axis("off")


def box(x, y, w, h, edge, fill=PANEL, lw=2, dashed=False, r=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fill, ec=edge, lw=lw, ls=(0, (4, 3)) if dashed else "-"))


def text(x, y, s, size=11, color=INK, weight="normal", ha="left", va="center"):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, linespacing=1.3)


def arrow(x1, y1, x2, y2, color=MUTED, dashed=False, both=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="<|-|>" if both else "-|>",
                                 mutation_scale=14, color=color, lw=1.8,
                                 ls=(0, (4, 3)) if dashed else "-"))


def chip(x, y, w, h, label, edge, size=10):
    box(x, y, w, h, edge, fill="#10291c", lw=1.4, r=0.8)
    text(x + w / 2, y + h / 2, label, size=size, ha="center")


# Title
text(80, 86, "ThermoTwin System Architecture", 26, GREEN, "bold", ha="center")
text(80, 82, "Existing logger data  →  physics twin  →  calibrated risk  →  deterministic alerts  →  people act",
     13, MUTED, ha="center")

# Main layers (centre column)
X, W = 36, 88
layers = [
    # y, h, colour, title, subtitle, chips
    (70, 8.5, BLUE, "0  INGEST", "Native timestamps (eVIN 10-min, WHO DS01.2 JSON, CSV)  ·  schema mapping  ·  observation age tracked, gaps never filled as data", []),
    (55, 13.5, GREEN, "1  TWIN  ·  physics core", "3-node RC model per fridge: air · product/buffer · enclosure + cooling", [
        "EKF state filter + windowed parameter fit", "Virtual Vial: product temp ± uncertainty", "Rollouts 60–120 min: as-is · door · power off"]),
    (40, 13.5, LIME, "2  SENTINEL  ·  ML risk engine", "Twin outputs feed the model as features", [
        "Trust gate: stuck, dropout, noisy probe", "LightGBM hazard + time-to-breach P10/P50/P90", "Calibration + conformal · SHAP cause · slow-fault drift"]),
    (25, 13.5, AMBER, "3  GUARDIAN  ·  alert policy (rules, not AI)", "Observed alarms are never gated by a forecast  ·  recovery-checked suppression  ·  escalation", []),
    (12.5, 10.5, ORANGE, "4  COPILOT  ·  bounded AI, off the alert path", "", [
        "Cause Card built by rules; LLM only rewords (Hindi/Marathi)", "SOP checklist · service ticket draft", "District digest · read-only Q&A"]),
    (2, 8.5, PURPLE, "5  COMMAND  ·  apps and channels", "Buzzer/LED  ·  SMS + voice  ·  WhatsApp / mobile app  ·  district map + technician tickets", []),
]
for y, h, c, title, sub, chips in layers:
    box(X, y, W, h, c)
    text(X + 2, y + h - 2.6, title, 15, c, "bold")
    if sub:
        text(X + 2, y + h - 5.9 if chips else y + 2.6, sub, 11, MUTED if chips else INK)
    if chips:
        cw = (W - 4 - 2 * 1.5) / 3
        for i, label in enumerate(chips):
            chip(X + 2 + i * (cw + 1.5), y + 1.4, cw, 3.8, label, c, 9.5)

# Alert tiers inside Guardian
tiers = [("Normal", GREEN), ("Advisory", BLUE), ("Early warning", AMBER), ("Critical", RED), ("Sensor check", PURPLE)]
tx = X + 2
for i, (t, c) in enumerate(tiers):
    w = 15.6
    box(tx, 27.6, w, 4, c, fill="#10291c", lw=1.6, r=0.8)
    text(tx + w / 2, 29.6, t, 11, c, "bold", ha="center")
    if i < len(tiers) - 1:
        arrow(tx + w + 0.1, 29.6, tx + w + 1.9, 29.6, MUTED)
    tx += w + 2

# Arrows down the stack
for y_from, y_to in [(70, 68.5), (55, 53.5), (40, 38.5), (25, 23)]:
    arrow(80, y_from, 80, y_to, GREEN)
ax.add_patch(FancyArrowPatch((122, 25), (122, 10.5), arrowstyle="-|>", mutation_scale=14,
                             color=AMBER, lw=1.8, connectionstyle="arc3,rad=0"))
text(121, 18.5, "alerts go\nstraight to\nchannels", 8.5, AMBER, ha="right")
arrow(80, 12.5, 80, 10.5, ORANGE)

# Left: data sources, simulator, benchmark
box(2, 64, 30, 14.5, BLUE)
text(4, 75.5, "Data in", 14, BLUE, "bold")
text(4, 69.5, "• Existing loggers: eVIN, WHO\n  RTMD / 30-DTR exports\n• Optional demo rig: ESP32,\n  door switch, current clamp", 10)
arrow(32, 74, 36, 74, BLUE)

box(2, 39, 30, 22, GREEN, dashed=True)
text(4, 58, "ColdChain Gym (simulator)", 14, GREEN, "bold")
text(4, 49, "• Thousands of fridge-days\n• Injected faults: thermostat drift,\n  compressor wear, door, power cut\n• Seasons, ILR cold spots\n• Ground-truth product temp\n  and cause labels", 10)
arrow(32, 50, 36, 62, GREEN, dashed=True)

box(2, 13, 30, 23, AMBER, dashed=True)
text(4, 33, "Replay Benchmark", 14, AMBER, "bold")
text(4, 23.5, "• Same traces, 4 policies:\n  P0 threshold · P1 WHO rules\n  P2 Nexleaf-style · P3 ThermoTwin\n• Lead time vs true product temp\n• ≤ 1 false SMS / fridge-month\n• Missed + suppressed events shown", 10)
arrow(32, 28, 36, 31, AMBER, dashed=True)

# Right: feedback and outputs
box(128, 40, 30, 28, LIME, dashed=True)
text(130, 65, "Feedback loop", 14, LIME, "bold")
text(130, 54, "• Staff confirm or reject\n  the likely cause\n• \"Repair outcome consistent\n  with recovery\", confirmed\n  by a person\n• Twin recalibrates per fridge\n• Model retrained on confirmed\n  events only", 10)
arrow(128, 50, 124, 46, LIME, dashed=True)
arrow(128, 60, 124, 62, LIME, dashed=True)

box(128, 2, 30, 34, PURPLE)
text(130, 33, "What people see", 14, PURPLE, "bold")
text(130, 21, "Health worker app\n• Status + countdown\n• Cause Card + steps\n• Acknowledge\n\nDistrict dashboard\n• Triage map, slow faults\n• Exposure Ledger (MKT,\n  time out of range)", 10)
arrow(124, 6, 128, 6, PURPLE)

text(80, 0.6, "Advisory layer: the certified logger stays the official record, and people decide what happens to stock.",
     9.5, MUTED, ha="center", va="bottom")

fig.savefig("D:/CodeApex/ppt_assets/06_architecture_v2.png", facecolor=BG)
print("saved")
