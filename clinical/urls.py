"""URL configuration for the clinical app."""
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("clinical-assessments", views.ClinicalAssessmentViewSet)
router.register("vital-signs", views.VitalSignViewSet)

app_name = "clinical"
urlpatterns = router.urls
