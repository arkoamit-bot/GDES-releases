from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DecisionViewSet, DecisionResultViewSet

router = DefaultRouter()
router.register("decisions", DecisionViewSet)
router.register("results", DecisionResultViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
