"""The reasoning and traceability panels show signal, not volume.

Two complaints from the clinic, both correct:

* the differential listed ten possibilities down to 1-2% for a patient whose
  biopsy had already established the diagnosis;
* traceability was a long list -- 44 rows for 8 distinct recommendations,
  because the generators run on every page render and each render wrote a new
  audit row.
"""
import pytest
from datetime import date

from django.utils import timezone

pytestmark = pytest.mark.django_db


def _patient(pid="BGD-SIG-1", **extra):
    from patients.models import Patient
    fields = dict(
        patient_id=pid, name="Sig", hospital_id=f"H-{pid}", phone="+1234567890",
        sex="F", cohort="GN", diabetes_status="none", primary_diagnosis="iga",
        current_phase="active", registration_status="active",
        registration_date=date.today(), enrollment_date=date.today(),
        created_at=timezone.now(), updated_at=timezone.now())
    fields.update(extra)
    return Patient.objects.create(**fields)


def _biopsy(patient, diagnosis="FSGS - primary"):
    from pathology.models import Biopsy, GNDiagnosis
    bx = Biopsy.objects.create(patient=patient, biopsy_date=date.today())
    if diagnosis:
        GNDiagnosis.objects.create(biopsy=bx, diagnosis=diagnosis)
    return bx


DIFFERENTIAL = [
    {"disease_id": "fsgs", "disease_name": "FSGS", "score": 9, "confidence": 21},
    {"disease_id": "mcd", "disease_name": "Minimal Change Disease", "score": 7, "confidence": 16},
    {"disease_id": "iga", "disease_name": "IgA Nephropathy", "score": 6, "confidence": 14},
    {"disease_id": "membranous", "disease_name": "Membranous", "score": 3, "confidence": 7},
    {"disease_id": "amyloidosis", "disease_name": "Amyloidosis", "score": 1, "confidence": 2},
    {"disease_id": "lightChain", "disease_name": "Light chain", "score": 1, "confidence": 2},
]


class TestDifferentialAfterBiopsy:
    def test_a_confirmed_diagnosis_replaces_the_ranking(self):
        from clinical_reasoning.services.differential import differential_for_display
        p = _patient("BGD-SIG-2")
        _biopsy(p)
        out = differential_for_display(p, DIFFERENTIAL)
        assert out["confirmed"] == "FSGS - primary"
        assert out["entries"] == []          # ranking suppressed, not deleted
        assert out["hidden_count"] == len(DIFFERENTIAL)
        assert "no longer clinically relevant" in out["note"]

    def test_a_biopsy_without_a_diagnosis_does_not_count_as_confirmed(self):
        from clinical_reasoning.services.differential import differential_for_display
        p = _patient("BGD-SIG-3")
        _biopsy(p, diagnosis=None)
        assert differential_for_display(p, DIFFERENTIAL)["confirmed"] == ""

    def test_level2_biopsy_diagnosis_is_honoured(self):
        # Biopsies recorded before the diagnosis was structured.
        from clinical_reasoning.services.differential import differential_for_display
        p = _patient("BGD-SIG-4", biopsy_diagnosis="Membranous nephropathy")
        _biopsy(p, diagnosis=None)
        assert differential_for_display(p, DIFFERENTIAL)["confirmed"] == "Membranous nephropathy"


class TestDifferentialBeforeBiopsy:
    def test_noise_below_the_floor_is_dropped(self):
        from clinical_reasoning.services.differential import differential_for_display
        out = differential_for_display(_patient("BGD-SIG-10"), DIFFERENTIAL)
        names = [d["disease_name"] for d in out["entries"]]
        assert "Amyloidosis" not in names and "Light chain" not in names
        assert out["hidden_count"] == 2
        assert "not shown" in out["note"]

    def test_real_candidates_are_kept_in_order(self):
        from clinical_reasoning.services.differential import differential_for_display
        out = differential_for_display(_patient("BGD-SIG-11"), DIFFERENTIAL)
        assert [d["disease_id"] for d in out["entries"]] == [
            "fsgs", "mcd", "iga", "membranous"]

    def test_the_list_is_capped(self):
        from clinical_reasoning.services.differential import (
            MAX_ENTRIES, differential_for_display)
        many = [{"disease_id": f"d{i}", "disease_name": f"D{i}", "confidence": 20}
                for i in range(12)]
        out = differential_for_display(_patient("BGD-SIG-12"), many)
        assert len(out["entries"]) == MAX_ENTRIES
        assert out["hidden_count"] == 12 - MAX_ENTRIES

    def test_empty_differential_is_safe(self):
        from clinical_reasoning.services.differential import differential_for_display
        out = differential_for_display(_patient("BGD-SIG-13"), None)
        assert out["entries"] == [] and out["confirmed"] == ""


class TestAuditTrailIsIdempotent:
    def _issue(self, patient, text="Start prednisolone 1 mg/kg"):
        from clinical_reasoning.services.audit import create_audit_record
        return create_audit_record(
            recommendation_type="management_plan", patient=patient,
            disease_id="fsgs", recommendation_text=text)

    def test_reissuing_the_same_recommendation_does_not_add_a_row(self):
        from knowledge.models import RecommendationAudit
        p = _patient("BGD-SIG-20")
        first = self._issue(p)
        for _ in range(5):                      # five page renders
            self._issue(p)
        # Registering a patient makes the engine write its own reasoning rows,
        # so scope to the recommendation under test.
        assert RecommendationAudit.objects.filter(
            patient=p, recommendation_type="management_plan").count() == 1
        assert self._issue(p).pk == first.pk

    def test_the_first_issue_date_is_the_one_kept(self):
        p = _patient("BGD-SIG-21")
        first = self._issue(p)
        again = self._issue(p)
        assert again.issued_at == first.issued_at

    def test_a_changed_recommendation_is_recorded_separately(self):
        from knowledge.models import RecommendationAudit
        p = _patient("BGD-SIG-22")
        self._issue(p, "Start prednisolone 1 mg/kg")
        self._issue(p, "Stop prednisolone, start tacrolimus")
        assert RecommendationAudit.objects.filter(
            patient=p, recommendation_type="management_plan").count() == 2

    def test_different_patients_do_not_share_a_record(self):
        from knowledge.models import RecommendationAudit
        self._issue(_patient("BGD-SIG-23"))
        self._issue(_patient("BGD-SIG-24"))
        assert RecommendationAudit.objects.filter(
            recommendation_type="management_plan").count() == 2


class TestDedupeCommand:
    def _row(self, patient, text="dup", **extra):
        from knowledge.models import RecommendationAudit
        import uuid
        fields = dict(
            recommendation_id=f"REC-{uuid.uuid4().hex[:10]}",
            recommendation_type="management_plan", patient=patient,
            disease_id="fsgs", recommendation_text=text,
            validation_date=date.today())
        fields.update(extra)
        return RecommendationAudit.objects.create(**fields)

    def test_duplicates_collapse_to_the_earliest(self):
        from django.core.management import call_command
        from knowledge.models import RecommendationAudit
        p = _patient("BGD-SIG-30")
        first = self._row(p)
        self._row(p); self._row(p)
        call_command("dedupe_recommendation_audit", "--apply")
        remaining = RecommendationAudit.objects.filter(
            patient=p, recommendation_type="management_plan")
        assert [r.pk for r in remaining] == [first.pk]

    def test_a_row_the_clinician_acted_on_is_never_deleted(self):
        from django.core.management import call_command
        from knowledge.models import RecommendationAudit
        p = _patient("BGD-SIG-31")
        self._row(p)
        overridden = self._row(p, approval_status="overridden",
                               override_reason="Patient declined steroids")
        call_command("dedupe_recommendation_audit", "--apply")
        assert RecommendationAudit.objects.filter(pk=overridden.pk).exists()

    def test_dry_run_deletes_nothing(self):
        from django.core.management import call_command
        from knowledge.models import RecommendationAudit
        p = _patient("BGD-SIG-32")
        self._row(p); self._row(p)
        call_command("dedupe_recommendation_audit")
        assert RecommendationAudit.objects.filter(
            patient=p, recommendation_type="management_plan").count() == 2


class TestDiseaseNamesAreReadable:
    def test_rule_data_name_is_used_when_no_disease_row_exists(self):
        # Seven active disease_ids have no Disease row; the raw camelCase id was
        # being shown to clinicians in the differential.
        import inspect
        from knowledge import services
        src = inspect.getsource(services)
        assert 'rule_data or {}).get("disease_name")' in src
