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

    def test_siteless_patient_does_not_500_the_list_endpoint(self):
        # `site` is nullable; the `site.code` traversal used to raise
        # AttributeError and take down the whole endpoint for every patient.
        from patients.models import Site
        site = Site.objects.create(code="S1", name="Site One")
        Patient.objects.create(patient_id="R-OK", name="with site", sex="M", site=site)
        Patient.objects.create(patient_id="R-NONE", name="no site", sex="M")

        self._auth(self._user("ro-null", "readonly"))
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)
        by_id = {r["patient_id"]: r for r in resp.data["results"]}
        self.assertEqual(by_id["R-OK"]["site_code"], "S1")
        self.assertIsNone(by_id["R-NONE"]["site_code"])

    def test_siteless_patient_detail_does_not_500(self):
        p = Patient.objects.create(patient_id="R-DET", name="no site", sex="M")
        self._auth(self._user("ro-null2", "readonly"))
        resp = self.client.get(f"/api/v1/patients/{p.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.data["site_code"])


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


class SiteScopingTests(RBACTestBase):
    """Multi-center scoping.

    With a single site there is nothing to scope, so the desktop pilot keeps
    working with no UserSiteRole rows at all. Once a second site exists, an
    account without a site assignment must NOT inherit the whole registry --
    that used to return every site's patients.
    """

    def setUp(self):
        from patients.models import Site
        self.site_a = Site.objects.create(code="SA", name="Site A")
        self.site_b = Site.objects.create(code="SB", name="Site B")
        self.pat_a = Patient.objects.create(
            patient_id="SA-1", name="a", sex="F", site=self.site_a)
        self.pat_b = Patient.objects.create(
            patient_id="SB-1", name="b", sex="M", site=self.site_b)

    def _assign(self, user, site, role="site_coordinator"):
        from patients.models import UserSiteRole
        UserSiteRole.objects.create(user=user, site=site, role=role)

    def test_user_with_no_site_assignment_sees_nothing(self):
        u = self._user("unassigned", "readonly")
        self._auth(u)
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 403)
        self.assertIn("not assigned to any site", str(resp.data).lower())

    def test_user_with_no_site_assignment_gets_empty_queryset(self):
        # The queryset itself must be fail-closed too, not just the permission.
        from django.test import RequestFactory

        from api.permissions import site_filter_kwargs
        from patients.models import Patient as P
        u = self._user("unassigned2", "readonly")
        request = RequestFactory().get("/")
        request.user = u
        kwargs = site_filter_kwargs(request, P)
        self.assertTrue(kwargs, "unassigned user must receive a restrictive filter")
        self.assertEqual(P.objects.filter(**kwargs).count(), 0)

    def test_site_coordinator_sees_only_their_site(self):
        u = self._user("coordA", "coordinator")
        self._assign(u, self.site_a)
        self._auth(u)
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["patient_id"], "SA-1")

    def test_site_coordinator_cannot_read_another_sites_patient_detail(self):
        u = self._user("coordB", "coordinator")
        self._assign(u, self.site_a)
        self._auth(u)
        resp = self.client.get(f"/api/v1/patients/{self.pat_b.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_data_manager_still_sees_every_site(self):
        self._auth(self._user("dm-multi", "data_manager"))
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_superuser_still_sees_every_site(self):
        su = User.objects.create_superuser("su-multi", "a@b.c", "x")
        self._auth(su)
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_single_site_registry_stays_unrestricted(self):
        from django.test import RequestFactory

        from api.permissions import site_filter_kwargs
        from patients.models import Patient as P, Site as S
        P.objects.update(site=None)
        S.objects.all().delete()
        u = self._user("solo", "readonly")
        request = RequestFactory().get("/")
        request.user = u
        self.assertEqual(site_filter_kwargs(request, P), {})

    def test_single_site_user_without_role_can_still_list(self):
        from patients.models import Site as S
        self.pat_b.site = None
        self.pat_b.save()
        self.site_b.delete()
        self._auth(self._user("solo2", "readonly"))
        resp = self.client.get("/api/v1/patients/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)


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
