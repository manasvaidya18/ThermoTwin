"""Role-based permissions."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


def role_of(user) -> str | None:
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return "admin"
    p = getattr(user, "profile", None)
    return p.role if p else None


class IsOfficer(BasePermission):
    def has_permission(self, request, view):
        return role_of(request.user) in ("admin", "officer")


class IsOfficerOrReadOnly(BasePermission):
    """Anyone may read (demo dashboards); only officers and admins may change network configuration."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or role_of(request.user) in ("admin", "officer")


class IsStaff(BasePermission):
    """Any logged-in ThermoTwin user (officer, employee, technician, driver, admin)."""
    def has_permission(self, request, view):
        return role_of(request.user) is not None
