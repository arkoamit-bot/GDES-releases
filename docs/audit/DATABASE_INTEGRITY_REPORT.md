# Database Integrity Report

## Schema Overview

**Database engine:** SQLite (dev), PostgreSQL (prod, with `SELECT FOR UPDATE` support)  
**Total models:** 30+ across 21 BGDDR apps  
**Migration count:** 1 per app (clinical_reasoning has 2 migrations)

### Central Entity: Patient

Patient is referenced by **19+ ForeignKey relationships** across all clinical apps:

| App | Model | FK Field | On Delete |
|---|---|---|---|
| encounters | ClinicalEncounter | patient | CASCADE |
| labs | LabResult | patient | CASCADE |
| pathology | Biopsy | patient | CASCADE |
| treatments | TreatmentExposure | patient | CASCADE |
| prescriptions | Prescription | patient | CASCADE |
| analytics | PatientOutcome | patient | CASCADE |
| audits | Consent | patient | CASCADE |
| studies | StudyEnrollment (presumed) | patient | CASCADE |
| safety | AdverseEvent | patient | CASCADE |
| scheduling | ScheduledVisit | patient | CASCADE |
| biomarkers | BiomarkerKinetics | patient | CASCADE |
| clinical | (referenced) | patient | CASCADE |
| decision | DecisionRequest | patient | CASCADE |
| timeline | (referenced) | patient | CASCADE |
| reminders | (referenced) | patient | CASCADE |
| fhir | (referenced) | patient | CASCADE |
| clinical_reasoning | ClinicalProfile | patient | CASCADE (OneToOne) |
| clinical_reasoning | ClinicalInsight | patient | CASCADE |

### Key Constraints

| Constraint | Location | Purpose |
|---|---|---|
| `Patient.patient_id` UNIQUE | `patients/models.py:59` | Stable patient identifier (BGD-NNNNN) |
| `EventSubscription.(event_type, handler_path)` UNIQUE | `events/models.py:33-34` | Prevent duplicate handler registrations |
| `ClinicalProfile.patient` OneToOne | `clinical_reasoning/models.py:17` | One profile per patient |
| `Consent.(patient, consent_type)` UNIQUE WHERE is_current | `audit/models.py` | One active consent per type per patient |
| `KnowledgeBaseVersion.(entry, version_number)` UNIQUE | `knowledge/models.py:91` | Version uniqueness per entry |
| `UserSiteRole.(user, site)` UNIQUE | `patients/models.py:138` | Single role per user per site |
| `KnowledgeBaseEntry.entry_id` UNIQUE | `knowledge/models.py:41` | Stable KB entry identifier |

### Index Coverage

| Index | Model | Fields | Purpose |
|---|---|---|---|
| PK indexes | All models | id | Primary key lookups |
| event_type + occurred_at | Event | event_type, occurred_at | Event listing by type |
| processed + event_type | Event | processed, event_type | Pending event processing |
| last_updated | ClinicalProfile | last_updated | Recent profile queries |
| patient + category | ClinicalInsight | patient, category | Insight filtering |
| patient + priority + dismissed | ClinicalInsight | patient, priority, dismissed | Active alerts |
| abbreviation + version_year | GuidelineSource | abbreviation, version_year | Guideline lookup |
| disease_id + status | KnowledgeBaseEntry | disease_id, status | Rule evaluation |
| model_label + object_pk | AuditLog | model_label, object_pk | Audit trail queries |
| changed_at | AuditLog | changed_at | Recent audit entries |

### Query Patterns

**Frequently executed queries (identified from service code):**

| Pattern | Location | Frequency | Optimization Status |
|---|---|---|---|
| `Patient.objects.get(patient_id=X)` | event_handlers.py | Per event | Indexed |
| `Patient.objects.get(pk=X)` | views.py | Per API call | PK index |
| `KnowledgeBaseEntry.objects.filter(status=ACTIVE)` | knowledge/services.py | Per evaluation | Indexed |
| `ClinicalProfile.objects.select_for_update().get_or_create(patient=X)` | engine.py | Per reasoning call | Uses PK |
| `TreatmentExposure.objects.filter(patient=X)` | disease_milestones.py | Per milestone check | FK index |
| `Patient.objects.all()` loop | operational_intelligence.py | Per compliance summary | Full scan |
| `Biopsy.objects.filter(patient=X).exists()` | multiple | Per patient check | FK index |
| `ClinicalProfile.objects.select_related("patient").all()` | views.py | Per list query | Covered by PK |

### Data Integrity Risks

| Risk | Location | Severity | Mitigation |
|---|---|---|---|
| `_save_milestones()` with `update_fields=["milestones"]` | `disease_milestones.py:163` | Low | `last_updated` won't auto-update; version field still tracks |
| `select_for_update()` but no retry on deadlock | `engine.py:54` | Medium | Add retry decorator for concurrent profile access |
| Bulk patient iteration without pagination | `engine.py:291`, `operational_intelligence.py:40-82` | Medium | Use `iterator(chunk_size=1000)` |
| No unique constraint on clinical profile fields | `clinical_reasoning/models.py` | Low | OneToOne PK already ensures uniqueness |
| Patient cascade delete affects 19+ models | `patients/models.py` | High | `on_delete=PROTECT` recommended for multi-site deployments |

### Migration Health

| Status | Count |
|---|---|
| Applied migrations | 20+ (1 per app, +1 for clinical_reasoning) |
| Unapplied migrations | 0 |
| Circular dependency | None detected |
| Squashed migrations | None needed (< 5 per app) |
