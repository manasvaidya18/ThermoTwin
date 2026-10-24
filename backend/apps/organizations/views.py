from rest_framework import viewsets

from apps.accounts.permissions import IsOfficerOrReadOnly

from .serializers import OrganizationSerializer
from .services import visible_organizations


class OrganizationViewSet(viewsets.ModelViewSet):
    """Government health departments and private cold-storage companies."""
    serializer_class = OrganizationSerializer
    permission_classes = [IsOfficerOrReadOnly]

    def get_queryset(self):
        return visible_organizations(self.request.user)
