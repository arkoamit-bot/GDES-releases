import pytest
import datetime as dt

from clinical_reasoning.services.management_plan import (
    generate_management_plan,
    DISEASE_TREATMENT_PROFILES,
)
from clinical_reasoning.services.monitoring_plan import (
    generate_monitoring_plan,
    DISEASE_MONITORING_PROTOCOLS,
    CKD_STAGE_MONITORING,
)
from clinical_reasoning.services.followup_scheduler import (
    generate_follow_up_schedule,
    auto_schedule_on_phase_change,
    generate_monitoring_tasks,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def patient():
    from patients.models import Patient
    from django.utils import timezone
    return Patient.objects.create(
        patient_id="P001",
        name="Test Patient",
        hospital_id="H001",
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


# ---------------------------------------------------------------------------
# Management Plan Tests
# ---------------------------------------------------------------------------

class TestManagementPlanGenerator:
    def test_generates_plan_for_known_disease(self, patient):
        plan = generate_management_plan(patient, "iga")
        assert plan is not None
        assert plan.disease_id == "iga"
        assert plan.disease_name == "IgA Nephropathy"
        assert plan.patient_id == patient.patient_id
        assert len(plan.first_line) > 0
        assert plan.first_line[0].get("drug") is not None

    def test_plan_has_all_sections(self, patient):
        plan = generate_management_plan(patient, "membranous")
        assert len(plan.first_line) > 0
        assert len(plan.second_line) > 0
        assert len(plan.rescue_therapy) > 0
        assert len(plan.contraindicated) > 0
        assert len(plan.monitoring) > 0
        assert isinstance(plan.follow_up, dict)
        assert len(plan.general_measures) > 0
        assert len(plan.safety_checks) >= 0
        assert len(plan.patient_education) > 0

    def test_unknown_disease_returns_default(self, patient):
        plan = generate_management_plan(patient, "rare_disease_xyz")
        assert plan is not None
        assert plan.disease_id == "rare_disease_xyz"
        assert len(plan.first_line) == 1  # Default: nephrology consultation
        assert plan.first_line[0]["drug"] == "Nephrology consultation"

    def test_to_dict_returns_dict(self, patient):
        plan = generate_management_plan(patient, "lupus")
        d = plan.to_dict()
        assert isinstance(d, dict)
        assert d["disease_id"] == "lupus"
        assert "first_line" in d
        assert "monitoring" in d

    def test_all_diseases_have_profiles(self):
        expected_diseases = [
            "iga", "membranous", "mcd", "fsgs", "lupus", "anca",
            "antiGbm", "infectionRelated", "c3",
        ]
        for disease_id in expected_diseases:
            assert disease_id in DISEASE_TREATMENT_PROFILES, f"Missing profile for {disease_id}"

    def test_all_disease_profiles_have_required_fields(self):
        required_fields = [
            "disease_name", "first_line", "second_line", "monitoring", "follow_up"
        ]
        for disease_id, profile in DISEASE_TREATMENT_PROFILES.items():
            for field in required_fields:
                assert field in profile, f"{disease_id} missing '{field}'"

    def test_pregnancy_check_for_female(self, patient):
        patient.sex = "F"
        patient.save()
        plan = generate_management_plan(patient, "lupus")
        pregnancy_checks = [c for c in plan.safety_checks if c.get("type") == "pregnancy_screening"]
        assert len(pregnancy_checks) == 1

    def test_infection_risk_check_for_immunosuppressive_diseases(self, patient):
        plan = generate_management_plan(patient, "lupus")
        infection_checks = [c for c in plan.safety_checks if c.get("type") == "infection_risk"]
        assert len(infection_checks) == 1

    def test_very_high_risk_intensifies_monitoring(self, patient):
        plan_normal = generate_management_plan(patient, "iga", risk_category="moderate")
        plan_high = generate_management_plan(patient, "iga", risk_category="very_high")
        # Very high risk should have "every 2 weeks" in monitoring
        very_high_intervals = [
            m["interval"] for m in plan_high.monitoring if "2 weeks" in m.get("interval", "")
        ]
        assert len(very_high_intervals) > 0

    def test_ckd_modifications_added(self, patient):
        plan = generate_management_plan(
            patient, "iga",
            features={"egfrTrend": "reduced"},
        )
        ckd_params = [m for m in plan.monitoring if "CKD-MBD" in m.get("parameter", "")]
        assert len(ckd_params) > 0


# ---------------------------------------------------------------------------
# Monitoring Plan Tests
# ---------------------------------------------------------------------------

class TestMonitoringPlanGenerator:
    def test_generates_plan_for_known_disease(self, patient):
        plan = generate_monitoring_plan(patient, "iga")
        assert plan is not None
        assert plan.disease_id == "iga"
        assert plan.disease_name == "IgA Nephropathy"
        assert len(plan.parameters) > 0

    def test_plan_has_all_sections(self, patient):
        plan = generate_monitoring_plan(patient, "membranous")
        assert len(plan.parameters) > 0
        assert isinstance(plan.treatment_monitoring, list)
        assert isinstance(plan.ckd_monitoring, list)
        assert isinstance(plan.risk_adjustments, list)
        assert plan.generated_date == str(dt.date.today())

    def test_unknown_disease_returns_default(self, patient):
        plan = generate_monitoring_plan(patient, "unknown_disease")
        assert plan is not None
        assert plan.disease_id == "unknown_disease"
        assert len(plan.parameters) == 3  # Default: creatinine, eGFR, BP

    def test_treatment_monitoring_included(self, patient):
        plan = generate_monitoring_plan(
            patient, "iga",
            active_treatments=["acei_arb", "sglt2_inhibitor"],
        )
        assert len(plan.treatment_monitoring) > 0
        treatment_names = {m["for_treatment"] for m in plan.treatment_monitoring}
        assert "acei_arb" in treatment_names
        assert "sglt2_inhibitor" in treatment_names

    def test_ckd_stage_monitoring_included(self, patient):
        plan = generate_monitoring_plan(patient, "iga", ckd_stage=4)
        assert len(plan.ckd_monitoring) > 0
        ckd_params = {m["name"] for m in plan.ckd_monitoring}
        assert "CKD-MBD panel (Ca/PO4/PTH)" in ckd_params
        assert "Hemoglobin" in ckd_params

    def test_very_high_risk_shortens_intervals(self, patient):
        plan_normal = generate_monitoring_plan(patient, "iga", risk_category="moderate")
        plan_high = generate_monitoring_plan(patient, "iga", risk_category="very_high")
        # Check that at least one interval was shortened
        assert len(plan_high.risk_adjustments) > 0

    def test_to_dict_returns_dict(self, patient):
        plan = generate_monitoring_plan(patient, "lupus")
        d = plan.to_dict()
        assert isinstance(d, dict)
        assert d["disease_id"] == "lupus"
        assert "parameters" in d
        assert "treatment_monitoring" in d

    def test_all_diseases_have_monitoring_protocols(self):
        expected = [
            "iga", "membranous", "mcd", "fsgs", "lupus", "anca",
            "antiGbm", "infectionRelated", "c3",
        ]
        for disease_id in expected:
            assert disease_id in DISEASE_MONITORING_PROTOCOLS

    def test_ckd_stages_have_protocols(self):
        for stage in [3, 4, 5]:
            assert stage in CKD_STAGE_MONITORING
            assert len(CKD_STAGE_MONITORING[stage]) > 0

    def test_ckd5_has_volume_monitoring(self):
        params = {m["name"] for m in CKD_STAGE_MONITORING[5]}
        assert "Volume status (weight/edema)" in params


# ---------------------------------------------------------------------------
# Follow-up Scheduler Tests
# ---------------------------------------------------------------------------

class TestFollowUpScheduler:
    def test_generates_schedule(self, patient):
        visits = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=3,
        )
        assert len(visits) == 3
        for visit in visits:
            assert "visit_id" in visit
            assert "task_id" in visit
            assert "label" in visit
            assert "target_date" in visit
            assert "window" in visit
            assert "kind" in visit

    def test_first_visit_is_early_safety(self, patient):
        visits = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=2,
        )
        assert visits[0]["kind"] == "early_safety"
        assert visits[1]["kind"] == "routine"

    def test_very_high_risk_has_shorter_intervals(self, patient):
        from scheduling.models import ScheduledVisit
        visits_vh = generate_follow_up_schedule(
            patient,
            risk_category="very_high",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=2,
        )
        # Clean up to avoid unique constraint on second call
        ScheduledVisit.objects.filter(patient=patient).delete()
        from followup.models import FollowUpTask
        FollowUpTask.objects.filter(patient=patient).delete()

        visits_low = generate_follow_up_schedule(
            patient,
            risk_category="low",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=2,
        )
        # Parse target dates to compare intervals
        td1 = dt.date.fromisoformat(visits_vh[0]["target_date"])
        td2 = dt.date.fromisoformat(visits_vh[1]["target_date"])
        td3 = dt.date.fromisoformat(visits_low[0]["target_date"])
        td4 = dt.date.fromisoformat(visits_low[1]["target_date"])
        interval_vh = (td2 - td1).days
        interval_low = (td4 - td3).days
        assert interval_vh <= interval_low

    def test_remission_phase_has_longer_intervals(self, patient):
        visits_rem = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="remission",
            treatment_phase="maintenance",
            num_visits=2,
        )
        visits_act = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=2,
        )
        td1 = dt.date.fromisoformat(visits_rem[0]["target_date"])
        td2 = dt.date.fromisoformat(visits_rem[1]["target_date"])
        td3 = dt.date.fromisoformat(visits_act[0]["target_date"])
        td4 = dt.date.fromisoformat(visits_act[1]["target_date"])
        interval_rem = (td2 - td1).days
        interval_act = (td4 - td3).days
        assert interval_rem >= interval_act

    def test_creates_scheduled_visit_records(self, patient):
        from scheduling.models import ScheduledVisit
        visits = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=3,
        )
        sv_count = ScheduledVisit.objects.filter(patient=patient).count()
        assert sv_count == 3

    def test_creates_followup_task_records(self, patient):
        from followup.models import FollowUpTask
        visits = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=3,
        )
        ft_count = FollowUpTask.objects.filter(
            patient=patient,
            task_type="visit_due",
        ).count()
        assert ft_count == 3

    def test_auto_schedule_on_phase_change(self, patient):
        from scheduling.models import ScheduledVisit
        # Create initial schedule
        generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=3,
        )
        assert ScheduledVisit.objects.filter(patient=patient).count() == 3

        # Phase change to remission
        patient.current_phase = "remission"
        patient.save()
        new_visits = auto_schedule_on_phase_change(patient, "active", "remission")
        # Old visits should be cancelled, new ones created
        cancelled = ScheduledVisit.objects.filter(
            patient=patient, status=ScheduledVisit.Status.CANCELLED
        ).count()
        assert cancelled == 3
        scheduled = ScheduledVisit.objects.filter(
            patient=patient, status=ScheduledVisit.Status.SCHEDULED
        ).count()
        assert scheduled > 0

    def test_generate_monitoring_tasks(self, patient):
        from followup.models import FollowUpTask
        params = [
            {"parameter": "UPCR", "interval": "monthly", "target": "<0.5", "action_threshold": ">1.0"},
            {"parameter": "Serum creatinine", "interval": "every 2 weeks", "target": "Stable", "action_threshold": ">20% decline"},
        ]
        tasks = generate_monitoring_tasks(patient, params, dt.date.today())
        assert len(tasks) == 2
        ft_count = FollowUpTask.objects.filter(
            patient=patient, task_type="drug_monitoring_due"
        ).count()
        assert ft_count == 2

    def test_induction_phase_has_more_frequent_initial(self, patient):
        """During induction, first 2 visits should be closer together."""
        visits = generate_follow_up_schedule(
            patient,
            risk_category="moderate",
            disease_phase="active",
            treatment_phase="induction",
            num_visits=4,
        )
        td0 = dt.date.fromisoformat(visits[0]["target_date"])
        td1 = dt.date.fromisoformat(visits[1]["target_date"])
        td2 = dt.date.fromisoformat(visits[2]["target_date"])
        interval_01 = (td1 - td0).days
        interval_12 = (td2 - td1).days
        # Initial visits should be more frequent
        assert interval_01 <= interval_12
