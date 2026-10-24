from django.urls import path

from . import views

urlpatterns = [
    path("summary", views.summary),
    path("alerts.csv", views.alerts_csv),
    path("incidents.csv", views.incidents_csv),
]
