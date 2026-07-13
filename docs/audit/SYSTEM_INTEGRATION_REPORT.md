# GDES System Integration Report

**Date:** 2026-07-10  
**Audit Scope:** All 30 installed apps (21 BGDDR-specific), 30+ models, 15 API viewset registrations, 34 domain events, 11 event handlers, 3 test files (348 tests passing)

---

## Architecture Maturity Score: **B+ (85/100)**

| Dimension | Score | Assessment |
|-----------|-------|------------|
| Module isolation | 90 | Clear app boundaries, minimal cross-app FK coupling beyond Patient |
| Event-driven integration | 85 | Full pub/sub dispatcher + signal bridge + 11 registered handlers |
| API consistency | 80 | REST framework with shared AuditedModelViewSet base; some URL prefix inconsistency |
| Data integrity | 85 | Foreign keys, unique constraints, select_for_update in reasoning pipeline |
| Test coverage | 80 | 348 tests covering integration paths; gaps exist in service unit tests |
| Documentation | 75 | Good docstrings; no formal ADR; TRACK.md maintained |
| Performance readiness | 70 | N+1 query risk in several service functions; no caching layer |
| Security | 85 | Token auth, DjangoModelPermissions, audit attribution, site-scoped RBAC |

---

## Integration Strength Summary

### Strengths
1. **Patient-centric data model**: `Patient` is the central entity; all clinical modules (encounters, labs, pathology, treatments, outcomes, clinical reasoning) FK to it. This makes cross-module joins natural and performant (`patients/models.py:46`).
2. **Event-driven architecture**: Full event dispatcher (`events/dispatcher.py`) with 34 domain event types (`events/event_types.py`), signal-to-event bridge (`events/signal_handlers.py`), and 11 registered handlers in `clinical_reasoning/event_handlers.py`. Events are persisted in `Event` model for audit/replay.
3. **Clinical Reasoning Pipeline** (`clinical_reasoning/services/engine.py:23`): `reason_about_patient()` integrates 9 service modules (knowledge rules, trajectory, care gaps, milestones, pathway engine, risk, evidence, insights) into a single atomic transaction.
4. **Layer separation**: Signal handlers → domain events → service-layer handlers → model updates. No circular dependencies between apps.
5. **Enterprise readiness**: `AuditedModelViewSet` (`api/base.py`), `AuditLog` model (`audit/models.py`), `RateLimiter` (`clinical_reasoning/services/enterprise_readiness.py:73`).

### Weaknesses
1. **URL prefix inconsistency**: Some apps mounted at `api/v1/` (knowledge, decision, clinical_reasoning), others at root-level prefixes (`prescriptions/`, `analytics/`, `safety/`, `studies/`). Clients need multiple base URLs.
2. **N+1 queries**: `operational_intelligence._count_missing_biopsy()` iterates all patients with `p.biopsies.exists()` per patient. `compute_care_gap_trends()` iterates all profiles without prefetching related data.
3. **In-memory rate limiter**: `RateLimiter` (`enterprise_readiness.py:73`) uses instance-level dictionary; resets on process restart and doesn't scale across workers.

### Critical Risks
1. **No async task queue for event handlers**: Event dispatch is synchronous in-process (`dispatcher.py:61`). A slow handler blocks the request. Celery is configured in settings but not wired to any event handler.
2. **No dead-letter/retry mechanism**: Failed handlers are logged but not retried. Event loss is possible on transient failures (dispatcher.py:69).
3. **Missing migration for `ClinicalProfile` `milestones` field**: Migration 0002 exists and is applied, but `_save_milestones()` uses `save(update_fields=["milestones"])` which can bypass `auto_now` on `last_updated`.

### Technical Debt
1. **Test consolidation**: 3 separate test files with overlapping fixtures. `conftest.py` exists but doesn't share common factories.
2. **Knowledge quality rules are static**: `score_rule_quality()` in `knowledge_quality.py` uses hardcoded thresholds; no calibration against clinical outcomes.
3. **Phase 4 test removal**: Test count dropped from 428 to 348; some Phase 4 integration tests were removed rather than migrated.

### Recommendations
1. Move event handler dispatch to Celery tasks using existing Redis broker config.
2. Add `select_related`/`prefetch_related` to all querysets in operational_intelligence and compute_care_gap_trends.
3. Consolidate URL structure: mount all app endpoints under `/api/v1/`.
4. Replace in-memory RateLimiter with database-backed or Redis-based implementation.
5. Add retry decorator to event dispatcher with dead-letter queue.
6. Create shared test factories in `conftest.py`.
