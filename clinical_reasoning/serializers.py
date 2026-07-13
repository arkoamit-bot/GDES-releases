from rest_framework import serializers
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
