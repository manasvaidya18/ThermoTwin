"""Incidents: corrective actions after an alert, and maintenance tickets from the slow loop."""
from django.conf import settings
from django.db import models


class Incident(models.Model):
    EXCURSION, MAINTENANCE, SENSOR, TRANSFER = "excursion", "maintenance", "sensor", "transfer"
    KINDS = [(EXCURSION, "Temperature excursion"), (MAINTENANCE, "Maintenance (cooling weakening)"),
             (SENSOR, "Sensor problem"), (TRANSFER, "Stock transfer")]
    OPEN, ASSIGNED, RESOLVED = "open", "assigned", "resolved"
    STATUSES = [(OPEN, "Open"), (ASSIGNED, "Technician assigned"), (RESOLVED, "Resolved")]

    unit = models.ForeignKey("facilities.StorageUnit", on_delete=models.CASCADE, related_name="incidents")
    kind = models.CharField(max_length=16, choices=KINDS)
    status = models.CharField(max_length=16, choices=STATUSES, default=OPEN)
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    technician = models.ForeignKey("facilities.Technician", null=True, blank=True, on_delete=models.SET_NULL)
    alert_event = models.ForeignKey("alerts.AlertEvent", null=True, blank=True, on_delete=models.SET_NULL)
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
                                  related_name="incidents_opened")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class IncidentAction(models.Model):
    """What someone did: 'turned thermostat warmer', 'moved Pentavalent to ILR-2', 'replaced door gasket'."""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="actions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
