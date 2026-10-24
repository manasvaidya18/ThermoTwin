"""Alert events (every tier change), acknowledgements and escalation state."""
from django.conf import settings
from django.db import models


class AlertEvent(models.Model):
    source = models.CharField(max_length=64)
    unit = models.ForeignKey("facilities.StorageUnit", on_delete=models.CASCADE, related_name="alert_events")
    tick = models.IntegerField()
    tier = models.CharField(max_length=32)
    kind = models.CharField(max_length=16, blank=True)
    message = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    escalation_level = models.IntegerField(default=0, help_text="0 = site staff, 1 = officer, 2 = senior officer")
    escalated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-tick", "unit"]
        unique_together = [("source", "unit", "tick", "tier")]

    @property
    def acknowledged(self) -> bool:
        return self.acknowledgements.exists()


class Acknowledgement(models.Model):
    event = models.ForeignKey(AlertEvent, on_delete=models.CASCADE, related_name="acknowledgements")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    note = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
