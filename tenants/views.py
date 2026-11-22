from decimal import Decimal

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Role, Tenant, User
from core.permissions import IsSuperAdmin
from core.serializers import TenantSerializer
from tenants.models import Plan, PlatformTransaction, Subscription

from .serializers import (
    PlanSerializer,
    PlatformStatsSerializer,
    PlatformTransactionSerializer,
    RoleSerializer,
    SubscriptionSerializer,
)


class TenantListCreateView(generics.ListCreateAPIView):
    """Super Admin: list all schools or create a new one."""

    permission_classes = [IsSuperAdmin]
    serializer_class = TenantSerializer

    def get_queryset(self):
        return Tenant.objects.all().order_by("-created_at")


class TenantDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = TenantSerializer

    def get_queryset(self):
        return Tenant.objects.all()


class PlanListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()


class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()


class SubscriptionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        qs = Subscription.objects.all()
        tenant_id = self.request.query_params.get("tenant_id")
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        return qs.select_related("tenant", "plan")


class PlatformTransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = PlatformTransactionSerializer

    def get_queryset(self):
        return PlatformTransaction.objects.all().select_related("tenant")


class RoleListCreateView(generics.ListCreateAPIView):
    """Super Admin: define/refine roles and their privilege keys."""

    permission_classes = [IsSuperAdmin]
    serializer_class = RoleSerializer
    queryset = Role.objects.all()


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = RoleSerializer
    queryset = Role.objects.all()


class PlatformStatsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        tenants_total = Tenant.objects.all().count()
        tenants_active = Tenant.objects.filter(is_active=True).count()
        users_total = User.objects.all().count()
        active_subs = Subscription.objects.filter(
            status__in=[Subscription.Status.ACTIVE, Subscription.Status.TRIALING]
        ).select_related("plan")

        mrr = Decimal("0")
        for sub in active_subs:
            price = (
                sub.plan.monthly_price
                if sub.billing_cycle == Subscription.BillingCycle.MONTHLY
                else (sub.plan.annual_price / 12)
            )
            mrr += price

        data = PlatformStatsSerializer(
            {
                "tenants_total": tenants_total,
                "tenants_active": tenants_active,
                "users_total": users_total,
                "active_subscriptions": active_subs.count(),
                "mrr_inr": mrr,
                "arr_inr": mrr * 12,
            }
        ).data
        return Response(data)