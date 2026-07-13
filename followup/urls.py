from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("followup-tasks", views.FollowUpTaskViewSet)
router.register("followup-plans", views.FollowUpPlanViewSet, basename="followup-plan")

app_name = "followup"
urlpatterns = router.urls
