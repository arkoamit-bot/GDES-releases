from django.urls import path

from . import views

app_name = "clinic"

urlpatterns = [
    # Patient-centric workflow
    path("patients/", views.patients_list, name="patients"),
    path("patients/quicksearch/", views.quicksearch, name="quicksearch"),
    path("patients/dup-check/", views.patient_dupcheck, name="patient_dupcheck"),
    path("patients/add/", views.patient_create, name="patient_create"),
    path("patients/<int:pk>/", views.patient_detail, name="patient_detail"),
    path("patients/<int:pk>/edit/", views.patient_edit, name="patient_edit"),
    path("patients/<int:pk>/delete/", views.patient_delete, name="patient_delete"),
    path("patients/<int:pk>/baseline/", views.baseline_edit, name="baseline"),
    path("patients/<int:pk>/followup/", views.followup_create, name="followup"),
    path("patients/<int:pk>/prescription/", views.prescription_create, name="prescription"),
    path("patients/<int:pk>/adverse-event/", views.adverse_event_create,
         name="adverse_event"),
    path("patients/<int:pk>/register/", views.patient_register, name="register"),
    path("patients/<int:pk>/relapse/", views.relapse_create, name="relapse"),
    path("patients/<int:pk>/admission/", views.admission_create, name="admission"),
    path("patients/<int:pk>/biopsy/", views.biopsy_create, name="biopsy"),
    path("patients/<int:pk>/enroll/", views.study_enroll, name="study_enroll"),
    path("patients/<int:pk>/consent/", views.consent_manage, name="consent"),
    path("patients/<int:pk>/treatment/", views.treatment_add, name="treatment"),
    path("patients/<int:pk>/lab-order/", views.lab_order_create, name="lab_order"),
    path("patients/<int:pk>/lab-results/", views.lab_results_entry, name="lab_results"),
    path("patients/<int:pk>/outcome/recompute/", views.outcome_recompute,
         name="outcome_recompute"),
    # Section landing pages
    path("clinic/worklist/", views.worklist_page, name="worklist"),
    path("clinic/quality/", views.quality_page, name="quality"),
    path("clinic/prescriptions/", views.prescriptions_list, name="prescriptions"),
    path("clinic/analytics/", views.analytics_page, name="analytics"),
    path("clinic/studies/", views.studies_page, name="studies"),
    path("clinic/safety/", views.safety_page, name="safety"),
    path("clinic/pathology/", views.pathology_page, name="pathology"),
    path("clinic/biomarkers/", views.biomarkers_page, name="biomarkers"),
    path("clinic/drugs/", views.drug_intelligence_page, name="drugs"),
    path("clinic/drugs/<str:drug_id>/", views.drug_intelligence_detail, name="drug_detail"),
    path("clinic/export/", views.export_page, name="export"),
    # In-app help / documentation
    path("clinic/help/", views.help_index, name="help"),
    path("clinic/help/user/", views.help_user, name="help_user"),
    path("clinic/help/admin/", views.help_admin, name="help_admin"),
    path("clinic/help/developer/", views.help_developer, name="help_developer"),
    # Advanced analytics HTML result pages
    path("clinic/analytics/cox/", views.cox_results, name="cox_results"),
    path("clinic/analytics/egfr-slope/", views.egfr_slope_results, name="egfr_slope_results"),
    path("clinic/analytics/cif/", views.cif_results, name="cif_results"),
]
