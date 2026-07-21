# Follow-up Engine Architecture

## Overview

The Follow-up Engine transforms follow-up from a passive scheduling system into an active clinical management engine. It determines **which** patient requires attention, **why**, **when** follow-up is due, **what** investigations are required, and **what** clinician action is needed.

## Design Principles

1. **Engine is the single source of truth** — All follow-up decisions are computed deterministically by the engine. No manual scheduling.
2. **Strict separation of concerns** — Business logic lives in the Follow-up Engine. Communication logic belongs in the Notification Platform (not yet built).
3. **Event-driven recomputation** — Any relevant data change automatically triggers plan recalculation.
4. **Disease-specific protocols** — Each GN disease defines its own visit schedule, lab requirements, and monitoring parameters per KDIGO 2024 guidelines.
5. **Risk-adaptive intervals** — High-risk patients automatically receive shorter follow-up intervals.
6. **No patient lost to follow-up** — Escalation chain ensures overdue tasks are escalated through warning → clinician → coordinator → department dashboard.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      Event Bus (events/)                      │
│  PATIENT_REGISTERED, ENCOUNTER_CREATED, LAB_RESULT_CREATED,   │
│  BIOPSY_CREATED, TREATMENT_EXPOSURE_CREATED, OUTCOME_RECORDED │
│  CLINICAL_PROFILE_UPDATED, CLINICAL_ASSESSMENT_UPDATED        │
└────────────────────────┬─────────────────────────────────────┘
                         │ dispatches to
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              followup/event_handlers.py                       │
│              _on_data_event()                                 │
└────────────────────────┬─────────────────────────────────────┘
                         │ calls
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              followup/services/engine.py                      │
│              compute_followup_plan(patient)                   │
│                                                               │
│  1. Select protocol (get_protocol_for_patient)                │
│  2. Assess risk (assess_risk_category)                        │
│  3. Calculate visit interval                                  │
│  4. Determine next visit date                                 │
│  5. Cancel stale tasks                                        │
│  6. Generate new tasks (task_generator)                       │
│  7. Dispatch FOLLOW_UP_PLAN_UPDATED event                     │
└────────────────────────┬─────────────────────────────────────┘
                         │ uses
                         ▼
┌──────────────────────────────────────────────────────────────┐
│  followup/protocols/          followup/services/              │
│  ┌──────────────────┐        ┌────────────────────────┐      │
│  │ IgANFollowUp     │        │  risk.py               │      │
│  │ MCDFollowUp      │        │  (risk stratification)  │      │
│  │ FSGSFollowUp     │        └────────────────────────┘      │
│  │ MembranousFollow │        ┌────────────────────────┐      │
│  │ LupusNephritis   │        │  task_generator.py     │      │
│  │ ANCAFollowUp     │        │  (task creation)       │      │
│  │ AntiGBMFollowUp  │        └────────────────────────┘      │
│  │ C3GFollowUp      │        ┌────────────────────────┐      │
│  │ MPGNFollowUp     │        │  escalation.py         │      │
│  │ DDDFollowUp      │        │  (overdue escalation)  │      │
│  │ GeneralFollowUp  │        └────────────────────────┘      │
│  └──────────────────┘        ┌────────────────────────┐      │
│                               │  dashboard.py          │      │
│                               │  (clinician worklist)  │      │
│                               └────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

## Data Model

### FollowUpTask
The only persistent model. Each row represents one structured clinical task.

| Field | Type | Description |
|-------|------|-------------|
| patient | FK → Patient | Target patient |
| task_type | CharField | visit_due, lab_due, drug_monitoring_due, vaccination_due, biopsy_review_due, safety_review_due, research_visit_due |
| priority | CharField | routine, urgent, emergent |
| reason | Text | Human-readable reason |
| clinical_reason | Text | Why this task is needed |
| due_date | Date | When the task is due |
| overdue_date | Date | When it becomes overdue |
| status | CharField | pending, completed, cancelled, overdue |
| assigned_to | FK → User | Responsible clinician |
| escalation_level | Integer | 0=none, 1=warning, 2=clinician, 3=coordinator, 4=department |
| protocol_label | CharField | e.g. "IgAN Month 3" |

## Protocol Classes

Each disease protocol is a Python class (not a DB model) inheriting from `FollowUpProtocol`:

- `disease_id` — machine key matching ClinicalProfile differential entries
- `base_visit_interval_days` — default interval (90 days for most)
- `visit_schedule` — list of timepoints with labels and days from index
- `required_labs` — lab tests required at routine visits
- `interval_labs` — lab tests with independent intervals
- `drug_monitoring` — drug class → lab requirements mapping
- `escalation_criteria` — triggers for escalation
- `discharge_criteria` — criteria for protocol discharge
- `get_visit_interval(patient, risk_category)` — returns risk-adjusted interval

Protocols are selected automatically. Priority: ClinicalProfile differential → biopsy GNDiagnosis → General protocol.

## Event Wiring

The engine subscribes to 17 event types via `followup/event_handlers.py`:

- `patient.registered`, `patient.updated`
- `encounter.created`, `encounter.updated`
- `lab_result.created`, `lab_result.updated`
- `biopsy.created`
- `clinical_assessment.created`, `clinical_assessment.updated`
- `treatment_exposure.created`, `treatment_exposure.updated`
- `clinical_event.created`
- `outcome.recorded`, `outcome.recomputed`
- `clinical_profile.updated`, `care_pathway.updated`, `reasoning.completed`

Additionally, `followup/services/engine.py` connects direct Django `post_save` signals for models not in the event signal-to-event map.

## Risk Stratification

`assess_risk_category()` returns one of: `very_high`, `high`, `moderate`, `low`.

Factors considered:
- eGFR (<15, 15-29, 30-44, 45-59)
- eGFR decline (sustained >=40%)
- Proteinuria (nephrotic-range, 1.0-3.5, 0.3-1.0)
- Disease trajectory trend (declining, relapse)
- Recent relapse (<6 months)
- Recent hospitalization (<3 months)
- Recent biopsy (<3 months)
- Immunosuppression intensity (cyclophosphamide/rituximab vs maintenance)
- Transplant status
- Pregnancy
- ESKD / composite kidney endpoint
- Recent clinical event

The risk category directly drives visit interval: very_high = 0.5×, high = 0.6×, moderate = 0.75×, low = 1.0×.

## Escalation Chain

```
Task overdue (past due_date)
    ↓ 7 days overdue
Level 1: Warning generated
    ↓ 14 days overdue
Level 2: Notify responsible clinician
    ↓ 30 days overdue
Level 3: Notify coordinator
    ↓ 60 days overdue
Level 4: Department dashboard
```

## Clinician Worklist

`dashboard.get_daily_worklist(as_of)` generates:
- Patients due today
- Patients overdue
- High-risk patients
- Drug monitoring due
- Laboratory monitoring due
- Missed appointments
- Recent relapses (<3 months)
- Recent AKI (<1 month)
- Rapid eGFR decline (<3 months)

## Registry Integration

Every follow-up action automatically updates:
- **Timeline**: Via `FOLLOW_UP_PLAN_UPDATED` event → timeline event_handlers
- **Clinical Profile**: Via `CLINICAL_PROFILE_UPDATED` event (triggered by reasoning)
- **Outcome Tracking**: Via `OUTCOME_RECOMPUTED` event
- **Research Dataset**: Via events → research sync handlers
- **Audit Log**: Via `audit/recording.py` signal handlers
- **Event Log**: Every plan update persists an Event row in `events/models.py`

No duplicate entry required.
