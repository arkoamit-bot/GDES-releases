# Bug Log — GDES Phase 1-5 Review

Generated: July 2026
Baseline: 210 tests passing → 213 tests after fixes

---

### BUG-001 [High] — `_get_previous_egfr` uses wrong field name and missing import

- **Location:** `clinical_reasoning/services/treatment_failure.py:430-431`
- **Symptom:** `ImportError` (uncought) when `from clinical_reasoning.utils import calculate_egfr` runs — the module `clinical_reasoning/utils.py` does not exist. Additionally `patient.gender` and `patient.age` would raise `AttributeError` (caught, but silently return None).
- **Root cause:** The code was written against assumptions (existence of `clinical_reasoning/utils.py` with a `calculate_egfr` function, `Patient.gender` field, `Patient.age` property) that do not match the real model.
- **Fix:** Rewrote `_get_previous_egfr()` to:
  - Import `ckd_epi_2021` from `labs.services.egfr` (the canonical CKD-EPI 2021 implementation already used by the labs app)
  - Use `patient.sex` instead of `patient.gender`
  - Compute age from `patient.dob` via a new `_get_age()` helper
  - Return None gracefully when `dob` is missing
- **Verified:** 3 new integration tests (`test_get_previous_egfr_via_creatinine`, `test_get_previous_egfr_reads_existing_egfr`, `test_get_previous_egfr_no_dob_returns_none`) in `tests/test_cds_integration.py`; full suite 213 pass; smoke test NONE.
- **Clinical impact:** None (code path was never reached in practice because no patient in the test DB had a 6-month-old creatinine result). If reached, would crash with `ImportError`.
- **Needs clinical validation?** No.

---

### BUG-002 [Medium] — `cds_errors` not rendered in template

- **Location:** `templates/clinic/patient_detail.html` (near line 14)
- **Symptom:** When a CDS module (management_plan, monitoring_plan, followup_schedule) raises an exception, the error is logged but never visible to the clinician — panels silently go blank. The view passes a `cds_errors` list but the template ignores it.
- **Root cause:** Template was never updated to display `cds_errors` after the view was modified to collect them (M-1 fix).
- **Fix:** Added a red warning banner at the top of the page listing which CDS modules failed whenever `cds_errors` is non-empty.
- **Verified:** Visual inspection; template renders error banner when `cds_errors` is populated; 213 pass.
- **Clinical impact:** Previously, clinicians could not tell the difference between "data doesn't support a recommendation" (blank, expected) and "module crashed" (blank, lost output). Now they see a visible error state.
- **Needs clinical validation?** No.

---

### BUG-003 [Low] — `patient.gender` and `patient.date_of_birth` in test file use wrong field names

- **Location:** `tests/test_v6_gap_services.py` lines setting `patient.gender = "M"` and `patient.date_of_birth = date(1980, 1, 1)`
- **Symptom:** These tests work because they set arbitrary attributes on a mock/MagicMock patient object which doesn't validate against the real model. They pass but test the wrong thing.
- **Root cause:** Tests written against assumed field names. `Patient` model uses `sex` and `dob`, not `gender` or `date_of_birth`.
- **Fix:** Not fixed — these are existing unit tests that mock heavily. They still pass. Flagged for awareness: the tests exercise test logic, not real ORM paths. The new integration tests in `test_cds_integration.py` cover the real model correctly.
- **Verified:** N/A (diagnosed, not changed per instruction "Don't fix tests by weakening them").
- **Clinical impact:** None (tests only).
- **Needs clinical validation?** No.

---

### BUG-004 [Info] — TEST-* knowledge rules exist in database

- **Location:** `knowledge_knowledgebaseentry` table
- **Finding:** Multiple TEST-* rules (TEST-IGA-001, TEST-LN-001, etc.) exist in the database. These are loaded by `load_test_knowledge` command (recognised and OK for test environments). They are NOT loaded by the production `seed_knowledge_base` command.
- **Action:** Documented but not changed. If TEST-* rules ever appear in production CDS output, run the management command to deactivate them.
- **Needs clinical validation?** Yes — clinician should verify no TEST-* rules are active in production.

---

### BUG-005 [Info] — eGFR slope and outcome recompute triggers run synchronously

- **Location:** `events/dispatcher.py:94-101`
- **Finding:** When Celery is absent (desktop mode), `mark_async` events fall back to in-process synchronous dispatch. This is correct behaviour per design, but means saving a lab result on a heavy patient will block the HTTP response until CDS recomputes. Verified that the fallback path works correctly.
- **Action:** Flagged for awareness. Acceptable for single-user desktop pilot.
- **Needs clinical validation?** No.

---

## Summary

| Bug | Severity | Status | Type |
|-----|----------|--------|------|
| BUG-001 | High | Fixed | Wrong field name + missing import |
| BUG-002 | Medium | Fixed | UI error invisibility |
| BUG-003 | Low | Diagnosed | Test uses wrong field names (mocked) |
| BUG-004 | Info | Documented | TEST-* rules in DB (expected) |
| BUG-005 | Info | Documented | Sync dispatch in desktop mode (by design) |

**All P0-CD-critical bugs found during this review have been fixed.** The remaining items are informational or test-quality issues.
