"""Facility services: the unit registry the prediction and alert steps work from, and the vaccine catalogue."""
from __future__ import annotations

from .models import StorageUnit, Technician, Vaccine


def registry() -> list[dict]:
    """Active storage units in a stable order, with facility details and stock (the demo scenario's fridge order)."""
    units = StorageUnit.objects.filter(active=True).select_related("facility").prefetch_related("stock")
    return [dict(id=u.slug, facility=u.facility.name, fridge=u.label, taluka=u.facility.taluka, cls=u.cls,
                 stock=[s.vaccine_id for s in u.stock.all()]) for u in units]


def vaccine_catalogue() -> dict[str, bool]:
    return dict(Vaccine.objects.values_list("name", "freeze_sensitive"))


def technicians_for(unit_slug: str) -> list[dict]:
    u = StorageUnit.objects.filter(slug=unit_slug).first()
    if not u:
        return []
    return [dict(name=t.name, phone=t.phone) for t in Technician.objects.filter(facilities=u.facility_id)]
