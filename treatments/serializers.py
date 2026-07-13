from rest_framework import serializers


class DrugInteractionCheckSerializer(serializers.Serializer):
    drugs = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=2,
        allow_empty=False,
        help_text="List of drug names or IDs to check",
    )
    patient_context = serializers.JSONField(required=False, default=dict,
                                            help_text="Optional clinical context (e.g. egfr, age)")


class DrugContraindicationCheckSerializer(serializers.Serializer):
    drug = serializers.CharField(max_length=100, help_text="Drug name or ID")
    patient_diseases = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True,
        help_text="List of patient's active disease/condition codes",
    )
    patient_context = serializers.JSONField(required=False, default=dict,
                                            help_text="Optional clinical context (e.g. egfr, age)")


class MultiDrugContraindicationCheckSerializer(serializers.Serializer):
    drugs = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        help_text="List of drug names or IDs",
    )
    patient_diseases = serializers.ListField(
        child=serializers.CharField(max_length=100),
        allow_empty=True,
        help_text="List of patient's active disease/condition codes",
    )
    patient_context = serializers.JSONField(required=False, default=dict)
