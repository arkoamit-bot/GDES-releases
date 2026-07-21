# GDES Continuous Knowledge Improvement

**Version:** 7.0
**Date:** 2026-07-11

## 1. Purpose

Every disagreement between clinician and AI should become structured feedback that improves the knowledge base.

## 2. Feedback Loop

1. Clinician overrides an AI recommendation (`RecommendationAudit.approval_status = "overridden"`)
2. Override reason captured (`RecommendationAudit.override_reason`)
3. Clinician documents final diagnosis (`Patient.primary_diagnosis`)
4. Outcome recorded (`Patient.outcome` or `ClinicalProfile` update)
5. Knowledge base reviewed for improvement opportunities
6. Rules updated, tested, approved, activated

## 3. Feedback Categories

| Category | Description | Action |
|----------|-------------|--------|
| Rule Inaccurate | KB rule produces wrong recommendation | Update rule conditions/weights |
| Guideline Outdated | Rule references old guideline version | Update source and rule_data |
| Missing Rule | Clinical scenario not covered by KB | Create new rule |
| Override Justified | Clinician override was clinically appropriate | Review rule for potential update |
| Override Incorrect | Clinician override was clinically inappropriate | Flag for educational review |

## 4. Knowledge Review Process

1. Monthly: export all overrides from `RecommendationAudit`
2. Categorize by feedback category
3. Prioritize: high-impact rules first (frequently overridden, high-severity)
4. Draft rule changes in DRAFT status
5. Clinical review (`RuleReview` model)
6. Approval (`KnowledgeBaseEntry.transition_to("approved")`)
7. Activation (`KnowledgeBaseEntry.transition_to("active")`)
8. Version bump (`KnowledgeBaseVersion` snapshot)

## 5. Automated Quality Indicators

- Rules with >20% override rate → flagged for review
- Rules with `evidence_grade = "OP"` → flagged for evidence upgrade
- Rules with `next_review_date < today` → flagged for re-review
- Rules in DRAFT >90 days → escalation

## 6. Knowledge Dashboard

`GET /api/v1/knowledge-base/governance_stats/` provides:

- Override rate per disease
- Override rate per rule type
- Rules needing re-review
- Evidence grade distribution
- Approval coverage

## 7. Integration with Pilot

- Every override becomes a structured data point
- Monthly knowledge review meetings
- Quarterly KB version releases
- Annual comprehensive guideline alignment review
