"""
DRF authentication that also establishes the tenant context.

Django middleware's process_view runs *before* DRF authenticates the JWT, so a
JWT-authenticated request would otherwise never set the thread-local tenant and
tenant isolation would silently no-op. This subclass authenticates the token and
then sets the tenant context, so every downstream query in the view (including
TenantManager filtering) is scoped to the right school.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication

from .middleware import set_current_context


class TenantJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, _token = result
            set_current_context(user)
        return result

    def authenticate_header(self, request):
        # simplejwt's default asks the client to use Bearer.
        return super().authenticate_header(request)
