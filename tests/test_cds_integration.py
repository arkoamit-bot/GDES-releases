"""Integration tests that exercise the real ORM path for CDS services.

These tests build real model rows and do NOT mock _get_current_medications
or _get_recent_lab_values, ensuring the fixes in B-1/B-2/B-3 hold.
"""
import pytest
from datetime import timedelta
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.fixture
def patient():
    from patients.models import Patient
    return Patient.objects.create(
        patient_id="P-INT-001",
        name="Integration Test Patient",
        hospital_id="H-INT-001",
        phone="+8801700000001",
        sex="M",
        cohort="GN",
        diabetes_status="no",
        primary_diagnosis="LN",
        current_phase="active",
        registration_status="active",
    )


@pytest.fixture
def drug_mmf():
    from treatments.models import DrugMaster, DrugClass
    return DrugMaster.objects.create(
        generic_name="Mycophenolate mofetil",
        drug_class=DrugClass.MMF,
        is_active=True,
    )


@pytest.fixture
def drug_tacrolimus():
    from treatments.models import DrugMaster, DrugClass
    return DrugMaster.objects.create(
        generic_name="Tacrolimus",
        drug_class=DrugClass.CNI,
        is_active=True,
    )


@pytest.fixture
def drug_rituximab():
    from treatments.models import DrugMaster, DrugClass
    return DrugMaster.objects.create(
        generic_name="Rituximab",
        drug_class=DrugClass.RITUXIMAB,
        is_active=True,
    )


@pytest.fixture
def wbc_test():
    from labs.models import LabTest
    return LabTest.objects.create(code="wbc", name="WBC", value_type="numeric")


@pytest.fixture
def creatinine_test():
    from labs.models import LabTest
    return LabTest.objects.create(code="creatinine", name="Creatinine", value_type="numeric")


@pytest.fixture
def igg_test():
    from labs.models import LabTest
    return LabTest.objects.create(code="igg", name="Immunoglobulin G", value_type="numeric")


# ── B-1: _get_current_medications reads ongoing TreatmentExposure ────────────


def test_toxicity_reads_ongoing_meds(patient, drug_mmf):
    from treatments.models import TreatmentExposure
    from clinical_reasoning.services.drug_toxicity import _get_current_medications
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        dose="1 g", frequency="1+0+1", start_date=timezone.now().date(),
        ongoing=True,
    )
    meds = _get_current_medications(patient)
    assert any("mycophenolate" in m["name"].lower() for m in meds)


def test_toxicity_returns_empty_for_no_meds(patient):
    from clinical_reasoning.services.drug_toxicity import _get_current_medications
    meds = _get_current_medications(patient)
    assert meds == []


def test_toxicity_ignores_stopped_exposures(patient, drug_mmf):
    from treatments.models import TreatmentExposure
    from clinical_reasoning.services.drug_toxicity import _get_current_medications
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        dose="1 g", frequency="1+0+1", start_date=timezone.now().date() - timedelta(days=365),
        stop_date=timezone.now().date() - timedelta(days=30),
        ongoing=False, stop_reason="remission",
    )
    meds = _get_current_medications(patient)
    assert all("mycophenolate" not in m["name"].lower() for m in meds)


# ── B-2: numeric_value → value_numeric (lab endpoints return 200) ────────────


def test_toxicity_endpoint_ok_with_labs(client, patient, drug_mmf, creatinine_test):
    from treatments.models import TreatmentExposure
    from labs.models import LabResult
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        dose="1 g", frequency="1+0+1", start_date=timezone.now().date(),
        ongoing=True,
    )
    LabResult.objects.create(
        patient=patient, test=creatinine_test,
        value_numeric=1.2, result_date=timezone.now().date(),
    )
    report = _run_detect_toxicity(patient)
    assert report is not None
    assert hasattr(report, "alerts")


def _run_detect_toxicity(patient):
    from clinical_reasoning.services.drug_toxicity import detect_drug_toxicity
    return detect_drug_toxicity(patient)


def test_treatment_failure_endpoint_ok(client, patient, creatinine_test):
    from labs.models import LabResult
    LabResult.objects.create(
        patient=patient, test=creatinine_test,
        value_numeric=1.0, result_date=timezone.now().date(),
    )
    from clinical_reasoning.services.treatment_failure import detect_treatment_failure
    report = detect_treatment_failure(patient)
    assert report is not None
    assert report.patient_id == patient.patient_id


# ── B-3: direction="low" for WBC/IgG rules ──────────────────────────────────


def test_normal_wbc_on_mmf_no_alert(patient, drug_mmf, wbc_test):
    from treatments.models import TreatmentExposure
    from labs.models import LabResult
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        dose="1 g", frequency="1+0+1", start_date=timezone.now().date(),
        ongoing=True,
    )
    LabResult.objects.create(
        patient=patient, test=wbc_test,
        value_numeric=7.0, result_date=timezone.now().date(),
    )
    report = _run_detect_toxicity(patient)
    critical = [a for a in report.alerts if a.severity == "critical"]
    assert len(critical) == 0


def test_critical_wbc_on_mmf(patient, drug_mmf, wbc_test):
    from treatments.models import TreatmentExposure
    from labs.models import LabResult
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        dose="1 g", frequency="1+0+1", start_date=timezone.now().date(),
        ongoing=True,
    )
    LabResult.objects.create(
        patient=patient, test=wbc_test,
        value_numeric=0.7, result_date=timezone.now().date(),
    )
    report = _run_detect_toxicity(patient)
    critical = [a for a in report.alerts if a.severity == "critical"]
    assert len(critical) >= 1
    assert any("wbc" in a.lab_test.lower() for a in critical)


def test_normal_igg_on_rituximab_no_alert(patient, drug_rituximab, igg_test):
    from treatments.models import TreatmentExposure
    from labs.models import LabResult
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_rituximab, drug_name="Rituximab",
        dose="1 g", frequency="1+0+0", start_date=timezone.now().date(),
        ongoing=True,
    )
    LabResult.objects.create(
        patient=patient, test=igg_test,
        value_numeric=1000, result_date=timezone.now().date(),
    )
    report = _run_detect_toxicity(patient)
    critical = [a for a in report.alerts if a.severity == "critical"]
    assert len(critical) == 0


def test_critical_igg_on_rituximab(patient, drug_rituximab, igg_test):
    from treatments.models import TreatmentExposure
    from labs.models import LabResult
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_rituximab, drug_name="Rituximab",
        dose="1 g", frequency="1+0+0", start_date=timezone.now().date(),
        ongoing=True,
    )
    LabResult.objects.create(
        patient=patient, test=igg_test,
        value_numeric=90, result_date=timezone.now().date(),
    )
    report = _run_detect_toxicity(patient)
    critical = [a for a in report.alerts if a.severity == "critical"]
    assert len(critical) >= 1
    assert any("immunoglobulin" in a.lab_test.lower() for a in critical)


def test_high_direction_still_works(patient, drug_tacrolimus, creatinine_test):
    """Regression: "high" direction rules still fire correctly."""
    from treatments.models import TreatmentExposure
    from labs.models import LabResult
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_tacrolimus, drug_name="Tacrolimus",
        dose="2 mg", frequency="1+0+0", start_date=timezone.now().date(),
        ongoing=True,
    )
    LabResult.objects.create(
        patient=patient, test=creatinine_test,
        value_numeric=3.6, result_date=timezone.now().date(),
    )
    report = _run_detect_toxicity(patient)
    critical = [a for a in report.alerts if a.severity == "critical"]
    assert len(critical) >= 1
    assert any("creatinine" in a.lab_test.lower() for a in critical)


# ── disease-milestones: TreatmentExposure uses drug_name (not treatment_name) ─


def test_treatment_milestones_generated(patient, drug_mmf, drug_tacrolimus):
    """_check_treatment_milestones must read drug_name off TreatmentExposure.

    Regression for the silent field-drift bug: the code previously read
    `treatment_name`/`regimen_name` (which do not exist on TreatmentExposure),
    so every access raised AttributeError and was swallowed — no treatment
    milestone was ever generated.
    """
    from treatments.models import TreatmentExposure
    from clinical_reasoning.services.disease_milestones import _check_treatment_milestones

    TreatmentExposure.objects.create(
        patient=patient, drug=drug_tacrolimus, drug_name="Tacrolimus",
        start_date=timezone.now().date() - timedelta(days=200),
        stop_date=timezone.now().date() - timedelta(days=10),
        ongoing=False, stop_reason="switch",
    )
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        start_date=timezone.now().date(), ongoing=True,
    )

    milestones: list = []
    _check_treatment_milestones(patient, milestones)
    types = [m["milestone_type"] for m in milestones]
    labels = " ".join(m["label"] for m in milestones)

    assert "treatment_started" in types
    assert "treatment_switched" in types
    assert "Tacrolimus" in labels
    assert "Mycophenolate mofetil" in labels


# ---------------------------------------------------------------------------
# Regression: _get_previous_egfr uses correct field names and ckd_epi_2021
# ---------------------------------------------------------------------------

def test_get_previous_egfr_via_creatinine(patient):
    """_get_previous_egfr should derive eGFR from creatinine using correct
    patient.sex (not .gender) and ckd_epi_2021 (not missing calculate_egfr)."""
    from datetime import date
    from clinical_reasoning.services.treatment_failure import _get_previous_egfr
    from labs.models import LabTest, LabResult

    # Ensure the creatinine LabTest exists
    lt, _ = LabTest.objects.get_or_create(
        code="creatinine",
        defaults={"name": "Creatinine", "default_unit": "mg/dL"},
    )
    # Patient needs a dob for age calculation
    patient.dob = date(1980, 6, 15)
    patient.save(update_fields=["dob"])

    # Create a creatinine result 6 months ago
    six_months_ago = timezone.now().date() - timedelta(days=180)
    LabResult.objects.create(
        patient=patient,
        test=lt,
        value_numeric=1.5,
        result_date=six_months_ago,
    )

    egfr = _get_previous_egfr(patient, months_ago=6)
    # 40yo male, creatinine 1.5 -> CKD-EPI 2021 ~53 (not exact, but > 0 means formula ran)
    assert egfr is not None, "Should derive eGFR from creatinine"
    assert egfr > 0, f"eGFR should be positive, got {egfr}"
    # Verify it's in plausible CKD-EPI range (40yo M, Cr 1.5 -> ~52-54)
    assert 45 < egfr < 65, f"eGFR {egfr} outside expected range for 40yo M Cr=1.5"


def test_get_previous_egfr_reads_existing_egfr(patient):
    """_get_previous_egfr should return stored eGFR directly."""
    from clinical_reasoning.services.treatment_failure import _get_previous_egfr
    from labs.models import LabTest, LabResult

    lt, _ = LabTest.objects.get_or_create(
        code="egfr",
        defaults={"name": "eGFR", "default_unit": "mL/min/1.73m2"},
    )
    six_months_ago = timezone.now().date() - timedelta(days=180)
    LabResult.objects.create(
        patient=patient,
        test=lt,
        value_numeric=55.0,
        result_date=six_months_ago,
    )

    egfr = _get_previous_egfr(patient, months_ago=6)
    assert egfr == 55.0, f"Should return stored eGFR, got {egfr}"


def test_get_previous_egfr_no_dob_returns_none(patient):
    """When patient has no dob, creatinine path returns None gracefully."""
    from clinical_reasoning.services.treatment_failure import _get_previous_egfr
    from labs.models import LabTest, LabResult

    lt, _ = LabTest.objects.get_or_create(
        code="creatinine",
        defaults={"name": "Creatinine", "default_unit": "mg/dL"},
    )
    patient.dob = None
    patient.save(update_fields=["dob"])

    six_months_ago = timezone.now().date() - timedelta(days=180)
    LabResult.objects.create(
        patient=patient,
        test=lt,
        value_numeric=1.2,
        result_date=six_months_ago,
    )

    egfr = _get_previous_egfr(patient, months_ago=6)
    assert egfr is None, "Should return None when dob is missing"
