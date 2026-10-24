from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsStaff

from . import services
from .models import Incident
from .serializers import ActionSerializer, IncidentSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    """Corrective actions and maintenance tickets. Reading is open in the demo; changes need a login."""
    queryset = Incident.objects.select_related("technician").prefetch_related("actions")
    serializer_class = IncidentSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return []
        return [IsStaff()]

    def get_queryset(self):
        qs = super().get_queryset()
        for f in ("unit", "kind", "status"):
            if self.request.query_params.get(f):
                qs = qs.filter(**{f if f != "unit" else "unit_id": self.request.query_params[f]})
        return qs

    def perform_create(self, serializer):
        d = serializer.validated_data
        inc, _ = services.open_incident(d["unit"].slug, d["kind"], d["title"], d.get("notes", ""),
                                        d.get("alert_event"), self.request.user)
        serializer.instance = inc

    @action(detail=True, methods=["post"], url_path="actions")
    def add_action(self, request, pk=None):
        """POST /api/incidents/<id>/actions {text}: record what was done."""
        s = ActionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.add_action(self.get_object(), s.validated_data.get("text", ""), request.user)
        return Response(IncidentSerializer(self.get_object()).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """POST /api/incidents/<id>/resolve {text}: close the incident."""
        s = ActionSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        services.resolve(self.get_object(), s.validated_data.get("text", ""), request.user)
        return Response(IncidentSerializer(self.get_object()).data)      # reload: includes the closing action
