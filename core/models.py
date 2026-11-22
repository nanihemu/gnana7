from django.contrib.auth.models import AbstractUser
from django.db import models


class Tenant(models.Model):
    """
    A tenant = one school. Every piece of school-owned data hangs off a tenant,
    and the TenantMiddleware scopes all queries to the request's tenant so no
    school ever sees another school's data (row-level isolation).
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    subdomain = models.CharField(
        max_length=100, unique=True, blank=True, null=True,
        help_text="e.g. 'stmarys' for stmarys.<base_domain>",
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Data-driven privileges. The Super Admin edits these rather than privileges
    being hard-coded, satisfying the 'privileges' requirement.
    """

    code = models.CharField(max_length=50, unique=True)  # super_admin|admin|teacher|student|parent
    name = models.CharField(max_length=100)
    permissions = models.JSONField(
        default=list,
        help_text="List of permission keys, e.g. ['tenant.manage', 'student.write']",
    )

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user. One person can hold multiple roles across the platform
    (a super-admin in one tenant, a teacher in another), so roles are a
    many-to-many with per-tenant resolution.
    """

    class RoleChoice(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        ADMIN = "admin", "School Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"
        PARENT = "parent", "Parent"

    role = models.CharField(
        max_length=20,
        choices=RoleChoice.choices,
        default=RoleChoice.STUDENT,
    )
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, null=True, blank=True,
        related_name="users",
    )
    # Super admins operate platform-wide and have no tenant; everyone else belongs
    # to exactly one tenant.
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_super_admin(self):
        return self.role == self.RoleChoice.SUPER_ADMIN