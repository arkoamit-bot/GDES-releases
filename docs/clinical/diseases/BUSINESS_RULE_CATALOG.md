# Business Rule Catalog

**Version:** 2.5  
**Rule:** Each business rule has exactly one authoritative implementation. No duplicated logic.

---

## Registry Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-R01 | Patient ID must be unique and follow BGD-NNNNN format | `next_patient_id()` auto-generates; UNIQUE constraint | `patients/models.py:12-19` |
| R-R02 | Registration status transitions must be valid | `RegistrationStatus` choices; enforced by application logic | `patients/workflow.py` |
| R-R03 | A patient must belong to an active Site | `Site.is_active` flag; FK with PROTECT on delete | `patients/models.py:69` |
| R-R04 | Each user can have only one role per site | `unique_together = [(user, site)]` | `patients/models.py:138` |
| R-R05 | Patient deletion cascades to all clinical data | `on_delete=CASCADE` on all FK relationships | Multiple models |

---

## Clinical Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-C01 | Differential diagnoses are ranked by total score descending | `sorted(results, key=lambda r: -r.total_score)` | `knowledge/services.py` |
| R-C02 | Only top differential generates a DIAGNOSTIC insight | `rule_results[0]` used for insight creation | `engine.py:273-282` |
| R-C03 | Information gaps are flagged: no biopsy (high), missing proteinuria (high), missing eGFR (high), limited serology (medium) | `_identify_information_gaps()` | `engine.py:111-140` |
| R-C04 | Risk assessment depends on latest eGFR threshold: <30 = high, <60 = moderate, >=60 = low | `_assess_risk()` | `engine.py:171-209` |
| R-C05 | Declining trajectory overrides other risk levels to "high" | `_assess_risk()` | `engine.py:201-207` |
| R-C06 | Reasoning chain must include: rule evaluation step, trajectory assessment, care gaps | `_build_reasoning_chain()` | `engine.py:143-168` |

---

## Care Pathway Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-P01 | Current stage is determined by disease_phase + eGFR | `determine_current_stage()` | `care_pathway_engine.py:111-128` |
| R-P02 | eGFR < 15 overrides any phase to ESKD stage | `determine_current_stage()` | `care_pathway_engine.py:116-118` |
| R-P03 | Stage transitions must follow the defined 8-stage directed graph | `detect_stage_transition()` | `care_pathway_engine.py:131-152` |
| R-P04 | Each stage has required actions; missing actions = deviation | `assess_pathway_deviation()` | `care_pathway_engine.py:155-184` |
| R-P05 | Assessment stage requires: biopsy, serology, urinalysis, eGFR | `PATHWAY_DEFINITION["assessment"].required_actions` | `care_pathway_engine.py:36-43` |

---

## Disease Milestone Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-M01 | Diagnosis milestone: created from patient.primary_diagnosis + registration/enrollment date | `_check_diagnosis_milestone()` | `disease_milestones.py:59-70` |
| R-M02 | Biopsy milestone: created from earliest patient biopsy date | `_check_biopsy_milestone()` | `disease_milestones.py:72-84` |
| R-M03 | Remission milestone: created when disease_phase == "remission" | `_check_remission_milestone()` | `disease_milestones.py:87-96` |
| R-M04 | ESKD milestone: created when phase == "eskd" or eGFR < 15 | `_check_eskd_milestone()` | `disease_milestones.py:99-109` |
| R-M05 | Treatment started milestone: created from first TreatmentExposure | `_check_treatment_milestones()` | `disease_milestones.py:112-137` |
| R-M06 | Treatment switched milestone: created from second distinct TreatmentExposure | `_check_treatment_milestones()` (count > 1) | `disease_milestones.py:126-137` |
| R-M07 | Milestones are merged: existing take priority, new types are appended | `_merge_milestones()` | `disease_milestones.py:148-156` |

---

## Laboratory Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-L01 | LabResult must have either value_numeric or value_text | `models.py` validation | `labs/models.py` |
| R-L02 | Lab flags are computed from value vs reference range | `flag` field | `labs/models.py` |
| R-L03 | eGFR is computed using CKD-EPI or MDRD formula | `formula_version` field | `labs/models.py` |

---

## Outcome Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-O01 | Remission criteria are disease-specific (LN complete vs partial vs MCD thresholds) | `_proteinuria_outcome()` with `_disease_key()` | `analytics/services/outcomes.py` |
| R-O02 | Sustained eGFR decline: first drop below 57% of baseline (3-month window) | `_sustained_drop(series, baseline, 0.57)` | `analytics/services/outcomes.py` |
| R-O03 | Sustained creatinine rise: first sustained 1.5x baseline | `_sustained_rise(series, baseline, 1.5)` | `analytics/services/outcomes.py` |
| R-O04 | Index date is the earliest of enrollment_date, first encounter, or first lab | `_index_date()` | `analytics/services/outcomes.py` |

---

## Knowledge Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-K01 | Only ACTIVE status rules are evaluated against patients | `evaluate_patient_rules()` filters by `status=ACTIVE` | `knowledge/services.py` |
| R-K02 | Rule evaluation supports 11 operators: eq, neq, contains, not_contains, gt, gte, lt, lte, in, exists, not_exists | `_evaluate_condition()` | `knowledge/services.py` |
| R-K03 | Rules are scored on quality: completeness (25%), clarity (25%), evidence (25%), testability (25%) | `score_rule_quality()` | `knowledge_quality.py:13-36` |
| R-K04 | Quality grade: A >=85, B >=70, C >=50, D <50 | `_quality_grade()` | `knowledge_quality.py:94-100` |
| R-K05 | Conflicting rules: same field + contradictory operators (eq vs neq, gt vs lt, exists vs not_exists) = conflict | `detect_rule_conflicts()`, `_is_contradictory()` | `knowledge_quality.py:103-160` |
| R-K06 | Status transitions: DRAFT → REVIEWED → ACTIVE → RETIRED | Status TextChoices | `knowledge/models.py:29` |
| R-K07 | Rule versioning is append-only; each update creates a new KnowledgeBaseVersion | `knowledge/models.py:72-95` | |

---

## Drug Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-D01 | Drug has renal_dose_adjustment flag and nephrotoxic flag | `DrugMaster` model fields | `treatments/models.py` |
| R-D02 | Active treatment without end_date = ongoing exposure | `TreatmentExposure.objects.filter(end_date__isnull=True)` | `operational_intelligence.py:63` |

---

## Follow-up Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-F01 | Overdue visit: no encounter in >180 days (6 months) | `_count_overdue_visits()`, `_check_follow_up_gap()` | `operational_intelligence.py:70-82`, `care_pathway.py` |
| R-F02 | Active disease requires intensified monitoring (monthly) | `compute_monitoring_schedule()` | `care_pathway.py` |

---

## Research Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-RS01 | Cohort discovery: patients grouped by diagnosis + phase intersection | `discover_cohorts()` | `research_intelligence.py:10-59` |
| R-RS02 | Protocol match score: diagnosis match (40pts) + phase match (30pts) + interventional (15pts) + age eligible (15pts) | `_compute_protocol_match_score()` | `research_intelligence.py:94-114` |
| R-RS03 | Research opportunities: frequent relapser (>=2 relapses), treatment-refractory (>=2 switches), rare GN, remission candidate | `detect_research_opportunities()` | `research_intelligence.py:117-163` |

---

## Enterprise Rules

| ID | Rule | Implementation | Located In |
|---|---|---|---|
| R-E01 | All API writes must be attributed to an authenticated actor | `AuditedModelViewSet.initial()` + `AuditLog` | `api/base.py:18`, `audit/models.py` |
| R-E02 | Site coordinators see only their site's data; superusers and data_managers see all | `site_filter_kwargs()` | `api/permissions.py` |
| R-E03 | Rate limit: 100 requests per 60 seconds per key (in-memory) | `RateLimiter.check()` | `enterprise_readiness.py:81` |
| R-E04 | Compliance score: starts at 100, deducts for missing biopsy (-15), missing eGFR (-10), no encounters (-20), overdue visits (-15) | `compute_patient_compliance()` | `operational_intelligence.py:89-122` |

---

## Rule Duplication Audit

| Duplicate Concern | Locations | Action |
|---|---|---|
| Overdue follow-up (180 day rule) | `operational_intelligence.py:70` + `care_pathway.py` | ✅ Same threshold, but duplicated logic. Extract to shared constant. |
| ESKD detection (eGFR < 15) | `determine_current_stage()` + `_check_eskd_milestone()` | ✅ Consistent threshold across both. |
| Missing biopsy detection | `engine.py:114`, `care_pathway_engine.py:164`, `operational_intelligence.py:40` | ⚠️ Three implementations. Should use a single shared query. |
| Missing eGFR detection | `engine.py:126`, `care_pathway_engine.py:176`, `operational_intelligence.py:49` | ⚠️ Same pattern. Consolidate. |
