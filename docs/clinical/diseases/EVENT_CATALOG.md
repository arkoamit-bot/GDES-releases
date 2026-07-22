# Event Catalog (Event Storming)

**Version:** 2.5  
**Pattern:** Every important state change generates a domain event. Events are immutable records of past occurrences.

---

## Legend

| Icon | Meaning |
|---|---|
| ✅ | Wired — signal → dispatch → handler |
| 🔌 | Wired — signal → dispatch (no handler) |
| 📝 | Defined — not yet wired to any signal or dispatch call |
| ❌ | Not defined — notable gap |

---

## Patient Lifecycle Events

### PatientRegistered
| Attribute | Detail |
|---|---|
| **Trigger** | Patient post_save (created=True) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_patient_event` → `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Retry** | ❌ No retry on failure |
| **Status** | ✅ Fully wired |

### PatientUpdated
| Attribute | Detail |
|---|---|
| **Trigger** | Patient post_save (created=False) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_patient_event` → `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Status** | ✅ Fully wired |

---

## Encounter Events

### EncounterCreated
| Attribute | Detail |
|---|---|
| **Trigger** | ClinicalEncounter post_save (created=True) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_patient_event` → `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Status** | ✅ Fully wired |

### EncounterUpdated
| Attribute | Detail |
|---|---|
| **Trigger** | ClinicalEncounter post_save (created=False) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_patient_event` → `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Status** | ✅ Fully wired |

### EncounterCompleted
| Attribute | Detail |
|---|---|
| **Trigger** | (no automatic trigger) |
| **Publisher** | Manual dispatch |
| **Subscribers** | (none) |
| **Status** | 📝 Defined but not wired |
| **Recommendation** | Wire to signal on encounter status change; trigger outcome recompute |

---

## Laboratory Events

### LabResultCreated
| Attribute | Detail |
|---|---|
| **Trigger** | LabResult post_save (created=True) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_lab_event` → `compute_patient_outcome()` + `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Status** | ✅ Fully wired |

### LabResultUpdated
| Attribute | Detail |
|---|---|
| **Same as LabResultCreated** | |
| **Status** | ✅ Fully wired |

### TrendAlertGenerated
| Attribute | Detail |
|---|---|
| **Trigger** | (not implemented) |
| **Status** | ❌ Not defined |
| **Recommendation** | Define and emit when eGFR/proteinuria trend crosses threshold |

---

## Biopsy Events

### BiopsyCreated
| Attribute | Detail |
|---|---|
| **Trigger** | Biopsy post_save (created=True) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_patient_event` → `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Status** | ✅ Fully wired |

### BiopsyFinalized
| Attribute | Detail |
|---|---|
| **Trigger** | (no automatic trigger) |
| **Publisher** | Manual dispatch |
| **Subscribers** | (none) |
| **Status** | 📝 Defined but not wired |
| **Recommendation** | Wire to signal on review_status change to finalized; trigger differential recompute |

---

## Clinical Events

### ClinicalEventCreated
| Attribute | Detail |
|---|---|
| **Trigger** | ClinicalEvent post_save (created=True) |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | `_on_clinical_event` → `compute_patient_outcome()` + `reason_about_patient()` |
| **Payload** | `{patient_id, pk, repr}` |
| **Status** | ✅ Fully wired |

### HardKidneyEndpointReached
| Attribute | Detail |
|---|---|
| **Trigger** | (no automatic trigger) |
| **Status** | 📝 Defined but not wired |
| **Recommendation** | Emit when outcome computation detects ESKD onset |

### DeathRecorded
| Attribute | Detail |
|---|---|
| **Trigger** | (no automatic trigger) |
| **Status** | 📝 Defined but not wired |
| **Recommendation** | Wire to ClinicalEvent with event_type=death |

---

## Treatment & Prescription Events

### PrescriptionCreated
| Attribute | Detail |
|---|---|
| **Trigger** | Prescription post_save |
| **Publisher** | `signal_handlers.py:\_model_post_save` |
| **Subscribers** | (none) |
| **Status** | 🔌 Wired to signal, no handler |
| **Recommendation** | Subscribe handler to check drug-drug interactions |

### PrescriptionFinalized
| Status | 📝 Defined but not wired |

### MedicationStarted
| Status | 📝 Defined but not wired |

### TreatmentExposureCreated
| **Status** | ✅ Fully wired |

### TreatmentExposureUpdated
| **Status** | ✅ Fully wired |

---

## Decision Support Events

### DecisionRequested
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from DecisionViewSet.create(); log for audit |

### RecommendationGenerated
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from DecisionResult creation; trigger notification |

### SafetyAlertRaised
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit when drug interaction or contraindication detected |

---

## Follow-up & Scheduling Events

### ReminderSent
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from reminders system; log to audit trail |

### FollowUpScheduled
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit when ScheduledVisit created |

### VisitOverdue
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from scheduled compliance check (Celery beat) |

---

## Outcome Events

### OutcomeRecorded
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from `compute_patient_outcome()` on first outcome record |

### OutcomeRecomputed
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from `compute_patient_outcome()` on update |

### DiseaseTrajectoryUpdated
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from `reason_about_patient()` when trajectory trend changes |

---

## Clinical Reasoning Events

### ClinicalProfileUpdated
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit from `reason_about_patient()` after profile save |

### CarePathwayUpdated
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit when care pathway stage changes |

### ReasoningCompleted
| Status | 📝 Defined but not wired |
|---|---|
| **Recommendation** | Emit at end of `reason_about_patient()`; could trigger downstream analytics |

---

## Missing Events (Recommended)

| Event | Trigger | Purpose |
|---|---|---|
| `SiteActivated` / `SiteDeactivated` | Site.is_active toggle | Multi-center operations |
| `PatientStatusChanged` | Registration status transition | Workflow triggers |
| `RuleActivated` / `RuleRetired` | KnowledgeBaseEntry status change | Knowledge platform governance |
| `StudyOpened` / `StudyClosed` | Study status transition | Research operations |
| `ConsentGranted` / `ConsentWithdrawn` | Consent creation/withdrawal | Compliance |
| `DataExported` | Export operation | Audit |

---

## Event Handler Failure Analysis

| Scenario | Current Behavior | Desired Behavior |
|---|---|---|
| Handler raises exception | Logged, event lost | Retry 3x with backoff, then dead-letter |
| DB unavailable | Event not persisted, exception logged | Queue for retry |
| Patient not found | Warning logged, handler returns | Create alert for admin |
| Payload malformed | Exception logged | Schema validation before dispatch |
| Handler timeout | No timeout mechanism | Add async processing with timeout |
