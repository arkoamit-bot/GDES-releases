from django.urls import path

from . import views

app_name = "safety"

urlpatterns = [
    path("summary/", views.summary, name="summary"),
    path("infection-incidence/", views.infection_incidence_view, name="infection_incidence"),
    path("study/<slug:code>/", views.study_safety_view, name="study_safety"),
]
