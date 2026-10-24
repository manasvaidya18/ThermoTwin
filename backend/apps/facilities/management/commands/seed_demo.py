"""Load the Pune demo network: organizations, facilities, units, vaccines, stock, technicians and demo users.

Usage:  python backend/manage.py seed_demo            (safe to run again: updates in place)
Demo users get the password from TT_DEMO_PASSWORD (see .env.example).
"""
from __future__ import annotations

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Profile
from apps.facilities.models import Facility, StockItem, StorageUnit, Technician, Vaccine
from apps.organizations.models import Organization

# Freeze sensitivity of UIP vaccines (WHO guidance; verify against current WHO documents and inserts).
VACCINES = [
    ("Pentavalent", True, "aluminium adjuvant"), ("Hepatitis B", True, "aluminium adjuvant"),
    ("DTP", True, "aluminium adjuvant"), ("Td", True, "aluminium adjuvant"), ("PCV", True, "aluminium adjuvant"),
    ("IPV", True, "liquid, freeze-sensitive"), ("Rotavirus", True, "liquid, freeze-sensitive"),
    ("HPV", True, "aluminium adjuvant"), ("OPV", False, "stored frozen at higher levels"),
    ("MR", False, "freeze-dried"), ("BCG", False, "freeze-dried"),
]
ORGS = [
    ("pune-dho", "Pune District Health Office", "government", "Pune", "Pune"),
    ("demo-coldchain", "Demo Cold Chain Logistics Pvt Ltd", "private", "Pune", "Pune"),
]
# slug, org, name, taluka, approximate latitude / longitude (for routing; approximate town centres)
FACILITIES = [
    ("phc-wagholi", "pune-dho", "PHC Wagholi", "Haveli", 18.580, 73.983),
    ("junnar-phc2", "pune-dho", "Junnar PHC-2", "Junnar", 19.208, 73.875),
    ("baramati-sdh", "pune-dho", "Baramati SDH", "Baramati", 18.151, 74.577),
    ("khed-phc", "pune-dho", "Khed PHC", "Khed", 18.853, 73.884),
    ("shirur-rh", "pune-dho", "Shirur RH", "Shirur", 18.827, 74.373),
    ("phc-lonikand", "pune-dho", "PHC Lonikand", "Haveli", 18.616, 74.020),
]
# The order fixes the simulation order of the demo scenario (do not reorder).
UNITS = [
    ("wagholi-ilr1", "phc-wagholi", "ILR-1", "ILR", ["Pentavalent", "Hepatitis B", "OPV", "MR"]),
    ("junnar-ilr01", "junnar-phc2", "ILR-01", "DOMESTIC", ["Pentavalent", "BCG"]),
    ("baramati-df01", "baramati-sdh", "FR-01", "DOMESTIC", ["PCV", "IPV"]),
    ("khed-ilr03", "khed-phc", "ILR-03", "ILR", ["Td", "MR"]),
    ("shirur-ilr01", "shirur-rh", "ILR-01", "ILR", ["OPV", "MR", "BCG"]),
    ("lonikand-ilr2", "phc-lonikand", "ILR-2", "ILR", ["Pentavalent", "Rotavirus"]),
]
# Placeholder phone numbers for the demo
TECHNICIANS = [
    ("Ravi K. (North)", "+91-00000-00001", ["junnar-phc2", "khed-phc", "shirur-rh"]),
    ("Meena P. (Central)", "+91-00000-00002", ["phc-wagholi", "phc-lonikand"]),
    ("Arif S. (South)", "+91-00000-00003", ["baramati-sdh"]),
]
USERS = [  # username, role, organization, facilities
    ("officer", "officer", "pune-dho", []),
    ("wagholi_staff", "employee", "pune-dho", ["phc-wagholi"]),
    ("technician", "technician", "pune-dho", ["phc-wagholi", "phc-lonikand"]),
    ("driver", "driver", "pune-dho", []),
]


class Command(BaseCommand):
    help = "Load the Pune demo network and demo users."

    def add_arguments(self, parser):
        parser.add_argument("--no-users", action="store_true", help="skip creating demo users")

    @transaction.atomic
    def handle(self, *args, **opts):
        for name, fs, note in VACCINES:
            Vaccine.objects.update_or_create(name=name, defaults=dict(freeze_sensitive=fs, note=note))
        for slug, name, kind, city, district in ORGS:
            Organization.objects.update_or_create(slug=slug, defaults=dict(name=name, kind=kind, city=city, district=district))
        for slug, org, name, taluka, lat, lon in FACILITIES:
            Facility.objects.update_or_create(slug=slug, defaults=dict(organization_id=org, name=name, taluka=taluka,
                                                                       district="Pune", latitude=lat, longitude=lon))
        for i, (slug, fac, label, cls, stock) in enumerate(UNITS):
            u, _ = StorageUnit.objects.update_or_create(slug=slug, defaults=dict(facility_id=fac, label=label, cls=cls,
                                                                                 sort_order=i))
            StockItem.objects.filter(unit=u).exclude(vaccine_id__in=stock).delete()
            for p, v in enumerate(stock):
                StockItem.objects.update_or_create(unit=u, vaccine_id=v, defaults=dict(position=p))
        for name, phone, facs in TECHNICIANS:
            t, _ = Technician.objects.update_or_create(name=name, defaults=dict(phone=phone))
            t.facilities.set(facs)
        made = []
        if not opts["no_users"]:
            pw = os.environ.get("TT_DEMO_PASSWORD", "thermotwin-demo")
            User = get_user_model()
            for username, role, org, facs in USERS:
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_password(pw)
                    user.save()
                    made.append(username)
                p, _ = Profile.objects.update_or_create(user=user, defaults=dict(role=role, organization_id=org))
                p.facilities.set(facs)
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(ORGS)} organizations, {len(FACILITIES)} facilities, {len(UNITS)} units, "
            f"{len(VACCINES)} vaccines, {len(TECHNICIANS)} technicians"
            + (f"; new demo users: {', '.join(made)} (password from TT_DEMO_PASSWORD)" if made else "")))
