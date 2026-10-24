from rest_framework import viewsets

from apps.accounts.permissions import IsOfficerOrReadOnly

from .models import Facility, StockItem, StorageUnit, Technician, Vaccine
from .serializers import (FacilitySerializer, StockItemSerializer, StorageUnitSerializer, TechnicianSerializer,
                          VaccineSerializer)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.prefetch_related("units__stock", "technicians")
    serializer_class = FacilitySerializer
    permission_classes = [IsOfficerOrReadOnly]


class StorageUnitViewSet(viewsets.ModelViewSet):
    queryset = StorageUnit.objects.select_related("facility").prefetch_related("stock")
    serializer_class = StorageUnitSerializer
    permission_classes = [IsOfficerOrReadOnly]


class VaccineViewSet(viewsets.ModelViewSet):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer
    permission_classes = [IsOfficerOrReadOnly]


class StockItemViewSet(viewsets.ModelViewSet):
    queryset = StockItem.objects.all()
    serializer_class = StockItemSerializer
    permission_classes = [IsOfficerOrReadOnly]


class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.prefetch_related("facilities")
    serializer_class = TechnicianSerializer
    permission_classes = [IsOfficerOrReadOnly]
