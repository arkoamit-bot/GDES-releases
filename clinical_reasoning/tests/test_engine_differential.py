"""
Tests for the clinical reasoning engine's differential ranking.

`evaluate_patient_rules` returns an entry for every disease that has at least
one ACTIVE rule, scoring 0 when none of its criteria matched. Code that picks a
"leading differential" must therefore filter on score > 0, otherwise a patient
whose data satisfies no rule gets an arbitrary zero-score disease presented as
their diagnosis.
"""
import datetime as dt

from django.test import SimpleTestCase, TestCase

from knowledge.models import GuidelineSource, KnowledgeBaseEntry
from knowledge.services import DiseaseScore
from patients.models import Patient

from clinical_reasoning.services.engine import (
    _build_differential, _build_reasoning_chain, _fired, _generate_recommendations,
)


def _score(disease_id, name, total, source="KDIGO 2021", rules=1):
    return DiseaseScore(
        disease_id=disease_id,
        disease_name=name,
        total_score=total,
        matched_rules=[f"rule-{i}" for i in range(rules)],
        source=source,
        evidence_grade="1",
    )


class TestFired(SimpleTestCase):
    def test_drops_zero_scores(self):
        results = [_score("a", "A", 0), _score("b", "B", 3)]
        self.assertEqual([r.disease_id for r in _fired(results)], ["b"])

    def test_all_zero_is_empty(self):
        self.assertEqual(_fired([_score("a", "A", 0), _score("b", "B", 0)]), [])

    def test_preserves_input_order(self):
        results = [_score("a", "A", 9), _score("b", "B", 4), _score("c", "C", 0)]
        self.assertEqual([r.disease_id for r in _fired(results)], ["a", "b"])


class TestBuildDifferential(SimpleTestCase):
    def test_excludes_zero_score_diseases(self):
        results = [_score("iga", "IgA nephropathy", 0), _score("fsgs", "FSGS", 7)]
        diff = _build_differential(results)
        self.assertEqual([d["disease_id"] for d in diff], ["fsgs"])

    def test_empty_when_nothing_fired(self):
        self.assertEqual(_build_differential([_score("a", "A", 0)]), [])

    def test_confidence_is_relative_share(self):
        diff = _build_differential([_score("a", "A", 3), _score("b", "B", 1)])
        self.assertEqual({d["disease_id"]: d["confidence"] for d in diff},
                         {"a": 75, "b": 25})

    def test_confidence_sums_to_100(self):
        diff = _build_differential(
            [_score("a", "A", 5), _score("b", "B", 3), _score("c", "C", 2)])
        self.assertEqual(sum(d["confidence"] for d in diff), 100)

    def test_ranked_highest_first(self):
        results = [_score("high", "High", 12), _score("mid", "Mid", 5),
                   _score("low", "Low", 1), _score("zero", "Zero", 0)]
        diff = _build_differential(results)
        self.assertEqual([d["disease_id"] for d in diff], ["high", "mid", "low"])


class TestNoArbitraryLeadingDisease(SimpleTestCase):
    """A patient matching no rule must not get a named leading diagnosis."""

    def test_reasoning_chain_omits_rule_evaluation_step(self):
        chain = _build_reasoning_chain(
            patient=None, rule_results=[_score("iga", "IgA nephropathy", 0)],
            trajectory={}, care_gaps=[])
        steps = [s.get("step") for s in chain]
        self.assertNotIn("rule_evaluation", steps)
        self.assertFalse(any("IgA nephropathy" in str(s) for s in chain))

    def test_reasoning_chain_names_the_top_fired_disease(self):
        chain = _build_reasoning_chain(
            patient=None,
            rule_results=[_score("iga", "IgA nephropathy", 0), _score("fsgs", "FSGS", 8)],
            trajectory={}, care_gaps=[])
        rule_steps = [s for s in chain if s.get("step") == "rule_evaluation"]
        self.assertEqual(len(rule_steps), 1)
        self.assertIn("FSGS", rule_steps[0]["finding"])

    def test_no_diagnostic_impression_when_nothing_fired(self):
        recs = _generate_recommendations(
            care_gaps=[], rule_results=[_score("iga", "IgA nephropathy", 0)])
        self.assertFalse([r for r in recs if r.get("type") == "diagnostic_impression"])


class TestActiveButUnmatchedRulesEndToEnd(TestCase):
    """ACTIVE rules exist, but none match this patient."""

    def setUp(self):
        self.source = GuidelineSource.objects.create(
            title="Test guideline", abbreviation="TEST-GL",
            version_year=2021, effective_date=dt.date(2021, 1, 1),
        )
        # Requires proteinuria == "nephrotic"; the patient has none.
        KnowledgeBaseEntry.objects.create(
            entry_id="KB-TEST-001",
            disease_id="iga",
            rule_data={
                "disease_name": "IgA nephropathy",
                "conditions": [{"field": "proteinuria", "operator": "eq",
                                "value": "nephrotic"}],
                "weight": 5,
            },
            source=self.source,
            status=KnowledgeBaseEntry.Status.ACTIVE,
            effective_date=dt.date(2021, 1, 1),
        )
        self.patient = Patient.objects.create(
            patient_id="CR-UNMATCHED", name="No Match", sex="F")

    def test_fixture_really_does_yield_a_zero_score_disease(self):
        # Guards the rest of this class from going vacuous: the ACTIVE rule must
        # actually be evaluated (so rule_results is non-empty) yet score 0.
        from knowledge.services import evaluate_patient_rules
        results = evaluate_patient_rules(self.patient)
        self.assertTrue(results, "ACTIVE rule was not evaluated at all")
        self.assertEqual([r.total_score for r in results], [0])
        self.assertEqual([r.disease_id for r in results], ["iga"])

    def test_differential_is_empty_and_no_leading_disease_is_stored(self):
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(self.patient)
        self.assertEqual(profile.differential, [])

    def test_no_clinical_insight_names_an_unmatched_disease(self):
        from clinical_reasoning.models import ClinicalInsight
        from clinical_reasoning.services.engine import reason_about_patient
        reason_about_patient(self.patient)
        titles = list(ClinicalInsight.objects.filter(
            patient=self.patient).values_list("title", flat=True))
        self.assertFalse([t for t in titles if "IgA" in t], titles)

    def test_no_reasoning_step_names_an_unmatched_disease(self):
        from clinical_reasoning.services.engine import reason_about_patient
        profile = reason_about_patient(self.patient)
        steps = profile.reasoning_chain or []
        self.assertFalse([s for s in steps if "IgA" in str(s)], steps)
