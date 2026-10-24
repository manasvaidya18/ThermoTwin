"""Organizations: a government health department (city / district) or a private cold-storage company."""
from django.db import models


class Organization(models.Model):
    GOVERNMENT, PRIVATE = "government", "private"
    KINDS = [(GOVERNMENT, "Government"), (PRIVATE, "Private")]

    slug = models.SlugField(primary_key=True, max_length=64)
    name = models.CharField(max_length=200)
    kind = models.CharField(max_length=16, choices=KINDS, default=GOVERNMENT)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
