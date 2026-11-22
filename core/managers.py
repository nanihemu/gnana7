from django.db import models

from .middleware import get_current_tenant


class TenantManager(models.Manager):
    """
    Base manager that automatically scopes queries to the current tenant,
    enforcing row-level isolation unless explicitly overridden with .all_objects.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is not None:
            qs = qs.filter(tenant=tenant)
        return qs


class AllObjectsManager(models.Manager):
    """Unscoped manager for Super-Admin / platform-wide queries."""

    def get_queryset(self):
        return super().get_queryset()


class TenantModel(models.Model):
    """
    Abstract base for every school-scoped model. Attaches a tenant FK and swaps
    the default manager for a tenant-scoped one, so that all normal ORM queries
    are isolated to the current school automatically.
    """

    tenant = models.ForeignKey(
        "core.Tenant",
        on_delete=models.CASCADE,
        related_name="%(class)s_set",
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True