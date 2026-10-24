"""Maintenance worker (slow loop): open a maintenance ticket for every unit whose cooling is weakening.

Uses the compressor-life model's output (maintenance.due) and assigns the technician saved for the facility.
Run once a day.

  python workers/maintenance_worker.py            demo scenario at its last reading, plus live units
"""
from __future__ import annotations

from _django import setup


def main() -> None:
    setup()
    from apps.alerts import services as alerts
    from apps.incidents.models import Incident
    from apps.incidents.services import open_incident
    from apps.telemetry.models import Reading
    from apps.telemetry.services import LIVE, clock

    eng = alerts.engine()
    summaries = eng.fleet(clock().end)
    for u in Reading.objects.filter(source=LIVE).values_list("unit_id", flat=True).distinct():
        s = alerts.live_summary(u)
        if s:
            summaries.append(s)
    opened = 0
    for s in summaries:
        m = s["maintenance"]
        if not m["due"]:
            continue
        days = f" (failure possible in about {m['days_to_service']:.0f} days)" if m["days_to_service"] else ""
        inc, created = open_incident(s["id"], Incident.MAINTENANCE, f"Cooling weakening{days}",
                                     notes=f"Cooling health {m['health_index']}. {m['message']}")
        opened += created
        print(f"{s['id']}: {'opened' if created else 'already open'} ticket #{inc.id}"
              + (f", technician {inc.technician.name}" if inc.technician else ""))
    print(f"{opened} new maintenance ticket(s)")


if __name__ == "__main__":
    main()
