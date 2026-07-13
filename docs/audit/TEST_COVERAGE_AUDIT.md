# Test Coverage Audit

## Test Inventory

| Test File | Test Count | Framework | Scope |
|---|---|---|---|
| `tests/test_event_orchestration.py` | 11 | pytest | Event dispatch, handler wiring, signal→event bridge |
| `tests/test_clinical_reasoning_services.py` | 26 | pytest | Milestone detection, explainability, knowledge quality, research intelligence, operational intelligence, enterprise readiness |
| `tests/test_clinical_intelligence_ws4_9.py` | 15 | pytest | Full pipeline integration (WS4-WS9), profile creation, batch recompute, edge cases |
| `api/tests.py` | 10 | Django TestCase | RBAC, auth, CRUD permissions, audit attribution |
| Other app tests | ~286 | Mixed | Core registry tests (Phase 1-4) |
| **Total** | **~348** | | |

## Phase 5 Test Coverage

### Event Orchestration (11 tests)

| Test | Coverage | Status |
|---|---|---|
| `test_event_dispatch_and_handlers` | dispatch → persist → handler call | ✅ |
| `test_event_subscription_wiring` | connect_handlers registration | ✅ |
| `test_event_persistence` | Event model creation | ✅ |
| `test_signal_to_event_bridge` | Django signal → domain event | ✅ |
| `test_multiple_events_processed` | Stacking events | ✅ |
| `test_lab_event_triggers_outcome_recompute` | Lab → outcome → profile | ✅ |
| `test_clinical_event_triggers_remission_outcome` | Clinical → outcome | ✅ |
| `test_event_handlers_patient_not_found` | Graceful error handling | ✅ |
| `test_reasoning_chain` | Full pipeline chain | ✅ |

### Clinical Reasoning Services (26 tests)

| Test | Coverage | Status |
|---|---|---|
| `test_detect_milestones_basic` | Basic milestone detection | ✅ |
| `test_milestone_merge_logic` | Dedup + merge existing + new | ✅ |
| `test_milestone_empty_patient` | Edge: no data | ✅ |
| `test_build_full_explainability` | Complete explainability report | ✅ |
| `test_explainability_empty_profile` | Edge: no profile | ✅ |
| `test_build_explainability_with_profile` | Profile → report | ✅ |
| `test_score_rule_quality` | Quality scoring | ✅ |
| `test_detect_rule_conflicts` | Conflict detection | ✅ |
| `test_analyze_coverage` | Coverage analysis | ✅ |
| `test_discover_cohorts` | Cohort discovery | ✅ |
| `test_match_patient_to_protocols` | Protocol matching | ✅ |
| `test_detect_research_opportunities` | Research opportunity detection | ✅ |
| `test_compute_compliance_summary` | Registry compliance | ✅ |
| `test_compute_patient_compliance` | Per-patient compliance | ✅ |
| `test_compute_care_gap_trends` | Gap trend analysis | ✅ |
| `test_log_audit_event` | Audit logging | ✅ |
| `test_get_audit_trail` | Audit trail retrieval | ✅ |
| `test_rate_limiter` | Rate limiter check/remaining | ✅ |
| `test_data_quality_report` | DQ report generation | ✅ |

### Clinical Intelligence Integration (15 tests)

| Test | Coverage | Status |
|---|---|---|
| `test_clinical_reasoning_pipeline` | Full reasoning pipeline | ✅ |
| `test_profile_creation` | ClinicalProfile creation | ✅ |
| `test_differential_computation` | Differential ranking | ✅ |
| `test_care_gap_detection` | Care gap identification | ✅ |
| `test_information_gap` | Info gap detection | ✅ |
| `test_milestone_detection` | Milestone detection | ✅ |
| `test_care_pathway_determination` | Pathway stage | ✅ |
| `test_pathway_deviation` | Deviation detection | ✅ |
| `test_risk_assessment` | Risk scoring | ✅ |
| `test_evidence_summary` | Evidence summary | ✅ |
| `test_insight_generation` | ClinicalInsight creation | ✅ |
| `test_batch_recompute` | Batch profile recompute | ✅ |
| `test_missing_knowledge_handling` | Empty KB edge case | ✅ |
| `test_empty_profile` | Empty patient profile | ✅ |
| `test_reasoning_chain` | Chain construction | ✅ |

## RBAC Test Coverage (10 tests)

| Test | Coverage | Status |
|---|---|---|
| `test_unauthenticated_is_rejected` | 401 for unauthenticated | ✅ |
| `test_token_obtain` | Token auth flow | ✅ |
| `test_any_authenticated_user_can_read` | Read access | ✅ |
| `test_readonly_cannot_write` | Write restriction | ✅ |
| `test_statistician_cannot_write` | Write restriction | ✅ |
| `test_data_manager_can_create_patient` | DM write permission | ✅ |
| `test_coordinator_can_create_patient` | Coordinator write | ✅ |
| `test_investigator_cannot_create_patient` | Investigator restriction | ✅ |
| `test_pathologist_separation` | Pathologist scope | ✅ |
| `test_api_write_is_attributed_in_audit_trail` | Audit attribution | ✅ |

## Coverage Gaps

| Area | Missing Tests | Risk |
|---|---|---|
| Care pathway engine stage transitions | No direct test of `detect_stage_transition()` | Medium |
| Enterprise readiness rate limiter concurrency | No concurrent access test | Low |
| Knowledge quality scoring edge cases | No test for rules with missing fields | Low |
| FHIR endpoints | No audit | Unknown |
| User management views | No audit | Low |
| URL routing coverage | No test that all 15 viewset URLs are valid | Low |
| Performance/load tests | None | Medium |

## Test Quality Assessment

| Metric | Value | Assessment |
|---|---|---|
| Total assertions (Phase 5) | 150+ | Adequate |
| Edge case coverage | 5 explicit edge cases | Good |
| Mock usage | Minimal (pytest mocks not used) | Acceptable but could improve isolation |
| Fixture sharing | Basic (conftest.py has shared helpers) | Could be expanded |
| CI integration | Not verified | Check README for test runner config |
