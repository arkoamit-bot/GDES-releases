"""
Registry API viewsets.

Reads are open to any authenticated user; writes are gated per-model by the
user's role (Group permissions) through DjangoModelPermissions (configured
globally). Computed/derived resources are read-only.
"""
from rest_framework import viewsets

from .base import AuditedModelViewSet
from .permissions import site_filter_kwargs

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

from . import serializers as s


class SiteViewSet(AuditedModelViewSet):
    queryset = Site.objects.all()
    serializer_class = s.SiteSerializer
    search_fields = ["code", "name"]


class UserSiteRoleViewSet(AuditedModelViewSet):
    queryset = UserSiteRole.objects.select_related("user", "site").all()
    serializer_class = s.UserSiteRoleSerializer
    filterset_fields = ["user", "site", "role"]


class PatientViewSet(AuditedModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = s.PatientSerializer
    search_fields = ["patient_id", "name", "hospital_id"]

    def get_queryset(self):
        qs = super().get_queryset()
        kwargs = site_filter_kwargs(self.request, Patient)
        if kwargs:
            qs = qs.filter(**kwargs)
        return qs


class ClinicalEncounterViewSet(AuditedModelViewSet):
    queryset = ClinicalEncounter.objects.all()
    serializer_class = s.ClinicalEncounterSerializer


class ClinicalEventViewSet(AuditedModelViewSet):
    queryset = ClinicalEvent.objects.all()
    serializer_class = s.ClinicalEventSerializer


class LabResultViewSet(AuditedModelViewSet):
    queryset = LabResult.objects.select_related("test").all()
    serializer_class = s.LabResultSerializer


class TreatmentExposureViewSet(AuditedModelViewSet):
    queryset = TreatmentExposure.objects.all()
    serializer_class = s.TreatmentExposureSerializer


class BiopsyViewSet(AuditedModelViewSet):
    queryset = Biopsy.objects.all()
    serializer_class = s.BiopsySerializer


class PathologyReviewViewSet(AuditedModelViewSet):
    queryset = PathologyReview.objects.all()
    serializer_class = s.PathologyReviewSerializer


class AdverseEventViewSet(AuditedModelViewSet):
    queryset = AdverseEvent.objects.all()
    serializer_class = s.AdverseEventSerializer


class ScheduledVisitViewSet(AuditedModelViewSet):
    queryset = ScheduledVisit.objects.all()
    serializer_class = s.ScheduledVisitSerializer


# --- Read-only (computed / derived) ----------------------------------------
class PrescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = s.PrescriptionSerializer


class PatientOutcomeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PatientOutcome.objects.all()
    serializer_class = s.PatientOutcomeSerializer


class BiomarkerKineticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BiomarkerKinetics.objects.all()
    serializer_class = s.BiomarkerKineticsSerializer


class DrugMasterViewSet(AuditedModelViewSet):
    queryset = DrugMaster.objects.all()
    serializer_class = s.DrugMasterSerializer
