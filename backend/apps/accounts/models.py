"""User profiles with a role: officers (district / zonal / company) see the network; employees work at facilities."""
from django.conf import settings
from django.db import models


class Profile(models.Model):
    ADMIN, OFFICER, EMPLOYEE, TECHNICIAN, DRIVER = "admin", "officer", "employee", "technician", "driver"
    ROLES = [(ADMIN, "Admin"), (OFFICER, "Officer"), (EMPLOYEE, "Facility employee"), (TECHNICIAN, "Technician"),
             (DRIVER, "Cold-chain driver")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=16, choices=ROLES, default=EMPLOYEE)
    organization = models.ForeignKey("organizations.Organization", null=True, blank=True, on_delete=models.SET_NULL)
    facilities = models.ManyToManyField("facilities.Facility", blank=True, related_name="staff")
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"
