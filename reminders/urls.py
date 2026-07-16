from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("reminders", views.ReminderScheduleViewSet)
router.register("reminder-templates", views.ReminderTemplateViewSet)
router.register("comm-preferences", views.PatientCommunicationPreferenceViewSet)

urlpatterns = [
    path("reminders/send/", views.send_custom_reminder, name="send-custom-reminder"),
    path("reminders/schedule/", views.schedule_reminders, name="schedule-reminders"),
    path("", include(router.urls)),
]
