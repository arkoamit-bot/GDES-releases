# Domain Event Catalog

## 34 Event Types Defined

Source: `events/event_types.py:55-67`

### Patient Lifecycle (2)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `patient.registered` | signal_handlers.py (Patient post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |
| `patient.updated` | signal_handlers.py (Patient post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |

### Encounters (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `encounter.created` | signal_handlers.py (ClinicalEncounter post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |
| `encounter.updated` | signal_handlers.py (ClinicalEncounter post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |
| `encounter.completed` | (defined but not wired to signal) | (no handler) | — |

### Labs (2)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `lab_result.created` | signal_handlers.py (LabResult post_save) | `_on_lab_event` → compute_outcome + reason_about_patient | patient_id, pk, repr |
| `lab_result.updated` | signal_handlers.py (LabResult post_save) | `_on_lab_event` → compute_outcome + reason_about_patient | patient_id, pk, repr |

### Biopsy (2)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `biopsy.created` | signal_handlers.py (Biopsy post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |
| `biopsy.finalized` | (defined but not wired) | (no handler) | — |

### Clinical Events (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `clinical_event.created` | signal_handlers.py (ClinicalEvent post_save) | `_on_clinical_event` → compute_outcome + reason_about_patient | patient_id, pk, repr |
| `hard_kidney_endpoint.reached` | (manual dispatch) | (no handler) | — |
| `death.recorded` | (manual dispatch) | (no handler) | — |

### Prescriptions / Medications (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `prescription.created` | signal_handlers.py (Prescription post_save) | (no handler) | patient_id, pk, repr |
| `prescription.finalized` | (defined but not wired) | (no handler) | — |
| `medication.started` | (defined but not wired) | (no handler) | — |

### Treatment Exposure (2)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `treatment_exposure.created` | signal_handlers.py (TreatmentExposure post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |
| `treatment_exposure.updated` | signal_handlers.py (TreatmentExposure post_save) | `_on_patient_event` → reason_about_patient | patient_id, pk, repr |

### Knowledge / Decision Support (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `decision.requested` | (manual dispatch) | (no handler) | — |
| `recommendation.generated` | (manual dispatch) | (no handler) | — |
| `safety_alert.raised` | (manual dispatch) | (no handler) | — |

### Reminders / Scheduling (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `reminder.sent` | (manual dispatch) | (no handler) | — |
| `follow_up.scheduled` | (manual dispatch) | (no handler) | — |
| `visit.overdue` | (manual dispatch) | (no handler) | — |

### Outcomes (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `outcome.recorded` | (manual dispatch) | (no handler) | — |
| `outcome.recomputed` | (manual dispatch) | (no handler) | — |
| `disease_trajectory.updated` | (manual dispatch) | (no handler) | — |

### Clinical Reasoning (3)
| Event | Emitted By | Handled By | Payload |
|---|---|---|---|
| `clinical_profile.updated` | (manual dispatch) | (no handler) | — |
| `care_pathway.updated` | (manual dispatch) | (no handler) | — |
| `reasoning.completed` | (manual dispatch) | (no handler) | — |

---

## Event Handler Subscriptions

Registered in `clinical_reasoning/event_handlers.py:74-85` (11 subscriptions):

| Handler | Subscribed Events | Action |
|---|---|---|
| `_on_patient_event` | patient.registered, patient.updated, encounter.created, encounter.updated, biopsy.created, treatment_exposure.created, treatment_exposure.updated | `reason_about_patient()` |
| `_on_lab_event` | lab_result.created, lab_result.updated | `compute_patient_outcome()` + `reason_about_patient()` |
| `_on_clinical_event` | clinical_event.created | `compute_patient_outcome()` + `reason_about_patient()` |

---

## Gaps

1. **18 event types have no handlers** — they are defined but never subscribed to (e.g., `encounter.completed`, `death.recorded`, `reminder.sent`).
2. **No event type has multiple handlers** — each subscribed event has exactly 1 handler.
3. **No async processing** — all handlers run synchronously in the request thread.
4. **No event replay mechanism** — persisted events are never re-dispatched programmatically.
