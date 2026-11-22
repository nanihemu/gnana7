import threading

from django.utils.deprecation import MiddlewareMixin

# Thread-local tenant context. The middleware sets it from the authenticated
# user for the duration of a request; models can read it to auto-scope queries.
_local = threading.local()


def get_current_tenant():
    """Return the Tenant instance for the current request thread, or None."""
    return getattr(_local, "tenant", None)


def get_current_user():
    """Return the authenticated user for the current request thread, or None."""
    return getattr(_local, "user", None)


class TenantMiddleware(MiddlewareMixin):
    """
    Injects the current tenant (and user) into thread-local storage for each
    request so the rest of the codebase can scope queries and enforce
    row-level isolation automatically.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = getattr(request, "user", None)
        tenant = None
        if user is not None and user.is_authenticated:
            tenant = getattr(user, "tenant", None)
        _local.tenant = tenant
        _local.user = user
        return None

    def process_response(self, request, response):
        # Clean up so nothing leaks across requests/threads.
        _local.tenant = None
        _local.user = None
        return response