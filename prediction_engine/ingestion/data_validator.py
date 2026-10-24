"""Ingestion checks: validate incoming readings, and the rule-based sensor trust check.

validate_readings() is used for readings posted by devices (ESP32, eVIN feed) before they are stored.
sensor_check() flags a probe stuck for 3 h or readings missing for 1 h, so a broken probe raises "check the sensor"
instead of a false freeze alarm.
"""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd

TEMP_MIN, TEMP_MAX = -100.0, 70.0      # anything outside is a sensor or transmission error


def validate_readings(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Check {fridge_id, timestamp (ISO 8601), temp_c} rows. Returns (clean rows sorted by time, errors).

    temp_c may be None (missing reading). Duplicate timestamps for the same fridge keep the last value.
    """
    clean, errors, seen = [], [], {}
    for i, r in enumerate(rows):
        fid = r.get("fridge_id")
        if not fid:
            errors.append(f"row {i}: fridge_id missing")
            continue
        try:
            ts = datetime.fromisoformat(str(r.get("timestamp")).replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"row {i}: bad timestamp {r.get('timestamp')!r}")
            continue
        t = r.get("temp_c")
        if t is not None:
            try:
                t = float(t)
            except (TypeError, ValueError):
                errors.append(f"row {i}: temp_c not a number")
                continue
            if not TEMP_MIN <= t <= TEMP_MAX or t != t:
                errors.append(f"row {i}: temp_c {t} outside {TEMP_MIN}..{TEMP_MAX} °C")
                continue
        seen[(fid, ts)] = dict(fridge_id=fid, timestamp=ts, temp_c=t)
    clean = sorted(seen.values(), key=lambda x: (x["fridge_id"], x["timestamp"]))
    return clean, errors


def sensor_check(feat: pd.DataFrame) -> np.ndarray:
    """Rule-based Sensor check tier: a reading unchanged for 3 hours, or a missing reading streak of 1 hour."""
    stuck = feat["stuck18"].to_numpy() > 0
    missing = feat.groupby("unit")["air_meas"].transform(lambda s: s.isna().rolling(6, min_periods=1).sum()) >= 6
    return stuck | missing.to_numpy()
