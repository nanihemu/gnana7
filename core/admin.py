from django.contrib import admin

from .models import Role, Tenant, User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "subdomain", "is_active", "created_at")
    search_fields = ("name", "slug", "subdomain")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "full_name", "role", "tenant", "is_active")
    list_filter = ("role", "tenant")
    search_fields = ("username", "full_name", "email")
