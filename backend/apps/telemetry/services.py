"""Telemetry services: the demo scenario, the demo clock, reading storage and device ingestion."""
from __future__ import annotations

import json
from datetime import timedelta
from functools import lru_cache

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.facilities.models import StorageUnit
from apps.facilities.services import registry

from .clock import Clock
from .models import Device, Reading

LIVE = "live"


# ---- demo scenario -------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def scenario() -> dict:
    return json.loads(settings.SCENARIO_PATH.read_text(encoding="utf-8"))


def scenario_source() -> str:
    return scenario()["name"]


def ensure_scenario_readings() -> int:
    """Simulate the demo scenario (ColdChain Gym) into the readings table once. Returns rows written."""
    src = scenario_source()
    if Reading.objects.filter(source=src).exists():
        return 0
    from prediction_engine.digital_twin.thermal_model import FleetConfig, simulate_fleet   # only needed here

    sc = scenario()
    reg = registry()
    spec = [dict(cls=f["cls"], **sc["fridges"].get(f["id"], {})) for f in reg]
    log, _, _ = simulate_fleet(FleetConfig(days=sc["days"], seed=sc["seed"], units_spec=spec))
    ids = [f["id"] for f in reg]
    rows = [Reading(unit_id=ids[int(u)], source=src, tick=int(t), minute=int(m), temp_c=None if a != a else float(a))
            for u, t, m, a in log[["unit", "tick", "minute", "air_meas"]].itertuples(index=False)]
    with transaction.atomic():
        Reading.objects.bulk_create(rows, batch_size=2000)
    return len(rows)


def readings(source: str, unit: str | None = None) -> list[dict]:
    qs = Reading.objects.filter(source=source)
    if unit:
        qs = qs.filter(unit_id=unit)
    return [dict(fridge_id=u, tick=t, minute=m, temp_c=v)
            for u, t, m, v in qs.order_by("unit_id", "tick").values_list("unit_id", "tick", "minute", "temp_c")]


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
    first = Reading.objects.filter(source=LIVE, unit=unit).order_by("tick").values_list("recorded_at", flat=True).first()
    t0 = first or clean[0]["timestamp"]
    stored = 0
    for r in clean:
        tick = int((r["timestamp"] - t0) / timedelta(minutes=10))
        if tick < 0:
            errors.append(f"{r['timestamp'].isoformat()}: before this unit's first live reading")
            continue
        Reading.objects.update_or_create(source=LIVE, unit=unit, tick=tick,
                                         defaults=dict(minute=(tick + 1) * 10, temp_c=r["temp_c"],
                                                       recorded_at=t0 + timedelta(minutes=10 * tick)))
        stored += 1
    Device.objects.filter(unit=unit).update(last_seen=timezone.now())
    return dict(stored=stored, errors=errors)
