# Performance Integration Report

## Critical Performance Paths

### Path 1: Patient Registration → Clinical Profile (Synchronous Chain)

```
POST /api/v1/patients/  (HTTP request)
  → Django save signal
  → dispatch("patient.registered")
  → _on_patient_event handler
  → reason_about_patient()
    → extract_patient_features()    [1 query: Patient + related]
    → evaluate_patient_rules()      [1 query: all ACTIVE KB entries]
    → assess_trajectory()           [feature-based, no DB]
    → detect_care_gaps()            [feature-based + encounter query]
    → detect_milestones()           [1-3 queries: biopsy, treatment]
    → determine_current_stage()     [feature-based, no DB]
    → assess_pathway_deviation()    [1 query: biopsy check]
    → ClinicalProfile.save()        [1 query: upsert]
    → ClinicalInsight.create()      [1-5 queries: care gap + diagnostic]
```

**Estimated latency per patient:** 50-200ms (empty DB), 200-500ms (loaded DB)  
**Risk:** Under high concurrency, `select_for_update()` on ClinicalProfile will queue requests

### Path 2: Batch Profile Recompute

```
POST /api/v1/profiles/reason_all/
  → recompute_all_profiles()
    → Patient.objects.iterator()          [streaming cursor]
    → for each patient: reason_about_patient()  [N iterations]
```

**Scale concern:** For 10K patients, this could take 30-60 minutes synchronously  
**Risk:** HTTP timeout before completion; no async task delegation

### Path 3: Operational Intelligence Compliance

```
GET /api/v1/operational/compliance/
  → compute_compliance_summary()
    → Patient.objects.count()                           [1 query]
    → _count_lost_to_follow_up()                        [1 query]
    → _count_missing_biopsy()                           [N queries — iterates all patients]
    → _count_missing_egfr()                             [1 query]
    → _count_active_without_tx()                        [N queries — iterates active patients]
    → _count_overdue_visits()                           [N queries — iterates all patients]
```

**Key bottleneck:** `_count_missing_biopsy()`, `_count_active_without_tx()`, `_count_overdue_visits()` each iterate all patients with per-row queries. For 10K patients, this is 30K+ individual queries.

### Path 4: Care Gap Trends

```
compute_care_gap_trends()
  → ClinicalProfile.objects.select_related("patient").all()
  → for each profile: access profile.care_pathway["care_gaps"]
```

**Risk:** Loads all profiles into memory. No pagination.

## N+1 Query Locations

| Location | File | Query Pattern |
|---|---|---|
| `_count_missing_biopsy()` | `operational_intelligence.py:40` | `p.biopsies.exists()` per patient |
| `_count_active_without_tx()` | `operational_intelligence.py:62` | `TreatmentExposure.objects.filter(patient=p)` per patient |
| `_count_overdue_visits()` | `operational_intelligence.py:75` | `p.encounters.order_by(...)` per patient |
| `_check_biopsy_milestone()` | `disease_milestones.py:74` | `patient.biopsies.order_by(...)` per profile |
| `_check_treatment_milestones()` | `disease_milestones.py:114` | `TreatmentExposure.objects.filter(patient=p)` per profile |

## Database Query Metrics

| Query Type | Estimated per Operation | Optimization |
|---|---|---|
| Patient list (paginated) | 1 query | Indexed |
| Clinical profile list (paginated) | 1 query (select_related) | Covered |
| Single patient reasoning | 4-8 queries | Acceptable for synchronous |
| Batch recompute (per patient) | 4-8 queries | Needs async |
| Compliance summary | 3N+3 queries | 🔴 CRITICAL — needs rewrite |
| Care gap trends | M queries (M profiles) | 🔴 CRITICAL — needs pagination |

## Recommendations

1. **Rewrite operational intelligence queries**: Replace per-iteration queries with annotated aggregates (`Patient.objects.annotate(biopsy_count=Count(...))`)
2. **Async event processing**: Move `reason_about_patient()` and `compute_patient_outcome()` to Celery tasks
3. **Batch recompute via Celery beat**: Schedule `recompute_all_profiles()` as a background task
4. **Add Redis caching** for compliance summary (TTL: 5 minutes)
5. **Rate limiter to Redis**: Replace in-memory RateLimiter with Redis-backed implementation using `django-redis` or `redis-py`
6. **Add database connection pooling** for PostgreSQL deployment (e.g., `django-db-connection-pool` or PgBouncer)
