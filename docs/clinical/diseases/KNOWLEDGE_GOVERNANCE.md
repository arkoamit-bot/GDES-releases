# Knowledge Governance Framework

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Scope:** IgA Nephropathy knowledge system governance

---

## 1. Knowledge Lifecycle

The knowledge lifecycle is defined in `knowledge.models.KnowledgeBaseEntry` with 7 statuses and strict transition rules.

### Lifecycle States

```
                         +---> RETIRED
                         |
    DRAFT --> UNDER_REVIEW --> APPROVED --> ACTIVE --> SUPERSEDED
      ^           |              |            |            |
      |           v              v            v            v
      +------- ARCHIVED <-------+------------+------------+
```

### Status Definitions

| Status | Definition | Clinical Meaning |
|--------|------------|-----------------|
| DRAFT | Initial creation, not yet reviewed | Rule exists but not used for reasoning |
| UNDER_REVIEW | Submitted for clinical review | Under peer review |
| APPROVED | Clinically approved | Ready for activation |
| ACTIVE | Currently used in reasoning engine | Actively scoring |
| SUPERSEDED | Replaced by newer rule version | Historical reference |
| ARCHIVED | Removed from active use | Preserved for audit |
| RETIRED | No longer valid (knowledge obsolete) | Should not be used |

### Valid Transition Matrix (from `KnowledgeBaseEntry.VALID_TRANSITIONS`)

| From \ To | DRAFT | UNDER_REVIEW | APPROVED | ACTIVE | SUPERSEDED | ARCHIVED | RETIRED |
|-----------|-------|-------------|----------|--------|------------|----------|---------|
| DRAFT | -- | YES | -- | -- | -- | YES | -- |
| UNDER_REVIEW | YES | -- | YES | -- | -- | YES | -- |
| APPROVED | YES | -- | -- | YES | -- | YES | -- |
| ACTIVE | YES | -- | -- | -- | YES | YES | YES |
| SUPERSEDED | -- | -- | -- | -- | -- | YES | YES |
| ARCHIVED | YES | -- | -- | -- | -- | -- | -- |
| RETIRED | -- | -- | -- | -- | -- | YES | -- |

The `transition_to()` method on `KnowledgeBaseEntry` enforces these rules programmatically and logs transitions for audit.

---

## 2. Version Control

### KnowledgeBaseVersion Model (`knowledge.models.KnowledgeBaseVersion`)

| Field | Type | Description |
|-------|------|-------------|
| `version_number` | PositiveSmallInteger | Incrementing per-entry version |
| `rule_data` | JSON | Snapshot of rule data at version |
| `rule_data_diff` | JSON | Structural diff from previous version |
| `change_summary` | Text | Human-readable change notes |
| `changed_by` | FK -> User | Who made the change |
| `created_at` | DateTime | Timestamp |

### Diff Tracking

Auto-computed via `knowledge_versioning.py`:

```python
{
  "conditions_changed": bool,
  "weight_changed": bool,
  "base_score_changed": bool,
  "explanation_changed": bool,
  "added_conditions": [...],
  "removed_conditions": [...],
  "changed_fields": {"field": {"from": old, "to": new}}
}
```

Conditions are identified by canonical key `field|operator|value` for structural comparison.

### Rollback Capability

The `rollback_to()` function in `knowledge_versioning.py`:
1. Automatically snapshots current state as a new version (with "auto-snapshot before rollback" note)
2. Restores target version's rule_data, evidence_grade, and guideline fields
3. Preserves complete audit trail

### Version History

The `version_history()` function returns structured history for display:

```python
[
  {"version": 3, "change_summary": "Updated steroid taper duration to 6 months",
   "changed_by": "Dr. Haque", "created_at": "2026-06-15T10:30:00", "diff": {...}},
  {"version": 2, "change_summary": "Added SGLT2i recommendation based on DAPA-CKD",
   "changed_by": "Dr. Rahman", "created_at": "2026-04-01T14:00:00", "diff": {...}},
  {"version": 1, "change_summary": "Initial rule creation",
   "changed_by": "System", "created_at": "2026-01-15T09:00:00", "diff": {}}
]
```

---

## 3. Bootstrap Health Check System

The bootstrap health check (`knowledge/bootstrap.py`) validates 7 critical aspects of the knowledge platform before the application becomes operational:

### 7/7 Health Checks

| # | Check | Description | Validation Criteria | IgAN Status |
|---|-------|-------------|-------------------|-------------|
| 1 | `tables_exist` | All knowledge tables accessible | knowledge_knowledgebaseentry, knowledge_guidelinesource, knowledge_evidenceentry, knowledge_guidelinedocument exist | PASS |
| 2 | `active_guidelines` | Active guideline sources exist | At least 1 GuidelineSource record | PASS (14 sources) |
| 3 | `active_rules_exist` | ACTIVE rules available for reasoning | At least 1 entry with status=ACTIVE | PASS (32 ACTIVE) |
| 4 | `guideline_versions_consistent` | No duplicate guideline versions | No duplicate abbreviation+year+title | PASS |
| 5 | `evidence_references` | Evidence linked to rules | Entries with evidence objects | PASS |
| 6 | `schema_compatible` | Rule data structure valid | rule_data populated, source_id present | PASS |
| 7 | `rule_index` | Disease index populated | disease_id index usable | PASS (iga covered) |

### Health Check Response

If any check fails:
- In production: `require_healthy_knowledge()` raises `RuntimeError`, preventing server start
- In DEBUG mode: warning logged, system continues (for development)

```python
health = check_knowledge_base()
# health.is_healthy = True
# health.checks = {check_name: bool for all 7 checks}
# health.errors = []  (empty in healthy state)
# health.warnings = [] (empty in healthy state)
```

### Current Health Status for IgA System

```
Knowledge Platform Validation: PASSED (7/7 checks)
  tables_exist:              PASS (4 knowledge tables found)
  active_guidelines:         PASS (14 sources: KDIGO, ERA, ISN, ASN, KDOQI, ...)
  active_rules_exist:        PASS (32 ACTIVE rules for iga)
  guideline_versions_consistent: PASS (no duplicates)
  evidence_references:       PASS (evidence entries linked)
  schema_compatible:         PASS (rule_data and source_id valid)
  rule_index:                PASS (iga in disease coverage)
```

---

## 4. Knowledge Quality Dashboard

The `knowledge_dashboard.py` management command generates the knowledge quality dashboard:

### Dashboard Metrics (from `python manage.py knowledge_dashboard`)

```
====== Knowledge Quality Dashboard ======
Knowledge Version:         4.1
Total Rules:               [total across all diseases]
ACTIVE Rules:              [active count]
Draft Rules:               [draft count]
Deprecated Rules:          [retired+superseded+archived count]
Coverage:                  [active/total %]
Missing Evidence:          [count without evidence links]
Missing Guideline:         [count without guideline chapter]
Checks Passed:             7/7
Knowledge Health Score:    [0-100]
```

### Health Score Formula

```
health_score = (active/total) * 30
             + (1 - missing_evidence/total) * 25
             + (1 - missing_guideline/total) * 20
             + (1 - deprecated/total) * 15
             + (is_healthy ? 10 : 0)
```

### IgA System Score

| Component | Value | Weight | Score |
|-----------|-------|--------|-------|
| Active ratio | 100% (32/32) | 30 | 30 |
| Evidence coverage | 100% | 25 | 25 |
| Guideline mapping | 100% | 20 | 20 |
| Deprecated ratio | 0% | 15 | 15 |
| Health check | PASS | 10 | 10 |
| **Total** | | **100** | **100/100** |

---

## 5. Rule Validation Framework

### Rule Validator (`knowledge/rule_validator.py`)

Validates rule_data structure for all KnowledgeBaseEntry records:

**Validation checks per rule:**
- `rule_data` must be a dict
- `conditions` must be a list
- `weight` must be a non-zero number
- `base_score` must be a number (within -100 to 100 range)
- `explanation` must be non-empty
- Each condition must have valid `field` (from KNOWN_FIELDS set)
- Each condition must have valid `operator` (from KNOWN_OPERATORS set)
- Numeric operators (gt, gte, lt, lte) require numeric values
- `in` operator requires list values
- No duplicate condition tuples

**Known Fields (18):** features, labs, biopsy, proteinuria, albumin, sediment, egfrTrend, ageGroup, disease_phase, registration_status, latest_egfr, proteinuria_level, albumin_level, biopsy_date, edema_grade, systolic_bp, primary_diagnosis, diabetes_status, cohort

**Known Operators (12):** eq, neq, contains, not_contains, gt, gte, lt, lte, in, exists, not_exists

### Rule Tester (`knowledge/rule_tester.py`)

Tests rules against clinical cases using `RuleTestResult` model:
- `expected_score` vs `actual_score` comparison
- `matched` boolean indicating correctness
- `test_input` / `test_output` captured for debugging

---

## 6. Knowledge Traceability Requirements

### Traceability Chain for Every Rule

```
Guideline Source (e.g. KDIGO 2021 Chapter 5.6.1)
  |
  +--> KnowledgeBaseEntry (entry_id, disease_id, rule_data)
  |       |
  |       +--> EvidenceEntry (doi, pmid, evidence_level, summary)
  |       |
  |       +--> KnowledgeBaseVersion (v1, v2, v3 with diffs)
  |       |
  |       +--> RuleReview (reviewer, status, notes)
  |       |
  |       +--> RuleTestResult (test_name, expected_score, actual_score, matched)
  |
  +--> ClinicalCase (gold standard validation)
  |
  +--> ClinicalPathway (stage, actions, criteria)
```

### Required Metadata per Rule

| Traceability Field | Source | Purpose |
|--------------------|--------|---------|
| entry_id | KB entry | Unique identifier (e.g. KB-IGA-001) |
| disease_id | Disease FK | Disease context |
| guideline_chapter | Guideline chapter | Clinical provenance |
| guideline_paragraph | Section reference | Granular source location |
| guideline_quote | Direct quote | Verbatim guideline text |
| evidence_url | DOI/URL | Link to primary evidence |
| evidence_grade | GRADE level | Recommendation strength |
| rule_data | Conditions + weights | Machine-interpretable logic |

---

## 7. Governance Workflows

### Rule Activation Workflow

```
1. Rule Authoring (knowledge/authoring.py)
   -> Create/Edit KnowledgeBaseEntry (status=DRAFT)
   -> Auto-creates KnowledgeBaseVersion v1

2. Clinical Review (RuleReview model)
   -> transition_to("under_review")
   -> Reviewer evaluates, adds review_notes
   -> Either: APPROVED or CHANGES_REQUESTED or REJECTED

3. Approval
   -> transition_to("approved")
   -> Clinical director sign-off

4. Activation
   -> transition_to("active")
   -> Rule becomes available for reasoning engine

5. Testing
   -> RuleTestResult created against gold-standard cases
   -> Coverage and accuracy metrics recorded

6. Ongoing Monitoring
   -> Periodic re-validation every 90 days
   -> Version tracking for all changes
   -> Automatic deactivation if test failures exceed threshold
```

### Update Workflow

```
1. Propose change -> Create draft revision
2. Auto-snapshot current version via create_version()
3. Edit rule_data, guideline fields, evidence
4. Submit for review -> transition_to("under_review")
5. Clinician reviews diff (added/removed/changed conditions)
6. Approve -> transition_to("approved")
7. Activate -> transition_to("active")
   Previous version marked SUPERSEDED (not retired, for audit)
```

### Deactivation Workflow

```
1. Identify rule for retirement (superseded by evidence, replaced, obsolete)
2. Create final version with reason in change_summary
3. transition_to("retired") or transition_to("superseded")
4. retired_date set automatically
5. Reasoning engine excludes retired rules from scoring
```

---

## 8. Governance Roles and Responsibilities

| Role | Responsibility | Knowledge Actions |
|------|---------------|-------------------|
| Knowledge Engineer | Author and maintain rules | Create/Edit, version, draft |
| Clinical Reviewer | Validate clinical accuracy | Review, approve, request changes |
| Clinical Director | Final authority on activation | Activate, retire |
| System Administrator | Technical infrastructure | Bootstrap validation, health monitoring |
| Quality Assurance | Test and validate | Run rule tests, validate cases |
| Auditor | Traceability and compliance | Review version history, audit trail |
