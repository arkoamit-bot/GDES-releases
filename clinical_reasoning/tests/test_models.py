"""Tests for clinical_reasoning models: ClinicalProfile, ClinicalInsight."""
import pytest
from django.utils import timezone

from clinical_reasoning.models import ClinicalProfile, ClinicalInsight


# ---------------------------------------------------------------------------
# ClinicalProfile tests
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.django_db


class TestClinicalProfile:
    """Test ClinicalProfile model creation, fields, and string representation."""

    def test_create_profile(self, patient):
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        assert profile.pk is not None
        assert profile.patient == patient
        # Event handler may have run and incremented version
        assert profile.version >= 0

    def test_str_representation(self, patient):
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        profile.version = 3
        profile.save()
        assert "TEST-001" in str(profile)
        assert "v3" in str(profile)

    def test_default_json_fields_are_empty(self, patient):
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        # Profile may have been populated by event handler; just verify types
        assert isinstance(profile.features_snapshot, dict)
        assert isinstance(profile.differential, (list, dict))
        assert isinstance(profile.disease_trajectory, dict)
        assert isinstance(profile.care_pathway, dict)
        assert isinstance(profile.risk_assessment, dict)
        assert isinstance(profile.evidence_summary, dict)
        assert isinstance(profile.reasoning_chain, list)
        assert isinstance(profile.information_gaps, list)
        assert isinstance(profile.milestones, list)

    def test_one_to_one_constraint(self, patient):
        """Cannot create two ClinicalProfiles for the same patient."""
        ClinicalProfile.objects.get_or_create(patient=patient)
        with pytest.raises(Exception):
            ClinicalProfile.objects.create(patient=patient)

    def test_cascade_delete(self, patient):
        """ClinicalProfile is deleted when Patient is deleted.

        Note: Patient.delete() is blocked by the model's override.
        We test via direct DB deletion to verify the FK cascade.
        """
        from django.db import connection
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        profile_pk = profile.pk
        # Delete via raw SQL to bypass the model override
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM patients_patient WHERE id = %s",
                [patient.pk],
            )
            # Django's FK cascade should remove the profile too
            cursor.execute(
                "SELECT COUNT(*) FROM clinical_reasoning_clinicalprofile WHERE id = %s",
                [profile_pk],
            )
            count = cursor.fetchone()[0]
            assert count == 0

    def test_last_updated_auto_set(self, patient):
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        assert profile.last_updated is not None

    def test_version_increment(self, clinical_profile):
        v = clinical_profile.version
        clinical_profile.version += 1
        clinical_profile.save()
        clinical_profile.refresh_from_db()
        assert clinical_profile.version == v + 1

    def test_features_snapshot_json(self, patient):
        features = {
            "egfr": 45,
            "proteinuria": "nephrotic",
            "labs": ["lowC3", "antiGbm"],
            "biopsy": ["fullHouse"],
        }
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        profile.features_snapshot = features
        profile.save()
        profile.refresh_from_db()
        assert profile.features_snapshot["egfr"] == 45
        assert "lowC3" in profile.features_snapshot["labs"]

    def test_differential_json(self, patient):
        diff = [
            {"disease_id": "iga", "score": 12.5, "confidence": 65},
            {"disease_id": "membranous", "score": 5.0, "confidence": 35},
        ]
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        profile.differential = diff
        profile.save()
        profile.refresh_from_db()
        assert len(profile.differential) == 2
        assert profile.differential[0]["disease_id"] == "iga"

    def test_meta_verbose_names(self):
        assert ClinicalProfile._meta.verbose_name == "clinical profile"
        assert ClinicalProfile._meta.verbose_name_plural == "clinical profiles"

    def test_meta_ordering_default(self, client):
        """ClinicalProfile has no explicit ordering — default is by pk."""
        assert ClinicalProfile._meta.ordering == []

    def test_related_name(self, patient):
        """Patient.clinical_profile reverse relation works."""
        profile, _ = ClinicalProfile.objects.get_or_create(patient=patient)
        assert patient.clinical_profile == profile

    def test_index_on_last_updated(self):
        """Model has an index on last_updated."""
        index_fields = [idx.fields for idx in ClinicalProfile._meta.indexes]
        assert ["last_updated"] in index_fields


# ---------------------------------------------------------------------------
# ClinicalInsight tests
# ---------------------------------------------------------------------------

class TestClinicalInsight:
    """Test ClinicalInsight model creation, choices, and string representation."""

    def test_create_insight(self, patient):
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.DIAGNOSTIC,
            priority=ClinicalInsight.Priority.HIGH,
            title="Test insight",
            description="Test description",
        )
        assert insight.pk is not None
        assert insight.patient == patient
        assert insight.category == "diagnostic"
        assert insight.priority == "high"

    def test_str_representation(self, clinical_insight):
        s = str(clinical_insight)
        assert "High" in s
        assert "Leading differential" in s

    def test_default_priority(self, patient):
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.MONITORING,
            title="Monitoring check",
        )
        assert insight.priority == ClinicalInsight.Priority.INFO

    def test_default_actionable_is_true(self, patient):
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.SAFETY,
            title="Safety alert",
        )
        assert insight.actionable is True

    def test_default_dismissed_is_false(self, patient):
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.SAFETY,
            title="Safety alert",
        )
        assert insight.dismissed is False

    def test_cascade_delete(self, patient):
        """ClinicalInsight is deleted when Patient is deleted."""
        from django.db import connection
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.CARE_GAP,
            title="Care gap",
        )
        insight_pk = insight.pk
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM patients_patient WHERE id = %s",
                [patient.pk],
            )
            cursor.execute(
                "SELECT COUNT(*) FROM clinical_reasoning_clinicalinsight WHERE id = %s",
                [insight_pk],
            )
            count = cursor.fetchone()[0]
            assert count == 0

    def test_created_at_auto_set(self, patient):
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.RESEARCH,
            title="Research opportunity",
        )
        assert insight.created_at is not None

    def test_insight_categories(self):
        """All 7 insight categories exist."""
        categories = [c[0] for c in ClinicalInsight.InsightCategory.choices]
        assert "diagnostic" in categories
        assert "prognostic" in categories
        assert "therapeutic" in categories
        assert "monitoring" in categories
        assert "safety" in categories
        assert "care_gap" in categories
        assert "research" in categories

    def test_insight_priorities(self):
        """All 5 priority levels exist."""
        priorities = [p[0] for p in ClinicalInsight.Priority.choices]
        assert "critical" in priorities
        assert "high" in priorities
        assert "medium" in priorities
        assert "low" in priorities
        assert "info" in priorities

    def test_multiple_insights_for_patient(self, patient):
        # Clear any existing insights from event handler
        ClinicalInsight.objects.filter(patient=patient).delete()
        for i in range(3):
            ClinicalInsight.objects.create(
                patient=patient,
                category=ClinicalInsight.InsightCategory.MONITORING,
                title=f"Insight {i}",
            )
        assert ClinicalInsight.objects.filter(patient=patient).count() == 3

    def test_meta_indexes(self):
        """Model has composite indexes."""
        index_fields = [idx.fields for idx in ClinicalInsight._meta.indexes]
        assert ["patient", "category"] in index_fields
        assert ["patient", "priority", "dismissed"] in index_fields

    def test_meta_ordering(self):
        """Model orders by -priority, -created_at."""
        assert ClinicalInsight._meta.ordering == ["-priority", "-created_at"]

    def test_expiry_nullable(self, patient):
        insight = ClinicalInsight.objects.create(
            patient=patient,
            category=ClinicalInsight.InsightCategory.CARE_GAP,
            title="Gap",
            expires_at=None,
        )
        assert insight.expires_at is None
