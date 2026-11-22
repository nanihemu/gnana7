from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "core"

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("me/", views.MeView.as_view(), name="me"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]