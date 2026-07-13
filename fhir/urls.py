from django.urls import path

from . import views

app_name = "fhir"

urlpatterns = [
    path("metadata", views.fhir_capabilities, name="fhir-capabilities"),
    path("Patient/<int:patient_id>", views.fhir_export_patient, name="fhir-export-patient"),
    path("Patient/", views.fhir_export_all, name="fhir-export-all"),
    path("import/", views.fhir_import, name="fhir-import"),
    # Bulk export
    path("export-all/", views.fhir_export_all, name="fhir-export-all-alt"),
]
