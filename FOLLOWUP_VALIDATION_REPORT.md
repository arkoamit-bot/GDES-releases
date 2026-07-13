# Follow-up Engine Validation Report

## Test Results

**Date**: 2026-07-11
**Suite**: `followup.tests` — 27 tests
**Result**: ✅ ALL PASS

| Test Category | Test Name | Status |
|--------------|-----------|--------|
| Protocol Registry | `test_all_protocols_are_registered` | ✅ |
| Protocol Registry | `test_get_protocol_by_id` | ✅ |
| Protocol Registry | `test_get_unknown_protocol_returns_none` | ✅ |
| Protocol Registry | `test_protocol_for_patient_without_profile_returns_general` | ✅ |
| IgAN Protocol | `test_visit_interval_low_risk` | ✅ |
| IgAN Protocol | `test_visit_interval_high_risk_reduced` | ✅ |
| IgAN Protocol | `test_visit_schedule_has_month_1_and_month_12` | ✅ |
| IgAN Protocol | `test_required_labs_include_creatinine` | ✅ |
| IgAN Protocol | `test_drug_monitoring_includes_raasi` | ✅ |
| IgAN Protocol | `test_drug_monitoring_unknown_class` | ✅ |
| Risk Stratification | `test_low_risk_patient` | ✅ |
| Risk Stratification | `test_very_high_risk_with_nephrotic_proteinuria` | ✅ |
| Risk Stratification | `test_high_risk_with_declining_trajectory` | ✅ |
| Task Generation | `test_compute_plan_creates_visit_task` | ✅ |
| Task Generation | `test_compute_plan_creates_lab_tasks` | ✅ |
| Task Generation | `test_stale_tasks_cancelled_on_recompute` | ✅ |
| Escalation | `test_overdue_task_gets_new_status` | ✅ |
| Escalation | `test_escalation_level_increases_with_days` | ✅ |
| Escalation | `test_new_tasks_not_escalated` | ✅ |
| Dashboard | `test_daily_worklist_contains_expected_keys` | ✅ |
| Dashboard | `test_dashboard_returns_empty_lists` | ✅ |
| Engine Integration | `test_compute_all_plans_runs_without_error` | ✅ |
| Engine Integration | `test_followup_plan_creates_tasks` | ✅ |
| Engine Integration | `test_patient_without_outcome_still_gets_plan` | ✅ |
| Protocol Dataclass | `test_lab_requirement_defaults` | ✅ |
| Protocol Dataclass | `test_visit_timepoint_defaults` | ✅ |
| Protocol Dataclass | `test_base_protocol_defaults` | ✅ |

## Broader Regression Test: 153 tests

- `audit.tests` (10) ✅
- `knowledge.tests` (116) ✅
- `followup.tests` (27) ✅

**All 153 tests pass. No regressions.**

## Success Criteria Verification

| Criteria | Status | Evidence |
|----------|--------|----------|
| Every patient has an auto-generated follow-up plan | ✅ | `compute_followup_plan(patient)` runs on registration and every subsequent data change via events |
| Disease-specific protocols implemented | ✅ | 10 disease protocols + 1 general protocol in `followup/protocols/` |
| Laboratory monitoring is automatic | ✅ | `task_generator._create_lab_tasks` generates lab tasks based on protocol interval requirements |
| Drug monitoring is automatic | ✅ | `task_generator._create_drug_monitoring_tasks` generates monitoring tasks per drug class |
| Risk-based scheduling functions correctly | ✅ | `risk.assess_risk_category` returns risk level; protocol applies risk multiplier to interval |
| Escalation rules work | ✅ | `escalation.run_escalation` escalates overdue tasks through 4 levels |
| Clinician worklists are generated automatically | ✅ | `dashboard.get_daily_worklist` returns 9 categories of actionable items |
| Registry, timeline, research and audit remain synchronized | ✅ | Events dispatched at each plan update; signal handlers wire all downstream systems |
| No patient lost to follow-up without detection | ✅ | Escalation chain ensures detection at 7, 14, 30, and 60 days overdue |

## File Structure

```
followup/
├── __init__.py
├── admin.py                # Admin registration for FollowUpTask
├── apps.py                 # AppConfig, connects signals and event handlers
├── models.py               # FollowUpTask model (persistent)
├── event_handlers.py       # Subscribes to 17 event types
├── tests.py                # 27 comprehensive tests
├── migrations/
│   └── 0001_initial.py     # Initial migration
├── protocols/
│   ├── __init__.py         # Protocol registry
│   ├── base.py             # FollowUpProtocol base class
│   ├── general.py          # General/unclassified protocol
│   ├── igan.py             # IgA Nephropathy
│   ├── mcd.py              # Minimal Change Disease
│   ├── fsgs.py             # FSGS
│   ├── mn.py               # Membranous Nephropathy
│   ├── ln.py               # Lupus Nephritis
│   ├── anca.py             # ANCA Vasculitis
│   ├── anti_gbm.py         # Anti-GBM Disease
│   ├── c3g.py              # C3 Glomerulopathy
│   ├── mpgn.py             # MPGN / Immune Complex MPGN
│   └── ddd.py              # Dense Deposit Disease
└── services/
    ├── __init__.py
    ├── engine.py            # Core rules engine (Workstream 1)
    ├── risk.py              # Risk stratification (Workstream 5)
    ├── task_generator.py    # Task creation (Workstream 6)
    ├── escalation.py        # Escalation chain (Workstream 7)
    └── dashboard.py         # Clinician worklist (Workstream 8)
```

## Registry Integration

The follow-up engine integrates with all downstream systems:

1. **Event Bus**: Plan updates dispatch `FOLLOW_UP_PLAN_UPDATED` events; task escalations dispatch `FOLLOW_UP_TASK_OVERDUE` events
2. **Timeline**: Clinical reasoning engine updates ClinicalProfile after each recomputation
3. **Outcome Tracking**: Event handlers trigger outcome recomputation
4. **Research Dataset**: Events propagate to research sync handlers
5. **Audit Log**: Task status changes are captured by audit middleware
6. **Event Log**: Every plan update persists to `events.Event` table

## Future Considerations

The Notification Platform (Phase 3.2) will consume `FollowUpTask` rows to generate SMS/email/WhatsApp reminders without touching any business logic. The strict separation of concerns is maintained: **business logic in the Follow-up Engine, communication logic in the Notification Engine.**
