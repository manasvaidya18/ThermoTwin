from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import services
from .serializers import SummarySerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def summary(request):
    """GET /api/reports/summary: units per tier, maintenance due, open incidents, 24 h exposure per unit."""
    return Response(SummarySerializer(services.summary()).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def alerts_csv(request):
    """GET /api/reports/alerts.csv?unit=: alert history export."""
    r = HttpResponse(services.alert_history_csv(request.GET.get("unit")), content_type="text/csv")
    r["Content-Disposition"] = 'attachment; filename="thermotwin_alerts.csv"'
    return r


@api_view(["GET"])
@permission_classes([AllowAny])
def incidents_csv(request):
    r = HttpResponse(services.incidents_csv(), content_type="text/csv")
    r["Content-Disposition"] = 'attachment; filename="thermotwin_incidents.csv"'
    return r
