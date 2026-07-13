from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit"

    def ready(self):
        from django.apps import apps

        from .recording import register

        # Models whose edits we want a defensible trail for. (Append-only or
        # purely-computed tables — LabResult, PatientOutcome — are intentionally
        # not audited; their provenance lives in the rows themselves.)
        register(apps.get_model("patients", "Patient"), exclude=["latest_egfr"])
        register(apps.get_model("encounters", "ClinicalEncounter"))
        register(apps.get_model("encounters", "ClinicalEvent"))
        register(apps.get_model("baseline", "BaselineAssessment"))
        register(apps.get_model("pathology", "Biopsy"))
        register(apps.get_model("pathology", "GNDiagnosis"))
        register(apps.get_model("pathology", "IgANScore"))
        register(apps.get_model("pathology", "LupusPathology"))
        register(apps.get_model("pathology", "FSGSPathology"))
        register(apps.get_model("pathology", "MembranousPathology"))
        register(apps.get_model("pathology", "PathologyReview"))
        register(apps.get_model("prescriptions", "Prescription"))
        register(apps.get_model("prescriptions", "PrescriptionItem"))
        register(apps.get_model("treatments", "TreatmentExposure"))
        # biobank disabled (protocol v2 removed biobanking) — Sample not audited.
        register(apps.get_model("audit", "Consent"))
        register(apps.get_model("studies", "StudyEnrollment"))
        register(apps.get_model("safety", "AdverseEvent"))
        register(apps.get_model("scheduling", "ScheduledVisit"))
