from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from patients.models import Patient
from scheduling.models import ScheduledVisit

from .models import ReminderSchedule, ReminderTemplate, ReminderType, ReminderChannel
from .tasks import schedule_visit_reminders, send_due_visit_reminders


class ReminderModelTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="BGD-TEST-001",
            name="Test Patient",
            phone="+8801712345678",
        )

    def test_create_reminder_schedule(self):
        reminder = ReminderSchedule.objects.create(
            patient=self.patient,
            reminder_type=ReminderType.FOLLOW_UP,
            channel=ReminderChannel.SMS,
            title="Test reminder",
            message="Test message",
            scheduled_at=timezone.now(),
        )
        self.assertEqual(reminder.status, "pending")
        self.assertEqual(str(reminder), f"Follow-up visit reminder for BGD-TEST-001 @ {reminder.scheduled_at}")

    def test_create_template(self):
        template = ReminderTemplate.objects.create(
            reminder_type=ReminderType.FOLLOW_UP,
            channel=ReminderChannel.SMS,
            name="default_follow_up",
            template_body="Dear {{patient_name}}, please attend clinic on {{visit_date}}.",
        )
        self.assertTrue(template.is_active)

    def test_cancel_reminder(self):
        reminder = ReminderSchedule.objects.create(
            patient=self.patient,
            reminder_type=ReminderType.FOLLOW_UP,
            channel=ReminderChannel.SMS,
            title="Cancel test",
            message="Test",
            scheduled_at=timezone.now(),
        )
        reminder.status = "cancelled"
        reminder.save()
        self.assertEqual(reminder.status, "cancelled")


class ReminderTaskTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="BGD-TEST-002",
            name="Task Test Patient",
            phone="+8801712345678",
        )

    @patch("reminders.tasks.send_sms")
    def test_schedule_visit_reminders(self, mock_sms):
        mock_sms.return_value = True

        visit = ScheduledVisit.objects.create(
            patient=self.patient,
            kind=ScheduledVisit.Kind.ROUTINE,
            label="Month 3",
            target_date=date.today() + timedelta(days=3),
            window_start=date.today() + timedelta(days=1),
            window_end=date.today() + timedelta(days=7),
            status=ScheduledVisit.Status.SCHEDULED,
        )

        result = schedule_visit_reminders()
        self.assertEqual(result["created"], 1)

        reminder = ReminderSchedule.objects.get(patient=self.patient)
        self.assertEqual(reminder.scheduled_visit, visit)
        self.assertEqual(reminder.reminder_type, ReminderType.FOLLOW_UP)
