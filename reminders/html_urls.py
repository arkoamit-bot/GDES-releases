from django.urls import path

from . import views

urlpatterns = [
    path("reminders/log/", views.reminder_log, name="log"),
    path("reminders/log/<int:pk>/done/", views.reminder_done, name="done"),
    path("reminders/log/<int:pk>/cancel/", views.reminder_cancel, name="cancel"),
]
