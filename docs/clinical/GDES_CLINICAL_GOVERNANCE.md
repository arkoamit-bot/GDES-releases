# GDES Clinical Governance Framework

**Version:** 6.5 Release Candidate
**Date:** 2026-07-11

---

## 1. Purpose

Every AI recommendation must be transparent, auditable, and trustworthy. This document describes the governance framework that ensures clinical safety.

## 2. Recommendation Audit Trail

The `RecommendationAudit` model (`knowledge/models.py`) captures every recommendation with:

- **Unique identifiers:** `recommendation_id`, `kb_rule_id`, `kb_version`
- **Classification:** `recommendation_type` — one of `investigation`, `drug_toxicity`, `treatment_failure`, `management_plan`, `monitoring_plan`, `followup`, `disease_validation`, `clinical_reasoning`
- **Patient and clinician:** Foreign keys to patient and clinician records
- **Clinical content:** `disease_id`, `recommendation_text`, `clinical_rationale`
- **Guideline linkage:** `guideline`, `guideline_version`, `guideline_section`, `guideline_recommendation_id`
- **Evidence:** `evidence_grade`, `evidence_source`
- **Confidence and reasoning:** `confidence_score`, `explanation` (full reasoning chain)
- **Validation lifecycle:** `validation_date`, `next_review_date`, `expert_reviewer`
- **Approval status:** One of `pending`, `approved`, `rejected`, `overridden`
- **Override capability:** `override_allowed` (boolean), `override_reason` (text, required when overridden)
- **Timestamps:** `issued_at`, `reviewed_at`

## 3. Knowledge Base Governance

The `KnowledgeBaseEntry` model includes governance fields:

| Field | Description |
|---|---|
| `author` | FK — original rule author |
| `approved_by` | FK — clinical reviewer who approved |
| `approved_at` | Timestamp of approval |
| `next_review_date` | Scheduled re-review date |
| `confidence_score` | AI confidence level (0–100) |
| `explanation` | Human-readable reasoning |
| `override_allowed` | Whether clinician may override |
| `recommendation_id` | Guideline recommendation ID |
| `knowledge_version` | KB version when rule was created |
| `date_validated` | Last validation date |

Existing fields retained: `source` (GuidelineSource FK), `evidence_grade`, `guideline_chapter`, `guideline_paragraph`, `guideline_quote`, `evidence_url`, `status` (7-state lifecycle with `VALID_TRANSITIONS` state machine), `transition_to()` method.

## 4. Lifecycle States

Seven states govern every knowledge base entry:

```
DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → SUPERSEDED
                                            → RETIRED
                                            → ARCHIVED
```

Valid transitions are enforced by the `VALID_TRANSITIONS` dictionary and the `transition_to()` method. Any invalid transition attempt raises an error.

## 5. Evidence Grading

GRADE-based evidence levels are applied to all recommendations:

| Level | Classification | Source Types |
|---|---|---|
| 1 | Strong | Randomised controlled trials, meta-analyses |
| 2 | Weak | Cohort studies, case-control studies |
| Not Graded | — | Expert consensus |
| Opinion | — | Clinical expert opinion |

## 6. Override Mechanism

Every recommendation carries an `override_allowed` boolean. If a clinician overrides a recommendation:

1. `override_reason` must be captured.
2. `approval_status` changes to `"overridden"`.
3. The full audit trail is preserved.

## 7. Review Workflow

The `RuleReview` model governs peer review of knowledge base entries:

**States:** `PENDING` → `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`

- The reviewer must be an authenticated user.
- Review notes are captured with the review record.
- Each review is version-linked for audit trail integrity.

## 8. Dashboard Metrics

`GET /api/v1/knowledge-base/governance_stats/` returns:

- **Status breakdown:** Counts across all 7 lifecycle states.
- **Evidence grade distribution:** Breakdown by evidence level.
- **Governance coverage:** Entries with author assigned, approved, confidence score, explanation, recommendation ID, and next review date.
- **Review workflow metrics:** Pending, approved, rejected counts and approval rate.
- **Re-review alerts:** Entries overdue for review and approvals pending re-review.
- **Override statistics:** Total overrides and override rate.
- **Recommendation audit stats:** Approval status breakdown, override rate, average confidence score.
- **Version activity:** Count of entries never versioned.

## 9. Admin Integration

- **`RecommendationAuditAdmin`:** Configurable `list_display`, `list_filter`, and admin actions for approve, reject, and mark-overridden workflows.
- **`KnowledgeBaseEntryAdmin`:** Existing lifecycle transition actions retained.

## 10. Guideline Traceability

Every recommendation links back to its originating guideline through:

- **Source:** Guideline title, abbreviation, and year.
- **Location:** Guideline chapter, paragraph, and verbatim quote.
- **Evidence:** Evidence grade and evidence URL/DOI.
- **Knowledge base:** Rule ID and version within the KB.
