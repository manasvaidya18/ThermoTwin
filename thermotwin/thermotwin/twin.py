"""Digital twin: a Kalman filter per fridge that estimates the vaccine temperature (Virtual Vial) from air readings.

State x = [T_air, slope, T_vial] per 10-minute tick.
    T_air'  = T_air + slope                      (local trend)
    slope'  = phi * slope                        (damped, so forecasts level off)
    T_vial' = T_vial + a * (T_air - T_vial),     a = 1 - exp(-dt / tau)   (Newton's law of cooling)
Only T_air is measured. tau comes from the fridge's equipment-class prior (fleet prior) and can be refitted per fridge.
Vectorised over fridges: every array has a leading fridge axis.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DT_MIN = 10.0
TAU_PRIOR = {"ILR": 60.0, "DOMESTIC": 60.0}   # product time constant, minutes
PHI = 0.85
Q = np.diag([0.30 ** 2, 0.06 ** 2, 0.045 ** 2])
R_MEAS = 0.12 ** 2
HORIZONS = (3, 6, 12)                           # forecast steps: 30, 60, 120 min


def _transition(a: np.ndarray) -> np.ndarray:
    n = a.size
    F = np.zeros((n, 3, 3))
    F[:, 0, 0] = 1.0
    F[:, 0, 1] = 1.0
    F[:, 1, 1] = PHI
    F[:, 2, 0] = a
    F[:, 2, 2] = 1.0 - a
    return F


def run_twin(air: np.ndarray, tau_min: np.ndarray) -> dict[str, np.ndarray]:
    """Filter a block of fridges.

    air: (n_units, n_ticks) measured air temperature, NaN for missing readings.
    tau_min: (n_units,) product time constant in minutes.
    Returns arrays of shape (n_units, n_ticks): filtered air, slope, vial estimate, vial std, innovation,
    and physics forecasts of air and vial at each horizon.
    """
    n, T = air.shape
    a = 1.0 - np.exp(-DT_MIN / tau_min)
    F = _transition(a)
    Ft = np.transpose(F, (0, 2, 1))
    first = np.where(np.isnan(air[:, 0]), np.nanmean(air[:, :6], axis=1), air[:, 0])
    x = np.stack([first, np.zeros(n), first], axis=1)
    P = np.tile(np.diag([0.5, 0.1, 1.0]), (n, 1, 1))

    out = {k: np.zeros((n, T)) for k in ("air_f", "slope", "vial", "vial_sd", "innov")}
    for h in HORIZONS:
        out[f"air_fc{h}"] = np.zeros((n, T))
        out[f"vial_fc{h}"] = np.zeros((n, T))
    out["vial_to_zero"] = np.zeros((n, T))   # steps until the forecast vial reaches 0 °C (13 = not within 2 h)
    out["vial_to_eight"] = np.zeros((n, T))  # steps until the forecast vial passes +8 °C (13 = not within 2 h)

    for t in range(T):
        # Predict
        x = np.einsum("nij,nj->ni", F, x)
        P = F @ P @ Ft + Q
        z = air[:, t]
        has = ~np.isnan(z)
        innov = np.where(has, z - x[:, 0], 0.0)
        S = P[:, 0, 0] + R_MEAS
        K = P[:, :, 0] / S[:, None]
        K[~has] = 0.0
        x = x + K * innov[:, None]
        P = P - K[:, :, None] * P[:, 0, :][:, None, :]

        out["air_f"][:, t] = x[:, 0]
        out["slope"][:, t] = x[:, 1]
        out["vial"][:, t] = x[:, 2]
        out["vial_sd"][:, t] = np.sqrt(np.maximum(P[:, 2, 2], 0))
        out["innov"][:, t] = innov

        # Physics forecast: roll the mean forward with no new data
        xf = x.copy()
        reach = np.full(n, 13.0)
        hot = np.full(n, 13.0)
        for step in range(1, 13):
            xf = np.einsum("nij,nj->ni", F, xf)
            reach = np.where((reach == 13) & (xf[:, 2] <= 0.0), step, reach)
            hot = np.where((hot == 13) & (xf[:, 2] > 8.0), step, hot)
            if step in HORIZONS:
                out[f"air_fc{step}"][:, t] = xf[:, 0]
                out[f"vial_fc{step}"][:, t] = xf[:, 2]
        out["vial_to_zero"][:, t] = reach
        out["vial_to_eight"][:, t] = hot
    return out


def twin_frame(log: pd.DataFrame, units: pd.DataFrame, tau_override: dict | None = None) -> pd.DataFrame:
    """Run the twin for every fridge in a simulator log and return its outputs aligned to the log rows."""
    n = units.shape[0]
    T = int(log["tick"].max()) + 1
    air = log.sort_values(["unit", "tick"])["air_meas"].to_numpy().reshape(n, T)
    tau = units["cls"].map(tau_override or TAU_PRIOR).to_numpy(dtype=float)
    res = run_twin(air, tau)
    df = pd.DataFrame({k: v.ravel() for k, v in res.items()})
    df.insert(0, "unit", np.repeat(np.arange(n), T))
    df.insert(1, "tick", np.tile(np.arange(T), n))
    return df
