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


def HasRole(roles):
    """
    Role gate. Returns a permission class allowing the given role codes, e.g.
    ``HasRole(["admin", "teacher"])``. A factory (not a class) so it composes
    cleanly with DRF, which instantiates each entry of ``permission_classes``.
    """

    roles = frozenset(roles)
    allowed_roles = roles

    class _HasRole(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            return bool(user and user.is_authenticated and user.role in allowed_roles)

        def has_object_permission(self, request, view, obj):
            # Tenant-scoped objects must match the current user's tenant.
            tenant = getattr(obj, "tenant", None)
            if tenant is not None:
                return tenant.id == getattr(request.user, "tenant_id", None)
            return True

    return _HasRole