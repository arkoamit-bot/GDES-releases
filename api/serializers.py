"""DRF serializers for the registry API."""
from rest_framework import serializers

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
    # `site` is nullable for backward compatibility, and a null FK would raise
    # AttributeError on the `site.code` traversal, turning one site-less patient
    # into an HTTP 500 for the entire list endpoint. allow_null keeps the field
    # serialisable as None instead.
    site_code = serializers.CharField(
        source="site.code", read_only=True, allow_null=True, default=None)

    class Meta:
        model = Patient
        fields = ["id", "patient_id", "hospital_id", "name", "phone", "sex",
                  "dob", "enrollment_date", "cohort", "diabetes_status",
                  "primary_diagnosis", "latest_egfr", "site", "site_code",
                  "created_at", "updated_at"]
        read_only_fields = ["latest_egfr", "created_at", "updated_at"]


class ClinicalEncounterSerializer(serializers.ModelSerializer):
    """systolic_bp / diastolic_bp / weight_kg are the projection of the
    visit's selected VitalSign. Values written here are recorded as a new
    reading (and selected) through encounters.services.vitals, so the visit,
    its printout and clinical reasoning keep reading one measurement."""
    _VITALS = ("systolic_bp", "diastolic_bp", "weight_kg")

    class Meta:
        model = ClinicalEncounter
        fields = "__all__"
        read_only_fields = ["selected_vital"]

    def _pop_vitals(self, validated_data):
        return {k: validated_data.pop(k) for k in self._VITALS if k in validated_data}

    def _record(self, encounter, vitals):
        from encounters.services.vitals import record_visit_vitals
        if not vitals or all(vitals.get(k) == getattr(encounter, k) for k in vitals):
            return
        merged = {k: vitals.get(k, getattr(encounter, k)) for k in self._VITALS}
        record_visit_vitals(encounter, systolic=merged["systolic_bp"],
                            diastolic=merged["diastolic_bp"],
                            weight_kg=merged["weight_kg"], source="api")

    def create(self, validated_data):
        vitals = self._pop_vitals(validated_data)
        encounter = super().create(validated_data)
        self._record(encounter, vitals)
        encounter.refresh_from_db()
        return encounter

    def update(self, instance, validated_data):
        vitals = self._pop_vitals(validated_data)
        encounter = super().update(instance, validated_data)
        self._record(encounter, vitals)
        encounter.refresh_from_db()
        return encounter


class ClinicalEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalEvent
        fields = "__all__"


class LabResultSerializer(serializers.ModelSerializer):
    """Writes go through labs.services.results -- the same command the guided
    pages use -- so creatinine derives a versioned eGFR and refreshes the
    patient cache, units are normalised, and an update is a correction that
    supersedes the original (with a reason) instead of overwriting it."""
    test_code = serializers.CharField(source="test.code", read_only=True)
    correction_reason = serializers.CharField(
        required=False, allow_blank=True, max_length=240,
        help_text="Required when updating: why the result is corrected.")

    class Meta:
        model = LabResult
        fields = ["id", "patient", "test", "test_code", "value_numeric",
                  "value_text", "unit", "sample_date", "result_date", "flag",
                  "source", "formula_version", "derived_from", "supersedes",
                  "is_current", "correction_reason", "idempotency_key",
                  "source_report_id", "specimen_id", "entry_path"]
        read_only_fields = ["flag", "formula_version", "derived_from",
                            "supersedes", "is_current", "entry_path"]
        # The idempotency constraint is enforced by the service, which
        # returns the existing row for a retried key instead of a 400.
        validators = []

    def _user(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        return user if getattr(user, "is_authenticated", False) else None

    def _record(self, fn, **kwargs):
        from django.core.exceptions import ValidationError as DjangoValidationError
        try:
            return fn(**kwargs)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    def create(self, validated_data):
        from labs.services.results import record_result
        validated_data.pop("correction_reason", None)
        source = validated_data.get("source") or LabResult.Source.LAB
        if source == LabResult.Source.DERIVED:
            raise serializers.ValidationError(
                {"source": "Derived results are computed, not entered."})
        return self._record(
            record_result, patient=validated_data["patient"],
            test_code=validated_data["test"],
            result_date=validated_data["result_date"],
            value_numeric=validated_data.get("value_numeric"),
            value_text=validated_data.get("value_text", ""),
            unit=validated_data.get("unit", ""),
            sample_date=validated_data.get("sample_date"),
            source=source, entry_path=LabResult.EntryPath.API,
            entered_by=self._user(),
            idempotency_key=validated_data.get("idempotency_key", ""),
            source_report_id=validated_data.get("source_report_id", ""),
            specimen_id=validated_data.get("specimen_id", ""))

    def update(self, instance, validated_data):
        from labs.services.results import correct_result
        if (validated_data.get("patient", instance.patient) != instance.patient
                or validated_data.get("test", instance.test) != instance.test):
            raise serializers.ValidationError(
                "A result cannot be moved to another patient or test; record a new one.")
        return self._record(
            correct_result, result=instance,
            reason=validated_data.get("correction_reason", ""),
            value_numeric=validated_data.get("value_numeric", instance.value_numeric),
            value_text=validated_data.get("value_text"),
            unit=validated_data.get("unit"),
            result_date=validated_data.get("result_date"),
            sample_date=validated_data.get("sample_date", instance.sample_date),
            entered_by=self._user(), entry_path=LabResult.EntryPath.API)


class TreatmentExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentExposure
        fields = "__all__"


class BiopsySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biopsy
        fields = "__all__"
        read_only_fields = ["review_status"]

    def validate(self, attrs):
        """The same cross-field rules as the biopsy form (pathology.consistency),
        against the stored diagnosis and current report when they exist."""
        from pathology.consistency import crescent_errors, result_category_errors
        from pathology.services.report import current_report
        inst = self.instance

        def value(name):
            return attrs[name] if name in attrs else getattr(inst, name, None)

        report = current_report(inst) if inst else None
        dx = getattr(getattr(inst, "diagnosis", None), "diagnosis", "") if inst else ""
        problems = (
            crescent_errors(value("crescents_present"), value("crescent_pct"),
                            count=getattr(report, "crescentic_glomeruli", None))
            + result_category_errors(value("result_category") or "", dx,
                                     value("adequacy") or "",
                                     report_status=getattr(report, "status", "")))
        errors = {}
        for _target, field, msg in problems:
            errors.setdefault(field if field in self.fields else "non_field_errors", []).append(msg)
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class PathologyFindingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    section = serializers.CharField()
    code = serializers.CharField(required=False, allow_blank=True)
    other_label = serializers.CharField(required=False, allow_blank=True, max_length=120)
    presence = serializers.CharField(required=False, allow_blank=True)
    severity = serializers.CharField(required=False, allow_blank=True)
    extent = serializers.CharField(required=False, allow_blank=True)
    extent_pct = serializers.DecimalField(max_digits=5, decimal_places=1, required=False,
                                          allow_null=True, min_value=0, max_value=100)
    count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    denominator = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    site = serializers.CharField(required=False, allow_blank=True)
    marker = serializers.CharField(required=False, allow_blank=True)
    intensity = serializers.CharField(required=False, allow_blank=True)
    distribution = serializers.CharField(required=False, allow_blank=True)
    detail = serializers.CharField(required=False, allow_blank=True, max_length=240)
    origin = serializers.CharField(read_only=True)
    legacy_value = serializers.CharField(read_only=True)


class PathologyReportSerializer(serializers.ModelSerializer):
    """A report revision with its findings. Writes go through
    pathology.services.report (same validation as the guided form). POSTing a
    report for a read that already has one records an amendment; it needs a
    ``revision_reason``. Existing revisions are never edited in place."""
    findings = PathologyFindingSerializer(many=True, required=False)
    kind = serializers.ChoiceField(choices=["amendment", "addendum"], required=False,
                                   write_only=True, default="amendment")

    class Meta:
        model = PathologyReport
        fields = ["id", "biopsy", "role", "revision", "supersedes", "is_current",
                  "origin", "revision_reason", "status", "report_identifier",
                  "laboratory", "pathologist", "specimen_date", "report_date",
                  "context", "signed_by", "signed_at", "cortex_present",
                  "medulla_present", "cores", "glomeruli_if", "glomeruli_em",
                  "globally_sclerosed", "segmentally_sclerosed",
                  "crescentic_glomeruli", "limitations", "lm_status", "if_status",
                  "ihc_status", "em_status", "primary_diagnosis",
                  "additional_diagnoses", "comment", "original_report_text",
                  "scores", "panel_override_reason", "findings", "kind",
                  "created_at"]
        read_only_fields = ["revision", "supersedes", "is_current", "origin",
                            "scores", "created_at"]

    def create(self, validated_data):
        from pathology.services.report import (ReportInvalid, amend_report,
                                               current_report, save_report)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        user = user if getattr(user, "is_authenticated", False) else None
        findings = [dict(f) for f in validated_data.pop("findings", [])]
        kind = validated_data.pop("kind", "amendment")
        biopsy = validated_data.pop("biopsy")
        role = validated_data.pop("role", "local")
        reason = validated_data.pop("revision_reason", "")
        try:
            existing = current_report(biopsy, role)
            if existing is None:
                report, _w = save_report(biopsy, data=validated_data, findings=findings,
                                         role=role, user=user,
                                         origin=PathologyReport.Origin.API)
            else:
                report, _w = amend_report(existing, data=validated_data,
                                          findings=findings, reason=reason,
                                          user=user, kind=kind)
        except ReportInvalid as exc:
            raise serializers.ValidationError(exc.errors)
        return report

    def update(self, instance, validated_data):
        raise serializers.ValidationError(
            "Report revisions are not edited in place; POST an amendment "
            "with a revision_reason.")


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
