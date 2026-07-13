# Dependency Audit

## App-Level Dependency Graph

```
patients ─┬→ encounters
          ├→ labs
          ├→ pathology
          ├→ treatments
          ├→ prescriptions
          ├→ analytics
          ├→ studies
          ├→ safety
          ├→ scheduling
          ├→ biomarkers
          ├→ clinical
          ├→ decision
          ├→ timeline
          ├→ reminders
          ├→ fhir
          └→ clinical_reasoning
```

**No circular dependencies between apps.** All arrows point away from `patients`.

### Dependency Direction Map

| App | Imports From | Imported By |
|---|---|---|
| patients | choices.py, workflow.py | All clinical apps |
| encounters | patients.Patient | analytics, decision, scheduling |
| labs | patients.Patient | analytics, biomarkers |
| pathology | patients.Patient | clinical_reasoning (milestones) |
| treatments | patients.Patient | analytics, clinical_reasoning (milestones) |
| analytics | patients, labs, encounters, treatments | clinical_reasoning (event_handlers) |
| knowledge | patients (via services.py), GuidelineSource | decision, clinical_reasoning |
| decision | patients, encounters, knowledge | — |
| events | patients (signal_handlers), own models | clinical_reasoning (handlers) |
| clinical_reasoning | patients, knowledge, analytics, treatments, pathology, encounters | — |
| audit | auth.User | clinical_reasoning (enterprise_readiness) |

---

## Service-Layer Call Graph

```
reason_about_patient() ─┬→ extract_patient_features()       [knowledge]
                        ├→ evaluate_patient_rules()          [knowledge]
                        ├→ assess_trajectory()               [disease_trajectory]
                        ├→ detect_care_gaps()                [care_pathway]
                        ├→ detect_milestones()               [disease_milestones]
                        │     ├→ _check_biopsy_milestone     [pathology.Biopsy]
                        │     └→ _check_treatment_milestones [treatments.TreatmentExposure]
                        ├→ determine_current_stage()         [care_pathway_engine]
                        ├→ assess_pathway_deviation()        [care_pathway_engine]
                        ├→ compute_pathway_summary()         [care_pathway_engine]
                        ├→ _assess_risk()                    [engine]
                        └→ _generate_insights()              [engine]
```

### Event Handler Call Graph

```
_on_lab_event() ─┬→ compute_patient_outcome()  [analytics/services/outcomes.py]
                 │     ├→ _series()             [labs.LabResult]
                 │     ├→ _proteinuria_series() [labs.LabResult]
                 │     ├→ _disease_key()        [patients.Patient.primary_diagnosis]
                 │     └→ _last_contact()       [encounters]
                 └→ _on_patient_event()
                       └→ reason_about_patient() [as above]
```

---

## Dependency Risks

| Risk | Location | Impact |
|---|---|---|
| `compute_patient_outcome()` called synchronously in event handler | `event_handlers.py:42` | Blocks request for full outcome + reasoning pipeline |
| `_count_missing_biopsy()` iterates ALL patients | `operational_intelligence.py:40` | O(N) query per field, grows with registry size |
| `compute_care_gap_trends()` iterates all profiles | `operational_intelligence.py:130` | No pagination; memory pressure with 10K+ patients |
| `match_patient_to_protocols()` iterates all active studies per patient | `research_intelligence.py:80` | N studies × M patients without caching |
| `recompute_all_profiles()` single-transaction loop | `engine.py:285` | One failed patient rolls back entire batch (individual transactions within loop OK, but outer iteration not) |

## Dependency Design Patterns

| Pattern | Where Used | Count |
|---|---|---|
| Direct function import | engine.py imports from knowledge, analytics | 4 imports |
| Django queryset | service functions query models directly | 15+ querysets |
| Event dispatch | signal → handler chain | 11 subscriptions |
| API-to-service | ViewSet calls service function | 5 viewset actions |
