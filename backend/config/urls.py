"""Root URLs: REST API under /api/, Django admin under /admin/, and the static frontend for everything else."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path, re_path

from . import frontend

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.organizations.urls")),
    path("api/", include("apps.facilities.urls")),
    path("api/", include("apps.telemetry.urls")),
    path("api/", include("apps.alerts.urls")),
    path("api/", include("apps.incidents.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("", frontend.index),
    re_path(r"^(?!api/|admin/)(?P<path>.+)$", frontend.frontend_file),
]
