# GDES Code Complexity Report

**Generated:** 2026-07-21  
**Repository:** C:\Users\User\Documents\GitHub\GDES

---

## 1. Lines of Code by App (Non-Migration Python)

| App | LOC | Functions/Classes | Verdict |
|-----|-----|-------------------|---------|
| knowledge | 12,392 | High (841 LOC models.py alone) | 🔴 Oversized |
| clinical_reasoning | 8,885 | High (management_plan.py: 2,196 LOC) | 🔴 Oversized |
| feedback | 3,400 | High (516 LOC models.py) | ⚠️ Large |
| desktop | 3,130 | High (launcher: 1,099 LOC) | ⚠️ Large |
| analytics | 3,016 | Medium | ⚠️ Large |
| followup | 2,359 | Medium | ⚠️ Moderate |
| clinic | 2,276 | Very High (58 defs in views.py) | 🔴 Oversized views |
| bgddr | 1,846 | Medium (settings: 455 LOC) | ⚠️ Settings sprawl |
| patients | 1,754 | Medium | ✅ Acceptable |
| treatments | 1,730 | Medium (434 LOC interactions.py) | ⚠️ Moderate |
| prescriptions | 1,301 | Low | ✅ Acceptable |
| decision | 1,150 | Low | ✅ Acceptable |
| labs | 1,016 | Low | ✅ Acceptable |
| studies | 992 | Low | ✅ Acceptable |
| pathology | 956 | Low | ✅ Acceptable |
| reminders | 778 | Low | ✅ Acceptable |
| audit | 660 | Low | ✅ Acceptable |
| fhir | 578 | Low | ✅ Acceptable |
| users | 573 | Low | ✅ Acceptable |
| api | 571 | Low | ✅ Acceptable |
| scheduling | 555 | Low | ✅ Acceptable |
| biomarkers | 489 | Low | ✅ Acceptable |
| encounters | 454 | Low | ✅ Acceptable |
| safety | 422 | Low | ✅ Acceptable |
| baseline | 385 | Low | ✅ Acceptable |
| events | 370 | Low | ✅ Acceptable |
| clinical | 282 | Low | ✅ Acceptable |
| timeline | 237 | Low | ✅ Acceptable |
| biobank | 171 | Low | ✅ Acceptable (disabled) |

**Total non-migration Python LOC: ~6,786** (from wc) — note: this counts only the top files; full project is ~47,000 LOC across all .py files.

## 2. Most Complex Files (Top 10 by LOC)

| File | LOC | Functions | Concern |
|------|-----|-----------|---------|
| `clinical_reasoning/services/management_plan.py` | **2,196** | 10 | 🔴 God file — should be split by disease profile |
| `clinic/views.py` | **1,507** | 58 | 🔴 Too many views in single file; split by resource |
| `knowledge/tests.py` | **1,235** | — | ⚠️ Monolithic test file; split by test layer |
| `knowledge/management/commands/seed_v4_knowledge.py` | **1,101** | — | ⚠️ Data seeding as code; should use fixtures |
| `desktop/launcher.py` | **1,099** | — | ⚠️ Monolithic launcher |
| `knowledge/management/commands/seed_knowledge_base.py` | **1,021** | — | ⚠️ More seeding code |
| `knowledge/views.py` | **989** | 102 | 🔴 Too many view functions; refactor to class-based views |
| `desktop/launcher-Dr-Wasim-2.py` | **901** | — | 🔴 Duplicate launcher (see dead code) |
| `knowledge/models.py` | **841** | — | ⚠️ Large model file; consider splitting by domain |
| `knowledge/tests_service_modules.py` | **743** | — | ⚠️ Additional test file, also large |

## 3. Complexity Hotspots

### `knowledge` app (12,392 LOC)
- **models.py** (841 LOC): 15+ models in one file
- **views.py** (989 LOC): 102 functions — average function is ~10 lines, but sheer count indicates god-file
- **admin.py** (449 LOC): Heavy admin configuration
- **services.py** (433 LOC): Business logic layer
- **graph_reasoning.py**: Graph-based reasoning (imported by clinical_reasoning)
- **3 test files** (1,235 + 743 + 496 = 2,474 LOC): Tests are well-covered but monolithic

### `clinical_reasoning` app (8,885 LOC)
- **management_plan.py** (2,196 LOC): Single file with 9 disease-specific treatment protocol generators
- **6 service modules** totaling ~2,500+ LOC:
  - `engine.py` (355 LOC): CDS engine
  - `disease_validation.py` (449 LOC)
  - `drug_toxicity.py` (444 LOC)
  - `treatment_failure.py` (570 LOC)
  - `disease_registry.py` (378 LOC)
  - `retrospective_validation.py` (376 LOC)
  - `followup_scheduler.py` (374 LOC)
  - `monitoring_plan.py` (332 LOC)
  - `investigation_engine.py` (328 LOC)

### `clinic` app (2,276 LOC)
- **views.py** (1,507 LOC, 58 functions): Almost entirely views — needs decomposition
- **forms.py** (671 LOC): Large form file importing from 7 other apps

## 4. Module Dependency Complexity

### `clinic/forms.py` — Most Connected File
Imports from **8 different apps** simultaneously:
- patients, baseline, encounters, safety, treatments, pathology, studies, audit

This creates a tight coupling that makes the clinic app fragile to changes in any of these apps.

### `clinical_reasoning/services/engine.py` — Core CDS Engine
Imports from:
- patients.models
- knowledge.models
- knowledge.services
- knowledge.graph_reasoning

### Cross-App Import Map (Top Connections)
```
clinical_reasoning → knowledge (5 files)
clinical_reasoning → patients (3 files)
feedback → knowledge (3 files)
feedback → bgddr (4 files)
clinic → patients, baseline, encounters, safety, treatments, pathology, studies, audit
decision → patients, api
```

## 5. Recommendations

| Priority | Action |
|----------|--------|
| 🔴 High | Split `management_plan.py` into per-disease modules |
| 🔴 High | Decompose `clinic/views.py` into view modules by resource |
| 🔴 High | Split `knowledge/views.py` — 102 functions is excessive |
| 🟡 Medium | Break `knowledge/models.py` into model modules (by domain) |
| 🟡 Medium | Extract `clinic/forms.py` shared logic into a domain service layer |
| 🟡 Medium | Consolidate 3 knowledge seed commands into parameterized fixture system |
| 🟢 Low | Consider using Django app labels more granularly for knowledge sub-domains |

---

*Report generated by automated analysis. Complexity metrics are based on LOC and function counts.*
