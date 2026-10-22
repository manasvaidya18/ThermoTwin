"""Per-tick features from what a real deployment can see: the logged air temperature, the twin, and the clock.

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
    # 3-6 hour shape features (computed in cause.add_cause_features), so the model sees as much history as the LSTM
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
