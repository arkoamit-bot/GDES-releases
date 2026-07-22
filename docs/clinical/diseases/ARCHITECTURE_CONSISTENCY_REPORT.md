# Architecture Consistency Report

**Version:** 2.5  
**Review:** Complete platform audit against Clean Architecture, DDD, SOLID, Repository Pattern, Event-Driven Architecture

---

## Clean Architecture Compliance

| Layer | Principle | Status | Evidence |
|---|---|---|---|
| **Domain Layer** | Independent of frameworks | ✅ Most business logic in service functions | ❌ Some rules in Django model fields (choices), some in services |
| | No infrastructure imports | ✅ No ORM imports in domain service functions | — |
| | Business rules expressible without Django | ⚠️ Partial — services use `Model.objects` directly | Need repository abstraction |
| **Application Layer** | Orchestrates domain services | ✅ `reason_about_patient()` is pure orchestration | `engine.py:23` |
| | Transaction boundaries | ✅ `@transaction.atomic` on `reason_about_patient()` | `engine.py:22` |
| | No business logic | ⚠️ Minor — `_assess_risk()` contains clinical thresholds | Should move to domain service |
| **Infrastructure Layer** | Implements interfaces | ⚠️ No formal interface contracts | Python duck typing |
| | Framework-specific code isolated | ✅ Django models/views/URLs in their own files | — |

### Violations
| Violation | File | Description | Fix |
|---|---|---|---|
| CA-01 | `engine.py:171-209` | `_assess_risk()` combines orchestration + clinical thresholds | Extract risk thresholds to domain value object |
| CA-02 | `analytics/services/outcomes.py` | Domain-agnostic functions (`_series`, `_sustained_drop`) mixed with domain-specific outcome logic | Split into infrastructure (data access) + domain (outcome rules) |
| CA-03 | `operational_intelligence.py` | All functions directly query ORM with no abstraction | Add repository layer for compliance queries |

---

## Domain-Driven Design Compliance

| Principle | Status | Assessment |
|---|---|---|
| **Ubiquitous Language** | ✅ Strong | Consistent terminology across most modules. Glossary produced. |
| **Aggregate Root** | ⚠️ Partial | ClinicalProfile root is clear. Patient root is used as FK from all modules, which is acceptable. |
| **Bounded Contexts** | ✅ Good | 16 contexts identified with clear boundaries. |
| **Value Objects** | ⚠️ Partial | Many VOs embedded as JSON blobs rather than typed classes. |
| **Domain Events** | ⚠️ Partial | 34 event types defined; 11 wired; 23 not yet active. |
| **Repository Pattern** | ❌ Not implemented | All data access via direct ORM. |
| **Anti-Corruption Layer** | ⚠️ Partial | `site_filter_kwargs()` acts as ACL for multi-tenancy. FHIR context missing ACL. |

### DDD Gaps
| Gap | Impact | Fix |
|---|---|---|
| Value objects stored as raw JSON in ClinicalProfile fields | No type safety, no encapsulation | Create typed Python dataclasses for Differential, RiskAssessment, etc. |
| Repository pattern absent | ORM leaks into domain layer | Introduce repository interfaces for each aggregate |
| Domain events underutilized | 23 of 34 events not active | Wire remaining events to handlers |
| Aggregate boundaries inconsistently enforced | Some aggregates modified via FK from other contexts | Enforce aggregate consistency rules |

---

## SOLID Compliance

| Principle | Status | Assessment |
|---|---|---|
| **S**ingle Responsibility | ✅ Good | Most services have clear single responsibility. `reason_about_patient()` is the exception — it orchestrates 9 services (acceptable for an application service). |
| **O**pen/Closed | ⚠️ Partial | Services are open for extension (new rules added to knowledge base) but closed for modification. `_assess_risk()` is closed. |
| **L**iskov Substitution | ✅ N/A | No inheritance hierarchies in domain. |
| **I**nterface Segregation | ⚠️ Partial | No formal interfaces. `AuditedModelViewSet` provides shared base. |
| **D**ependency Inversion | ❌ Not implemented | All services depend on concrete model classes, not abstractions. |

### SOLID Actions
- Add dependency injection for repository interfaces (Phase 3.0)
- Extract closed business rules (risk thresholds) into configurable policies
- Add abstract base classes for service interfaces

---

## Event-Driven Architecture Compliance

| Pattern | Status | Notes |
|---|---|---|
| **Event Publishing** | ✅ 34 event types defined | Signal → dispatch for 7 model types |
| **Event Handling** | ⚠️ 11 handlers active | Only 3 handler functions, 7 event types subscribed |
| **Event Persistence** | ✅ All events stored in Event model | Immutable event log |
| **At-Least-Once Delivery** | ❌ Not implemented | No retry on handler failure |
| **Handler Isolation** | ⚠️ Partial | Each handler wrapped in try/except, but same process |
| **Event Replay** | ❌ Not implemented | Events stored but no replay mechanism |
| **Schema Versioning** | ❌ Not implemented | Event payloads have no schema |
| **Dead Letter Queue** | ❌ Not implemented | Failed events silently dropped |

---

## Repository Pattern Compliance

| Criteria | Status | Notes |
|---|---|---|
| Repositories exist per aggregate | ❌ | All access via `Model.objects` |
| Hides persistence details | ❌ | Services use ORM queries directly |
| No business logic in repositories | ✅ N/A | No repositories exist |
| Returns domain objects | ✅ | ORM returns model instances |

---

## Specification Pattern Compliance

| Criteria | Status | Notes |
|---|---|---|
| Specifications for queries | ❌ | Not implemented |
| Reusable query predicates | ❌ | Not implemented |
| Combinable specifications | ❌ | Not implemented |

---

## Overall Consistency Score

| Dimension | Score |
|---|---|
| Clean Architecture | 70/100 |
| Domain-Driven Design | 75/100 |
| SOLID Principles | 65/100 |
| Event-Driven Architecture | 60/100 |
| Repository Pattern | 30/100 |
| Specification Pattern | 20/100 |
| **Overall** | **53/100** |

**Note:** Low scores on Repository and Specification patterns are acceptable for a Django monolith. These patterns add value at scale but introduce overhead. The Event-Driven and DDD scores represent the most actionable improvement areas.

---

## Compliance Summary

| Area | Score (0-100) | Critical Issues |
|---|---|---|
| Clean Architecture | 70 | CA-01, CA-02, CA-03 |
| DDD | 75 | VO typing, repository, events |
| SOLID | 65 | Dependency inversion, interface segregation |
| Event-Driven | 60 | No retry, no replay, 23 inactive events |
| Repository | 30 | Direct ORM everywhere |
| Specification | 20 | Not used |
| **Overall** | **53** | |

**Priority actions for 2.5:**
1. Wire remaining domain events (especially outcome and reasoning events)
2. Add retry mechanism to event dispatcher
3. Consolidate duplicated clinical rules (missing biopsy, missing eGFR)
4. Document repository interface (implementation deferred to 3.0)
