from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("profiles", views.ClinicalProfileViewSet)
router.register("insights", views.ClinicalInsightViewSet)

app_name = "clinical_reasoning"
urlpatterns = router.urls
