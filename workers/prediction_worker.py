"""Prediction worker: score every unit that has live readings and record its alert events.

  python workers/prediction_worker.py                 once
  python workers/prediction_worker.py --interval 600  every 10 minutes (one logger interval)

The web dashboards score the demo scenario on their own; this worker keeps live units (ESP32 / eVIN) up to date.
"""
from __future__ import annotations

import argparse

from _django import run, setup


def job() -> None:
    from apps.alerts import services as alerts
    from apps.telemetry.models import Reading
    from apps.telemetry.services import LIVE

    units = list(Reading.objects.filter(source=LIVE).values_list("unit_id", flat=True).distinct())
    if not units:
        print("no live readings yet")
    for u in units:
        s = alerts.live_summary(u)
        if s:
            print(f"{u}: {s['tier']} | {s['message']} | vaccine {s['vial']} °C | health {s['maintenance']['health_index']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=None, help="seconds between runs (default: run once)")
    a = ap.parse_args()
    setup()
    run(job, a.interval)


if __name__ == "__main__":
    main()
