# GDES Development Plan V10 — Predictive Intelligence

> **"From what happened to what will happen."**

---

## Core Philosophy

**V9 built intelligence. V10 makes it predictive.**

The system now understands what has happened (V9 intelligence). V10 adds the ability to forecast what will happen next — and when to act. Every prediction must be:

1. **Clinically grounded** — derived from validated statistical models, not vibes
2. **Explainable** — every forecast shows its drivers (which data points moved the needle)
3. **Actionable** — tied to a monitoring recommendation or intervention window
4. **Uncertainty-aware** — confidence intervals on every estimate; never a single number

---

## What V10 Is NOT

- NOT a black-box ML model (no neural networks, no "trust me")
- NOT a replacement for clinical judgment — a forecasting assistant
- NOT new Django apps or new database tables where existing ones suffice
- NOT population-level analytics (that's V12)

---

## Existing Data Assets (Already Built)

V10 leverages what V9 and earlier phases already created — no new data collection required:

| Asset | Location | What It Gives V10 |
|-------|----------|-------------------|
| **LabResult.series()** | `labs/models.py` | Longitudinal eGFR, creatinine, proteinuria, albumin, complement, anti-PLA2R, anti-dsDNA over time |
| **PatientOutcome** | `analytics/models.py` | Computed eGFR slope, sustained decline endpoints, remission dates, relapse dates, ESKD/death |
| **ClinicalEvent** | `encounters/models.py` | Time-to-event data: ESKD, dialysis, transplant, death, complete/partial remission, relapse, major CV |
| **BiomarkerKinetics** | `biomarkers/models.py` | Anti-PLA2R trajectory, complement recovery, anti-dsDNA normalization, early responder status |
| **RelapseEpisode** | `encounters/models.py` | Relapse type, criteria, action taken |
| **ClinicalProfile** | `clinical_reasoning/models.py` | Existing risk_assessment JSON (progression/relapse/kidney survival scores) |
| **KM estimator** | `analytics/services/survival.py` | Kaplan-Meier, Greenwood CI, Nelson-Aalen, log-rank |
| **Cox regression** | `analytics/services/cox.py` | Multivariable hazard ratios with 95% CI |
| **Competing risks** | `analytics/services/competing_risks.py` | Cause-specific CIF (kidney + death competing) |
| **Mixed model** | `analytics/services/mixed_model.py` | LMM for eGFR slope comparison |
| **Cohort analysis** | `analytics/services/cohort.py` | Cohort splitting, summary stats, design matrix builder |
| **MICE imputation** | `analytics/services/imputation.py` | Multiple imputation for missing covariates |

---

## V10 Sprint Plan

### Sprint 7 — eGFR Trajectory Prediction

**Goal:** For every patient, forecast their eGFR at 6, 12, and 24 months — with confidence intervals.

**Deliverables:**

1. **`analytics/services/prediction.py`** — new module, single file
   - `PredictedEGFR` dataclass: `{ patient_id, prediction_date, horizon_months, predicted_egfr, lower_ci, upper_ci, model_type, driver_factors, confidence }`
   - `predict_egfr_trajectory(patient_id, horizons=[6, 12, 24])` — main entry point
   - Routing logic:
     - **≥4 eGFR points over ≥6 months**: Linear mixed-effects model (random intercept + slope per patient via existing `mixed_model.py`)
     - **2–3 points**: Linear extrapolation with bootstrap CI
     - **<2 points**: Population-level CKD trajectory table (by disease, baseline eGFR, proteinuria category) — sourced from `Disease.risk_stratification` KB field
   - `_extract_egfr_series(patient_id)` — pulls `LabResult.series(patient, "egfr")`, returns clean `(dates, values)` arrays
   - `_lmm_forecast(dates, values, horizons)` — wraps existing `mixed_model.py` for patient-level forecast
   - `_linear_forecast(dates, values, horizons)` — OLS + bootstrap (100 resamples) for CI
   - `_population_forecast(patient, horizons)` — lookup-based forecast using KB risk stratification data
   - `_explain_driver(patient, series, forecast)` — identifies which factors moved the prediction: "eGFR has declined 3.2 mL/min/year; at this rate, ESKD in ~18 months" vs "eGFR stable; proteinuria improving"

2. **`clinical_reasoning/services/clinical_intelligence.py`** — extend pipeline
   - New step 7.5 (after confidence calculation, before final recommendation):
     ```
     if complexity >= MODERATE:
         egfr_forecast = predict_egfr_trajectory(patient_id, [6, 12])
     else:
         egfr_forecast = predict_egfr_trajectory(patient_id, [12, 24])
     ```
   - `egfr_forecast` added to `ClinicalProfile.risk_assessment["egfr_trajectory"]`
   - If forecast shows ESKD within 24 months → `ClinicalInsight` (category: prognostic, priority: high) auto-generated

3. **Tests** (`analytics/tests/test_prediction.py`)
   - Test OLS forecast against known linear trajectory
   - Test bootstrap CI width (should be narrow with 6+ points, wide with 2–3)
   - Test LMM forecast with mock patient data (≥4 eGFR points)
   - Test population fallback for patients with <2 eGFR values
   - Test `_explain_driver` output contains meaningful text
   - Test integration with `ClinicalIntelligenceService.analyze_patient()` — forecast appears in report

---

### Sprint 8 — Relapse Probability Forecasting

**Goal:** Estimate the probability of relapse at 6 and 12 months — disease-specific, evidence-backed.

**Deliverables:**

1. **`analytics/services/prediction.py`** — extend with:
   - `PredictedRelapse` dataclass: `{ patient_id, prediction_date, horizon_months, probability, lower_ci, upper_ci, risk_factors, protective_factors, monitoring_recommendation }`
   - `predict_relapse_risk(patient_id, horizons=[6, 12])` — main entry point
   - **Disease-specific models:**
     - **IgAN**: Proteinuria trajectory + Oxford MEST-C (S2/T2) + immunosuppression status → Cox model coefficients from published IgAN cohorts (pre-loaded as KB entries)
     - **MN**: Anti-PLA2R trajectory + rituximab exposure + immunological remission status → from `BiomarkerKinetics` (early_pla2r_responder is already computed)
     - **Lupus**: Anti-dsDNA trend + complement recovery + ISN/RPS class + steroid dose → from `BiomarkerKinetics`
     - **FSGS**: Proteinuria trajectory + calcineurin inhibitor exposure + histological variant
     - **General CKD**: eGFR slope + proteinuria category + RAAS blockade adherence
   - Each disease model is a coefficient table stored in the `KnowledgeBaseEntry.rule_data` under a new `prognostic_model` key (NOT code in Python — data in KB)
   - `_get_disease_model(disease_id)` — loads coefficients from KB
   - `_compute_relapse_probability(model, features, horizons)` — applies Cox-like hazard calculation: `h(t) = h0(t) * exp(β'x)` where β coefficients come from the KB model

2. **`knowledge/models.py`** — extend `KnowledgeBaseEntry.rule_data` schema
   - New optional key: `"prognostic_model"` containing:
     ```json
     {
       "baseline_hazard_6mo": 0.08,
       "baseline_hazard_12mo": 0.15,
       "covariates": [
         {"name": "proteinuria_g_per_day", "beta": 0.42, "source": "Jhaveri 2024"},
         {"name": "egfr_slope_per_year", "beta": -0.18, "source": "Jhaveri 2024"},
         {"name": "on_immunosuppression", "beta": -0.35, "source": "Jhaveri 2024"},
         {"name": "oxford_S2_or_higher", "beta": 0.61, "source": "Jhaveri 2024"}
       ],
       "validation_cohort": "STOP-IgAN, TESTING, NefIgAIC",
       "performance": {"c_statistic": 0.78, "calibration_slope": 0.95}
     }
     ```

3. **`clinical_reasoning/services/clinical_intelligence.py`** — extend pipeline
   - New step 7.6: `relapse_forecast = predict_relapse_risk(patient_id)`
   - Stored in `ClinicalProfile.risk_assessment["relapse_forecast"]`
   - If probability > 30% at 6 months → `ClinicalInsight` (prognostic, priority: critical) with monitoring recommendation

4. **Tests** (`analytics/tests/test_prediction.py`)
   - Test IgAN model with known coefficients against manual calculation
   - Test MN model: early PLA2R responder → lower risk
   - Test lupus model: complement recovery → lower risk
   - Test edge cases: missing covariates (graceful degradation), patient with no disease model (population fallback)
   - Test that `ClinicalProfile.risk_assessment` is updated after analysis

---

### Sprint 9 — Treatment Response Prediction

**Goal:** For patients starting or on treatment, predict response probability and optimal monitoring cadence.

**Deliverables:**

1. **`analytics/services/prediction.py`** — extend with:
   - `PredictedResponse` dataclass: `{ patient_id, treatment, response_type, probability, time_to_response_months, confidence, monitoring_cadence, stopping_criteria_met }`
   - `predict_treatment_response(patient_id, treatment=None)` — main entry point
   - **Treatment-specific prediction logic:**
     - **Rituximab in MN**: Probability of anti-PLA2R decline ≥50% at 3/6/12 months, based on baseline PLA2R titer (higher = slower), prior rituximab exposure, rituximab dose. Source: `BiomarkerKinetics` data + KB prognostic models
     - **Rituximab in Lupus**: Probability of complement recovery + anti-dsDNA normalization at 6 months
     - **Immunosuppression in IgAN**: Probability of proteinuria ≥30% reduction at 12 months, based on baseline proteinuria, Oxford MEST-C, ACEi/ARB adherence, eGFR
     - **Calcineurin inhibitors in FSGS**: Probability of partial/complete remission at 6 months, based on histological variant (tip vs collapsing vs NOS), baseline proteinuria
     - **General**: If treatment not specified → infer from `Prescription` model active prescriptions + disease

2. **`clinical_reasoning/services/clinical_intelligence.py`** — extend pipeline
   - New step 7.7: `treatment_response = predict_treatment_response(patient_id)`
   - Stored in `ClinicalProfile.risk_assessment["treatment_response"]`
   - Generates `ClinicalInsight` (category: therapeutic, priority: high) if:
     - Response probability < 30% → "Consider alternative treatment"
     - Stopping criteria met → "Current treatment may be discontinued"

3. **Monitoring cadence optimizer** (within `prediction.py`):
   - `_suggest_monitoring_cadence(treatment, response_probability, side_effect_risk)`:
     - High response probability + low side effect risk → every 3 months
     - Low response probability OR high side effect risk → every 1–2 months
     - Treatment complete (remission) → every 6 months
   - Output stored in `ClinicalProfile.care_pathway["monitoring_cadence"]`

4. **Tests** (`analytics/tests/test_prediction.py`)
   - Test rituximab-MN model: baseline PLA2R 200 → slower response vs PLA2R 20
   - Test rituximab-lupus model: complement already recovered → higher probability
   - Test IgAN model: MEST-C S2T2 + high proteinuria → lower probability
   - Test monitoring cadence logic
   - Test integration: treatment_response appears in `analyze_patient()` report

---

### Sprint 10 — Risk Stratification Dashboard

**Goal:** Clinicians see a risk-stratified patient cohort view — who's declining, who's stable, who needs attention now.

**Deliverables:**

1. **`analytics/services/prediction.py`** — extend with:
   - `PatientRiskSummary` dataclass: `{ patient_id, name, disease, egfr_trend, relapse_risk, treatment_response, overall_risk_tier, next_action, next_action_date }`
   - `risk_stratify_cohort(cohort_filter=None)` — batch prediction for all active patients
     - Returns `PatientRiskSummary` list sorted by overall_risk_tier (critical → high → moderate → low)
     - Filters: by disease, by site, by risk tier, by next-action window
   - `overall_risk_tier(patient)` — composite score combining:
     - eGFR trajectory tier (declining >5 mL/min/yr = critical, 2–5 = high, stable = low)
     - Relapse forecast tier (probability >50% = critical, 30–50% = high, <30% = low)
     - Treatment response tier (probability <30% = critical, 30–60% = moderate, >60% = low)
     - Overall = worst tier across the three dimensions

2. **`analytics/views.py`** — new view
   - `risk_dashboard(request)` — renders the risk-stratified cohort view
     - KPI cards: total patients, critical (amber), high (red), moderate (yellow), low (green)
     - Table: patient name, disease, eGFR trend, relapse risk %, treatment response %, tier badge, next action + date
     - Filters: disease, site, risk tier
     - Sortable columns
   - HTMX partial: `risk_table_partial(request)` for live-filtered table updates

3. **`templates/analytics/risk_dashboard.html`** — new template
   - Extends `base.html`
   - Uses Flowbite card, table, badge components
   - Color-coded tier badges (red/amber/yellow/green)
   - "Analyze" button per patient → runs `analyze_patient()` and redirects to patient detail with forecast in context

4. **`analytics/urls.py`** — add URL
   - `path("risk/", views.risk_dashboard, name="risk_dashboard")`
   - `path("partials/risk-table/", views.risk_table_partial, name="risk-table-partial")`

5. **`templates/base.html`** — add nav link
   - "Risk Dashboard" under Analytics section, key `analytics_risk_dashboard`

6. **Tests** (`analytics/tests/test_prediction.py`)
   - Test `risk_stratify_cohort()` with mock patient data → correct tier assignment
   - Test filter by disease → returns only matching patients
   - Test `overall_risk_tier()` logic
   - Test view renders without error (authenticated client)

---

### Sprint 11 — Prediction Audit & Explainability

**Goal:** Every prediction is auditable, explainable, and stored for later review.

**Deliverables:**

1. **`analytics/models.py`** — extend (no new tables; extend existing)
   - Add `prediction_log` JSONField to `PatientOutcome`:
     ```json
     {
       "last_prediction_date": "2026-07-23",
       "egfr_forecast": {"6mo": 38.2, "12mo": 33.1, "ci_width": 4.2},
       "relapse_forecast": {"6mo": 0.28, "12mo": 0.41, "top_factors": ["proteinuria_g_per_day", "oxford_S2"]},
       "treatment_response": {"treatment": "rituximab", "probability": 0.62, "time_months": 6},
       "overall_tier": "moderate"
     }
     ```

2. **`analytics/services/prediction.py`** — extend with:
   - `_log_prediction(patient_id, egfr, relapse, response, tier)` — writes to `PatientOutcome.prediction_log`
   - `prediction_history(patient_id, limit=10)` — retrieves past prediction snapshots for trend view
   - `prediction_explanation(patient_id)` — returns structured explanation:
     - eGFR drivers: "eGFR has declined 4.1 mL/min/yr over the past 12 months. At this rate, ESKD in approximately 18 months."
     - Relapse drivers: "Proteinuria is 2.8 g/day (nephrotic range). Oxford S2 lesion present. On immunosuppression."
     - Protective factors: "Early PLA2R responder (50% decline in 45 days). On ACEi."
     - Next steps: "Consider increasing monitoring frequency to every 2 months."

3. **`templates/clinic/patient_detail.html`** — extend Clinical Reasoning tab
   - New section: "Predictive Intelligence" below existing intelligence report
   - Shows: eGFR forecast table (6/12/24 month projections with CI), relapse risk gauge, treatment response probability bar, monitoring cadence, overall risk tier badge
   - Expandable "Explanation" section showing driver factors
   - Historical predictions table (if `prediction_log` has prior entries) showing how forecasts have changed over time

4. **`clinical_reasoning/views.py`** — extend patient detail context
   - Add `prediction` context variable from `PatientOutcome.prediction_log`
   - Add `prediction_explanation` from `prediction_explanation()`

5. **Tests** (`analytics/tests/test_prediction.py`)
   - Test `_log_prediction()` writes to `PatientOutcome.prediction_log`
   - Test `prediction_history()` returns sorted recent predictions
   - Test `prediction_explanation()` returns meaningful driver text
   - Test patient detail template renders with prediction context

---

### Sprint 12 — Proactive Alerting & Watchlist

**Goal:** System proactively alerts clinicians when patients cross risk thresholds.

**Deliverables:**

1. **`analytics/services/prediction.py`** — extend with:
   - `Alert` dataclass: `{ patient_id, alert_type, severity, message, triggered_by, threshold, current_value, recommended_action, created_at }`
   - `check_predictions_for_alerts(patient_id)` — evaluates all predictions against alert thresholds:
     - **eGFR alert**: eGFR dropped ≥5 mL/min in 6 months → "Acute kidney injury suspected" (severity: critical)
     - **eGFR alert**: eGFR trajectory suggests ESKD within 12 months → "Prepare for renal replacement therapy discussion" (severity: high)
     - **Relapse alert**: 6-month relapse probability > 50% → "High relapse risk; consider intensifying monitoring" (severity: high)
     - **Treatment alert**: Response probability < 20% after 6 months on treatment → "Consider treatment modification" (severity: critical)
     - **Monitoring gap**: No lab results in ≥ 3 months for patient on active treatment → "Monitoring gap detected" (severity: moderate)
     - **Biomarker alert**: Anti-PLA2R rising after immunological remission → "Possible relapse; urgent review needed" (severity: critical)
   - `get_patient_alerts(patient_id, include_resolved=False)` — returns active (unresolved) alerts for patient
   - `get_cohort_alerts(cohort_filter=None)` — returns all active alerts across cohort, sorted by severity

2. **`feedback/models.py`** — extend (no new table; add alert to existing models or use `PatientOutcome.prediction_log["active_alerts"]`)
   - Store active alerts in `PatientOutcome.prediction_log["active_alerts"]` as a list
   - Each alert has a `resolved` boolean and `resolved_by` / `resolved_at` / `resolution_note` fields
   - `_resolve_alert(patient_id, alert_type, resolved_by, note)` — marks alert resolved

3. **`analytics/views.py`** — new view
   - `alerts_dashboard(request)` — renders all active alerts across cohort
     - Grouped by severity (critical → high → moderate)
     - Patient name, disease, alert type, message, recommended action, "View Patient" link
     - Filter: by severity, by disease, by alert type
   - `resolve_alert(request, patient_id, alert_type)` — POST handler to resolve an alert

4. **`templates/analytics/alerts_dashboard.html`** — new template
   - Extends `base.html`
   - Red/amber/yellow alert cards grouped by severity
   - Total active alert count badge in nav

5. **`analytics/urls.py`** — add URL
   - `path("alerts/", views.alerts_dashboard, name="alerts_dashboard")`
   - `path("alerts/<int:patient_id>/<str:alert_type>/resolve/", views.resolve_alert, name="resolve_alert")`

6. **`templates/base.html`** — add nav link
   - "Alerts" under Analytics section, with active alert count badge (if > 0)
   - Key: `analytics_alerts`

7. **`clinical_intelligence.py`** — extend pipeline
   - New step 8 (after treatment response): `alerts = check_predictions_for_alerts(patient_id)`
   - If any critical alerts → `ClinicalInsight` (priority: critical) auto-generated
   - Alerts added to report returned by `analyze_patient()`

8. **Tests** (`analytics/tests/test_prediction.py`)
   - Test eGFR drop alert triggers when slope exceeds threshold
   - Test relapse probability alert triggers at > 50%
   - Test monitoring gap alert triggers when no labs in 3 months
   - Test `resolve_alert()` correctly marks alert resolved
   - Test `get_cohort_alerts()` returns sorted by severity
   - Test alert integration with `analyze_patient()` — critical alerts appear in report

---

## V10 File Map

```
analytics/
  models.py              — extend PatientOutcome with prediction_log JSONField
  services/
    prediction.py        — NEW: all prediction logic (Sprints 7-12)
  views.py               — add risk_dashboard, alerts_dashboard, resolve_alert
  urls.py                — add risk/, alerts/ URLs
  tests/
    test_prediction.py   — NEW: tests for all prediction functions
templates/
  analytics/
    risk_dashboard.html  — NEW: risk-stratified cohort view
    alerts_dashboard.html — NEW: alerts dashboard
  clinic/
    patient_detail.html  — extend with Predictive Intelligence section
  base.html              — add nav links for Risk Dashboard + Alerts
clinical_reasoning/
  services/
    clinical_intelligence.py — extend pipeline with prediction steps + alerts
  views.py               — extend patient_detail context
knowledge/
  models.py              — document prognostic_model schema in KB rule_data
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| eGFR forecast MAE at 12 months | < 5 mL/min (vs naive slope extrapolation) |
| Relapse prediction c-statistic | > 0.70 (disease-specific models) |
| Treatment response prediction calibration slope | 0.8–1.2 |
| Alert false-positive rate | < 20% (clinician-resolved within 7 days) |
| Prediction audit coverage | 100% of patients analyzed have prediction_log |
| Clinician adoption | Risk dashboard used ≥ 3x/week per active clinician |
| Test coverage (prediction module) | ≥ 95% |

---

## Data Dependencies

| What We Need | Where It Comes From | Status |
|--------------|---------------------|--------|
| Longitudinal eGFR (≥4 values) | `LabResult.series(patient, "egfr")` | ✅ Available |
| Proteinuria trajectory | `LabResult.series(patient, "upcr")` or `proteinuria` | ✅ Available |
| Anti-PLA2R trajectory | `BiomarkerKinetics` | ✅ Available |
| Complement levels | `BiomarkerKinetics` | ✅ Available |
| Anti-dsDNA | `BiomarkerKinetics` | ✅ Available |
| Oxford MEST-C | `Patient.oxford_mestc` | ✅ Available |
| ISN/RPS class | `Patient.isn_rps_class` | ✅ Available |
| Disease identity | `Patient.primary_diagnosis` | ✅ Available |
| Active prescriptions | `prescriptions.Prescription` | ✅ Available |
| Relapse history | `RelapseEpisode` | ✅ Available |
| Time-to-event endpoints | `ClinicalEvent` + `PatientOutcome.duration_event()` | ✅ Available |
| Published Cox coefficients for disease-specific models | `KnowledgeBaseEntry.rule_data["prognostic_model"]` | ⚠️ Must be populated per disease |

**Key dependency:** Sprint 8+ requires curated prognostic model coefficients in the knowledge base. These come from published literature and must be manually entered or imported from guideline documents. Sprint 7 (eGFR trajectory) has zero external dependencies — it uses only the patient's own longitudinal data.

---

## Non-Goals (V10)

- NO new Django apps
- NO new database tables (extend existing models only)
- NO machine learning model training (use published coefficients only)
- NO population-level analytics (V12)
- NO real-time data streams (batch predictions run on-demand or nightly)
- NO external prediction APIs (all computation local)
- NO integration with commercial EHR prediction tools

---

## Estimated Effort

| Sprint | Focus | Estimated Duration |
|--------|-------|-------------------|
| 7 | eGFR trajectory prediction | 2–3 days |
| 8 | Relapse probability forecasting | 3–4 days (requires KB model curation) |
| 9 | Treatment response prediction | 2–3 days |
| 10 | Risk stratification dashboard | 2 days |
| 11 | Prediction audit & explainability | 2 days |
| 12 | Proactive alerting & watchlist | 2–3 days |
| **Total** | | **13–17 days** |

---

*V10 builds on V9's intelligence foundation. Every prediction feeds back into the Clinical Intelligence Service — making the system not just smart, but forward-looking.*
