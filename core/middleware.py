import threading

from django.utils.deprecation import MiddlewareMixin

# Thread-local tenant context. The middleware sets it from the authenticated
# user for the duration of a request; DRF's TenantJWTAuthentication also sets it
# after token auth (which runs after Django middleware, so both are needed).
# Models read it via TenantManager to auto-scope queries.
_local = threading.local()


def get_current_tenant():
    """Return the Tenant instance for the current request thread, or None."""
    return getattr(_local, "tenant", None)


def get_current_user():
    """Return the authenticated user for the current request thread, or None."""
    return getattr(_local, "user", None)


def set_current_context(user):
    """Set tenant+user from an authenticated user (used by DRF auth).

    DRF authenticates JWTs inside the view's dispatch, which is *after* Django
    middleware's process_view. Without this, the thread-local tenant would stay
    None for every API request and tenant isolation would silently no-op.
    """
    if user is not None and user.is_authenticated:
        _local.tenant = getattr(user, "tenant", None)
        _local.user = user
    else:
        _local.tenant = None
        _local.user = None


class TenantMiddleware(MiddlewareMixin):
    """
    Injects the current tenant (and user) into thread-local storage for each
    request so the rest of the codebase can scope queries and enforce
    row-level isolation automatically.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Session-authenticated requests (e.g. Django admin) resolve the tenant
        # here. JWT-authenticated API calls resolve it later, inside DRF auth.
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            set_current_context(user)
        return None

    def process_response(self, request, response):
        # Clean up so nothing leaks across requests/threads.
        _local.tenant = None
        _local.user = None
        return response