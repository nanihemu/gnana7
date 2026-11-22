from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Platform-level access: only users with role super_admin."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_super_admin)


class IsSchoolAdmin(BasePermission):
    """School-level admin: role admin within a tenant."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role == user.RoleChoice.ADMIN
        )


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role == user.RoleChoice.TEACHER
        )


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role == user.RoleChoice.STUDENT
        )


class IsParent(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role == user.RoleChoice.PARENT
        )


class HasRole(BasePermission):
    """Role gate: pass the allowed role codes, e.g. HasRole(['admin', 'teacher'])."""

    def __init__(self, roles):
        self.roles = roles

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in self.roles)

    def has_object_permission(self, request, view, obj):
        # Tenant-scoped objects must match the current user's tenant.
        tenant = getattr(obj, "tenant", None)
        if tenant is not None:
            return tenant.id == getattr(request.user, "tenant_id", None)
        return True