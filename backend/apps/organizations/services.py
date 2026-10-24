"""Organization rules: which organizations a user may see."""
from __future__ import annotations

from .models import Organization


def visible_organizations(user):
    """Officers and admins see every organization; everyone else sees their own (all, when not logged in: demo)."""
    qs = Organization.objects.all()
    profile = getattr(user, "profile", None) if user and user.is_authenticated else None
    if profile and profile.role not in ("admin", "officer") and profile.organization_id:
        qs = qs.filter(slug=profile.organization_id)
    return qs
