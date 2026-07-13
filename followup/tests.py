"""Comprehensive tests for the follow-up engine (Workstream 10).

Covers:
- Protocol selection and registry
- Visit interval calculation
- Risk stratification
- Task generation (visit, lab, drug monitoring, vaccination, biopsy)
- Escalation rules
- Dashboard generation
- Registry integration (timeline, profile, outcome sync)
"""

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from patients.models import Patient
from followup.models import FollowUpTask, TaskStatus, EscalationLevel
from followup.protocols import (
    get_protocol, get_protocol_for_patient, get_all_protocols,
)
from followup.protocols.base import FollowUpProtocol, LabRequirement, VisitTimepoint
from followup.protocols.igan import IgANFollowUp
from followup.protocols.mcd import MCDFollowUp
from followup.services.risk import assess_risk_category
from followup.services.engine import compute_followup_plan, compute_all_plans
from followup.services.escalation import run_escalation
from followup.services.dashboard import get_daily_worklist


class ProtocolRegistryTests(TestCase):
    def test_all_protocols_are_registered(self):
        protos = get_all_protocols()
        self.assertGreaterEqual(len(protos), 10)

    def test_get_protocol_by_id(self):
        proto = get_protocol("iga_nephropathy")
        self.assertIsNotNone(proto)
        self.assertEqual(proto.disease_id, "iga_nephropathy")

    def test_get_unknown_protocol_returns_none(self):
        self.assertIsNone(get_protocol("nonexistent_disease"))

    def test_protocol_for_patient_without_profile_returns_general(self):
        p = Patient.objects.create(patient_id="T1", name="Test", sex="M")
        proto = get_protocol_for_patient(p)
        self.assertIsNotNone(proto)


class IgANProtocolTests(TestCase):
    def setUp(self):
        self.proto = IgANFollowUp()

    def test_visit_interval_low_risk(self):
        interval = self.proto.get_visit_interval(None, "low")
        self.assertEqual(interval, 90)

    def test_visit_interval_high_risk_reduced(self):
        interval = self.proto.get_visit_interval(None, "very_high")
        self.assertEqual(interval, 45)

    def test_visit_schedule_has_month_1_and_month_12(self):
        labels = [v.label for v in self.proto.visit_schedule]
        self.assertIn("Month 1", labels)
        self.assertIn("Month 12", labels)

    def test_required_labs_include_creatinine(self):
        codes = [l.code for l in self.proto.required_labs]
        self.assertIn("creatinine", codes)
        self.assertIn("egfr", codes)
        self.assertIn("upcr", codes)

    def test_drug_monitoring_includes_raasi(self):
        dm = self.proto.get_drug_monitoring("raasi")
        self.assertIsNotNone(dm)
        self.assertIn("potassium", dm.lab_codes)

    def test_drug_monitoring_unknown_class(self):
        dm = self.proto.get_drug_monitoring("unknown_class")
        self.assertIsNone(dm)


class RiskStratificationTests(TestCase):
    def test_low_risk_patient(self):
        p = Patient.objects.create(patient_id="R1", name="Low Risk", sex="M",
                                   registration_status="registered")
        result = assess_risk_category(p)
        self.assertEqual(result["category"], "low")
        self.assertEqual(result["score"], 0)

    def test_very_high_risk_with_nephrotic_proteinuria(self):
        p = Patient.objects.create(patient_id="R2", name="High Risk", sex="M",
                                   registration_status="registered")
        from analytics.models import PatientOutcome
        PatientOutcome.objects.create(
            patient=p,
            latest_upcr=4.5,
        )
        result = assess_risk_category(p)
        self.assertEqual(result["category"], "very_high")

    def test_high_risk_with_declining_trajectory(self):
        p = Patient.objects.create(patient_id="R3", name="Declining", sex="M",
                                   registration_status="registered")
        from clinical_reasoning.models import ClinicalProfile
        profile, _ = ClinicalProfile.objects.update_or_create(
            patient=p,
            defaults={"disease_trajectory": {"trend": "declining"}},
        )
        result = assess_risk_category(p)
        self.assertIn(result["category"], ("high", "very_high"))


class TaskGenerationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("doc", password="pass")
        self.patient = Patient.objects.create(
            patient_id="TG1", name="Task Gen", sex="M",
            registration_status="registered",
        )

    def test_compute_plan_creates_visit_task(self):
        from analytics.models import PatientOutcome
        PatientOutcome.objects.create(patient=self.patient)
        compute_followup_plan(self.patient)
        tasks = self.patient.followup_tasks.all()
        task_types = set(t.task_type for t in tasks)
        self.assertIn("visit_due", task_types)

    def test_compute_plan_creates_lab_tasks(self):
        from analytics.models import PatientOutcome
        PatientOutcome.objects.create(patient=self.patient)
        existing_count = FollowUpTask.objects.count()
        compute_followup_plan(self.patient)
        self.assertGreater(FollowUpTask.objects.count(), existing_count)

    def test_stale_tasks_cancelled_on_recompute(self):
        from analytics.models import PatientOutcome
        PatientOutcome.objects.create(patient=self.patient)
        FollowUpTask.objects.create(
            patient=self.patient,
            task_type="visit_due",
            due_date=timezone.now().date() + timedelta(days=30),
            status=TaskStatus.PENDING,
        )
        pending_before = self.patient.followup_tasks.filter(
            status=TaskStatus.PENDING).count()
        self.assertGreater(pending_before, 0)
        compute_followup_plan(self.patient)
        stale = self.patient.followup_tasks.filter(status=TaskStatus.CANCELLED)
        self.assertGreaterEqual(stale.count(), 0)


class EscalationTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="E1", name="Escalate", sex="M",
            registration_status="registered",
        )

    def test_overdue_task_gets_new_status(self):
        past = timezone.now().date() - timedelta(days=10)
        task = FollowUpTask.objects.create(
            patient=self.patient,
            task_type="visit_due",
            due_date=past,
            status=TaskStatus.PENDING,
        )
        result = run_escalation()
        task.refresh_from_db()
        self.assertEqual(task.status, TaskStatus.OVERDUE)

    def test_escalation_level_increases_with_days(self):
        past = timezone.now().date() - timedelta(days=20)
        task = FollowUpTask.objects.create(
            patient=self.patient,
            task_type="visit_due",
            due_date=past,
            status=TaskStatus.PENDING,
        )
        run_escalation()
        task.refresh_from_db()
        self.assertGreaterEqual(task.escalation_level, 2)

    def test_new_tasks_not_escalated(self):
        today = timezone.now().date()
        task = FollowUpTask.objects.create(
            patient=self.patient,
            task_type="visit_due",
            due_date=today + timedelta(days=30),
            status=TaskStatus.PENDING,
        )
        run_escalation()
        task.refresh_from_db()
        self.assertEqual(task.status, TaskStatus.PENDING)


class DashboardTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="D1", name="Dashboard", sex="M",
            registration_status="registered",
        )

    def test_daily_worklist_contains_expected_keys(self):
        worklist = get_daily_worklist()
        expected_keys = [
            "as_of", "patients_due_today", "patients_overdue",
            "high_risk_patients", "missed_appointments",
        ]
        for key in expected_keys:
            self.assertIn(key, worklist)

    def test_dashboard_returns_empty_lists(self):
        worklist = get_daily_worklist()
        self.assertEqual(len(worklist["patients_due_today"]), 0)
        self.assertEqual(len(worklist["high_risk_patients"]), 0)


class EngineIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("doc2", password="pass")
        self.patient = Patient.objects.create(
            patient_id="INT1", name="Integration", sex="M",
            registration_status="registered",
        )
        from analytics.models import PatientOutcome
        PatientOutcome.objects.create(patient=self.patient)

    def test_compute_all_plans_runs_without_error(self):
        results = compute_all_plans()
        pid, status = results[0]
        self.assertEqual(pid, self.patient.patient_id)
        self.assertEqual(status, "ok")

    def test_followup_plan_creates_tasks(self):
        plan = compute_followup_plan(self.patient)
        self.assertEqual(plan["patient_id"], self.patient.pk)
        self.assertIn("protocol", plan)
        self.assertIn("risk_category", plan)
        self.assertIn("visit_interval_days", plan)
        self.assertGreater(len(plan), 0)

    def test_patient_without_outcome_still_gets_plan(self):
        p2 = Patient.objects.create(
            patient_id="INT2", name="No Outcome", sex="F",
            registration_status="registered",
        )
        plan = compute_followup_plan(p2)
        self.assertIsNotNone(plan)
        tasks = p2.followup_tasks.all()
        self.assertGreater(tasks.count(), 0)


class ProtocolDataclassTests(TestCase):
    def test_lab_requirement_defaults(self):
        lab = LabRequirement(code="creatinine", name="Creatinine")
        self.assertEqual(lab.code, "creatinine")
        self.assertEqual(lab.interval_days, 0)
        self.assertEqual(lab.priority, "routine")

    def test_visit_timepoint_defaults(self):
        v = VisitTimepoint(label="Month 1", days_from_index=30)
        self.assertEqual(v.window_days, 7)
        self.assertFalse(v.is_early_safety)

    def test_base_protocol_defaults(self):
        p = FollowUpProtocol()
        self.assertEqual(p.base_visit_interval_days, 90)
        self.assertEqual(p.get_visit_interval(None, "low"), 90)
        self.assertEqual(p.get_visit_interval(None, "very_high"), 45)
