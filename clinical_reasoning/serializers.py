from rest_framework import serializers
from knowledge.models import RecommendationAudit
from .models import ClinicalProfile, ClinicalInsight


class ClinicalProfileSerializer(serializers.ModelSerializer):
    patient_id_display = serializers.CharField(source="patient.patient_id", read_only=True)
    patient_name = serializers.CharField(source="patient.name", read_only=True)

    class Meta:
        model = ClinicalProfile
        fields = "__all__"
        read_only_fields = ["last_updated", "version"]


class ClinicalInsightSerializer(serializers.ModelSerializer):
    patient_id_display = serializers.CharField(source="patient.patient_id", read_only=True)

    class Meta:
        model = ClinicalInsight
        fields = "__all__"
        read_only_fields = ["created_at"]


class ReasoningRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK to reason about")
    force = serializers.BooleanField(default=False, help_text="Force recomputation")


class RecommendationAuditSerializer(serializers.ModelSerializer):
    patient_id_display = serializers.CharField(source="patient.patient_id", read_only=True)
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    clinician_name = serializers.CharField(source="clinician.get_full_name", read_only=True, default="")

    class Meta:
        model = RecommendationAudit
        fields = [
            "recommendation_id", "recommendation_type", "patient", "patient_id_display",
            "patient_name", "clinician", "clinician_name", "disease_id",
            "recommendation_text", "clinical_rationale", "guideline",
            "guideline_version", "guideline_section", "evidence_grade",
            "confidence_score", "kb_rule_id", "kb_version",
            "approval_status", "override_allowed", "override_reason",
            "explanation", "issued_at", "reviewed_at",
        ]
        read_only_fields = [
            "recommendation_id", "issued_at", "reviewed_at",
        ]


class ReviewRecommendationSerializer(serializers.Serializer):
    approval_status = serializers.ChoiceField(
        choices=["approved", "rejected", "overridden"],
        help_text="Clinician decision on this recommendation",
    )
    override_reason = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Reason for rejection/override (required if rejected)",
    )

    def validate(self, data):
        if data["approval_status"] in ("rejected", "overridden") and not data.get("override_reason"):
            raise serializers.ValidationError(
                "override_reason is required when rejecting or overriding a recommendation"
            )
        return data


class ExplainabilityRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")


class ManagementPlanRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")
    disease_id = serializers.CharField(max_length=50, help_text="Disease ID (e.g. 'iga', 'membranous')")
    risk_category = serializers.ChoiceField(
        choices=["low", "moderate", "high", "very_high"],
        default="moderate",
    )
    features = serializers.DictField(required=False, help_text="Optional pre-extracted features")


class MonitoringPlanRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")
    disease_id = serializers.CharField(max_length=50, help_text="Disease ID")
    active_treatments = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Active treatment class keys",
    )
    ckd_stage = serializers.IntegerField(required=False, min_value=1, max_value=5, default=None)
    risk_category = serializers.ChoiceField(
        choices=["low", "moderate", "high", "very_high"],
        default="moderate",
    )


class FollowUpScheduleRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")
    risk_category = serializers.ChoiceField(
        choices=["low", "moderate", "high", "very_high"],
        default="moderate",
    )
    disease_phase = serializers.ChoiceField(
        choices=["active", "relapse", "remission", "ckd"],
        default="active",
    )
    treatment_phase = serializers.ChoiceField(
        choices=["induction", "maintenance", "remission"],
        default="induction",
    )
    disease_id = serializers.CharField(max_length=50, required=False, default=None)
    num_visits = serializers.IntegerField(default=6, min_value=1, max_value=24)


class PatientRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")


class InvestigationRecommendationRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")
    features = serializers.DictField(required=False, help_text="Optional pre-extracted features")


class DiseaseValidationRequestSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(help_text="Patient PK")
    disease = serializers.CharField(max_length=50, help_text="Disease code (e.g. 'iga', 'lupus')")
