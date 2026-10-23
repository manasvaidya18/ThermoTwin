"""URL routes for ThermoTwin Core API (/api/*)."""
from __future__ import annotations

from django.urls import path
from . import views

urlpatterns = [
    path("state", views.state, name="state"),
    path("clock", views.clock, name="clock"),
    path("fridges", views.fridges, name="fridges"),
    path("fridges/<str:fid>", views.fridge_detail, name="fridge_detail"),
    path("alerts", views.active_alerts, name="alerts"),
    path("alerts/history", views.alert_history, name="alert_history"),
    path("health", views.health, name="health"),
]
