from rest_framework import serializers


class SummarySerializer(serializers.Serializer):
    clock = serializers.CharField()
    units = serializers.IntegerField()
    by_tier = serializers.DictField(child=serializers.IntegerField())
    maintenance_due = serializers.ListField(child=serializers.DictField())
    open_incidents = serializers.IntegerField()
    exposure_24h = serializers.ListField(child=serializers.DictField())
