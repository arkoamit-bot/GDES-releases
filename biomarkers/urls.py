from django.urls import path

from . import views

app_name = "biomarkers"

urlpatterns = [
    path("patient/<str:patient_id>/", views.patient_biomarkers, name="patient"),
    path("pla2r-predictor/", views.pla2r_predictor, name="pla2r_predictor"),
]
