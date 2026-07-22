# Technical Debt Report

**Version:** 2.5  
**Scope:** Code TODOs, deprecated code, duplicates, dead code, naming inconsistencies, API inconsistencies

---

## TODOs in Code

| Location | Line | TODO | Severity |
|---|---|---|---|
| (None found in active code) | — | — | — |

**Assessment:** Zero TODO comments in active code. Good discipline.

---

## Naming Inconsistencies

| Issue | Current | Should Be | Location |
|---|---|---|---|
| IN-01 | `signal_handlers.py` named inconsistently with `event_handlers.py` | Both follow `_handlers.py` convention | `events/signal_handlers.py` vs `clinical_reasoning/event_handlers.py` |
| IN-02 | `_count_lost_to_follow_up()` uses underscore convention | `count_lost_to_follow_up()` (public) | `operational_intelligence.py:30` |
| IN-03 | `_count_missing_biopsy()` vs `_count_missing_egfr()` — some use `pct` field, others don't | Consistent pattern | `operational_intelligence.py:30-82` |
| IN-04 | `_assess_risk()` is in `engine.py` (application service) | Should be in domain service | `engine.py:171` |
| IN-05 | `_determine_care_stage()` in engine.py duplicates `determine_current_stage()` in care_pathway_engine.py | Remove duplicate | `engine.py:212` vs `care_pathway_engine.py:111` |
| IN-06 | `disease_milestones.py` filename — singular vs plural inconsistency | `disease_milestone.py` (singular) | `clinical_reasoning/services/` |
| IN-07 | Some services export public functions with underscore prefix (`_check_biopsy_milestone`) | Should be private | `disease_milestones.py` |

---

## Duplicate Implementations

| ID | Duplicate | Locations | Lines | Action |
|---|---|---|---|---|
| DUP-01 | Missing biopsy detection | `engine.py:114-120`, `care_pathway_engine.py:164-173`, `operational_intelligence.py:40-46` | 15 lines × 3 | Consolidate into shared function |
| DUP-02 | Missing eGFR detection | `engine.py:126-131`, `care_pathway_engine.py:176-183`, `operational_intelligence.py:49-52` | 10 lines × 3 | Consolidate into shared function |
| DUP-03 | Overdue visit detection | `care_pathway.py` (gap detection), `operational_intelligence.py:70-82` | 8 lines × 2 | Consolidate |
| DUP-04 | Patient resolution logic | `_resolve_patient()` in `event_handlers.py:10` — also exists in pattern across `views.py:55` | 5 lines × 2 | Extract to shared utility |
| DUP-05 | ESKD detection (eGFR < 15) | `care_pathway_engine.py:116-118`, `disease_milestones.py:102` | 3 lines × 2 | Consolidate |
| DUP-06 | `_determine_care_stage()` vs `determine_current_stage()` | `engine.py:212-226` vs `care_pathway_engine.py:111-128` | Full function | Remove `engine.py` version (unused) |

---

## Dead Code

| ID | Dead Code | Location | Reason |
|---|---|---|---|
| DEAD-01 | `_determine_care_stage()` in engine.py | `engine.py:212-226` | Defined but never called — `determine_current_stage()` in care_pathway_engine.py is used instead |
| DEAD-02 | `hard_kidney_endpoint.reached` event | `events/event_types.py:22` | Defined, no emitter, no handler |
| DEAD-03 | `death.recorded` event | `events/event_types.py:23` | Defined, no emitter, no handler |
| DEAD-04 | `prescription.finalized`, `medication.started` events | `events/event_types.py:27-28` | Defined, no emitter, no handler |
| DEAD-05 | 18 other unhandled event types | `events/event_types.py` | Defined but no subscribers, no emitters |

---

## API Inconsistencies

| ID | Issue | Details |
|---|---|---|
| API-01 | Mixed URL prefixes | 11 apps at root level, 15+ at `/api/v1/` |
| API-02 | `results/` endpoint name conflict | `decision/urls.py` registers `results/` which is generic |
| API-03 | Error format inconsistency | Some endpoints return `{"error": "..."}`, others DRF default `{"detail": "..."}` |
| API-04 | No API version header | All versioning via URL prefix only |
| API-05 | No OpenAPI schema | No auto-generated API documentation |

---

## Framework / Library Debt

| ID | Issue | Details |
|---|---|---|
| LIB-01 | In-memory RateLimiter | Not suitable for multi-worker deployment |
| LIB-02 | No async task queue wired | Celery configured in settings but no tasks defined |
| LIB-03 | SQLite for development | Missing PostgreSQL-specific features (array fields, full-text search) |
| LIB-04 | No migration health check | No `manage.py makemigrations --check` in CI |

---

## Security Debt

| ID | Issue | Details |
|---|---|---|
| SEC-01 | Patient cascade DELETE | Deleting a Patient cascades to 19+ models. Should use PROTECT. |
| SEC-02 | No input schema validation for Event payloads | Any JSON accepted |
| SEC-03 | No audit for read operations | Only writes are audited |
| SEC-04 | SECRET_KEY has dev default | `"dev-only-insecure-change-me"` — acceptable for dev, must be overridden in prod |

---

## Test Debt

| ID | Issue | Details |
|---|---|---|
| TST-01 | No shared test factories | Each test file creates its own fixtures |
| TST-02 | No performance/load tests | No benchmarks for N+1 queries |
| TST-03 | No URL routing tests | No test that all viewset URLs resolve |
| TST-04 | `detect_stage_transition()` untested | No direct unit test for care pathway transitions |
| TST-05 | FHIR endpoints untested | No test coverage for `/fhir/` |

---

## Technical Debt Summary

| Category | Count | Key Items |
|---|---|---|
| Naming inconsistencies | 7 | IN-01 through IN-07 |
| Duplicate implementations | 6 | DUP-01 through DUP-06 |
| Dead code | 5 | DEAD-01 through DEAD-05 |
| API inconsistencies | 5 | API-01 through API-05 |
| Library/tech debt | 4 | LIB-01 through LIB-04 |
| Security debt | 4 | SEC-01 through SEC-04 |
| Test debt | 5 | TST-01 through TST-05 |
| **Total** | **36** | |

---

## Debt Resolution Plan (for 2.5 scope)

### Immediate (must fix in 2.5)
1. DUP-01, DUP-02, DUP-03: Consolidate duplicated clinical checks
2. DEAD-01: Remove unused `_determine_care_stage()`
3. IN-05, DUP-06: Resolve duplicate care stage function
4. SEC-01: Change Patient cascade DELETE to PROTECT

### Before 3.0
1. All API-* items: Standardize URL structure and error format
2. LIB-01: Replace RateLimiter with Redis-backed
3. TST-01: Create shared test factories
4. IN-01 through IN-07: Standardize naming

### Deferred (post-3.0)
1. All DEAD-* event types: Wire when business requirements emerge
2. LIB-02: Wire Celery tasks when async processing needed
3. SEC-02: Add event schema validation
4. TST-02, TST-03, TST-04, TST-05: Add when corresponding features are enhanced
