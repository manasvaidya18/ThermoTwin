"""Alert endpoints. The first five keep the exact shape the website and phone app already use."""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.permissions import IsStaff
from apps.telemetry import services as telemetry

from . import prediction_client, services
from .models import Acknowledgement, AlertEvent
from .serializers import AcknowledgeSerializer, AlertEventSerializer


def _state() -> dict:
    return telemetry.clock_state()


@api_view(["GET"])
@permission_classes([AllowAny])
def fridges(request):
    """GET /api/fridges: every unit with tier, Virtual Vial, risk, countdown, cause, recovery note, cooling health."""
    s = _state()
    return Response({"state": s, "fridges": services.engine().fleet(s["tick"])})


@api_view(["GET"])
@permission_classes([AllowAny])
def fridge_detail(request, fid: str):
    """GET /api/fridges/<id>?hours=24: one unit with history, forecast and 24 h exposure."""
    eng = services.engine()
    if not eng.has(fid):
        return Response({"detail": f"unknown fridge {fid}"}, status=404)
    try:
        hours = max(1, min(int(request.GET.get("hours", 24)), 48))
    except ValueError:
        hours = 24
    return Response(eng.detail(fid, _state()["tick"], hours=hours))


@api_view(["GET"])
@permission_classes([AllowAny])
def active_alerts(request):
    s = _state()
    return Response({"state": s, "alerts": [f for f in services.engine().fleet(s["tick"]) if f["tier"] != "Normal"]})


@api_view(["GET"])
@permission_classes([AllowAny])
def alert_history(request):
    s = _state()
    eng = services.engine()
    return Response({"state": s, "events": services.history(eng.source, s["tick"], request.GET.get("fridge_id"))})


@api_view(["POST"])
@permission_classes([IsStaff])
def acknowledge(request, event_id: int):
    """POST /api/alerts/<id>/acknowledge {note}: staff confirm they are acting on an alert (stops escalation)."""
    ev = AlertEvent.objects.filter(id=event_id).first()
    if ev is None:
        return Response({"detail": "unknown alert"}, status=404)
    s = AcknowledgeSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    Acknowledgement.objects.create(event=ev, user=request.user, note=s.validated_data.get("note", ""))
    return Response(AlertEventSerializer(ev).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def unit_live(request, unit: str):
    """GET /api/units/<id>/live: latest status from the unit's live device readings (ESP32 / eVIN)."""
    res = services.live_summary(unit)
    if res is None:
        return Response({"detail": "no live readings for this unit yet (need at least 2)"}, status=404)
    return Response(res)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    from django.db import connection
    return Response({"backend": {"ok": True, "framework": "django", "database": connection.vendor},
                     "timeseries": {"store": telemetry.store().name},
                     "prediction_engine": {"ok": True, "mode": prediction_client.mode()}})
