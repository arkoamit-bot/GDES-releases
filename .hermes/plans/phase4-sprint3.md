# Phase 4, Sprint 3: Clinical Analytics & Monitoring

## Overview
Build real-time clinical dashboards, surface existing survival prediction models, and add population-level outcome analytics. The analytics app already has backend infrastructure (survival, regression, quality metrics) — Sprint 3 wires them into usable tools.

## Focus Areas

### 1. Clinical Analytics Dashboard Endpoint (`analytics/views.py`)
**Add a dashboard endpoint returning consolidated metrics:**
- `GET /api/analytics/dashboard/` returning:
  - Total patient count, enrollment trend (last 12 months)
  - Disease distribution (pie-chart ready)
  - Outcome summaries (remission, ESRD, death rates per disease)
  - Quality metrics (biopsy yield, remission concordance)
  - Compliance snapshot (follow-up adherence)

Use existing `dashboard_data.py` and `quality.py` functions as building blocks.

### 2. Kidney Survival Prediction Tool (`analytics/services/prediction.py`)
**New file:** `analytics/services/prediction.py`
- `predict_kidney_survival(patient_data, disease, risk_factors)`:
  - Uses existing cox.py model infrastructure
  - Returns 1/3/5-year kidney survival probabilities
  - Risk factor attribution (what factors drive the prediction)
  - KDIGO risk category (low, moderate, high, very high)

### 3. Patient-Level Clinical Timeline (`analytics/views.py` or new endpoint)
- `GET /api/analytics/patient/{id}/trajectory/`
  - eGFR trajectory (last 24 months)
  - Proteinuria trend
  - Treatment timeline
  - Care gaps summary (from Sprint 2)
  - Current pathway stage (from Sprint 2)

### 4. Population Outcome Report
**Enhance** `cohort_summary_view` to include:
- Disease-specific outcome breakdown (remission, relapse, ESRD)
- Time-to-event statistics (median survival)
- Quality indicator summary per cohort

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `analytics/services/prediction.py` | **Create** | Kidney survival prediction |
| `analytics/views.py` | Modify | Add dashboard + patient trajectory endpoints |
| `analytics/urls.py` | Modify | Wire new endpoints |
| `analytics/dashboard_data.py` | Modify | Add helper for trajectory data |
| `analytics/tests.py` | **Enhance** | Tests for prediction + dashboard |

## Data Flow
```
patient data → predict_kidney_survival() → {survival_probs, risk_factors, kdigo_risk}
              → trajectory_data → {egfr_series, proteinuria_series, treatments}
api endpoint → aggregate → {overview, disease_distribution, outcomes, quality}
```

## Acceptance Criteria
- [ ] `/api/analytics/dashboard/` returns all required fields
- [ ] `predict_kidney_survival()` returns valid 1/3/5-year probabilities
- [ ] Patient trajectory endpoint returns eGFR + proteinuria trend
- [ ] Cohort summary includes disease-specific outcomes
- [ ] All 565+ existing tests still pass
- [ ] Ruff lint passes

## Quality Gates
- `python -m pytest --tb=short -q`
- `python -m ruff check analytics/`
