"""
Comprehensive tests for V2 Phase 4 service modules:
rule_validator, rule_tester, evidence_engine, guideline_parser,
guideline_import, knowledge_versioning, authoring.
"""
import datetime as dt
import json

from django.test import TestCase

from patients.models import Patient

from .models import (
    GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion,
    RuleTemplate, RuleReview, RuleTestResult, GuidelineDocument, EvidenceEntry,
)
from .rule_validator import (
    validate_rule_data, check_duplicate_conditions,
    validate_all_entries, ValidationResult,
)
from .rule_tester import test_rule, test_disease_suite, test_all_active_rules
from .evidence_engine import (
    grade_evidence, suggest_evidence_grade,
    generate_citation, GRADE_QUALITY, STRENGTH_MAP,
)
from .guideline_parser import (
    parse_markdown_guideline, parse_json_rules,
    RULE_BLOCK_PATTERN, FIELD_ALIASES,
)
from .guideline_import import (
    import_json_guideline, import_csv_guideline,
    import_yaml_guideline, import_markdown_guideline,
)
from .knowledge_versioning import (
    compute_rule_diff, create_version, rollback_to, version_history,
)
from .authoring import (
    build_rule_data, create_rule, update_rule, apply_template,
)


# =============================================================================
# Helpers
# =============================================================================

def _make_source(**kw):
    defaults = dict(title="KDIGO 2025", abbreviation="KDIGO",
                    version_year=2025, effective_date=dt.date(2025, 1, 1))
    defaults.update(kw)
    return GuidelineSource.objects.create(**defaults)


def _make_entry(source=None, **kw):
    if source is None:
        source = _make_source()
    defaults = dict(
        entry_id="KB-TST-001", disease_id="test",
        rule_data=dict(conditions=[], weight=1, explanation="Test rule"),
        source=source, effective_date=dt.date(2025, 1, 1), status="active",
    )
    defaults.update(kw)
    return KnowledgeBaseEntry.objects.create(**defaults)


# =============================================================================
# Rule Validator Tests
# =============================================================================

class RuleValidatorTests(TestCase):

    def test_validate_valid_rule(self):
        data = {
            "conditions": [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
            "weight": 2, "base_score": 1, "explanation": "Nephrotic-range proteinuria",
        }
        result = validate_rule_data(data, "KB-001")
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_validate_invalid_type(self):
        result = validate_rule_data("not a dict")
        self.assertFalse(result.is_valid)

    def test_validate_empty_conditions_warning(self):
        data = {"conditions": [], "weight": 1, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertTrue(result.is_valid)
        self.assertTrue(any("empty conditions" in w for w in result.warnings))

    def test_validate_zero_weight_warning(self):
        data = {"conditions": [{"field": "x", "operator": "eq", "value": "y"}],
                "weight": 0, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertTrue(result.is_valid)
        self.assertTrue(any("weight is 0" in w for w in result.warnings))

    def test_validate_unknown_field_warning(self):
        data = {"conditions": [{"field": "unknownField", "operator": "eq", "value": "x"}],
                "weight": 1, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertTrue(result.is_valid)
        self.assertTrue(any("unknown" in w for w in result.warnings))

    def test_validate_invalid_operator_error(self):
        data = {"conditions": [{"field": "x", "operator": "invalid_op", "value": "x"}],
                "weight": 1, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertFalse(result.is_valid)

    def test_validate_in_operator_requires_list(self):
        data = {"conditions": [{"field": "x", "operator": "in", "value": "not_a_list"}],
                "weight": 1, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("requires a list" in e for e in result.errors))

    def test_validate_condition_not_dict(self):
        data = {"conditions": ["not_a_dict"], "weight": 1, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertFalse(result.is_valid)

    def test_condition_missing_field(self):
        data = {"conditions": [{"operator": "eq", "value": "x"}],
                "weight": 1, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertTrue(any("missing 'field'" in e for e in result.errors))

    def test_check_duplicate_conditions(self):
        data = {
            "conditions": [
                {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
                {"field": "proteinuria", "operator": "eq", "value": "nephrotic"},
            ],
            "weight": 1,
        }
        result = check_duplicate_conditions(data)
        self.assertTrue(any("duplicate" in w for w in result.warnings))

    def test_validate_all_entries_empty(self):
        results = validate_all_entries()
        self.assertEqual(len(results), 0)

    def test_validate_weight_not_number(self):
        data = {"conditions": [], "weight": "not_a_number", "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertFalse(result.is_valid)

    def test_validate_base_score_extreme_warning(self):
        data = {"conditions": [], "weight": 1, "base_score": 999, "explanation": "Test"}
        result = validate_rule_data(data)
        self.assertTrue(any("unusually large" in w for w in result.warnings))

    def test_validate_missing_explanation_warning(self):
        data = {"conditions": [{"field": "x", "operator": "eq", "value": "y"}], "weight": 1}
        result = validate_rule_data(data)
        self.assertTrue(any("missing explanation" in w for w in result.warnings))


# =============================================================================
# Rule Tester Tests
# =============================================================================

class RuleTesterTests(TestCase):

    def setUp(self):
        self.source = _make_source()
        self.entry = _make_entry(
            source=self.source, entry_id="KB-TST-TESTER-001",
            rule_data={
                "conditions": [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
                "weight": 3, "base_score": 1, "explanation": "Test scoring",
            },
        )

    def test_test_rule_with_features_matching(self):
        result = test_rule(self.entry, features={"proteinuria": "nephrotic"})
        self.assertTrue(result.matched)
        self.assertAlmostEqual(result.actual_score, 4.0)

    def test_test_rule_with_features_not_matching(self):
        entry_no_base = _make_entry(
            source=self.source, entry_id="KB-TST-NOMATCH",
            rule_data={
                "conditions": [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
                "weight": 3, "base_score": 0, "explanation": "No base score",
            },
        )
        result = test_rule(entry_no_base, features={"proteinuria": "none"})
        self.assertFalse(result.matched)
        self.assertAlmostEqual(result.actual_score, 0.0)

    def test_test_rule_with_expected_score(self):
        result = test_rule(self.entry, features={"proteinuria": "nephrotic"}, expected_score=4.0)
        self.assertTrue(result.matched)
        result2 = test_rule(self.entry, features={"proteinuria": "nephrotic"}, expected_score=5.0)
        self.assertFalse(result2.matched)

    def test_test_rule_creates_ruletestresult(self):
        self.assertEqual(RuleTestResult.objects.count(), 0)
        test_rule(self.entry, features={"proteinuria": "nephrotic"})
        self.assertEqual(RuleTestResult.objects.count(), 1)
        r = RuleTestResult.objects.first()
        self.assertEqual(r.entry, self.entry)
        self.assertIn("total_score", r.test_output)

    def test_test_rule_with_patient(self):
        p = Patient.objects.create(name="Test", sex="M")
        result = test_rule(self.entry, patient=p)
        self.assertIsNotNone(result)
        self.assertEqual(result.patient, p)

    def test_test_disease_suite(self):
        _make_entry(source=self.source, entry_id="KB-TST-002", disease_id="test",
                    rule_data={"conditions": [{"field": "x", "operator": "eq", "value": "a"}],
                               "weight": 1, "explanation": "X=A"})
        test_cases = [
            {"features": {"x": "a"}, "expected_top_disease": "test", "min_score": 1},
        ]
        results = test_disease_suite("test", test_cases)
        self.assertGreater(len(results), 0)

    def test_test_all_active_rules(self):
        _make_entry(source=self.source, entry_id="KB-TST-ALL-001",
                    rule_data={"conditions": [{"field": "x", "operator": "eq", "value": "a"}],
                               "weight": 1, "explanation": "All test"},
                    status="active")
        summary = test_all_active_rules()
        self.assertIn("total_tests", summary)
        self.assertIn("passed", summary)
        self.assertIn("pass_rate", summary)


# =============================================================================
# Evidence Engine Tests
# =============================================================================

class EvidenceEngineTests(TestCase):

    def setUp(self):
        self.source = _make_source()
        self.entry = _make_entry(source=self.source)

    def test_grade_evidence_no_entries(self):
        result = grade_evidence(self.entry)
        self.assertEqual(result["entry_id"], self.entry.entry_id)
        self.assertEqual(result["evidence_count"], 0)

    def test_grade_evidence_with_entries(self):
        EvidenceEntry.objects.create(
            entry=self.entry, title="RCT of Treatment",
            authors="Smith J", journal="NEJM", year=2024,
            evidence_level="rct",
        )
        result = grade_evidence(self.entry)
        self.assertEqual(result["evidence_count"], 1)
        self.assertEqual(result["best_evidence_level"], "rct")
        self.assertEqual(result["grade_quality"], "High")

    def test_grade_evidence_meta_analysis_highest(self):
        EvidenceEntry.objects.create(
            entry=self.entry, title="RCT", evidence_level="rct",
        )
        EvidenceEntry.objects.create(
            entry=self.entry, title="Meta", evidence_level="meta",
        )
        result = grade_evidence(self.entry)
        self.assertEqual(result["best_evidence_level"], "meta")

    def test_suggest_evidence_grade_from_rct(self):
        EvidenceEntry.objects.create(
            entry=self.entry, title="Large RCT",
            evidence_level="rct",
        )
        suggested = suggest_evidence_grade(self.entry)
        self.assertEqual(suggested, "1")

    def test_suggest_evidence_grade_from_cohort(self):
        EvidenceEntry.objects.create(
            entry=self.entry, title="Cohort Study",
            evidence_level="cohort",
        )
        suggested = suggest_evidence_grade(self.entry)
        self.assertEqual(suggested, "2")

    def test_suggest_evidence_grade_no_evidence(self):
        suggested = suggest_evidence_grade(self.entry)
        self.assertEqual(suggested, "NG")

    def test_generate_citation_full(self):
        e = EvidenceEntry(
            entry=self.entry, title="Study Title",
            authors="Smith J, Doe J", year=2024,
            journal="NEJM", doi="10.1056/NEJMoa123456",
        )
        citation = generate_citation(e)
        self.assertIn("Smith J, Doe J", citation)
        self.assertIn("(2024)", citation)
        self.assertIn("Study Title", citation)
        self.assertIn("NEJM", citation)
        self.assertIn("doi:10.1056/NEJMoa123456", citation)

    def test_generate_citation_minimal(self):
        e = EvidenceEntry(entry=self.entry, title="Just a Title")
        citation = generate_citation(e)
        self.assertIn("Just a Title", citation)

    def test_grade_evidence_quality_map_values(self):
        self.assertEqual(GRADE_QUALITY["meta"], "High")
        self.assertEqual(GRADE_QUALITY["cohort"], "Moderate")
        self.assertEqual(GRADE_QUALITY["case_control"], "Low")
        self.assertEqual(GRADE_QUALITY["expert"], "Very Low")

    def test_strength_map_values(self):
        self.assertEqual(STRENGTH_MAP["1"], "Strong")
        self.assertEqual(STRENGTH_MAP["2"], "Weak")
        self.assertEqual(STRENGTH_MAP["NG"], "Not graded")


# =============================================================================
# Guideline Parser Tests
# =============================================================================

class GuidelineParserTests(TestCase):

    def setUp(self):
        self.source = _make_source()
        self.doc = GuidelineDocument.objects.create(
            title="Test Guideline", source=self.source,
            document_type="markdown",
            content="# Recommendation Test\n\nIf proteinuria is nephrotic then suspect MN.",
        )

    def test_parse_markdown_guideline(self):
        candidates = parse_markdown_guideline(self.doc)
        self.assertIsInstance(candidates, list)

    def test_parse_markdown_detects_rule_blocks(self):
        content = (
            "# Recommendation: IgA Nephropathy\n\n"
            "Level 1: If proteinuria > 3.5 then high risk.\n\n"
            "## Rule: Membranous\n\n"
            "If albumin < 3.0 then nephrotic.\n"
        )
        self.doc.content = content
        self.doc.save()
        candidates = parse_markdown_guideline(self.doc)
        self.assertGreater(len(candidates), 0)

    def test_parse_json_rules(self):
        data = [
            {"disease_id": "iga", "conditions": [{"field": "x", "operator": "eq", "value": "y"}],
             "weight": 1, "explanation": "Test"},
        ]
        candidates = parse_json_rules(data)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["disease_id"], "iga")

    def test_parse_json_rules_skips_non_dict(self):
        candidates = parse_json_rules([1, "string", None])
        self.assertEqual(len(candidates), 0)

    def test_field_aliases(self):
        self.assertIn("egfr", FIELD_ALIASES)
        self.assertEqual(FIELD_ALIASES["egfr"], "latest_egfr")
        self.assertIn("proteinuria", FIELD_ALIASES)

    def test_rule_block_pattern_compiles(self):
        self.assertIsNotNone(RULE_BLOCK_PATTERN)


# =============================================================================
# Guideline Import Tests
# =============================================================================

class GuidelineImportTests(TestCase):

    def setUp(self):
        self.source = _make_source()

    def test_import_json_guideline(self):
        data = [
            {"disease_id": "iga", "entry_id": "KB-IMP-001",
             "conditions": [{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
             "weight": 2, "explanation": "Test import"},
        ]
        result = import_json_guideline(data, source_abbr="KDIGO", source_year=2025)
        self.assertGreater(result["created"], 0)
        self.assertTrue(KnowledgeBaseEntry.objects.filter(entry_id="KB-IMP-001").exists())

    def test_import_json_guideline_skip_duplicate(self):
        _make_entry(source=self.source, entry_id="KB-IMP-DUP")
        data = [{"disease_id": "test", "entry_id": "KB-IMP-DUP",
                 "conditions": [], "weight": 1, "explanation": "Dup"}]
        result = import_json_guideline(data)
        self.assertGreater(result["skipped"], 0)

    def test_import_csv_guideline(self):
        csv_content = "disease_id,conditions_json,weight,explanation,entry_id\n" \
                      "test,\"[{\"\"field\"\":\"\"x\"\",\"\"operator\"\":\"\"eq\"\",\"\"value\"\":\"\"y\"\"}]\",1,CSV Test,KB-CSV-001\n"
        result = import_csv_guideline(csv_content, source_abbr="KDIGO", source_year=2025)
        self.assertGreater(result["created"], 0)

    def test_import_csv_guideline_no_conditions(self):
        csv_content = "disease_id,weight,explanation,entry_id\n" \
                      "test,1,No condition JSON,KB-CSV-NOCOND\n"
        result = import_csv_guideline(csv_content)
        self.assertGreater(result["created"], 0)

    def test_import_yaml_guideline(self):
        yaml_content = """
rules:
  - disease_id: test
    entry_id: KB-YAML-001
    conditions:
      - field: x
        operator: eq
        value: y
    weight: 1
    explanation: YAML import test
source:
  abbreviation: KDIGO
  year: 2025
"""
        result = import_yaml_guideline(yaml_content)
        self.assertGreater(result["created"], 0)

    def test_import_markdown_guideline(self):
        doc = GuidelineDocument.objects.create(
            title="Markdown Test", source=self.source,
            document_type="markdown",
            content="# Recommendation Test\n\nIf proteinuria is nephrotic then risk.",
        )
        result = import_markdown_guideline(doc)
        self.assertIsNotNone(result)
        self.assertIn("created", result)

    def test_import_json_guideline_error_handling(self):
        data = [{"disease_id": "test", "entry_id": "KB-ERR",
                 "conditions": "invalid", "weight": 1, "explanation": "Err"}]
        result = import_json_guideline(data)
        self.assertIsNotNone(result)


# =============================================================================
# Knowledge Versioning Tests
# =============================================================================

class KnowledgeVersioningTests(TestCase):

    def setUp(self):
        self.source = _make_source()
        self.entry = _make_entry(source=self.source)

    def test_compute_rule_diff_no_changes(self):
        diff = compute_rule_diff(
            {"conditions": [], "weight": 1, "explanation": "X"},
            {"conditions": [], "weight": 1, "explanation": "X"},
        )
        self.assertFalse(diff["conditions_changed"])
        self.assertFalse(diff["weight_changed"])
        self.assertFalse(diff["explanation_changed"])

    def test_compute_rule_diff_conditions_added(self):
        old = {"conditions": [{"field": "a", "operator": "eq", "value": "x"}], "weight": 1}
        new = {"conditions": [{"field": "a", "operator": "eq", "value": "x"},
                               {"field": "b", "operator": "eq", "value": "y"}], "weight": 1}
        diff = compute_rule_diff(old, new)
        self.assertTrue(diff["conditions_changed"])
        self.assertEqual(len(diff["added_conditions"]), 1)
        self.assertEqual(len(diff["removed_conditions"]), 0)

    def test_compute_rule_diff_conditions_removed(self):
        old = {"conditions": [{"field": "a", "operator": "eq", "value": "x"},
                               {"field": "b", "operator": "eq", "value": "y"}], "weight": 1}
        new = {"conditions": [{"field": "a", "operator": "eq", "value": "x"}], "weight": 1}
        diff = compute_rule_diff(old, new)
        self.assertTrue(diff["conditions_changed"])
        self.assertEqual(len(diff["removed_conditions"]), 1)

    def test_compute_rule_diff_weight_changed(self):
        old = {"conditions": [], "weight": 1}
        new = {"conditions": [], "weight": 5}
        diff = compute_rule_diff(old, new)
        self.assertTrue(diff["weight_changed"])
        self.assertEqual(diff["changed_fields"]["weight"]["from"], 1)
        self.assertEqual(diff["changed_fields"]["weight"]["to"], 5)

    def test_compute_rule_diff_explanation_changed(self):
        old = {"conditions": [], "weight": 1, "explanation": "Old"}
        new = {"conditions": [], "weight": 1, "explanation": "New"}
        diff = compute_rule_diff(old, new)
        self.assertTrue(diff["explanation_changed"])

    def test_create_version_first(self):
        version = create_version(self.entry, change_summary="Initial", user=None)
        self.assertEqual(version.version_number, 1)
        self.assertEqual(version.entry, self.entry)
        self.assertEqual(version.change_summary, "Initial")

    def test_create_version_increments_number(self):
        create_version(self.entry, "v1")
        create_version(self.entry, "v2")
        v3 = create_version(self.entry, "v3")
        self.assertEqual(v3.version_number, 3)

    def test_create_version_with_diff(self):
        create_version(self.entry, "Original")
        self.entry.rule_data["weight"] = 5
        self.entry.save()
        v = create_version(self.entry, "Changed weight")
        self.assertIn("weight_changed", v.rule_data_diff)

    def test_rollback_to(self):
        original_data = dict(self.entry.rule_data)
        create_version(self.entry, "v1")

        self.entry.rule_data = {"conditions": [], "weight": 99, "explanation": "Changed"}
        self.entry.save()
        create_version(self.entry, "v2")

        v1 = KnowledgeBaseVersion.objects.get(entry=self.entry, version_number=1)
        rollback_to(self.entry, v1)

        self.entry.refresh_from_db()
        self.assertEqual(self.entry.rule_data["weight"], original_data["weight"])

    def test_version_history(self):
        create_version(self.entry, "v1")
        create_version(self.entry, "v2")
        history = version_history(self.entry)
        self.assertEqual(len(history), 2)
        self.assertIn("version", history[0])
        self.assertIn("diff", history[0])


# =============================================================================
# Authoring Tests
# =============================================================================

class AuthoringTests(TestCase):

    def setUp(self):
        self.source = _make_source()

    def test_build_rule_data(self):
        data = build_rule_data(
            conditions=[{"field": "x", "operator": "eq", "value": "y"}],
            weight=2, base_score=1, explanation="Test",
        )
        self.assertEqual(data["weight"], 2)
        self.assertEqual(data["base_score"], 1)
        self.assertEqual(len(data["conditions"]), 1)

    def test_create_rule_minimal(self):
        entry = create_rule(
            entry_id="KB-AUTH-001", disease_id="test",
            conditions=[{"field": "proteinuria", "operator": "eq", "value": "nephrotic"}],
            explanation="Test create rule",
        )
        self.assertEqual(entry.entry_id, "KB-AUTH-001")
        self.assertEqual(entry.disease_id, "test")
        self.assertEqual(entry.status, KnowledgeBaseEntry.Status.DRAFT)
        self.assertEqual(entry.evidence_grade, "NG")

    def test_create_rule_with_source(self):
        entry = create_rule(
            entry_id="KB-AUTH-002", disease_id="iga",
            conditions=[{"field": "x", "operator": "eq", "value": "y"}],
            source_abbr="KDIGO", source_year=2025,
        )
        self.assertEqual(entry.source.abbreviation, "KDIGO")

    def test_create_rule_with_tags(self):
        entry = create_rule(
            entry_id="KB-AUTH-TAG", disease_id="test",
            conditions=[{"field": "x", "operator": "eq", "value": "y"}],
            explanation="Tags test", tags=["pediatric", "urgent"],
        )
        self.assertIn("pediatric", entry.tags)
        self.assertIn("urgent", entry.tags)

    def test_create_rule_validates(self):
        with self.assertRaises(ValueError):
            create_rule(
                entry_id="KB-AUTH-INV", disease_id="test",
                conditions=["not", "valid", "conditions"],
                explanation="Should fail validation",
            )

    def test_update_rule(self):
        entry = _make_entry(source=self.source, entry_id="KB-AUTH-UPD")
        updated = update_rule(entry, weight=10, change_summary="Increased weight")
        self.assertEqual(updated.rule_data["weight"], 10)
        self.assertTrue(KnowledgeBaseVersion.objects.filter(entry=entry).exists())

    def test_update_rule_creates_version(self):
        entry = _make_entry(source=self.source, entry_id="KB-AUTH-UPD-VER")
        self.assertEqual(entry.versions.count(), 0)
        update_rule(entry, explanation="Updated explanation", change_summary="Changed expl")
        self.assertEqual(entry.versions.count(), 1)

    def test_apply_template(self):
        template = RuleTemplate.objects.create(
            template_id="TMPL-001", name="Test Template",
            category="diagnostic", description="A test template",
            condition_schema={
                "fields": [
                    {"field": "proteinuria", "operator": "eq", "default": "nephrotic"},
                    {"field": "albumin", "operator": "eq", "default": "low"},
                ]
            },
        )
        entry = apply_template(template, disease_id="test", values={})
        self.assertIsNotNone(entry)
        self.assertEqual(entry.rule_type, "diagnostic")
        conditions = entry.rule_data.get("conditions", [])
        self.assertGreater(len(conditions), 0)

    def test_apply_template_with_custom_values(self):
        template = RuleTemplate.objects.create(
            template_id="TMPL-002", name="Custom Template",
            category="treatment",
            condition_schema={
                "fields": [
                    {"field": "egfr", "operator": "gte", "default": 30},
                ]
            },
        )
        entry = apply_template(template, disease_id="test",
                                values={"egfr": 45, "weight": 3})
        self.assertIsNotNone(entry)
        conditions = entry.rule_data.get("conditions", [])
        self.assertEqual(conditions[0]["value"], 45)


# =============================================================================
# Model Integration Tests
# =============================================================================

class NewModelTests(TestCase):

    def test_rule_template_creation(self):
        t = RuleTemplate.objects.create(
            template_id="RT-001", name="Test Template", category="diagnostic",
        )
        self.assertEqual(str(t), "RT-001 — Test Template")

    def test_rule_template_category_choices(self):
        for val, _ in RuleTemplate.Category.choices:
            t = RuleTemplate.objects.create(
                template_id=f"RT-{val}", name=val, category=val,
            )
            self.assertEqual(t.category, val)

    def test_rule_review_creation(self):
        source = _make_source()
        entry = _make_entry(source=source)
        review = RuleReview.objects.create(
            entry=entry, status=RuleReview.ReviewStatus.PENDING,
        )
        self.assertEqual(str(review), f"Review {entry.entry_id} — Pending review")

    def test_rule_review_status_transitions(self):
        source = _make_source()
        entry = _make_entry(source=source)
        r = RuleReview.objects.create(entry=entry)
        for val, _ in RuleReview.ReviewStatus.choices:
            r.status = val
            r.save()
            r.refresh_from_db()
            self.assertEqual(r.status, val)

    def test_rule_test_result_str(self):
        source = _make_source()
        entry = _make_entry(source=source)
        r = RuleTestResult.objects.create(
            entry=entry, actual_score=4.0, matched=True,
            test_input={}, test_output={},
        )
        self.assertIn(entry.entry_id, str(r))

    def test_guideline_document_creation(self):
        source = _make_source()
        doc = GuidelineDocument.objects.create(
            title="Test Doc", source=source,
            content="# Test", document_type="markdown",
        )
        self.assertEqual(str(doc), "Test Doc (Pending)")
        self.assertEqual(doc.import_status, GuidelineDocument.ImportStatus.PENDING)

    def test_guideline_document_import_status_transitions(self):
        source = _make_source()
        for val, _ in GuidelineDocument.ImportStatus.choices:
            doc = GuidelineDocument.objects.create(
                title=f"Doc {val}", source=source,
                import_status=val,
            )
            self.assertEqual(doc.import_status, val)

    def test_evidence_entry_creation(self):
        source = _make_source()
        entry = _make_entry(source=source)
        ev = EvidenceEntry.objects.create(
            entry=entry, title="Test Study",
            authors="Author A", journal="Test Journal",
            year=2024, evidence_level="rct",
        )
        self.assertIn("Test Study", str(ev))
        self.assertEqual(ev.evidence_level, "rct")

    def test_evidence_entry_level_choices(self):
        source = _make_source()
        entry = _make_entry(source=source)
        for val, _ in EvidenceEntry.EvidenceLevel.choices:
            ev = EvidenceEntry.objects.create(
                entry=entry, title=f"Study {val}",
                evidence_level=val,
            )
            self.assertEqual(ev.evidence_level, val)

    def test_knowledgebaseentry_rule_type_field(self):
        source = _make_source()
        entry = _make_entry(source=source, rule_type="treatment")
        self.assertEqual(entry.rule_type, "treatment")
        entry2 = _make_entry(source=source, entry_id="KB-TYP-002", rule_type="monitoring")
        self.assertEqual(entry2.rule_type, "monitoring")

    def test_knowledgebaseentry_tags_field(self):
        source = _make_source()
        entry = _make_entry(source=source, tags=["pediatric", "urgent"])
        self.assertIn("pediatric", entry.tags)
        entry3 = _make_entry(source=source, entry_id="KB-TAG-003", tags=[])
        self.assertEqual(entry3.tags, [])

    def test_knowledgebaseversion_rule_data_diff(self):
        source = _make_source()
        entry = _make_entry(source=source)
        v = KnowledgeBaseVersion.objects.create(
            entry=entry, version_number=1,
            rule_data=entry.rule_data,
            rule_data_diff={"weight_changed": False, "conditions_changed": False},
        )
        self.assertIn("weight_changed", v.rule_data_diff)
