"""
Site-scoped RBAC permissions and queryset filtering for multi-center operation.

Site coordinators see only their site's patients. data_manager role sees all.
"""

from rest_framework.permissions import BasePermission


def user_sites(request):
    """Return list of site IDs the user has access to."""
    if not request.user or not request.user.is_authenticated:
        return []
    if request.user.is_superuser:
        return None  # None = all sites
    from patients.models import UserSiteRole
    roles = UserSiteRole.objects.filter(user=request.user)
    if not roles.exists():
        return []
    return list(roles.values_list("site_id", flat=True))


def site_filter_kwargs(request, model=None):
    """Build filter kwargs for site-scoped querysets.

    Returns an empty dict if user can see all sites (superuser or data_manager).
    """
    from django.conf import settings
    mgr_group = None
    try:
        from django.contrib.auth.models import Group
        mgr_group = Group.objects.get(name="data_manager")
    except Exception:
        pass

    is_mgr = mgr_group and mgr_group in request.user.groups.all()

    if request.user.is_superuser or is_mgr:
        return {}

    sites = user_sites(request)
    if sites is None:
        return {}
    if not sites:
        return {}

    site_field = "site_id"
    if model:
        for f in model._meta.get_fields():
            if hasattr(f, "name") and f.name == "site":
                site_field = "site_id"
                break
            if hasattr(f, "related_model") and f.related_model and f.related_model.__name__ == "Patient":
                site_field = "patient__site_id"
                break

    return {site_field + "__in": sites}


class IsSiteScoped(BasePermission):
    """Permission check: user must belong to at least one site, or be superuser."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        from patients.models import UserSiteRole
        return UserSiteRole.objects.filter(user=request.user).exists()
