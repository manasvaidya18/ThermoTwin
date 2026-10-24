from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import services
from .permissions import IsOfficer
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """POST /api/auth/login {username, password} -> {token, user}. Send the token as 'Authorization: Token <token>'."""
    s = LoginSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    res = services.login(s.validated_data["username"], s.validated_data["password"])
    if res is None:
        return Response({"detail": "wrong username or password"}, status=status.HTTP_400_BAD_REQUEST)
    user, token = res
    return Response({"token": token, "user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsOfficer])
def register(request):
    """Officers create accounts for their staff (employees, technicians, drivers, other officers)."""
    s = RegisterSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    d = s.validated_data
    user = services.create_user(d["username"], d["password"], d["role"], d.get("organization"), d.get("facilities"),
                                d.get("first_name", ""), d.get("phone", ""))
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
