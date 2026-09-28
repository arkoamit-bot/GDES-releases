# OpenCode Instructions — Thorough Bug Review & Fix for GDES (BGDDR)

**Paste this whole file to opencode as the task.** It is a bug-finding-and-fixing
playbook tailored to *this* codebase. Follow it in order. Work incrementally:
find → fix → verify → log, one bug at a time. Do **not** do a giant rewrite.

---

## 0. What this project is (context you need)

- **App:** Glomerular Disease Expert System (GDES), a Django project under
  `bgddr/`. It is a clinical registry + AI clinical-decision-support (CDS) +
  follow-up + research platform for kidney (glomerular) disease.
- **Stack:** Django, Django REST Framework, SQLite (single-PC desktop pilot;
  PostgreSQL-ready). Jazzmin admin theme. HTMX + Tailwind + Chart.js front end.
  Tests use `pytest` / `pytest-django`.
- **Runtime model:** single-user Windows desktop. `manage.py runserver`.
  Celery is optional and usually absent — an event bus degrades to in-process.
- **Where the important/logic-heavy code lives:**
  - `knowledge/` — knowledge base, rule engine (`knowledge/services.py`), admin.
  - `clinical_reasoning/services/` — the CDS engine, drug toxicity, treatment
    failure, management/monitoring/follow-up plans, milestones. **Most bugs
    historically live here.**
  - `events/` — domain-event bus + Django signal bridge (auto-triggers CDS).
  - `clinic/` — the clinician UI views/templates (`clinic/views.py`,
    `templates/clinic/`). The registry UI is generally correct.
  - `analytics/`, `studies/`, `followup/`, `scheduling/`, `prescriptions/`,
    `labs/`, `pathology/`, `treatments/`, `patients/`, `encounters/`.

### Golden rule (why the test suite lies)
The suite is **green (210 passing) but does not catch the real bugs**, because
the unit tests **mock the exact ORM functions that are broken** (they build
`MagicMock` patients and `patch(...)` the data-access functions). **A green
`pytest` run is NOT evidence of correctness here.** You must exercise the real
code against the real database (see Phase 2). This is the single most important
instruction in this document.

---

## 1. Ground rules (this is a clinical system — read before changing anything)

1. **Never auto-activate clinical rules.** Imported/edited knowledge rules must
   stay `DRAFT` for human review. Do not change lifecycle so rules go live
   without approval.
2. **Never send patient data (PHI) to external services or into URLs.**
3. **Do not silently change diagnostic/therapeutic logic.** If a "bug" is really
   a *clinical* judgement (e.g. how a differential is scored, a drug threshold,
   a monitoring interval), **FLAG it in the bug log with a recommendation** and,
   if you change it, mark it "NEEDS CLINICAL VALIDATION". Do not quietly alter
   what the system recommends to clinicians.
4. **Do not "fix" tests by weakening them.** Never make a failing test pass by
   mocking the thing under test, loosening an assertion, or deleting the test.
5. **Do not swallow exceptions.** Replacing a real error with
   `except Exception: pass` (or `= None`) is how these bugs got shipped. Fix the
   cause; if you must catch, `logger.exception(...)` and surface a visible state.
6. **Preserve existing data.** Prefer `get_or_create` / `update_or_create` and
   guards over destructive rewrites. Never overwrite a clinician's decision
   (e.g. an `enrolled`/`completed` record) during an automated pass.
7. **Small, reversible commits.** One bug per fix. Re-run verification each time.

---

## 2. Environment & baseline

```bash
cd bgddr
python -m pytest -q                       # baseline: expect ~210 passing
python manage.py check                    # system checks
python manage.py makemigrations --check --dry-run   # detect model/migration drift
```

Record the baseline pass count. After every fix, the suite must still pass **and
you must add a regression test** (see Phase 7). If a number changes, know why.

There is a real database at `bgddr/db.sqlite3` with ~8 test patients — use it for
the read-only smoke tests in Phase 2 (those scripts roll back or clean up; never
leave test rows behind).

---

## 3. Phase 1 — Static sweep (grep for the known bug patterns)

This codebase has repeating failure patterns. Search for each and inspect every
hit. Fix the ones that are wrong; log them.

### 3a. Schema drift (wrong field/model names that only fail at runtime)
The CDS services were written against a data model that differs from the real
one. Cross-check every ORM attribute against the actual model. Known genuine
field names (verify before trusting):
- `labs.LabResult` → `value_numeric` (NOT `numeric_value`), `result_date`,
  `sample_date`, `test` (FK to `LabTest`, whose `.code` is the slug).
- `prescriptions.Prescription` status choices are `draft` / `final` only. The
  drug/dose/frequency live on `prescriptions.PrescriptionItem`, not
  `Prescription`. Current meds are best read from
  `treatments.TreatmentExposure` (has `patient`, `drug`, `ongoing`).
- `patients.Patient` → `sex` (not `gender`), `dob` (not `date_of_birth`),
  `latest_egfr`, `primary_diagnosis`, `diabetes_status`, `cohort`,
  `enrollment_date`, `registration_date`.
- `followup.models` class is `FollowUpTask` (capital U). Importing `FollowupTask`
  silently fails.

Commands:
```bash
grep -rn "\.numeric_value" --include=*.py .            # should be value_numeric
grep -rn "FollowupTask" --include=*.py .               # wrong; it's FollowUpTask
grep -rn "date_of_birth\|\.gender" --include=*.py .     # verify vs Patient model
grep -rn "status__in=(\"active\"\|status=.active." --include=*.py prescriptions clinical_reasoning
```
For each hit: open the referenced model, confirm the real field, fix, log.

### 3b. Imports of apps/models that don't exist
```bash
grep -rn "from comorbidities\|from allergies\|import comorbidities" --include=*.py .
```
These apps do not exist; such imports sit inside `try/except: pass` and silently
disable features. Either wire to a real source or remove the dead branch.

### 3c. Silenced failures (the pattern that hid every bug)
```bash
grep -rn "except Exception:" --include=*.py clinical_reasoning clinic knowledge | grep -i "pass\|= None"
```
For each: is a real error being hidden? Replace with narrow handling +
`logger.exception(...)`, and make the UI show an explicit "unavailable" state
rather than a silently blank panel.

### 3d. Side effects on GET (writes during page render)
Views should not create/modify rows on a GET. Look in `clinic/views.py` and any
service it calls for `.objects.create(` / `.save(` triggered by rendering a page.
If found, make it idempotent (`get_or_create`/`update_or_create`) or move the
write to an event handler. (A fixed example already exists:
`clinical_reasoning/services/followup_scheduler.py` now uses `get_or_create`.)

### 3e. Unique-constraint crashes
For every `.objects.create(...)`, check the model's `Meta.constraints` /
`unique=True` / `unique_together`. If the same logical row can be created twice
(e.g. on repeated runs/events), switch to `get_or_create`/`update_or_create`.
```bash
grep -rn "UniqueConstraint\|unique_together\|unique=True" --include=*.py .
```

### 3f. Dead code / duplicate mechanisms
- The `decision` app is deprecated (URLs disabled) but still in
  `INSTALLED_APPS` — confirm nothing imports it, then remove it.
- Two follow-up mechanisms coexist (`followup/` engine and
  `clinical_reasoning/services/followup_scheduler.py`). Don't delete either
  blindly — log it and ask before consolidating (behavioural change).
- `TEST-*` knowledge rules may be ACTIVE in the DB and pollute results — log,
  don't auto-delete.

---

## 4. Phase 2 — Dynamic smoke tests (THE high-value step)

Static grep misses most of these bugs. **Run every service, view, and endpoint
against the real database and catch exceptions.** Use this harness pattern (it is
how the worst bugs in this codebase were actually found). It rolls back, so it
leaves no data behind:

```python
# scratch_smoke.py  — run with:  python manage.py shell < scratch_smoke.py
import logging; logging.disable(logging.WARNING)
from patients.models import Patient
from clinical_reasoning.services.engine import reason_about_patient
from clinical_reasoning.services.drug_toxicity import detect_drug_toxicity
from clinical_reasoning.services.treatment_failure import detect_treatment_failure, detect_relapse
from clinical_reasoning.services.disease_validation import validate_disease_management
from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
from clinical_reasoning.services.followup_scheduler import generate_follow_up_schedule
from clinical_reasoning.services.investigation_engine import generate_investigation_recommendations
from clinical_reasoning.services.management_plan import generate_management_plan

fails = {}
def run(name, fn):
    try: fn()
    except Exception as e:
        fails.setdefault(name, []).append(f"{p.patient_id}: {type(e).__name__}: {e}")

for p in Patient.objects.all():
    prof = reason_about_patient(p)
    did = (prof.differential[0] or {}).get("disease_id","") if prof.differential else ""
    run("drug_toxicity",   lambda: detect_drug_toxicity(p))
    run("treatment_failure", lambda: detect_treatment_failure(p, prof))
    run("relapse",         lambda: detect_relapse(p, prof))
    run("disease_validation", lambda: did and validate_disease_management(p, did))
    run("monitoring_plan", lambda: did and generate_monitoring_plan(p, did))
    run("followup",        lambda: did and generate_follow_up_schedule(p, risk_category="moderate", disease_phase=p.current_phase or "active", treatment_phase="maintenance", disease_id=did, num_visits=6))
    run("investigations",  lambda: generate_investigation_recommendations(p, prof.differential))
    run("management_plan", lambda: did and generate_management_plan(p, did))

print("FAILURES:", fails or "NONE")
```
Every entry in `fails` is a real bug (wrong field, unique clash, None handling,
etc.). Fix each, then re-run until it prints `NONE`. **Watch the server log
too** — a caught exception that only appears as an `ERROR` line (page still 200)
is still a bug (e.g. a blank panel). `grep`-check for it.

### Also smoke-test the HTTP layer
Load every page and hit every DRF endpoint as a logged-in superuser; a `200` that
logs an error, or renders an empty panel where data exists, is a bug.
```python
from django.test import Client
from django.contrib.auth import get_user_model
c = Client(); c.force_login(get_user_model().objects.filter(is_superuser=True).first())
H = {"HTTP_HOST": "localhost"}   # ALLOWED_HOSTS excludes 'testserver'
for url in ["/", "/dashboard/enrollment/", "/dashboard/outcomes/", "/dashboard/compliance/",
            "/patients/", "/prescriptions/", "/analytics/", "/studies/", "/safety/"]:
    r = c.get(url, **H); print(r.status_code, url)
# then each patient page — LOAD IT TWICE (some bugs only appear on the 2nd load):
from patients.models import Patient
for p in Patient.objects.all():
    for _ in range(2):
        r = c.get(f"/patients/{p.pk}/", **H); print(r.status_code, p.patient_id)
```
Watch server logs for `IntegrityError`, `AttributeError`, `RelatedObjectDoesNotExist`.

---

## 5. Phase 3 — Event bus & integration

The app auto-recomputes CDS/outcomes when data is saved, via
`events/signal_handlers.py` → `events/dispatcher.py` → each app's
`event_handlers.py` (registered in `apps.py: ready()`). Verify the whole chain
works **by saving a real model and checking the side effect happens** (not by
calling the handler directly):
```python
# e.g. change a patient so it becomes study-eligible, save, and check a screening
# record appears — proving signal → event → handler fires end to end.
```
Check: async events (`mark_async`) must degrade to in-process when
`CELERY_BROKER_URL` is empty (desktop). Confirm `dispatcher.dispatch` runs
handlers synchronously in that case.

---

## 6. Phase 4 — Templates / UI correctness

Blank panels that should show data are a recurring bug (a view rendered a
template with **no context**, so `{% if data %}` fell through to an empty state).
For each dashboard/partial and patient-tab:
- Confirm the view actually computes and passes the context the template reads.
- Confirm charts get non-empty `data-labels`/`data-values`.
- Confirm the value the template keys on actually exists (e.g. a `disease_id`
  read from the wrong dict is always empty → panel never renders).

---

## 7. Phase 5 — Data & DB integrity

```bash
python manage.py makemigrations --check --dry-run   # models vs migrations in sync?
```
- Look for models edited without a migration.
- Spot-check the live DB for governance/data problems (these are *reported*, not
  auto-changed): e.g. knowledge rules with no reviewer/validation date,
  `confidence_score` all 0.0, `TEST-*` rules ACTIVE. Log for a human.

---

## 8. How to FIX (rules for every change)

1. Find the **root cause**, not the symptom. (Wrong field name → fix the name,
   don't wrap in try/except.)
2. Prefer the smallest correct change that matches surrounding code style.
3. Idempotency: repeated runs/events must not crash or duplicate — use
   `get_or_create` / `update_or_create`, keyed on the real unique fields.
4. Centralize when a bug is copy-pasted (e.g. the same lab-reading code in 3
   files) — but only if low-risk; otherwise fix each and note the duplication.
5. If a fix changes clinical output (diagnosis ranking, drug thresholds,
   intervals), STOP: mark it **NEEDS CLINICAL VALIDATION** and show a before/after
   for a few real patients; do not silently ship it.

---

## 9. How to VERIFY every fix (do all three)

1. **Unit + integration tests:** `python -m pytest -q` stays green, AND add a new
   `@pytest.mark.django_db` **integration** test that builds real model rows
   (Patient, LabResult, TreatmentExposure, …) and would have caught this bug.
   Do **not** mock the function you fixed. (See `tests/test_cds_integration.py`
   and `tests/test_auto_screen.py` for the pattern.)
2. **Re-run the Phase 2 smoke harness** → must print `FAILURES: NONE`.
3. **Reload the affected page twice** as a superuser → 200, no error in logs,
   data visible.

---

## 10. Deliverable — keep a bug log

Create/append `BUGLOG.md`. One entry per bug:

```
### BUG-007  [High]  Follow-up schedule crashes on 2nd patient-page load
- Location: clinical_reasoning/services/followup_scheduler.py:139
- Symptom: IntegrityError (unique patient+label); follow-up panel blank on reload.
- Root cause: unconditional ScheduledVisit.objects.create() on GET render.
- Fix: get_or_create keyed on (patient, label); idempotent tasks; persisted dates.
- Verified: generator run 3× stable; patient page loads 2× clean; +1 regression test.
- Clinical impact: none (scheduling only). Needs clinical validation? No.
```
Severity scale: **Critical** (data loss / patient-safety / crash on core path),
**High** (feature broken or wrong output), **Medium** (degraded / silent),
**Low** (cleanup). Rank the final list most-severe first.

---

## 11. What NOT to do (recap)
- ❌ Don't trust the green test suite as proof of correctness.
- ❌ Don't mock the code under test to make a test pass.
- ❌ Don't swallow exceptions or leave blank panels — log + surface.
- ❌ Don't auto-activate knowledge rules or send PHI anywhere.
- ❌ Don't silently change what the system recommends clinically — flag it.
- ❌ Don't do a big-bang refactor; small verified fixes, each with a test.

## 12. Suggested order of work
1. Phase 0 baseline → 2. Phase 1 static sweep → 3. Phase 2 smoke (fix until
   `NONE`) → 4. Phase 3 event bus → 5. Phase 4 UI panels → 6. Phase 5 data →
   7. write `BUGLOG.md`, ranked, with the clinical-validation items flagged
   separately for a human.

Begin with Phase 0 and report the baseline before making any change.
