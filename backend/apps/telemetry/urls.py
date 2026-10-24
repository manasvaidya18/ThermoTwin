from django.urls import path

from . import views

urlpatterns = [
    path("state", views.state),
    path("clock", views.clock),
    path("readings", views.readings),
]
