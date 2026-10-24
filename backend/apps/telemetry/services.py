"""Telemetry services: the demo scenario, the demo clock, reading storage (InfluxDB or the database) and ingestion."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from functools import lru_cache

from django.conf import settings
from django.utils import timezone

from apps.facilities.models import StorageUnit
from apps.facilities.services import registry

from .clock import Clock
from .models import Device
from .timeseries import store  # noqa: F401  (re-exported for other apps)

LIVE = "live"


# ---- demo scenario -------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def scenario() -> dict:
    return json.loads(settings.SCENARIO_PATH.read_text(encoding="utf-8"))


def scenario_source() -> str:
    return scenario()["name"]


def scenario_time(tick: int) -> datetime:
    """Timestamp of a scenario reading (end of its 10-minute interval)."""
    return datetime.fromisoformat(scenario()["start_time"]) + timedelta(minutes=10 * (tick + 1))


def ensure_scenario_readings() -> int:
    """Simulate the demo scenario (ColdChain Gym) into the reading store once. Returns readings written."""
    src = scenario_source()
    if store().has_source(src):
        return 0
    from prediction_engine.digital_twin.thermal_model import FleetConfig, simulate_fleet   # only needed here

    sc = scenario()
    reg = registry()
    spec = [dict(cls=f["cls"], **sc["fridges"].get(f["id"], {})) for f in reg]
    log, _, _ = simulate_fleet(FleetConfig(days=sc["days"], seed=sc["seed"], units_spec=spec))
    ids = [f["id"] for f in reg]
    rows = [(ids[int(u)], int(t), scenario_time(int(t)), None if a != a else float(a))
            for u, t, a in log[["unit", "tick", "air_meas"]].itertuples(index=False)]
    return store().write_readings(src, rows)


def readings(source: str, unit: str | None = None) -> list[dict]:
    """Readings as a complete 10-minute grid per unit (gaps filled with temp_c None), as the twin expects."""
    rows = store().read(source, unit)
    by_unit: dict[str, dict[int, float | None]] = {}
    for u, t, _, v in rows:
        by_unit.setdefault(u, {})[t] = v
    if not by_unit:
        return []
    last = max(max(d) for d in by_unit.values())
    return [dict(fridge_id=u, tick=t, minute=(t + 1) * 10, temp_c=d.get(t))
            for u, d in sorted(by_unit.items()) for t in range(last + 1)]


def live_units() -> list[str]:
    """Units that have live device readings."""
    return sorted({u for u, _, _, _ in store().read(LIVE)})


def tick_time(source: str, unit: str, tick: int) -> datetime | None:
    """Real timestamp of a reading (for writing predictions next to it)."""
    if source == scenario_source():
        return scenario_time(tick)
    first = _first_live_time(unit)
    return first + timedelta(minutes=10 * tick) if first else None


def _first_live_time(unit: str) -> datetime | None:
    rows = [r for r in store().read(LIVE, unit) if r[2] is not None]
    return min((ts - timedelta(minutes=10 * t) for _, t, ts, _ in rows), default=None)


# ---- demo clock ------------------------------------------------------------------------------------------------------
_clock: Clock | None = None


def clock() -> Clock:
    global _clock
    if _clock is None:
        sc = scenario()
        _clock = Clock(start=sc["start_tick"], end=sc["end_tick"])
    return _clock


def clock_state() -> dict:
    from apps.alerts.rules import clock_label
    c = clock()
    t = c.now()
    return dict(tick=t, clock=clock_label(t), playing=c.playing, seconds_per_tick=c.seconds_per_tick,
                start=c.start, end=c.end)


def clock_action(action: str, ticks: int = 1, seconds_per_tick: float | None = None) -> dict:
    c = clock()
    if seconds_per_tick:
        c.seconds_per_tick = max(0.2, float(seconds_per_tick))
    if action == "play":
        c.play()
    elif action == "pause":
        c.pause()
    elif action == "reset":
        c.reset()
    elif action == "step":
        c.step(int(ticks))
    else:
        raise ValueError("action must be play, pause, reset or step")
    return clock_state()


# ---- device ingestion ------------------------------------------------------------------------------------------------
def ingest(unit: StorageUnit, rows: list[dict]) -> dict:
    """Store live readings ({timestamp, temp_c}) for a unit as 10-minute ticks from its first live reading.

    Rows are validated by the prediction engine's data validator (timestamps, plausible temperature range).
    """
    from prediction_engine.ingestion.data_validator import validate_readings

    clean, errors = validate_readings([dict(r, fridge_id=unit.slug) for r in rows])
    if not clean:
        return dict(stored=0, errors=errors)
    t0 = _first_live_time(unit.slug) or clean[0]["timestamp"]
    rows = []
    for r in clean:
        tick = int((r["timestamp"] - t0) / timedelta(minutes=10))
        if tick < 0:
            errors.append(f"{r['timestamp'].isoformat()}: before this unit's first live reading")
            continue
        rows.append((unit.slug, tick, t0 + timedelta(minutes=10 * tick), r["temp_c"]))
    stored = store().write_readings(LIVE, rows) if rows else 0
    Device.objects.filter(unit=unit).update(last_seen=timezone.now())
    return dict(stored=stored, errors=errors, store=store().name)
