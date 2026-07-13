# End-to-End Clinical Workflows

## Workflow 1: Patient Registration → Clinical Profile

```
User → API POST /api/v1/patients/ [PatientViewSet]
  → Audit: AuditedModelViewSet.initial() sets actor (api/base.py:18)
  → Signal: post_save on Patient → events/signal_handlers.py:_model_post_save
  → Event: dispatch("patient.registered", ...) (events/dispatcher.py:34)
    → Persists Event model record (dispatcher.py:51)
    → Calls registered handlers (dispatcher.py:61)
      → clinical_reasoning/event_handlers.py:_on_patient_event (line 22)
        → _resolve_patient(patient_id) (line 10)
        → reason_about_patient(patient) (services/engine.py:23)
          → extract_patient_features(patient) (knowledge/services.py)
          → evaluate_patient_rules(patient) (knowledge/services.py)
          → assess_trajectory(patient, features) (services/disease_trajectory.py)
          → detect_care_gaps(patient, features) (services/care_pathway.py)
          → detect_milestones(patient, features, trajectory) (services/disease_milestones.py:32)
          → determine_current_stage(patient, features) (care_pathway_engine.py:111)
          → assess_pathway_deviation(patient, stage, features) (care_pathway_engine.py:155)
          → ClinicalProfile.get_or_create + save (engine.py:54-77)
          → Generate ClinicalInsight objects (engine.py:79)
```

**Code paths exercised:** API → Audit → Signal → Event → Handler → 9 service modules → 2 models  
**Test coverage:** `test_event_orchestration.py` test_event_dispatch_and_handlers  
**Data persisted:** Patient, Event, ClinicalProfile, ClinicalInsight (+ AuditLog)

---

## Workflow 2: Lab Result Entry → Outcome Recompute

```
User → API POST /api/v1/lab-results/ [LabResultViewSet]
  → Signal: post_save on LabResult → dispatch("lab_result.created", ...)
  → Handler: _on_lab_event (event_handlers.py:40)
    → compute_patient_outcome(patient) (analytics/services/outcomes.py)
      → Evaluates eGFR trend, proteinuria, remission status
      → Creates/updates PatientOutcome record
    → _on_patient_event → reason_about_patient(patient)
      → Full clinical reasoning pipeline (as above)
```

**Key integration:** Lab results trigger BOTH outcome computation AND clinical profile update in a single handler chain.

---

## Workflow 3: Clinical Decision Request

```
User → POST /api/v1/decisions/evaluate/ [DecisionViewSet]
  → Creates DecisionRequest (decision/models.py:6)
  → Evaluates case using calculators/disease rules
  → Creates DecisionResult with:
    - ranked_differential, urgency, next_steps
    - traceability (KB entries applied)
    - explanation text
  → POST /api/v1/decisions/{id}/override/ [DecisionResultViewSet]
    → Sets override_reason, alternative_diagnosis, overridden_by
```

**Code path:** API → DecisionRequest → rule evaluation → DecisionResult → (optional) override  
**Integration dependency:** `knowledge.models.KnowledgeBaseEntry` for traceability

---

## Workflow 4: Care Pathway Transition

```
Clinical event occurs → _on_clinical_event (event_handlers.py:57)
  → compute_patient_outcome(patient)
  → reason_about_patient(patient)
    → determine_current_stage(patient, features) (care_pathway_engine.py:111)
      → Maps patient.current_phase → pathway stage name
      → Checks eGFR for ESKD detection
    → assess_pathway_deviation(patient, stage, features) (care_pathway_engine.py:155)
      → Checks required actions: biopsy, eGFR
    → compute_pathway_summary(patient, stage, deviations, milestones) (care_pathway_engine.py:187)
    → detect_stage_transition(patient, old_stage, new_stage) validates transition
```

**Stage model:** 8-stage directed graph: assessment → active_disease → remission_monitoring ↔ relapse → ckd_management → eskd_care → post_transplant → conservative_care

---

## Workflow 5: Explainability Request

```
User → POST /api/v1/profiles/explain/ [ClinicalProfileViewSet.explain]
  → Resolves patient by PK
  → Gets or creates ClinicalProfile
  → build_full_explainability(profile) (services/explainability.py:19)
    → Builds: summary, triggering_findings, matched_rules
    → guideline_support, evidence_quality
    → rejected_alternatives with score differences
    → information_gaps with confidence impact
    → audit_trail (profile version, last_updated, feature count)
```

**Returns:** Full explainability report with rationale, evidence grades, and alternative diagnoses.

---

## Workflow 6: Research Cohort Discovery

```
User → API GET /api/v1/research/cohorts/ [ResearchIntelligence view]
  → discover_cohorts() (services/research_intelligence.py:10)
    → Queries Patient by primary_diagnosis + current_phase
    → Builds named cohorts: "Active LN", "Nephrotic Range", "Rapid Decliners"
    → Returns cohort name + patient_count + description
```

**Patient-level matching:** `match_patient_to_protocols(patient)` (research_intelligence.py:72) scores each active study against patient characteristics.
