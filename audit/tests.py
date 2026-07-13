"""
Tests for the audit trail and consent versioning.
"""
import datetime as dt

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from patients.models import Patient

from .local import acting_as
from .models import AuditLog, Consent
from .recording import history_for
from .services.consent import (consent_history, current_consent, grant_consent,
                               has_consent, withdraw_consent)


class AuditTrailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("dr_rahman")

    def test_create_logs_a_create_row(self):
        p = Patient.objects.create(patient_id="A1", name="Anwar", sex="M")
        logs = history_for(p)
        self.assertEqual(logs.filter(action=AuditLog.Action.CREATE).count(), 1)

    def test_field_update_records_old_and_new_with_actor(self):
        p = Patient.objects.create(patient_id="A2", name="Old Name", sex="M")
        with acting_as(self.user, reason="name correction"):
            p.name = "Correct Name"
            p.save()
        row = history_for(p).get(action=AuditLog.Action.UPDATE, field_name="name")
        self.assertEqual(row.old_value, "Old Name")
        self.assertEqual(row.new_value, "Correct Name")
        self.assertEqual(row.changed_by, self.user)
        self.assertEqual(row.change_reason, "name correction")

    def test_unchanged_save_writes_no_update_row(self):
        p = Patient.objects.create(patient_id="A3", name="Stable", sex="F")
        before = history_for(p).filter(action=AuditLog.Action.UPDATE).count()
        p.save()   # no field changed
        after = history_for(p).filter(action=AuditLog.Action.UPDATE).count()
        self.assertEqual(before, after)

    def test_excluded_field_not_audited(self):
        # latest_egfr is excluded (it's a cache, refreshed by the labs engine).
        p = Patient.objects.create(patient_id="A4", name="Cache", sex="M")
        p.latest_egfr = 42
        p.save()
        self.assertFalse(history_for(p).filter(field_name="latest_egfr").exists())

    def test_delete_blocked_by_business_rule(self):
        p = Patient.objects.create(patient_id="A5", name="Gone", sex="M")
        pk = p.pk
        with self.assertRaises(PermissionDenied):
            p.delete()
        # Patient still exists in the database.
        self.assertTrue(Patient.objects.filter(pk=pk).exists())
        # Setting inactive generates an audit record.
        p.registration_status = "inactive"
        p.save()
        self.assertTrue(AuditLog.objects.filter(
            model_label="patients.Patient", object_pk=str(pk),
            action=AuditLog.Action.UPDATE, field_name="registration_status").exists())


class ConsentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("consenter")
        self.p = Patient.objects.create(patient_id="C1", name="Consent P", sex="F")

    def test_grant_sets_current_and_active(self):
        c = grant_consent(self.p, Consent.Type.REGISTRY, "BGDDR-ICF-v1.0",
                          consent_date=dt.date(2025, 1, 1), obtained_by=self.user)
        self.assertTrue(c.is_active)
        self.assertTrue(has_consent(self.p, Consent.Type.REGISTRY))

    def test_new_version_supersedes_previous(self):
        v1 = grant_consent(self.p, Consent.Type.REGISTRY, "v1.0",
                           consent_date=dt.date(2025, 1, 1))
        v2 = grant_consent(self.p, Consent.Type.REGISTRY, "v2.0",
                           consent_date=dt.date(2025, 6, 1))
        v1.refresh_from_db()
        self.assertFalse(v1.is_current)
        self.assertTrue(v2.is_current)
        self.assertEqual(v2.supersedes_id, v1.id)
        self.assertEqual(current_consent(self.p, Consent.Type.REGISTRY), v2)
        # Only one current consent of this type (DB constraint upheld).
        self.assertEqual(Consent.objects.filter(
            patient=self.p, consent_type=Consent.Type.REGISTRY,
            is_current=True).count(), 1)

    def test_withdrawal_revokes_access(self):
        grant_consent(self.p, Consent.Type.BIOBANK, "v1.0",
                      consent_date=dt.date(2025, 1, 1))
        self.assertTrue(has_consent(self.p, Consent.Type.BIOBANK))
        withdrawn = withdraw_consent(self.p, Consent.Type.BIOBANK,
                                     withdrawn_date=dt.date(2025, 8, 1))
        self.assertEqual(withdrawn.status, Consent.Status.WITHDRAWN)
        self.assertFalse(has_consent(self.p, Consent.Type.BIOBANK))

    def test_consent_changes_are_themselves_audited(self):
        c = grant_consent(self.p, Consent.Type.GENETIC, "v1.0",
                          consent_date=dt.date(2025, 1, 1))
        self.assertTrue(history_for(c).filter(
            action=AuditLog.Action.CREATE).exists())

    def test_history_lists_versions(self):
        grant_consent(self.p, Consent.Type.REGISTRY, "v1.0", consent_date=dt.date(2025, 1, 1))
        grant_consent(self.p, Consent.Type.REGISTRY, "v2.0", consent_date=dt.date(2025, 6, 1))
        self.assertEqual(consent_history(self.p, Consent.Type.REGISTRY).count(), 2)
