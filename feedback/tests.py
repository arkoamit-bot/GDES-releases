from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import (
    ErrorLog, ClinicalConflict, KnowledgeConflict, AIFailureLog,
    RuleFailureLog, UserFeedback, WorkflowFeedback, PerformanceLog,
)


class FeedbackModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="testpass123")

    def test_error_log_creation(self):
        log = ErrorLog.objects.create(
            error_type="ValueError", severity="error", module="test"
        )
        self.assertIn("[error] ValueError", str(log))

    def test_clinical_conflict_creation(self):
        conflict = ClinicalConflict.objects.create(
            disease="iga", ai_recommendation="RAS inhibitor",
            clinician_decision="SGLT2 inhibitor", ai_confidence=0.75,
        )
        self.assertFalse(conflict.resolved)
        self.assertIn("Conflict: iga", str(conflict))

    def test_knowledge_conflict(self):
        kc = KnowledgeConflict.objects.create(
            conflict_type="drug_contraindication", severity="high",
            description="ACEi contraindicated in pregnancy",
        )
        self.assertEqual(kc.get_conflict_type_display(), "Drug Contraindication")

    def test_ai_failure_log(self):
        failure = AIFailureLog.objects.create(
            failure_type="diagnosis", confidence=0.3,
            missing_data={"egfr": "not available"},
        )
        self.assertIn("AI Failure: Diagnosis", str(failure))

    def test_rule_failure_log(self):
        rfl = RuleFailureLog.objects.create(
            rule_id="KB-IGA-001", disease="iga",
            condition=[{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
        )
        self.assertEqual(str(rfl), "Rule Failure: KB-IGA-001")

    def test_user_feedback(self):
        fb = UserFeedback.objects.create(
            user=self.user, feedback_type="suggestion",
            title="Add MCD protocol",
        )
        self.assertEqual(str(fb), "[Suggestion] Add MCD protocol")

    def test_workflow_feedback(self):
        wf = WorkflowFeedback.objects.create(
            user=self.user, feedback_type="treatment_plan", rating=4,
        )
        self.assertEqual(str(wf), "Treatment Plans: 4 stars")

    def test_performance_log(self):
        pl = PerformanceLog.objects.create(
            metric_name="slow_page", duration_ms=3500, module="dashboard"
        )
        self.assertIn("Slow Page Load: 3500ms", str(pl))


class FeedbackViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", password="testpass123")
        self.admin = User.objects.create_superuser("admin", "admin@test.com", "admin123")
        self.client = Client()

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("feedback:feedback_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("feedback:feedback_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Field Feedback Dashboard")

    def test_report_problem_get(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("feedback:report_problem"))
        self.assertEqual(response.status_code, 200)

    def test_report_problem_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("feedback:report_problem"), {
            "feedback_type": "software_bug",
            "title": "Test bug report",
            "description": "Something broke",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(UserFeedback.objects.count(), 1)

    def test_workflow_feedback_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("feedback:workflow_feedback"), {
            "feedback_type": "diagnosis",
            "rating": 4,
            "comments": "Good suggestions",
        })
        self.assertEqual(response.status_code, 302)

    def test_api_clinical_conflict(self):
        self.client.force_login(self.admin)
        response = self.client.post("/api/v1/feedback/report-conflict/", {
            "disease": "iga",
            "ai_recommendation": "RASi",
            "clinician_decision": "SGLT2i",
            "ai_confidence": 0.7,
        }, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_api_user_feedback_create(self):
        self.client.force_login(self.admin)
        response = self.client.post("/api/v1/feedback/feedback/", {
            "feedback_type": "suggestion",
            "title": "API test",
        }, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["feedback_type"], "suggestion")

    def test_export_requires_admin(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/v1/feedback/export-package/")
        self.assertEqual(response.status_code, 403)

    def test_export_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get("/api/v1/feedback/export-package/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

    def test_summary_report_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get("/api/v1/feedback/summary-report/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("app_version", response.json())

    def test_workflow_feedback_api(self):
        self.client.force_login(self.admin)
        response = self.client.post("/api/v1/feedback/submit-workflow-feedback/", {
            "feedback_type": "treatment_plan", "rating": 5,
        }, content_type="application/json")
        self.assertEqual(response.status_code, 201)

    def test_conflict_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("feedback:conflict_list"))
        self.assertEqual(response.status_code, 200)
