# Module Integration Matrix

## Integration Density: 38 integration points across 21 BGDDR apps

| Module (App) | Inputs From | Outputs To | Integration Method | FK/Relation |
|---|---|---|---|---|
| **patients** | — | All clinical modules | Patient PK as FK | Central model |
| **encounters** | patients.Patient | decisions, scheduling, analytics | Patient FK + events | FK: patient → Patient |
| **labs** | patients.Patient | analytics, clinical_reasoning, biomarkers | Patient FK + signal → event | FK: patient → Patient |
| **pathology** | patients.Patient | clinical_reasoning, studies | Patient FK | FK: patient → Patient |
| **treatments** | patients.Patient | analytics, clinical_reasoning | Patient FK + signal → event | FK: patient → Patient |
| **prescriptions** | encounters, patients | analytics | Signal → event | FK: encounter → ClinicalEncounter |
| **analytics** | patients, labs, encounters, treatments | clinical_reasoning (event handler) | Direct service call + events | FK: patient → Patient |
| **outcomes** (analytics/) | labs, encounters, pathology | Event handler → clinical_reasoning | `compute_patient_outcome()` called from event_handlers.py:42 | FK: patient → Patient |
| **audit** | All audited viewsets | enterprise_readiness.py | `AuditLog.objects.create()` via AuditedModelViewSet + log_audit_event() | FK: changed_by → User |
| **studies** | patients | research_intelligence | Patient FK + study query | FK: patient → Patient (via enrollment) |
| **safety** | patients | — | Patient FK | FK: patient → Patient |
| **scheduling** | patients | operational_intelligence | Patient FK + encounter query | FK: patient → Patient |
| **biomarkers** | patients, labs | — | Patient FK | FK: patient → Patient |
| **clinical** | patients | — | Patient FK | FK: patient → Patient |
| **knowledge** | patients (via features) | decision, clinical_reasoning | `evaluate_patient_rules()` + `extract_patient_features()` | FK: source → GuidelineSource |
| **decision** | patients, encounters, knowledge | — | Direct service call | FK: patient → Patient, encounter → ClinicalEncounter |
| **timeline** | patients | — | Patient FK | FK: patient → Patient |
| **reminders** | patients, scheduling | — | Patient FK | FK: patient → Patient |
| **fhir** | patients | — | Patient FK | FK: patient → Patient |
| **events** | 7 model signals | clinical_reasoning (handlers) | Signal → Dispatch → Handler | Self-contained models |
| **clinical_reasoning** | patients, knowledge, analytics, treatments, pathology, encounters | API response | Direct service calls + event handlers | FK: patient → Patient (ClinicalProfile), patient → Patient (ClinicalInsight) |

---

## Integration Layer Summary

| Layer | Mechanism | Where |
|---|---|---|
| **Database** | ForeignKey to Patient | 17 models across 12 apps |
| **Signal → Event** | `post_save` → `dispatch()` | `events/signal_handlers.py:8` |
| **Event → Handler** | `subscribe()` → registered function | `clinical_reasoning/event_handlers.py:74` |
| **Service call** | Direct function import | `engine.py:14-15` imports from knowledge, analytics |
| **API call** | HTTP via DRF ViewSets | 15 viewset registrations in `api/urls.py` |
| **Audit** | ViewSet base class | `api/base.py:12` `AuditedModelViewSet` |

---

## Cross-Cutting Integration Touch Points

| Touch Point | Modules |
|---|---|
| Patient registration | patients → events → clinical_reasoning → (profile created) |
| Lab result entry | labs → events → analytics(outcomes) + clinical_reasoning(profile) |
| Biopsy recorded | pathology → events → clinical_reasoning(milestones + differential) |
| Decision request | clinical → decision → knowledge → clinical_reasoning |
| Care pathway eval | clinical_reasoning → patients(phase) + encounters + labs + pathology + treatments |
| Research matching | research_intelligence → patients + studies |
| Operational dashboards | operational_intelligence → patients + encounters + treatments |
