# Automation Audit
## GDES Version 5.0 — Workstream 3

**Date:** 2026-07-11
**Status:** Complete

---

## Audit Methodology

Every clinical workflow step was evaluated for: (1) whether it is currently automated, (2) the gap between current state and full automation potential, and (3) whether automation would improve the four core objectives (Registry, Clinical Management, Follow-up, Research).

---

## 1. Patient Registration

| Aspect | Detail |
|--------|--------|
| **Current state** | Manual form entry via `/patients/add/` |
| **Automation potential** | High |
| **What could be automated** | Duplicate check (✅ done via HTMX), auto-assign Study ID (✅ done), auto-generate baseline tasks |
| **Gap** | **No baseline tasks or follow-up schedule auto-created on registration.** After registration, the clinician must manually navigate to `/patients/<pk>/baseline/` to enter baseline data. The system knows a new patient needs assessment but does not act on it. |
| **Event trigger** | `patient.registered` fires → clinical profile recomputed |
| **Missing automation** | Auto-create a `ReminderSchedule` for initial baseline visit; auto-create a `ScheduledVisit` for first follow-up at default interval |
| **Clinical impact** | New patients may fall through the gap between registration and first assessment |
| **Priority** | High |

---

## 2. Clinical Encounter (Follow-up Visit)

| Aspect | Detail |
|--------|--------|
| **Current state** | Manual form entry via `/patients/<pk>/followup/` |
| **Automation potential** | High |
| **What is automated** | Carry-forward of previous visit data (✅), clinical profile recomputation (✅ async) |
| **Gap** | **Follow-up interval is not auto-generated.** After encounter, the system should compute the next follow-up date based on disease phase, trajectory, and treatment, then auto-create a `ScheduledVisit`. Currently, `compute_monitoring_schedule()` is called and stored in the clinical profile but never acted upon. |
| **Missing automation** | After `encounter.created` → read `care_pathway.monitoring_schedule` → create `ScheduledVisit` at the recommended interval |
| **Clinical impact** | Clinicians must manually schedule follow-ups. Inconsistency between recommended interval and actual scheduling. |
| **Priority** | High |

---

## 3. Laboratory Results

| Aspect | Detail |
|--------|--------|
| **Current state** | Manual entry via `/patients/<pk>/lab-results/` |
| **Automation potential** | High |
| **What is automated** | eGFR derivation from creatinine (✅), outcome recomputation (✅ async), clinical profile recomputation (✅ async), trend detection (✅ Celery 6h), CKD stage progression alerts (✅) |
| **Gap** | **Missing lab reminders.** The system detects abnormal trends (`detect_lab_trends`) but does not proactively remind clinicians when labs are overdue. `ReminderSchedule` for lab frequency exists in monitoring protocols but is not integrated. |
| **Missing automation** | When `monitoring_protocol.frequency` specifies "monthly" and no lab result exists within the window → generate `ClinicalInsight` with category `monitoring` and priority `high` |
| **Clinical impact** | Patients may miss scheduled lab monitoring between visits |
| **Priority** | Medium |

---

## 4. Biopsy & Diagnosis

| Aspect | Detail |
|--------|--------|
| **Current state** | Manual form entry via `/patients/<pk>/biopsy/` |
| **Automation potential** | Medium |
| **What is automated** | Conditional score forms (MEST-C, ISN/RPS, FSGS, Membranous) auto-show based on diagnosis (✅), clinical profile recomputation (✅) |
| **Gap** | **Central pathology review does not trigger recomputation.** `biopsy.finalized` event is dead code. When a central reviewer changes a diagnosis, downstream systems are not updated. |
| **Missing automation** | Wire `biopsy.finalized` event → recompute clinical profile + outcome + timeline |
| **Clinical impact** | Stale clinical profile after central review changes diagnosis |
| **Priority** | Medium |

---

## 5. Treatment & Prescription

| Aspect | Detail |
|--------|--------|
| **Current state** | Manual form entry via `/patients/<pk>/prescription/` |
| **Automation potential** | High |
| **What is automated** | Duplicate-class warning (✅), renal-dose warning (✅), clinical profile recomputation after finalization (✅ via `treatment_exposure.created`) |
| **Gap 1: Drug-drug interaction checking** | `DrugIntelligence.drug_interactions` JSON exists but is not queried during prescription. No automated DD interaction warning. |
| **Gap 2: Monitoring plan auto-generation** | Graph traversal produces monitoring protocols for each drug (`enhance_treatment_plan()`), but these are stored in `care_pathway.graph_treatment_plan` and never used to create actual lab orders or follow-up visits. |
| **Gap 3: Safety alert dispatch** | No `safety_alert.raised` event is dispatched when a serious AE is recorded or when a contraindicated drug is prescribed. |
| **Missing automation** | 1) Query `DrugIntelligence.drug_interactions` during drug selection → show warning in prescription form. 2) On prescription finalization → read monitoring protocols → auto-create `LabOrder` + `ScheduledVisit`. 3) On SAE → dispatch `safety_alert.raised` → notify responsible clinician. |
| **Clinical impact** | Safety risks (DD interactions); monitoring plans not executed; SAEs not escalated |
| **Priority** | High |

---

## 6. Disease Activity Assessment

| Aspect | Detail |
|--------|--------|
| **Current state** | Fully automated via `reason_about_patient()` |
| **Automation potential** | N/A (already automated) |
| **What is automated** | 10-step pipeline: feature extraction → rule evaluation → graph augmentation → trajectory → care gaps → milestones → risk → evidence → chain → insights |
| **Gap** | **Assessment output not surfaced in the UI at the point of care.** The differential, risk scores, and reasoning chain are stored in `ClinicalProfile` but the patient hub Overview tab does not display them. Clinicians must use the API or quality page to see reasoning output. |
| **Missing automation** | Add a "Clinical Reasoning" section to the patient hub Overview tab showing top differential, risk scores, and recommendations |
| **Clinical impact** | Clinical decision support exists but is invisible to most users |
| **Priority** | High |

---

## 7. Follow-up & Reminders

| Aspect | Detail |
|--------|--------|
| **Current state** | Celery tasks (`send_due_visit_reminders` every 12h, `send_overdue_visit_reminders` every 24h) |
| **Automation potential** | Medium |
| **What is automated** | Due and overdue visit reminders sent (✅), worklist displayed on dashboard (✅) |
| **Gap 1: Event emission** | `reminder.sent`, `follow_up.scheduled`, `visit.overdue` events are defined but **never dispatched**. |
| **Gap 2: Protocol-driven scheduling** | Monitoring protocols have `monitoring_schedule` JSON but the scheduling engine does not read it. Every patient on Drug X with monthly monitoring gets the same schedule manually entered. |
| **Missing automation** | 1) After reminder send → dispatch `reminder.sent`. 2) After overdue detection → dispatch `visit.overdue`. 3) Read monitoring protocol schedules → auto-create `ScheduledVisit` entries. |
| **Clinical impact** | Reminder audit trail missing; protocol-driven scheduling requires manual setup per patient |
| **Priority** | Medium |

---

## 8. Research & Outcomes

| Aspect | Detail |
|--------|--------|
| **Current state** | Outcome engine recomputes automatically on lab/clinical events |
| **Automation potential** | Medium |
| **What is automated** | `PatientOutcome` recomputed automatically (✅), survival analysis available on-demand (✅), cohort discovery runs on query (✅) |
| **Gap 1: Event emission** | `outcome.recorded`, `outcome.recomputed` events defined but never dispatched. |
| **Gap 2: Proactive cohort notification** | `discover_cohorts()` must be called manually. No alert when a patient matches a new protocol. |
| **Missing automation** | 1) After outcome computation → dispatch `outcome.recomputed`. 2) After clinical profile update → re-run `match_patient_to_protocols()` → if match found → create `ClinicalInsight` with category `research`. |
| **Clinical impact** | Research opportunities computed but not surfaced to clinicians |
| **Priority** | Medium |

---

## 9. Data Quality

| Aspect | Detail |
|--------|--------|
| **Current state** | Quality page (`/clinic/quality/`) displays quality metrics on demand |
| **Automation potential** | Low |
| **What is automated** | Missing biopsy %, missing eGFR %, overdue visits %, active without treatment % (✅) |
| **Gap** | **Quality report is static — no trend or alerting.** If data quality drops below a threshold (e.g., >20% missing eGFR), no alert is generated. |
| **Missing automation** | Periodic quality threshold check → if below threshold → create `ClinicalInsight` or dispatch `quality_alert` event |
| **Clinical impact** | Data quality issues may go unnoticed until the quarterly audit |
| **Priority** | Low |

---

## Automation Opportunity Summary

| Area | Current Automation | Gap | Impact | Priority |
|------|-------------------|-----|--------|----------|
| Registration → Baseline | None | No auto-created baseline tasks | Patients lost to first assessment | **High** |
| Encounter → Schedule | Partial | No auto-scheduling from interval | Manual scheduling only | **High** |
| Treatment → Monitoring | Partial | Graph monitoring plans not executed | Monitoring gaps for new drugs | **High** |
| Treatment → Safety | Partial | No DD interaction check | Safety risk | **High** |
| Clinical Assessment → UI | Full | Output not displayed to clinician | CDS invisible | **High** |
| Biopsy → Central Review | Partial | No finalized event → stale profile | Stale recommendations | **Medium** |
| Lab → Reminders | Full | No proactive lab reminders | Missed lab monitoring | **Medium** |
| Research → Notification | Full | No proactive protocol matching | Missed trial opportunities | **Medium** |
| Reminder → Event | Full | Events not dispatched | No audit trail | **Medium** |
| Data Quality → Alert | Full | No threshold alerting | Silent degradation | **Low** |

**5 High priority, 5 Medium priority, 1 Low priority automation gaps identified.**

See `WORKFLOW_GAP_ANALYSIS.md` for detailed resolution plans.
