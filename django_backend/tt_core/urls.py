"""Root URL patterns for ThermoTwin Django project."""
from __future__ import annotations

from django.urls import include, path
from core import views

urlpatterns = [
    # Public API endpoints (/api/*)
    path("api/", include("core.urls")),
    # Serve index.html at root
    path("", views.index, name="index"),
    # Serve static frontend assets (shared/, web/, mobile/, etc.)
    path("<path:path>", views.frontend_files, name="frontend_files"),
]
