from rest_framework import serializers

from .models import Device, Reading


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reading
        fields = ["id", "unit", "source", "tick", "minute", "temp_c", "recorded_at"]


class RawReadingSerializer(serializers.Serializer):
    timestamp = serializers.CharField(help_text="ISO 8601, e.g. 2026-10-24T10:20:00+05:30")
    temp_c = serializers.FloatField(allow_null=True)


class IngestSerializer(serializers.Serializer):
    """Readings from a device (device_id + X-Device-Key header) or from a logged-in user (unit)."""
    device_id = serializers.CharField(required=False)
    unit = serializers.CharField(required=False)
    readings = RawReadingSerializer(many=True)

    def validate(self, attrs):
        if not attrs.get("device_id") and not attrs.get("unit"):
            raise serializers.ValidationError("send device_id (with X-Device-Key) or unit")
        return attrs


class ClockActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["play", "pause", "reset", "step"])
    ticks = serializers.IntegerField(required=False, default=1)
    seconds_per_tick = serializers.FloatField(required=False, allow_null=True)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["device_id", "unit", "last_seen"]
