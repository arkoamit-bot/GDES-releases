# GDES_V5_0_PHASE2_FOLLOWUP_AUTOMATION.md

# GDES Version 5.0
## Phase 2 – Complete Automated Follow-up Engine

Status: Highest Priority

Prerequisite

Priority 1 blockers have been completed.

✓ Audit tests corrected

✓ Clinical Decision Support visible on Patient Hub

✓ ClinicalAssessment integrated into event architecture

The next objective is to complete the automated follow-up engine before implementing the Patient Communication Platform.

---

# Objective

Transform follow-up from a passive scheduling system into an active clinical management engine.

The follow-up engine—not the SMS module—must determine:

• Which patient requires attention

• Why they require attention

• When follow-up is due

• What investigations are required

• What clinician action is required

Communication systems will simply deliver these decisions.

---

# Workstream 1
## Follow-up Rules Engine

Create a dedicated Follow-up Engine responsible for generating future clinical tasks.

Each patient should always have a computed follow-up plan.

The engine should run automatically whenever:

Patient registered

Clinical assessment updated

Laboratory result received

Biopsy completed

Treatment started

Treatment changed

Treatment stopped

Outcome recorded

Clinical reasoning updated

Knowledge rule updated

No manual recalculation should be required.

---

# Workstream 2
## Disease-specific Follow-up Protocols

Every disease should define follow-up schedules.

Examples

IgA Nephropathy

Minimal Change Disease

FSGS

Membranous Nephropathy

Lupus Nephritis

ANCA Vasculitis

Anti-GBM Disease

C3 Glomerulopathy

MPGN / Immune Complex MPGN

Dense Deposit Disease

Each protocol should define:

Visit interval

Required laboratory tests

Monitoring parameters

Drug monitoring

Escalation criteria

Discharge criteria

---

# Workstream 3
## Laboratory Monitoring

Automatically determine when investigations are due.

Examples

Serum Creatinine

eGFR

Urine Protein

Urine Albumin

CBC

LFT

Complement

ANCA

Anti-dsDNA

PLA2R

Tacrolimus Level

Cyclosporine Level

BK PCR

Every investigation should generate:

Due Date

Overdue Date

Priority

Clinical reason

---

# Workstream 4
## Medication Monitoring

Every medication should define:

Monitoring laboratory tests

Monitoring interval

Expected adverse effects

Required vaccinations

Contraindications

Drug interaction review interval

Automatic monitoring tasks should be created.

---

# Workstream 5
## Risk-driven Follow-up

Patients should not all receive identical follow-up.

Adjust interval according to:

Disease activity

Current treatment

Kidney function

Proteinuria

Recent relapse

Recent hospitalization

Recent biopsy

Pregnancy

Transplant status

High-risk patients should automatically receive shorter intervals.

---

# Workstream 6
## Follow-up Task Generation

Generate structured tasks rather than reminders.

Examples

Visit Due

Laboratory Due

Drug Monitoring Due

Vaccination Due

Biopsy Review Due

Safety Review Due

Research Visit Due

Every task should include:

Patient

Priority

Reason

Due date

Status

Responsible clinician

Completion date

---

# Workstream 7
## Escalation Rules

If a task is overdue:

Generate Warning

↓

Notify Responsible Clinician

↓

Escalate to Coordinator

↓

Escalate to Department Dashboard

No patient should silently disappear from follow-up.

---

# Workstream 8
## Clinician Worklist

Automatically generate:

Patients due today

Patients overdue

High-risk patients

Drug monitoring due

Laboratory monitoring due

Missed appointments

Recent relapse

Recent AKI

Rapid eGFR decline

This should become the clinician's daily dashboard.

---

# Workstream 9
## Registry Integration

Every follow-up action must automatically update:

Timeline

Clinical Profile

Outcome Tracking

Research Dataset

Audit Log

Notification Queue

No duplicate entry should be required.

---

# Workstream 10
## Testing

Develop comprehensive tests covering:

Protocol generation

Interval calculation

Task generation

Escalation

Risk stratification

Medication monitoring

Laboratory monitoring

Timeline updates

Research synchronization

Event processing

Target:

100% deterministic tests.

No timing-dependent failures.

---

# Deliverables

followup/

followup/services/

followup/protocols/

followup/tasks.py

followup/escalation.py

followup/dashboard.py

FOLLOWUP_ENGINE_ARCHITECTURE.md

FOLLOWUP_PROTOCOL_LIBRARY.md

FOLLOWUP_VALIDATION_REPORT.md

---

# Success Criteria

Version 5.0 Phase 2 is complete when:

✓ Every patient has an automatically generated follow-up plan.

✓ Disease-specific protocols are implemented.

✓ Laboratory monitoring is automatic.

✓ Drug monitoring is automatic.

✓ Risk-based scheduling functions correctly.

✓ Escalation rules work.

✓ Clinician worklists are generated automatically.

✓ Registry, timeline, research and audit remain synchronized.

✓ No patient becomes lost to follow-up without detection.

---

# Final Instruction

Do NOT begin implementing SMS, email, or WhatsApp delivery during this phase.

The Follow-up Engine must become the single source of truth.

The future Notification Platform will consume follow-up tasks generated here.

Business logic belongs in the Follow-up Engine.

Communication logic belongs in the Notification Engine.

Maintain strict separation of responsibilities.