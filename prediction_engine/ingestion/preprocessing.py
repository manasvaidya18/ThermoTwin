"""Feature engineering: per-reading features from what a real deployment can see (logged air temperature, the twin,
the clock).

No door, compressor or power signal is used: eVIN loggers report temperature only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURES = [
    "air", "d1", "d3", "d6", "min6", "max6", "std6", "std18", "stuck18",
    "air_f", "slope", "vial", "vial_sd", "innov", "abs_innov6",
    "air_fc3", "air_fc6", "air_fc12", "vial_fc3", "vial_fc6", "vial_fc12", "vial_to_zero", "vial_to_eight",
    "hour", "is_domestic",
    # 3-6 hour shape features (computed in add_long_window_features), so the model sees as much history as the LSTM
    "d18", "d36", "mean36_dev", "std36", "min36", "max36", "rise_share36", "flat36",
]


def build_features(log: pd.DataFrame, twin: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    df = log[["unit", "tick", "minute", "air_meas"]].merge(twin, on=["unit", "tick"]).sort_values(["unit", "tick"])
    g = df.groupby("unit")["air_meas"]
    air = g.transform(lambda s: s.ffill())
    df["air"] = air
    ga = air.groupby(df["unit"])
    df["d1"] = ga.diff(1)
    df["d3"] = ga.diff(3)
    df["d6"] = ga.diff(6)
    df["min6"] = ga.transform(lambda s: s.rolling(6, min_periods=1).min())
    df["max6"] = ga.transform(lambda s: s.rolling(6, min_periods=1).max())
    df["std6"] = ga.transform(lambda s: s.rolling(6, min_periods=2).std())
    df["std18"] = ga.transform(lambda s: s.rolling(18, min_periods=2).std())
    df["stuck18"] = (df["std18"] < 0.01).astype(float)
    df["abs_innov6"] = df["innov"].abs().groupby(df["unit"]).transform(lambda s: s.rolling(6, min_periods=1).mean())
    df["hour"] = (df["minute"] // 60) % 24
    df["is_domestic"] = df["unit"].map(units.set_index("unit")["cls"].eq("DOMESTIC").astype(float))
    return df.reset_index(drop=True)


def add_long_window_features(feat: pd.DataFrame) -> pd.DataFrame:
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


# Older name, kept so earlier scripts keep working
add_cause_features = add_long_window_features
