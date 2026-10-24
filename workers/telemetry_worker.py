"""Telemetry worker: get readings into the database.

  python workers/telemetry_worker.py                     build the demo scenario's readings (once)
  python workers/telemetry_worker.py --csv export.csv    import logger readings (columns: unit, timestamp, temp_c),
                                                          e.g. an eVIN export, as live readings
"""
from __future__ import annotations

import argparse
import csv

from _django import setup


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", help="CSV with columns unit, timestamp (ISO 8601), temp_c")
    a = ap.parse_args()
    setup()
    from apps.facilities.models import StorageUnit
    from apps.telemetry import services

    if not a.csv:
        n = services.ensure_scenario_readings()
        print(f"demo scenario '{services.scenario_source()}': {n} readings written" if n else "demo scenario already loaded")
        return
    by_unit: dict[str, list[dict]] = {}
    with open(a.csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            temp = r.get("temp_c", "").strip()
            by_unit.setdefault(r["unit"].strip(), []).append(dict(timestamp=r["timestamp"].strip(),
                                                                  temp_c=float(temp) if temp else None))
    for slug, rows in by_unit.items():
        unit = StorageUnit.objects.filter(slug=slug).first()
        if unit is None:
            print(f"{slug}: unknown unit, skipped")
            continue
        res = services.ingest(unit, rows)
        print(f"{slug}: stored {res['stored']}, {len(res['errors'])} rejected")


if __name__ == "__main__":
    main()
