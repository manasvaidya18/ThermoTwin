"""Guardian tier rules and alert wording (as in the PRD and the benchmark's P3 policy)."""
from __future__ import annotations

import numpy as np
import pandas as pd

TIER_ORDER = {"Critical": 0, "Early warning": 1, "Sensor check": 2, "Advisory": 3, "Normal": 4}

# Cause Card wording per class. Thermostat-too-cold and relay-stuck-on look alike from temperature alone.
CARD = {
    "cooling_too_hard": ("Thermostat set too cold, or relay stuck on",
                         ["Turn the thermostat one step warmer", "Move freeze-sensitive vaccines away from the walls",
                          "If it keeps cooling, call the technician: the relay may be stuck"]),
    "power_cut": ("Power cut", ["Keep the door shut", "Check the holdover clock", "Call the supervisor if under 1 h left"]),
    "weak_cooling": ("Weak cooling: compressor wear or a leaking door seal",
                     ["Check the door closes and seals fully", "Clean dust from the condenser at the back",
                      "Book a technician visit"]),
    "sensor_fault": ("Sensor problem: probe stuck or drifting",
                     ["Check the probe cable is connected", "Compare with a second thermometer", "Ask for a probe check"]),
    "none": ("No fault detected", ["No action needed"]),
}


def tier_timeline(r: pd.DataFrame, th: dict[str, float]) -> list[tuple[str, str]]:
    """Tiers for one fridge, reading by reading, with memory: an Early warning starts after two readings above the
    threshold and ends only after 30 minutes well below it with the air back in range. Measured breaches are
    Critical and are never gated by a forecast."""
    air = r["air"].to_numpy()
    risk = {"freeze": r["risk_freeze"].to_numpy(), "heat": r["risk_heat"].to_numpy()}
    sensor = r["sensor"].to_numpy()
    early = {"freeze": False, "heat": False}
    out = []
    for i in range(len(r)):
        a6, a3, a2 = air[max(0, i - 5): i + 1], air[max(0, i - 2): i + 1], air[max(0, i - 1): i + 1]
        for k in ("freeze", "heat"):
            rk = risk[k][max(0, i - 2): i + 1]
            if len(rk) >= 2 and (rk[-2:] >= th[k]).all():
                early[k] = True
            in_range = (a3 >= 2.0).all() if k == "freeze" else (a3 <= 8.0).all()
            if early[k] and len(rk) == 3 and (rk < th[k] / 2).all() and in_range:
                early[k] = False
        if len(a6) == 6 and (a6 <= -0.5).all():
            out.append(("Critical", "freeze"))
        elif len(a3) == 3 and (a3 > 8).all():
            out.append(("Critical", "heat"))
        elif sensor[i]:
            out.append(("Sensor check", "sensor"))
        elif early["freeze"]:
            out.append(("Early warning", "freeze"))
        elif early["heat"]:
            out.append(("Early warning", "heat"))
        elif risk["freeze"][i] >= th["freeze"] / 2 or (len(a2) == 2 and (a2 < 2.0).all()):
            out.append(("Advisory", "freeze"))
        elif risk["heat"][i] >= th["heat"] / 2 or (len(a2) == 2 and (a2 > 8.0).all()):
            out.append(("Advisory", "heat"))
        else:
            out.append(("Normal", ""))
    return out


def message(tier: str, kind: str, row: pd.Series) -> str:
    if tier == "Critical":
        return "Air at or below −0.5 °C for an hour (measured)" if kind == "freeze" else \
            f"Air above +8 °C for 30 min (measured), now {row['air']:.1f} °C"
    if tier == "Sensor check":
        return "Probe reading unchanged for 3 h: check the sensor"
    if tier in ("Early warning", "Advisory") and kind == "freeze":
        p50 = row["ttb_f_p50"]
        if p50 == p50:
            return f"Vaccine may freeze in about {p50:.0f} min"
        if tier == "Early warning":
            return f"Cooling too hard: {row['risk_freeze']:.0%} chance of freezing within 2 h"
        return f"Air {row['air']:.1f} °C, below the 2 °C safe limit" if row["air"] < 2 else "Cooling too hard; freeze risk rising"
    if tier in ("Early warning", "Advisory") and kind == "heat":
        p50 = row["ttb_h_p50"]
        return f"Vaccine may pass +8 °C in about {p50:.0f} min" if p50 == p50 else "Warming; heat risk rising"
    return "Stable, within 2–8 °C"


def num(v) -> float | None:
    return None if v is None or v != v else float(v)


def lst(s: pd.Series) -> list:
    return [round(float(v), 3) for v in np.asarray(s, dtype=float)]
