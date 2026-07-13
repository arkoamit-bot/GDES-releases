# Architecture Compliance Report

## Architecture Style: Modular Monolith with Event-Driven Integration

### Adherence to Django Best Practices

| Principle | Status | Evidence |
|---|---|---|
| App isolation | ✅ Pass | 21 BGDDR apps, clear domain boundaries, no cross-app model inheritance |
| Fat models, thin views | ✅ Pass | Models encapsulate business logic (Patient.save auto-generates IDs), views delegate to services |
| Signal decoupling | ✅ Pass | `signal_handlers.py` bridges Django signals to domain events; handlers in separate app |
| DRY serializers | ✅ Pass | `AuditedModelViewSet` provides base class for audit attribution |
| Migration management | ✅ Pass | All apps have proper initial migrations; clinical_reasoning has 2 migrations |
| Settings modularity | ✅ Pass | Dev/prod separation via `settings_prod.py` |
| Environment-based config | ✅ Pass | SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL from env |

### REST API Compliance

| REST Principle | Status | Notes |
|---|---|---|
| Resource-oriented URLs | ⚠️ Partial | Mixed prefix strategy: `/api/v1/` + app-specific prefixes |
| Proper HTTP methods | ✅ Pass | GET/ POST/ PATCH/ DELETE per DRF conventions |
| Stateless auth | ✅ Pass | Token authentication via `rest_framework.authtoken` |
| Pagination | ✅ Pass | DRF pagination configured globally |
| Content negotiation | ✅ Pass | JSON request/response |
| HATEOAS | ❌ Missing | No hypermedia links in responses |

### Event-Driven Architecture Compliance

| Pattern | Status | Notes |
|---|---|---|
| Event persistence | ✅ Pass | All events persisted to Event model |
| At-least-once delivery | ❌ Not implemented | No retry on handler failure |
| Handler isolation | ⚠️ Partial | Exceptions logged but not isolated per handler |
| Event replay | ❌ Not implemented | No replay/redispatch mechanism |
| Schema versioning | ❌ Not implemented | No event schema versioning |
| Dead letter queue | ❌ Not implemented | Failed events silently dropped |

### Security Architecture

| Control | Status | Details |
|---|---|---|
| Authentication | ✅ Pass | Token + Session auth; unauthenticated requests return 401 |
| Authorization (role-based) | ✅ Pass | 6 roles (data_manager, statistician, readonly, coordinator, investigator, pathologist) via Groups |
| Site-scoped RBAC | ✅ Pass | `site_filter_kwargs()` limits data per user's site |
| Audit trail | ✅ Pass | `AuditLog` captures all audited writes with actor attribution |
| Rate limiting | ⚠️ Partial | In-memory only; no DB/Redis backing |
| CSRF | ✅ Pass | CSRF middleware enabled |
| XSS | ✅ Pass | Django template auto-escaping |

### Database Architecture

| Aspect | Status | Notes |
|---|---|---|
| Normalization | ✅ Pass | 3NF with patient as central FK target |
| JSON fields for flexible data | ✅ Pass | ClinicalProfile uses 9 JSON fields |
| Index coverage | ⚠️ Partial | Some query patterns missing composite indexes |
| Migration integrity | ✅ Pass | All FKs reference existing models |
| Constraint enforcement | ✅ Pass | Unique together, db_index on query fields |

### Clinical Domain Architecture

| Domain Concept | Implementation | Compliance |
|---|---|---|
| Patient identity | patient_id (BGD-NNNNN) auto-generated | 🟢 Full |
| Multi-center | Site model + UserSiteRole + site_filter_kwargs | 🟢 Full |
| Disease staging | DiseasePhase choices + 8-stage PATHWAY_DEFINITION | 🟢 Full |
| Remission criteria | Disease-specific rules in analytics/services/outcomes.py | 🟢 Full |
| Evidence-based rules | KnowledgeBaseEntry with evidence_grade, guideline linkage | 🟢 Full |
| Clinical audit trail | AuditLog + enterprise_readiness.log_audit_event() | 🟢 Full |
| Patient consent | Consent model in audit app | 🟢 Full |
| FHIR interoperability | fhir/ endpoint | 🟢 Present, not audited |
