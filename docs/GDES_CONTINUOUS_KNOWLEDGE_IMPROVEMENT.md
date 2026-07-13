# GDES Continuous Knowledge Improvement

**Version:** 7.1  
**Date:** 2026-07-12  
**Status:** Draft  
**Author:** GDES Clinical Informatics Team

---

## 1. Purpose

The GDES knowledge base encodes clinical reasoning rules for glomerular diseases. Like any clinical system, its accuracy degrades over time as guidelines evolve, new evidence emerges, and clinical practice shifts. This document defines the continuous knowledge improvement framework — the closed-loop process by which every clinician interaction with the system feeds back into knowledge base quality, ensuring that GDES recommendations remain clinically valid, evidence-based, and trustworthy.

## 2. Philosophy

Knowledge improvement in GDES follows three principles:

1. **Every disagreement is a learning opportunity.** When a clinician overrides an AI recommendation, the system captures structured feedback that feeds into rule improvement — not as a passive log, but as an actionable data pipeline.
2. **Versioned and reversible.** Every knowledge base change is versioned, auditable, and reversible. No rule is modified without a trace, and no activation occurs without review.
3. **Clinician-in-the-loop.** The knowledge base evolves through clinician oversight, not automated retraining. Rules are drafted, reviewed, approved, and activated through a governed workflow — maintaining clinical accountability for every recommendation the system produces.

## 3. Current Feedback Mechanism

The existing feedback loop captures clinician behaviour through the `RecommendationAudit` model and its associated workflow:

### 3.1 Capture Stage
When the clinical reasoning engine generates a recommendation, a `RecommendationAudit` record is created with:
- Full recommendation text and clinical rationale
- Guideline linkage (source, version, section, recommendation ID)
- Evidence grade and AI confidence score
- Knowledge base rule ID and version

### 3.2 Clinician Response
The clinician reviews the recommendation and selects one of four approval statuses:

| Status | Meaning | Feedback Signal |
|--------|---------|----------------|
| `pending` | Not yet reviewed | — |
| `approved` | Clinician agrees with the recommendation | Positive validation |
| `rejected` | Clinician rejects the recommendation | Disagreement — requires reason |
| `overridden` | Clinician accepts the recommendation but modifies the action | Partial agreement — requires reason |

### 3.3 Override Reason Capture
When a recommendation is overridden, the clinician documents:
- The override reason (free-text field: `RecommendationAudit.override_reason`)
- The final clinical action taken

### 3.4 Patient Outcomes
The clinician records the final diagnosis (`Patient.primary_diagnosis`) and clinical outcomes (`ClinicalProfile` updates), creating the ground-truth data against which rule accuracy can be assessed.

## 4. Enhanced Feedback Loop

The enhanced feedback loop extends the current mechanism into a structured, multi-stage pipeline:

### Stage 1: Data Collection
- `RecommendationAudit` records capture every recommendation and clinician response.
- `ClinicalProfile` updates capture evolving patient state.
- `Patient.primary_diagnosis` and outcome records capture ground truth.
- Lab results, pathology data, and treatment responses provide outcome signals.

### Stage 2: Feedback Aggregation
- Monthly export of all `RecommendationAudit` records.
- Aggregation by disease, rule type, recommendation type, and clinician.
- Computation of override rates, approval rates, and rejection rates per rule.
- Trend analysis: override rate changes over time for individual rules.

### Stage 3: Categorisation
Each feedback instance is classified into one of the defined feedback categories (Section 5).
- Automated pre-classification based on override reason text and recommendation outcome.
- Manual review and correction by the knowledge team.
- Categorisation drives prioritisation and response type.

### Stage 4: Prioritisation
Rules are prioritised for review based on:
- **Override frequency:** Rules with > 20% override rate are flagged.
- **Clinical severity:** High-impact rules (treatment, safety) reviewed before low-impact rules (informational).
- **Evidence grade:** Rules with `evidence_grade = "OP"` (expert opinion) are flagged for evidence upgrade.
- **Age:** Rules not reviewed within their `next_review_date` are escalated.
- **Patient volume:** Rules affecting more patients receive higher priority.

### Stage 5: Drafting Changes
Knowledge team drafts rule modifications:
- Create a new `KnowledgeBaseEntry` version with updated `rule_data`.
- Document changes in `KnowledgeBaseVersion.change_summary` and `rule_data_diff`.
- Changes stored in DRAFT status until reviewed.

### Stage 6: Clinical Review
- Draft rules reviewed by at least one nephrologist (consultant level).
- Review tracked through `RuleReview` model with approval chain.
- Reviewer assesses: clinical accuracy, guideline alignment, evidence quality, risk of harm.

### Stage 7: Testing
- Draft rules tested against gold-standard clinical cases using `RuleTestResult`.
- Regression testing: all existing active test cases re-run to detect unintended consequences.
- Test results must pass before activation (Section 10).

### Stage 8: Activation
- Approved rules transitioned through `KnowledgeBaseEntry.transition_to("active")`.
- Previous version superseded or retired as appropriate.
- Version snapshot captured in `KnowledgeBaseVersion`.

### Stage 9: Monitoring
- Post-activation monitoring of override rates for newly modified rules.
- 30-day monitoring window for each rule change.
- Regression alerts if override rate exceeds pre-change baseline by > 10 percentage points.

## 5. Feedback Categories

| Category | Description | Example | Action |
|----------|-------------|---------|--------|
| **Rule Inaccurate** | KB rule produces a recommendation inconsistent with clinical evidence | Rule recommends immunosuppression for IgAN patients with crescentic pattern, but current KDIGO recommends plasmapheresis first | Update rule conditions and weights |
| **Guideline Outdated** | Rule references an old guideline version or superseded recommendation | Rule cites KDIGO 2012 when KDIGO 2021 is current | Update `source`, `rule_data`, and guideline linkage fields |
| **Missing Rule** | Clinical scenario not covered by any active rule | No rule for concurrent anti-GBM and ANCA positivity | Create new rule with appropriate conditions |
| **Override Justified** | Clinician override was clinically appropriate given patient context | AI recommended rituximab but patient had active hepatitis B — clinician appropriately deferred | Review rule for addition of exclusion criteria |
| **Override Incorrect** | Clinician override was clinically inappropriate | Clinician declined nephrology referral for rapidly declining eGFR | Flag for educational review (non-punitive) |
| **Edge Case** | Rule produces correct recommendation in most cases but fails for unusual presentations | Rule does not account for pediatric IgAN patients | Refine rule conditions or add paediatric sub-rules |
| **Interaction Gap** | Drug-drug interaction or disease-drug interaction not flagged by the system | Mycophenolate prescribed without checking for concurrent live vaccination | Add interaction detection rule |
| **False Positive Alert** | System generates an alert that is clinically irrelevant in context | Drug toxicity alert for low-dose corticosteroid use that is within acceptable range | Adjust alert thresholds or add context-aware suppression |

## 6. Knowledge Review Process

### 6.1 Monthly Review Cycle

| Week | Activity | Responsible |
|------|----------|-------------|
| Week 1 | Export and aggregate override/rejection data from `RecommendationAudit` | Knowledge team (automated) |
| Week 2 | Categorise feedback, prioritise rules for review | Knowledge team + clinical lead |
| Week 3 | Draft rule changes, run test cases | Knowledge team |
| Week 4 | Clinical review, approval/rejection, activation decisions | Clinical advisory board |

### 6.2 Quarterly Release Cycle
- Every 3 months, all approved rule changes bundled into a quarterly release.
- Release snapshot: `KnowledgeBaseVersion` record capturing all active rules at release date.
- Release notes documenting all changes, rationale, and evidence updates.
- Post-release monitoring period (30 days).

### 6.3 Annual Comprehensive Review
- Full audit of all active rules against current guideline versions.
- Evidence grade reassessment for all rules.
- Retirement of rules no longer supported by current evidence.
- Gap analysis: clinical scenarios not covered by the knowledge base.

## 7. Clinician Override Capture and Analysis Pipeline

### 7.1 Automated Capture
Every `RecommendationAudit` record with `approval_status = "overridden"` triggers:
1. Override reason recorded in `RecommendationAudit.override_reason`.
2. Final diagnosis captured in `Patient.primary_diagnosis`.
3. Clinical outcome tracked through subsequent `ClinicalProfile` updates.
4. Audit timestamp and clinician identity recorded.

### 7.2 Analysis Pipeline

```
RecommendationAudit (overridden)
    ↓
Monthly aggregation (by disease, rule_type, kb_rule_id)
    ↓
Override rate computation per rule
    ↓
Threshold flagging (>20% override rate)
    ↓
Categorisation (automated pre-classification + manual review)
    ↓
Prioritisation scoring (severity × frequency × evidence_grade_risk)
    ↓
Knowledge team review queue
```

### 7.3 Disagreement Analysis
For each high-priority override:
1. **Context review:** What patient features triggered the recommendation?
2. **Rule review:** What conditions in `rule_data` produced the score?
3. **Evidence review:** Is the underlying evidence still current?
4. **Clinician rationale review:** Was the override based on additional clinical information not captured in the system?
5. **Outcome review:** What was the patient outcome? Was the clinician's action validated by subsequent events?

## 8. Structured Learning from Disagreements

### 8.1 Learning Categories
Disagreements are analysed to identify systemic patterns:

| Pattern | Example | Learning |
|---------|---------|----------|
| **Knowledge gap** | No rule exists for a common clinical scenario | New rule required |
| **Rule insensitivity** | Rule exists but conditions are too strict, missing true positives | Broaden conditions or adjust thresholds |
| **Rule hypersensitivity** | Rule triggers too broadly, generating false positives | Tighten conditions or add exclusion criteria |
| **Context blindness** | Rule ignores clinically relevant context (age, comorbidities, drug interactions) | Add contextual modifiers |
| **Evidence lag** | Rule is based on superseded evidence | Update to current guideline version |
| **Data quality issue** | Rule fails because required patient data is missing | Improve data capture or add default handling |

### 8.2 Learning Integration
Each identified pattern produces a structured action:
- Action recorded in the knowledge team's review queue.
- Action linked to the originating `RecommendationAudit` records.
- Action tracked through to completion (rule change activated).
- Outcome measured: override rate change after rule modification.

## 9. Knowledge Base Versioning and Rollback Strategy

### 9.1 Versioning
- Every `KnowledgeBaseEntry` change creates a `KnowledgeBaseVersion` record.
- Version numbering: sequential per entry (v1, v2, v3, ...).
- Version metadata includes: `rule_data_diff`, `change_summary`, `changed_by`, `created_at`.
- Global knowledge base version: `KnowledgeBaseVersion` snapshot at each quarterly release.

### 9.2 Rollback Triggers
- Override rate increase > 10 percentage points within 30 days of rule activation.
- Clinician-reported critical error in a modified rule.
- Test case regression detected during automated testing.
- Guideline retraction or major update.

### 9.3 Rollback Process
1. Identify the rule version to revert to (previous `KnowledgeBaseVersion`).
2. Restore `rule_data` and related fields from the version snapshot.
3. Transition current rule status to `superseded`.
4. Transition reverted version to `active`.
5. Document rollback reason and notify clinical advisory board.
6. Root cause analysis within 7 days.

## 10. Rule Testing Against Gold-Standard Clinical Cases

### 10.1 Test Case Repository
- Maintained in `knowledge/rule_tester.py` and seeded via `knowledge/management/commands/seed_clinical_cases.py`.
- Each test case defines: patient features (synthetic or real), expected rule response (score range, matched/not-matched).
- Test cases organised by disease and rule type.
- Minimum 3 test cases per active rule.

### 10.2 Test Execution
- Automated via `knowledge/management/commands/run_rule_tests.py`.
- Run on every knowledge base change (CI/CD integration).
- Run on every quarterly release before activation.
- Results stored in `RuleTestResult` model.

### 10.3 Test Pass Criteria
- All existing test cases must pass (no regressions).
- New rules must have ≥ 80% test case match rate.
- No critical test case failures (test cases marked as `critical` in test metadata).

## 11. Quality Metrics for Knowledge Base

### 11.1 Rule-Level Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Precision** | Proportion of rule activations that are clinically appropriate | ≥ 0.80 |
| **Recall** | Proportion of clinically appropriate scenarios where the rule activates | ≥ 0.75 |
| **Override rate** | Proportion of rule-based recommendations overridden by clinicians | < 20% |
| **Evidence grade distribution** | Proportion of rules with Level 1 or Level 2 evidence | ≥ 60% |
| **Timeliness** | Proportion of rules reviewed within their `next_review_date` | ≥ 90% |
| **Completeness** | Proportion of rules with all mandatory fields populated | 100% |

### 11.2 System-Level Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Overall override rate** | All recommendations overridden / all recommendations issued | < 15% |
| **Alert-to-action ratio** | Recommendations leading to a clinical action / total recommendations | ≥ 0.70 |
| **Knowledge coverage** | Clinical scenarios covered by at least one active rule / total clinical scenarios encountered | ≥ 80% |
| **Rule freshness** | Proportion of rules reviewed within 12 months | ≥ 90% |
| **Test coverage** | Rules with ≥ 3 test cases / total active rules | 100% |

### 11.3 Computation
Quality metrics are computed by the `clinical_reasoning.services.knowledge_quality` module:
- `score_rule_quality(entry)` returns per-rule scores for completeness, clarity, evidence, and testability.
- System-level aggregates computed via the knowledge governance stats endpoint (`/api/v1/knowledge-base/governance_stats/`).

## 12. Automated Regression Testing

### 12.1 Regression Test Suite
- Run after every knowledge base change that activates or modifies an active rule.
- Suite includes all gold-standard test cases across all diseases.
- Any test case that previously passed but now fails triggers a regression alert.

### 12.2 Regression Alert Protocol
1. **Alert:** Automated notification to knowledge team lead and clinical advisory board.
2. **Hold:** Rule change held in `approved` status (not activated) until regression is resolved.
3. **Investigation:** Knowledge team investigates root cause within 3 business days.
4. **Resolution:** Fix regression, re-run test suite, proceed with activation or rollback.

### 12.3 CI/CD Integration
- Rule tests run as part of the automated test suite (`python manage.py test knowledge`).
- GitHub Actions (or equivalent) runs full regression suite on every pull request touching `knowledge/` or `clinical_reasoning/` modules.
- Deployment blocked if regression suite fails.

## 13. Governance Workflow for Knowledge Changes

### 13.1 Lifecycle States

```
DRAFT → UNDER_REVIEW → APPROVED → ACTIVE → SUPERSEDED / RETIRED
  ↑         ↓              ↓
  ←─────────┘              │
  ←────────────────────────┘
```

### 13.2 State Transitions (Valid)

| Current State | Allowed Next States |
|---------------|-------------------|
| DRAFT | UNDER_REVIEW, ARCHIVED |
| UNDER_REVIEW | APPROVED, DRAFT, ARCHIVED |
| APPROVED | ACTIVE, DRAFT, ARCHIVED |
| ACTIVE | SUPERSEDED, RETIRED, DRAFT, ARCHIVED |
| SUPERSEDED | ARCHIVED, RETIRED |
| ARCHIVED | DRAFT |
| RETIRED | ARCHIVED |

### 13.3 Approval Requirements
- **DRAFT → UNDER_REVIEW:** Knowledge team member initiates review.
- **UNDER_REVIEW → APPROVED:** At least one nephrologist (consultant level) approves. Review recorded in `RuleReview`.
- **APPROVED → ACTIVE:** Knowledge team activates. All regression tests must pass.
- **Any → RETIRED/SUPERSEDED:** Clinical advisory board decision with documented rationale.

### 13.4 Audit Trail
- Every state transition logged via `KnowledgeBaseEntry.transition_to()` method.
- Log includes: entry ID, old state, new state, user, timestamp.
- Audit trail queryable via admin interface and API.

## 14. Integration with RecommendationAudit

The `RecommendationAudit` model serves as the primary data source for the continuous improvement loop:

| RecommendationAudit Field | Role in Feedback Loop |
|--------------------------|----------------------|
| `approval_status` | Signals clinician agreement/disagreement |
| `override_reason` | Provides free-text explanation for overrides |
| `kb_rule_id` | Links audit record to the triggering KB rule |
| `kb_version` | Enables version-specific analysis |
| `confidence_score` | Correlates AI confidence with override likelihood |
| `evidence_grade` | Enables evidence-quality-stratified analysis |
| `clinical_rationale` | Provides the system's reasoning for audit |
| `issued_at` | Enables temporal trend analysis |
| `disease_id` | Enables disease-specific override rate analysis |

### 14.1 Derived Views
The following derived data products are computed from `RecommendationAudit`:
- **Override rate per rule:** `COUNT(approval_status='overridden') / COUNT(*)` grouped by `kb_rule_id`.
- **Override rate per disease:** `COUNT(approval_status='overridden') / COUNT(*)` grouped by `disease_id`.
- **Confidence-override correlation:** Mean `confidence_score` for overridden vs. approved recommendations.
- **Temporal trends:** Monthly override rate per rule (detect drift).
- **Clinician variation:** Override rate per `clinician` (detect practice variation).

## 15. Feedback Dashboard Design

The knowledge governance dashboard (accessible via `/api/v1/knowledge-base/governance_stats/`) provides:

### 15.1 Overview Metrics
- Total active rules, total overrides this month, overall override rate.
- Rules needing re-review (past `next_review_date`).
- Rules in DRAFT > 90 days (escalation indicator).

### 15.2 Disease-Level Breakdown
- Override rate per disease (bar chart).
- Trend of override rate over time per disease (line chart).
- Top 5 most-overridden rules (table).

### 15.3 Evidence Quality Distribution
- Pie chart: proportion of rules by evidence grade (Level 1, Level 2, Not Graded, Expert Opinion).
- List of rules with `evidence_grade = "OP"` flagged for evidence upgrade.

### 15.4 Recent Changes
- List of rules activated in the last 30 days.
- List of rules superseded or retired in the last 30 days.
- Pending reviews queue.

## 16. Continuous Improvement Cycle Timeline

| Frequency | Activity | Output |
|-----------|----------|--------|
| **Weekly** | Review new overrides from the past 7 days; flag critical issues | Override triage report |
| **Monthly** | Full feedback aggregation, categorisation, prioritisation; draft rule changes | Monthly knowledge review report; draft changes submitted |
| **Quarterly** | Clinical review of all draft changes; activation of approved rules; regression testing; version release | Quarterly release notes; updated `KnowledgeBaseVersion` snapshot |
| **Annually** | Comprehensive guideline alignment review; evidence grade reassessment; knowledge coverage gap analysis; quality metrics review | Annual knowledge base audit report |

## 17. Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Overall system override rate | < 15% | Monthly from `RecommendationAudit` |
| Rules reviewed within scheduled review date | ≥ 90% | Quarterly from `KnowledgeBaseEntry.next_review_date` |
| Regression test pass rate | 100% before any activation | Per-activation from `RuleTestResult` |
| Time from override identification to rule review | < 30 days | Monthly from override triage log |
| Time from approved rule change to activation | < 7 days | Monthly from `RuleReview` timestamps |
| Knowledge coverage of encountered clinical scenarios | ≥ 80% | Quarterly from clinical reasoning engine logs |
| Evidence grade distribution: Level 1 or Level 2 | ≥ 60% of active rules | Quarterly from `KnowledgeBaseEntry.evidence_grade` |
| Clinician trust in recommendations (survey) | ≥ 4.0 / 5.0 | Quarterly from clinician survey |

## 18. Implementation Plan

### Phase 1: Foundation (Months 1–2)
- Confirm `RecommendationAudit` capture is functioning in pilot environment.
- Set up monthly override export and aggregation scripts.
- Define gold-standard test case repository (minimum 3 cases per disease).
- Establish knowledge team roles and responsibilities.

### Phase 2: Operationalise (Months 3–4)
- Launch monthly knowledge review meetings.
- Implement override categorisation workflow.
- Enable regression testing in CI/CD pipeline.
- Deploy feedback dashboard in admin interface.

### Phase 3: Optimise (Months 5–6)
- Refine prioritisation scoring based on initial experience.
- Expand test case repository based on real clinical encounters.
- Implement automated override rate alerting (> 20% threshold).
- Begin quarterly release cycle.

### Phase 4: Mature (Months 7–12)
- Full annual audit cycle operational.
- Knowledge base quality metrics integrated into pilot evaluation report.
- Continuous improvement data feeding into research publication plan.
- Framework documented for potential multi-site rollout.

---

**Document Status:** Draft  
**Next Review:** GDES Clinical Advisory Board meeting  
**Distribution:** Knowledge Team, Clinical Advisory Board, Development Team, BIRDEM Nephrology Department
