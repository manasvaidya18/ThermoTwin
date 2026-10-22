"""Live demo engine: scripted fridges from the UI, scored by the trained models, replayed on a demo clock.

Everything shown comes from the simulator plus the real twin, risk and cause models; nothing is hand-typed.
Alert tiers follow the PRD's Guardian rules: measured breaches are Critical and are never gated by a forecast.
"""
from __future__ import annotations

import pickle
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .cause import CARD, add_cause_features, sensor_check
from .features import build_features
from .simulator import FleetConfig, simulate_fleet
from .twin import twin_frame
from .vaccines import adjust_tier, freeze_sensitive_stock

DAY = 1440
MODELS = Path(__file__).resolve().parent.parent / "outputs" / "models.pkl"

# Demo fridges (ids match the UI). Fault times are minutes from the start of the 3-day scenario.
DEMO = [
    dict(id="wagholi-ilr1", stock=["Pentavalent", "Hepatitis B", "OPV", "MR"], facility="PHC Wagholi", fridge="ILR-1", taluka="Haveli", cls="ILR", setpoint=4.6, amb_base=31,
         faults=[dict(kind="thermostat_cold", start=2 * DAY + 120, end=3 * DAY, setpoint=-3.0, ramp=90)]),
    dict(id="junnar-ilr01", stock=["Pentavalent", "BCG"], facility="Junnar PHC-2", fridge="ILR-01", taluka="Junnar", cls="DOMESTIC", setpoint=4.8,
         amb_base=34, faults=[dict(kind="power_cut", start=2 * DAY + 400, end=2 * DAY + 560)]),
    dict(id="baramati-df01", stock=["PCV", "IPV"], facility="Baramati SDH", fridge="FR-01", taluka="Baramati", cls="DOMESTIC", setpoint=5.0,
         amb_base=35, faults=[dict(kind="compressor_wear", start=DAY, end=3 * DAY, rate=0.32)]),
    dict(id="khed-ilr03", stock=["Td", "MR"], facility="Khed PHC", fridge="ILR-03", taluka="Khed", cls="ILR", setpoint=4.8, amb_base=30,
         faults=[dict(kind="sensor_stuck", start=2 * DAY + 300, end=3 * DAY)]),
    dict(id="shirur-ilr01", stock=["OPV", "MR", "BCG"], facility="Shirur RH", fridge="ILR-01", taluka="Shirur", cls="ILR", setpoint=3.0, amb_base=33,
         faults=[]),
    dict(id="lonikand-ilr2", stock=["Pentavalent", "Rotavirus"], facility="PHC Lonikand", fridge="ILR-2", taluka="Haveli", cls="ILR", setpoint=4.5,
         amb_base=30, faults=[]),
]
START_TICK = 2 * 144 + 40      # demo clock starts at day 3, 06:40: Wagholi still Normal, early warning about 8 ticks later
END_TICK = 3 * 144 - 1


@dataclass
class Clock:
    start: int = START_TICK
    tick: int = START_TICK
    playing: bool = False
    seconds_per_tick: float = 2.0
    _t0: float = 0.0
    _tick0: int = START_TICK

    def now(self) -> int:
        if self.playing:
            self.tick = min(END_TICK, self._tick0 + int((time.time() - self._t0) / self.seconds_per_tick))
        return self.tick

    def play(self) -> None:
        self._tick0, self._t0, self.playing = self.now(), time.time(), True

    def pause(self) -> None:
        self.now()
        self.playing = False

    def reset(self) -> None:
        self.playing, self.tick = False, self.start

    def step(self, ticks: int) -> None:
        self.tick = int(np.clip(self.now() + ticks, 0, END_TICK))
        self._tick0, self._t0 = self.tick, time.time()


class LiveEngine:
    def __init__(self, models_path: Path = MODELS, seed: int = 7) -> None:
        with open(models_path, "rb") as f:
            m = pickle.load(f)
        self.models = m
        cfg = FleetConfig(days=3, seed=seed, units_spec=[{k: v for k, v in d.items() if k not in ("id", "stock")} for d in DEMO])
        log, units, _ = simulate_fleet(cfg)
        feat = add_cause_features(build_features(log, twin_frame(log, units), units))
        risk_f = m["freeze"].predict(feat)
        risk_h = m["heat"].predict(feat)
        cause = m["cause"].predict(feat)
        self.T = 3 * 144
        self.feat = feat.assign(
            risk_freeze=risk_f["risk12"].to_numpy(), risk_freeze1h=risk_f["risk6"].to_numpy(),
            ttb_f_p10=risk_f["ttb_p10"].to_numpy(), ttb_f_p50=risk_f["ttb_p50"].to_numpy(), ttb_f_p90=risk_f["ttb_p90"].to_numpy(),
            risk_heat=risk_h["risk12"].to_numpy(),
            ttb_h_p10=risk_h["ttb_p10"].to_numpy(), ttb_h_p50=risk_h["ttb_p50"].to_numpy(), ttb_h_p90=risk_h["ttb_p90"].to_numpy(),
            cause=cause["cause"].to_numpy(), cause_conf=cause["confidence"].to_numpy(),
            sensor=sensor_check(feat),
        )
        self.ids = [d["id"] for d in DEMO]
        self.meta = {d["id"]: d for d in DEMO}
        self.clock = Clock()
        self._tiers = {}
        for u in range(len(DEMO)):
            self._tiers[u] = self._tiers_for(self.feat[self.feat["unit"] == u].sort_values("tick"))

    # ---- helpers -------------------------------------------------------------------------------------------------
    def _rows(self, fid: str) -> pd.DataFrame:
        u = self.ids.index(fid)
        return self.feat[self.feat["unit"] == u].set_index("tick", drop=False).rename_axis(None)

    @staticmethod
    def _clock_label(tick: int) -> str:
        minutes = (tick + 1) * 10
        day, rem = divmod(minutes, DAY)
        return f"Day {day + 1}, {rem // 60:02d}:{rem % 60:02d}"

    def _tiers_for(self, r: pd.DataFrame) -> list[tuple[str, str]]:
        """Guardian tiers for one fridge, tick by tick, with memory (as in the benchmark's P3 policy):
        an Early warning starts after two readings above the threshold and ends only after 30 minutes well below it
        with the air back in range. Measured breaches are Critical and are never gated by a forecast."""
        th = {"freeze": self.models["thresholds"]["freeze"], "heat": self.models["thresholds"]["heat"]}
        air = r["air"].to_numpy()
        risk = {"freeze": r["risk_freeze"].to_numpy(), "heat": r["risk_heat"].to_numpy()}
        sensor = r["sensor"].to_numpy()
        early = {"freeze": False, "heat": False}
        out = []
        for i in range(len(r)):
            a6, a3, a2 = air[max(0, i - 5): i + 1], air[max(0, i - 2): i + 1], air[max(0, i - 1): i + 1]
            for k in ("freeze", "heat"):
                rk = risk[k][max(0, i - 2): i + 1]
                if len(rk) >= 2 and (rk[-2:] >= th[k]).all():
                    early[k] = True
                in_range = (a3 >= 2.0).all() if k == "freeze" else (a3 <= 8.0).all()
                if early[k] and len(rk) == 3 and (rk < th[k] / 2).all() and in_range:
                    early[k] = False
            if len(a6) == 6 and (a6 <= -0.5).all():
                out.append(("Critical", "freeze"))
            elif len(a3) == 3 and (a3 > 8).all():
                out.append(("Critical", "heat"))
            elif sensor[i]:
                out.append(("Sensor check", "sensor"))
            elif early["freeze"]:
                out.append(("Early warning", "freeze"))
            elif early["heat"]:
                out.append(("Early warning", "heat"))
            elif risk["freeze"][i] >= th["freeze"] / 2 or (len(a2) == 2 and (a2 < 2.0).all()):
                out.append(("Advisory", "freeze"))
            elif risk["heat"][i] >= th["heat"] / 2 or (len(a2) == 2 and (a2 > 8.0).all()):
                out.append(("Advisory", "heat"))
            else:
                out.append(("Normal", ""))
        return out

    def _tier(self, r: pd.DataFrame, t: int) -> tuple[str, str]:
        u = int(r["unit"].iloc[0])
        return self._tiers[u][t]

    def _message(self, tier: str, kind: str, row: pd.Series) -> str:
        if tier == "Critical":
            return "Air at or below −0.5 °C for an hour (measured)" if kind == "freeze" else \
                f"Air above +8 °C for 30 min (measured), now {row['air']:.1f} °C"
        if tier == "Sensor check":
            return "Probe reading unchanged for 3 h: check the sensor"
        if tier in ("Early warning", "Advisory") and kind == "freeze":
            p50 = row["ttb_f_p50"]
            if p50 == p50:
                return f"Vaccine may freeze in about {p50:.0f} min"
            if tier == "Early warning":
                return f"Cooling too hard: {row['risk_freeze']:.0%} chance of freezing within 2 h"
            return f"Air {row['air']:.1f} °C, below the 2 °C safe limit" if row["air"] < 2 else "Cooling too hard; freeze risk rising"
        if tier in ("Early warning", "Advisory") and kind == "heat":
            p50 = row["ttb_h_p50"]
            return f"Vaccine may pass +8 °C in about {p50:.0f} min" if p50 == p50 else "Warming; heat risk rising"
        return "Stable, within 2–8 °C"

    # ---- public API ------------------------------------------------------------------------------------------------
    def summary(self, fid: str, t: int | None = None) -> dict:
        t = self.clock.now() if t is None else t
        r = self._rows(fid)
        row = r.loc[t]
        tier, kind = self._tier(r, t)
        stock = self.meta[fid].get("stock", [])
        tier, stock_note = adjust_tier(tier, kind, stock)
        cause_key = row["cause"] if tier != "Normal" else "none"
        if tier == "Sensor check":
            cause_key = "sensor_fault"
        title, steps = CARD.get(cause_key, CARD["none"])
        m = self.meta[fid]
        risk = row["risk_freeze"] if kind != "heat" else row["risk_heat"]
        pre = "f" if kind != "heat" else "h"
        return dict(
            id=fid, facility=m["facility"], fridge=m["fridge"], taluka=m["taluka"], cls=m["cls"],
            tick=int(t), clock=self._clock_label(t), tier=tier, kind=kind,
            message=self._message(tier, kind, row),
            air=round(float(row["air"]), 1), vial=round(float(row["vial"]), 1), vial_sd=round(float(row["vial_sd"]), 2),
            air_in_1h=round(float(row["air_fc6"]), 1), slope_per_10min=round(float(row["slope"]), 2),
            risk_2h=round(float(risk), 3),
            ttb=dict(p10=_num(row[f"ttb_{pre}_p10"]), p50=_num(row[f"ttb_{pre}_p50"]), p90=_num(row[f"ttb_{pre}_p90"])),
            cause=dict(key=cause_key, title=title, steps=steps, confidence=round(float(row["cause_conf"]), 2)),
            stock=stock, freeze_sensitive=freeze_sensitive_stock(stock), stock_note=stock_note,
        )

    def detail(self, fid: str, hours: int = 24) -> dict:
        t = self.clock.now()
        r = self._rows(fid)
        lo = max(0, t - hours * 6)
        hist = r.loc[lo: t]
        s = self.summary(fid, t)
        fc_ticks = [t + h for h in (3, 6, 12)]
        s["series"] = dict(
            ticks=[int(i) for i in hist.index], air=_lst(hist["air"]), vial=_lst(hist["vial"]), vial_sd=_lst(hist["vial_sd"]),
            risk_freeze=_lst(hist["risk_freeze"]), risk_heat=_lst(hist["risk_heat"]))
        s["forecast"] = dict(ticks=[t] + fc_ticks,
                             air=[round(float(r.loc[t, "air"]), 2)] + [round(float(r.loc[t, f"air_fc{h}"]), 2) for h in (3, 6, 12)],
                             vial=[round(float(r.loc[t, "vial"]), 2)] + [round(float(r.loc[t, f"vial_fc{h}"]), 2) for h in (3, 6, 12)])
        day = r.loc[max(0, t - 143): t]
        s["exposure_24h"] = dict(minutes_above_8=int((day["vial"] > 8).sum() * 10),
                                 minutes_below_0=int((day["vial"] <= -0.5).sum() * 10))
        return s

    def fleet(self) -> list[dict]:
        order = {"Critical": 0, "Early warning": 1, "Sensor check": 2, "Advisory": 3, "Normal": 4}
        return sorted((self.summary(f) for f in self.ids), key=lambda s: order[s["tier"]])

    def state(self) -> dict:
        t = self.clock.now()
        return dict(tick=t, clock=self._clock_label(t), playing=self.clock.playing,
                    seconds_per_tick=self.clock.seconds_per_tick, start=self.clock.start, end=END_TICK)


def _num(v) -> float | None:
    return None if v != v else float(v)


def _lst(s: pd.Series) -> list:
    return [round(float(v), 3) for v in s.to_numpy()]
