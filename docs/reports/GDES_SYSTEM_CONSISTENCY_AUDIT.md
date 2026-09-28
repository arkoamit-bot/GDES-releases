# GDES System Consistency Audit

**Version:** 6.5 Release Candidate
**Date:** 2026-07-11

---

## 1. Executive Summary

This audit ensures GDES operates with a **single reasoning engine**, a **single follow-up engine**, a **single management engine**, and no orphan tables. Any duplication between subsystems is identified, classified, and assigned a deprecation path.

**Overall Assessment:**
- **4 critical duplicates** identified
- **2 medium overlaps** identified
- **1 low overlap** identified

---

## 2. Duplicate Analysis

### CRITICAL: Legacy Differential Diagnosis Engine

| Component | `decision/services.py` | `clinical_reasoning/services/engine.py` |
|-----------|----------------------|----------------------------------------|
| Disease count | 9 (hardcoded) | 18 (database-driven via KnowledgeBase) |
| Data source | Hardcoded profiles | Seed knowledge base (`seed_knowledge_base.py`) |
| Output | Ranked differentials | Ranked differentials |

Both produce ranked differential diagnoses for the same patients using incompatible logic and disease counts.

**Action:** DEPRECATED `evaluate_case()` with `DeprecationWarning`. Legacy engine retained for backward compatibility only. `ClinicalProfileViewSet.reason()` is the canonical API.

---

### HIGH: Duplicate Follow-up Schedulers

| Component | `clinical_reasoning/services/followup_scheduler.py` | `followup/` app |
|-----------|-----------------------------------------------------|-----------------|
| Intervals | Hardcoded | Disease-specific protocol classes |
| Triggering | Manual call | Signal-based |
| Tasks created | `ScheduledVisit` + `FollowUpTask` | `FollowUpTask` only |

Both can create duplicate tasks for the same patient.

**Action:** DEPRECATED `followup_scheduler.py`. `followup/` app is the canonical follow-up system.

---

### MEDIUM: Monitoring Data Duplicated

| Component | `management_plan.py` | `monitoring_plan.py` |
|-----------|---------------------|---------------------|
| Structure | Embedded "monitoring" lists within `DISEASE_TREATMENT_PROFILES` | Structured `DISEASE_MONITORING_PROTOCOLS` |
| Parameters | UPCR, creatinine, BP, potassium | UPCR, creatinine, BP, potassium |

Same monitoring parameters maintained in two places. `monitoring_plan.py` is the structured, canonical source.

**Action:** `management_plan.py` monitoring data to be removed post-pilot. `monitoring_plan.py` is the canonical source.

---

### MEDIUM: Care Pathway Naming Confusion

| Component | `care_pathway.py` | `care_pathway_engine.py` |
|-----------|-------------------|--------------------------|
| Responsibility | Care gap detection + `compute_monitoring_schedule` | Stage definitions + transitions |

Complementary but confusing naming. `compute_monitoring_schedule` in `care_pathway.py` overlaps with `monitoring_plan.py`.

**Action:** `care_pathway.py` to be renamed `care_gap_detector.py` post-pilot.

---

### LOW: Explainability Overlap

| Component | `decision/explainability.py` | `clinical_reasoning/services/explainability.py` |
|-----------|-----------------------------|------------------------------------------------|
| Explains | Legacy `evaluate_case()` output | `ClinicalProfile` output |

Two explainability systems for two different engines. The legacy system has no future use case.

**Action:** `decision/explainability.py` is deprecated along with `evaluate_case()`.

---

## 3. Orphan Table Analysis

| Table | Conceptual Data | Status |
|-------|----------------|--------|
| `DecisionResult.ranked_differential` | Ranked differential diagnoses | Deprecated in favor of `ClinicalProfile.differential` |
| `ClinicalProfile.differential` | Ranked differential diagnoses | **Canonical** |
| `DecisionRequest` | Audit trail | Retained for audit trail; deprecated in favor of `ClinicalProfile` |
| `DecisionResult` | Audit trail | Retained for audit trail; deprecated in favor of `ClinicalProfile` |

**No truly orphan tables found.** Deprecated tables are retained for backward compatibility and audit traceability.

---

## 4. Consolidation Status

| Engine | File | Status |
|--------|------|--------|
| Primary reasoning engine | `engine.py` | ACTIVE |
| Knowledge base | `seed_knowledge_base.py` | ACTIVE (18 diseases, 209 rules) |
| Management plan | `management_plan.py` | ACTIVE (treatment protocols) |
| Monitoring plan | `monitoring_plan.py` | ACTIVE (canonical monitoring source) |
| Investigation engine | `investigation_engine.py` | ACTIVE |
| Drug toxicity | `drug_toxicity.py` | ACTIVE |
| Treatment failure | `treatment_failure.py` | ACTIVE |
| Care pathway engine | `care_pathway_engine.py` | ACTIVE (stage transitions) |
| Care gap detection | `care_pathway.py` | RENAME to `care_gap_detector.py` post-pilot |
| Disease trajectory | `disease_trajectory.py` | ACTIVE |
| Disease milestones | `disease_milestones.py` | ACTIVE |
| Follow-up engine | `followup/` | ACTIVE (canonical) |
| Legacy follow-up | `followup_scheduler.py` | DEPRECATED |
| Legacy engine | `decision/services.py` `evaluate_case()` | DEPRECATED |
| Legacy explainability | `decision/explainability.py` | DEPRECATED |

---

## 5. API Endpoint Audit

| Endpoint | Status |
|----------|--------|
| `ClinicalProfileViewSet.reason()` | ACTIVE (canonical reasoning endpoint) |
| `DecisionViewSet.create()` / `evaluate()` | DEPRECATED |
| `ClinicalProfileViewSet` — management_plan, monitoring_plan, followup_schedule, investigation_recommendations, drug_toxicity, treatment_failure, relapse_detection, validate_disease, retrospective_validation | ACTIVE |
| `/api/v1/results/` (`DecisionResultViewSet`) | DEPRECATED (legacy results) |
| `/api/v1/knowledge-base/governance_stats/` | ACTIVE (new) |

---

## 6. Recommendations

1. **Post-pilot:** Remove `evaluate_case()`, `followup_scheduler.py`, `decision/explainability.py`.
2. **Post-pilot:** Rename `care_pathway.py` to `care_gap_detector.py`.
3. **Post-pilot:** Remove embedded monitoring data from `management_plan.py`.
4. **Post-pilot:** Consolidate `DecisionResult` into `ClinicalProfile`.
