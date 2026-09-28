# Phase 4, Sprint 1: Treatment Failure Detection

## Overview
Implement the egfr_decline pattern evaluation in the clinical_reasoning treatment failure engine. Currently, both the rate-based and percent-based decline checks are `pass` stubs.

## Files to Modify

### 1. `clinical_reasoning/services/treatment_failure.py` (primary)

**Location:** `_evaluate_failure_pattern()` function, lines 500-507

**Current code (stub):**
```python
elif pattern.failure_type == "egfr_decline":
    # Check rate-based decline
    if "egfr_decline_rate" in criteria:
        # Simplified: compare current vs 12 months ago
        pass
    # Check percent-based decline
    if "egfr_decline_percent" in criteria:
        pass
```

**Requirements:**
- Rate-based decline: compare lab_values["egfr_decline_rate"] against pattern.criteria["egfr_decline_rate"]. If current rate exceeds threshold, generate a TreatmentFailureAlert.
- Percent-based decline: calculate percent decline from lab_values["baseline_egfr"] and lab_values["current_egfr"]. If decline exceeds criteria["egfr_decline_percent"], generate a TreatmentFailureAlert.
- Severity logic: `"critical"` if rate > 2x threshold or percent > 2x threshold, else `"warning"`.
- Priority: `"urgent"` if critical, `"high"` if warning.
- Include `current_values` dict with the measured values.

### 2. `clinical_reasoning/tests/test_services.py`

**Update test `test_egfr_decline_pattern`** (line 995):
- Change from asserting `alert is None` (stub) to asserting `alert is not None`
- Add a second test `test_egfr_decline_pattern_rate_based` that tests the rate-based path
- Add a third test `test_egfr_decline_pattern_percent_based` that tests the percent-based path
- Add a fourth test `test_egfr_decline_no_alert_when_below_threshold` that verifies no alert is generated when values are below threshold

### 3. `clinical_reasoning/services/treatment_failure.py` (FailurePattern dataclass)

Verify the `FailurePattern` dataclass has appropriate fields for egfr_decline patterns. Add fields if missing.

## Acceptance Criteria
- [ ] `_evaluate_failure_pattern()` returns `TreatmentFailureAlert` when egfr_decline_rate exceeds criteria threshold
- [ ] `_evaluate_failure_pattern()` returns `TreatmentFailureAlert` when percent decline exceeds criteria threshold
- [ ] Alert includes severity, priority, current_values, and clinical context
- [ ] No alert when values are below thresholds
- [ ] All existing tests still pass (`python -m pytest clinical_reasoning/tests/ -q`)
- [ ] Ruff lint passes (`python -m ruff check clinical_reasoning/`)

## Quality Gates
- Run `python -m pytest clinical_reasoning/tests/ --tb=short -q` before commit
- Run `python -m ruff check clinical_reasoning/services/treatment_failure.py`
- Ensure `git diff --stat` shows only the intended changes

## Branch
`phase4-sprint1-treatment-failure`
