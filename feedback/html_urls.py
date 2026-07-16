from django.urls import path
from . import views

urlpatterns = [
    path("feedback/", views.feedback_dashboard, name="feedback_dashboard"),
    path("feedback/report/", views.report_problem, name="report_problem"),
    path("feedback/conflicts/", views.conflict_list, name="conflict_list"),
    path("feedback/conflicts/<int:pk>/resolve/", views.resolve_conflict, name="resolve_conflict"),
    path("feedback/workflow/", views.workflow_feedback_page, name="workflow_feedback"),
    path("feedback/improvements/", views.improvement_suggestions, name="improvement_suggestions"),
    path("feedback/summary/", views.summary_report_view, name="summary_report"),
]
