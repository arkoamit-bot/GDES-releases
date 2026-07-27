"""Tests for feedback analytics and continuous improvement (Sprint 6)."""
import pytest
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from feedback.analytics import (
    override_rate_by_disease,
    override_rate_by_rule,
    override_rate_by_clinician,
    temporal_override_trend,
    overall_override_rate,
    suggestion_lifecycle_stats,
    pending_suggestions_for_review,
    patient_override_context,
)
from feedback.models import WorkflowFeedback, KnowledgeImprovementSuggestion
from feedback.services import generate_improvement_suggestions

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testdoc", password="testpass123")


@pytest.fixture
def patient(db):
    from patients.models import Patient
    return Patient.objects.create(
        patient_id="TEST-001",
        name="Test Patient",
        sex="M",
        dob="1980-01-01",
    )


@pytest.fixture
def feedback_factory(db, user, patient):
    def _create(action="accept", feedback_type="clinical_reasoning",
                recommendation_ref="", comments="", days_ago=0):
        return WorkflowFeedback.objects.create(
            user=user,
            patient=patient,
            feedback_type=feedback_type,
            action=action,
            rating={"accept": 5, "modify": 3, "reject": 1}.get(action, 0),
            recommendation_ref=recommendation_ref,
            comments=comments,
            created_at=timezone.now() - timedelta(days=days_ago),
        )
    return _create


@pytest.mark.django_db
class TestOverrideRateByDisease:
    def test_empty(self):
        result = override_rate_by_disease()
        assert result == []

    def test_with_feedback(self, feedback_factory):
        feedback_factory(action="accept")
        feedback_factory(action="accept")
        feedback_factory(action="modify")
        feedback_factory(action="reject")

        result = override_rate_by_disease()
        assert len(result) == 1
        r = result[0]
        assert r["total"] == 4
        assert r["accepted"] == 2
        assert r["modified"] == 1
        assert r["rejected"] == 1
        assert r["override_rate"] == 50.0

    def test_only_recent(self, feedback_factory):
        feedback_factory(action="reject", days_ago=100)
        feedback_factory(action="accept", days_ago=5)

        result = override_rate_by_disease(days=30)
        assert len(result) == 1
        assert result[0]["total"] == 1
        assert result[0]["accepted"] == 1


@pytest.mark.django_db
class TestOverrideRateByRule:
    def test_empty(self):
        result = override_rate_by_rule()
        assert result == []

    def test_groups_by_ref(self, feedback_factory):
        feedback_factory(action="reject", recommendation_ref="differential:iga")
        feedback_factory(action="modify", recommendation_ref="differential:iga")
        feedback_factory(action="accept", recommendation_ref="differential:iga")
        feedback_factory(action="accept", recommendation_ref="differential:membranous")

        result = override_rate_by_rule()
        assert len(result) == 1  # membranous has only 1 feedback (<2 threshold)
        assert result[0]["recommendation_ref"] == "differential:iga"
        assert result[0]["total"] == 3
        assert result[0]["override_rate"] == 66.7


@pytest.mark.django_db
class TestOverrideRateByClinician:
    def test_empty(self):
        result = override_rate_by_clinician()
        assert result == []

    def test_with_user(self, feedback_factory, user):
        feedback_factory(action="reject")
        feedback_factory(action="accept")

        result = override_rate_by_clinician()
        assert len(result) == 1
        assert result[0]["clinician"] == "testdoc"
        assert result[0]["total"] == 2


@pytest.mark.django_db
class TestTemporalTrend:
    def test_empty(self):
        result = temporal_override_trend()
        assert result == []

    def test_groups_by_week(self, feedback_factory):
        feedback_factory(action="reject", days_ago=3)
        feedback_factory(action="accept", days_ago=3)
        feedback_factory(action="modify", days_ago=10)

        result = temporal_override_trend(days=30, bucket="week")
        assert len(result) >= 1
        total = sum(r["total"] for r in result)
        assert total == 3


@pytest.mark.django_db
class TestOverallOverrideRate:
    def test_empty(self):
        result = overall_override_rate()
        assert result["total"] == 0
        assert result["overrides"] == 0
        assert result["override_rate"] == 0

    def test_with_feedback(self, feedback_factory):
        feedback_factory(action="reject")
        feedback_factory(action="modify")
        feedback_factory(action="accept")

        result = overall_override_rate()
        assert result["total"] == 3
        assert result["overrides"] == 2
        assert result["override_rate"] == 66.7


@pytest.mark.django_db
class TestSuggestionLifecycleStats:
    def test_empty(self):
        result = suggestion_lifecycle_stats()
        assert result["total"] == 0

    def test_with_suggestions(self, db):
        KnowledgeImprovementSuggestion.objects.create(
            rule_id="KB-001", disease="iga", status="pending", override_count=3)
        KnowledgeImprovementSuggestion.objects.create(
            rule_id="KB-002", disease="membranous", status="approved", override_count=5)

        result = suggestion_lifecycle_stats()
        assert result["pending"] == 1
        assert result["approved"] == 1
        assert result["total"] == 2


@pytest.mark.django_db
class TestPendingSuggestions:
    def test_empty(self):
        result = pending_suggestions_for_review()
        assert result == []

    def test_returns_top_by_override_count(self, db):
        for i in range(5):
            KnowledgeImprovementSuggestion.objects.create(
                rule_id=f"KB-{i:03d}", disease="iga",
                status="pending", override_count=10 - i)

        result = pending_suggestions_for_review(limit=3)
        assert len(result) == 3
        assert result[0].override_count >= result[1].override_count


@pytest.mark.django_db
class TestPatientOverrideContext:
    def test_empty(self, patient):
        result = patient_override_context(patient)
        assert result["local_total"] == 0
        assert result["local_overrides"] == 0
        assert result["local_override_rate"] is None

    def test_with_feedback(self, patient, feedback_factory):
        feedback_factory(action="reject")
        feedback_factory(action="accept")

        result = patient_override_context(patient)
        assert result["local_total"] == 2
        assert result["local_overrides"] == 1
        assert result["local_override_rate"] == 50.0


@pytest.mark.django_db
class TestGenerateImprovementSuggestionsWorkflowFeedback:
    def test_creates_suggestion_from_workflow_overrides(self, feedback_factory):
        for i in range(4):
            feedback_factory(
                action="reject",
                recommendation_ref="differential:iga",
                comments="Wrong diagnosis" if i % 2 == 0 else " guideline outdated",
            )

        suggestions = generate_improvement_suggestions()
        wf_suggestions = [s for s in suggestions if s.rule_id == "differential:iga"]
        assert len(wf_suggestions) == 1
        assert wf_suggestions[0].override_count >= 3

    def test_does_not_create_below_threshold(self, feedback_factory):
        for i in range(2):
            feedback_factory(
                action="modify",
                recommendation_ref="differential:membranous",
            )

        suggestions = generate_improvement_suggestions()
        wf_suggestions = [s for s in suggestions if "membranous" in s.rule_id]
        assert len(wf_suggestions) == 0

    def test_idempotent(self, feedback_factory):
        for i in range(4):
            feedback_factory(action="reject", recommendation_ref="differential:iga")

        s1 = generate_improvement_suggestions()
        s2 = generate_improvement_suggestions()
        assert len(s1) == len(s2)
        assert KnowledgeImprovementSuggestion.objects.filter(
            rule_id="differential:iga").count() == 1
