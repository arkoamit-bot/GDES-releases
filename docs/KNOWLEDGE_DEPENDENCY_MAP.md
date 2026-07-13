# Knowledge Dependency Map

## Overview

This document explicitly maps every runtime dependency between GDES Knowledge Platform components. No hidden runtime dependency should remain.

---

## 1. Component Architecture

```
patients.models.Patient
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE LAYER                               │
│                                                                  │
│  knowledge/services.py                                           │
│    extract_patient_features(patient) ───► dict of clinical data  │
│    evaluate_patient_rules(patient)  ───► list[DiseaseScore]      │
│         │                                                         │
│         │  depends on                                                    │
│         ▼                                                         │
│    knowledge/models.py: KnowledgeBaseEntry (ACTIVE status only)   │
│    knowledge/models.py: GuidelineSource                           │
│    knowledge/rule_validator.py (structural validation)            │
│                                                                  │
│  knowledge/bootstrap.py                                          │
│    check_knowledge_base() ───► KnowledgeHealth                    │
│    require_healthy_knowledge() — startup guard                    │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│              CLINICAL REASONING ENGINE                            │
│                                                                  │
│  clinical_reasoning/services/engine.py                           │
│    reason_about_patient(patient) ───► ClinicalProfile            │
│         │                                                         │
│         ├──► knowledge/services.py (feature extraction, rules)    │
│         ├──► disease_trajectory.py (trajectory assessment)        │
│         ├──► care_pathway.py (care gap detection)                │
│         ├──► disease_milestones.py (milestone detection)          │
│         ├──► care_pathway_engine.py (stage/pathway)              │
│         └──► clinical_reasoning/models.py: ClinicalProfile       │
│                                                                  │
│  clinical_reasoning/services/explainability.py                   │
│    build_full_explainability(profile) ───► dict                  │
│                                                                  │
│  clinical_reasoning/models.py: ClinicalInsight                   │
│    created by _generate_insights() in engine.py                  │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│                   DECISION SUPPORT LAYER                          │
│                                                                  │
│  decision/services.py                                            │
│    evaluate_case(patient) ───► ranked differential               │
│    classify_phenotype() / classify_urgency() / build_next_steps() │
│         │                                                         │
│    decision/models.py: DecisionRequest / DecisionResult          │
│                                                                  │
│  decision/explainability.py                                      │
│    build_explainability(patient) / build_traceability_entry()     │
│                                                                  │
│  NOTE: Decision Support uses OLDER scoring rules (hardcoded      │
│  disease profiles), NOT the KnowledgeBaseEntry rule engine.      │
│  This is a parallel system — see §Dual-Pathway Risk.             │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│                  DRUG INTELLIGENCE LAYER                          │
│                                                                  │
│  treatments/interactions.py                                      │
│    check_interactions(drugs, context) ───► list[InteractionResult]│
│                                                                  │
│  treatments/contraindications.py                                 │
│    check_contraindications(drug, diseases, context)               │
│         │                                                         │
│    treatments/models.py: DrugMaster / TreatmentExposure          │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│                EVENT ORCHESTRATION LAYER                          │
│                                                                  │
│  events/dispatcher.py                                            │
│    dispatch(event_type, ...) ───► handlers (in-process or Celery) │
│         │                                                         │
│    events/models.py: Event / EventSubscription                   │
│    clinical_reasoning/event_handlers.py: auto-recompute triggers  │
│                                                                  │
│  bgddr/celery.py (async dispatch — requires Redis broker)        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Explicit Dependency Table

### Knowledge Layer Dependencies

| Consumer | Provider | Dependency Type | Failure Mode |
|----------|----------|----------------|--------------|
| `extract_patient_features()` | `patients.models.Patient` | Model | RuntimeError if Patient schema changes |
| `extract_patient_features()` | `encounters.models.ClinicalEncounter` | Model | RuntimeError if Encounter schema changes |
| `extract_patient_features()` | `labs.models.LabResult` | Model | RuntimeError if LabResult schema changes |
| `extract_patient_features()` | `pathology.models.Biopsy` | Model | RuntimeError if Biopsy schema changes |
| `evaluate_patient_rules()` | `KnowledgeBaseEntry` (ACTIVE) | Query | Returns empty list if no ACTIVE rules (PREVIOUSLY SILENT) |
| `evaluate_patient_rules()` | `GuidelineSource` | FK | PROTECT on delete |
| `evaluate_entry()` | `KnowledgeBaseEntry.rule_data` (JSON) | Schema | ValidateRuleDataError if malformed |
| `_evaluate_condition()` | `KnowledgeBaseEntry.rule_data.conditions` | Schema | Silent False if condition field missing |

### Clinical Reasoning Engine Dependencies

| Consumer | Provider | Dependency Type | Failure Mode |
|----------|----------|----------------|--------------|
| `reason_about_patient()` | `extract_patient_features()` | Function | Returns incomplete features |
| `reason_about_patient()` | `evaluate_patient_rules()` | Function | Returns empty differential (was silent) |
| `reason_about_patient()` | `ClinicalProfile` | Model | DatabaseError on save |
| `reason_about_patient()` | `ClinicalInsight` | Model | DatabaseError on create |
| `_assess_disease_trajectory()` | `disease_trajectory.assess_trajectory()` | Function | Returns default trajectory |
| `_detect_care_gaps()` | `care_pathway.detect_care_gaps()` | Function | Returns empty list |
| `detect_milestones()` | `disease_milestones.detect_milestones()` | Function | Returns empty list |
| `determine_current_stage()` | `care_pathway_engine.PATHWAY_DEFINITION` | Data | Returns "assessment" default |
| `_build_differential()` | `evaluate_patient_rules()` | Function | Returns empty list (was silent) |
| `_save_milestones()` | `patient.clinical_profile` | FK | RelatedObjectDoesNotExist (logged) |
| `_generate_insights()` | `ClinicalProfile` | Model | DatabaseError |

### Event Orchestration Dependencies

| Consumer | Provider | Dependency Type | Failure Mode |
|----------|----------|----------------|--------------|
| `dispatch()` | `Event` model | Model | DatabaseError on save |
| `dispatch()` | Celery / Redis | Service | Fallback to in-process |
| `_run_handlers()` | Handler functions | Import | Handlers are registered; errors isolated per handler |

### Decision Support Dependencies

| Consumer | Provider | Dependency Type | Failure Mode |
|----------|----------|----------------|--------------|
| `evaluate_case()` | Hardcoded disease profiles | Data | Deterministic — no runtime dependency |
| `classify_phenotype()` | Phenotype classification rules | Data | Deterministic |
| `renal_dose_adjustment()` | Drug lookup table | Data | Returns "unspecified" |

### Drug Intelligence Dependencies

| Consumer | Provider | Dependency Type | Failure Mode |
|----------|----------|----------------|--------------|
| `check_interactions()` | Curated interaction table | Data | Returns empty list |
| `check_contraindications()` | Curated contraindication table | Data | Returns empty list |

---

## 3. Dual-Pathway Risk: Decision Support vs. Knowledge Engine

GDES has TWO independent clinical scoring systems:

| Aspect | Decision Support (decision/) | Knowledge Engine (knowledge/) |
|--------|------------------------------|-------------------------------|
| Data source | Hardcoded disease profiles | KnowledgeBaseEntry DB records |
| Status | Deterministic, always available | Depends on ACTIVE rules existing |
| Coverage | 9 diseases | 18+ diseases |
| Rule granularity | Simple scoring | Complex conditions + weights |
| Guideline linkage | None | Full provenance tracking |
| Override tracking | Yes (DecisionResult) | No |
| Explainability | Traces all fired rules | Structured report with evidence |

**Risk**: The two systems may produce DIFFERENT differentials for the same patient.
**Mitigation**: Knowledge Engine is the canonical system. Decision Support exists for backward compatibility.

---

## 4. Knowledge Export Dependencies

| Consumer | Provider | Dependency Type |
|----------|----------|----------------|
| `export_knowledge_base` command | All KnowledgeBaseEntry records | Read |
| `export_knowledge_base` command | GuidelineSource | FK |
| `export_knowledge_base` command | EvidenceEntry | FK |

---

## 5. Critical Hidden Dependencies (Now Explicit)

| # | Hidden Dependency | Discovery | Fix |
|---|-------------------|-----------|-----|
| 1 | ENGINE REQUIRES ACTIVE RULES | Empty differential returned silently | `bootstrap.check_knowledge_base()` active_rules_exist check |
| 2 | `biopsy.gn_diagnosis` → `biopsy.diagnosis` | Feature extraction silently missed biopsy features | Changed `getattr(biopsy, "gn_diagnosis")` to `getattr(biopsy, "diagnosis")` |
| 3 | Celery RESULT_BACKEND requires Redis | 20-second retry delay in test/offline | Default broker URL changed from `redis://localhost:6379/0` to `""` |
| 4 | Rule status filter filters ALL entries | All 229 seed rules imported as DRAFT | `activate_entries` command + admin actions |
| 5 | `evaluate_entry()` silently returns 0 on error | No validation of rule_data structure | `validate_rules` command exists |

---

## 6. Startup Validation Sequence

```
AppConfig.ready()
    │
    ▼
check_knowledge_base()
    ├── 1. tables_exist
    ├── 2. active_guidelines
    ├── 3. active_rules_exist
    ├── 4. guideline_versions_consistent
    ├── 5. evidence_references
    ├── 6. schema_compatible
    └── 7. rule_index
    │
    ▼
If NOT healthy in production → RuntimeError (refuse to start)
If NOT healthy in DEBUG     → Logger warning (continue anyway)
```

---

*Document ID: GDES-V3.6-OBJ1-001*
*Generated: 2026-07-10*
