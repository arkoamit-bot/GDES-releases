# Entity Catalog

**Version:** 2.5  
**Pattern:** All entities have a persistent identity (surrogate PK `id` + business key where applicable)

---

## 1. Patient

| Attribute | Type | Notes |
|---|---|---|
| Identity | `patient_id` (BGD-NNNNN) + `id` (PK) | Auto-generated sequential ID |
| Attributes | name, phone, sex, dob, enrollment_date, site, cohort, diabetes_status, primary_diagnosis, latest_egfr, registration_status, current_phase | Clinical & demographic |
| Lifecycle | Suspected → Confirmed → Active → Remission/Relapse/CKD → ESKD/Transplant/Conservative | Via registration_status + current_phase |
| Domain Events | PatientRegistered, PatientUpdated | |
| Repository | `Patient.objects` (Django ORM) | |

**Business invariants:**
- patient_id must be unique
- registration_status must follow valid state transitions
- site must be an active Site

---

## 2. Site

| Attribute | Type | Notes |
|---|---|---|
| Identity | `code` (e.g. BIRDEM, DMCH) + `id` (PK) | Short unique site code |
| Attributes | name, address, phone, email, config, is_active | |
| Lifecycle | Created → Active → Inactive | |
| Domain Events | SiteCreated, SiteDeactivated | |

---

## 3. ClinicalEncounter

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, encounter_date, encounter_type, provider, department, notes | |
| Lifecycle | Created → Updated → Completed | |
| Domain Events | EncounterCreated, EncounterUpdated, EncounterCompleted | |
| Repository | `ClinicalEncounter.objects` | |

**Invariants:** Must reference an existing Patient.

---

## 4. ClinicalEvent

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, event_date, event_type, description, severity | |
| Lifecycle | Created → Updated | |
| Domain Events | ClinicalEventCreated, HardKidneyEndpointReached, DeathRecorded | |

---

## 5. LabResult

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, test, value_numeric, value_text, unit, sample_date, result_date, flag, source, formula_version | |
| Lifecycle | Created → Updated | |
| Domain Events | LabResultCreated, LabResultUpdated, TrendAlertGenerated | |

**Invariants:** test must reference a valid LabTest.

---

## 6. Biopsy

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, biopsy_date, histological_diagnosis, light_microscopy, immunofluorescence, electron_microscopy, review_status | |
| Lifecycle | Created → Under Review → Finalized | |
| Domain Events | BiopsyCreated, BiopsyFinalized | |

---

## 7. PathologyReview

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | biopsy, reviewer, role, diagnosis, notes, is_final | |
| Lifecycle | Created → Updated → Finalized | |
| Domain Events | PathologyReviewSubmitted | |

---

## 8. TreatmentExposure

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, treatment_name, regimen_name, start_date, end_date, dose, route, indication | |
| Lifecycle | Created → Ongoing → Ended | |
| Domain Events | TreatmentExposureCreated, TreatmentExposureUpdated, TreatmentExposureEnded | |

---

## 9. DrugMaster

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | drug_name, drug_class, is_active, default_route, available_routes, renal_dose_adjustment, nephrotoxic, pregnancy_category | Reference data |

---

## 10. Prescription

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | encounter, patient, status, diagnosis_text, printed_at, content_hash, reconciled_at, version | |
| Lifecycle | Draft → Finalized → Reconciled | |
| Domain Events | PrescriptionCreated, PrescriptionFinalized | |

---

## 11. GuidelineSource

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | title, abbreviation, version_year, url, effective_date, retired_date | |
| Lifecycle | Active → Retired | |

---

## 12. KnowledgeBaseEntry

| Attribute | Type | Notes |
|---|---|---|
| Identity | `entry_id` (KB-XXX-NNN) + `id` (PK) | Stable business key |
| Attributes | disease_id, rule_data (JSON), source, evidence_grade, rule_type, status, effective_date, retired_date, tags, guideline_chapter, guideline_paragraph, guideline_quote, evidence_url | |
| Lifecycle | Draft → Reviewed → Active → Retired | |
| Child Entities | KnowledgeBaseVersion, RuleReview, RuleTestResult, EvidenceEntry | |
| Domain Events | RuleCreated, RuleActivated, RuleRetired, RuleConflictDetected | |
| Repository | `KnowledgeBaseEntry.objects` | |

---

## 13. ClinicalProfile

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) — linked 1:1 to Patient | |
| Attributes | features_snapshot (JSON), differential (JSON), disease_trajectory (JSON), care_pathway (JSON), risk_assessment (JSON), evidence_summary (JSON), reasoning_chain (JSON), information_gaps (JSON), milestones (JSON), version | |
| Lifecycle | Created → Updated (version increments on each recompute) | |
| Domain Events | ClinicalProfileUpdated, ReasoningCompleted, CarePathwayUpdated | |
| Repository | `ClinicalProfile.objects` | |

**Invariants:** Version must increment monotonically. Last_updated must reflect most recent recompute.

---

## 14. ClinicalInsight

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, category, priority, title, description, evidence, guidelines, reasoning, actionable, dismissed, expires_at | |
| Lifecycle | Created → Dismissed → Expired | |
| Domain Events | InsightGenerated, InsightDismissed | |

---

## 15. DecisionRequest

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, encounter, input_snapshot | |
| Child Entity | DecisionResult (1:1) | |
| Domain Events | DecisionRequested | |

---

## 16. DecisionResult

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK (same as DecisionRequest) |
| Attributes | phenotype, urgency_level, urgency_tone, urgency_reasons, ranked_differential, next_steps, traceability, explanation, override_reason, alternative_diagnosis, clinician_notes, overridden_by, override_at | |
| Lifecycle | Created → Overridden (optional) | |
| Domain Events | RecommendationGenerated, RecommendationOverridden | |

---

## 17. PatientOutcome

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, outcome_type, event_date, details, computed_at | |
| Domain Events | OutcomeRecorded, OutcomeRecomputed | |

---

## 18. Study

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | protocol_id, name, description, status, target_diagnoses, eligible_phases, is_interventional, max_age_years | |
| Child Entities | StudyEnrollment | |
| Lifecycle | Planned → Recruiting → Active → Completed → Closed | |

---

## 19. AuditLog

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | model_label, object_pk, object_repr, action, field_name, old_value, new_value, changed_by, change_reason | Immutable after creation |

---

## 20. Consent

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, consent_type, form_version, status, consent_date, withdrawn_date, obtained_by, scope, document, notes, supersedes, is_current | |
| Lifecycle | Created → Current → Superseded/Withdrawn | |

---

## 21. Event

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | event_type, source_model, source_pk, payload, occurred_at, processed | Immutable after creation |

---

## 22. ScheduledVisit / Reminder

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, scheduled_date, visit_type, status, notes | |
| Lifecycle | Scheduled → Completed → Missed/Cancelled | |

---

## 23. BiomarkerKinetics

| Attribute | Type | Notes |
|---|---|---|
| Identity | `id` (PK) | Surrogate PK |
| Attributes | patient, biomarker, value, trend, computed_at | Computed/derived entity |

---

## Entity Relationship Summary

| Entity | Aggregate Root | Parent Aggregate |
|---|---|---|
| Patient | ✅ Yes | — |
| Site | ✅ Yes | — |
| ClinicalEncounter | ✅ Yes | — |
| LabResult | ✅ Yes | — |
| Biopsy | ✅ Yes | — |
| PathologyReview | ❌ No | Biopsy |
| TreatmentExposure | ✅ Yes | — |
| DrugMaster | ✅ Yes (reference) | — |
| Prescription | ✅ Yes | — |
| GuidelineSource | ✅ Yes | — |
| KnowledgeBaseEntry | ✅ Yes | — |
| KnowledgeBaseVersion | ❌ No | KnowledgeBaseEntry |
| RuleReview | ❌ No | KnowledgeBaseEntry |
| RuleTestResult | ❌ No | KnowledgeBaseEntry |
| EvidenceEntry | ❌ No | KnowledgeBaseEntry |
| GuidelineDocument | ✅ Yes | — |
| ClinicalProfile | ✅ Yes | — |
| ClinicalInsight | ❌ No | Patient (conceptual) |
| DecisionRequest | ✅ Yes | — |
| DecisionResult | ❌ No | DecisionRequest |
| PatientOutcome | ✅ Yes | — |
| Study | ✅ Yes | — |
| StudyEnrollment | ❌ No | Study |
| AuditLog | ✅ Yes | — |
| Consent | ❌ No | Patient (conceptual) |
| Event | ✅ Yes | — |
| ScheduledVisit | ✅ Yes | — |
| BiomarkerKinetics | ✅ Yes (computed) | — |
