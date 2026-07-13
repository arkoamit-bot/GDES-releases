# GDES Workflow Gap Analysis

## Missing Transitions, Unreachable States, Duplicated Workflows & Orphan Events

Covers: GDES V3.8 Objective 5

---

## 1. Complete E2E Workflow Map

The intended clinical workflow (13 steps):

```
Registration → Baseline → Clinical Assessment → Labs → Biopsy
  → Knowledge Evaluation → Clinical Reasoning → Drug Recommendation
  → Prescription → Timeline Event → Follow-up → Outcome → Export
```

## 2. Missing Transitions

### 2.1 Registration → Baseline: no enforced transition

After patient registration (`registration_status="suspected"`), the baseline is created in a **separate HTTP request** with no guard. A patient can have encounters, labs, biopsies, and prescriptions without ever completing a baseline assessment. The workflow progress strip on the detail page shows baseline as "not done" but does not block downstream actions.

**Impact:** Low — clinical practice may involve patients who received care elsewhere before baseline.

### 2.2 Biopsy → Knowledge Evaluation: no automated trigger

When a biopsy is created, the event bus fires `biopsy.created`, which triggers `reason_about_patient()`. However, the knowledge evaluation step (`evaluate_patient_rules()`) runs inside `reason_about_patient()` only if there are ACTIVE `KnowledgeBaseEntry` rules. If no rules match, the reasoning chain is empty and no diagnostic suggestions appear.

**Impact:** Medium — a patient with a biopsy but no matching KB rules gets no diagnostic output from the reasoning engine.

### 2.3 Drug Recommendation → Prescription: manual bridge

Drug recommendations from the reasoning engine (`ClinicalProfile.care_pathway.recommendations`) are **never automatically converted to prescriptions**. The prescription form is a manual clinician-driven process that carries forward previous prescription items and ongoing TreatmentExposures. There is no "Generate Prescription from Recommendations" button.

**Impact:** Low — prescription is inherently a clinical act requiring clinician judgment.

### 2.4 Prescription → Timeline Event: missing

When a prescription is finalized, the event `prescription.created` fires and is subscribed by clinical_reasoning handlers. However, there is **no automatic `TimelineEvent` creation for prescription finalization**. The timeline only captures events from encounters, clinical assessments, and biopsies.

**Impact:** Low — prescriptions appear in the encounter timeline context, but not in the standalone timeline view.

### 2.5 No automated follow-up scheduling after encounter

When an encounter is created, `apply_visit()` updates the disease phase but does **not** create a `ScheduledVisit`. The scheduling engine (`scheduling/services/schedule.py`) is never called automatically. `encounter.next_due_date` is manually set on the encounter form or during prescription creation.

**Impact:** Medium — clinicians must manually schedule follow-ups.

## 3. Unreachable States

### 3.1 Patient `registration_status = "not_registered"`

Defined in `patients/workflow.py:20` but **never set by any code path**. Patients are either:
- `"suspected"` (default on creation)
- `"registered"` (set by `register_patient()` on positive biopsy)
- `"excluded"` (set on negative biopsy)

The `"not_registered"` status is unreachable.

### 3.2 ClinicalEncounter `encounter_type = "baseline"`

Defined in `encounters/models.py` but the baseline assessment uses a dedicated `BaselineAssessment` model with a separate form (`BaselineForm`), not an encounter with `encounter_type="baseline"`. The encounter types are:
- `"baseline"` — defined but **never used** in any view
- `"followup"` — used by `followup_create()`
- `"unscheduled"` — used for unscheduled visits

**Impact:** Low — the `"baseline"` type is a zombie value.

### 3.3 KnowledgeBaseEntry status "archived"

The KnowledgeBaseEntry lifecycle has 7 states: `draft`, `under_review`, `approved`, `active`, `retired`, `archived`, `deprecated`. The `transition_to()` method in `knowledge/models.py` enforces valid transitions, but the `archived` state has **no outbound transitions defined**. Once a rule reaches `archived`, it can never leave.

**Impact:** Low — archived rules are meant to be permanent; but if a clinician accidentally archives a key rule, it's unrecoverable via the API (admin intervention can still fix via direct DB or migration).

## 4. Duplicated Workflows

### 4.1 Patient deletion: two paths

| Path | File | Transaction | Status |
|------|------|-------------|--------|
| `delete_patient` management command | `patients/management/commands/delete_patient.py` | Yes (manual) | Works (calls `services.delete_patient_cascade`) |
| `patient_delete` clinic view | `clinic/views.py:139-171` | Yes | Works (manual deletion loop) |
| **Admin action** | `patients/admin.py` | Yes | Works (calls `delete_patient_and_all_data`) |

These three paths handle PROTECT FK violations differently. The management command uses `delete_patient_cascade()` (now fixed); the view has its own manual loop; the admin action has its own loop. **The view and admin action duplicate the logic** in `delete_patient_cascade()`.

### 4.2 Lab result recording: two entry points

| Path | File | Best-effort? |
|------|------|-------------|
| Inline labs on baseline/followup forms | `clinic/views.py:_save_labs()` | Yes — errors silently swallowed |
| Dedicated lab results page | `clinic/views.py:lab_results_entry()` | Yes — per-row error handling |

Both call `record_result()` from `labs/services/results.py`. The difference is in error handling: the inline version silently drops errors (bare `except Exception: pass`), while the dedicated page has per-row error messages.

## 5. Orphan Events

18 event types are defined in `events/event_types.py` but **never emitted** by any code (see MODULE_INTEGRATION_REPORT.md §2). Notable gaps:

| Orphan Event | Should Be Emitted By | Impact |
|-------------|---------------------|--------|
| `biopsy.finalized` | Pathology review reaching `is_final=True` | No event-driven recomputation on finalization |
| `prescription.finalized` | `finalize_prescription()` | No event-driven outcome update after prescription |
| `death.recorded` | ClinicalEvent with `event_type=death` | Censoring events don't propagate automatically |
| `decision.requested` | DecisionViewSet.create() | Decision results are siloed |
| `recommendation.generated` | Clinical reasoning engine | Recommendations don't trigger downstream actions |
| `safety_alert.raised` | `finalize_prescription()` safety check | Safety warnings are returned to HTTP caller but not broadcast |
| `reminder.sent` | Reminder engine | No audit trail for sent reminders |
| `follow_up.scheduled` | Scheduling engine | Scheduled visits don't trigger timeline events |
| `visit.overdue` | Scheduling engine | Overdue detection doesn't trigger alerts |
| `outcome.recorded`, `outcome.recomputed` | Outcome engine | Outcome changes don't cascade to reasoning |
| `care_pathway.updated`, `clinical_profile.updated`, `reasoning.completed` | Clinical reasoning engine | Internal events defined but never used |

## 6. Missing Audit Records

The audit trail (`audit/recording.py`) registers models at `audit/apps.py:16-33`. **Notably absent:**

| Model | Missing Audit | Risk |
|-------|--------------|------|
| `LabResult` | ❌ | Lab values can change without audit trail |
| `PatientOutcome` | ❌ | Outcome re-computation not audited |
| `ClinicalProfile` | ❌ | Profile updates not audited |
| `ClinicalInsight` | ❌ | Insight dismissal not audited |
| `DecisionResult` | ❌ | Decision overrides not audited |
| `ScheduledVisit` | ❌ | Schedule changes not audited |

**Critical gap:** Lab results (`LabResult`) carry clinical decisions (eGFR changes, treatment adjustments). Changes to lab data have no audit trail.

## 7. State Machine Gaps

| State Machine | States | Transitions Missing |
|--------------|--------|-------------------|
| **Patient.registration_status** | suspected → registered/excluded | `registered → not_registered` not possible; `excluded → registered` not possible |
| **Patient.current_phase** | active → remission → post_remission → relapse → active | No direct `active → relapse` (must go through remission first) |
| **Prescription.status** | draft → final | No `final → draft` (amendment not possible); no `final → void` |
| **Biopsy.review_status** | pending → awaiting_central → concordant/discordant → adjudicated | No `adjudicated → pending` (re-review not possible) |

## 8. Gap Severity Summary

| # | Gap | Severity | Impact |
|---|-----|----------|--------|
| G1 | No enforced Registration→Baseline transition | 🟡 Medium | Patients in follow-up without baseline data |
| G2 | Biopsy→Knowledge not always triggered | 🟠 High | Silent empty diagnostic suggestions |
| G3 | No automated follow-up scheduling | 🟡 Medium | Manual scheduling burden on clinician |
| G4 | `not_registered` status unreachable | 🟢 Low | Zombie state in enum |
| G5 | `encounter_type=baseline` zombie value | 🟢 Low | Dead code in model |
| G6 | `archived` KB state is a dead end | 🟢 Low | Requires admin intervention to recover |
| G7 | 3 redundant patient-deletion paths | 🟡 Medium | Triple maintenance burden |
| G8 | 2 redundant lab entry points | 🟢 Low | Acceptable UX difference |
| G9 | 18 orphan event types | 🟠 High | Event bus is 58% inactive |
| G10 | LabResult not audited | 🔴 Critical | Clinical data changes leave no trail |
| G11 | Prescription no-amendment state machine | 🟡 Medium | Can't revise finalized prescription |
| G12 | Biopsy review can't re-open | 🟢 Low | Acceptable for final adjudication |
