from rest_framework import serializers

from .models import Incident, IncidentAction


class IncidentActionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True, default=None)

    class Meta:
        model = IncidentAction
        fields = ["id", "text", "user", "created_at"]


class IncidentSerializer(serializers.ModelSerializer):
    actions = IncidentActionSerializer(many=True, read_only=True)
    technician_name = serializers.CharField(source="technician.name", read_only=True, default=None)
    technician_phone = serializers.CharField(source="technician.phone", read_only=True, default=None)

    class Meta:
        model = Incident
        fields = ["id", "unit", "kind", "status", "title", "notes", "technician", "technician_name", "technician_phone",
                  "alert_event", "created_at", "updated_at", "resolved_at", "actions"]
        read_only_fields = ["status", "resolved_at"]


class ActionSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=300, required=False, allow_blank=True)
