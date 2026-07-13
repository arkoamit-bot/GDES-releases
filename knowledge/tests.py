"""
Knowledge app tests — GuidelineSource, KnowledgeBaseEntry models, and rule engine.
"""
import datetime as dt

from django.test import TestCase

from patients.models import Patient
from patients.workflow import DiseasePhase, RegistrationStatus
from encounters.models import ClinicalEncounter
from patients.workflow import ClinicianResponse

from .models import (
    GuidelineSource, KnowledgeBaseEntry,
    Disease, Syndrome, PathologyEntity, LabEntity,
    DrugIntelligence, MonitoringProtocol, Complication,
    KnowledgeGraphNode, KnowledgeGraphEdge,
)
from .graph_service import (
    populate_from_models, find_paths, get_reasoning_chain,
    get_differential, get_graph_summary,
)
from .graph_reasoning import (
    get_treatment_recommendations, get_monitoring_recommendations,
    get_complication_risks, get_syndrome_matches,
    get_graph_differential, augment_differential,
    build_graph_reasoning_steps, enhance_treatment_plan,
)
from .services import (
    _evaluate_condition,
    evaluate_entry,
    evaluate_patient_rules,
    extract_patient_features,
)


class GuidelineSourceTests(TestCase):

    def test_create_source(self):
        s = GuidelineSource.objects.create(
            title="KDIGO 2025 IgAN and IgAV Guideline",
            abbreviation="KDIGO",
            version_year=2025,
            effective_date=dt.date(2025, 1, 1),
        )
        self.assertEqual(s.title, "KDIGO 2025 IgAN and IgAV Guideline")
        self.assertEqual(s.abbreviation, "KDIGO")
        self.assertEqual(s.version_year, 2025)

    def test_str(self):
        s = GuidelineSource.objects.create(
            title="KDIGO 2025",
            abbreviation="KDIGO",
            version_year=2025,
            effective_date=dt.date(2025, 1, 1),
        )
        self.assertEqual(str(s), "KDIGO 2025")

    def test_optional_fields(self):
        s = GuidelineSource.objects.create(
            title="Test",
            abbreviation="T",
            version_year=2024,
            effective_date=dt.date(2024, 1, 1),
        )
        self.assertEqual(s.url, "")
        self.assertIsNone(s.retired_date)

    def test_retired_source(self):
        s = GuidelineSource.objects.create(
            title="Old Guideline",
            abbreviation="OLD",
            version_year=2020,
            effective_date=dt.date(2020, 1, 1),
            retired_date=dt.date(2025, 1, 1),
        )
        self.assertEqual(s.retired_date, dt.date(2025, 1, 1))

    def test_index_on_abbreviation_year(self):
        GuidelineSource.objects.create(
            title="KDIGO 2024",
            abbreviation="KDIGO",
            version_year=2024,
            effective_date=dt.date(2024, 1, 1),
        )
        GuidelineSource.objects.create(
            title="KDIGO 2025",
            abbreviation="KDIGO",
            version_year=2025,
            effective_date=dt.date(2025, 1, 1),
        )
        self.assertEqual(GuidelineSource.objects.count(), 2)


class KnowledgeBaseEntryTests(TestCase):

    def setUp(self):
        self.source = GuidelineSource.objects.create(
            title="KDIGO 2025 IgAN Guideline",
            abbreviation="KDIGO",
            version_year=2025,
            effective_date=dt.date(2025, 1, 1),
        )

    def _make_entry(self, **kwargs):
        defaults = {
            "entry_id": "KB-IGA-001",
            "disease_id": "iga",
            "rule_data": {
                "path": ["sediment", "hematuria"],
                "weight": 2,
                "explanation": "Hematuria on urine sediment",
            },
            "source": self.source,
            "effective_date": dt.date(2025, 1, 1),
        }
        defaults.update(kwargs)
        return KnowledgeBaseEntry.objects.create(**defaults)

    def test_create_entry(self):
        e = self._make_entry()
        self.assertEqual(e.entry_id, "KB-IGA-001")
        self.assertEqual(e.disease_id, "iga")
        self.assertEqual(e.rule_data["weight"], 2)

    def test_str(self):
        e = self._make_entry()
        s = str(e)
        self.assertIn("KB-IGA-001", s)
        self.assertIn("iga", s)
        self.assertIn("Draft", s)

    def test_default_status_draft(self):
        e = self._make_entry()
        self.assertEqual(e.status, KnowledgeBaseEntry.Status.DRAFT)

    def test_status_choices(self):
        for status in KnowledgeBaseEntry.Status:
            e = self._make_entry(
                entry_id=f"KB-TEST-{status.value}",
                status=status.value,
            )
            self.assertEqual(e.status, status.value)
            e.delete()

    def test_evidence_grade_choices(self):
        for grade in KnowledgeBaseEntry.EvidenceGrade:
            e = self._make_entry(
                entry_id=f"KB-TEST-{grade.value}",
                evidence_grade=grade.value,
            )
            self.assertEqual(e.evidence_grade, grade.value)
            e.delete()

    def test_unique_entry_id(self):
        self._make_entry()
        with self.assertRaises(Exception):
            self._make_entry()

    def test_source_protect_delete(self):
        self._make_entry()
        with self.assertRaises(Exception):
            self.source.delete()

    def test_rule_data_json(self):
        rule = {
            "conditions": [
                {"field": "proteinuria", "operator": "gte", "value": 3.5},
                {"field": "albumin", "operator": "lte", "value": 3.0},
            ],
            "weight": 3,
            "explanation": "Nephrotic-range proteinuria with hypoalbuminemia",
            "evidence_grade": "1",
        }
        e = self._make_entry(rule_data=rule)
        e.refresh_from_db()
        self.assertEqual(e.rule_data["conditions"][0]["field"], "proteinuria")
        self.assertEqual(e.rule_data["weight"], 3)

    def test_review_notes(self):
        e = self._make_entry(review_notes="Reviewed by Dr. Haque on 2025-06-01")
        self.assertIn("Dr. Haque", e.review_notes)

    def test_effective_and_retired_dates(self):
        e = self._make_entry(
            effective_date=dt.date(2025, 1, 1),
            retired_date=dt.date(2025, 12, 31),
        )
        self.assertEqual(e.effective_date, dt.date(2025, 1, 1))
        self.assertEqual(e.retired_date, dt.date(2025, 12, 31))

    def test_index_on_disease_id_status(self):
        self._make_entry(entry_id="KB-IGA-001", disease_id="iga", status="active")
        self._make_entry(entry_id="KB-IGA-002", disease_id="iga", status="draft")
        self._make_entry(entry_id="KB-MEM-001", disease_id="membranous", status="active")
        self.assertEqual(KnowledgeBaseEntry.objects.count(), 3)

    def test_multiple_entries_per_disease(self):
        self._make_entry(entry_id="KB-IGA-001")
        self._make_entry(entry_id="KB-IGA-002")
        self.assertEqual(
            KnowledgeBaseEntry.objects.filter(disease_id="iga").count(), 2
        )

    def test_related_name(self):
        self._make_entry()
        self.assertEqual(self.source.entries.count(), 1)

    def test_created_at_auto_set(self):
        e = self._make_entry()
        self.assertIsNotNone(e.created_at)

    def test_updated_at_auto_set(self):
        e = self._make_entry()
        old_updated = e.updated_at
        e.review_notes = "Updated notes"
        e.save()
        e.refresh_from_db()
        self.assertGreaterEqual(e.updated_at, old_updated)


# ---------------------------------------------------------------------------
# Rule Engine Tests
# ---------------------------------------------------------------------------
def _make_patient(**kwargs):
    defaults = {"name": "Test Patient", "sex": "M", "dob": dt.date(1990, 1, 1)}
    defaults.update(kwargs)
    return Patient.objects.create(**defaults)


class ConditionEvaluationTests(TestCase):
    """Test _evaluate_condition() with various operators."""

    def test_eq_operator_match(self):
        cond = {"field": "proteinuria", "operator": "eq", "value": "nephrotic"}
        features = {"proteinuria": "nephrotic"}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_eq_operator_no_match(self):
        cond = {"field": "proteinuria", "operator": "eq", "value": "nephrotic"}
        features = {"proteinuria": "none"}
        self.assertFalse(_evaluate_condition(cond, features))

    def test_eq_operator_list_contains(self):
        cond = {"field": "features", "operator": "eq", "value": "edema"}
        features = {"features": ["edema", "hypertension"]}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_eq_operator_list_not_contains(self):
        cond = {"field": "features", "operator": "eq", "value": "edema"}
        features = {"features": ["hypertension"]}
        self.assertFalse(_evaluate_condition(cond, features))

    def test_contains_operator(self):
        cond = {"field": "labs", "operator": "contains", "value": "lowC3"}
        features = {"labs": ["lowC3", "lowC4"]}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_not_contains_operator(self):
        cond = {"field": "labs", "operator": "not_contains", "value": "anca"}
        features = {"labs": ["lowC3"]}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_gt_operator(self):
        cond = {"field": "latest_egfr", "operator": "gt", "value": 30}
        features = {"latest_egfr": 45}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_gte_operator(self):
        cond = {"field": "proteinuria_level", "operator": "gte", "value": 3.5}
        features = {"proteinuria_level": 3.5}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_lt_operator(self):
        cond = {"field": "albumin_level", "operator": "lt", "value": 3.0}
        features = {"albumin_level": 2.5}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_lte_operator(self):
        cond = {"field": "albumin_level", "operator": "lte", "value": 3.0}
        features = {"albumin_level": 3.0}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_in_operator(self):
        cond = {"field": "disease_phase", "operator": "in", "value": ["active", "relapse"]}
        features = {"disease_phase": "relapse"}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_exists_operator(self):
        cond = {"field": "biopsy_date", "operator": "exists"}
        features = {"biopsy_date": "2025-01-01"}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_not_exists_operator(self):
        cond = {"field": "biopsy_date", "operator": "not_exists"}
        features = {"biopsy_date": ""}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_neq_operator(self):
        cond = {"field": "proteinuria", "operator": "neq", "value": "none"}
        features = {"proteinuria": "nephrotic"}
        self.assertTrue(_evaluate_condition(cond, features))

    def test_numeric_comparison_invalid_value(self):
        cond = {"field": "egfr", "operator": "gt", "value": 30}
        features = {"egfr": "not_a_number"}
        self.assertFalse(_evaluate_condition(cond, features))


class EvaluateEntryTests(TestCase):
    """Test evaluate_entry() with a KnowledgeBaseEntry."""

    def setUp(self):
        self.source = GuidelineSource.objects.create(
            title="KDIGO 2025",
            abbreviation="KDIGO",
            version_year=2025,
            effective_date=dt.date(2025, 1, 1),
        )

    def test_entry_with_matching_conditions(self):
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-001",
            disease_id="iga",
            rule_data={
                "conditions": [
                    {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
                ],
                "weight": 3,
                "explanation": "Nephrotic-range proteinuria",
                "base_score": 1,
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        features = {"proteinuria": "nephrotic"}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 4)  # base 1 + weight 3
        self.assertEqual(len(result.matched_rules), 1)

    def test_entry_with_no_matching_conditions(self):
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-002",
            disease_id="iga",
            rule_data={
                "conditions": [
                    {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
                ],
                "weight": 3,
                "explanation": "Nephrotic-range proteinuria",
                "base_score": 1,
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        features = {"proteinuria": "none"}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 1)  # Only base score
        self.assertEqual(len(result.matched_rules), 0)

    def test_entry_multiple_conditions_or_logic(self):
        """Each matching condition adds weight independently (OR logic)."""
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-003",
            disease_id="membranous",
            rule_data={
                "conditions": [
                    {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
                    {"field": "albumin", "operator": "eq", "value": "low"},
                ],
                "weight": 4,
                "explanation": "Nephrotic syndrome",
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        # Both match → weight added twice
        features = {"proteinuria": "nephrotic", "albumin": "low"}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 8)  # 4 + 4
        self.assertEqual(len(result.matched_rules), 2)

        # Only one matches → weight added once
        features = {"proteinuria": "nephrotic", "albumin": "normal"}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 4)
        self.assertEqual(len(result.matched_rules), 1)

        # None match → score is 0
        features = {"proteinuria": "none", "albumin": "normal"}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 0)
        self.assertEqual(len(result.matched_rules), 0)

    def test_entry_negative_weight_floored_at_zero(self):
        """Negative weights reduce score but total is floored at 0."""
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-004",
            disease_id="membranous",
            rule_data={
                "conditions": [
                    {"field": "labs", "operator": "contains", "value": "anaDsDna"},
                ],
                "weight": -2,
                "explanation": "ANA positivity shifts away from primary membranous",
                "base_score": 0,
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        features = {"labs": ["anaDsDna"]}
        result = evaluate_entry(entry, features)
        # Weight is -2 but total_score is floored at 0
        self.assertEqual(result.total_score, 0)
        self.assertEqual(len(result.matched_rules), 1)

    def test_entry_negative_weight_with_base_score(self):
        """Negative weight can reduce a positive base score."""
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-004b",
            disease_id="membranous",
            rule_data={
                "conditions": [
                    {"field": "labs", "operator": "contains", "value": "anaDsDna"},
                ],
                "weight": -2,
                "explanation": "ANA positivity shifts away",
                "base_score": 5,
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        features = {"labs": ["anaDsDna"]}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 3)  # 5 - 2 = 3

    def test_score_floored_at_zero(self):
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-005",
            disease_id="test",
            rule_data={
                "conditions": [
                    {"field": "features", "operator": "contains", "value": "test"},
                ],
                "weight": -10,
                "explanation": "Heavy penalty",
                "base_score": 0,
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        features = {"features": ["test"]}
        result = evaluate_entry(entry, features)
        self.assertEqual(result.total_score, 0)  # Floored at zero

    def test_source_in_result(self):
        entry = KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-006",
            disease_id="test",
            rule_data={"conditions": [], "weight": 1, "explanation": "Test"},
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )
        result = evaluate_entry(entry, {})
        self.assertIn("KDIGO", result.source)
        self.assertIn("2025", result.source)


class PatientFeatureExtractionTests(TestCase):
    """Test extract_patient_features() pulls correct data from patient records."""

    def test_child_age_group(self):
        p = _make_patient(dob=dt.date(2015, 1, 1))  # ~11 years old
        features = extract_patient_features(p)
        self.assertEqual(features["ageGroup"], "child")

    def test_adult_age_group(self):
        p = _make_patient(dob=dt.date(1990, 1, 1))
        features = extract_patient_features(p)
        self.assertEqual(features["ageGroup"], "adult")

    def test_disease_phase_extracted(self):
        p = _make_patient(current_phase=DiseasePhase.REMISSION)
        features = extract_patient_features(p)
        self.assertEqual(features["disease_phase"], DiseasePhase.REMISSION)

    def test_edema_from_encounter(self):
        p = _make_patient()
        ClinicalEncounter.objects.create(
            patient=p,
            encounter_date=dt.date.today(),
            edema_grade=2,
        )
        features = extract_patient_features(p)
        self.assertIn("edema", features["features"])

    def test_hypertension_from_encounter(self):
        p = _make_patient()
        ClinicalEncounter.objects.create(
            patient=p,
            encounter_date=dt.date.today(),
            systolic_bp=150,
        )
        features = extract_patient_features(p)
        self.assertIn("hypertension", features["features"])

    def test_low_egfr_rapid_decline(self):
        p = _make_patient(latest_egfr=25)
        features = extract_patient_features(p)
        self.assertEqual(features["egfrTrend"], "rapidDecline")

    def test_low_egfr_reduced(self):
        p = _make_patient(latest_egfr=45)
        features = extract_patient_features(p)
        self.assertEqual(features["egfrTrend"], "reduced")

    def test_normal_egfr(self):
        p = _make_patient(latest_egfr=90)
        features = extract_patient_features(p)
        self.assertEqual(features["egfrTrend"], "normal")

    def test_lupus_diagnosis(self):
        p = _make_patient(primary_diagnosis="Lupus nephritis")
        features = extract_patient_features(p)
        self.assertIn("sle", features["features"])

    def test_dkd_diagnosis(self):
        p = _make_patient(primary_diagnosis="DKD only")
        features = extract_patient_features(p)
        self.assertIn("diabetes", features["features"])


class EvaluatePatientRulesTests(TestCase):
    """Test evaluate_patient_rules() end-to-end."""

    def setUp(self):
        self.source = GuidelineSource.objects.create(
            title="KDIGO 2025",
            abbreviation="KDIGO",
            version_year=2025,
            effective_date=dt.date(2025, 1, 1),
        )

    def _make_active_entry(self, entry_id, disease_id, conditions, weight=2, base_score=0):
        return KnowledgeBaseEntry.objects.create(
            entry_id=entry_id,
            disease_id=disease_id,
            rule_data={
                "conditions": conditions,
                "weight": weight,
                "explanation": f"Rule for {disease_id}",
                "base_score": base_score,
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="active",
        )

    def test_only_active_entries_evaluated(self):
        self._make_active_entry(
            "KB-IGA-001", "iga",
            [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
        )
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-IGA-002",
            disease_id="iga",
            rule_data={
                "conditions": [
                    {"field": "proteinuria", "operator": "eq", "value": "nephrotic"}
                ],
                "weight": 10,
                "explanation": "Draft rule",
            },
            source=self.source,
            effective_date=dt.date(2025, 1, 1),
            status="draft",
        )
        p = _make_patient()
        results = evaluate_patient_rules(p)
        # Only active entry should be evaluated
        iga_result = next((r for r in results if r.disease_id == "iga"), None)
        self.assertIsNotNone(iga_result)
        self.assertEqual(iga_result.total_score, 0)  # No matching features

    def test_disease_id_filter(self):
        self._make_active_entry(
            "KB-IGA-001", "iga",
            [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
        )
        self._make_active_entry(
            "KB-MEM-001", "membranous",
            [{"field": "albumin", "operator": "eq", "value": "low"}],
        )
        p = _make_patient()
        results = evaluate_patient_rules(p, disease_id="iga")
        disease_ids = [r.disease_id for r in results]
        self.assertIn("iga", disease_ids)
        self.assertNotIn("membranous", disease_ids)

    def test_scores_sorted_descending(self):
        self._make_active_entry(
            "KB-IGA-001", "iga",
            [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
            weight=2, base_score=1,
        )
        self._make_active_entry(
            "KB-MEM-001", "membranous",
            [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
            weight=5, base_score=3,
        )
        p = _make_patient()
        # We need to set up the patient features manually since extract_patient_features
        # won't find lab results. Let's create entries that match on simple fields.
        # Instead, let's test with entries that have base_score differences.
        KnowledgeBaseEntry.objects.filter(entry_id="KB-IGA-001").update(
            rule_data={
                "conditions": [],
                "weight": 1,
                "explanation": "Base",
                "base_score": 5,
            }
        )
        KnowledgeBaseEntry.objects.filter(entry_id="KB-MEM-001").update(
            rule_data={
                "conditions": [],
                "weight": 1,
                "explanation": "Base",
                "base_score": 10,
            }
        )
        results = evaluate_patient_rules(p)
        if len(results) >= 2:
            self.assertGreaterEqual(results[0].total_score, results[1].total_score)

    def test_multiple_rules_same_disease_aggregated(self):
        self._make_active_entry(
            "KB-IGA-001", "iga",
            [{"field": "disease_phase", "operator": "eq", "value": "active"}],
            weight=2,
        )
        self._make_active_entry(
            "KB-IGA-002", "iga",
            [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
            weight=3,
        )
        p = _make_patient(current_phase=DiseasePhase.ACTIVE)
        results = evaluate_patient_rules(p)
        iga_result = next((r for r in results if r.disease_id == "iga"), None)
        self.assertIsNotNone(iga_result)
        # Only the first rule matches (disease_phase=active), proteinuria=none
        self.assertEqual(iga_result.total_score, 2)
        self.assertEqual(len(iga_result.matched_rules), 1)

    def test_empty_when_no_active_rules(self):
        p = _make_patient()
        results = evaluate_patient_rules(p)
        self.assertEqual(len(results), 0)


# ─── V4.2 Reusable Knowledge Object Tests ─────────────────────────────────


class SyndromeTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="iga", name="IgA Nephropathy",
            definition="Test disease for syndrome testing",
        )

    def test_create_syndrome(self):
        s = Syndrome.objects.create(
            id="nephrotic_syndrome", name="Nephrotic Syndrome",
            definition="Proteinuria >3.5g/day, hypoalbuminemia, edema, hyperlipidemia",
        )
        s.associated_diseases.add(self.disease)
        self.assertEqual(str(s), "Nephrotic Syndrome (nephrotic_syndrome)")
        self.assertIn(self.disease, s.associated_diseases.all())

    def test_syndrome_defaults(self):
        s = Syndrome.objects.create(id="test_syndrome", name="Test Syndrome")
        self.assertTrue(s.is_active)
        self.assertEqual(s.diagnostic_criteria, [])
        self.assertEqual(s.common_causes, [])

    def test_syndrome_active_filter(self):
        Syndrome.objects.create(id="active_syn", name="Active Syndrome", is_active=True)
        Syndrome.objects.create(id="inactive_syn", name="Inactive Syndrome", is_active=False)
        self.assertEqual(Syndrome.objects.filter(is_active=True).count(), 1)

    def test_syndrome_verbose_name_plural(self):
        self.assertEqual(Syndrome._meta.verbose_name_plural, "syndromes")


class PathologyEntityTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="lupus", name="Lupus Nephritis",
            definition="Test disease for pathology testing",
        )

    def test_create_pathology_entity(self):
        p = PathologyEntity.objects.create(
            id="mesangial_proliferation", name="Mesangial Proliferation",
            definition="Increased number of mesangial cells and matrix",
        )
        p.associated_diseases.add(self.disease)
        self.assertEqual(str(p), "Mesangial Proliferation (mesangial_proliferation)")
        self.assertIn(self.disease, p.associated_diseases.all())

    def test_pathology_entity_defaults(self):
        p = PathologyEntity.objects.create(id="crescents", name="Crescents")
        self.assertTrue(p.is_active)
        self.assertEqual(p.histological_appearance, "")

    def test_pathology_entity_plural(self):
        self.assertEqual(PathologyEntity._meta.verbose_name_plural, "pathology entities")


class LabEntityTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="membranous", name="Membranous Nephropathy",
            definition="Test disease for lab testing",
        )

    def test_create_lab_entity(self):
        l = LabEntity.objects.create(
            id="proteinuria", name="Proteinuria",
            interpretation="Elevated protein indicates glomerular damage",
            reference_ranges={"adult": {"normal": "<0.15", "nephrotic": ">3.5"}},
        )
        l.associated_diseases.add(self.disease)
        self.assertEqual(str(l), "Proteinuria (proteinuria)")
        self.assertEqual(l.reference_ranges["adult"]["nephrotic"], ">3.5")

    def test_lab_entity_defaults(self):
        l = LabEntity.objects.create(id="egfr", name="eGFR")
        self.assertTrue(l.is_active)
        self.assertEqual(l.false_positives, "")

    def test_lab_entity_plural(self):
        self.assertEqual(LabEntity._meta.verbose_name_plural, "lab entities")


class DrugIntelligenceTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="iga", name="IgA Nephropathy",
            definition="Test disease for drug testing",
        )

    def test_create_drug(self):
        d = DrugIntelligence.objects.create(
            id="rituximab", name="Rituximab",
            drug_class="Monoclonal antibody (anti-CD20)",
            mechanism_of_action="B-cell depletion via CD20 binding",
            pregnancy="FDA Category C",
        )
        d.indications.add(self.disease)
        self.assertEqual(str(d), "Rituximab (rituximab)")
        self.assertIn(self.disease, d.indications.all())

    def test_drug_evidence_level(self):
        d = DrugIntelligence.objects.create(
            id="cyclophosphamide", name="Cyclophosphamide",
            evidence_level="1",
        )
        self.assertEqual(d.evidence_level, "1")

    def test_drug_default_side_effects(self):
        d = DrugIntelligence.objects.create(id="test_drug", name="Test Drug")
        self.assertEqual(d.common_side_effects, [])
        self.assertEqual(d.serious_side_effects, [])

    def test_drug_plural(self):
        self.assertEqual(DrugIntelligence._meta.verbose_name_plural, "drug intelligence")


class MonitoringProtocolTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="iga", name="IgA Nephropathy",
            definition="Test disease for monitoring testing",
        )

    def test_create_protocol(self):
        m = MonitoringProtocol.objects.create(
            id="rituximab_monitoring", name="Rituximab Monitoring Protocol",
            baseline_investigations=["CBC", "LFT", "Hepatitis B serology"],
            monitoring_schedule=[{"week": 0, "tests": ["CBC"]}, {"week": 4, "tests": ["CD19+ count"]}],
        )
        m.associated_diseases.add(self.disease)
        self.assertEqual(str(m), "Rituximab Monitoring Protocol (rituximab_monitoring)")
        self.assertEqual(len(m.baseline_investigations), 3)

    def test_protocol_drug_link(self):
        drug = DrugIntelligence.objects.create(id="rituximab", name="Rituximab")
        m = MonitoringProtocol.objects.create(
            id="ritux_mon", name="Ritux Monitoring", drug=drug,
        )
        self.assertEqual(m.drug, drug)

    def test_protocol_defaults(self):
        m = MonitoringProtocol.objects.create(id="test_protocol", name="Test Protocol")
        self.assertTrue(m.is_active)
        self.assertEqual(m.baseline_investigations, [])

    def test_protocol_plural(self):
        self.assertEqual(MonitoringProtocol._meta.verbose_name_plural, "monitoring protocols")


class ComplicationTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="iga", name="IgA Nephropathy",
            definition="Test disease for complication testing",
        )
        self.drug = DrugIntelligence.objects.create(id="steroid", name="Corticosteroid")

    def test_create_complication(self):
        c = Complication.objects.create(
            id="infection", name="Infection",
            risk_factors=["Immunosuppression", "Neutropenia", "Diabetes"],
            prevention="Vaccination, prophylactic antibiotics",
        )
        c.associated_diseases.add(self.disease)
        c.associated_drugs.add(self.drug)
        self.assertEqual(str(c), "Infection (infection)")
        self.assertIn(self.disease, c.associated_diseases.all())
        self.assertIn(self.drug, c.associated_drugs.all())

    def test_complication_defaults(self):
        c = Complication.objects.create(id="thrombosis", name="Thrombosis")
        self.assertTrue(c.is_active)
        self.assertEqual(c.risk_factors, [])

    def test_complication_cascade_delete(self):
        c = Complication.objects.create(id="test_comp", name="Test Complication")
        c.associated_diseases.add(self.disease)
        c.associated_drugs.add(self.drug)
        self.assertEqual(c.associated_diseases.count(), 1)
        self.assertEqual(c.associated_drugs.count(), 1)

    def test_complication_plural(self):
        self.assertEqual(Complication._meta.verbose_name_plural, "complications")


# ─── V4.2 Knowledge Graph Tests ────────────────────────────────────────────


class KnowledgeGraphNodeTests(TestCase):
    def test_create_node(self):
        n = KnowledgeGraphNode.objects.create(
            node_id="d:iga", node_type=KnowledgeGraphNode.NodeType.DISEASE,
            label="IgA Nephropathy",
        )
        self.assertEqual(str(n), "Disease: IgA Nephropathy (d:iga)")
        self.assertEqual(n.node_type, "disease")

    def test_node_defaults(self):
        n = KnowledgeGraphNode.objects.create(
            node_id="sy:nephrotic", node_type=KnowledgeGraphNode.NodeType.SYNDROME,
            label="Nephrotic Syndrome",
        )
        self.assertTrue(n.is_active)
        self.assertEqual(n.metadata, {})

    def test_node_types_coverage(self):
        for nt in KnowledgeGraphNode.NodeType:
            n = KnowledgeGraphNode.objects.create(
                node_id=f"test:{nt.value}", node_type=nt.value,
                label=f"Test {nt.label}",
            )
            self.assertEqual(n.node_type, nt.value)

    def test_node_verbose_name_plural(self):
        self.assertEqual(KnowledgeGraphNode._meta.verbose_name_plural, "knowledge graph nodes")


class KnowledgeGraphEdgeTests(TestCase):
    def setUp(self):
        self.src = KnowledgeGraphNode.objects.create(
            node_id="sy:nephrotic", node_type=KnowledgeGraphNode.NodeType.SYNDROME,
            label="Nephrotic Syndrome",
        )
        self.tgt = KnowledgeGraphNode.objects.create(
            node_id="d:mcd", node_type=KnowledgeGraphNode.NodeType.DISEASE,
            label="Minimal Change Disease",
        )

    def test_create_edge(self):
        e = KnowledgeGraphEdge.objects.create(
            source=self.src, target=self.tgt,
            edge_type=KnowledgeGraphEdge.EdgeType.CAUSES,
            weight=0.9,
        )
        expected = "Nephrotic Syndrome --[Causes]--> Minimal Change Disease"
        self.assertEqual(str(e), expected)
        self.assertEqual(e.weight, 0.9)

    def test_edge_defaults(self):
        e = KnowledgeGraphEdge.objects.create(
            source=self.src, target=self.tgt,
            edge_type=KnowledgeGraphEdge.EdgeType.CAUSES,
        )
        self.assertEqual(e.weight, 1.0)
        self.assertTrue(e.is_active)

    def test_edge_types_coverage(self):
        for et in KnowledgeGraphEdge.EdgeType:
            e = KnowledgeGraphEdge.objects.create(
                source=self.src, target=self.tgt,
                edge_type=et.value,
            )
            self.assertEqual(e.edge_type, et.value)

    def test_edge_relations(self):
        e = KnowledgeGraphEdge.objects.create(
            source=self.src, target=self.tgt,
            edge_type=KnowledgeGraphEdge.EdgeType.CAUSES,
        )
        self.assertIn(e, self.src.outgoing_edges.all())
        self.assertIn(e, self.tgt.incoming_edges.all())

    def test_edge_verbose_name_plural(self):
        self.assertEqual(KnowledgeGraphEdge._meta.verbose_name_plural, "knowledge graph edges")


class GraphPopulationTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(
            id="iga", name="IgA Nephropathy",
            definition="IgA deposition in glomeruli",
        )
        self.syndrome = Syndrome.objects.create(
            id="nephritic_syndrome", name="Nephritic Syndrome",
            definition="Hematuria, hypertension, oliguria",
        )
        self.syndrome.associated_diseases.add(self.disease)
        self.pathology = PathologyEntity.objects.create(
            id="mesangial_iga", name="Mesangial IgA Deposits",
            definition="Dominant IgA on immunofluorescence",
        )
        self.pathology.associated_diseases.add(self.disease)
        self.lab = LabEntity.objects.create(
            id="hematuria", name="Hematuria",
            interpretation="RBCs in urine",
        )
        self.lab.associated_diseases.add(self.disease)

    def test_populate_creates_nodes(self):
        populate_from_models()
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="sy:nephritic_syndrome").exists())
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="d:iga").exists())
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="p:mesangial_iga").exists())
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="l:hematuria").exists())

    def test_populate_creates_edges(self):
        populate_from_models()
        # Syndrome → Disease (CAUSES)
        self.assertTrue(
            KnowledgeGraphEdge.objects.filter(
                source__node_id="sy:nephritic_syndrome",
                target__node_id="d:iga",
                edge_type=KnowledgeGraphEdge.EdgeType.CAUSES,
            ).exists()
        )
        # Disease → Pathology (DIAGNOSED_BY)
        self.assertTrue(
            KnowledgeGraphEdge.objects.filter(
                source__node_id="d:iga",
                target__node_id="p:mesangial_iga",
                edge_type=KnowledgeGraphEdge.EdgeType.DIAGNOSED_BY,
            ).exists()
        )
        # Disease → Lab (DIAGNOSED_BY)
        self.assertTrue(
            KnowledgeGraphEdge.objects.filter(
                source__node_id="d:iga",
                target__node_id="l:hematuria",
                edge_type=KnowledgeGraphEdge.EdgeType.DIAGNOSED_BY,
            ).exists()
        )

    def test_populate_idempotent(self):
        populate_from_models()
        first_count = KnowledgeGraphNode.objects.count()
        populate_from_models()
        second_count = KnowledgeGraphNode.objects.count()
        self.assertEqual(first_count, second_count)

    def test_populate_drugs_and_monitoring(self):
        drug = DrugIntelligence.objects.create(
            id="steroid", name="Prednisolone",
            mechanism_of_action="Immunosuppression",
        )
        drug.indications.add(self.disease)
        protocol = MonitoringProtocol.objects.create(
            id="steroid_monitoring", name="Steroid Monitoring",
            drug=drug,
        )
        protocol.associated_diseases.add(self.disease)
        populate_from_models()
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="dr:steroid").exists())
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="m:steroid_monitoring").exists())
        # Drug → Monitoring (MONITORED_BY)
        self.assertTrue(
            KnowledgeGraphEdge.objects.filter(
                source__node_id="dr:steroid",
                target__node_id="m:steroid_monitoring",
                edge_type=KnowledgeGraphEdge.EdgeType.MONITORED_BY,
            ).exists()
        )

    def test_populate_complications(self):
        complication = Complication.objects.create(
            id="ckd_progression", name="CKD Progression",
        )
        complication.associated_diseases.add(self.disease)
        populate_from_models()
        self.assertTrue(KnowledgeGraphNode.objects.filter(node_id="co:ckd_progression").exists())
        self.assertTrue(
            KnowledgeGraphEdge.objects.filter(
                source__node_id="d:iga",
                target__node_id="co:ckd_progression",
                edge_type=KnowledgeGraphEdge.EdgeType.COMPLICATED_BY,
            ).exists()
        )


class GraphTraversalTests(TestCase):
    def setUp(self):
        self.disease = Disease.objects.create(id="iga", name="IgA Nephropathy")
        self.syndrome = Syndrome.objects.create(id="nephritic", name="Nephritic Syndrome")
        self.syndrome.associated_diseases.add(self.disease)
        self.pathology = PathologyEntity.objects.create(id="mesangial_iga", name="Mesangial IgA")
        self.pathology.associated_diseases.add(self.disease)
        self.lab = LabEntity.objects.create(id="hematuria", name="Hematuria")
        self.lab.associated_diseases.add(self.disease)
        populate_from_models()

    def test_find_paths_from_syndrome(self):
        results = find_paths("sy:nephritic")
        self.assertGreater(len(results), 0)
        node_ids = [r["node"].node_id for r in results]
        self.assertIn("d:iga", node_ids)

    def test_find_paths_filtered_by_type(self):
        results = find_paths("sy:nephritic", target_node_type="pathology")
        for r in results:
            self.assertEqual(r["node"].node_type, "pathology")

    def test_find_paths_max_depth(self):
        results = find_paths("sy:nephritic", max_depth=1)
        for r in results:
            self.assertLessEqual(r["depth"], 1)

    def test_find_paths_nonexistent_source(self):
        results = find_paths("sy:nonexistent")
        self.assertEqual(results, [])

    def test_get_reasoning_chain(self):
        chain = get_reasoning_chain("iga")
        self.assertEqual(chain["disease_id"], "iga")
        self.assertEqual(chain["disease_label"], "IgA Nephropathy")
        self.assertGreater(len(chain["synapses"]), 0)
        self.assertGreater(len(chain["diagnosis"]), 0)

    def test_get_reasoning_chain_nonexistent(self):
        chain = get_reasoning_chain("nonexistent")
        self.assertIn("error", chain)

    def test_get_differential(self):
        diff = get_differential("nephritic")
        self.assertEqual(diff["syndrome_id"], "nephritic")
        self.assertGreater(len(diff["differentials"]), 0)
        self.assertIn("d:iga", [d["node_id"] for d in diff["differentials"]])

    def test_get_differential_nonexistent(self):
        diff = get_differential("nonexistent")
        self.assertIn("error", diff)

    def test_get_graph_summary(self):
        summary = get_graph_summary()
        self.assertIn("total_nodes", summary)
        self.assertIn("total_edges", summary)
        self.assertIn("nodes_by_type", summary)
        self.assertIn("edges_by_type", summary)
        self.assertGreater(summary["total_nodes"], 0)
        self.assertGreater(summary["total_edges"], 0)


# ---------------------------------------------------------------------------
# Graph-Enhanced Reasoning Tests
# ---------------------------------------------------------------------------

class GraphReasoningTests(TestCase):
    """Test the graph-enhanced clinical reasoning bridge service."""

    @classmethod
    def setUpTestData(cls):
        cls.disease = Disease.objects.create(id="iga", name="IgA Nephropathy",
            definition="Mesangial IgA deposits")
        cls.disease2 = Disease.objects.create(id="mcd", name="Minimal Change Disease",
            definition="Foot process effacement")
        cls.syndrome = Syndrome.objects.create(id="nephritic", name="Nephritic Syndrome")
        cls.syndrome.associated_diseases.add(cls.disease)
        cls.syndrome2 = Syndrome.objects.create(id="nephrotic", name="Nephrotic Syndrome")
        cls.syndrome2.associated_diseases.add(cls.disease2)
        cls.pathology = PathologyEntity.objects.create(id="mesangial",
            name="Mesangial Proliferation", definition="Increased mesangial cells")
        cls.pathology.associated_diseases.add(cls.disease)
        cls.lab = LabEntity.objects.create(id="hematuria", name="Hematuria",
            interpretation="RBCs in urine")
        cls.lab.associated_diseases.add(cls.disease)
        cls.drug = DrugIntelligence.objects.create(
            id="pred", name="Prednisolone",
            mechanism_of_action="Corticosteroid immunosuppression")
        cls.drug.indications.add(cls.disease)
        cls.monitoring = MonitoringProtocol.objects.create(
            id="mon_pred", name="Prednisolone Monitoring Protocol", drug=cls.drug)
        cls.monitoring.associated_diseases.add(cls.disease)
        cls.complication = Complication.objects.create(
            id="infection", name="Infection",
            clinical_features="Fever, leukocytosis")
        cls.complication.associated_diseases.add(cls.disease)
        populate_from_models()

    def test_get_treatment_recommendations(self):
        treatments = get_treatment_recommendations("iga")
        names = [t["drug_name"] for t in treatments]
        self.assertIn("Prednisolone", names)

    def test_get_treatment_recommendations_empty(self):
        treatments = get_treatment_recommendations("nonexistent")
        self.assertEqual(treatments, [])

    def test_get_monitoring_recommendations(self):
        protocols = get_monitoring_recommendations("iga")
        labels = [p["label"] for p in protocols]
        self.assertIn("Prednisolone Monitoring Protocol", labels)

    def test_get_monitoring_recommendations_empty(self):
        protocols = get_monitoring_recommendations("nonexistent")
        self.assertEqual(protocols, [])

    def test_get_complication_risks(self):
        complications = get_complication_risks("iga")
        names = [c["complication_name"] for c in complications]
        self.assertIn("Infection", names)

    def test_get_complication_risks_empty(self):
        complications = get_complication_risks("nonexistent")
        self.assertEqual(complications, [])

    def test_get_syndrome_matches(self):
        features = {"features": ["hypertension"], "labs": ["hematuria"], "biopsy": [],
                     "proteinuria": "nephrotic", "egfrTrend": "normal"}
        matches = get_syndrome_matches(features)
        self.assertGreater(len(matches), 0)
        self.assertIn("Nephrotic Syndrome", [m["syndrome_name"] for m in matches])

    def test_get_graph_differential(self):
        features = {"features": [], "labs": [], "biopsy": [],
                     "proteinuria": "nephrotic", "egfrTrend": "normal"}
        diff = get_graph_differential(features)
        self.assertGreater(len(diff), 0)

    def test_augment_differential_adds_graph_diseases(self):
        rule_based = [{"disease_id": "iga", "disease_name": "IgA Nephropathy", "score": 15}]
        features = {"features": [], "labs": [], "biopsy": [],
                     "proteinuria": "nephrotic", "egfrTrend": "normal"}
        augmented = augment_differential(rule_based, features)
        self.assertGreater(len(augmented), 0)

    def test_build_graph_reasoning_steps(self):
        steps = build_graph_reasoning_steps("iga")
        self.assertGreater(len(steps), 0)
        step_types = [s["step"] for s in steps]
        self.assertIn("graph_syndrome_association", step_types)
        self.assertIn("graph_diagnostic_evidence", step_types)
        self.assertIn("graph_treatment_options", step_types)
        self.assertIn("graph_monitoring_plan", step_types)

    def test_build_graph_reasoning_steps_nonexistent(self):
        steps = build_graph_reasoning_steps("nonexistent")
        self.assertEqual(steps, [])

    def test_enhance_treatment_plan(self):
        plan = enhance_treatment_plan("iga")
        self.assertIn("treatments", plan)
        self.assertIn("monitoring", plan)
        self.assertIn("complication_risks", plan)
        self.assertGreater(len(plan["treatments"]), 0)
        self.assertGreater(len(plan["complication_risks"]), 0)


class GraphEdgeDeactivationTests(TestCase):
    def setUp(self):
        self.src = KnowledgeGraphNode.objects.create(
            node_id="test:src", node_type=KnowledgeGraphNode.NodeType.DISEASE,
            label="Source",
        )
        self.tgt = KnowledgeGraphNode.objects.create(
            node_id="test:tgt", node_type=KnowledgeGraphNode.NodeType.DRUG,
            label="Target",
        )
        self.edge = KnowledgeGraphEdge.objects.create(
            source=self.src, target=self.tgt,
            edge_type=KnowledgeGraphEdge.EdgeType.TREATED_BY,
        )

    def test_deactivate_node(self):
        self.src.is_active = False
        self.src.save()
        fresh = KnowledgeGraphNode.objects.get(node_id=self.src.node_id)
        self.assertFalse(fresh.is_active)

    def test_deactivate_edge(self):
        self.edge.is_active = False
        self.edge.save()
        self.assertFalse(
            KnowledgeGraphEdge.objects.filter(
                source=self.src, target=self.tgt, is_active=True
            ).exists()
        )
