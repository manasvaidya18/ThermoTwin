"""Alerts service: turns scored readings into Guardian tiers, Cause Cards and vaccine-aware alert messages.

On start it pulls the registry and readings from telemetry-service, has inference-service score them, precomputes
the tier timeline per fridge and records every tier change in the alert_events table.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.common import config
from backend.common.db import connect, vaccine_catalogue
from backend.common.timefmt import clock_label

from .rules import CARD, TIER_ORDER, lst, maintenance_info, message, num, recovery_info, tier_timeline
from .vaccines import adjust_tier, freeze_sensitive_stock


class AlertService:
    def __init__(self, telemetry, inference, db_path: Path = config.DB_PATH) -> None:
        """telemetry / inference: the service objects (local mode) or their HTTP clients (http mode)."""
        self.con = connect(db_path)
        self.catalogue = vaccine_catalogue(self.con)
        reg = telemetry.registry()
        self.source = telemetry.clock_state()["source"]
        self.meta = {f["id"]: f for f in reg}
        self.ids = [f["id"] for f in reg]
        scored = inference.score([dict(id=f["id"], cls=f["cls"]) for f in reg], telemetry.readings())
        self.thresholds = scored["thresholds"]
        feat = pd.DataFrame(scored["rows"])
        for c in feat.columns:
            if c not in ("fridge_id", "cause", "sensor"):
                feat[c] = pd.to_numeric(feat[c], errors="coerce").astype(float)
        feat["sensor"] = feat["sensor"].astype(bool)
        feat["tick"] = feat["tick"].astype(int)
        self._rows = {fid: g.set_index("tick", drop=False).rename_axis(None).sort_index()
                      for fid, g in feat.groupby("fridge_id")}
        self._tiers = {fid: dict(zip(self._rows[fid].index, tier_timeline(self._rows[fid], self.thresholds)))
                       for fid in self.ids}
        self._record_events()

    # ---- persistence -------------------------------------------------------------------------------------------------
    def _record_events(self) -> None:
        rows = []
        for fid in self.ids:
            prev = None
            for t in self._rows[fid].index:
                s = self.summary(fid, int(t))
                if s["tier"] != prev:
                    rows.append((self.source, fid, int(t), s["tier"], s["kind"], s["message"]))
                    prev = s["tier"]
        with self.con:
            self.con.execute("DELETE FROM alert_events WHERE source = ?", (self.source,))
            self.con.executemany("INSERT INTO alert_events (source, fridge_id, tick, tier, kind, message) "
                                 "VALUES (?,?,?,?,?,?)", rows)

    # ---- queries -----------------------------------------------------------------------------------------------------
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
            recovery=recovery, maintenance=maintenance_info(row),
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
        return sorted((self.summary(f, t) for f in self.ids), key=lambda s: TIER_ORDER[s["tier"]])

    def history(self, t: int, fridge_id: str | None = None) -> list[dict]:
        q = "SELECT fridge_id, tick, tier, kind, message FROM alert_events WHERE source = ? AND tick <= ?"
        args: list = [self.source, t]
        if fridge_id:
            q += " AND fridge_id = ?"
            args.append(fridge_id)
        rows = [dict(r) for r in self.con.execute(q + " ORDER BY tick DESC, fridge_id", args)]
        for r in rows:
            r["clock"] = clock_label(r["tick"])
        return rows
