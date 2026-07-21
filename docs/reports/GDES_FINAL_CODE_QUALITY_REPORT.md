# GDES_FINAL_CODE_QUALITY_REPORT.md

**System:** GDES
**Reviewer:** Claude Code (independent)
**Date:** 2026-07-12

---

## 1. Test suite: green, but structurally blind to the defects

- **195 tests, all passing** in 15.7 s (`python -m pytest -q`) — the claim in
  the audit request is accurate.
- **However, the passing suite does not touch the code that is broken.** The
  drug-toxicity tests patch out **the exact three functions** that carry the
  Clinical Safety blockers:

  ```python
  # tests/test_v6_gap_services.py:180-182, 191-195, 207-211
  with patch("...drug_toxicity._get_current_medications", return_value=[...]), \
       patch("...drug_toxicity._get_recent_lab_values", return_value={...}), \
       patch("...drug_toxicity._assess_risk_factors", return_value=[]):
      report = detect_drug_toxicity(mock_patient)
  ```

  `mock_patient` is a `MagicMock` (test file lines 33-52), not an ORM object.
  So the tests validate the *pure rule math* but never execute the real
  querysets — which is why S-1/S-2/S-3 (wrong `status`, wrong `value_numeric`,
  missing `comorbidities`/`allergies` apps, inverted WBC/IgG direction) all pass
  CI while being non-functional in production.

**This is the most important code-quality finding:** the green suite creates
**false confidence** about the safety layer. The number "195 passing" should not
be cited as evidence of clinical readiness.

**Fix:** add integration tests using `@pytest.mark.django_db` with a real
`Patient`, `Encounter`, `PrescriptionItem`, and `LabResult`, asserting that a
patient on tacrolimus with a real creatinine result produces an alert, and that
a patient with a normal WBC on MMF produces **no** critical alert (would catch
S-2).

---

## 2. Recurring code smells

| Smell | Examples | Risk |
|-------|----------|------|
| Broad `except Exception: pass` / `= None` | `drug_toxicity.py:264,311-343`; `clinic/views.py:337-361`; `knowledge/services.py:164,195` | Hides schema/logic errors — direct cause of the shipped safety defects. |
| Schema names hard-coded in many places | `numeric_value` in 6 sites; prescription status strings | Drift goes undetected; centralize accessors. |
| Duplicated lab-reading logic | `drug_toxicity._get_recent_lab_values`, `treatment_failure._get_lab_values`, `engine`/`knowledge` feature extraction | Same bug copied to several files. |
| Dead code in running config | `decision` app installed but URL-disabled; `biobank` half-removed | Maintenance noise. |
| Four overlapping KB seed commands | `knowledge/management/commands/seed_*`, `load_test_knowledge` | Ambiguous source of truth. |
| Test fixtures mixed into ACTIVE prod data | `TEST-*` rules ACTIVE in DB | Pollutes the differential. |

---

## 3. Positives

- **Comment quality is high** — modules explain *why*, not just *what*
  (settings, prescriptions, backup, clinic views are exemplary).
- **Consistent Django idioms**, type hints, dataclasses for report objects.
- **Registry/Gen-1 code is clean and correct**, including the parts that read
  the same models the CDS layer gets wrong — proving the model is fine.
- **Migrations are present and ordered**; DB opens and queries cleanly.
- **Security hygiene** — secrets from env, prod settings force `DEBUG=False`,
  DRF permissions default to authenticated + model perms.

---

## 4. Maintainability assessment

The codebase is **maintainable** and the fixes required are **small and local**
(field renames, one wiring line, one direction flag, remove one app). No
large-scale refactor is needed. The main structural debt is the **duplicated,
un-integration-tested data-access code** in `clinical_reasoning/services/`;
consolidating it behind one tested accessor would prevent recurrence.

---

## 5. Priorities before code freeze

1. **Add integration tests** for the CDS data-access paths (highest value —
   would have caught every safety blocker).
2. Replace broad `except Exception` in CDS paths with narrow, logged handling.
3. Consolidate lab/med/feature reads into one module.
4. Remove `decision` from `INSTALLED_APPS`; retire `TEST-*` rules; pick one KB
   seed.
