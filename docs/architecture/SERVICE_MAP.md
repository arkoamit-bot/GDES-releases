# BGDDR — Service Layer Documentation

## Overview

- **39 service files** across **12 apps**
- **~102 public functions**
- **10 dataclasses** for structured return types
- All pure-Python, no external statistical libraries

---

## Service Files by App

### patients/services.py
| Function | Signature | Description |
|---|---|---|
| `delete_patient_cascade` | `(patient) -> str` | Delete patient and all children in FK-safe order. Returns patient_id. |

---

### encounters/services/workflow.py
| Function | Signature | Description |
|---|---|---|
| `register_patient` | `(patient, date=None, by=None) -> Patient` | Register suspected patient into GN follow-up |
| `derive_phase` | `(patient, response, explicit="") -> str` | Compute next disease phase from current + response |
| `apply_visit` | `(encounter) -> None` | Advance patient phase from a saved follow-up encounter |
| `record_relapse` | `(patient, relapse_date, relapse_type, *, criteria, action_taken, encounter, by) -> RelapseEpisode` | Document relapse, emit ClinicalEvent, flip phase |

**State Machine**:
```
ACTIVE ──complete──► REMISSION ──stable──► POST_REMISSION
  ▲                                              │
  └──────────────── RELAPSE ◄────(record_relapse)┘
```

---

### labs/services/egfr.py
| Function | Signature | Description |
|---|---|---|
| `ckd_epi_2021` | `(scr_mg_dl, age_years, sex) -> (float, str)` | CKD-EPI 2021 race-free equation. Returns (eGFR, formula_version) |
| `egfr_to_decimal` | `(value) -> Decimal` | Convert float to Decimal |

**Formula**: `CKD-EPI-2021-creatinine` (stored on LabResult for reproducibility)

---

### labs/services/ordering.py
| Function | Signature | Description |
|---|---|---|
| `create_order` | `(patient, encounter, tests, date) -> LabOrder` | Create lab order with items |
| `record_result` | `(order_item, value, unit, date, source) -> LabResult` | Record result, auto-derive eGFR |

---

### labs/services/results.py
| Function | Signature | Description |
|---|---|---|
| `egfr_slope` | `(patient) -> float` | Simple linear regression eGFR slope (mL/min/1.73m²/year) |
| `record_result_with_derivation` | `(patient, test_code, value, date) -> LabResult` | Record creatinine → auto-derive eGFR |

---

### pathology/services/review.py
| Function | Signature | Description |
|---|---|---|
| `submit_review` | `(biopsy, role, *, diagnosis, broad_group, reviewer, review_date, mest, isn_rps_class, fsgs_variant, notes) -> str` | Record/update one pathology read |
| `concordance` | `(biopsy) -> dict` | Compare LOCAL vs CENTRAL reads field-by-field |
| `adjudicate` | `(biopsy, *, diagnosis, ...) -> str` | Consensus resolution of discordant biopsy |
| `_recompute_status` | `(biopsy) -> str` | Recompute biopsy review status |
| `_finalize` | `(biopsy) -> None` | Write GNDiagnosis/IgANScore from final read |

**Workflow**: LOCAL → CENTRAL → (DISCORDANT → ADJUDICATION) → CONCORDANT/ADJUDICATED → _finalize()

---

### pathology/services/agreement.py
| Function | Signature | Description |
|---|---|---|
| `cohens_kappa` | `(ratings_a, ratings_b) -> float` | Inter-observer kappa for two raters |
| `fleiss_kappa` | `(ratings_matrix) -> float` | Multi-rater kappa |

---

### prescriptions/services/safety.py
| Function | Signature | Description |
|---|---|---|
| `check_prescription` | `(prescription) -> list[SafetyWarning]` | Run all safety checks |

**Checks**:
1. **Renal dosing**: Drug flagged + patient eGFR below threshold
2. **Prior intolerance**: Re-prescribing drug previously stopped for AE/intolerance
3. **Duplicate therapy**: Two drugs of same DrugClass on one Rx
4. **Glycaemic effect**: Steroid/CNI in diabetic → intensification warning; in non-diabetic → monitoring warning

**Dataclass**: `SafetyWarning(level: str, code: str, message: str)`

---

### prescriptions/services/reconciliation.py
| Function | Signature | Description |
|---|---|---|
| `plan_reconciliation` | `(prescription) -> ReconciliationPlan` | Pure diff — computes what would change, writes nothing |
| `apply_reconciliation` | `(prescription, *, stop_reasons, force) -> None` | Project prescription onto TreatmentExposure |

**Dataclasses**:
- `PlannedAction(action, drug_id, drug_name, detail, exposure_id)`
- `ReconciliationPlan(prescription_id, as_of, actions)`

**Actions**: open | close | change | continue

---

### prescriptions/services/finalize.py
| Function | Signature | Description |
|---|---|---|
| `finalize_prescription` | `(prescription, *, user, stop_reasons, override_blocks) -> list[SafetyWarning]` | Freeze + reconcile. Raises FinalizeBlocked if hard safety check fails. |
| `new_version_from` | `(prescription) -> Prescription` | Create next immutable version from finalized Rx |

---

### analytics/services/outcomes.py
| Function | Signature | Description |
|---|---|---|
| `compute_patient_outcome` | `(patient) -> PatientOutcome` | Derive full outcome row from longitudinal data |
| `compute_all_outcomes` | `() -> int` | Re-compute outcomes for all patients. Returns count. |

**Internal functions**: `_series`, `_index_date`, `_sustained_drop`, `_sustained_rise`, `_proteinuria_series`, `_disease_key`, `_egfr_at`, `_proteinuria_outcome`, `_first_sustained`, `_proteinuria_relapse`, `_last_contact`, `_earliest`, `_dec`

---

### analytics/services/remission.py
| Function | Signature | Description |
|---|---|---|
| `disease_key` | `(diagnosis_text) -> str` | Map free-text diagnosis to remission-rule key |
| `complete_predicate` | `(disease, baseline) -> callable` | Sustained complete remission (< 0.3 g/day) |
| `lupus_complete_predicate` | `(baseline_egfr, egfr_at) -> callable` | Lupus complete response (< 0.5 + eGFR preserved) |
| `partial_predicate` | `(disease, baseline) -> callable` | Partial remission (≥50% reduction & < 3.5) |
| `igan_response_predicate` | `(baseline) -> callable` | IgAN response (≥30% reduction or < 0.3) |
| `egfr_preserved` | `(baseline_egfr, egfr_value) -> bool` | eGFR within KDIGO tolerance of baseline |

**Constants**: COMPLETE=0.3, LUPUS_COMPLETE=0.5, NEPHROTIC=3.5, PARTIAL_REDUCTION=0.50, RELAPSE=1.0

---

### analytics/services/survival.py
| Function | Signature | Description |
|---|---|---|
| `kaplan_meier` | `(durations, events, confidence) -> list[KMStep]` | KM survival estimate with Greenwood CI |
| `median_survival` | `(steps) -> float` | Smallest time at S(t) ≤ 0.5 |
| `survival_at` | `(steps, t) -> float` | S(t) at time t |
| `nelson_aalen` | `(durations, events) -> list[NAStep]` | Nelson-Aalen cumulative hazard |
| `logrank_test` | `(d1, e1, d2, e2) -> LogRankResult` | Two-group log-rank test |
| `incidence_rate` | `(durations, events, *, per, time_unit_days) -> (rate, n, py)` | Person-time incidence rate |

**Dataclasses**: `KMStep`, `NAStep`, `LogRankResult`

---

### analytics/services/cox.py
| Function | Signature | Description |
|---|---|---|
| `cox_fit` | `(X, durations, events, names, *, max_iter, tol) -> CoxResult` | Multivariable Cox PH regression |
| `cox_score_test` | `(X, durations, events) -> (chi2, p)` | Global score test at beta=0 |

**Dataclasses**: `CoxCovariate`, `CoxResult`

**Algorithm**: Newton-Raphson on Breslow partial log-likelihood, mean-centred covariates

---

### analytics/services/competing_risks.py
| Function | Signature | Description |
|---|---|---|
| `cumulative_incidence` | `(data, *, cause, confidence) -> list[CIFStep]` | Cause-specific CIF (Aalen-Johansen) |
| `cif_at` | `(steps, t) -> float` | CIF at time t |
| `final_cif` | `(steps) -> float` | Final CIF value |
| `compare_cif_at` | `(data1, data2, t, *, cause) -> dict` | Pointwise z-test of CIF difference |

**Dataclass**: `CIFStep`

---

### analytics/services/mixed_model.py
| Function | Signature | Description |
|---|---|---|
| `fit_lmm` | `(clusters, *, q, max_iter, tol) -> dict` | Linear mixed-effects model (Laird-Ware EM) |
| `egfr_slope_lmm` | `(series_by_group) -> dict` | Compare eGFR slope between two groups |

---

### analytics/services/imputation.py
| Function | Signature | Description |
|---|---|---|
| `mice` | `(data, *, m, iterations, k, seed) -> list[list[list]]` | Multiple imputation by chained equations with PMM |
| `rubin_pool` | `(estimates, variances) -> dict` | Rubin's rules pooling |

---

### analytics/services/cohort.py
| Function | Signature | Description |
|---|---|---|
| `split_patients` | `(queryset, group_by) -> dict[str, list]` | Split patients by research dimension |
| `cohort_survival` | `(queryset, group_by, endpoint) -> CohortSurvival` | KM + log-rank per group |
| `build_cox_design` | `(queryset, covariate_specs, endpoint) -> (X, durations, events, names, dropped)` | Build Cox design matrix |
| `cox_regression` | `(queryset, covariate_specs, endpoint) -> (dict, dict)` | Fit multivariable Cox model |
| `cohort_egfr_slope` | `(queryset, group_by) -> dict` | LMM eGFR slope comparison |
| `cohort_competing_risks` | `(queryset, group_by, *, at_days) -> dict` | CIF analysis per group |
| `cohort_summary` | `(queryset, group_by) -> list[dict]` | Baseline + outcome summary |

**Grouping dimensions**: diabetes, diagnosis, cohort, drug:<class>, biomarker:pla2r_response, study:<code>

---

### analytics/services/linalg.py
| Function | Signature | Description |
|---|---|---|
| `zeros` | `(n, m) -> list[list]` | Zero matrix |
| `identity` | `(n) -> list[list]` | Identity matrix |
| `transpose` | `(A) -> list[list]` | Matrix transpose |
| `matmul` | `(A, B) -> list[list]` | Matrix multiplication |
| `matvec` | `(A, x) -> list` | Matrix-vector product |
| `add` | `(A, B) -> list[list]` | Matrix addition |
| `scale` | `(A, c) -> list[list]` | Scalar multiplication |
| `inverse` | `(A) -> list[list]` | Gauss-Jordan inverse |
| `outer` | `(x, y) -> list[list]` | Outer product |

---

### analytics/services/stats_utils.py
| Function | Signature | Description |
|---|---|---|
| `normal_sf_two_sided` | `(z) -> float` | Two-sided survival function of standard normal |

---

### safety/services/summary.py
| Function | Signature | Description |
|---|---|---|
| `safety_summary` | `(queryset) -> dict` | AE counts by category, severity, infection type |
| `infection_incidence` | `(queryset, group_by, *, per) -> dict` | Infection incidence density per group |
| `study_safety` | `(study) -> dict` | Per-arm SAE/infection counts for DSMB |

---

### studies/services/randomization.py
| Function | Signature | Description |
|---|---|---|
| `enroll` | `(study, patient, *, by, screened_date, enrolled_date, require_consent) -> StudyEnrollment` | Screen + enrol + randomize |
| `withdraw` | `(enrollment, *, withdrawn_date) -> StudyEnrollment` | Withdraw from study |
| `study_dashboard` | `(study) -> dict` | CONSORT-style counts |
| `compute_stratum` | `(study, patient) -> str` | Compute stratification factor |
| `generate_sequence` | `(study, arms, stratum, n) -> list[str]` | Deterministic allocation sequence |

**Schemes**: simple, block, stratified_block
**Stratification factors**: diabetes, egfr_stratum, egfr_30, proteinuria_range, gn_subtype, sex

---

### studies/services/eligibility.py
| Function | Signature | Description |
|---|---|---|
| `screen` | `(study, patient) -> (bool, list)` | Screen patient against study criteria |

---

### scheduling/services/schedule.py
| Function | Signature | Description |
|---|---|---|
| `generate_schedule` | `(patient, anchor_date, *, immunosuppressed, horizon_months) -> list[ScheduledVisit]` | Create protocol-mandated visits |
| `due_visits` | `(as_of) -> list[ScheduledVisit]` | Visits due today |
| `overdue_visits` | `(as_of) -> list[ScheduledVisit]` | Overdue visits |
| `clinic_roster` | `(clinic_date) -> dict` | All visits for a clinic day |
| `complete_visit` | `(visit, encounter) -> ScheduledVisit` | Mark visit completed |
| `mark_missed` | `(as_of) -> int` | Flag overdue as missed |
| `nearest_clinic_day` | `(d) -> date` | Nearest Tuesday (configurable) |

**Protocol**: Months 1,3,6,9,12,18,24,30,36,42,48,54,60 + early safety weeks 1,2,4

---

### scheduling/services/monitoring.py
| Function | Signature | Description |
|---|---|---|
| `immunosuppression_alerts` | `(patient) -> list` | Check for overdue monitoring |

---

### audit/services/consent.py
| Function | Signature | Description |
|---|---|---|
| `current_consent` | `(patient, consent_type) -> Consent` | Get current consent |
| `has_consent` | `(patient, consent_type) -> bool` | Check if consent is active |
| `grant_consent` | `(patient, consent_type, form_version, ...) -> Consent` | Grant new consent (supersedes previous) |
| `withdraw_consent` | `(patient, consent_type, ...) -> Consent` | Withdraw consent |
| `consent_history` | `(patient, consent_type) -> QuerySet` | Full consent history |

---

### knowledge/services.py
| Function | Signature | Description |
|---|---|---|
| `extract_patient_features` | `(patient) -> dict` | Extract clinical features for rule evaluation |
| `evaluate_entry` | `(entry, features) -> DiseaseScore` | Evaluate single KB entry against features |
| `evaluate_patient_rules` | `(patient, disease_id) -> list[DiseaseScore]` | Evaluate all active rules for a patient |

**Dataclasses**: `MatchedRule`, `DiseaseScore`

**Rule structure**: `{conditions: [{field, operator, value}], weight, explanation}`

---

### decision/services.py
| Function | Signature | Description |
|---|---|---|
| `evaluate_case` | `(patient) -> dict` | Score patient against 9 disease profiles |
| `classify_phenotype` | `(patient) -> str` | Classify presentation pattern |
| `classify_urgency` | `(patient, ranked) -> dict` | Determine urgency level |
| `build_next_steps` | `(patient, ranked, urgency) -> list` | Generate clinical action suggestions |

**Disease profiles**: iga, membranous, mcd, fsgs, lupus, anca, antiGbm, infectionRelated, c3

---

### timeline/services.py
| Function | Signature | Description |
|---|---|---|
| `aggregate_timeline` | `(patient) -> list[TimelineEvent]` | Cross-domain event aggregation |

---

### exports/services/dataset.py
| Function | Signature | Description |
|---|---|---|
| `columns` | `(identified=False) -> list[str]` | Column list for research dataset |
| `build_row` | `(patient, *, identified) -> dict` | Build one patient row |
| `build_dataset` | `(queryset, *, identified, study) -> (cols, rows)` | Build full dataset |

**Output formats**: CSV (via writers.py), XLSX (openpyxl), SAV (pyreadstat)

---

### exports/services/writers.py
| Function | Signature | Description |
|---|---|---|
| `write_csv` | `(path, columns, rows) -> str` | Write CSV file |
| `write_xlsx` | `(path, columns, rows) -> str` | Write Excel file with formatting |
| `write_sav` | `(path, columns, rows) -> str` | Write SPSS .sav file |

---

### exports/services/dictionary.py
| Function | Signature | Description |
|---|---|---|
| `data_dictionary` | `() -> list[dict]` | Generate data dictionary with column metadata |

---

## Dataclass Summary

| Dataclass | File | Purpose |
|---|---|---|
| `SafetyWarning` | prescriptions/services/safety.py | Prescription safety check result |
| `PlannedAction` | prescriptions/services/reconciliation.py | Single reconciliation action |
| `ReconciliationPlan` | prescriptions/services/reconciliation.py | Full reconciliation plan |
| `KMStep` | analytics/services/survival.py | Kaplan-Meier step |
| `NAStep` | analytics/services/survival.py | Nelson-Aalen step |
| `LogRankResult` | analytics/services/survival.py | Log-rank test result |
| `CoxCovariate` | analytics/services/cox.py | Cox model covariate |
| `CoxResult` | analytics/services/cox.py | Full Cox model result |
| `CIFStep` | analytics/services/competing_risks.py | CIF step |
| `MatchedRule` | knowledge/services.py | Matched knowledge rule |
| `DiseaseScore` | knowledge/services.py | Disease scoring result |
| `GroupResult` | analytics/services/cohort.py | Cohort group result |
| `CohortSurvival` | analytics/services/cohort.py | Full cohort survival result |
