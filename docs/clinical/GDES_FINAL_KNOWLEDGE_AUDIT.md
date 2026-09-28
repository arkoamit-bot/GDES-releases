# GDES_FINAL_KNOWLEDGE_AUDIT.md

**System:** GDES
**Reviewer:** Claude Code (independent)
**Date:** 2026-07-12
**Scope:** Knowledge base architecture, rule execution, governance, explainability.
**Method:** `knowledge/` source + live `db.sqlite3` (625 KnowledgeBaseEntry rows).

---

## 1. What is actually in the knowledge base (live DB)

| Metric | Value |
|--------|-------|
| Total `KnowledgeBaseEntry` | 625 |
| ACTIVE | 618 |
| DRAFT | 7 |
| Distinct diseases (`disease_id`) | 23 |
| Rule types | diagnostic, treatment, monitoring, pathophysiology, etc. (entry-id prefixes `KB-*`, `IRGN-`, `TCMR-`, `MPGN-`, `CRYO-`, `DKD-*`, `CNI-*`, `BKV-*`, `AMR-*`, `HIV-*`, `FGN-*`, plus `TEST-*`) |

This is a **substantial, genuinely broad** body of nephrology knowledge — well
beyond the "18 diseases" claimed, spanning native GN, transplant rejection
(TCMR/AMR), BK virus, and drug-induced entities. The clinical **content** in the
treatment planner (`management_plan.py`) is **high quality and current** — e.g.
IgAN: RAASi + SGLT2i foundation, sparsentan (PROTECT), targeted-release
budesonide (NefIgArd); MN: rituximab first-line for PLA2R+ (MENTOR), Ponticelli
protocol. Evidence citations to named trials are present and correct.

---

## K-1 — Rule execution engine

`knowledge/services.py` implements a clean condition evaluator
(`_evaluate_condition`, 11 operators) that scores diseases by summing rule
weights over matched conditions (`evaluate_patient_rules`). Verified working
against the live DB: the differential populates with real `disease_id`s and
9-disease rankings per patient. **The engine itself is sound and traceable** —
each matched rule carries its condition, weight, source, and evidence grade.

**K-1a (minor).** Feature/condition-format coupling: `extract_patient_features`
emits categorical proteinuria (`"nephrotic"`/`"subnephrotic"`/`"none"`,
services.py:98-104), while the module docstring advertises numeric proteinuria
conditions (`gte 3.5`). Numeric conditions on `proteinuria` would silently
evaluate false (`float("nephrotic")` → caught → `False`). Rules must be authored
against the categorical vocabulary the extractor actually produces. Confirm all
618 ACTIVE rules use fields/values the extractor emits; any that don't are dead
weight that never fires.

**K-1b (minor).** `disease_name = entry.entry_id` (services.py:341) puts raw IDs
where a human disease name is expected downstream.

---

## K-2 — Governance metadata: schema present, sign-off absent (MAJOR)

The `KnowledgeBaseEntry` schema is **excellent** — it has columns for
`evidence_grade`, `source`, `guideline_chapter`, `guideline_paragraph`,
`guideline_quote`, `evidence_url`, `confidence_score`, `recommendation_id`,
`author`, `approved_by`, `approved_at`, `date_validated`, `next_review_date`,
`override_allowed`, `knowledge_version`. This is exactly the right structure for
clinical governance.

**But the shipped data leaves the governance-critical fields empty:**

| Field | Populated / 625 | Assessment |
|-------|-----------------|------------|
| `source_id` (guideline source) | 625 | ✅ every rule cites a source |
| `evidence_grade` | 625 | ✅ graded (1A…OP distribution present) |
| `guideline_quote` | 33 | ⚠️ only 5% quote the guideline |
| `evidence_url` | 4 | ⚠️ ~0% link the evidence |
| `confidence_score` | 625 but **all = 0.0** | ❌ meaningless — the "confidence score" shown to clinicians is always zero |
| `recommendation_id` | 0 | ❌ traceability id never populated |
| `explanation` | 0 | ❌ empty |
| `author_id` | 0 | ❌ no author of record |
| `approved_by_id` | 0 | ❌ **no rule has been approved by a named reviewer** |
| `date_validated` | 0 | ❌ no validation date |
| `next_review_date` | 0 | ❌ no review schedule |
| `RecommendationAudit` rows | 0 | (expected pre-pilot — override trail never exercised) |

**Interpretation for the audit's Section 3 checklist:**

- Guideline reference / version / evidence grade / evidence source → **present**.
- Recommendation ID / confidence score / validation date / reviewer / review
  schedule → **missing or placeholder** across the entire base.

So the *governance layer exists structurally but has not been operated*: **no
human has signed off on any of the 618 active rules, none carries a validation
date or a review-due date, and the confidence score is a constant 0.0.** For a
system whose value proposition is "explainable, governed decision support," this
is the single most important governance gap.

---

## K-3 — Explainability

Structurally strong. Every recommendation can answer:

- **Why / which features?** — `MatchedRule` records the exact condition and
  weight (services.py:224-233); `reasoning_chain` and `evidence_summary` are
  stored on the profile (`engine.py:120-121`).
- **Which guideline / evidence?** — `source`, `guideline_chapter/paragraph`,
  `evidence_grade` on each entry.
- **Can the clinician override?** — `override_allowed = True` on all 625 rows;
  `RecommendationAudit` model exists to log overrides.
- **How confident?** — **this is the weak link:** `confidence_score` is always
  0.0, so any UI "confidence" figure is not real (the differential's separate
  score is real; the governance confidence is not).

No "black box": the reasoning is rule-based and inspectable. The gap is that the
*populated* explainability (confidence, quotes, validation) does not match the
*designed* explainability.

---

## K-4 — Rule lifecycle & test/production separation

- Lifecycle machinery exists: `status` (draft/active/retired),
  `effective_date`, `retired_date`, `knowledge_versioning.py`, `authoring.py`,
  `rule_validator.py`, `rule_tester.py`, management commands
  (`validate_rules`, `run_rule_tests`, `activate_entries`).
- **But** `TEST-*` and other fixture rules are ACTIVE alongside production rules
  in the live DB. The canonical pilot seed is ambiguous (four seed commands
  exist). Before freeze: designate one seed as authoritative, retire test rules,
  and re-run `validate_rules`.

---

## Knowledge verdict

**Content: strong. Engine: sound and explainable. Governance operation:
incomplete.** The knowledge base is robust enough to *support* a pilot, but it
must not be presented as "clinically governed / reviewer-validated" until at
least the following are done for the active set: a named clinical reviewer
approves the rules (`approved_by`, `date_validated`), a real `confidence_score`
is set (or the field is hidden), and a `next_review_date` schedule is
established. See `GDES_FINAL_RECOMMENDATIONS.md` G-1…G-3.
