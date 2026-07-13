"""DRF serializers for the clinical app."""
from rest_framework import serializers

from .models import ClinicalAssessment, VitalSign


class ClinicalAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalAssessment
        fields = "__all__"


class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = "__all__"
