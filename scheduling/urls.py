from django.urls import path

from . import views

app_name = "scheduling"

urlpatterns = [
    path("due/", views.due, name="due"),
    path("overdue/", views.overdue, name="overdue"),
    path("roster/", views.roster, name="roster"),
    path("monitoring/<str:patient_id>/", views.monitoring, name="monitoring"),
]
