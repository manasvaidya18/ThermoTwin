"""Inference service: the ML side of ThermoTwin.

Fast loop (every reading): digital twin (Virtual Vial) -> freeze/heat risk -> cause classifier -> sensor check
                           -> door-opening recovery check.
Slow loop (rolling 24 h):  Cooling Health Index -> degradation model (days until service).

Input: fridge list and 10-minute readings. Output: one scored row per reading. Stateless apart from the loaded models.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from backend.common import config

# ML package (ml/thermotwin). The pickled models reference these module paths, so the package keeps its name.
from thermotwin.cause import add_cause_features, sensor_check  # noqa: E402
from thermotwin.degradation import DAY, window_features  # noqa: E402
from thermotwin.features import build_features  # noqa: E402
from thermotwin.recovery import frame_states  # noqa: E402
from thermotwin.twin import twin_frame  # noqa: E402

OUT_COLS = ["tick", "air", "vial", "vial_sd", "slope", "air_fc3", "air_fc6", "air_fc12", "vial_fc3", "vial_fc6",
            "vial_fc12"]


class InferenceService:
    def __init__(self, models_path: Path = config.MODELS_PATH) -> None:
        with open(models_path, "rb") as f:
            self.models = pickle.load(f)
        self.models_path = Path(models_path)

    def info(self) -> dict:
        return dict(models=[k for k in self.models if k != "thresholds"], thresholds=self.models["thresholds"],
                    path=str(self.models_path))

    def score(self, fridges: list[dict], readings: list[dict]) -> dict:
        ids = [f["id"] for f in fridges]
        units = pd.DataFrame({"unit": np.arange(len(ids)), "cls": [f["cls"] for f in fridges]})
        r = pd.DataFrame(readings)
        log = pd.DataFrame({"unit": r["fridge_id"].map({k: i for i, k in enumerate(ids)}).astype(int),
                            "tick": r["tick"].astype(int), "minute": r["minute"].astype(int),
                            "air_meas": pd.to_numeric(r["temp_c"], errors="coerce").astype(float)})
        log = log.sort_values(["unit", "tick"]).reset_index(drop=True)
        feat = add_cause_features(build_features(log, twin_frame(log, units), units))
        m = self.models
        rf, rh, cause = m["freeze"].predict(feat), m["heat"].predict(feat), m["cause"].predict(feat)
        out = feat[OUT_COLS].copy()
        out.insert(0, "fridge_id", [ids[u] for u in feat["unit"]])
        out = out.assign(
            risk_freeze=rf["risk12"].to_numpy(), risk_freeze1h=rf["risk6"].to_numpy(),
            ttb_f_p10=rf["ttb_p10"].to_numpy(), ttb_f_p50=rf["ttb_p50"].to_numpy(), ttb_f_p90=rf["ttb_p90"].to_numpy(),
            risk_heat=rh["risk12"].to_numpy(),
            ttb_h_p10=rh["ttb_p10"].to_numpy(), ttb_h_p50=rh["ttb_p50"].to_numpy(), ttb_h_p90=rh["ttb_p90"].to_numpy(),
            cause=cause["cause"].to_numpy(), cause_conf=cause["confidence"].to_numpy(),
            sensor=sensor_check(feat),
            recovery=frame_states(feat),
        )
        out = out.join(self._slow_loop(feat))
        return dict(thresholds={k: float(v) for k, v in m["thresholds"].items()}, rows=_records(out))


    def _slow_loop(self, feat: pd.DataFrame) -> pd.DataFrame:
        """Cooling Health Index and days-until-service at every reading, from the last 24 hours vs the unit's baseline.

        The baseline is the first 3 days of history (1 day when less than a week of history exists, as in the demo).
        Before one full day of history there is no estimate yet (None).
        """
        cols = ["health", "service_risk7", "days_to_service", "maintenance_due"]
        deg = self.models.get("degradation")
        empty = pd.DataFrame({c: np.nan for c in cols}, index=feat.index)
        if deg is None:
            return empty
        span = int(feat["tick"].max()) + 1
        w = window_features(feat, baseline_days=3 if span >= 7 * DAY else 1)
        assert (w["tick"].to_numpy() == feat["tick"].to_numpy()).all() and (w["unit"].to_numpy() == feat["unit"].to_numpy()).all()
        p = deg.predict(w)
        res = pd.DataFrame({"health": p["health"].to_numpy(), "service_risk7": p["service_risk7"].to_numpy(),
                            "days_to_service": p["days_to_service"].to_numpy(),
                            "maintenance_due": p["alert"].to_numpy().astype(float)}, index=feat.index)
        res[w["w_mean"].isna().to_numpy()] = np.nan          # no full day of history yet
        return res


def _records(df: pd.DataFrame) -> list[dict]:
    """JSON-safe rows: native Python types, NaN -> None."""
    cols = {c: [None if (isinstance(v, float) and v != v) else v for v in df[c].tolist()] for c in df.columns}
    return [dict(zip(cols, vals)) for vals in zip(*cols.values())]
