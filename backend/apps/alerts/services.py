"""Alert services: turn scored readings into Guardian tiers, Cause Cards and vaccine-aware messages.

The engine scores a whole source (the demo scenario, or one unit's live readings) through the prediction engine,
precomputes the tier timeline per unit and records every tier change as an AlertEvent.
"""
from __future__ import annotations

import threading

import pandas as pd
from django.db import transaction

from apps.facilities.services import registry, technicians_for, vaccine_catalogue
from apps.telemetry import services as telemetry

from . import prediction_client
from .models import AlertEvent
from .rules import CARD, TIER_ORDER, clock_label, lst, maintenance_info, message, num, recovery_info, tier_timeline
from .vaccines import adjust_tier, freeze_sensitive_stock


class AlertEngine:
    def __init__(self, source: str, units: list[dict], readings: list[dict]) -> None:
        self.source = source
        self.catalogue = vaccine_catalogue()
        self.meta = {f["id"]: f for f in units}
        self.ids = [f["id"] for f in units]
        self.techs = {f: technicians_for(f) for f in self.ids}
        scored = prediction_client.score([dict(id=f["id"], cls=f["cls"]) for f in units], readings)
        self.thresholds = scored["thresholds"]
        feat = pd.DataFrame(scored["rows"])
        for c in feat.columns:
            if c not in ("fridge_id", "cause", "sensor", "why_freeze", "why_heat"):
                feat[c] = pd.to_numeric(feat[c], errors="coerce").astype(float)
        feat["sensor"] = feat["sensor"].astype(bool)
        feat["tick"] = feat["tick"].astype(int)
        self._rows = {fid: g.set_index("tick", drop=False).rename_axis(None).sort_index()
                      for fid, g in feat.groupby("fridge_id")}
        self._tiers = {fid: dict(zip(self._rows[fid].index, tier_timeline(self._rows[fid], self.thresholds)))
                       for fid in self.ids if fid in self._rows}
        self._store_predictions(feat)

    def _store_predictions(self, feat: pd.DataFrame) -> None:
        """Write the model's outputs (Virtual Vial, risk, cooling health) to InfluxDB as a time series."""
        st = telemetry.store()
        if st.name != "influxdb":
            return
        try:
            rows = []
            for fid, g in feat.groupby("fridge_id"):
                t0 = telemetry.tick_time(self.source, fid, 0)
                if t0 is None:
                    continue
                for r in g.itertuples(index=False):
                    rows.append(dict(unit=fid, tick=int(r.tick), time=t0 + pd.Timedelta(minutes=10 * int(r.tick)),
                                     vial=r.vial, risk_freeze=r.risk_freeze, risk_heat=r.risk_heat,
                                     health=None if r.health != r.health else r.health))
            st.write_predictions(self.source, rows)
        except Exception as e:      # noqa: BLE001 - storing history must never break alerting
            import logging
            logging.getLogger(__name__).warning("could not write predictions to InfluxDB: %s", e)

    # ---- persistence -------------------------------------------------------------------------------------------------
    def record_events(self) -> int:
        """Store every tier change (kept across restarts so acknowledgements stay attached)."""
        have = set(AlertEvent.objects.filter(source=self.source).values_list("unit_id", "tick", "tier"))
        new = []
        for fid in self._tiers:
            prev = None
            for t in self._rows[fid].index:
                s = self.summary(fid, int(t))
                if s["tier"] != prev:
                    if (fid, int(t), s["tier"]) not in have:
                        new.append(AlertEvent(source=self.source, unit_id=fid, tick=int(t), tier=s["tier"],
                                              kind=s["kind"], message=s["message"][:300]))
                    prev = s["tier"]
        with transaction.atomic():
            AlertEvent.objects.bulk_create(new, ignore_conflicts=True)
        return len(new)

    # ---- queries -----------------------------------------------------------------------------------------------------
    def has(self, fid: str) -> bool:
        return fid in self._tiers

    def last_tick(self, fid: str) -> int:
        return int(self._rows[fid].index.max())

    def summary(self, fid: str, t: int) -> dict:
        row = self._rows[fid].loc[t]
        tier, kind = self._tiers[fid][t]
        m = self.meta[fid]
        stock = m.get("stock", [])
        tier, stock_note = adjust_tier(tier, kind, stock, self.catalogue)
        cause_key = row["cause"] if tier != "Normal" else "none"
        if tier == "Sensor check":
            cause_key = "sensor_fault"
        title, steps = CARD.get(cause_key, CARD["none"])
        risk = row["risk_freeze"] if kind != "heat" else row["risk_heat"]
        pre = "f" if kind != "heat" else "h"
        recovery = recovery_info(row)
        msg = message(tier, kind, row)
        if tier == "Normal" and recovery["state"] == "recovered":
            msg = recovery["message"]
        why = ""
        if tier in ("Early warning", "Advisory") and kind in ("freeze", "heat"):
            why = row.get("why_freeze" if kind == "freeze" else "why_heat") or ""
        return dict(
            id=fid, facility=m["facility"], fridge=m["fridge"], taluka=m["taluka"], cls=m["cls"],
            tick=int(t), clock=clock_label(t), tier=tier, kind=kind,
            message=msg,
            air=round(float(row["air"]), 1), vial=round(float(row["vial"]), 1), vial_sd=round(float(row["vial_sd"]), 2),
            air_in_1h=round(float(row["air_fc6"]), 1), slope_per_10min=round(float(row["slope"]), 2),
            risk_2h=round(float(risk), 3),
            ttb=dict(p10=num(row[f"ttb_{pre}_p10"]), p50=num(row[f"ttb_{pre}_p50"]), p90=num(row[f"ttb_{pre}_p90"])),
            cause=dict(key=cause_key, title=title, steps=steps, confidence=round(float(row["cause_conf"]), 2)),
            stock=stock, freeze_sensitive=freeze_sensitive_stock(stock, self.catalogue), stock_note=stock_note,
            recovery=recovery, maintenance=maintenance_info(row), why=why, technicians=self.techs.get(fid, []),
        )

    def detail(self, fid: str, t: int, hours: int = 24) -> dict:
        r = self._rows[fid]
        hist = r.loc[max(0, t - hours * 6): t]
        s = self.summary(fid, t)
        s["series"] = dict(
            ticks=[int(i) for i in hist.index], air=lst(hist["air"]), vial=lst(hist["vial"]), vial_sd=lst(hist["vial_sd"]),
            risk_freeze=lst(hist["risk_freeze"]), risk_heat=lst(hist["risk_heat"]))
        s["forecast"] = dict(ticks=[t] + [t + h for h in (3, 6, 12)],
                             air=[round(float(r.loc[t, "air"]), 2)] + [round(float(r.loc[t, f"air_fc{h}"]), 2) for h in (3, 6, 12)],
                             vial=[round(float(r.loc[t, "vial"]), 2)] + [round(float(r.loc[t, f"vial_fc{h}"]), 2) for h in (3, 6, 12)])
        day = r.loc[max(0, t - 143): t]
        s["exposure_24h"] = dict(minutes_above_8=int((day["vial"] > 8).sum() * 10),
                                 minutes_below_0=int((day["vial"] <= -0.5).sum() * 10))
        return s

    def fleet(self, t: int) -> list[dict]:
        return sorted((self.summary(f, t) for f in self.ids if f in self._tiers), key=lambda s: TIER_ORDER[s["tier"]])


def history(source: str, t: int, unit: str | None = None) -> list[dict]:
    qs = AlertEvent.objects.filter(source=source, tick__lte=t).prefetch_related("acknowledgements")
    if unit:
        qs = qs.filter(unit_id=unit)
    return [dict(id=e.id, fridge_id=e.unit_id, tick=e.tick, tier=e.tier, kind=e.kind, message=e.message,
                 clock=clock_label(e.tick), acknowledged=bool(e.acknowledgements.all()),
                 escalation_level=e.escalation_level)
            for e in qs.order_by("-tick", "unit_id")]


# ---- engine for the demo scenario (built once, on first use) --------------------------------------------------------
_engine: AlertEngine | None = None
_lock = threading.Lock()


def engine() -> AlertEngine:
    global _engine
    with _lock:
        if _engine is None:
            telemetry.ensure_scenario_readings()
            src = telemetry.scenario_source()
            _engine = AlertEngine(src, registry(), telemetry.readings(src))
            _engine.record_events()
        return _engine


def reset_engine() -> None:
    global _engine
    with _lock:
        _engine = None


def live_summary(unit: str) -> dict | None:
    """Score one unit's live device readings (ESP32 / eVIN) and return its latest status."""
    rows = telemetry.readings(telemetry.LIVE, unit)
    if len(rows) < 2:
        return None
    meta = [f for f in registry() if f["id"] == unit]
    if not meta:
        return None
    eng = AlertEngine(telemetry.LIVE, meta, rows)
    eng.record_events()
    return eng.summary(unit, eng.last_tick(unit))
