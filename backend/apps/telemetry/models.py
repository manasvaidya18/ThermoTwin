"""Incoming sensor readings and the devices that send them."""
from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class Reading(models.Model):
    """One logger reading (every 10 minutes, like eVIN). temp_c is null for a missing reading."""
    unit = models.ForeignKey("facilities.StorageUnit", on_delete=models.CASCADE, related_name="readings")
    source = models.CharField(max_length=64, help_text="scenario name, 'live' for device data, or an upload batch")
    tick = models.IntegerField(help_text="10-minute index from the start of the source")
    minute = models.IntegerField()
    temp_c = models.FloatField(null=True)
    recorded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["source", "unit", "tick"]
        unique_together = [("source", "unit", "tick")]
        indexes = [models.Index(fields=["source", "unit", "tick"])]


class Device(models.Model):
    """A sensor gateway (ESP32, or an eVIN feed) allowed to post readings for one unit."""
    device_id = models.CharField(primary_key=True, max_length=64)
    unit = models.ForeignKey("facilities.StorageUnit", on_delete=models.CASCADE, related_name="devices")
    key_hash = models.CharField(max_length=128)
    last_seen = models.DateTimeField(null=True, blank=True)

    def set_key(self, raw: str) -> None:
        self.key_hash = make_password(raw)

    def check_key(self, raw: str) -> bool:
        return check_password(raw, self.key_hash)
