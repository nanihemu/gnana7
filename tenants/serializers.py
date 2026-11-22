from rest_framework import serializers

from core.models import Role, Tenant
from .models import Plan, PlatformTransaction, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id", "name", "code", "monthly_price", "annual_price",
            "max_students", "max_teachers", "max_storage_gb",
            "ai_features", "is_active",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)
    plan_name = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id", "tenant", "tenant_name", "plan", "plan_name",
            "billing_cycle", "status", "starts_at", "ends_at",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class PlatformTransactionSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = PlatformTransaction
        fields = [
            "id", "tenant", "tenant_name", "subscription", "kind",
            "amount", "currency", "status", "gateway_ref", "created_at",
        ]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "permissions"]


class PlatformStatsSerializer(serializers.Serializer):
    """Aggregate platform-level numbers for the Super Admin dashboard."""

    tenants_total = serializers.IntegerField()
    tenants_active = serializers.IntegerField()
    users_total = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    mrr_inr = serializers.DecimalField(max_digits=12, decimal_places=2)
    arr_inr = serializers.DecimalField(max_digits=12, decimal_places=2)