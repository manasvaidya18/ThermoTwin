"""End-to-end API tests (Django test database).

Run from the repo root:  python backend/manage.py test tests
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from apps.alerts import services as alerts
from apps.telemetry import services as telemetry
from apps.telemetry.models import Device


class ThermoTwinAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def setUp(self):
        alerts.reset_engine()
        telemetry.clock().reset()
        self.c = APIClient()

    def login(self, username: str) -> None:
        import os
        r = self.c.post("/api/auth/login", {"username": username, "password": os.environ.get("TT_DEMO_PASSWORD", "thermotwin-demo")},
                        format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.c.credentials(HTTP_AUTHORIZATION="Token " + r.json()["token"])

    def test_demo_story_alert_flow_and_reports(self):
        """Wagholi: Advisory -> Early warning -> Critical, with cause, reasons, technician; then acknowledge + report."""
        tiers = []
        for _ in range(12):
            d = self.c.get("/api/fridges/wagholi-ilr1").json()
            tiers.append(d["tier"])
            if d["tier"] == "Early warning":
                self.assertTrue(d["why"], "an early warning should say why")
            self.c.post("/api/clock", {"action": "step", "ticks": 6}, format="json")
        self.assertLess(tiers.index("Early warning"), tiers.index("Critical"))
        d = self.c.get("/api/fridges/wagholi-ilr1").json()
        self.assertEqual(d["cause"]["key"], "cooling_too_hard")
        self.assertEqual(d["technicians"][0]["name"], "Meena P. (Central)")
        self.assertIn("maintenance", d)
        self.assertIn("recovery", d)

        events = self.c.get("/api/alerts/history", {"fridge_id": "wagholi-ilr1"}).json()["events"]
        crit = next(e for e in events if e["tier"] == "Critical")
        self.assertEqual(self.c.post(f"/api/alerts/{crit['id']}/acknowledge", {"note": "x"}, format="json").status_code, 401)
        self.login("wagholi_staff")
        r = self.c.post(f"/api/alerts/{crit['id']}/acknowledge", {"note": "Thermostat turned warmer"}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["acknowledgements"][0]["note"], "Thermostat turned warmer")

        s = self.c.get("/api/reports/summary").json()
        self.assertEqual(s["units"], 6)
        self.assertIn("Critical", s["by_tier"])
        csv = self.c.get("/api/reports/alerts.csv")
        self.assertEqual(csv.status_code, 200)
        self.assertIn(b"wagholi-ilr1", csv.content)

    def test_unknown_fridge_bad_clock_and_frontend(self):
        self.assertEqual(self.c.get("/api/fridges/nope").status_code, 404)
        self.assertEqual(self.c.post("/api/clock", {"action": "jump"}, format="json").status_code, 400)
        self.assertEqual(self.c.get("/web/overview.html").status_code, 200)
        self.assertEqual(self.c.get("/../backend/config/settings.py").status_code, 404)

    def test_roles_and_network_configuration(self):
        self.assertEqual(self.c.get("/api/organizations").status_code, 200)
        self.assertEqual(self.c.post("/api/organizations", {"slug": "x", "name": "X"}, format="json").status_code, 401)
        self.login("wagholi_staff")
        self.assertEqual(self.c.post("/api/organizations", {"slug": "x", "name": "X"}, format="json").status_code, 403)
        self.login("officer")
        r = self.c.post("/api/organizations", {"slug": "acme-cold", "name": "Acme Cold Storage", "kind": "private"}, format="json")
        self.assertEqual(r.status_code, 201)
        r = self.c.post("/api/auth/register", {"username": "new_staff", "password": "longenough1", "role": "employee",
                                               "facilities": ["phc-wagholi"]}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.c.get("/api/facilities/phc-wagholi").json()["units"][0]["stock"][0], "Pentavalent")

    def test_device_ingest_then_live_score(self):
        dev = Device(device_id="esp32-wagholi", unit_id="wagholi-ilr1")
        dev.set_key("secret-key")
        dev.save()
        t0 = datetime(2026, 10, 24, 8, 0, tzinfo=timezone.utc)
        rows = [{"timestamp": (t0 + timedelta(minutes=10 * i)).isoformat(), "temp_c": 5.0 - 0.05 * i} for i in range(40)]
        bad = self.c.post("/api/readings", {"device_id": "esp32-wagholi", "readings": rows}, format="json",
                          HTTP_X_DEVICE_KEY="wrong")
        self.assertEqual(bad.status_code, 403)
        r = self.c.post("/api/readings", {"device_id": "esp32-wagholi", "readings": rows + [{"timestamp": "x", "temp_c": 1}]},
                        format="json", HTTP_X_DEVICE_KEY="secret-key")
        self.assertEqual(r.status_code, 201, r.content)
        self.assertEqual(r.json()["stored"], 40)
        self.assertEqual(len(r.json()["errors"]), 1)
        live = self.c.get("/api/units/wagholi-ilr1/live").json()
        self.assertEqual(live["tick"], 39)
        self.assertAlmostEqual(live["air"], 3.0, delta=0.15)

    def test_incident_lifecycle(self):
        self.login("technician")
        r = self.c.post("/api/incidents", {"unit": "baramati-df01", "kind": "maintenance", "title": "Cooling weakening"},
                        format="json")
        self.assertEqual(r.status_code, 201, r.content)
        inc = r.json()
        self.assertEqual(inc["technician_name"], "Arif S. (South)")
        again = self.c.post("/api/incidents", {"unit": "baramati-df01", "kind": "maintenance", "title": "dup"}, format="json")
        self.assertEqual(again.json()["id"], inc["id"])          # no duplicate ticket
        self.c.post(f"/api/incidents/{inc['id']}/actions", {"text": "Cleaned condenser"}, format="json")
        r = self.c.post(f"/api/incidents/{inc['id']}/resolve", {"text": "Cooling back to normal"}, format="json")
        self.assertEqual(r.json()["status"], "resolved")
        self.assertEqual(len(r.json()["actions"]), 2)
