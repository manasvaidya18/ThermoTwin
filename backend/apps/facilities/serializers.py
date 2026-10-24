from rest_framework import serializers

from .models import Facility, StockItem, StorageUnit, Technician, Vaccine


class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = ["name", "freeze_sensitive", "note"]


class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = ["id", "unit", "vaccine", "doses", "position"]


class StorageUnitSerializer(serializers.ModelSerializer):
    facility_name = serializers.CharField(source="facility.name", read_only=True)
    stock = serializers.SerializerMethodField()

    class Meta:
        model = StorageUnit
        fields = ["slug", "facility", "facility_name", "label", "cls", "min_temp_c", "max_temp_c", "sort_order",
                  "active", "stock"]

    def get_stock(self, obj):
        return [s.vaccine_id for s in obj.stock.all()]


class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = ["id", "name", "phone", "facilities"]


class FacilitySerializer(serializers.ModelSerializer):
    units = StorageUnitSerializer(many=True, read_only=True)
    technicians = TechnicianSerializer(many=True, read_only=True)

    class Meta:
        model = Facility
        fields = ["slug", "organization", "name", "taluka", "district", "latitude", "longitude", "units", "technicians"]
