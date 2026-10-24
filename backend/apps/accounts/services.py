"""Account services: create users with a role, issue login tokens."""
from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

from .models import Profile

User = get_user_model()


@transaction.atomic
def create_user(username: str, password: str, role: str, organization: str | None = None,
                facilities: list[str] | None = None, first_name: str = "", phone: str = ""):
    user = User.objects.create_user(username=username, password=password, first_name=first_name)
    profile = Profile.objects.create(user=user, role=role, organization_id=organization or None, phone=phone)
    if facilities:
        profile.facilities.set(facilities)
    return user


def login(username: str, password: str) -> tuple[object, str] | None:
    user = authenticate(username=username, password=password)
    if user is None:
        return None
    token, _ = Token.objects.get_or_create(user=user)
    return user, token.key
