# Service Catalog

**Version:** 2.5  
**Pattern:** Application services coordinate. Domain services implement business logic. Infrastructure services handle technical concerns.

---

## Application Services (Orchestration Layer)

These services coordinate domain operations — they do not implement business rules.

| Service | Function | Location | Orchestrates | Transaction Boundary |
|---|---|---|---|---|
| `reason_about_patient()` | Full clinical reasoning pipeline | `engine.py:23` | 9 sub-services | ✅ `@transaction.atomic` + `select_for_update()` |
| `recompute_all_profiles()` | Batch reasoning for all patients | `engine.py:285` | `reason_about_patient()` per patient | ✅ Per-patient transaction |
| `compute_patient_outcome()` | Disease-specific outcome computation | `analytics/services/outcomes.py` | 6 sub-functions | ❌ No explicit transaction |
| `compute_all_outcomes()` | Batch outcome computation | `analytics/services/outcomes.py` | `compute_patient_outcome()` per patient | ❌ No explicit transaction |
| `evaluate_patient_rules()` | Rule-based patient evaluation | `knowledge/services.py` | `extract_patient_features()` + `evaluate_entry()` | ❌ Read-only |
| `build_full_explainability()` | Explainability report generation | `explainability.py:19` | 7 sub-functions | ❌ Read-only |

---

## Domain Services (Business Logic Layer)

These services implement domain-specific business rules.

### Clinical Reasoning Domain Services

| Service | Function | Location | Business Rules Applied |
|---|---|---|---|
| Trajectory Assessment | `assess_trajectory()` | `disease_trajectory.py` | R-C04 (eGFR thresholds), R-C05 (declining override) |
| Care Gap Detection | `detect_care_gaps()` | `care_pathway.py` | R-P04, R-F01, R-F02 |
| Milestone Detection | `detect_milestones()` | `disease_milestones.py` | R-M01 through R-M07 |
| Care Pathway Engine | `determine_current_stage()` | `care_pathway_engine.py` | R-P01, R-P02 |
| | `detect_stage_transition()` | `care_pathway_engine.py` | R-P03 |
| | `assess_pathway_deviation()` | `care_pathway_engine.py` | R-P04 |
| | `compute_pathway_summary()` | `care_pathway_engine.py` | — |
| Risk Assessment | `_assess_risk()` | `engine.py` | R-C04, R-C05 |
| Differential Builder | `_build_differential()` | `engine.py` | R-C01 |
| Information Gap Detector | `_identify_information_gaps()` | `engine.py` | R-C03 |
| Insight Generator | `_generate_insights()` | `engine.py` | R-C02 |
| Reasoning Chain Builder | `_build_reasoning_chain()` | `engine.py` | R-C06 |

### Knowledge Domain Services

| Service | Function | Location | Business Rules Applied |
|---|---|---|---|
| Feature Extraction | `extract_patient_features()` | `knowledge/services.py` | — (data transformation) |
| Rule Evaluation | `evaluate_entry()` | `knowledge/services.py` | R-K02 (11 operators) |
| | `evaluate_patient_rules()` | `knowledge/services.py` | R-K01 (only ACTIVE) |
| Rule Quality Scoring | `score_rule_quality()` | `knowledge_quality.py` | R-K03, R-K04 |
| Conflict Detection | `detect_rule_conflicts()` | `knowledge_quality.py` | R-K05 |
| Coverage Analysis | `analyze_coverage()` | `knowledge_quality.py` | — |

### Analytics Domain Services

| Service | Function | Location | Business Rules Applied |
|---|---|---|---|
| Lab Series Extraction | `_series()` | `analytics/services/outcomes.py` | — |
| Remission Detection | `_proteinuria_outcome()` | `analytics/services/outcomes.py` | R-O01 |
| Sustained eGFR Drop | `_sustained_drop()` | `analytics/services/outcomes.py` | R-O02 |
| Sustained Cr Rise | `_sustained_rise()` | `analytics/services/outcomes.py` | R-O03 |

### Research Domain Services

| Service | Function | Location | Business Rules Applied |
|---|---|---|---|
| Cohort Discovery | `discover_cohorts()` | `research_intelligence.py` | R-RS01 |
| Protocol Matching | `match_patient_to_protocols()` | `research_intelligence.py` | R-RS02 |
| Opportunity Detection | `detect_research_opportunities()` | `research_intelligence.py` | R-RS03 |

### Operational Domain Services

| Service | Function | Location | Business Rules Applied |
|---|---|---|---|
| Compliance Summary | `compute_compliance_summary()` | `operational_intelligence.py` | R-F01 |
| Patient Compliance | `compute_patient_compliance()` | `operational_intelligence.py` | R-E04 |
| Care Gap Trends | `compute_care_gap_trends()` | `operational_intelligence.py` | — |
| Data Quality Report | `get_data_quality_report()` | `enterprise_readiness.py` | — |

---

## Infrastructure Services

| Service | Function | Location | Type |
|---|---|---|---|
| Event Dispatcher | `dispatch()`, `subscribe()` | `events/dispatcher.py` | In-process pub/sub |
| Audit Logger | `log_audit_event()` | `enterprise_readiness.py` | DB-persisted audit trail |
| Audit Trail Reader | `get_audit_trail()` | `enterprise_readiness.py` | DB query |
| Rate Limiter | `RateLimiter.check()`, `RateLimiter.remaining()` | `enterprise_readiness.py` | In-memory (should be Redis) |
| JSON Safety | `json_safe()` | `json_util.py` | Serialization helper |
| Signal Bridge | `_model_post_save()`, `connect_all()` | `events/signal_handlers.py` | Django signal → domain event |

---

## Service Responsibility Assessment

| Service | Single Responsibility? | Transaction Boundaries? | Domain Logic in Service? | Assessment |
|---|---|---|---|---|
| `reason_about_patient()` | ✅ Orchestrates sub-services | ✅ Atomic | ✅ Delegates to domain services | ✅ Clean |
| `compute_patient_outcome()` | ✅ Outcome computation | ❌ Missing explicit transaction | ✅ | ⚠️ Add transaction |
| `evaluate_patient_rules()` | ✅ Rule evaluation | N/A (read-only) | ✅ | ✅ Clean |
| `extract_patient_features()` | ✅ Feature extraction | N/A (read-only) | ⚠️ Contains clinical mapping logic | 🟡 Move mappings to domain |
| `detect_care_gaps()` | ✅ Gap detection | N/A (read-only) | ✅ | ✅ Clean |
| `detect_milestones()` | ✅ Milestone detection | ✅ Partial save | ✅ | ✅ Clean |
| `compute_compliance_summary()` | ✅ Compliance metrics | N/A (read-only) | ✅ | ✅ Clean (perf issue only) |
| `log_audit_event()` | ✅ Audit logging | ✅ | ✅ | ✅ Clean |

---

## Service Duplication Audit

| Duplicate Functionality | Locations | Action |
|---|---|---|
| Missing biopsy detection | `engine.py:114`, `care_pathway_engine.py:164`, `operational_intelligence.py:40` | Consolidate into shared domain service |
| Missing eGFR detection | `engine.py:126`, `care_pathway_engine.py:176`, `operational_intelligence.py:49` | Consolidate into shared domain service |
| Overdue visit detection | `care_pathway.py`, `operational_intelligence.py:70` | Consolidate into shared domain service |
| ESKD detection (eGFR < 15) | `care_pathway_engine.py:116`, `disease_milestones.py:102` | ✅ Consistent, but consolidate to single source |
