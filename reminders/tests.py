from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from patients.models import Patient
from scheduling.models import ScheduledVisit

from .models import (
    ReminderSchedule, ReminderStatus, ReminderTemplate, ReminderType, ReminderChannel,
)
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


class ReminderPermissionTests(APITestCase):
    """The reminder endpoints replaced the project default
    (IsAuthenticated + DjangoModelPermissions) with authentication alone, so any
    logged-in account could read every patient's reminder history and fire an
    SMS/WhatsApp/email with an arbitrary body."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import Group, User
        from django.core.management import call_command
        from rest_framework.authtoken.models import Token
        call_command("seed_roles")
        cls._tokens = {}
        for username, role in (("rem_data", "data_manager"),
                               ("rem_readonly", "readonly")):
            u = User.objects.create_user(username, password="x")
            u.groups.add(Group.objects.get(name=role))
            cls._tokens[username] = Token.objects.get_or_create(user=u)[0].key
        # An account with no group membership at all.
        u = User.objects.create_user("rem_nobody", password="x")
        cls._tokens["rem_nobody"] = Token.objects.get_or_create(user=u)[0].key

    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="BGD-PERM-001", name="Perm Patient", phone="+8801700000000")
        self.reminder = ReminderSchedule.objects.create(
            patient=self.patient,
            reminder_type=ReminderType.GENERAL,
            channel=ReminderChannel.SMS,
            title="Lab reminder",
            message="Please attend the lab.",
            scheduled_at=timezone.now(),
        )

    def _auth(self, key):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {key}")

    def test_unauthenticated_cannot_read(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/reminders/").status_code, 401)

    def test_authenticated_user_without_a_group_cannot_write(self):
        # NOTE: DRF 3.15 dropped the `view_<model>` requirement — its
        # DjangoModelPermissions.perms_map has GET/HEAD/OPTIONS -> []. So reads
        # are open to any authenticated account project-wide, and only writes
        # are permission-gated. This test pins the write behaviour.
        self._auth(self._tokens["rem_nobody"])
        resp = self.client.post("/api/v1/reminders/", {
            "patient": self.patient.id,
            "reminder_type": "general",
            "channel": "sms",
            "title": "x",
            "message": "y",
            "scheduled_at": timezone.now().isoformat(),
        })
        self.assertEqual(resp.status_code, 403)

    def test_data_manager_can_create_a_reminder(self):
        self._auth(self._tokens["rem_data"])
        resp = self.client.post("/api/v1/reminders/", {
            "patient": self.patient.id,
            "reminder_type": "general",
            "channel": "sms",
            "title": "x",
            "message": "y",
            "scheduled_at": timezone.now().isoformat(),
        })
        self.assertEqual(resp.status_code, 201)

    def test_communication_preferences_cannot_be_rewritten_without_permission(self):
        from .models import PatientCommunicationPreference
        pref = PatientCommunicationPreference.objects.create(
            patient=self.patient, reminder_lab=True)
        url = f"/api/v1/comm-preferences/{pref.id}/"
        self._auth(self._tokens["rem_nobody"])
        self.assertEqual(self.client.patch(url, {"reminder_lab": False}).status_code, 403)
        self._auth(self._tokens["rem_readonly"])
        self.assertEqual(self.client.patch(url, {"reminder_lab": False}).status_code, 403)
        self._auth(self._tokens["rem_data"])
        self.assertEqual(self.client.patch(url, {"reminder_lab": False}).status_code, 200)
        pref.refresh_from_db()
        self.assertFalse(pref.reminder_lab)


class ReminderWebViewWritePermissionTests(TestCase):
    """``reminder_done`` / ``reminder_cancel`` mutate state from a GET link.

    They previously delegated to ``ReminderWritePermission.has_permission``,
    which short-circuits safe methods -- so any authenticated account could
    close out or cancel another clinician's reminder just by following the URL.
    """

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import Group, User
        from django.core.management import call_command
        call_command("seed_roles")
        cls.data_user = User.objects.create_user("remweb_data", password="x")
        cls.data_user.groups.add(Group.objects.get(name="data_manager"))
        cls.readonly_user = User.objects.create_user("remweb_readonly", password="x")
        cls.readonly_user.groups.add(Group.objects.get(name="readonly"))

    def setUp(self):
        self.patient = Patient.objects.create(
            patient_id="BGD-WEB-001", name="Web Patient", phone="+8801700000001")
        self.reminder = ReminderSchedule.objects.create(
            patient=self.patient,
            reminder_type=ReminderType.GENERAL,
            channel=ReminderChannel.APP,
            title="Bring records",
            message="Bring your records.",
            scheduled_at=timezone.now(),
        )

    def test_anonymous_is_redirected_to_login(self):
        resp = self.client.get(f"/reminders/log/{self.reminder.pk}/done/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp["Location"])

    def test_readonly_cannot_mark_a_reminder_done(self):
        self.client.force_login(self.readonly_user)
        resp = self.client.get(f"/reminders/log/{self.reminder.pk}/done/")
        self.assertEqual(resp.status_code, 403)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.status, ReminderStatus.PENDING)

    def test_readonly_cannot_cancel_a_reminder(self):
        self.client.force_login(self.readonly_user)
        resp = self.client.get(f"/reminders/log/{self.reminder.pk}/cancel/")
        self.assertEqual(resp.status_code, 403)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.status, ReminderStatus.PENDING)

    def test_permitted_user_can_mark_a_reminder_done(self):
        self.client.force_login(self.data_user)
        resp = self.client.get(f"/reminders/log/{self.reminder.pk}/done/")
        self.assertEqual(resp.status_code, 302)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.status, ReminderStatus.SENT)

    def test_permitted_user_can_cancel_a_reminder(self):
        self.client.force_login(self.data_user)
        resp = self.client.get(f"/reminders/log/{self.reminder.pk}/cancel/")
        self.assertEqual(resp.status_code, 302)
        self.reminder.refresh_from_db()
        self.assertEqual(self.reminder.status, ReminderStatus.CANCELLED)

    def test_readonly_cannot_log_a_reminder(self):
        self.client.force_login(self.readonly_user)
        resp = self.client.post("/reminders/log/", {
            "patient": self.patient.pk,
            "reminder_type": "general",
            "title": "x",
            "message": "y",
        })
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(ReminderSchedule.objects.count(), 1)

    def test_permitted_user_can_log_a_reminder(self):
        self.client.force_login(self.data_user)
        resp = self.client.post("/reminders/log/", {
            "patient": self.patient.pk,
            "reminder_type": "general",
            "title": "Call back",
            "message": "Ring the patient.",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(ReminderSchedule.objects.filter(title="Call back").exists())

