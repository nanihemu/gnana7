from django.contrib import admin

from .models import Plan, PlatformTransaction, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "monthly_price", "annual_price", "is_active")
    search_fields = ("name", "code")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("tenant", "plan", "billing_cycle", "status", "ends_at")
    list_filter = ("status", "billing_cycle")


@admin.register(PlatformTransaction)
class PlatformTransactionAdmin(admin.ModelAdmin):
    list_display = ("tenant", "kind", "amount", "currency", "status", "created_at")
    list_filter = ("kind", "status")
