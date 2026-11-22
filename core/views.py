from pathlib import Path

from django.http import FileResponse, Http404
from django.conf import settings
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


def spa_index(request, path=""):
    """Serve the built React SPA (single entrypoint with history fallback).

    The catch-all is only mounted after the /api/v1/ includes, and the regex
    excludes /api, /admin, /static and /media, so this only answers browser
    navigation to SPA routes like /login or /classes.
    """
    index = Path(settings.BASE_DIR) / "frontend" / "dist" / "index.html"
    if not index.exists():
        raise Http404(
            "Frontend not built. Run `npm run build` in frontend/ (or use the "
            "Vite dev server during development)."
        )
    return FileResponse(index.open("rb"), content_type="text/html")


# Re-export generics for reuse across apps.
__all__ = ["generics", "permissions", "Response", "User", "UserSerializer"]