# Workflow Gap Analysis
## GDES Version 5.0 — Workstream 4

**Date:** 2026-07-11
**Status:** Complete

---

## Gap Inventory

Every gap is documented with description, clinical impact, priority, and recommended solution.

---

### GAP-001: Baseline Assessment Does Not Trigger Clinical Profile Update

| Field | Value |
|-------|-------|
| **Description** | `ClinicalAssessment` model is not in the signal-to-event map in `events/signal_handlers.py`. When a clinician enters a baseline assessment, no domain event fires. The clinical profile is not automatically recomputed. |
| **Location** | `events/signal_handlers.py:_MODEL_EVENT_MAP` |
| **Clinical Impact** | High — Clinician enters baseline data but the differential diagnosis, risk scores, and recommendations remain stale until a lab result or follow-up visit triggers recomputation. |
| **Root Cause** | `ClinicalAssessment` was not included when the signal-to-event bridge was designed. |
| **Recommended Solution** | Add `"clinical.ClinicalAssessment": ("clinical_assessment.created", None)` to `_MODEL_EVENT_MAP`. Register a new event type `clinical_assessment.created` in `event_types.py`. Subscribe `clinical_reasoning` event handlers to it. |
| **Effort** | Small (4 files to modify) |
| **Priority** | **High** |

---

### GAP-002: Follow-up Interval Not Auto-Scheduled After Encounter

| Field | Value |
|-------|-------|
| **Description** | `care_pathway.compute_monitoring_schedule()` calculates the recommended follow-up interval based on disease phase. The result is stored in `care_pathway.monitoring_schedule` inside `ClinicalProfile.care_pathway`. But no downstream automation creates a `ScheduledVisit` or updates the clinic roster. |
| **Location** | `clinical_reasoning/services/care_pathway.py` → output consumed by no scheduling action |
| **Clinical Impact** | High — Follow-up intervals are computed but invisible to clinicians. Scheduling depends on manual input. Patients may have overdue follow-ups that the system predicted but did not act on. |
| **Root Cause** | Missing bridge between clinical reasoning output and scheduling engine. |
| **Recommended Solution** | After `reason_about_patient()` completes, if `care_pathway.monitoring_schedule` has a recommended interval, delegate to scheduling service to create a `ScheduledVisit` or update `ReminderSchedule`. Alternatively, create a new `follow_up_scheduled` event and subscribe scheduling app to it. |
| **Effort** | Medium (new service method + event wiring) |
| **Priority** | **High** |

---

### GAP-003: Drug-Drug Interaction Not Checked at Prescription Time

| Field | Value |
|-------|-------|
| **Description** | `DrugIntelligence.drug_interactions` is a JSON field that stores known drug-drug interactions. The prescription form (`prescription_form.html`) has duplicate-class warnings and renal-dose alerts, but does not query the drug interaction data to warn about interacting drug combinations. |
| **Location** | `clinic/forms.py` (prescription form) and `prescriptions` app |
| **Clinical Impact** | High — Patients on multiple immunosuppressants (common in GN) may receive interacting drug combinations without automated warning. |
| **Root Cause** | Drug interaction data is stored but never queried at prescription time. |
| **Recommended Solution** | Add a drug interaction check service that queries `DrugIntelligence.drug_interactions` for all active drugs + new prescription. Add a real-time check in the prescription form (AJAX/HTMX on drug selection) that warns about known interactions. |
| **Effort** | Medium (new service + form JS integration) |
| **Priority** | **High** |

---

### GAP-004: Monitoring Plans From Graph Traversal Not Executed

| Field | Value |
|-------|-------|
| **Description** | `enhance_treatment_plan()` in `knowledge/graph_reasoning.py` traverses `TREATED_BY` → `MONITORED_BY` edges to build monitoring plans for each drug. These plans are stored in `care_pathway.graph_treatment_plan` but are never used to auto-create lab orders, follow-up visits, or reminder schedules. |
| **Location** | `knowledge/graph_reasoning.py` → output consumed by `ClinicalProfile.care_pathway` field only |
| **Clinical Impact** | High — The system knows which monitoring is needed for each drug (e.g., "monthly eGFR for SGLT2i, quarterly CBC for MMF") but does not act on this knowledge. Monitoring gaps are inevitable. |
| **Root Cause** | Graph reasoning integration stops at data storage — no downstream execution pipeline. |
| **Recommended Solution** | Create a service that reads `graph_treatment_plan.monitoring[]` and generates: 1) `LabOrder` records for each required test, 2) `ScheduledVisit` records for each required follow-up at the specified frequency. Hook this into the prescription finalization flow. |
| **Effort** | Medium (new service + scheduling integration) |
| **Priority** | **High** |

---

### GAP-005: Clinical Decision Support Not Surfaced in UI

| Field | Value |
|-------|-------|
| **Description** | `ClinicalProfile` contains the differential diagnosis, risk scores, reasoning chain, evidence summary, and treatment recommendations. This data is available via the REST API (`/api/v1/profiles/<patient_pk>/`) and the quality page (`/clinic/quality/`), but **the patient hub Overview tab does not display it**. Clinicians on the patient hub do not see the automated clinical reasoning output. |
| **Location** | `templates/clinic/patient_detail.html` (Overview tab) |
| **Clinical Impact** | High — The entire clinical decision support system (V4.0 rules + V4.2 graph reasoning) produces rich output but clinicians must leave the patient hub or use the API to see it. This makes the CDS functionally invisible to routine clinical use. |
| **Root Cause** | The patient hub was designed before the clinical reasoning engine existed. |
| **Recommended Solution** | Add a "Clinical Reasoning" section to the patient hub Overview tab showing: top 3 differential diagnoses with scores, risk assessment summary (progression/relapse), key recommendations, information gaps, and syndrome matches. Use the existing API or a new HTMX partial. |
| **Effort** | Medium (template changes + new clinic view) |
| **Priority** | **High** |

---

### GAP-006: `biopsy.finalized` Event Not Wired

| Field | Value |
|-------|-------|
| **Description** | `biopsy.finalized` is defined in `event_types.py` but is never dispatched. The central pathology review process (which confirms or changes a diagnosis) does not fire an event. Downstream systems (clinical profile, timeline, outcomes) are not notified of diagnosis changes from central review. |
| **Location** | `events/event_types.py` (defined but dead) + `pathology` (never dispatched) |
| **Clinical Impact** | Medium — After central review changes a diagnosis, the clinical profile remains stale until another event triggers recomputation. Timeline is not updated. |
| **Root Cause** | The review workflow was added without wiring the event bridge. |
| **Recommended Solution** | Dispatch `biopsy.finalized` from the central review confirmation view/action. Subscribe `clinical_reasoning` to recompute the clinical profile and `timeline` to record the event. |
| **Effort** | Small (view modification + subscription) |
| **Priority** | **Medium** |

---

### GAP-007: Outcome Events Not Dispatched

| Field | Value |
|-------|-------|
| **Description** | `outcome.recorded` and `outcome.recomputed` are defined in `event_types.py` but never dispatched. When `compute_patient_outcome()` completes (either via event handler or management command), no event is fired. |
| **Location** | `analytics/services/outcomes.py` |
| **Clinical Impact** | Medium — No downstream system can react to outcome computation completing. The dashboard outcomes summary refreshes on page load (not event-driven). |
| **Root Cause** | Outcome engine was built before the event system matured. |
| **Recommended Solution** | After `compute_patient_outcome()` successfully saves, dispatch `outcome.recomputed`. |
| **Effort** | Small (one dispatch call) |
| **Priority** | **Medium** |

---

### GAP-008: Clinical Reasoning Events Not Dispatched

| Field | Value |
|-------|-------|
| **Description** | `clinical_profile.updated`, `care_pathway.updated`, `reasoning.completed` are defined in `event_types.py` but never dispatched. When `reason_about_patient()` finishes, no event fires. |
| **Location** | `clinical_reasoning/services/engine.py` |
| **Clinical Impact** | Medium — No downstream integration can react to reasoning completion. Dashboard cannot show real-time "profile updated" indicators. |
| **Root Cause** | Reasoning engine was built without emitting completion events. |
| **Recommended Solution** | At the end of `reason_about_patient()`, dispatch `reasoning.completed` and `clinical_profile.updated`. |
| **Effort** | Small (one dispatch call per event) |
| **Priority** | **Medium** |

---

### GAP-009: Safety Events Not Dispatched

| Field | Value |
|-------|-------|
| **Description** | `safety_alert.raised` is defined in `event_types.py` but never dispatched. Recording a serious adverse event does not trigger any downstream reaction (e.g., alert, clinical profile update, notification). |
| **Location** | `safety` app (no event dispatch) |
| **Clinical Impact** | Medium — SAEs are recorded but do not trigger automated escalation or clinical reasoning update. |
| **Root Cause** | Safety app predates the event system. |
| **Recommended Solution** | After creating an `AdverseEvent` with `is_serious=True`, dispatch `safety_alert.raised`. Subscribe clinical reasoning to re-evaluate the patient's safety profile. |
| **Effort** | Small (event dispatch + subscription) |
| **Priority** | **Medium** |

---

### GAP-010: Reminder Events Not Dispatched

| Field | Value |
|-------|-------|
| **Description** | `reminder.sent`, `follow_up.scheduled`, `visit.overdue` are defined in `event_types.py` but never dispatched. The Celery reminder tasks send notifications but leave no trace in the event log. |
| **Location** | `reminders` app (Celery tasks) and `scheduling` app |
| **Clinical Impact** | Low — Reminder delivery works but cannot be audited via the event stream. No downstream integration possible (e.g., escalate after N overdue reminders). |
| **Root Cause** | Reminder tasks were built before the event system. |
| **Recommended Solution** | After each reminder send, dispatch the appropriate event. Wire a simple audit handler to log to the Event model. |
| **Effort** | Small (dispatch calls in Celery tasks) |
| **Priority** | **Low** |

---

### GAP-011: Study Enrollment Does Not Trigger Profile Update

| Field | Value |
|-------|-------|
| **Description** | When a patient is enrolled in a study, no domain event fires. The clinical profile is not recomputed. Study enrollment data may impact treatment recommendations or risk assessment but the reasoning engine is not notified. |
| **Location** | `studies` app (no event dispatch) |
| **Clinical Impact** | Low — Study enrollment is primarily a research tracking function. Clinical impact is minimal because enrollment does not change clinical data. |
| **Root Cause** | Studies app predates the event system. |
| **Recommended Solution** | Define and dispatch `trial_enrolled` event. Optionally recompute clinical profile if enrollment affects the active treatment plan. |
| **Effort** | Small (event type + dispatch + subscription) |
| **Priority** | **Low** |

---

### GAP-012: Reminder Events Not Dispatched | Timeline Not Integrated With Events

| Field | Value |
|-------|-------|
| **Description** | The timeline app (`timeline/`) has `record_event()` but is never called automatically. Clinical events (biopsy, diagnosis, treatment change, relapse) do not automatically appear in the patient timeline. The timeline must be manually reconstructed. |
| **Location** | `timeline` app — no event subscription |
| **Clinical Impact** | Low — Timeline is available but requires manual maintenance. Most users rely on the encounter/visit history rather than the timeline. |
| **Root Cause** | Timeline was built as a standalone feature, not integrated with the event bus. |
| **Recommended Solution** | Subscribe timeline to key events (biopsy.created, biopsy.finalized, treatment_exposure.created, relapse) and auto-record events. |
| **Effort** | Medium (subscription + event-to-timeline mapping) |
| **Priority** | **Low** |

---

## Gap Prioritization Matrix

| Gap ID | Area | Clinical Impact | Automation Potential | Effort | Priority |
|--------|------|----------------|-------------------|--------|----------|
| GAP-001 | Baseline → Profile | High | High | Small | **High** |
| GAP-002 | Follow-up → Schedule | High | High | Medium | **High** |
| GAP-003 | Prescription → Safety | High | High | Medium | **High** |
| GAP-004 | Treatment → Monitoring | High | High | Medium | **High** |
| GAP-005 | CDS → UI | High | Medium | Medium | **High** |
| GAP-006 | Biopsy → Finalized | Medium | Medium | Small | **Medium** |
| GAP-007 | Outcome → Event | Medium | Medium | Small | **Medium** |
| GAP-008 | Reasoning → Event | Medium | Medium | Small | **Medium** |
| GAP-009 | Safety → Event | Medium | Medium | Small | **Medium** |
| GAP-010 | Reminder → Event | Low | Medium | Small | **Low** |
| GAP-011 | Study → Event | Low | Low | Small | **Low** |
| GAP-012 | Timeline → Events | Low | Low | Medium | **Low** |

---

## Resolution Plan (Ordered by Priority)

| Phase | Gaps | Focus | Estimated Effort |
|-------|------|-------|-----------------|
| **Phase A** (Immediate) | GAP-001, GAP-005, GAP-003 | Safety + CDS visibility | 3-5 days |
| **Phase B** (Short-term) | GAP-002, GAP-004 | Automated scheduling + monitoring execution | 5-7 days |
| **Phase C** (Medium-term) | GAP-006, GAP-007, GAP-008, GAP-009 | Event completeness for core clinical events | 2-3 days |
| **Phase D** (Future) | GAP-010, GAP-011, GAP-012 | Event completeness for secondary events | 2-3 days |
