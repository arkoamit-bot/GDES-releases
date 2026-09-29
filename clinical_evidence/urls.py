from django.urls import path

from . import views

app_name = "clinical_evidence"

urlpatterns = [
    path("evidence/search/", views.search_evidence, name="search"),
    path("evidence/queries/<str:query_id>/", views.query_detail, name="query-detail"),
    path("evidence/packages/<str:package_id>/", views.package_detail, name="package-detail"),
    path("evidence/validations/", views.validation_list, name="validation-list"),
    path("evidence/conflicts/", views.conflicts_list, name="conflicts-list"),
    path("evidence/alerts/", views.alerts_list, name="alerts-list"),
    path("evidence/analytics/", views.analytics_dashboard, name="analytics"),
    path("evidence/analytics/compute/", views.compute_analytics, name="compute-analytics"),
    path("evidence/providers/", views.provider_status, name="provider-status"),
    path("evidence/summaries/", views.summaries_list, name="summaries-list"),
    path("evidence/knowledge-gaps/", views.knowledge_gaps, name="knowledge-gaps"),
    path("evidence/guidelines/", views.guidelines_list, name="guidelines-list"),
]
