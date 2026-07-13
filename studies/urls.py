from django.urls import path

from . import views

app_name = "studies"

urlpatterns = [
    path("<slug:code>/dashboard/", views.dashboard, name="dashboard"),
]
