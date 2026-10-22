"""End-to-end training and evaluation shared by the CLI and the API."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .benchmark import pick_threshold, run_benchmark
from .cause import CLASSES, CauseModel, active_fault, add_cause_features, sensor_check
from .features import build_features
from .labels import find_events, ticks_to_next_onset
from .model import HazardModel, hazard_rows
from .simulator import FleetConfig, simulate_fleet
from .twin import twin_frame


@dataclass
class Fleet:
    cfg: FleetConfig
    log: pd.DataFrame = field(repr=False)
    units: pd.DataFrame = field(repr=False)
    faults: list = field(repr=False)
    feat: pd.DataFrame = field(repr=False)
    split: dict = field(repr=False)

    @property
    def n(self) -> int:
        return self.cfg.n_units

    @property
    def T(self) -> int:
        return self.cfg.days * 144

    def part(self, name: str) -> pd.DataFrame:
        return self.feat[self.feat["unit"].isin(self.split[name])].reset_index(drop=True)

    def air_grid(self, units_: np.ndarray) -> np.ndarray:
        return self.log.sort_values(["unit", "tick"])["air_meas"].to_numpy().reshape(self.n, self.T)[units_]

    def grid(self, pred: pd.DataFrame, col: str, units_: np.ndarray) -> np.ndarray:
        g = np.zeros((self.n, self.T))
        g[pred["unit"], pred["tick"]] = pred[col]
        return g[units_]

    @staticmethod
    def remap(ev: pd.DataFrame, units_: np.ndarray) -> pd.DataFrame:
        pos = {u: i for i, u in enumerate(units_)}
        ev = ev[ev["unit"].isin(units_)].copy()
        ev["unit"] = ev["unit"].map(pos)
        return ev


def build_fleet(cfg: FleetConfig) -> Fleet:
    log, units, faults = simulate_fleet(cfg)
    feat = add_cause_features(build_features(log, twin_frame(log, units), units))
    rng = np.random.default_rng(cfg.seed)
    perm = rng.permutation(cfg.n_units)
    n = cfg.n_units
    split = {"train": perm[: int(0.6 * n)], "val": perm[int(0.6 * n): int(0.8 * n)], "test": perm[int(0.8 * n):]}
    return Fleet(cfg, log, units, faults, feat, split)


def train_risk(fleet: Fleet, kind: str, seed: int = 0) -> dict:
    """Train, calibrate and benchmark the hazard model for 'freeze' or 'heat'."""
    rng = np.random.default_rng(seed)
    events = find_events(fleet.log.attrs["prod_min"], kind)
    to_next, in_event = ticks_to_next_onset(events, fleet.n, fleet.T)
    X, y, w = hazard_rows(fleet.part("train"), to_next, in_event, rng)
    model = HazardModel().fit(X, y, w)
    val = fleet.part("val")
    model.calibrate(val, to_next, in_event)
    pv = model.predict(val)
    sv = fleet.split["val"]
    th = pick_threshold(fleet.air_grid(sv), fleet.remap(events, sv), fleet.grid(pv, "risk12", sv),
                        fleet.cfg.days, budget=0.8, kind=kind)  # 20% safety margin under the 1.0 budget
    test = fleet.part("test")
    pt = model.predict(test)
    st = fleet.split["test"]
    ev_test = fleet.remap(events, st)
    bench = run_benchmark(fleet.air_grid(st), ev_test, fleet.grid(pt, "risk12", st), th, fleet.cfg.days, kind)
    bench.insert(0, "kind", kind)
    return dict(model=model, threshold=th, bench=bench, events=len(events), test_events=len(ev_test),
                onsets=int(y.sum()), rows=len(X), pred_test=pt)


def train_cause(fleet: Fleet, seed: int = 0) -> dict:
    """Train the cause classifier and score it on held-out fridges, overall and at the ticks where alerts fire."""
    rng = np.random.default_rng(seed)
    lab = active_fault(fleet.faults, fleet.n, fleet.T)
    cm = CauseModel().fit(fleet.part("train"), lab, rng)
    test = fleet.part("test")
    from .cause import manifest_mask
    m = manifest_mask(test, lab)
    truth = lab[test["unit"].to_numpy(), test["tick"].to_numpy()]
    pred = cm.predict(test)
    acc = float((pred["cause"].to_numpy()[m] == truth[m]).mean())
    conf = pd.crosstab(pd.Series(truth[m], name="true"), pd.Series(pred["cause"].to_numpy()[m], name="predicted"),
                       normalize="index").reindex(index=CLASSES, columns=CLASSES).fillna(0)
    sc = sensor_check(test)
    is_sensor = truth == "sensor_fault"
    sensor_recall = float(sc[is_sensor].mean()) if is_sensor.any() else float("nan")
    sensor_fp = float(sc[truth == "none"].mean())
    return dict(model=cm, accuracy=acc, confusion=conf, sensor_rule_recall=sensor_recall,
                sensor_rule_false_rate=sensor_fp, labels=lab)
