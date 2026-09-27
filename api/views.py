"""
Registry API viewsets.

Reads are open to any authenticated user; writes are gated per-model by the
user's role (Group permissions) through DjangoModelPermissions (configured
globally). Computed/derived resources are read-only.
"""
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from .base import AuditedModelViewSet
from .permissions import IsSiteScoped, site_filter_kwargs

from analytics.models import PatientOutcome
from biomarkers.models import BiomarkerKinetics
from encounters.models import ClinicalEncounter, ClinicalEvent
from labs.models import LabResult
from pathology.models import Biopsy, PathologyReport, PathologyReview
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
    # An account with no site assignment is rejected rather than silently served
    # an empty list. No-op for superuser/data_manager and single-site registries.
    permission_classes = [IsSiteScoped, DjangoModelPermissions]

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
    """Current observations. Create/update go through the recording service;
    an update supersedes (see LabResultSerializer). Measured history is never
    deleted over the API -- correct the result instead."""
    queryset = LabResult.objects.select_related("test").all()
    serializer_class = s.LabResultSerializer

    def destroy(self, request, *args, **kwargs):
        from rest_framework import status
        from rest_framework.response import Response
        return Response(
            {"detail": "Lab results are not deleted; PUT/PATCH with a "
                       "correction_reason to supersede one."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TreatmentExposureViewSet(AuditedModelViewSet):
    queryset = TreatmentExposure.objects.all()
    serializer_class = s.TreatmentExposureSerializer


class BiopsyViewSet(AuditedModelViewSet):
    queryset = Biopsy.objects.all()
    serializer_class = s.BiopsySerializer


class PathologyReportViewSet(AuditedModelViewSet):
    """Report revisions with their findings. Create = new report or an
    amendment (through pathology.services.report); no in-place edit, no delete."""
    queryset = PathologyReport.objects.select_related("biopsy").prefetch_related("findings")
    serializer_class = s.PathologyReportSerializer
    filterset_fields = ["biopsy", "role", "is_current"]
    http_method_names = ["get", "post", "head", "options"]


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
