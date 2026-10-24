"""Reports: alert history, network summary and exports, computed from alert events, incidents and the live engine."""
from __future__ import annotations

import csv
import io
from collections import Counter

from apps.alerts import services as alerts
from apps.alerts.rules import clock_label
from apps.incidents.models import Incident
from apps.telemetry import services as telemetry


def summary() -> dict:
    """Network snapshot at the current demo time: units per tier, maintenance due, open incidents, exposure."""
    t = telemetry.clock_state()["tick"]
    eng = alerts.engine()
    fleet = eng.fleet(t)
    exposure = []
    for f in fleet:
        d = eng.detail(f["id"], t, hours=24)["exposure_24h"]
        exposure.append(dict(unit=f["id"], facility=f["facility"], **d))
    return dict(
        clock=clock_label(t),
        units=len(fleet),
        by_tier=dict(Counter(f["tier"] for f in fleet)),
        maintenance_due=[dict(unit=f["id"], facility=f["facility"], health=f["maintenance"]["health_index"],
                              message=f["maintenance"]["message"]) for f in fleet if f["maintenance"]["due"]],
        open_incidents=Incident.objects.exclude(status=Incident.RESOLVED).count(),
        exposure_24h=exposure,
    )


def alert_history_csv(unit: str | None = None) -> str:
    t = telemetry.clock_state()["tick"]
    rows = alerts.history(alerts.engine().source, t, unit)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["clock", "unit", "tier", "kind", "message", "acknowledged", "escalation_level"])
    for r in rows:
        w.writerow([r["clock"], r["fridge_id"], r["tier"], r["kind"], r["message"], r["acknowledged"], r["escalation_level"]])
    return buf.getvalue()


def incidents_csv() -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "unit", "kind", "status", "title", "technician", "created_at", "resolved_at"])
    for i in Incident.objects.select_related("technician"):
        w.writerow([i.id, i.unit_id, i.kind, i.status, i.title, i.technician.name if i.technician else "",
                    i.created_at.isoformat(), i.resolved_at.isoformat() if i.resolved_at else ""])
    return buf.getvalue()
