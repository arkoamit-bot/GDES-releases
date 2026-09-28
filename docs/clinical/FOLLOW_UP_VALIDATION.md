# Follow-up Validation Report
## GDES Version 5.0 — Workstream 6

**Date:** 2026-07-11
**Status:** Complete

---

## Validation Scope

Every automated follow-up capability was evaluated: visit reminders, laboratory reminders, drug monitoring, vaccination reminders, relapse surveillance, remission surveillance, and protocol-driven scheduling.

---

## 1. Visit Reminders

| Aspect | Detail |
|--------|--------|
| **Mechanism** | Celery tasks: `send_due_visit_reminders` (every 12h), `send_overdue_visit_reminders` (every 24h) |
| **What it checks** | `ScheduledVisit` records for due/overdue dates relative to `timezone.now()` |
| **What it does** | Sends email/SMS reminders (configurable via `ReminderTemplate`) |
| **Event emissions** | `reminder.sent` defined but **never dispatched** |
| **✅ Verdict** | Functional — reminders are sent on schedule |
| **⚠️ Issue** | GAP-010: `reminder.sent` event not dispatched. No audit trail of reminder delivery in the event stream. |
| **Priority** | Low |

---

## 2. Overdue Visit Detection

| Aspect | Detail |
|--------|--------|
| **Mechanism** | Celery task: `send_overdue_visit_reminders` (every 24h) |
| **What it checks** | Patients without an encounter within a configurable window (default 180 days for stable, shorter for active disease) |
| **What it does** | Sends overdue notification + marks `visit.overdue` |
| **Event emissions** | `visit.overdue` defined but **never dispatched** |
| **Dashboard display** | ✅ Worklist partial on dashboard shows due/overdue counts |
| **✅ Verdict** | Functional — overdue detection works |
| **⚠️ Issue** | GAP-010: `visit.overdue` event not dispatched. No escalation path for repeated overdue visits. |
| **Priority** | Medium |

---

## 3. Laboratory Reminders

| Aspect | Detail |
|--------|--------|
| **Mechanism** | None dedicated. `detect_lab_trends` Celery task (6h) detects abnormal values but does not check for missing labs. |
| **What should be checked** | Patients on drugs requiring monitoring (e.g., monthly eGFR for SGLT2i, quarterly CBC for MMF) |
| **Current behavior** | No proactive laboratory reminder system. Monitoring protocols define schedules but they are not checked. |
| **✅ Verdict** | **Not implemented** |
| **⚠️ Issue** | GAP-004: Monitoring plans from graph are not executed. GAP-002: Monitoring schedules not auto-generated. |
| **Priority** | **High** |

---

## 4. Drug Monitoring Reminders

| Aspect | Detail |
|--------|--------|
| **Mechanism** | None. Drug-specific monitoring requirements exist in `DrugIntelligence` model (e.g., laboratory_monitoring, vaccination_advice) and `MonitoringProtocol` model (safety_monitoring, monitoring_schedule). |
| **Current behavior** | Data exists but no automation acts on it. |
| **What should happen** | When a patient is prescribed Drug X with monitoring protocol Y, auto-create a `ReminderSchedule` for Y's lab tests at Y's frequency. |
| **✅ Verdict** | **Not implemented** |
| **⚠️ Issue** | GAP-004: Drug monitoring plans exist but are not executed. |
| **Priority** | **High** |

---

## 5. Vaccination Reminders

| Aspect | Detail |
|--------|--------|
| **Mechanism** | None automated. Vaccination advice is stored in `DrugIntelligence.vaccination_advice` as text. |
| **What should happen** | Before or at immunosuppression start, check vaccination status and create reminder |
| **Current behavior** | Vaccination advice is static text in DrugIntelligence. No automated reminder system. |
| **✅ Verdict** | **Not implemented** |
| **⚠️ Issue** | Vaccination tracking is entirely manual. No model for patient vaccination records exists. |
| **Priority** | Medium |

---

## 6. Relapse Surveillance

| Aspect | Detail |
|--------|--------|
| **Mechanism** | `disease_trajectory.assess_trajectory()` monitors for trends indicating relapse. Milestone detection includes `relapse_detected` type. |
| **Current behavior** | Relapse is detected via feature analysis (proteinuria increase, eGFR decline, disease phase change). Manually confirmed via `/patients/<pk>/relapse/` form. |
| **Event trigger** | Relapse detection is part of `reason_about_patient()` — runs on every patient event |
| **✅ Verdict** | Automated surveillance works but only within the clinical reasoning engine. No proactive alert when relapse is suspected. |
| **⚠️ Issue** | When trajectory analysis suggests relapse (e.g., proteinuria doubling, rapid eGFR decline), no `ClinicalInsight` with `priority=critical` is auto-generated. No event is dispatched. |
| **Priority** | Medium |

---

## 7. Remission Surveillance

| Aspect | Detail |
|--------|--------|
| **Mechanism** | `analytics.services.remission` with disease-specific thresholds. `remission_status` in `PatientOutcome`. Milestone detection includes `remission` type. |
| **Current behavior** | Remission is computed automatically on every lab/clinical event. Complete, partial, and IgAN-specific response are tracked. |
| **✅ Verdict** | Automated — remission is computed and stored |
| **⚠️ Issue** | Remission status is stored but not proactively surfaced. No event (`outcome.recorded`) fires when remission status changes. Clinician only sees remission on the quality page or API. |
| **Priority** | Low |

---

## 8. Protocol-Driven Scheduling

| Aspect | Detail |
|--------|--------|
| **Mechanism** | `care_pathway.compute_monitoring_schedule()` computes interval based on disease phase. 8-stage pathway definition has expected durations and required actions. |
| **What it produces** | `monitoring_schedule` dict inside `ClinicalProfile.care_pathway` — describes visit/lab frequency |
| **Current behavior** | Computed and stored but never consumed by scheduling engine |
| **✅ Verdict** | **Not automated** — schedule is computed but not acted upon |
| **⚠️ Issue** | GAP-002: Follow-up intervals are computed but not auto-scheduled |
| **Priority** | **High** |

---

## 9. Missed Appointment Escalation

| Aspect | Detail |
|--------|--------|
| **Mechanism** | None. `visit.overdue` event exists but is never dispatched. No escalation chain for repeated missed visits. |
| **Current behavior** | Patient appears on worklist as "overdue" but no escalation (e.g., notify coordinator after 2 missed visits, notify nephrologist after 3) |
| **✅ Verdict** | **Not implemented** |
| **⚠️ Issue** | GAP-010: overdue events not dispatched |
| **Priority** | Low |

---

## Automated Follow-up Scorecard

| Capability | Status | Missing Component | Priority |
|-----------|--------|-----------------|----------|
| Visit reminders | ✅ Functional | Event dispatch (Low) | Low |
| Overdue visit detection | ✅ Functional | Event dispatch + escalation (Medium) | Medium |
| Lab reminders | ❌ Missing | Full system needed | **High** |
| Drug monitoring reminders | ❌ Missing | Full system needed | **High** |
| Vaccination reminders | ❌ Missing | Full system needed | Medium |
| Relapse surveillance | ⚠️ Partial | Alert generation | Medium |
| Remission surveillance | ✅ Automated | UI surfacing | Low |
| Protocol-driven scheduling | ⚠️ Partial | Execution bridge | **High** |
| Missed appointment escalation | ❌ Missing | Event dispatch + escalation chain | Low |

**Score: 2/9 fully functional, 2/9 partial, 5/9 missing or not implemented.**

---

## Key Findings

1. **Follow-up is the weakest pillar of GDES.** Despite being one of the five core objectives (Automated Patient Follow-up), most follow-up automation exists only as computed data or defined-but-unused event types.

2. **The scheduling engine and clinical reasoning engine do not communicate.** `care_pathway.compute_monitoring_schedule()` produces schedules that are never read by the scheduling app or Celery tasks.

3. **Drug-specific monitoring is data-rich but automation-poor.** The V4.2 `MonitoringProtocol` model and `DrugIntelligence.laboratory_monitoring` contain detailed schedules but no pipeline executes them.

4. **Proactive alerts are absent.** Relapse suspicion, remission achievement, and protocol matching are computed but do not generate alerts or `ClinicalInsight` entries automatically.

5. **No patient can be "lost to follow-up" because there is no formal loss-to-follow-up detection.** The system checks for overdue visits on a fixed 180-day window but does not track cumulative missed visits or escalate.

See `WORKFLOW_GAP_ANALYSIS.md` for resolution plans (GAP-002, GAP-004, GAP-010).
