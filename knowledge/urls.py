"""URL configuration for the knowledge app."""
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("guideline-sources", views.GuidelineSourceViewSet)
router.register("knowledge-base", views.KnowledgeBaseEntryViewSet)
router.register("rule-templates", views.RuleTemplateViewSet)
router.register("rule-reviews", views.RuleReviewViewSet)
router.register("rule-test-results", views.RuleTestResultViewSet)
router.register("guideline-documents", views.GuidelineDocumentViewSet)
router.register("evidence-entries", views.EvidenceEntryViewSet)
router.register("diseases", views.DiseaseViewSet)
router.register("clinical-cases", views.ClinicalCaseViewSet)
router.register("clinical-pathways", views.ClinicalPathwayViewSet)
router.register("syndromes", views.SyndromeViewSet)
router.register("pathology-entities", views.PathologyEntityViewSet)
router.register("lab-entities", views.LabEntityViewSet)
router.register("drug-intelligence", views.DrugIntelligenceViewSet)
router.register("monitoring-protocols", views.MonitoringProtocolViewSet)
router.register("complications", views.ComplicationViewSet)
router.register("graph-nodes", views.KnowledgeGraphNodeViewSet)
router.register("graph-edges", views.KnowledgeGraphEdgeViewSet)
router.register("graph-reasoning", views.GraphReasoningViewSet, basename="graph-reasoning")

app_name = "knowledge"
urlpatterns = router.urls
