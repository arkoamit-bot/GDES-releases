from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("patient/<str:patient_id>/outcome/", views.patient_outcome, name="patient_outcome"),
    path("cohort/survival/", views.cohort_survival_view, name="cohort_survival"),
    path("cohort/survival/plot/", views.cohort_survival_plot, name="cohort_survival_plot"),
    path("cohort/cox/", views.cohort_cox_view, name="cohort_cox"),
    path("cohort/egfr-slope/", views.cohort_egfr_slope_view, name="cohort_egfr_slope"),
    path("cohort/cif/", views.cohort_cif_view, name="cohort_cif"),
    path("cohort/summary/", views.cohort_summary_view, name="cohort_summary"),
]
