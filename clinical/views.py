"""DRF viewsets for the clinical app."""
from api.base import AuditedModelViewSet

from .models import ClinicalAssessment, VitalSign
from . import serializers as s


class ClinicalAssessmentViewSet(AuditedModelViewSet):
    queryset = ClinicalAssessment.objects.select_related("encounter").all()
    serializer_class = s.ClinicalAssessmentSerializer


class VitalSignViewSet(AuditedModelViewSet):
    queryset = VitalSign.objects.select_related("encounter").all()
    serializer_class = s.VitalSignSerializer
