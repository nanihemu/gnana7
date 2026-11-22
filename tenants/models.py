from django.db import models
from django.conf import settings


class Plan(models.Model):
    """A subscription plan the Super Admin offers (free/standard/premium)."""

    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=50, unique=True)
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_students = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    max_teachers = models.PositiveIntegerField(default=0)
    max_storage_gb = models.PositiveIntegerField(default=5)
    ai_features = models.JSONField(default=list, help_text="Enabled AI feature keys")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "plans"

    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Which plan a tenant is on, and its billing cycle."""

    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past Due"
        CANCELED = "canceled", "Canceled"

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    billing_cycle = models.CharField(max_length=10, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TRIALING)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tenant} · {self.plan}"


class PlatformTransaction(models.Model):
    """Money moving on the platform (subscription payments, refunds)."""

    class Kind(models.TextChoices):
        SUBSCRIPTION = "subscription", "Subscription"
        ADDON = "addon", "Add-on"
        REFUND = "refund", "Refund"

    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, related_name="platform_transactions")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.SUBSCRIPTION)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=20, default="succeeded")
    gateway_ref = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "platform_transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tenant} · {self.kind} · {self.amount}"