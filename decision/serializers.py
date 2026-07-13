from rest_framework import serializers
from .models import DecisionRequest, DecisionResult


class DecisionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionRequest
        fields = ["id", "patient", "encounter", "input_snapshot", "created_at"]
        read_only_fields = ["id", "created_at"]


class DecisionResultSerializer(serializers.ModelSerializer):
    override_summary = serializers.SerializerMethodField()

    class Meta:
        model = DecisionResult
        fields = [
            "id", "request", "phenotype", "urgency_level", "urgency_tone",
            "urgency_reasons", "ranked_differential", "next_steps", "traceability",
            "explanation", "created_at",
            "override_reason", "alternative_diagnosis", "clinician_notes",
            "overridden_by", "override_at", "override_summary",
        ]

    def get_override_summary(self, obj):
        if not obj.override_reason:
            return {"overridden": False}
        return {
            "overridden": True,
            "reason": obj.override_reason,
            "alternative_diagnosis": obj.alternative_diagnosis,
            "clinician_notes": obj.clinician_notes,
            "overridden_by": obj.overridden_by_id,
            "override_at": obj.override_at.isoformat() if obj.override_at else None,
        }


class OverrideDecisionSerializer(serializers.Serializer):
    """Serializer for overriding a decision result."""
    override_reason = serializers.CharField(max_length=1000)
    alternative_diagnosis = serializers.CharField(max_length=200, required=False, default="")
    clinician_notes = serializers.CharField(required=False, default="")

    def validate_override_reason(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Override reason must be at least 5 characters.")
        return value


class CalculatorRequestSerializer(serializers.Serializer):
    """Generic calculator input."""
    calculator = serializers.ChoiceField(choices=[
        "egfr", "bsa", "upcr_to_utp", "utp_to_upcr", "proteinuria_category",
        "renal_dose", "kdigo_heatmap",
    ])


class EGFRCalculatorSerializer(serializers.Serializer):
    creatinine_mg_dl = serializers.FloatField(min_value=0.1, max_value=20.0)
    age = serializers.IntegerField(min_value=1, max_value=120)
    sex = serializers.ChoiceField(choices=["male", "female"])
    race = serializers.ChoiceField(choices=["white", "black", "other"], default="other")


class BSACalculatorSerializer(serializers.Serializer):
    height_cm = serializers.FloatField(min_value=30, max_value=250)
    weight_kg = serializers.FloatField(min_value=2, max_value=300)


class ProteinuriaConverterSerializer(serializers.Serializer):
    value = serializers.FloatField(min_value=0)
    direction = serializers.ChoiceField(choices=["upcr_to_utp", "utp_to_upcr"])
    weight_kg = serializers.FloatField(min_value=2, max_value=300)


class RenalDoseSerializer(serializers.Serializer):
    drug = serializers.CharField(max_length=100)
    egfr = serializers.FloatField(min_value=0, max_value=200)


class KDIGOHeatmapSerializer(serializers.Serializer):
    egfr = serializers.FloatField(min_value=0, max_value=200)
    upcr = serializers.FloatField(min_value=0, max_value=20)
