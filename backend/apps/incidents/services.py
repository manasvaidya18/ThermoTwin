"""Incident services: open tickets without duplicates, assign the saved technician, resolve."""
from __future__ import annotations

from django.utils import timezone

from apps.facilities.models import StorageUnit, Technician

from .models import Incident, IncidentAction


def open_incident(unit_slug: str, kind: str, title: str, notes: str = "", alert_event=None, user=None) -> tuple[Incident, bool]:
    """Open an incident unless one of the same kind is already open for this unit. Returns (incident, created)."""
    existing = Incident.objects.filter(unit_id=unit_slug, kind=kind).exclude(status=Incident.RESOLVED).first()
    if existing:
        return existing, False
    unit = StorageUnit.objects.get(slug=unit_slug)
    tech = Technician.objects.filter(facilities=unit.facility_id).first()
    inc = Incident.objects.create(unit=unit, kind=kind, title=title[:200], notes=notes, alert_event=alert_event,
                                  opened_by=user if user and user.is_authenticated else None, technician=tech,
                                  status=Incident.ASSIGNED if tech else Incident.OPEN)
    return inc, True


def add_action(inc: Incident, text: str, user=None) -> IncidentAction:
    return IncidentAction.objects.create(incident=inc, text=text[:300], user=user if user and user.is_authenticated else None)


def resolve(inc: Incident, text: str = "", user=None) -> Incident:
    if text:
        add_action(inc, text, user)
    inc.status, inc.resolved_at = Incident.RESOLVED, timezone.now()
    inc.save(update_fields=["status", "resolved_at", "updated_at"])
    return inc
