from django.urls import path

from . import views

urlpatterns = [
    path("fridges", views.fridges),
    path("fridges/<str:fid>", views.fridge_detail),
    path("alerts", views.active_alerts),
    path("alerts/history", views.alert_history),
    path("alerts/<int:event_id>/acknowledge", views.acknowledge),
    path("units/<str:unit>/live", views.unit_live),
    path("health", views.health),
]
