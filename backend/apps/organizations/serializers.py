from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    facility_count = serializers.IntegerField(source="facilities.count", read_only=True)

    class Meta:
        model = Organization
        fields = ["slug", "name", "kind", "city", "district", "facility_count", "created_at"]
