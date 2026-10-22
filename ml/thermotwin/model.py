"""LightGBM discrete-time hazard model.

For each tick t and each future slot k = 1..12 (10-minute slots, 2 hours), the model estimates
    h_k = P(event starts in slot k | no event before slot k, features at t).
Cumulative risk by slot k: 1 - prod_{j<=k} (1 - h_j). Time-to-breach quantiles are read off that curve.
The 1- and 2-hour cumulative risks are then calibrated with isotonic regression on held-out fridges.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from .features import FEATURES

K = 12


def hazard_rows(feat: pd.DataFrame, to_next: np.ndarray, in_event: np.ndarray, rng: np.random.Generator,
                far_keep: float = 0.06) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Expand ticks into (tick, slot) rows. Ticks far from any onset are subsampled and re-weighted."""
    u, t = feat["unit"].to_numpy(), feat["tick"].to_numpy()
    tn = to_next[u, t]
    ok = ~in_event[u, t]
    near = tn <= 2 * K
    keep = ok & (near | (rng.random(len(feat)) < far_keep))
    base = feat.loc[keep, FEATURES].reset_index(drop=True)
    tn_k = tn[keep]
    w_tick = np.where(tn_k <= 2 * K, 1.0, 1.0 / far_keep)
    X, y, w = [], [], []
    for k in range(1, K + 1):
        alive = tn_k >= k            # no onset before slot k
        Xi = base[alive].copy()
        Xi["k"] = k
        X.append(Xi)
        y.append((tn_k[alive] == k).astype(np.int8))
        w.append(w_tick[alive])
    return pd.concat(X, ignore_index=True), np.concatenate(y), np.concatenate(w)


@dataclass
class HazardModel:
    params: dict = field(default_factory=lambda: dict(
        n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=50,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, verbose=-1))
    model: lgb.LGBMClassifier | None = None
    cal: dict = field(default_factory=dict)

    def fit(self, X: pd.DataFrame, y: np.ndarray, w: np.ndarray) -> "HazardModel":
        self.model = lgb.LGBMClassifier(**self.params)
        self.model.fit(X, y, sample_weight=w)
        return self

    def hazards(self, feat: pd.DataFrame) -> np.ndarray:
        """(n_ticks, K) per-slot hazards."""
        base = feat[FEATURES].reset_index(drop=True)
        rows = pd.concat([base.assign(k=k) for k in range(1, K + 1)], ignore_index=True)
        h = self.model.predict_proba(rows)[:, 1]
        return h.reshape(K, len(base)).T

    def risk_curve(self, feat: pd.DataFrame) -> np.ndarray:
        h = self.hazards(feat)
        return 1.0 - np.cumprod(1.0 - h, axis=1)

    def calibrate(self, feat: pd.DataFrame, to_next: np.ndarray, in_event: np.ndarray) -> None:
        """Isotonic calibration of 1-h and 2-h risk on held-out fridges.

        Ticks inside an ongoing event (or its recovery window) are excluded, exactly as in training: there the
        question "will a new event start soon?" does not apply.
        """
        u, t = feat["unit"].to_numpy(), feat["tick"].to_numpy()
        ok = ~in_event[u, t]
        curve = self.risk_curve(feat[ok])
        tn = to_next[u[ok], t[ok]]
        for k in (6, 12):
            iso = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1)
            iso.fit(curve[:, k - 1], (tn <= k).astype(float))
            self.cal[k] = iso

    def predict(self, feat: pd.DataFrame) -> pd.DataFrame:
        curve = self.risk_curve(feat)
        out = pd.DataFrame({"unit": feat["unit"].to_numpy(), "tick": feat["tick"].to_numpy()})
        for k in (6, 12):
            raw = curve[:, k - 1]
            out[f"risk{k}"] = self.cal[k].predict(raw) if k in self.cal else raw
        # Time to breach (minutes) at the 10th / 50th / 90th percentile of the event-time distribution
        for q, name in ((0.1, "ttb_p10"), (0.5, "ttb_p50"), (0.9, "ttb_p90")):
            idx = (curve >= q).argmax(axis=1)
            reached = curve[np.arange(len(curve)), idx] >= q
            out[name] = np.where(reached, (idx + 1) * 10.0, np.nan)
        return out

    def explain(self, feat_row: pd.DataFrame, k: int = 6) -> pd.Series:
        """SHAP contributions (log-odds) for one tick at slot k, largest first."""
        X = feat_row[FEATURES].assign(k=k)
        contrib = self.model.booster_.predict(X, pred_contrib=True)[0][:-1]
        return pd.Series(contrib, index=list(X.columns)).sort_values(key=np.abs, ascending=False)
