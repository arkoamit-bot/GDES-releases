# Dependency Graph

**Version:** 2.5  
**Goal:** Remove unnecessary coupling, prefer event-driven communication, eliminate circular dependencies

---

## Current State: App-Level Dependency Graph

```
                  ┌──────────────────────────────┐
                  │          events              │
                  │  (dispatcher, signal_handlers)│
                  └──────────┬───────────────────┘
                             │ publishes to
                             ▼
              ┌──────────────────────────────┐
              │    clinical_reasoning         │
              │  (event_handlers subscribes)  │
              └──────────────────────────────┘
                      │  │  │  │  │
        ┌─────────────┘  │  │  │  └──────────────┐
        ▼                 ▼  ▼  ▼                 ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ patients │  │ knowledge│  │ analytics│  │ treatments│
  │ (Patient)│  │ (rules)  │  │(outcomes)│  │ (exposure)│
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
       │
       │ FK references ▼
       ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │encounters│  │  labs    │  │pathology │  │studies   │  │scheduling│
  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │decision  │  │prescript.│  │safety    │  │biomarkers│  │clinical  │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │ timeline │  │ reminders│  │   fhir   │  │   audit  │  │  exports │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

**No circular dependencies detected.** All arrows point away from `patients`.

---

## Dependency Types

| Type | Count | Examples |
|---|---|---|
| FK reference (FK → Patient model) | 19 | All clinical data models |
| Direct service import | 4 | `engine.py` imports from `knowledge.services`, `analytics.services.outcomes` |
| Event subscription | 11 | `event_handlers.py` subscribes to 7 event types |
| API call | 27 | 16 registry + 11 GDES viewset registrations |
| Signal → event bridge | 7 | `signal_handlers.py` listens to 7 model post_save signals |

---

## Unnecessary Coupling

| Coupling | From → To | Current Method | Recommendation |
|---|---|---|---|
| C1 | `disease_milestones.py` → `treatments.models.TreatmentExposure` | Direct queryset | ✅ Acceptable — milestone detection needs to query treatments |
| C2 | `disease_milestones.py` → `pathology.models.Biopsy` | Direct queryset | ✅ Acceptable |
| C3 | `operational_intelligence.py` → `treatments.models.TreatmentExposure` | Direct queryset | ✅ Acceptable |
| C4 | `operational_intelligence.py` → `encounters` | Direct queryset (via Patient) | ✅ Acceptable |
| C5 | `analytics/services/outcomes.py` → `labs.models.LabResult` | Direct queryset | ✅ Acceptable (outcome computation needs lab series) |
| C6 | `analytics/services/outcomes.py` → `encounters` | Direct queryset | ✅ Acceptable |
| C7 | `research_intelligence.py` → `studies.models.Study` | Direct queryset | ✅ Acceptable |
| C8 | `explainability.py` → `clinical_reasoning.models.ClinicalProfile` | Direct model access | ✅ Acceptable (same app context) |

**No unnecessary coupling identified.** All cross-module dependencies are justified by domain requirements.

---

## Proximity Coupling Risks

| Risk | Description | Mitigation |
|---|---|---|
| `reason_about_patient()` calls 4 external services synchronously | Extends request lifecycle | Move to async event handler |
| `_on_lab_event()` chains outcome + reasoning | Two full pipelines in one handler | Split into separate events or async |
| `compute_compliance_summary()` queries 5+ models | Tight coupling for dashboard | Materialized view or cache |
| `compute_patient_outcome()` accesses 4 external querysets | Deep coupling for outcome computation | Acceptable — outcome needs all clinical data |

---

## Target State: Event-Driven Architecture

```
┌──────────────┐     publishes     ┌──────────────────┐     subscribes    ┌──────────────────┐
│ Clinical Apps │ ────────────────▶ │ EventDispatcher  │ ────────────────▶│ ClinicalReasoning│
│ (patients,    │                   │ (async via Celery)│                  │ (profiles)       │
│  labs, etc.)  │                   └──────────────────┘                  │ (analytics)      │
└──────────────┘                                                            └──────────────────┘
       │                                                                           │
       │ (direct FK for reads)                                                     │ (direct FK for reads)
       ▼                                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                     Database                                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

**Principle:** Writes go through events. Reads go through direct FK queries (reads are eventually consistent).

---

## Dependency Simplification Actions

| Action | Current | Target | Priority |
|---|---|---|---|
| Move event dispatch to Celery | Sync in-process | Async via task queue | High |
| Split `_on_lab_event` into two events | One handler does outcome + reasoning | Two handlers, or chained events | Medium |
| Add materialized view for compliance | Dynamic queries over all models | Pre-computed summary | Medium |
| Standardize all API mount points | `/api/v1/` + root prefixes | All under `/api/v1/` | High |
| Remove direct model access from services | Services call `Model.objects` | Repository pattern (Phase I) | Phase I |
