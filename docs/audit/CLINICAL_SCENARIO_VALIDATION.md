# Clinical Scenario Validation

## Scenario 1: New Patient with Nephrotic Syndrome

**Trigger:** POST `/api/v1/patients/` → signal → `patient.registered` → `reason_about_patient()`

**Expected behavior:**
1. `extract_patient_features()` builds feature dict: `{proteinuria: "nephrotic", features: ["edema", "hypertension"]}`
2. `evaluate_patient_rules()` scores differentials (MCD, MN, FSGS, IgAN, LN)
3. `_identify_information_gaps()` flags: "No biopsy findings" (high), "Limited serological data" (medium)
4. `_assess_risk()`: if `latest_egfr` is null, risk = "unknown"
5. `determine_current_stage()`: phase is empty → `"assessment"`
6. `assess_pathway_deviation()`: missing biopsy → high-severity deviation
7. ClinicalInsight created: CARE_GAP "Missing: biopsy" (HIGH)
8. ClinicalInsight created: DIAGNOSTIC "Leading differential: ..." (HIGH)

**Validated by:** `test_clinical_intelligence_ws4_9.py` `test_clinical_reasoning_pipeline`

---

## Scenario 2: Lab Result Triggers Outcome Recompute

**Trigger:** POST `/api/v1/lab-results/` → signal → `lab_result.created` → `_on_lab_event`

**Expected behavior:**
1. `compute_patient_outcome(patient)` → evaluates eGFR trend, proteinuria, remission
2. If eGFR < 15: ESKD outcome recorded
3. `_on_patient_event` also called → full reasoning pipeline
4. Profile updated: trajectory, risk, milestones

**Validated by:** `test_event_orchestration.py` `test_lab_event_triggers_outcome_recompute`

---

## Scenario 3: Biopsy Result Refines Differential

**Trigger:** POST `/api/v1/biopsies/` → signal → `biopsy.created` → `_on_patient_event`

**Expected behavior:**
1. `_check_biopsy_milestone()`: adds "biopsy" milestone with `{histology: diagnosis}`
2. On next `reason_about_patient()`: biopsy features in differential scoring
3. Information gap "No biopsy findings" removed from list
4. Care pathway deviation "missing_biopsy" resolved

**Validated by:** `test_clinical_intelligence_ws4_9.py` `test_milestone_detection`

---

## Scenario 4: Treatment Started → Milestone Recorded

**Trigger:** POST `/api/v1/treatment-exposures/` → signal → `treatment_exposure.created` → `_on_patient_event`

**Expected behavior:**
1. `_check_treatment_milestones()`: detects first treatment → `treatment_started` milestone
2. If second treatment: `treatment_switched` milestone
3. Profile updated with new milestones

**Validated by:** `test_clinical_intelligence_ws4_9.py` `test_milestone_detection`

---

## Scenario 5: Clinical Event → ESKD Pathway Transition

**Trigger:** POST `/api/v1/clinical-events/` with eGFR < 15 → `_on_clinical_event`

**Expected behavior:**
1. `compute_patient_outcome()`: records ESKD outcome
2. `determine_current_stage()`: eGFR < 15 → `"eskd_care"`
3. `detect_stage_transition()`: validates transition from previous stage
4. Pathway stage: ESKD/RRT with required actions (rrt_access, transplant_evaluation)
5. Risk assessment: `overall = "high"`

**Validated by:** `test_clinical_intelligence_ws4_9.py`

---

## Scenario 6: Explainability Report

**Trigger:** POST `/api/v1/profiles/explain/` `{patient_id: N}`

**Expected behavior:**
1. Resolves patient, gets/creates ClinicalProfile
2. `build_full_explainability(profile)` returns:
   - `summary`: "Leading clinical impression: ... (score N, evidence grade ...)"
   - `triggering_findings`: clinical, lab, pathology findings with weights
   - `matched_rules`: top 3 diseases with matched count
   - `guideline_support`: source abbreviations with evidence grades
   - `evidence_quality`: grade distribution, strong/weak counts
   - `rejected_alternatives`: with score differences and reasons
   - `information_gaps`: with confidence impact statements
   - `audit_trail`: profile version, last_updated, feature_count

**Validated by:** `test_clinical_reasoning_services.py` `test_build_full_explainability`

---

## Scenario 7: Batch Profile Recompute

**Trigger:** POST `/api/v1/profiles/reason_all/` (authenticated)

**Expected behavior:**
1. `recompute_all_profiles()` iterates all Patient records
2. Each patient: `reason_about_patient()` in atomic transaction
3. Returns `{total: N, errors: 0}`
4. Errors logged per-patient, not stopping the batch

**Validated by:** `test_clinical_intelligence_ws4_9.py` `test_batch_recompute`

---

## Edge Cases Validated by Tests

| Edge Case | Test | Expected Behavior |
|---|---|---|
| Patient not found for event | `test_event_handlers_patient_not_found` | Warning logged, no crash |
| Malformed patient_id in payload | `test_event_dispatch_and_handlers` | Graceful fallback to source_pk |
| No clinical profile exists | `test_clinical_reasoning_pipeline` `test_profile_creation` | Profile auto-created |
| Knowledge base empty | `test_missing_knowledge_handling` | Empty differential, "insufficient data" summary |
| No encounters/labs | `test_empty_profile` | All defaults, care gaps detected |
| Decimal in payload | `test_milestone_detection` | json_safe converts to float |
| Duplicate event processing | `test_event_dispatch_and_handlers` | Idempotent update on profile |
