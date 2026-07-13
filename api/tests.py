"""
Tests for the REST API and role-based access control.
"""
import datetime as dt

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from patients.models import Patient


class RBACTestBase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_roles")

    def _user(self, username, role=None):
        u = User.objects.create_user(username, password="x")
        if role:
            u.groups.add(Group.objects.get(name=role))
        return u

    def _auth(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


class AuthTests(RBACTestBase):
    def test_unauthenticated_is_rejected(self):
        self.client.credentials()
        self.assertEqual(self.client.get("/api/v1/patients/").status_code, 401)

    def test_token_obtain(self):
        self._user("tok", "readonly")
        resp = self.client.post("/api/v1/auth/token/",
                                {"username": "tok", "password": "x"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.data)


class ReadAccessTests(RBACTestBase):
    def test_any_authenticated_user_can_read(self):
        Patient.objects.create(patient_id="R1", name="r", sex="M")
        self._auth(self._user("ro", "readonly"))
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)


class WriteRBACTests(RBACTestBase):
    PATIENT = {"patient_id": "W1", "name": "w", "sex": "M"}

    def test_readonly_cannot_write(self):
        self._auth(self._user("ro2", "readonly"))
        self.assertEqual(self.client.post("/api/v1/patients/", self.PATIENT).status_code, 403)

    def test_statistician_cannot_write(self):
        self._auth(self._user("stat", "statistician"))
        self.assertEqual(self.client.post("/api/v1/patients/", self.PATIENT).status_code, 403)

    def test_data_manager_can_create_patient(self):
        self._auth(self._user("dm", "data_manager"))
        self.assertEqual(self.client.post("/api/v1/patients/", self.PATIENT).status_code, 201)

    def test_coordinator_can_create_patient(self):
        self._auth(self._user("coord", "coordinator"))
        self.assertEqual(self.client.post("/api/v1/patients/", self.PATIENT).status_code, 201)

    def test_investigator_cannot_create_patient_but_can_log_ae(self):
        inv = self._user("inv", "investigator")
        self._auth(inv)
        # No add_patient permission.
        self.assertEqual(self.client.post("/api/v1/patients/", self.PATIENT).status_code, 403)
        # But can log an adverse event.
        p = Patient.objects.create(patient_id="W2", name="w2", sex="M")
        ae = {"patient": p.id, "onset_date": "2026-01-01", "category": "infection",
              "severity": "moderate"}
        self.assertEqual(self.client.post("/api/v1/adverse-events/", ae).status_code, 201)

    def test_pathologist_separation(self):
        path_u = self._user("path", "pathologist")
        self._auth(path_u)
        self.assertEqual(self.client.post("/api/v1/patients/", self.PATIENT).status_code, 403)
        p = Patient.objects.create(patient_id="W3", name="w3", sex="M")
        from pathology.models import Biopsy
        b = Biopsy.objects.create(patient=p, biopsy_date=dt.date(2026, 1, 1))
        review = {"biopsy": b.id, "role": "local", "diagnosis": "IgA nephropathy"}
        self.assertEqual(self.client.post("/api/v1/pathology-reviews/", review).status_code, 201)


class ApiAuditAttributionTests(RBACTestBase):
    def test_api_write_is_attributed_in_audit_trail(self):
        dm = self._user("dm2", "data_manager")
        self._auth(dm)
        resp = self.client.post("/api/v1/patients/",
                                {"patient_id": "AUD1", "name": "n", "sex": "M"})
        self.assertEqual(resp.status_code, 201)
        from audit.models import AuditLog
        row = AuditLog.objects.filter(model_label="patients.Patient",
                                      action=AuditLog.Action.CREATE).latest("changed_at")
        self.assertEqual(row.changed_by, dm)
