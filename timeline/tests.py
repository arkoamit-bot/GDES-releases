from datetime import date, datetime
from django.test import TestCase
from django.utils import timezone
from patients.models import Patient
from .models import TimelineEvent
from .services import record_event, get_patient_timeline, rebuild_patient_timeline
from encounters.models import ClinicalEncounter


class TimelineTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            name="Timeline Test", sex="F",
            dob=date(1990, 1, 1),
        )

    def test_record_event(self):
        event = record_event(
            patient=self.patient,
            domain="patient",
            event_type="patient.registered",
            event_date=timezone.now(),
            summary="Test event",
        )
        self.assertEqual(event.summary, "Test event")

    def test_get_timeline(self):
        record_event(self.patient, "lab", "lab.result", timezone.now(), "Lab result")
        timeline = get_patient_timeline(self.patient)
        self.assertEqual(len(timeline), 1)

    def test_rebuild_timeline(self):
        ClinicalEncounter.objects.create(
            patient=self.patient, encounter_date=date.today(),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP,
        )
        events = rebuild_patient_timeline(self.patient)
        self.assertGreater(len(events), 0)
