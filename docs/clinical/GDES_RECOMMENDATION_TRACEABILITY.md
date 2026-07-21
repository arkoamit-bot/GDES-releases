# GDES Recommendation Traceability

**Version:** 7.0
**Date:** 2026-07-11

## 1. Purpose

Every AI recommendation must be fully transparent and traceable. This document describes the traceability system that ensures every recommendation produced by GDES can be audited, reviewed, and governed throughout its lifecycle.

## 2. Traceability Panel

A dedicated "Traceability" tab on the patient detail page displays every recommendation audit record. Each record contains:

| Field | Description | Source |
|-------|-------------|--------|
| Recommendation | Human-readable recommendation text | `recommendation_text` |
| Clinical Rationale | Why this recommendation was made | `clinical_rationale` |
| Guideline | Which clinical guideline | `guideline` |
| Guideline Version | Year/version of the guideline | `guideline_version` |
| Guideline Section | Specific section reference | `guideline_section` |
| Recommendation ID | Unique guideline recommendation ID | `guideline_recommendation_id` |
| Evidence Grade | GRADE evidence level (1/2/NG/OP) | `evidence_grade` |
| Evidence Source | URL/DOI to supporting evidence | `evidence_source` |
| Confidence Score | AI confidence (0–100%) | `confidence_score` |
| KB Rule ID | Knowledge base rule identifier | `kb_rule_id` |
| KB Version | Knowledge base version | `knowledge_version` |
| Date Validated | When this recommendation was validated | `validation_date` |
| Next Review Date | Scheduled re-review date | `next_review_date` |
| Expert Reviewer | Who reviewed this recommendation | `expert_reviewer` |
| Approval Status | pending / approved / rejected / overridden | `approval_status` |
| Override | Clinician can override with reason | `override_allowed` + `override_reason` |
| Explanation | Full reasoning chain | `explanation` |

## 3. Audit Trail

Every recommendation-producing service creates a `RecommendationAudit` record:

| Service Method | Audit Category |
|----------------|----------------|
| `reason()` | CLINICAL_REASONING |
| `management_plan()` | MANAGEMENT_PLAN |
| `monitoring_plan()` | MONITORING_PLAN |
| `investigation_recommendations()` | INVESTIGATION |
| `drug_toxicity()` | DRUG_TOXICITY |
| `treatment_failure()` | TREATMENT_FAILURE |
| `relapse_detection()` | TREATMENT_FAILURE |

## 4. Override Mechanism

- Every recommendation displays an **Override** button when `override_allowed=True`.
- Override requires a free-text reason, captured in `override_reason`.
- Override changes `approval_status` to `"overridden"`.
- Full audit trail is preserved — original recommendation and override reason are both retained.

## 5. Knowledge Governance

`GET /api/v1/knowledge-base/governance_stats/` returns:

- **Status breakdown** — draft / under_review / approved / active / superseded / archived / retired
- **Governance coverage** — author, approval, confidence, explanation, recommendation_id, next_review_date
- **Review workflow metrics** — items pending review, overdue reviews, time-to-approval
- **Override statistics** — total overrides, override rate, top override reasons
- **Recommendation audit stats** — records by category, approval distribution, average confidence

## 6. Backend Implementation

| Component | Description |
|-----------|-------------|
| `RecommendationAudit` model | 25+ fields covering all traceability data |
| `audit.py` helper | 7 audit functions — one per recommendation type |
| ClinicalProfileViewSet | All endpoints wired to create audit records |
| `RecommendationAuditAdmin` | Admin actions for approve / reject / override |
