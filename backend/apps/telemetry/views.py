from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.accounts.permissions import role_of
from apps.facilities.models import StorageUnit

from . import services
from .models import Device
from .serializers import ClockActionSerializer, IngestSerializer


def _public_state() -> dict:
    return services.clock_state()


@api_view(["GET"])
@permission_classes([AllowAny])
def state(request):
    """GET /api/state: demo clock."""
    return Response(_public_state())


@api_view(["POST"])
@permission_classes([AllowAny])
def clock(request):
    """POST /api/clock {action: play|pause|reset|step, ticks}: drive the demo replay (open, it is a demo control)."""
    s = ClockActionSerializer(data=request.data)
    if not s.is_valid():
        return Response({"detail": "action must be play, pause, reset or step"}, status=400)
    d = s.validated_data
    services.clock_action(d["action"], d.get("ticks", 1), d.get("seconds_per_tick"))
    return Response(_public_state())


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def readings(request):
    """GET /api/readings?unit=&source=live: stored readings.
    POST /api/readings: {device_id, readings:[{timestamp, temp_c}]} with header X-Device-Key,
                        or {unit, readings:[...]} as a logged-in user."""
    if request.method == "GET":
        src = request.GET.get("source", services.LIVE)
        rows = services.readings(src, request.GET.get("unit"))
        return Response({"source": src, "store": services.store().name, "readings": rows[-500:]})

    s = IngestSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    d = s.validated_data
    if d.get("device_id"):
        dev = Device.objects.filter(device_id=d["device_id"]).select_related("unit").first()
        if dev is None or not dev.check_key(request.headers.get("X-Device-Key", "")):
            return Response({"detail": "unknown device or wrong key"}, status=status.HTTP_403_FORBIDDEN)
        unit = dev.unit
    else:
        if role_of(request.user) is None:
            return Response({"detail": "log in or send a device key"}, status=status.HTTP_401_UNAUTHORIZED)
        unit = StorageUnit.objects.filter(slug=d["unit"]).first()
        if unit is None:
            return Response({"detail": f"unknown unit {d['unit']}"}, status=404)
    res = services.ingest(unit, [dict(r) for r in d["readings"]])
    return Response(res, status=status.HTTP_201_CREATED if res["stored"] else status.HTTP_400_BAD_REQUEST)
