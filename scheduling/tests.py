"""
Tests for follow-up scheduling: protocol timepoints, Tuesday snapping + windows,
early safety visits, clinic capacity, due/overdue, and monitoring requirements.
"""
import datetime as dt

from django.test import TestCase

from encounters.models import ClinicalEncounter
from patients.models import Patient
from treatments.models import DrugClass, DrugMaster, TreatmentExposure

from .models import ScheduledVisit
from .services.monitoring import (is_on_active_immunosuppression,
                                  monitoring_requirements)
from .services.schedule import (ROUTINE_MONTHS, clinic_roster, complete_visit,
                                due_visits, generate_schedule, nearest_clinic_day,
                                overdue_visits)


class ScheduleGenerationTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(patient_id="SC1", name="x", sex="M")
        self.anchor = dt.date(2026, 1, 5)   # a Monday

    def test_routine_schedule_created_on_tuesdays(self):
        created = generate_schedule(self.p, self.anchor, horizon_months=12)
        # Months 1,3,6,9,12 within a 12-month horizon.
        labels = sorted(v.label for v in created)
        self.assertEqual(set(labels),
                         {"Month 1", "Month 3", "Month 6", "Month 9", "Month 12"})
        for v in created:
            self.assertEqual(v.clinic_date.weekday(), 1)      # Tuesday
            self.assertLessEqual(v.window_start, v.clinic_date)
            self.assertLessEqual(v.clinic_date, v.window_end)

    def test_early_safety_visits_only_when_immunosuppressed(self):
        created = generate_schedule(self.p, self.anchor, immunosuppressed=True,
                                    horizon_months=6)
        labels = {v.label for v in created}
        self.assertTrue({"Week 1", "Week 2", "Week 4"} <= labels)
        early = [v for v in created if v.kind == ScheduledVisit.Kind.EARLY_SAFETY]
        self.assertEqual(len(early), 3)

    def test_nearest_clinic_day_is_tuesday(self):
        # 2026-01-05 is Monday -> nearest Tuesday is 2026-01-06.
        self.assertEqual(nearest_clinic_day(dt.date(2026, 1, 5)), dt.date(2026, 1, 6))
        self.assertEqual(nearest_clinic_day(dt.date(2026, 1, 6)).weekday(), 1)

    def test_full_schedule_spans_five_years(self):
        created = generate_schedule(self.p, self.anchor)
        self.assertEqual(len(created), len(ROUTINE_MONTHS))


class CapacityAndStatusTests(TestCase):
    def test_capacity_pushes_to_another_tuesday(self):
        anchor = dt.date(2026, 1, 5)
        # Fill one Month-1 Tuesday with capacity (15) patients, then a 16th must
        # land on a different clinic day within its window.
        from django.test import override_settings
        with override_settings(SCHEDULING={"clinic_weekday": 1, "session_capacity": 2,
                                            "window_days": 7}):
            for i in range(3):
                p = Patient.objects.create(patient_id=f"CAP{i}", name=f"c{i}", sex="M")
                generate_schedule(p, anchor, horizon_months=1)
            m1 = ScheduledVisit.objects.filter(label="Month 1")
            clinic_days = {v.clinic_date for v in m1}
            # 3 patients, capacity 2 -> must use >1 clinic day.
            self.assertGreater(len(clinic_days), 1)

    def test_due_and_overdue(self):
        p = Patient.objects.create(patient_id="DUE1", name="d", sex="M")
        generate_schedule(p, dt.date(2026, 1, 5), horizon_months=12)
        m1 = ScheduledVisit.objects.get(patient=p, label="Month 1")
        # as_of inside the Month-1 window -> due; well after -> overdue.
        self.assertIn(m1, due_visits(as_of=m1.clinic_date))
        self.assertIn(m1, overdue_visits(as_of=m1.window_end + dt.timedelta(days=1)))

    def test_complete_visit_links_encounter(self):
        p = Patient.objects.create(patient_id="CMP1", name="c", sex="M")
        generate_schedule(p, dt.date(2026, 1, 5), horizon_months=1)
        visit = ScheduledVisit.objects.get(patient=p, label="Month 1")
        enc = ClinicalEncounter.objects.create(patient=p, encounter_date=visit.clinic_date)
        complete_visit(visit, enc)
        visit.refresh_from_db()
        self.assertEqual(visit.status, ScheduledVisit.Status.COMPLETED)
        self.assertEqual(visit.encounter, enc)
        # No longer due/overdue once completed.
        self.assertNotIn(visit, overdue_visits(as_of=dt.date(2030, 1, 1)))

    def test_roster_reports_capacity(self):
        p = Patient.objects.create(patient_id="ROST1", name="r", sex="M")
        created = generate_schedule(p, dt.date(2026, 1, 5), horizon_months=1)
        cd = created[0].clinic_date
        roster = clinic_roster(cd)
        self.assertEqual(roster["capacity"], 15)
        self.assertGreaterEqual(roster["booked"], 1)
        self.assertFalse(roster["over_capacity"])


class MonitoringTests(TestCase):
    def setUp(self):
        self.p = Patient.objects.create(patient_id="MON1", name="m", sex="M")
        self.cyc = DrugMaster.objects.create(
            generic_name="Cyclophosphamide", drug_class=DrugClass.CYCLOPHOSPHAMIDE)

    def test_no_monitoring_without_immunosuppression(self):
        self.assertFalse(is_on_active_immunosuppression(self.p))
        self.assertEqual(monitoring_requirements(self.p), [])

    def test_cyclophosphamide_monitoring(self):
        TreatmentExposure.objects.create(
            patient=self.p, drug=self.cyc, drug_name="Cyclophosphamide",
            start_date=dt.date(2026, 1, 1), ongoing=True)
        self.assertTrue(is_on_active_immunosuppression(self.p))
        reqs = monitoring_requirements(self.p)
        self.assertTrue(any("Urinalysis" in r["labs"] for r in reqs))
        self.assertTrue(any("nadir" in r["labs"] for r in reqs))
