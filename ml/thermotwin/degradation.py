"""Slow loop: Cooling Health Index and days-until-service prediction (third LightGBM).

Gradual faults (compressor wear, leaking door seal) take days to weeks. The thermostat compensates by running the
compressor longer, so the temperature only creeps up: the unit runs warmer than its own normal, most at its warmest
moments. We measure that from temperature alone over rolling 24-hour windows, against the unit's own first-day
baseline, and learn how many days remain before it can no longer keep the vaccine below +8 °C.

  Cooling Health Index (0-100) = 100 - 25 x (how far the unit's 24-hour 90th-percentile air temperature sits above its
                                 own baseline, in °C, averaged over 3 days); 1 °C warmer = 75, 4 °C warmer = 0.
  Degradation model: LightGBM discrete-time hazard over the next 14 days (daily slots), on window features and their
                     3- and 7-day trends. Outputs the chance of a degradation failure within 7 and 14 days and an
                     estimated number of days (P50).

Labels (simulator): the first heat event (vaccine > 8 °C for 60 min) that starts while compressor wear or a gasket
leak is active. In deployment the labels would come from repair records (date the unit was serviced).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

DAY = 144          # 10-minute readings per day
K_DAYS = 14
DEG_FAULTS = ("compressor_wear", "gasket_leak")

DEV_COLS = ["w_mean", "w_p90", "w_max", "w_p10", "w_std", "w_pm", "w_fall", "w_rise"]
DEG_FEATURES = ([c + "_dev" for c in DEV_COLS] + ["w_absinnov", "w_hot_share", "health"]
                + ["mean_dev_d3", "p90_dev_d3", "mean_dev_d7", "p90_dev_d7", "is_domestic"])


def window_features(feat: pd.DataFrame, baseline_days: int = 3) -> pd.DataFrame:
    """Rolling 24-hour statistics at every reading, relative to the unit's own baseline.

    Baseline = median of the unit's first `baseline_days` full days (after installation or a service).
    feat needs: unit, tick, air, d1, innov, hour, is_domestic. Rows with less than one day of history get NaN.
    """
    f = feat[["unit", "tick", "air", "d1", "innov", "hour", "is_domestic"]].sort_values(["unit", "tick"]).reset_index(drop=True)
    g = f.groupby("unit")["air"]
    roll = lambda s, fn: getattr(s.rolling(DAY, min_periods=DAY), fn)()  # noqa: E731
    w = pd.DataFrame({"unit": f["unit"], "tick": f["tick"], "is_domestic": f["is_domestic"]})
    w["w_mean"] = g.transform(lambda s: roll(s, "mean"))
    w["w_p90"] = g.transform(lambda s: s.rolling(DAY, min_periods=DAY).quantile(0.9))
    w["w_p10"] = g.transform(lambda s: s.rolling(DAY, min_periods=DAY).quantile(0.1))
    w["w_max"] = g.transform(lambda s: roll(s, "max"))
    w["w_std"] = g.transform(lambda s: roll(s, "std"))
    pm = f["air"].where(f["hour"].between(12, 17))          # afternoon, when the room is hottest
    w["w_pm"] = pm.groupby(f["unit"]).transform(lambda s: s.rolling(DAY, min_periods=DAY // 6).mean())
    # strength of the cooling dips (10th percentile of 10-minute changes) and of the warming steps
    gd = f.groupby("unit")["d1"]
    w["w_fall"] = gd.transform(lambda s: s.rolling(DAY, min_periods=DAY).quantile(0.1))
    w["w_rise"] = gd.transform(lambda s: s.rolling(DAY, min_periods=DAY).quantile(0.9))
    w["w_absinnov"] = f["innov"].abs().groupby(f["unit"]).transform(lambda s: roll(s, "mean"))
    # baseline = median over the unit's first full days
    ends = [(d + 1) * DAY - 1 for d in range(baseline_days)]
    base = w[w["tick"].isin(ends)].groupby("unit")[DEV_COLS].median()
    for c in DEV_COLS:
        w[c + "_dev"] = w[c] - w["unit"].map(base[c])
    hot = (f["air"] > f["unit"].map(base["w_p90"])).astype(float)
    w["w_hot_share"] = hot.groupby(f["unit"]).transform(lambda s: roll(s, "mean"))
    w.loc[w["w_mean"].isna(), "w_hot_share"] = np.nan
    gu = w.groupby("unit")
    p90_3d = gu["w_p90_dev"].transform(lambda s: s.rolling(3 * DAY, min_periods=1).mean())
    w["health"] = (100 - 25 * p90_3d.clip(lower=0)).clip(0, 100)
    for c, short in (("w_mean_dev", "mean_dev"), ("w_p90_dev", "p90_dev")):
        for d in (3, 7):
            w[f"{short}_d{d}"] = (w[c] - gu[c].shift(d * DAY)) / d
    return w


def failure_days(heat_events: pd.DataFrame, faults: list[list[dict]], n_units: int) -> np.ndarray:
    """Day of the first degradation-caused heat failure per unit (inf if none)."""
    out = np.full(n_units, np.inf)
    for r in heat_events.itertuples():
        if any(f["kind"] in DEG_FAULTS and f["start"] <= r.onset_min < f["end"] for f in faults[r.unit]):
            out[r.unit] = min(out[r.unit], r.onset_min // 1440)
    return out


def daily_rows(w: pd.DataFrame) -> pd.DataFrame:
    """One row per unit per day, at the last reading of the day, after the baseline period."""
    d = w[(w["tick"] % DAY == DAY - 1) & (w["tick"] >= 3 * DAY - 1)].copy()
    d["day"] = d["tick"] // DAY
    return d.reset_index(drop=True)


@dataclass
class DegradationModel:
    params: dict = field(default_factory=lambda: dict(
        n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=30, subsample=0.8,
        subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0, verbose=-1))
    model: lgb.LGBMClassifier | None = None
    cal: IsotonicRegression | None = None
    threshold: float = 0.5

    @staticmethod
    def hazard_rows(days: pd.DataFrame, fail_day: np.ndarray, horizon_end: int):
        X, y = [], []
        dtf = fail_day[days["unit"].to_numpy()] - days["day"].to_numpy()
        ok = dtf > 0
        base = days.loc[ok, DEG_FEATURES].reset_index(drop=True)
        dtf, day = dtf[ok], days["day"].to_numpy()[ok]
        for k in range(1, K_DAYS + 1):
            known = (day + k <= horizon_end) | (dtf <= k)       # outcome observed within the simulation
            alive = (dtf >= k) & known
            Xi = base[alive].copy()
            Xi["k"] = k
            X.append(Xi)
            y.append((dtf[alive] == k).astype(np.int8))
        return pd.concat(X, ignore_index=True), np.concatenate(y)

    def fit(self, days: pd.DataFrame, fail_day: np.ndarray, horizon_end: int) -> "DegradationModel":
        X, y = self.hazard_rows(days, fail_day, horizon_end)
        self.model = lgb.LGBMClassifier(**self.params).fit(X, y)
        return self

    def risk_curve(self, days: pd.DataFrame) -> np.ndarray:
        base = days[DEG_FEATURES].reset_index(drop=True)
        rows = pd.concat([base.assign(k=k) for k in range(1, K_DAYS + 1)], ignore_index=True)
        h = self.model.predict_proba(rows)[:, 1].reshape(K_DAYS, len(base)).T
        return 1.0 - np.cumprod(1.0 - h, axis=1)

    def calibrate(self, days: pd.DataFrame, fail_day: np.ndarray, horizon_end: int) -> None:
        dtf = fail_day[days["unit"].to_numpy()] - days["day"].to_numpy()
        ok = (dtf > 0) & ((days["day"].to_numpy() + 7 <= horizon_end) | (dtf <= 7))
        curve = self.risk_curve(days[ok])
        self.cal = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(curve[:, 6], (dtf[ok] <= 7).astype(float))

    def predict(self, days: pd.DataFrame) -> pd.DataFrame:
        curve = self.risk_curve(days)
        out = pd.DataFrame({"unit": days["unit"].to_numpy(), "tick": days["tick"].to_numpy()})
        out["score7"] = curve[:, 6]                       # raw score: used for the alert threshold (finer grained)
        out["service_risk7"] = self.cal.predict(curve[:, 6]) if self.cal is not None else curve[:, 6]
        out["alert"] = out["score7"] >= self.threshold
        out["service_risk14"] = curve[:, 13]
        idx = (curve >= 0.5).argmax(axis=1)
        out["days_to_service"] = np.where(curve[np.arange(len(curve)), idx] >= 0.5, idx + 1.0, np.nan)
        out["health"] = days["health"].to_numpy()
        return out
