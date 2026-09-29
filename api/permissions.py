"""
Site-scoped RBAC permissions and queryset filtering for multi-center operation.

Site coordinators see only their site's patients. data_manager role sees all.

Scoping is fail-CLOSED whenever it can matter. A user with no ``UserSiteRole``
row used to receive an unfiltered queryset, which meant a misconfigured (or
unassigned) account in a multi-center registry could read every site's patients.
They now match nothing instead. The single-site desktop pilot is unaffected:
with fewer than two ``Site`` rows there is nothing to leak, so the registry
stays unrestricted and a fresh install keeps working.
"""

from rest_framework.permissions import BasePermission


def _sees_all_sites(user):
    """True for superusers and the ``data_manager`` group (registry-wide role)."""
    if not (user and user.is_authenticated):
        return False
    if user.is_superuser:
        return True
    from django.contrib.auth.models import Group
    return Group.objects.filter(
        name="data_manager", user=user).exists()


def user_sites(request):
    """Return list of site IDs the user has access to, or None for all sites."""
    if not request.user or not request.user.is_authenticated:
        return []
    if _sees_all_sites(request.user):
        return None  # None = all sites
    from patients.models import UserSiteRole
    return list(
        UserSiteRole.objects.filter(user=request.user).values_list("site_id", flat=True))


def _is_single_site_registry():
    """True when there is only one site, so site scoping is a no-op."""
    from patients.models import Site
    return Site.objects.count() <= 1


def site_filter_kwargs(request, model=None):
    """Build filter kwargs for site-scoped querysets.

    Returns an empty dict when the user may see all sites (superuser,
    data_manager, or a single-site registry) or when the model has no site path.
    Otherwise returns a restrictive filter -- including a filter that matches no
    rows when the user has no site assignment.
    """
    if not request.user or not request.user.is_authenticated:
        return {"pk__in": []}
    if _sees_all_sites(request.user):
        return {}
    if _is_single_site_registry():
        return {}

    sites = user_sites(request)
    if not sites:
        # Fail closed: an unassigned account in a multi-center registry must not
        # inherit the whole registry.
        return {"pk__in": []}

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
    """Require registry-wide access or at least one site assignment.

    Kept consistent with :func:`site_filter_kwargs`: data_manager and
    superusers pass, everyone else needs a ``UserSiteRole`` row. An unassigned
    account is rejected outright rather than served a silently empty list.
    """

    message = "You are not assigned to any site. Ask a data manager for access."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if _sees_all_sites(request.user):
            return True
        if _is_single_site_registry():
            return True
        from patients.models import UserSiteRole
        return UserSiteRole.objects.filter(user=request.user).exists()
