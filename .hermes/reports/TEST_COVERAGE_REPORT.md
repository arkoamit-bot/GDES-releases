# GDES Test Coverage Report

**Generated:** 2026-07-21  
**Repository:** C:\Users\User\Documents\GitHub\GDES

---

## 1. Test Infrastructure

| Component | Status |
|-----------|--------|
| pytest.ini | ✅ Configured (`django_find_project = true`, `testpaths = tests feedback/tests.py`) |
| conftest.py (root) | ✅ Sets Django settings and calls `django.setup()` |
| conftest.py (tests/) | ✅ Session-scoped DB fixture with `load_test_knowledge` |
| pytest-django | ✅ Implied by `django_find_project` |

### Configuration Issues
1. **`testpaths` is incomplete** — Only `tests/` and `feedback/tests.py` are listed, but many apps have their own `tests.py` files that won't be discovered automatically.
2. **No `--cov` configured** — No coverage plugin configured in pytest.ini
3. **No CI pipeline visible** — No GitHub Actions, GitLab CI, or similar test runner config detected

## 2. Test Files by App

| App | Test Files | Test LOC | Test Functions | Status |
|-----|-----------|----------|----------------|--------|
| **tests/** (central) | 19 files | 3,800+ | 311+ | ✅ Primary test suite |
| knowledge | 3 (tests.py, tests_api.py, tests_service_modules.py) | 2,474 | ~60 | ✅ Well tested |
| analytics | 2 | ~400 | ~15 | ⚠️ Moderate |
| labs | 2 | ~200 | ~8 | ⚠️ Moderate |
| studies | 1 (tests.py) | ~150 | 10 | ⚠️ Minimal |
| timeline | 1 (tests.py) | ~50 | 3 | 🔴 Thin |
| feedback | 1 (tests.py) | ~300 | ~12 | ⚠️ Moderate |
| **analytics** (tests.py) | 1 | 347 | — | ⚠️ In-app test |

### Apps with ZERO Test Files

| App | LOC | Risk Level |
|-----|-----|-----------|
| **clinical_reasoning** | 8,885 | 🔴 CRITICAL — no dedicated test file despite complex CDS logic |
| **clinic** | 2,276 | 🔴 HIGH — complex views/forms with no tests |
| **decision** | 1,150 | 🔴 HIGH — decision support with no tests |
| **users** | 573 | 🟡 MEDIUM — auth/user management untested |
| **treatments** | 1,730 | 🟡 MEDIUM — drug interactions/contraindications untested |
| **bgddr** | 1,846 | 🟡 MEDIUM — settings/backup/updater untested |
| **desktop** | 3,130 | 🟡 MEDIUM — launcher logic untested |
| **encounters** | 454 | 🟡 MEDIUM — clinical encounters untested |
| **events** | 370 | 🟡 MEDIUM — event dispatcher untested |
| **fhir** | 578 | 🟡 MEDIUM — FHIR interop untested |

**10 out of 29 apps have NO test files.** These apps represent ~18,000 LOC of untested production code.

## 3. Test Function Count

### Central Test Suite (`tests/`)

| File | Functions | Focus Area |
|------|-----------|------------|
| test_clinical_intelligence_ws4_9.py | 42 | Clinical intelligence WS4.9 |
| test_clinical_validation.py | 37 | Clinical validation |
| test_v6_gap_services.py | 36 | V6 gap services |
| test_cds_plans.py | 32 | CDS management plans |
| test_clinical_reasoning_services.py | 25 | Clinical reasoning |
| test_review_fixes.py | 23 | Review fixes |
| test_clinical_acceptance.py | 22 | Clinical acceptance |
| test_event_orchestration.py | 19 | Event system |
| test_knowledge_integration.py | 18 | Knowledge integration |
| test_cds_integration.py | 14 | CDS integration |
| test_desktop_hardening.py | 11 | Desktop security |
| test_kb_version.py | 8 | KB versioning |
| test_desktop_backup.py | 6 | Backup system |
| test_drug_intelligence.py | 5 | Drug intelligence |
| test_auto_screen.py | 4 | Auto-screening |
| test_recommendation_feedback.py | 3 | Feedback loop |
| test_github_update.py | 3 | GitHub updates |
| test_evidence_retrieval.py | 3 | Evidence retrieval |

**Total: ~311 test functions in `tests/`**

### In-App Tests
| File | LOC | Functions |
|------|-----|-----------|
| knowledge/tests.py | 1,235 | ~30 |
| knowledge/tests_api.py | 496 | ~15 |
| knowledge/tests_service_modules.py | 743 | ~15 |
| analytics/tests.py | 347 | ~12 |
| studies/tests.py | 150 | 10 |

## 4. Coverage Analysis

### Estimated Coverage by Domain

| Domain | Estimated Coverage | Notes |
|--------|-------------------|-------|
| Clinical reasoning/CDS | ~30% | Central tests cover services; no view/form tests |
| Knowledge management | ~70% | 3 test files with good service/API coverage |
| Patient management | ~20% | Only central tests touch patients |
| Drug interactions | ~40% | test_drug_intelligence + central tests |
| Desktop/backup | ~50% | test_desktop_hardening + test_desktop_backup |
| Event system | ~30% | test_event_orchestration only |
| Feedback/telemetry | ~25% | feedback/tests.py + central tests |
| FHIR integration | 0% | No tests |
| User management | 0% | No tests |
| Clinic UI views | 0% | No tests |
| Treatments/interactions | ~15% | Some central tests |
| Encounters | 0% | No tests |
| Scheduling | ~5% | No dedicated tests |
| Safety/adverse events | ~5% | No dedicated tests |
| **Overall** | **~20-25%** | Estimated based on test function distribution |

## 5. Test Quality Observations

### Strengths
- ✅ Well-structured test conftest with deterministic knowledge loading
- ✅ Good separation between unit, integration, and acceptance tests (documented in conftest)
- ✅ Central test suite covers critical CDS paths
- ✅ Clinical reasoning services have dedicated test coverage
- ✅ Knowledge API has dedicated test file

### Weaknesses
- 🔴 **pytest.ini testpaths incomplete** — many app-level tests won't be discovered
- 🔴 **No coverage measurement** — no `--cov` or `coverage.xml` generation
- 🔴 **No CI pipeline** — tests aren't run automatically
- ⚠️ **No fixture factory** — no `factory_boy` or `model_bakery` for test data
- ⚠️ **No mock strategy visible** — some tests may depend on seeded knowledge base
- ⚠️ **Monolithic test files** — knowledge has 1,235-line test file
- ⚠️ **10 apps with 0% test coverage** — significant risk for clinical software

## 6. Recommendations

| Priority | Action |
|----------|--------|
| 🔴 Critical | Fix `pytest.ini` testpaths to include ALL app-level test files |
| 🔴 Critical | Add tests for clinical_reasoning, clinic, decision, users, treatments |
| 🔴 Critical | Enable `pytest-cov` and generate coverage reports |
| 🔴 Critical | Set up CI pipeline (GitHub Actions) to run tests on every push |
| 🟡 High | Add `factory_boy` or `model_bakery` for test fixtures |
| 🟡 High | Split monolithic test files (knowledge/tests.py, etc.) |
| 🟡 High | Add view/form tests for clinic app |
| 🟡 Medium | Add integration tests for FHIR module |
| 🟢 Low | Add mutation testing (e.g., `mutmut`) for critical CDS logic |

---

*Report generated by automated analysis. Coverage estimates are based on test file distribution, not actual coverage instrumentation.*
