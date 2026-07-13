"""
Shared DRF viewset base classes.

AuditedModelViewSet sets the audit actor from the DRF-authenticated user, so API
writes land in the audit trail attributed to the right person (token auth happens
in DRF's layer, after the AuditMiddleware runs, so we set it again here).
"""
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from audit.local import set_actor


class AuditedModelViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user if request.user.is_authenticated else None
        set_actor(user, reason=request.META.get("HTTP_X_CHANGE_REASON", ""))
