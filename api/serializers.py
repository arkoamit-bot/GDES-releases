"""DRF serializers for the registry API."""
from rest_framework import serializers

from analytics.models import PatientOutcome
from biomarkers.models import BiomarkerKinetics
from encounters.models import ClinicalEncounter, ClinicalEvent
from labs.models import LabResult
from pathology.models import Biopsy, PathologyReview
from patients.models import Patient, Site, UserSiteRole
from prescriptions.models import Prescription
from safety.models import AdverseEvent
from scheduling.models import ScheduledVisit
from treatments.models import DrugMaster, TreatmentExposure


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"


class UserSiteRoleSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    site_code = serializers.CharField(source="site.code", read_only=True)

    class Meta:
        model = UserSiteRole
        fields = "__all__"


class PatientSerializer(serializers.ModelSerializer):
    site_code = serializers.CharField(source="site.code", read_only=True)

    class Meta:
        model = Patient
        fields = ["id", "patient_id", "hospital_id", "name", "phone", "sex",
                  "dob", "enrollment_date", "cohort", "diabetes_status",
                  "primary_diagnosis", "latest_egfr", "site", "site_code",
                  "created_at", "updated_at"]
        read_only_fields = ["latest_egfr", "created_at", "updated_at"]


class ClinicalEncounterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalEncounter
        fields = "__all__"


class ClinicalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalEvent
        fields = "__all__"


class LabResultSerializer(serializers.ModelSerializer):
    test_code = serializers.CharField(source="test.code", read_only=True)

    class Meta:
        model = LabResult
        fields = ["id", "patient", "test", "test_code", "value_numeric",
                  "value_text", "unit", "sample_date", "result_date", "flag",
                  "source", "formula_version"]
        read_only_fields = ["flag", "formula_version"]


class TreatmentExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentExposure
        fields = "__all__"


class BiopsySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biopsy
        fields = "__all__"
        read_only_fields = ["review_status"]


class PathologyReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PathologyReview
        fields = "__all__"
        read_only_fields = ["is_final"]


class AdverseEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdverseEvent
        fields = "__all__"


class ScheduledVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledVisit
        fields = "__all__"


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["id", "encounter", "version", "status", "diagnosis_text",
                  "printed_at", "content_hash", "reconciled_at"]


class PatientOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientOutcome
        fields = "__all__"


class BiomarkerKineticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiomarkerKinetics
        fields = "__all__"


class DrugMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrugMaster
        fields = ["id", "generic_name", "brand_names", "drug_class", "is_active",
                  "default_route", "available_routes", "available_strengths",
                  "strengths_by_route", "default_frequency",
                  "renal_dose_adjust", "egfr_caution_below",
                  "nephrotoxic", "hepatic_dose_adjust", "dialysis_dose_adjust",
                  "pregnancy_category", "lactation_safety", "indications"]
        read_only_fields = ["is_active"]
