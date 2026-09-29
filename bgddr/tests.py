"""
Tests for the dashboard views and the health-check endpoint.

The dashboard used to be the unauthenticated landing page at ``/``. It renders
registry census, cohort and demographic breakdowns, outcome aggregates and the
follow-up worklist, so it must require a login, and in a multi-center registry
it must respect site scoping.
"""
import json

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase

from patients.models import Patient, Site, UserSiteRole


DASHBOARD_URLS = [
    "/",
    "/dashboard/partials/overview-stats/",
    "/dashboard/partials/worklist/",
    "/dashboard/partials/enrollment-summary/",
    "/dashboard/partials/cohort-breakdown/",
    "/dashboard/partials/enrollment-trend/",
    "/dashboard/partials/demographics/",
    "/dashboard/partials/outcomes-summary/",
    "/dashboard/partials/compliance/",
    "/dashboard/enrollment/",
    "/dashboard/outcomes/",
    "/dashboard/compliance/",
]


class DashboardRequiresLoginTests(TestCase):
    def test_anonymous_is_redirected_for_every_dashboard_url(self):
        for url in DASHBOARD_URLS:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 302, f"{url} was not protected")
                self.assertIn("/login/", resp["Location"])


class HealthCheckTests(TestCase):
    def test_anonymous_probe_gets_ok_without_patient_count(self):
        resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.content)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["database"], "ok")
        # Anonymous callers must not learn the registry census.
        self.assertIsNone(body["patient_count"])

    def test_staff_probe_includes_patient_count(self):
        call_command("seed_roles")
        u = User.objects.create_user("probe_staff", password="x", is_staff=True)
        u.groups.add(Group.objects.get(name="data_manager"))
        Patient.objects.create(patient_id="HC-1", name="a", sex="F")
        self.client.force_login(u)
        body = json.loads(self.client.get("/health/").content)
        self.assertEqual(body["patient_count"], 1)


class DashboardSiteScopingTests(TestCase):
    def setUp(self):
        call_command("seed_roles")
        self.site_a = Site.objects.create(code="DA", name="Site A")
        self.site_b = Site.objects.create(code="DB", name="Site B")
        Patient.objects.create(patient_id="DA-1", name="a", sex="F", site=self.site_a)
        Patient.objects.create(patient_id="DB-1", name="b", sex="M", site=self.site_b)
        Patient.objects.create(patient_id="DB-2", name="b2", sex="F", site=self.site_b)

        self.coord = User.objects.create_user("dash_coord", password="x")
        self.coord.groups.add(Group.objects.get(name="coordinator"))
        UserSiteRole.objects.create(
            user=self.coord, site=self.site_a, role=UserSiteRole.Role.SITE_COORDINATOR)

    def test_coordinator_dashboard_counts_only_their_site(self):
        self.client.force_login(self.coord)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["total_patients"], 1)
        self.assertEqual(resp.context["active_patients"], 1)

    def test_data_manager_dashboard_sees_every_site(self):
        dm = User.objects.create_user("dash_dm", password="x")
        dm.groups.add(Group.objects.get(name="data_manager"))
        self.client.force_login(dm)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["total_patients"], 3)

    def test_enrollment_summary_partial_is_scoped(self):
        self.client.force_login(self.coord)
        resp = self.client.get("/dashboard/partials/enrollment-summary/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["data"]["total"], 1)

    def test_single_site_dashboard_still_works_without_site_roles(self):
        # The desktop pilot has no UserSiteRole rows at all; with a single site
        # there is nothing to scope, so the dashboard must not be empty.
        Patient.objects.update(site=None)
        self.site_b.delete()
        u = User.objects.create_user("dash_solo", password="x")
        u.groups.add(Group.objects.get(name="coordinator"))
        self.client.force_login(u)
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["total_patients"], 3)
