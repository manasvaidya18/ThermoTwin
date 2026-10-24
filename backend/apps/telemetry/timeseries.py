"""Time-series storage for sensor readings and model outputs.

InfluxDB (when INFLUX_URL and INFLUX_TOKEN are set and the server answers):
  measurement "temperature": tags unit, source; fields temp_c (float, absent for a missing reading), tick (int)
  measurement "prediction":  tags unit, source; fields vial, risk_freeze, risk_heat, health, tick
Otherwise readings go to the telemetry_reading table in the main database (PostgreSQL), so nothing breaks.

Everything above this module works in ticks (10-minute reading index from the start of a source); the stores keep the
real timestamp too, so InfluxDB queries and dashboards see proper time series.
"""
from __future__ import annotations

import logging
from datetime import datetime

from django.conf import settings

log = logging.getLogger(__name__)


class SqlStore:
    """Fallback: readings in the relational database (telemetry_reading)."""
    name = "postgres_table"

    def has_source(self, source: str) -> bool:
        from .models import Reading
        return Reading.objects.filter(source=source).exists()

    def write_readings(self, source: str, rows: list[tuple[str, int, datetime, float | None]]) -> int:
        from django.db import transaction

        from .models import Reading
        objs = [Reading(unit_id=u, source=source, tick=t, minute=(t + 1) * 10, temp_c=v, recorded_at=ts)
                for u, t, ts, v in rows]
        with transaction.atomic():
            Reading.objects.bulk_create(objs, batch_size=2000, update_conflicts=True,
                                        unique_fields=["source", "unit", "tick"],
                                        update_fields=["temp_c", "recorded_at", "minute"])
        return len(objs)

    def read(self, source: str, unit: str | None = None) -> list[tuple[str, int, datetime | None, float | None]]:
        from .models import Reading
        qs = Reading.objects.filter(source=source)
        if unit:
            qs = qs.filter(unit_id=unit)
        return list(qs.order_by("unit_id", "tick").values_list("unit_id", "tick", "recorded_at", "temp_c"))

    def write_predictions(self, source: str, rows: list[dict]) -> int:
        return 0                      # model outputs are not stored in the relational fallback


class InfluxStore:
    name = "influxdb"

    def __init__(self) -> None:
        from influxdb_client import InfluxDBClient
        from influxdb_client.client.write_api import SYNCHRONOUS
        self.bucket, self.org = settings.INFLUX["bucket"], settings.INFLUX["org"]
        self.client = InfluxDBClient(url=settings.INFLUX["url"], token=settings.INFLUX["token"], org=self.org, timeout=60_000)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except Exception:     # noqa: BLE001
            return False

    def _flux(self, measurement: str, source: str, unit: str | None, tail: str = "") -> str:
        unit_f = f' and r.unit == "{_safe(unit)}"' if unit else ""
        return (f'from(bucket: "{self.bucket}") |> range(start: 0) '
                f'|> filter(fn: (r) => r._measurement == "{measurement}" and r.source == "{_safe(source)}"{unit_f}) {tail}')

    def has_source(self, source: str) -> bool:
        tables = self.query_api.query(self._flux("temperature", source, None, '|> filter(fn: (r) => r._field == "tick") |> limit(n: 1)'))
        return any(t.records for t in tables)

    def write_readings(self, source: str, rows: list[tuple[str, int, datetime, float | None]]) -> int:
        from influxdb_client import Point
        pts = []
        for u, t, ts, v in rows:
            p = Point("temperature").tag("unit", u).tag("source", source).field("tick", int(t)).time(ts)
            if v is not None:
                p = p.field("temp_c", float(v))
            pts.append(p)
        for i in range(0, len(pts), 5000):
            self.write_api.write(bucket=self.bucket, record=pts[i:i + 5000])
        return len(pts)

    def read(self, source: str, unit: str | None = None) -> list[tuple[str, int, datetime | None, float | None]]:
        q = self._flux("temperature", source, unit,
                       '|> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value") '
                       '|> keep(columns: ["_time", "unit", "tick", "temp_c"])')
        out = []
        for table in self.query_api.query(q):
            for r in table.records:
                v = r.values
                out.append((v["unit"], int(v["tick"]), v["_time"], v.get("temp_c")))
        return sorted(out, key=lambda x: (x[0], x[1]))

    def write_predictions(self, source: str, rows: list[dict]) -> int:
        from influxdb_client import Point
        pts = []
        for r in rows:
            p = Point("prediction").tag("unit", r["unit"]).tag("source", source).field("tick", int(r["tick"])).time(r["time"])
            for k in ("vial", "risk_freeze", "risk_heat", "health"):
                if r.get(k) is not None:
                    p = p.field(k, float(r[k]))
            pts.append(p)
        for i in range(0, len(pts), 5000):
            self.write_api.write(bucket=self.bucket, record=pts[i:i + 5000])
        return len(pts)


def _safe(s: str) -> str:
    return str(s).replace("\\", "").replace('"', "")


_store = None


def store():
    """InfluxDB if configured and reachable, else the relational table. Decided once per process."""
    global _store
    if _store is None:
        cfg = settings.INFLUX
        if cfg["url"] and cfg["token"]:
            try:
                s = InfluxStore()
                if s.ping():
                    _store = s
                    log.info("readings: InfluxDB at %s, bucket %s", cfg["url"], cfg["bucket"])
                else:
                    log.warning("InfluxDB at %s not reachable; readings go to the database table", cfg["url"])
            except Exception as e:      # noqa: BLE001
                log.warning("InfluxDB unavailable (%s); readings go to the database table", e)
        if _store is None:
            _store = SqlStore()
    return _store


def reset_store() -> None:
    global _store
    _store = None
