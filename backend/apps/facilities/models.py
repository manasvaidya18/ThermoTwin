"""Facilities (PHCs, hospitals, cold stores), their storage units (fridges, freezers, cold rooms), stock and technicians."""
from django.db import models


class Facility(models.Model):
    slug = models.SlugField(primary_key=True, max_length=64)
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="facilities")
    name = models.CharField(max_length=200)
    taluka = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "facilities"

    def __str__(self) -> str:
        return self.name


class StorageUnit(models.Model):
    """One temperature-controlled unit: a fridge (ILR / domestic), a freezer or a cold room."""
    ILR, DOMESTIC, FREEZER, COLD_ROOM = "ILR", "DOMESTIC", "FREEZER", "COLD_ROOM"
    CLASSES = [(ILR, "Ice-lined refrigerator"), (DOMESTIC, "Domestic fridge"), (FREEZER, "Freezer"),
               (COLD_ROOM, "Walk-in cold room")]

    slug = models.SlugField(primary_key=True, max_length=64)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name="units")
    label = models.CharField(max_length=64)
    cls = models.CharField("unit type", max_length=16, choices=CLASSES, default=ILR)
    min_temp_c = models.FloatField(default=2.0)
    max_temp_c = models.FloatField(default=8.0)
    sort_order = models.IntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "slug"]

    def __str__(self) -> str:
        return f"{self.facility.name} · {self.label}"


class Vaccine(models.Model):
    name = models.CharField(primary_key=True, max_length=64)
    freeze_sensitive = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True)

    def __str__(self) -> str:
        return self.name


class StockItem(models.Model):
    unit = models.ForeignKey(StorageUnit, on_delete=models.CASCADE, related_name="stock")
    vaccine = models.ForeignKey(Vaccine, on_delete=models.PROTECT)
    doses = models.IntegerField(null=True, blank=True)
    position = models.IntegerField(default=0)

    class Meta:
        ordering = ["unit", "position"]
        unique_together = [("unit", "vaccine")]


class Technician(models.Model):
    """Saved at onboarding so site staff can call the right person from an alert."""
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    facilities = models.ManyToManyField(Facility, related_name="technicians", blank=True)

    def __str__(self) -> str:
        return self.name
