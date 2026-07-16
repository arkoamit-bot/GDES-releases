from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("errors", views.ErrorLogViewSet)
router.register("crashes", views.CrashReportViewSet)
router.register("conflicts", views.ClinicalConflictViewSet)
router.register("knowledge-conflicts", views.KnowledgeConflictViewSet)
router.register("ai-failures", views.AIFailureLogViewSet)
router.register("rule-failures", views.RuleFailureLogViewSet)
router.register("feedback", views.UserFeedbackViewSet)
router.register("workflow-feedback", views.WorkflowFeedbackViewSet)
router.register("performance", views.PerformanceLogViewSet)
router.register("improvements", views.KnowledgeImprovementSuggestionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("report-conflict/", views.report_clinical_conflict, name="report-clinical-conflict"),
    path("report-knowledge-conflict/", views.report_knowledge_conflict, name="report-knowledge-conflict"),
    path("log-ai-failure/", views.log_ai_failure, name="log-ai-failure"),
    path("log-rule-failure/", views.log_rule_failure, name="log-rule-failure"),
    path("generate-suggestions/", views.generate_suggestions, name="generate-suggestions"),
    path("export-package/", views.export_package, name="export-package"),
    path("submit-workflow-feedback/", views.submit_workflow_feedback, name="submit-workflow-feedback"),
    path("summary-report/", views.summary_report, name="summary-report"),
]
