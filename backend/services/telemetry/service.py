"""Telemetry service: fridge registry, logger readings and the demo clock.

Readings live in the database. On first start the demo scenario is simulated (ColdChain Gym) and stored, so every
other service reads the same numbers a real logger feed would provide.
"""
from __future__ import annotations

import json
from pathlib import Path

from backend.common import config
from backend.common.db import connect
from backend.common.timefmt import clock_label

from .clock import Clock


class TelemetryService:
    def __init__(self, db_path: Path = config.DB_PATH, scenario_path: Path = config.SCENARIO_PATH) -> None:
        self.con = connect(db_path)
        self.scenario = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
        self.source = self.scenario["name"]
        self.clock = Clock(start=self.scenario["start_tick"], end=self.scenario["end_tick"])
        self._ensure_readings()

    # ---- registry ----------------------------------------------------------------------------------------------------
    def registry(self) -> list[dict]:
        rows = self.con.execute(
            "SELECT f.id, f.label, f.cls, fa.name AS facility, fa.taluka FROM fridges f "
            "JOIN facilities fa ON fa.id = f.facility_id ORDER BY f.sort_order, f.id").fetchall()
        out = []
        for r in rows:
            stock = [s["vaccine"] for s in self.con.execute(
                "SELECT vaccine FROM fridge_stock WHERE fridge_id = ? ORDER BY position", (r["id"],))]
            out.append(dict(id=r["id"], facility=r["facility"], fridge=r["label"], taluka=r["taluka"], cls=r["cls"],
                            stock=stock))
        return out

    # ---- readings ----------------------------------------------------------------------------------------------------
    def _ensure_readings(self) -> None:
        n = self.con.execute("SELECT COUNT(*) FROM readings WHERE source = ?", (self.source,)).fetchone()[0]
        if n:
            return
        from thermotwin.simulator import FleetConfig, simulate_fleet   # ML package, only needed to build the scenario

        reg = self.registry()
        spec = [dict(cls=f["cls"], **self.scenario["fridges"].get(f["id"], {})) for f in reg]
        log, _, _ = simulate_fleet(FleetConfig(days=self.scenario["days"], seed=self.scenario["seed"], units_spec=spec))
        ids = [f["id"] for f in reg]
        rows = [(self.source, ids[int(u)], int(t), int(m), None if a != a else float(a))
                for u, t, m, a in log[["unit", "tick", "minute", "air_meas"]].itertuples(index=False)]
        with self.con:
            self.con.executemany("INSERT INTO readings (source, fridge_id, tick, minute, temp_c) VALUES (?,?,?,?,?)", rows)

    def readings(self) -> list[dict]:
        cur = self.con.execute("SELECT fridge_id, tick, minute, temp_c FROM readings WHERE source = ? "
                               "ORDER BY fridge_id, tick", (self.source,))
        return [dict(r) for r in cur]

    # ---- clock -------------------------------------------------------------------------------------------------------
    def clock_state(self) -> dict:
        t = self.clock.now()
        return dict(tick=t, clock=clock_label(t), playing=self.clock.playing,
                    seconds_per_tick=self.clock.seconds_per_tick, start=self.clock.start, end=self.clock.end,
                    source=self.source)

    def clock_action(self, action: str, ticks: int = 1, seconds_per_tick: float | None = None) -> dict:
        c = self.clock
        if seconds_per_tick:
            c.seconds_per_tick = max(0.2, seconds_per_tick)
        if action == "play":
            c.play()
        elif action == "pause":
            c.pause()
        elif action == "reset":
            c.reset()
        elif action == "step":
            c.step(ticks)
        else:
            raise ValueError("action must be play, pause, reset or step")
        return self.clock_state()
