"""Attribute audited changes during a web request to request.user."""
from .local import clear_actor, set_actor


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        set_actor(user if (user and user.is_authenticated) else None,
                  reason=request.META.get("HTTP_X_CHANGE_REASON", ""))
        try:
            return self.get_response(request)
        finally:
            clear_actor()
