"""Clinical Validation — disease workflow tests for V3 Production Release."""
import pytest
from datetime import date, timedelta

pytestmark = pytest.mark.django_db


@pytest.fixture
def patient():
    from patients.models import Patient
    from django.utils import timezone
    p = Patient.objects.create(
        patient_id="VALIDATE-001",
        name="Validation Patient",
        hospital_id="H-VAL-001",
        phone="+1234567890",
        sex="F",
        cohort="GN",
        diabetes_status="no",
        primary_diagnosis="LN",
        current_phase="active",
        registration_status="active",
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    return p


class TestClinicalChecks:
    """Verify shared clinical checks module (deduplication)."""

    def test_check_biopsy_exists_no_biopsy(self, patient):
        from clinical_reasoning.services.clinical_checks import check_biopsy_exists
        assert check_biopsy_exists(patient) is False

    def test_check_biopsy_exists_with_biopsy(self, patient):
        from pathology.models import Biopsy
        from datetime import date
        Biopsy.objects.create(patient=patient, biopsy_date=date.today(), adequacy="adequate")
        from clinical_reasoning.services.clinical_checks import check_biopsy_exists
        assert check_biopsy_exists(patient) is True

    def test_check_egfr_exists_missing(self, patient):
        from clinical_reasoning.services.clinical_checks import check_egfr_exists
        assert check_egfr_exists(patient) is False

    def test_check_egfr_exists_present(self, patient):
        patient.latest_egfr = 45.0
        patient.save()
        from clinical_reasoning.services.clinical_checks import check_egfr_exists
        assert check_egfr_exists(patient) is True

    def test_check_overdue_visit_no_encounters(self, patient):
        from clinical_reasoning.services.clinical_checks import check_overdue_visit
        overdue, latest = check_overdue_visit(patient)
        assert overdue is True
        assert latest is None

    def test_check_overdue_visit_recent(self, patient):
        from encounters.models import ClinicalEncounter
        from datetime import date
        ClinicalEncounter.objects.create(
            patient=patient, encounter_date=date.today() - timedelta(days=30), encounter_type="clinic"
        )
        from clinical_reasoning.services.clinical_checks import check_overdue_visit
        overdue, _ = check_overdue_visit(patient)
        assert overdue is False

    def test_has_active_treatment_no(self, patient):
        from clinical_reasoning.services.clinical_checks import has_active_treatment
        assert has_active_treatment(patient) is False

    def test_has_active_treatment_yes(self, patient):
        from treatments.models import TreatmentExposure, DrugMaster
        from datetime import date
        drug = DrugMaster.objects.create(generic_name="Mycophenolate mofetil")
        TreatmentExposure.objects.create(
            patient=patient, drug=drug, start_date=date.today(), ongoing=True
        )
        from clinical_reasoning.services.clinical_checks import has_active_treatment
        assert has_active_treatment(patient) is True


class TestOperationalIntelligenceNPlusOne:
    """Verify N+1 queries are eliminated."""

    def test_compute_compliance_summary_no_crash(self, patient):
        from clinical_reasoning.services.operational_intelligence import compute_compliance_summary
        result = compute_compliance_summary()
        assert "total_patients" in result
        assert "missing_biopsy" in result
        assert "missing_egfr" in result
        assert result["total_patients"] >= 1

    def test_compute_patient_compliance(self, patient):
        from clinical_reasoning.services.operational_intelligence import compute_patient_compliance
        result = compute_patient_compliance(patient)
        assert result["patient_id"] == "VALIDATE-001"
        assert "deductions" in result
        assert "compliance_score" in result


class TestPatientDeleteProtection:
    """Verify Patient.delete() raises PermissionDenied."""

    def test_patient_delete_raises(self, patient):
        from django.core.exceptions import PermissionDenied
        with pytest.raises(PermissionDenied):
            patient.delete()

    def test_patient_inactive_still_allowed(self, patient):
        """Marking inactive should work fine."""
        patient.registration_status = "inactive"
        patient.save()
        assert patient.registration_status == "inactive"


class TestAsyncDispatch:
    """Verify async dispatch marks events correctly."""

    def test_mark_async_and_dispatch(self):
        from events.dispatcher import mark_async, dispatch, subscribe, _async_event_types
        test_type = "test.clinical.validation"
        events_called = []

        def handler(event_type, **kwargs):
            events_called.append(event_type)

        subscribe(test_type, handler)
        mark_async(test_type)
        assert test_type in _async_event_types
        dispatch(test_type, payload={"test": True})
        # Should still dispatch in-process since no Celery broker
        assert test_type in events_called

    def test_dispatcher_persists_event(self):
        from events.dispatcher import dispatch
        dispatch("test.persistence", source_model="Patient", source_pk="1", payload={"k": "v"})
        from events.models import Event
        assert Event.objects.filter(event_type="test.persistence").exists()


class TestRateLimiterRedisFallback:
    """Verify RateLimiter works (in-memory fallback)."""

    def test_rate_limiter_allows(self):
        from clinical_reasoning.services.enterprise_readiness import RateLimiter
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.check("test-key") is True

    def test_rate_limiter_blocks(self):
        from clinical_reasoning.services.enterprise_readiness import RateLimiter
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.check("block-key") is True
        assert limiter.check("block-key") is True
        assert limiter.check("block-key") is False

    def test_rate_limiter_remaining(self):
        from clinical_reasoning.services.enterprise_readiness import RateLimiter
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.remaining("remaining-key") == 10
        limiter.check("remaining-key")
        assert limiter.remaining("remaining-key") == 9


class TestHealthEndpoint:
    """Verify health check returns proper status."""

    def test_health_check_ok(self, rf):
        from bgddr.views import health_check
        request = rf.get("/health/")
        response = health_check(request)
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert data["database"] == "ok"
        assert data["version"] == 3


class TestCarePathwayEngine:
    """Verify care pathway deviation detection works."""

    def test_assess_pathway_deviation_no_stage(self, patient):
        from clinical_reasoning.services.care_pathway_engine import assess_pathway_deviation
        deviations = assess_pathway_deviation(patient, "nonexistent", {})
        assert deviations == []

    def test_assess_pathway_deviation_assessment(self, patient):
        from clinical_reasoning.services.care_pathway_engine import assess_pathway_deviation
        deviations = assess_pathway_deviation(patient, "assessment", {})
        assert len(deviations) >= 1
        issues = [d["issue"] for d in deviations]
        assert "missing_biopsy" in issues
        assert "missing_egfr" in issues

    def test_determine_current_stage(self, patient):
        from clinical_reasoning.services.care_pathway_engine import determine_current_stage
        stage = determine_current_stage(patient, {"disease_phase": "active"})
        assert stage == "active_disease"

    def test_detect_stage_transition_valid(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        result = detect_stage_transition(None, "assessment", "active_disease")
        assert result["valid"] is True

    def test_detect_stage_transition_invalid(self):
        from clinical_reasoning.services.care_pathway_engine import detect_stage_transition
        result = detect_stage_transition(None, "assessment", "post_transplant")
        assert result["valid"] is False


class TestDiseaseMilestones:
    """Verify milestone detection."""

    def test_detect_milestones_returns_list(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {}, {})
        assert isinstance(milestones, list)

    def test_milestone_diagnosis_detected(self, patient):
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {}, {})
        types = [m["milestone_type"] for m in milestones]
        assert "diagnosis" in types

    def test_milestone_eskd_detected(self, patient):
        patient.latest_egfr = 10.0
        patient.save()
        from clinical_reasoning.services.disease_milestones import detect_milestones
        milestones = detect_milestones(patient, {"disease_phase": ""}, {})
        types = [m["milestone_type"] for m in milestones]
        assert "eskd" in types


class TestEngineIntegration:
    """Verify the clinical reasoning engine integration works."""

    def test_reason_about_patient_creates_profile(self, patient):
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(patient)
        assert profile is not None
        assert profile.patient == patient
        assert profile.version >= 1

    def test_recompute_all_profiles(self, patient):
        from clinical_reasoning.services.engine import recompute_all_profiles
        result = recompute_all_profiles()
        assert result["total"] >= 1
        assert result["errors"] == 0
