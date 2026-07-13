# GDES V3 Architecture Summary

## Components
```
┌──────────────────────────────────────────────┐
│                  nginx (SSL)                  │
├──────────────────────────────────────────────┤
│          Gunicorn WSGI (4 workers)            │
│         Django 5 / DRF / Jazzmin              │
├──────────────────────────────────────────────┤
│   Celery Worker         │   Celery Beat       │
│   (async event handling)│   (periodic tasks)  │
├──────────────────────────────────────────────┤
│   Redis 7 (broker + cache + rate limiting)    │
├──────────────────────────────────────────────┤
│         PostgreSQL 16 (primary database)      │
└──────────────────────────────────────────────┘
```

## Key Changes from V2.5
1. **Async events**: High-volume event types (lab results, encounters) now dispatch via Celery workers instead of in-process
2. **Repository-ready queries**: All N+1 patterns replaced with annotated aggregate queries
3. **Clinical deduplication**: `clinical_checks.py` is the single source of truth for biopsy/eGFR/overdue checks
4. **Patient safety**: `Patient.delete()` raises `PermissionDenied` — use `registration_status='inactive'`
5. **Production deployment**: Docker Compose with PostgreSQL, Redis, nginx, Celery, and health checks
6. **Standardized API**: StandardJSONRenderer wraps all responses in `{"status":"success","data":...}` or `{"status":"error","code":...,"message":...}`
7. **Redis-backed rate limiting**: `RateLimiter` tries Redis first, falls back to in-memory

## Data Flow
```
Event Source → dispatch() → persist Event → [async?] → Celery Task → Handler → DB
                                                        ↓ (no broker)
                                                     In-process handler
```

## Security
- SSL termination at nginx
- CSRF/Secure cookies in production
- RBAC via DjangoModelPermissions across all API viewsets
- Audit trail on all model mutations (AuditMiddleware)
- Rate limiting on API operations
- Patient deletion forbidden at ORM level
