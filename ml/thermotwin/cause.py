"""Cause classifier and sensor-check tier.

Cause labels come only from the fault the simulator injected; ThermoTwin's own rules never produce labels.
The classifier uses temperature-only features over 1-6 hours plus the twin, and outputs a Cause Card category.
"""
from __future__ import annotations

import lightgbm as lgb
import numpy as np
import pandas as pd

from .features import FEATURES

LOG_EVERY = 10
# Cause Card wording per class. Thermostat-too-cold and relay-stuck-on look alike from temperature alone, so they
# share one card and the steps cover both.
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
GROUP = {"thermostat_cold": "cooling_too_hard", "relay_stuck_on": "cooling_too_hard", "power_cut": "power_cut",
         "compressor_wear": "weak_cooling", "gasket_leak": "weak_cooling", "sensor_stuck": "sensor_fault",
         "sensor_drift": "sensor_fault"}
CLASSES = list(CARD)
CAUSE_FEATURES = list(dict.fromkeys(FEATURES + ["d18", "d36", "mean36_dev", "std36", "min36", "max36", "rise_share36", "flat36"]))


def add_cause_features(feat: pd.DataFrame) -> pd.DataFrame:
    """Longer-window (3-6 h) shape features, relative to each fridge's own first-day normal."""
    f = feat.copy()
    g = f.groupby("unit")["air"]
    base = f[f["tick"] < 144].groupby("unit")["air"].median()
    f["d18"] = g.diff(18)
    f["d36"] = g.diff(36)
    f["mean36_dev"] = g.transform(lambda s: s.rolling(36, min_periods=6).mean()) - f["unit"].map(base)
    f["std36"] = g.transform(lambda s: s.rolling(36, min_periods=6).std())
    f["min36"] = g.transform(lambda s: s.rolling(36, min_periods=6).min())
    f["max36"] = g.transform(lambda s: s.rolling(36, min_periods=6).max())
    up = (g.diff() > 0).astype(float)
    f["rise_share36"] = up.groupby(f["unit"]).transform(lambda s: s.rolling(36, min_periods=6).mean())
    f["flat36"] = (g.diff().abs() < 0.05).astype(float).groupby(f["unit"]).transform(
        lambda s: s.rolling(36, min_periods=6).mean())
    return f


def active_fault(faults: list[list[dict]], n_units: int, n_ticks: int) -> np.ndarray:
    """(n_units, n_ticks) array of the injected fault group active at each tick ('none' if none)."""
    lab = np.full((n_units, n_ticks), "none", dtype=object)
    for u, fl in enumerate(faults):
        for f in fl:
            s, e = f["start"] // LOG_EVERY, min(f["end"] // LOG_EVERY, n_ticks)
            lab[u, s:e] = GROUP[f["kind"]]
    return lab


def manifest_mask(feat: pd.DataFrame, lab: np.ndarray) -> np.ndarray:
    """Ticks where a fault is visible in the data (or clearly normal), so the classifier learns real signatures."""
    u, t = feat["unit"].to_numpy(), feat["tick"].to_numpy()
    y = lab[u, t]
    dev = feat["mean36_dev"].abs().fillna(0).to_numpy()
    visible = (y != "none") & ((dev > 0.8) | (y == "sensor_fault") | (feat["d18"].abs().fillna(0).to_numpy() > 1.5))
    normal = (y == "none") & (dev < 0.5)
    return visible | normal


class CauseModel:
    def __init__(self) -> None:
        self.model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=40,
                                        class_weight="balanced", subsample=0.8, subsample_freq=1,
                                        colsample_bytree=0.8, verbose=-1)

    def fit(self, feat: pd.DataFrame, lab: np.ndarray, rng: np.random.Generator) -> "CauseModel":
        m = manifest_mask(feat, lab)
        y = lab[feat["unit"].to_numpy(), feat["tick"].to_numpy()]
        keep = m & ((y != "none") | (rng.random(len(feat)) < 0.1))
        self.model.fit(feat.loc[keep, CAUSE_FEATURES], y[keep])
        return self

    def predict(self, feat: pd.DataFrame) -> pd.DataFrame:
        proba = self.model.predict_proba(feat[CAUSE_FEATURES])
        cls = self.model.classes_
        out = pd.DataFrame(proba, columns=cls, index=feat.index)
        out["cause"] = cls[proba.argmax(axis=1)]
        out["confidence"] = proba.max(axis=1)
        return out


def sensor_check(feat: pd.DataFrame) -> np.ndarray:
    """Rule-based Sensor check tier: a reading unchanged for 3 hours, or a missing reading streak of 1 hour."""
    stuck = feat["stuck18"].to_numpy() > 0
    missing = feat.groupby("unit")["air_meas"].transform(lambda s: s.isna().rolling(6, min_periods=1).sum()) >= 6
    return stuck | missing.to_numpy()
