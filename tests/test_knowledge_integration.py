"""Integration tests — use the deterministic test knowledge fixture.

These tests verify the complete deterministic pipeline:
  Patient → Feature Extraction → Rule Matching → Differential Generation → Recommendation

Expected outputs are completely deterministic because the test knowledge base
is curated, small, independent, and version-controlled.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("django_db_setup")]


# ---------------------------------------------------------------------------
# Helper — build a minimal patient with clinical data for a given disease
# ---------------------------------------------------------------------------

def _make_patient(patient_id, diagnosis, egfr, labs, biopsy_gn=None,
                  encounter_type="baseline", phase="active", features_extra=None):
    from patients.models import Patient
    p = Patient.objects.create(
        patient_id=patient_id, name="IntTest", hospital_id=f"H-{patient_id}",
        phone="+1234567890", sex="F", cohort="GN", diabetes_status="no",
        primary_diagnosis=diagnosis, current_phase=phase,
        registration_status="active", registration_date=date.today(),
        enrollment_date=date.today(), latest_egfr=egfr,
        created_at=timezone.now(), updated_at=timezone.now(),
    )
    from encounters.models import ClinicalEncounter
    ClinicalEncounter.objects.create(
        patient=p, encounter_date=date.today(), encounter_type=encounter_type,
        disease_phase=phase, systolic_bp=120, diastolic_bp=80,
    )
    from labs.models import LabTest, LabResult
    for code, val in (labs or []):
        test, _ = LabTest.objects.get_or_create(
            code=code, defaults={"name": code, "value_type": "numeric"},
        )
        LabResult.objects.create(
            patient=p, test=test, value_numeric=val,
            result_date=date.today(),
        )
    if biopsy_gn:
        from pathology.models import Biopsy, GNDiagnosis
        b = Biopsy.objects.create(patient=p, biopsy_date=date.today(), adequacy="adequate")
        GNDiagnosis.objects.create(biopsy=b, diagnosis=biopsy_gn)
    return p


def _differential_scores(profile):
    """Return {disease_id: score} from a ClinicalProfile."""
    return {d["disease_id"]: d["score"] for d in (profile.differential or [])}


# ---------------------------------------------------------------------------
# IgAN — expect iga score >= 10 (matched rules for IgAN patient)
# ---------------------------------------------------------------------------

class TestIgAIntegration:
    def test_igan_differential(self):
        p = _make_patient("INT-IGA-001", "IgA nephropathy", Decimal("50"),
                          labs=[("upcr", Decimal("1.2"))], biopsy_gn="IgA nephropathy (IgAN)")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("iga", 0) >= 10, f"Expected IgAN score >= 10, got: {scores}"


class TestLupusIntegration:
    def test_lupus_differential(self):
        p = _make_patient("INT-LN-001", "Lupus nephritis", Decimal("55"),
                          labs=[("upcr", Decimal("3.0")), ("c3", Decimal("65"))],
                          biopsy_gn="Lupus nephritis")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("lupus", 0) >= 10, f"Expected Lupus score >= 10, got: {scores}"


class TestANCAIntegration:
    def test_anca_differential(self):
        p = _make_patient("INT-ANCA-001", "ANCA vasculitis", Decimal("25"),
                          labs=[("creatinine", Decimal("2.5")), ("anca", 1)],
                          biopsy_gn="ANCA vasculitis")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("anca", 0) >= 10, f"Expected ANCA score >= 10, got: {scores}"


class TestMembranousIntegration:
    def test_membranous_differential(self):
        p = _make_patient("INT-MN-001", "Membranous nephropathy", Decimal("70"),
                          labs=[("upcr", Decimal("5.0")), ("albumin", Decimal("2.1"))],
                          biopsy_gn="Membranous nephropathy")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("membranous", 0) >= 10, f"Expected Membranous score >= 10, got: {scores}"


class TestFSGSIntegration:
    def test_fsgs_differential(self):
        p = _make_patient("INT-FSGS-001", "FSGS", Decimal("45"),
                          labs=[("upcr", Decimal("4.0"))],
                          biopsy_gn="FSGS")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("fsgs", 0) >= 10, f"Expected FSGS score >= 10, got: {scores}"


class TestMCDIntegration:
    def test_mcd_differential(self):
        p = _make_patient("INT-MCD-001", "Minimal change disease", Decimal("90"),
                          labs=[("upcr", Decimal("6.0")), ("albumin", Decimal("1.8"))],
                          biopsy_gn="Minimal change disease")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("mcd", 0) >= 10, f"Expected MCD score >= 10, got: {scores}"


class TestAntiGBMIntegration:
    def test_anti_gbm_differential(self):
        p = _make_patient("INT-GBM-001", "Anti-GBM disease", Decimal("15"),
                          labs=[("creatinine", Decimal("4.0")), ("antiGbm", 1)],
                          biopsy_gn="Anti-GBM disease")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("antiGbm", 0) >= 10, f"Expected Anti-GBM score >= 10, got: {scores}"


class TestC3GIntegration:
    def test_c3g_differential(self):
        p = _make_patient("INT-C3-001", "C3 glomerulopathy", Decimal("60"),
                          labs=[("c3", Decimal("45")), ("upcr", Decimal("2.5"))],
                          biopsy_gn="C3 glomerulopathy")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("c3", 0) >= 10, f"Expected C3G score >= 10, got: {scores}"


class TestDKDIntegration:
    def test_dkd_differential(self):
        p = _make_patient("INT-DKD-001", "Diabetic kidney disease", Decimal("42"),
                          labs=[("creatinine", Decimal("1.6")), ("hba1c", Decimal("7.5"))],
                          phase="ckd", encounter_type="followup")
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(p)
        scores = _differential_scores(profile)
        assert scores.get("diabeticNephropathy", 0) >= 8, f"Expected DKD score >= 8, got: {scores}"
