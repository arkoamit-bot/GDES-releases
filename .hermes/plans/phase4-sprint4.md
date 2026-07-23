# Phase 4, Sprint 4: Validation & Testing

## Overview
End-to-end clinical validation, KDIGO guideline compliance checks, regression testing for AI Factory stability, and clinical scenario tests covering the full patient journey.

## Focus Areas

### 1. End-to-End Clinical Scenario Tests
Create `tests/test_clinical_scenarios.py` with full-pipeline tests:
- **Full IgA workup**: Register patient → initial labs → clinical profile → care gaps → treatment failure → management plan → outcome
- **Membranous nephropathy journey**: PLA2R testing → immunosuppression → remission monitoring → relapse detection
- **Diabetic nephropathy with DKD**: eGFR decline → proteinuria → RAAS blockade → progression monitoring
- **Lupus nephritis flare**: Active disease → induction therapy → monitoring → maintenance
- **Rapidly progressive GN**: ANCA-positive → emergent treatment → plasmapheresis → remission

Each scenario should verify:
- Correct care gaps detected at each stage
- Appropriate treatment failure patterns flagged
- Management plan matches disease stage
- Explainability output contains guideline references
- eGFR decline pattern fires at correct thresholds

### 2. KDIGO Guideline Compliance Validation
Create `tests/test_kdigo_compliance.py`:
- Verify management plan `first_line` recommendations match KDIGO 2021/2024 for each disease
- Check that guideline references in explainability are valid KDIGO citations
- Validate that treatment failure thresholds match KDIGO definitions (e.g., proteinuria > 1g/day for IgA)
- Ensure care gaps reference KDIGO recommendations

### 3. AI Factory Regression Test Suite
Create `tests/test_ai_factory_regression.py`:
- Verify all Quality Gates defined in `.hermes/workflows/QUALITY_GATES.md`
- Test that all agent entry points are importable
- Validate CI/CD workflow YAML files are syntactically valid
- Ensure no circular imports exist in the project

### 4. Clinical Prediction Validation
Add to `analytics/tests.py`:
- Verify `predict_kidney_survival()` produces monotonic probabilities (1y ≥ 3y ≥ 5y)
- Test all 9 disease baselines
- Verify risk factor attribution sums to ~100%
- Test edge cases: age 0, age 120, missing eGFR, extreme proteinuria

## Files to Create/Modify
| File | Action |
|------|--------|
| `tests/test_clinical_scenarios.py` | Create |
| `tests/test_kdigo_compliance.py` | Create |
| `tests/test_ai_factory_regression.py` | Create |
| `analytics/tests.py` | Add prediction validation tests |

## Acceptance Criteria
- [ ] 5+ end-to-end clinical scenarios covering major disease pathways
- [ ] KDIGO compliance checks for all 8+ management plan profiles
- [ ] AI Factory regression suite passes all quality gates
- [ ] Prediction validation: monotonic probabilities, all disease baselines, edge cases
- [ ] Full test suite passes: `python -m pytest --tb=short -q`
- [ ] Ruff lint passes

## Quality Gates
- `python -m pytest --tb=short -q`
- `python -m ruff check tests/ analytics/`
