from rest_framework import serializers

from .models import Acknowledgement, AlertEvent


class AcknowledgementSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True, default=None)

    class Meta:
        model = Acknowledgement
        fields = ["id", "user", "note", "created_at"]


class AlertEventSerializer(serializers.ModelSerializer):
    acknowledgements = AcknowledgementSerializer(many=True, read_only=True)

    class Meta:
        model = AlertEvent
        fields = ["id", "source", "unit", "tick", "tier", "kind", "message", "created_at", "escalation_level",
                  "escalated_at", "acknowledgements"]


class AcknowledgeSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=300)
