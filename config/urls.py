"""Root URL configuration: mounts each module under /api/v1/."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from core.views import spa_index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("core.urls")),
    path("api/v1/", include("tenants.urls")),
    path("api/v1/", include("academics.urls")),
    path("api/v1/", include("ai.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# SPA fallback: any non-API, non-admin, non-static path serves the React app's
# index.html so client-side routing (react-router) works when Django serves the
# built frontend (e.g. the Docker image). Mounted last on purpose.
urlpatterns += [
    re_path(r"^(?!api/|admin/|static/|media/).*$", spa_index),
]