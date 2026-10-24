"""Escalation worker: raise unacknowledged alerts to the next level.

Critical and Early warning alerts that nobody acknowledged within TT_ESCALATE_AFTER_MIN minutes go from site staff
(level 0) to the officer (level 1), then to the senior officer (level 2). Notifications are simulated (printed); plug
an SMS or voice provider into notify() to send them for real.

  python workers/escalation_worker.py [--source live] [--interval 60]
"""
from __future__ import annotations

import argparse
from datetime import timedelta

from _django import run, setup

LEVELS = {1: "officer", 2: "senior officer"}


def notify(event, level: int) -> None:
    print(f"[simulated SMS to {LEVELS[level]}] {event.unit_id}: {event.tier} - {event.message}")


def make_job(source: str):
    def job() -> None:
        from django.conf import settings
        from django.utils import timezone

        from apps.alerts.models import AlertEvent

        cutoff = timezone.now() - timedelta(minutes=settings.ESCALATE_AFTER_MIN)
        due = (AlertEvent.objects.filter(source=source, tier__in=["Critical", "Early warning"], escalation_level__lt=2,
                                         acknowledgements__isnull=True)
               .exclude(escalated_at__gt=cutoff).filter(created_at__lte=cutoff))
        n = 0
        for ev in due:
            ev.escalation_level += 1
            ev.escalated_at = timezone.now()
            ev.save(update_fields=["escalation_level", "escalated_at"])
            notify(ev, ev.escalation_level)
            n += 1
        print(f"escalated {n} alert(s)")
    return job


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="live", help="'live' for device data, or the demo scenario name")
    ap.add_argument("--interval", type=float, default=None)
    a = ap.parse_args()
    setup()
    run(make_job(a.source), a.interval)


if __name__ == "__main__":
    main()
