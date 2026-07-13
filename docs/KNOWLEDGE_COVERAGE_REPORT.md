# Knowledge Coverage Report

Generated: 2026-07-10
Scope: Deterministic Test Knowledge Base (10 rules)

---

## Summary

| Metric | Value |
|--------|-------|
| Total Rules | 10 |
| ACTIVE Rules | 10 |
| Inactive Rules | 0 |
| Deprecated Rules | 0 |
| Untested Rules (non-TEST) | 0 |
| Unused Rules | 0 (all rules participate in evaluation) |
| Duplicate Rules | 0 |
| Rules without Evidence | 10 (test rules do not link evidence) |
| Rules without Guideline Linkage | 10 (test rules have no guideline chapter/quote) |
| Guideline Sources | 1 |

---

## Coverage by Disease

| Disease | Total | Active |
|---------|-------|--------|
| anca | 1 | 1 |
| antiGbm | 1 | 1 |
| c3 | 1 | 1 |
| diabeticNephropathy | 1 | 1 |
| fsgs | 1 | 1 |
| iga | 2 | 2 |
| lupus | 1 | 1 |
| mcd | 1 | 1 |
| membranous | 1 | 1 |

---

## Coverage by Evidence Grade

| Grade | Count |
|-------|-------|
| 1 (Strong) | 7 |
| 2 (Weak) | 3 |

---

## Coverage by Rule Type

| Type | Count |
|------|-------|
| diagnostic | 10 |

---

## Coverage by Guideline Source

| Source | Count |
|--------|-------|
| TEST (2026) | 10 |

---

## Exercised by Automated Tests

| Rule ID | Disease | Integration Test | Clinical Acceptance Test |
|---------|---------|-----------------|-------------------------|
| TEST-IGA-001 | iga | `TestIgAIntegration.test_igan_differential` | `TestIgANephropathyJourney` |
| TEST-IGA-002 | iga | `TestIgAIntegration.test_igan_differential` | `TestIgANephropathyJourney` |
| TEST-MN-001 | membranous | `TestMembranousIntegration.test_membranous_differential` | `TestMembranousJourney` |
| TEST-FSGS-001 | fsgs | `TestFSGSIntegration.test_fsgs_differential` | `TestFSGSJourney` |
| TEST-MCD-001 | mcd | `TestMCDIntegration.test_mcd_differential` | `TestMCDJourney` |
| TEST-LN-001 | lupus | `TestLupusIntegration.test_lupus_differential` | `TestLNJourney` |
| TEST-ANCA-001 | anca | `TestANCAIntegration.test_anca_differential` | `TestANCAJourney` |
| TEST-GBM-001 | antiGbm | `TestAntiGBMIntegration.test_anti_gbm_differential` | `TestAntiGBMJourney` |
| TEST-C3-001 | c3 | `TestC3GIntegration.test_c3g_differential` | `TestC3GJourney` |
| TEST-DKD-001 | diabeticNephropathy | `TestDKDIntegration.test_dkd_differential` | `TestDKDJourney` |

**Every ACTIVE rule is exercised by at least one automated test.** ✓

---

## Production Knowledge Base (when seeded)

When seeded via `python manage.py seed_knowledge_base`, the production KB adds ~200+ rules across 18+ disease profiles. Run this report against the production KB for full coverage analysis:

```
python manage.py seed_knowledge_base
python manage.py activate_entries --all
# then regenerate this report
```

---

## Gaps & Recommendations

| Gap | Impact | Recommendation |
|-----|--------|----------------|
| No non-diagnostic rule types | Treatment/monitoring/referral rules not tested | Add TEST rules for treatment, monitoring, referral types |
| No evidence entries on test rules | Evidence linkage untested | Add evidence_entries fixture to test KB |
| No guideline chapter/quote on test rules | Guideline provenance untested | Add guideline_chapter/guideline_quote to test rules |
| DRAFT rules not tested for validation | Status filtering not validated | Add DRAFT rule test (ensure they are excluded from evaluation) |
