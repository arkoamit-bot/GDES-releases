# Workflow Validation Report
## GDES Version 5.0 — Workstream 1

**Date:** 2026-07-11
**Status:** Complete
**Validator:** GDES Review Team

---

## Validation Methodology

Each workflow was traced end-to-end by examining: (1) the UI template flow, (2) the view handler logic, (3) the underlying service/API pipeline, (4) the event-driven downstream processing, and (5) the test coverage. Gaps are documented with **clinical impact** and **priority**.

---

## 1. New Patient Journey

```
Registration → Baseline → Encounter → Labs → Biopsy → Pathology Review → Diagnosis → Clinical Reasoning → Treatment → Prescription → Follow-up Scheduling → Outcome Assessment → Research Dataset
```

### Step-by-step Validation

| # | Step | Where | Automated? | Verified? | Notes |
|---|------|-------|-----------|-----------|-------|
| 1 | Patient Registration | `/patients/add/` → `patient_create` → `Patient` model | **Partial** | ✅ Form validates | Event fires `patient.registered` → auto-recomputes clinical profile |
| 2 | Baseline Assessment | `/patients/<pk>/baseline/` → `baseline_edit` → `ClinicalAssessment` | Manual | ✅ 5 fieldsets | No event fires on baseline creation. Clinical profile NOT auto-recomputed after baseline. |
| 3 | Clinical Encounter (follow-up) | `/patients/<pk>/followup/` → `followup_create` → `ClinicalEncounter` | Manual | ✅ Carry-forward | Event fires `encounter.created` → auto-recomputes clinical profile (async) |
| 4 | Lab Results | `/patients/<pk>/lab-results/` → `LabResult` creation | **Partial** | ✅ Creatinine → eGFR | Event fires `lab_result.created` → recomputes outcome + profile (async) |
| 5 | Biopsy | `/patients/<pk>/biopsy/` → `Biopsy` + `GNDiagnosis` | Manual | ✅ Conditional scores | Event fires `biopsy.created` → recomputes profile. Diagnosis updated via `apply_biopsy()`. |
| 6 | Pathology Review | `/clinic/pathology/` → central review forms | Manual | ✅ Concordance tracking | Event `biopsy.finalized` defined but **never dispatched** (no handler in signal_handlers) |
| 7 | Diagnosis Update | Biopsy form → `apply_biopsy()` → updates `Patient.primary_diagnosis` | **Partial** | ✅ | Disease phase advances automatically. But `Patient` update fires `patient.updated` → recomputes clinical profile. |
| 8 | Clinical Reasoning | `clinical_reasoning` engine | **Fully Automated** | ✅ | Triggered by any upstream event. Runs 10-step pipeline. |
| 9 | Treatment Recommendation | `clinical_reasoning` engine embedds into `care_pathway` | **Automated** | ✅ | Graph + rule-based combined. Not displayed in current UI. |
| 10 | Prescription | `/patients/<pk>/prescription/` → `Prescription` draft → finalize → `TreatmentExposure` | Manual | ✅ Drug safety checks | Event fires `treatment_exposure.created` → recomputes profile |
| 11 | Follow-up Scheduling | `compute_monitoring_schedule()` + Celery tasks | **Partial** | ⚠️ | Reminder tasks exist but monitoring schedule not auto-triggered by prescription finalization |
| 12 | Outcome Assessment | `analytics.services.outcomes.compute_patient_outcome()` | **Automated** | ✅ | Triggered by lab + clinical events |
| 13 | Research Dataset Inclusion | `/exports/research-dataset/` | Manual download | ✅ | CSV/XLSX/SAV with 80+ variables |

### ⚠️ Gaps Found

1. **GAP-NP-001**: No event fires after baseline/clinical assessment creation. The `ClinicalAssessment` model is NOT in `_MODEL_EVENT_MAP` in `events/signal_handlers.py`. This means entering a baseline assessment does not automatically trigger clinical profile recomputation.
   - **Clinical Impact**: Clinician enters baseline data but the clinical profile (differential, reasoning chain) is not updated until another event (e.g., lab result) triggers recomputation.
   - **Priority**: High

2. **GAP-NP-002**: `biopsy.finalized` event is defined but never wired to any Django signal handler. Central pathology review confirmation does not trigger automatic recomputation.
   - **Clinical Impact**: After central review changes a diagnosis, the clinical profile is not automatically updated until the patient is touched by another event.
   - **Priority**: Medium

3. **GAP-NP-003**: No event fires on prescription finalization (only on `prescription.created`). The medication reconciliation step (`finalize` → `TreatmentExposure` creation) does trigger via `treatment_exposure.created`, but the `prescription.finalized` event remains unsubscribed.
   - **Clinical Impact**: Minor — the `TreatmentExposure` event chain covers the recomputation need. But `prescription.finalized` is not persisted in the event log.
   - **Priority**: Low

---

## 2. Follow-up Visit Workflow

```
Patient arrives → Retrieve history → Compare results → Disease activity → Remission/Relapse → Drug monitoring → Recommendation update → Follow-up interval → Research update
```

### Validation

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Retrieve previous history | ✅ | `followup_form.html` carries forward previous visit + last labs |
| 2 | Compare current vs previous | ✅ | Chart.js trend chart on patient Overview tab |
| 3 | Disease activity assessment | **Automated** | `reason_about_patient()` evaluates rules, trajectory, care gaps |
| 4 | Remission detection | **Automated** | `analytics.services.remission` with disease-specific thresholds |
| 5 | Relapse detection | Manual | `relapse_create` form; `relapse_detected` milestone tracked |
| 6 | Drug monitoring | **Partial** | Drug safety rules in `rule_validator`; safety alerts event defined but unsubscribed |
| 7 | Recommendation update | **Automated** | Profile recomputation triggered by encounter event |
| 8 | Follow-up interval | **Partial** | `compute_monitoring_schedule()` exists but not auto-called on encounter save |
| 9 | Research update | **Automated** | Outcome recomputation triggered by lab + clinical events |

### ⚠️ Gaps

4. **GAP-FUV-001**: Follow-up interval is computed by `care_pathway.compute_monitoring_schedule()` but the result is stored in the clinical profile's `care_pathway` field — it is not surfaced in the UI or used to generate scheduling actions automatically. The clinician must manually navigate to the worklist to see due dates.
   - **Clinical Impact**: Follow-up intervals are computed but invisible to the clinician at the point of care. Missed opportunity for automated scheduling.
   - **Priority**: High

5. **GAP-FUV-002**: `visit.overdue` event defined but never dispatched. The Celery task `send_overdue_visit_reminders` works independently and does not fire domain events.
   - **Clinical Impact**: Overdue detection exists but the event system is not notified, so no downstream reactions (e.g., escalation, alert generation) occur.
   - **Priority**: Medium

---

## 3. Biopsy Workflow

```
Biopsy request → Biopsy performed → Pathology entered → Diagnosis updated → Reasoning recalculated → Treatment updated → Timeline updated → Research updated
```

### Validation

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Biopsy request | ✅ | `biopsy_form.html` creates `Biopsy` record |
| 2 | Biopsy performed | ✅ | Date, adequacy, histological diagnosis recorded |
| 3 | Pathology entered | ✅ | Disease-specific score blocks (MEST-C, ISN/RPS, etc.) |
| 4 | Diagnosis updated | **Partial** | `apply_biopsy()` updates `Patient.primary_diagnosis`. But central review (`biopsy.finalized` event) is not wired. |
| 5 | Reasoning recalculated | ✅ | `biopsy.created` event triggers profile recomputation |
| 6 | Treatment updated | **Automated** | Profile recomputation includes enhanced treatment plan from graph |
| 7 | Timeline updated | **Partial** | Timeline app has `record_event` but no handler subscribes to `biopsy.created/finalized` |
| 8 | Research updated | **Partial** | Outcome computes `egfr_slope`, `remission_status` from biopsy-anchored assessment periods |

### ⚠️ Gaps

6. **GAP-BX-001**: No `biopsy.finalized` signal handler. Central pathology review confirmation (changing a diagnosis) does not fire an event, so downstream systems (timeline, clinical profile) are not notified.
   - **Clinical Impact**: After central review changes a diagnosis, the timeline and clinical profile become stale until another event triggers recomputation.
   - **Priority**: Medium

---

## 4. Drug Management Workflow

```
Treatment initiated → Interaction check → Contraindication check → Dose adjustment → Monitoring plan → Safety alerts → Lab reminders → Follow-up scheduling
```

### Validation

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Treatment initiated | ✅ | Prescription form with drug picker |
| 2 | Interaction check | ✅ | `prescription_form.html` has live duplicate-class warning |
| 3 | Contraindication check | **Partial** | Renal-dose warning (eGFR threshold) only. No formal drug-drug interaction DB query in the prescription flow. |
| 4 | Dose adjustment | Manual | `adjust_for_renal_function` exists in drug intelligence model |
| 5 | Monitoring plan | **Automated** | `enhance_treatment_plan()` in graph reasoning generates monitoring from graph traversal |
| 6 | Safety alerts | **Partial** | `safety_alert.raised` event defined but **never dispatched** by any handler |
| 7 | Lab reminders | **Partial** | Celery `detect_lab_trends` runs every 6 hours but does not generate reminders for missing labs |
| 8 | Follow-up scheduling | **Partial** | Monitoring protocol has `monitoring_schedule` JSON field but not integrated with scheduling engine |

### ⚠️ Gaps

7. **GAP-DM-001**: No automated drug-drug interaction checking at prescription time. The `DrugIntelligence.drug_interactions` JSON field stores interaction data but it is not queried during the prescription workflow.
   - **Clinical Impact**: Clinicians must manually check for drug interactions. Potential safety issue for patients on multiple immunosuppressants.
   - **Priority**: High

8. **GAP-DM-002**: Monitoring plan from graph reasoning is stored in `care_pathway.graph_treatment_plan` but not surfaced in the prescription UI or used to auto-generate lab orders/follow-up visits.
   - **Clinical Impact**: The system knows which monitoring is needed (from graph traversal) but does not act on it — no auto-creation of lab orders or follow-up visits based on the treatment plan.
   - **Priority**: High

---

## 5. Research Workflow

```
Patient enrolled → Data validated → Cohort assignment → Outcome tracking → Statistical dataset → Publication export
```

### Validation

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | Patient enrolled | ✅ | Study enrollment with eligibility screening |
| 2 | Data validated | **Partial** | Duplicate check exists at registration. No formal data quality score at enrollment time. |
| 3 | Cohort assignment | **Automated** | `research_intelligence.discover_cohorts()` identifies 10 predefined cohorts |
| 4 | Outcome tracking | **Automated** | Outcome engine recomputes on every lab/clinical event |
| 5 | Statistical dataset generation | ✅ | `exports/services/dataset.py` produces 80+ variable dataset |
| 6 | Publication export | ✅ | CSV/XLSX/SAV formats with data dictionary |

### ⚠️ Gaps

9. **GAP-RES-001**: Cohort discovery identifies patients but does not proactively notify the research team. No event or alert when a patient matches a clinical trial protocol.
   - **Clinical Impact**: Research opportunities are computed but not surfaced. Clinicians must manually check study eligibility.
   - **Priority**: Medium

---

## Summary

| Workflow | Steps | Fully Automated | Partial | Manual | Gaps Found |
|----------|-------|----------------|---------|--------|------------|
| New Patient Journey | 13 | 6 | 4 | 3 | 3 |
| Follow-up Visit | 9 | 4 | 3 | 2 | 2 |
| Biopsy | 8 | 3 | 3 | 2 | 1 |
| Drug Management | 8 | 1 | 5 | 2 | 2 |
| Research | 6 | 3 | 2 | 1 | 1 |

**Total gaps identified: 9** (4 High, 3 Medium, 2 Low)

See `WORKFLOW_GAP_ANALYSIS.md` for detailed resolution plans.
