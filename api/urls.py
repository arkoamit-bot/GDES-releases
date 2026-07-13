from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from django.urls import path

from . import views

router = DefaultRouter()
router.register("sites", views.SiteViewSet)
router.register("user-site-roles", views.UserSiteRoleViewSet)
router.register("patients", views.PatientViewSet)
router.register("encounters", views.ClinicalEncounterViewSet)
router.register("events", views.ClinicalEventViewSet)
router.register("lab-results", views.LabResultViewSet)
router.register("treatment-exposures", views.TreatmentExposureViewSet)
router.register("biopsies", views.BiopsyViewSet)
router.register("pathology-reviews", views.PathologyReviewViewSet)
router.register("adverse-events", views.AdverseEventViewSet)
router.register("scheduled-visits", views.ScheduledVisitViewSet)
router.register("prescriptions", views.PrescriptionViewSet)
router.register("outcomes", views.PatientOutcomeViewSet)
router.register("biomarkers", views.BiomarkerKineticsViewSet)
router.register("drugs", views.DrugMasterViewSet)

app_name = "api"
urlpatterns = [
    path("auth/token/", obtain_auth_token, name="token"),
    *router.urls,
]
