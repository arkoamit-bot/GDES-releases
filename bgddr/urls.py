from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views
from . import admin_backup

# Splice the superuser Backup & Restore console into the admin URL map.
admin_backup.install()

urlpatterns = [
    # Branded landing dashboard: registry counts, due/overdue worklist, quick
    # links. (Previously this redirected straight to /admin/.)
    path("", views.dashboard, name="dashboard"),
    path("health/", views.health_check, name="health-check"),
    # Dashboard HTMX partials (live-refresh)
    path("dashboard/partials/overview-stats/", views.partial_overview_stats,
         name="dashboard-partial-overview-stats"),
    path("dashboard/partials/worklist/", views.partial_worklist,
         name="dashboard-partial-worklist"),
    path("dashboard/partials/enrollment-summary/", views.partial_enrollment_summary,
         name="dashboard-partial-enrollment-summary"),
    path("dashboard/partials/cohort-breakdown/", views.partial_cohort_breakdown,
         name="dashboard-partial-cohort-breakdown"),
    path("dashboard/partials/enrollment-trend/", views.partial_enrollment_trend,
         name="dashboard-partial-enrollment-trend"),
    path("dashboard/partials/demographics/", views.partial_demographics,
         name="dashboard-partial-demographics"),
    path("dashboard/partials/outcomes-summary/", views.partial_outcomes_summary,
         name="dashboard-partial-outcomes-summary"),
    path("dashboard/partials/compliance/", views.partial_compliance,
         name="dashboard-partial-compliance"),
    # Dashboard pages (Phase 3.3)
    path("dashboard/enrollment/", views.dashboard_enrollment,
         name="dashboard-enrollment"),
    path("dashboard/outcomes/", views.dashboard_outcomes,
         name="dashboard-outcomes"),
    path("dashboard/compliance/", views.dashboard_compliance,
         name="dashboard-compliance"),
    # Guided clinical-workflow UI (patients hub, baseline, follow-up, etc.)
    path("", include("clinic.urls")),
    path("", include("users.urls")),
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
    path("prescriptions/", include("prescriptions.urls")),
    path("analytics/", include("analytics.urls")),
    path("studies/", include("studies.urls")),
    path("safety/", include("safety.urls")),
    path("scheduling/", include("scheduling.urls")),
    path("api/v1/", include("reminders.urls")),
    path("pathology/", include("pathology.urls")),
    path("biomarkers/", include("biomarkers.urls")),
    path("exports/", include("exports.urls")),
    # GDES clinical decision support
    path("api/v1/", include("clinical.urls")),
    path("api/v1/", include("knowledge.urls")),
    # DEPRECATED: Legacy 9-disease engine — retained for backward compat only.
    # Use /api/v1/clinical_reasoning/profiles/reason/ instead (18-disease KB engine).
    # path("api/v1/", include("decision.urls")),
    path("api/v1/", include("timeline.urls")),
    # Clinical Intelligence & Explainable Decision Platform (Phase 5)
    path("api/v1/", include("clinical_reasoning.urls")),
    # Follow-up Engine (Phase 5.1)
    path("api/v1/", include("followup.urls")),
    # Drug intelligence (Phase 3.2)
    path("api/v1/", include("treatments.urls")),
    # FHIR R4 interoperability (Phase 3.3)
    path("fhir/", include("fhir.urls")),
]

# Serve media files in development (Django dev server only).
# In production, the reverse proxy / Whitenoise handles static; media needs
# a dedicated route or the web server (nginx / S3 / etc.).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Also add static fallback for development (already handled by runserver,
    # but this makes collectstatic-less dev work for simple pages).
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
