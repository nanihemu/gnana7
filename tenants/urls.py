from django.urls import path

from . import views

app_name = "tenants"

urlpatterns = [
    # Super Admin: platform/tenant management
    path("tenants/", views.TenantListCreateView.as_view(), name="tenant-list"),
    path("tenants/<int:pk>/", views.TenantDetailView.as_view(), name="tenant-detail"),
    path("plans/", views.PlanListCreateView.as_view(), name="plan-list"),
    path("plans/<int:pk>/", views.PlanDetailView.as_view(), name="plan-detail"),
    path("subscriptions/", views.SubscriptionListCreateView.as_view(), name="subscription-list"),
    path(
        "transactions/",
        views.PlatformTransactionListCreateView.as_view(),
        name="transaction-list",
    ),
    path("roles/", views.RoleListCreateView.as_view(), name="role-list"),
    path("roles/<int:pk>/", views.RoleDetailView.as_view(), name="role-detail"),
    path("platform/stats/", views.PlatformStatsView.as_view(), name="platform-stats"),
]