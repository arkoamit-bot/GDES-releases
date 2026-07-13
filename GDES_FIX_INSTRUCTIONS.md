# GDES_FIX_INSTRUCTIONS.md

**System:** GDES (Glomerular Disease Expert System)
**Purpose:** Step-by-step remediation guide for the issues found in the final audit
**Date:** 2026-07-12
**Scope:** Corrective only — no new features, no redesign. Every change below is a
wiring / field-name / logic correction that makes an *existing* feature work.

---

## How to use this document

Work top to bottom. The order is deliberate:

1. **P0 (B-1 … B-5)** — must be done, and re-validated, before any pilot that
   turns the CDS layer on. If you cannot finish them in time, jump to
   [Appendix A — the "disable CDS" escape hatch](#appendix-a--registry-only-fallback-path-b)
   and pilot registry-only.
2. **P1 (M-1 … G-3)** — do before you *rely on* the CDS output or show any
   "confidence" number.
3. **P2 (C-1 … C-6)** — cleanup; safe to batch afterward.

Each fix has: **the problem**, **the file/line**, **exactly what to change**
(with before/after code), and **how to prove it's fixed**. Line numbers are from
the audited revision — if code has since moved, search for the quoted snippet.

Before you start:

```bash
# from the repo root (…/bgddr)
git checkout -b fix/cds-blockers
python manage.py test        # baseline: should be 195 passing
```

Ground truth reference — the real field names the CDS layer got wrong:

| Concept | WRONG name used by CDS | CORRECT name | Defined in |
|---|---|---|---|
| Lab numeric value | `numeric_value` | `value_numeric` | `labs/models.py:131` |
| Lab date | (mixed) | `sample_date` / `result_date` — confirm per model | `labs/models.py` |
| Prescription status | `active` / `ongoing` | `draft` / `final` | `prescriptions/models.py:19-21` |
| Drug / dose / frequency | on `Prescription` | on `PrescriptionItem` | `prescriptions/models.py:107-117` |
| Prescription → patient | `Prescription.patient` | `Prescription.encounter.patient` | `prescriptions/models.py:23` |
| Disease id on profile | `disease_trajectory["disease_id"]` | `differential[0]["disease_id"]` | live DB + `disease_trajectory.py` |

> **Best-source note:** for "current medications" the cleanest source is not
> `PrescriptionItem` at all — it's `TreatmentExposure` (see
> `treatments/models.py:160`), which the reconciliation engine already maintains
> with a direct `patient` FK, `ongoing` flag, and denormalized `drug_name` /
> `dose` / `frequency`. B-1 below uses it. This is still corrective — you are
> pointing an existing query at the model that already holds the answer.

---

# P0 — Blockers

## B-1 — Make drug-toxicity read real medications

**Problem.** `_get_current_medications()` filters `Prescription` by statuses that
don't exist (`active`/`ongoing`), reads `drug`/`dose`/`frequency` off
`Prescription` (they live on `PrescriptionItem`), and filters by
`patient=` (Prescription has no `patient` — it reaches the patient through
`encounter`). Every failure is swallowed by `except Exception: return []`, so the
function silently returns `[]` for every patient and **no toxicity alert can ever
fire.**

**File.** `clinical_reasoning/services/drug_toxicity.py:245-265`

**Change — replace the whole function** with a read from the reconciled exposure
table (the model that actually holds the patient's standing regimen):

```python
def _get_current_medications(patient) -> list[dict]:
    """Current (ongoing) medications for the patient.

    Source of truth is TreatmentExposure, which the reconciliation engine
    keeps up to date from finalized prescriptions. It has a direct patient FK,
    an `ongoing` flag, and denormalized drug/dose/frequency.
    """
    from treatments.models import TreatmentExposure

    meds = []
    exposures = (
        TreatmentExposure.objects
        .filter(patient=patient, ongoing=True)
        .select_related("drug")
    )
    for e in exposures:
        meds.append({
            "name": e.drug_name or getattr(e.drug, "generic_name", ""),
            "drug_class": getattr(e.drug, "drug_class", ""),
            "dose": e.dose,
            "frequency": e.frequency,
        })
    return meds
```

> Note: `drug_class` on `DrugMaster` is a coded choice (`treatments/models.py:63`).
> `_medication_matches_rule()` already matches on the drug **name** keywords
> (tacrolimus, mycophenolate, …), so name-based matching keeps working; the class
> string is informational.

**Do NOT keep the bare `except Exception: return []`.** If the query genuinely
errors, that must surface (see M-1), not masquerade as "no medications."

**Alternative if you must use prescriptions directly** (e.g. `TreatmentExposure`
isn't populated in your pilot data): read finalized items instead —

```python
from prescriptions.models import PrescriptionItem
items = (
    PrescriptionItem.objects
    .filter(prescription__encounter__patient=patient,
            prescription__status="final")
    .select_related("drug", "prescription")
    .order_by("-prescription__printed_at")
)
```

— but the reconciliation route above is preferred because it already dedupes to
the *current* regimen; iterating every finalized item re-lists stopped drugs.

**Prove it.** See B-5 integration test `test_toxicity_reads_ongoing_meds`.

---

## B-2 — Fix the lab field name everywhere (`numeric_value` → `value_numeric`)

**Problem.** The real field is `LabResult.value_numeric` (`labs/models.py:131`).
The CDS services read `r.numeric_value`, which raises `AttributeError`. The guards
only catch `ValueError`/`TypeError`, so the error propagates and the endpoint
returns **HTTP 500** for any patient who has a lab result in the window.

**Files & lines.**

- `clinical_reasoning/services/drug_toxicity.py:297`
- `clinical_reasoning/services/treatment_failure.py:357, 379, 403, 428, 431`
- `clinical_reasoning/services/disease_validation.py:252`

**Change.** Replace every `.numeric_value` with `.value_numeric`. In
`drug_toxicity.py:297`:

```python
# before
lab_values[key] = float(r.numeric_value)
# after
lab_values[key] = float(r.value_numeric)
```

Apply the identical rename at each line above.

**Also check the date field while you're in these files.** `drug_toxicity.py`
uses `result_date` (line 289). Confirm the real name on `LabResult` — the audit
found the toxicity module and the registry UI disagreed. Open `labs/models.py`
and match the actual field (`sample_date` vs `result_date`); fix any mismatch the
same way. A wrong date field silently drops the 90-day filter or crashes.

**Fast way to find every occurrence:**

```bash
grep -rn "numeric_value" clinical_reasoning/
grep -rn "result_date\|sample_date" clinical_reasoning/ labs/models.py
```

**Prove it.** B-5 test `test_toxicity_endpoint_ok_with_labs` must return 200, not
500, for a patient with a recent `LabResult`.

---

## B-3 — Fix the inverted "lower = worse" toxicity rules

**Problem.** `_evaluate_toxicity_rule()` grades every rule as *higher = worse*
(`lab_value >= critical`). That is correct for creatinine, potassium, glucose,
ALT. It is **backwards** for the two leukopenia/hypogammaglobulinemia rules where
*lower = worse*:

- MMF & Cyclophosphamide **WBC** (myelotoxicity) — `drug_toxicity.py:83, 95`
- Rituximab **IgG** (hypogammaglobulinemia) — `drug_toxicity.py:107`

A normal WBC of 7.0 satisfies `7.0 >= 0.8` → graded **critical**. Once B-1/B-2
make the module actually run, this fires a false "critical marrow toxicity" on
every patient with a normal count → alert fatigue. **B-3 must ship together with
B-1/B-2, never after.**

**Fix — add an explicit direction to the rule, then branch on it.**

**Step 1.** Add a field to the `ToxicityRule` dataclass (`drug_toxicity.py:27-38`):

```python
@dataclass
class ToxicityRule:
    drug_class: str
    drug_name: str
    lab_test: str
    severity_thresholds: dict[str, float]
    mechanism: str
    clinical_action: str
    monitoring_frequency: str
    risk_factors: list[str] = field(default_factory=list)
    contraindication_check: str = ""
    direction: str = "high"   # "high" = higher is worse (default),
                              # "low"  = lower is worse (leukopenia, hypo-IgG)
```

**Step 2.** Mark the three "low is worse" rules. On the two **WBC** rules
(lines ~79-101) and the **immunoglobulin_g** rule (lines ~102-113) add
`direction="low",`:

```python
    ToxicityRule(
        drug_class="IMPDH inhibitor",
        drug_name="Mycophenolate mofetil",
        lab_test="WBC",
        severity_thresholds={"mild": 3.5, "moderate": 2.5, "severe": 1.5, "critical": 0.8},
        ...
        direction="low",
    ),
    # …same for the Cyclophosphamide WBC rule and the Rituximab IgG rule
```

Leave every other rule as-is (they default to `"high"`).

**Step 3.** Branch in `_evaluate_toxicity_rule()` (`drug_toxicity.py:369-393`):

```python
def _evaluate_toxicity_rule(rule, lab_value, risk_factors):
    thresholds = rule.severity_thresholds
    severity = None
    threshold = None

    if rule.direction == "low":
        # lower value = worse; critical is the LOWEST threshold
        if lab_value <= thresholds.get("critical", float("-inf")):
            severity, threshold = "critical", thresholds["critical"]
        elif lab_value <= thresholds.get("severe", float("-inf")):
            severity, threshold = "severe", thresholds["severe"]
        elif lab_value <= thresholds.get("moderate", float("-inf")):
            severity, threshold = "moderate", thresholds["moderate"]
        elif lab_value <= thresholds.get("mild", float("-inf")):
            severity, threshold = "mild", thresholds["mild"]
    else:
        # higher value = worse (unchanged behavior)
        if lab_value >= thresholds.get("critical", float("inf")):
            severity, threshold = "critical", thresholds["critical"]
        elif lab_value >= thresholds.get("severe", float("inf")):
            severity, threshold = "severe", thresholds["severe"]
        elif lab_value >= thresholds.get("moderate", float("inf")):
            severity, threshold = "moderate", thresholds["moderate"]
        elif lab_value >= thresholds.get("mild", float("inf")):
            severity, threshold = "mild", thresholds["mild"]

    if severity is None:
        return None
    # …rest unchanged (risk-factor boost, priority, return ToxicityAlert)
```

**Prove it.** Add these assertions to B-5:

- WBC = 7.0 on MMF → **no** alert.
- WBC = 0.7 on MMF → **critical**.
- IgG = 1000 on Rituximab → **no** alert.
- IgG = 90 on Rituximab → **critical**.
- Creatinine = 3.6 on Tacrolimus → still **critical** (regression: "high" path
  unchanged).

---

## B-4 — Make the CDS plans actually render (one line)

**Problem.** The clinician patient page reads the disease id from
`profile.disease_trajectory["disease_id"]`, but `disease_trajectory` never
contains that key (it holds `trend`, `detail`, `confidence`,
`kidney_survival_estimate`). So `disease_id` is always `""`, the `if disease_id:`
block never runs, and the management / monitoring / follow-up plans are always
`None` → the template renders nothing. The disease id actually lives on
`profile.differential[0]["disease_id"]`.

**File.** `clinic/views.py:332`

**Change.**

```python
# before
if profile and profile.disease_trajectory:
    disease_id = profile.disease_trajectory.get("disease_id", "")

# after
if profile and profile.differential:
    disease_id = (profile.differential[0] or {}).get("disease_id", "")
```

`profile.differential` is a list; guard the index in case it's empty (the
`(… or {})` handles a null first element). The rest of the block
(`if disease_id:` and the three generators) is already correct.

**Prove it.** For a patient whose profile has `differential[0].disease_id = "iga"`,
load `/clinic/patient/<id>/` (or whatever the route is) and confirm the
Management / Monitoring / Follow-up panels now populate. Add a view test that
asserts `management_plan is not None` in the template context.

---

## B-5 — Add integration tests that exercise the real ORM path

**Problem.** 195 tests pass, but every toxicity/treatment-failure/relapse test
**mocks out `_get_current_medications` and `_get_recent_lab_values`** — i.e. it
mocks exactly the two functions that were broken. Green CI proved nothing about
the safety paths. You must add tests that hit the real ORM.

**File.** new, e.g. `clinical_reasoning/tests/test_cds_integration.py`

**Rules for these tests:**

- Use `@pytest.mark.django_db` (or Django's `TestCase`).
- Build **real** rows: a `Patient`, a finalized `Prescription` +
  `PrescriptionItem` (or a `TreatmentExposure`), and real `LabResult` rows.
- **Do not mock** `_get_current_medications` or `_get_recent_lab_values`.

**Skeleton:**

```python
import pytest
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
def test_toxicity_reads_ongoing_meds(patient, drug_mmf):
    from treatments.models import TreatmentExposure
    from clinical_reasoning.services.drug_toxicity import _get_current_medications
    TreatmentExposure.objects.create(
        patient=patient, drug=drug_mmf, drug_name="Mycophenolate mofetil",
        dose="1 g", frequency="1+0+1", start_date=timezone.now().date(),
        ongoing=True,
    )
    meds = _get_current_medications(patient)
    assert any("mycophenolate" in m["name"].lower() for m in meds)

@pytest.mark.django_db
def test_normal_wbc_on_mmf_no_alert(patient, drug_mmf, wbc_test):
    # ongoing MMF + normal WBC 7.0 -> NO critical alert (regression for B-3)
    ...
    report = run_drug_toxicity(patient)   # the real service entry point
    assert all(a.severity != "critical" for a in report.alerts)

@pytest.mark.django_db
def test_toxicity_endpoint_ok_with_labs(client, patient_with_recent_labs):
    # was HTTP 500 before B-2
    resp = client.get(f"/api/v1/.../{patient_with_recent_labs.pk}/drug_toxicity/")
    assert resp.status_code == 200
```

Add parallel tests for `treatment_failure` and `relapse_detection` endpoints:
create a `LabResult` in-window and assert **200**, not 500.

**Prove it.** `python manage.py test` — new tests pass, old 195 still pass.

---

# P1 — Major

## M-1 — Stop silently swallowing CDS failures

**Problem.** `clinic/views.py:334-361` wraps each generator in
`except Exception: <plan> = None`, and the template renders nothing when a plan is
`None`. A clinician cannot tell "no recommendation applies" from "the engine
crashed." In decision support, a silently-vanishing recommendation is more
dangerous than a visible error.

**Change.** Log the exception and pass an explicit unavailable-state flag to the
template instead of a bare `None`.

```python
import logging
logger = logging.getLogger(__name__)

cds_errors = []
try:
    from clinical_reasoning.services.management_plan import generate_management_plan
    management_plan = generate_management_plan(patient, disease_id)
except Exception:
    logger.exception("management_plan failed for patient %s", patient.pk)
    management_plan = None
    cds_errors.append("management")
# …same pattern for monitoring_plan_data and followup_schedule
```

Then in the template, where a panel is empty **and** its name is in `cds_errors`,
show "Recommendations temporarily unavailable — logged for review" rather than a
blank space. Add `cds_errors` to the template context.

Do the same in B-1: don't let `_get_current_medications` return `[]` on a real
error — let it raise so M-1 catches and surfaces it.

---

## M-2 — Regenerate the ClinicalProfile automatically

**Problem.** The CDS plans depend on a `ClinicalProfile` that today is only built
by a manual API call, so in routine clinic use the profile is stale or missing
and CDS never appears even after B-4.

**Change.** Add a `post_save` signal (or hook the existing save flow) so that
saving a `ClinicalEncounter`, `LabResult`, or biopsy triggers profile
regeneration for that patient. Keep it cheap:

```python
# clinical_reasoning/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender="encounters.ClinicalEncounter")
@receiver(post_save, sender="labs.LabResult")
def _regenerate_profile(sender, instance, **kwargs):
    from clinical_reasoning.services.profile import regenerate_profile  # existing generator
    patient = instance.patient if hasattr(instance, "patient") else instance.encounter.patient
    regenerate_profile(patient)   # wrap in try/log; never block the save
```

Register the signals module in the app's `AppConfig.ready()`. If regeneration is
expensive, enqueue it instead of running inline. **Confirm the real generator
function name** before wiring — reuse whatever the manual API endpoint calls.

**Prove it.** Save a new lab for a patient with no profile → profile exists
afterward → patient page shows CDS without any manual API call.

---

## G-1 — Get a named clinician to sign off the active knowledge base

**Problem.** 0 of 618 active rules have `approved_by`, `date_validated`, or
`next_review_date`. Governance fields exist but were never populated — there is no
record that a clinician approved the content the pilot will act on.

**Change (process + data, not code):**

1. A named nephrologist reviews the active rule set and signs off.
2. Stamp the approval on every active row:

```python
python manage.py shell -c "
from django.utils import timezone
from <kb_app>.models import <RuleModel>
from datetime import timedelta
RuleModel = <RuleModel>
RuleModel.objects.filter(active=True).update(
    approved_by='Dr <Name>, <reg no>',
    date_validated=timezone.now().date(),
    next_review_date=timezone.now().date() + timedelta(days=180),
)
"
```

(Substitute the real app/model/field names — find them with
`grep -rn "approved_by\|date_validated\|next_review_date" --include=*.py`.)
Do **not** rubber-stamp: this is a clinical sign-off, the shell command just
records it.

---

## G-2 — Make `confidence_score` real, or hide it

**Problem.** `confidence_score` is a constant `0.0` on all rows. Any UI showing a
confidence number is showing a meaningless figure.

**Change — pick one:**

- **Preferred:** hide/remove the confidence figure from the clinician UI until a
  real score exists. Search the templates for where it's rendered and gate it out.
- **Or:** populate a defensible score (e.g. by evidence grade: KDIGO 1A → 0.95,
  1B → 0.85, 2C → 0.6, expert opinion → 0.4) and document the mapping. Never leave
  a live `0.0` on screen implying "no confidence."

---

## G-3 — Designate one canonical seed; retire `TEST-*` fixtures

**Problem.** `TEST-*` fixture rules are mixed into the ACTIVE knowledge set, and
there are multiple seed commands. The pilot must run on a single, known KB.

**Change.**

```bash
grep -rn "TEST-" --include=*.py --include=*.json .   # find the fixtures + seeders
```

1. Deactivate or delete `TEST-*` rules from the active set:
   `RuleModel.objects.filter(entry_id__startswith="TEST-").update(active=False)`.
2. Choose **one** seed command as canonical; document it in the README as the
   pilot KB loader. Mark or remove the others.

**Prove it.** `RuleModel.objects.filter(active=True, entry_id__startswith="TEST-").count() == 0`.

---

# P2 — Minor (safe cleanup)

## C-1 — Remove the dead `decision` app
`decision` is in `INSTALLED_APPS` but URL-disabled and deprecated. Remove it from
`INSTALLED_APPS` (settings). Run the test suite after — if nothing imports it,
you're done.

## C-2 — Repair or delete `_assess_risk_factors`
`drug_toxicity.py:304-344` imports `comorbidities.models` and `allergies.models` —
**neither app exists**, so both imports fail into `except: pass` and the
risk-factor severity boost never triggers. Either (a) delete the two dead import
blocks and the boost, or (b) re-source risk factors from data that *does* exist
(e.g. baseline comorbidity text, `patient.latest_egfr`). Lowest priority — it only
degrades scoring, it doesn't crash.

## C-3 — One tested accessor for lab/med/feature reads
The schema-drift bugs (B-1, B-2) happened because each service re-implemented ORM
reads. Centralize them: put `get_current_medications(patient)` and
`get_recent_lab_values(patient)` in one module with tests, and have every CDS
service import from there. Prevents the next field-name drift.

## C-4 — Don't surface raw rule IDs as disease names
`disease_name = entry.entry_id` makes rule IDs appear where a disease name should.
Map `entry_id → human-readable disease name` (or read the disease name field) at
that assignment.

## C-5 — Don't imply automated SMS
The "SMS reminder" path has no real gateway. Either wire a real SMS provider or
relabel it "manual reminder log" in the UI so staff don't assume messages send
automatically.

## C-6 — Enforce one-active-machine for the OneDrive SQLite DB
Two DB files exist (`db.sqlite3`, `db-Dr-Wasim.sqlite3`) and OneDrive-synced
SQLite **corrupts if opened on two machines at once.** Document and enforce "one
active machine at a time," or move the pilot DB out of the OneDrive-synced folder.
This is a data-integrity risk independent of the CDS fixes.

---

# Verification checklist (run before declaring P0 done)

```bash
# 1. No wrong field names remain
grep -rn "numeric_value" clinical_reasoning/            # -> no results
grep -rn "status__in=(\"active\"\|status__in=('active'" clinical_reasoning/  # -> none

# 2. Full suite + new integration tests pass
python manage.py test

# 3. Manual smoke on a real patient (has ongoing MMF + recent normal WBC + labs)
#    a. /api/.../drug_toxicity/    -> 200, normal WBC -> NO critical alert
#    b. /api/.../treatment_failure/ -> 200 (was 500)
#    c. /api/.../relapse_detection/ -> 200 (was 500)
#    d. clinician patient page      -> Management/Monitoring/Follow-up panels render
```

Sign-off gate: **all four smoke checks green + G-1 clinical sign-off recorded**
before the CDS layer is enabled for the pilot.

---

# Appendix A — Registry-only fallback (Path B)

If P0 can't be completed and re-validated before the pilot start date, ship the
pilot with the **CDS layer flagged OFF**. The registry, prescription, lab,
pathology, outcomes, and research core is safe and usable today.

1. Add a settings flag, e.g. `CDS_ENABLED = False`.
2. In `clinic/views.py`, skip the CDS block entirely when the flag is off (set all
   three plans to `None`, and have the template hide the panels rather than showing
   an "unavailable" state).
3. Gate the CDS API endpoints (`drug_toxicity`, `treatment_failure`,
   `relapse_detection`) behind the same flag → return 404/disabled when off.
4. Pilot registry-only. Re-enable CDS as a validated increment once B-1…B-5 and
   G-1/G-2 are done.

This is the safe default. **Under no circumstances enable the CDS layer in its
current (pre-fix) state** — it under-reports toxicity and relapse and can mislead.
