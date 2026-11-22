from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class MeView(APIView):
    """Return the current authenticated user's profile + their permissions."""

    def get(self, request):
        serializer = UserSerializer(request.user)
        data = serializer.data
        # Surface the user's privilege keys so frontends can gate UI.
        data["permissions"] = request.user_permissions if hasattr(request, "user_permissions") else []
        return Response(data)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "sms-api"})


# Re-export generics for reuse across apps.
__all__ = ["generics", "permissions", "Response", "User", "UserSerializer"]