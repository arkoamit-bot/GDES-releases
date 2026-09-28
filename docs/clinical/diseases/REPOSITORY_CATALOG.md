# Repository Catalog

**Version:** 2.5  
**Pattern:** Repositories persist aggregates and hide persistence details. No business logic in repositories.

---

## Current State

All repositories use **Django ORM Model Managers** directly. There is no dedicated repository layer — services call `Model.objects.filter(...)` directly.

| Aggregate Root | Repository (Current) | Pattern | Business Logic Mixed? |
|---|---|---|---|
| Patient | `Patient.objects` (Django ORM) | Direct ORM | ❌ Clean |
| ClinicalProfile | `ClinicalProfile.objects` (Django ORM) | Direct ORM | ❌ Clean (uses `select_for_update()`) |
| KnowledgeBaseEntry | `KnowledgeBaseEntry.objects` (Django ORM) | Direct ORM | ⚠️ `filter(status=ACTIVE)` in service |
| DecisionRequest | `DecisionRequest.objects` (Django ORM) | Direct ORM | ❌ Clean |
| ClinicalEncounter | `ClinicalEncounter.objects` (Django ORM) | Direct ORM | ❌ Clean |
| LabResult | `LabResult.objects` (Django ORM) | Direct ORM | ❌ Clean |
| Biopsy | `Biopsy.objects` (Django ORM) | Direct ORM | ❌ Clean |
| TreatmentExposure | `TreatmentExposure.objects` (Django ORM) | Direct ORM | ❌ Clean |
| Prescription | `Prescription.objects` (Django ORM) | Direct ORM | ❌ Clean |
| Study | `Study.objects` (Django ORM) | Direct ORM | ❌ Clean |
| PatientOutcome | `PatientOutcome.objects` (Django ORM) | Direct ORM | ❌ Clean |
| Event | `Event.objects` (Django ORM) | Direct ORM | ❌ Clean |
| Site | `Site.objects` (Django ORM) | Direct ORM | ❌ Clean |

---

## Query Patterns by Aggregate

### Patient Repository
| Query | Used By | Frequency | Optimized? |
|---|---|---|---|
| `get(patient_id=X)` | `event_handlers.py` | Per event | ✅ (indexed) |
| `get(pk=X)` | `views.py` | Per API call | ✅ (PK index) |
| `filter(current_phase=X, primary_diagnosis=Y)` | `research_intelligence.py` | Per cohort discovery | ⚠️ (no composite index) |
| `filter(latest_egfr__isnull=False)` | `enterprise_readiness.py` | Per DQ report | ⚠️ (full scan) |
| `all()` loop + per-row subqueries | `operational_intelligence.py` | Per compliance summary | ❌ (N+1) |

### ClinicalProfile Repository
| Query | Used By | Frequency | Optimized? |
|---|---|---|---|
| `select_for_update().get_or_create(patient=X)` | `engine.py` | Per reasoning call | ✅ (PK) |
| `select_related("patient").all()` | `views.py` | Per list API call | ✅ |
| `filter(care_pathway__care_gaps__0__exists=True)` | `views.py` | Per gap query | ⚠️ (JSON field, no index) |

### KnowledgeBaseEntry Repository
| Query | Used By | Frequency | Optimized? |
|---|---|---|---|
| `filter(status=ACTIVE)` | `knowledge/services.py` | Per evaluation | ✅ (indexed on disease_id + status) |
| `filter(status=ACTIVE).select_related("source")` | `knowledge_quality.py` | Per conflict/coverage | ✅ |

### Event Repository
| Query | Used By | Frequency | Optimized? |
|---|---|---|---|
| `create(event_type, ...)` | `dispatcher.py` | Per event | ✅ |
| `filter(event_type=X, occurred_at__gte=Y)` | (potential) | Event replay | ✅ (composite index) |

---

## Missing Repository Features

| Feature | Current State | Recommended |
|---|---|---|
| **Pagination** | Used in API layer via DRF | ✅ Already implemented |
| **Filtering** | Direct queryset chaining | Add reusable filter sets per aggregate |
| **Caching** | None | Add cache layer for read-heavy queries |
| **Soft Delete** | Not implemented | Not needed (audit log covers history) |
| **Query Optimization** | Manual `select_related` | Create optimized query methods on repositories |
| **Specification Pattern** | Not used | Create reusable specification objects for complex queries |

---

## Proposed Repository Interface (for migration)

```python
class PatientRepository:
    def get_by_patient_id(self, patient_id: str) -> Patient: ...
    def get_by_pk(self, pk: int) -> Patient: ...
    def find_by_phase_and_diagnosis(self, phase: str, diagnosis: str) -> QuerySet: ...
    def count_active(self) -> int: ...
    def count_with_egfr(self) -> int: ...
    def iterate_all(self, chunk_size: int = 1000) -> Iterator[Patient]: ...
    def exists_with_biopsy(self, patient: Patient) -> bool: ...
```

Note: Full repository pattern migration is a **Phase 3.0** concern. For 2.5, document the current state and identify where ORM leaks should be sealed.

---

## ORM Leak Assessment

| Leak | Location | Impact | Fix |
|---|---|---|---|
| Service calls `KnowledgeBaseEntry.objects.filter(status=ACTIVE)` | `knowledge/services.py` | Business logic in query | Add repository method `find_active_by_disease()` |
| Service iterates `Patient.objects.all()` with per-row subqueries | `operational_intelligence.py` | Coupling + performance | Add aggregate queries to repository |
| Service accesses `patient.biopsies.exists()` | `disease_milestones.py:74`, `care_pathway_engine.py:166` | ORM lazy loading | Add `has_biopsy()` method |
| Service accesses `patient.encounters.order_by(...)` | `operational_intelligence.py:77` | ORM lazy loading | Add `get_latest_encounter()` method |
