"""Explainable predictions: turn SHAP contributions of the risk model into plain-language reasons.

LightGBM gives exact SHAP values (pred_contrib). For each reading we take the features that pushed the risk up most
and phrase them with the feature's actual value, e.g. "air forecast -0.1 °C in 1 h; fell 2.3 °C over 3 h".
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from prediction_engine.ingestion.preprocessing import FEATURES

PHRASES = {
    "air": "air now {v:.1f} °C",
    "air_f": "air (filtered) {v:.1f} °C",
    "d1": "changed {v:+.1f} °C in the last 10 min",
    "d3": "changed {v:+.1f} °C over 30 min",
    "d6": "changed {v:+.1f} °C over 1 h",
    "d18": "changed {v:+.1f} °C over 3 h",
    "d36": "changed {v:+.1f} °C over 6 h",
    "min6": "lowest reading in the last hour {v:.1f} °C",
    "max6": "highest reading in the last hour {v:.1f} °C",
    "min36": "lowest reading in 6 h {v:.1f} °C",
    "max36": "highest reading in 6 h {v:.1f} °C",
    "std6": "jumpy over the last hour",
    "std18": "unsteady over 3 h",
    "std36": "unsteady over 6 h",
    "slope": "trend {v:+.2f} °C per 10 min",
    "vial": "vaccine estimate {v:.1f} °C",
    "vial_sd": "uncertain vaccine estimate",
    "innov": "reading {v:+.1f} °C off the twin's forecast",
    "abs_innov6": "readings keep surprising the twin",
    "air_fc3": "air forecast {v:.1f} °C in 30 min",
    "air_fc6": "air forecast {v:.1f} °C in 1 h",
    "air_fc12": "air forecast {v:.1f} °C in 2 h",
    "vial_fc3": "vaccine forecast {v:.1f} °C in 30 min",
    "vial_fc6": "vaccine forecast {v:.1f} °C in 1 h",
    "vial_fc12": "vaccine forecast {v:.1f} °C in 2 h",
    "vial_to_zero": "twin: vaccine reaches 0 °C in about {m:.0f} min",
    "vial_to_eight": "twin: vaccine passes 8 °C in about {m:.0f} min",
    "mean36_dev": "{v:+.1f} °C from this unit's normal",
    "rise_share36": "mostly rising over 6 h",
    "flat36": "readings flat over 6 h",
    "stuck18": "reading unchanged for 3 h",
    "hour": "time of day",
    "is_domestic": "domestic fridge (less thermal mass)",
}


def _phrase(name: str, v: float) -> str | None:
    t = PHRASES.get(name)
    if t is None or v != v:
        return None
    if name in ("vial_to_zero", "vial_to_eight"):
        return None if v >= 13 else t.format(m=v * 10)
    return t.format(v=v)


def reasons(model, feat: pd.DataFrame, slot: int = 6, top: int = 2) -> list[str]:
    """Top reasons pushing the risk up, for every row of feat (one string per row, '' if nothing stands out)."""
    if model is None or getattr(model, "model", None) is None or feat.empty:
        return [""] * len(feat)
    X = feat[FEATURES].assign(k=slot)
    contrib = model.model.booster_.predict(X, pred_contrib=True)[:, :-1]     # drop the bias column
    names = list(X.columns)
    vals = X.to_numpy(dtype=float)
    order = np.argsort(-contrib, axis=1)[:, : top + 3]
    out = []
    for i in range(len(X)):
        parts = []
        for j in order[i]:
            if contrib[i, j] <= 0.05 or names[j] == "k":
                continue
            p = _phrase(names[j], vals[i, j])
            if p:
                parts.append(p)
            if len(parts) == top:
                break
        out.append("; ".join(parts))
    return out
