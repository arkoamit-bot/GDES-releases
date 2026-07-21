# GDES_FINAL_CLINICAL_SAFETY_AUDIT.md

**System:** Glomerular Disease Expert System (GDES) — Release Candidate
**Reviewer:** Claude Code (independent external review)
**Date:** 2026-07-12
**Method:** Direct source + live-database inspection (`db.sqlite3`), not prior reports.
**Verdict feeds:** `GDES_FINAL_PILOT_READINESS_REPORT.md`, `GDES_FINAL_RECOMMENDATIONS.md`

> Patient safety was treated as the highest priority. Every finding below was
> verified against the actual code and/or the live database. File:line
> references are provided so each can be re-checked independently.

---

## Executive summary

The **registry, prescription, laboratory, and pathology core is clinically
safe** and schema-correct. The **AI / clinical-decision-support (CDS) layer is
not**. Several safety-monitoring features are wired to a data model that does
not exist in this codebase, so they either crash or silently return a falsely
reassuring "nothing wrong." None of the AI safety-monitoring services has ever
executed against real patient data — the 195-test suite mocks out exactly the
functions that are broken (see `GDES_FINAL_CODE_QUALITY_REPORT.md`).

These are **not** design flaws requiring redesign. They are a small, bounded set
of field-name / wiring defects. But until they are fixed and re-validated
end-to-end, the CDS layer must **not** be relied on for patient care.

| # | Severity | Finding | Status |
|---|----------|---------|--------|
| S-1 | **BLOCKER** | Drug-toxicity monitoring cannot read medications or labs — always empty or crashes | Broken |
| S-2 | **BLOCKER** | Toxicity thresholds for leukopenia (WBC) & hypogammaglobulinemia (IgG) are directionally inverted | Broken logic |
| S-3 | **BLOCKER** | Treatment-failure & relapse detection crash (HTTP 500) for any patient with recent labs | Broken |
| S-4 | **MAJOR** | Personalized management / monitoring / follow-up plans never render in the clinician UI | Broken wiring |
| S-5 | **MAJOR** | Silent-failure pattern: CDS generation swallowed by bare `except Exception` | Unsafe pattern |
| S-6 | **MINOR** | Patient-specific risk factors (diabetes, CKD, allergy) never contribute to toxicity scoring | Degraded |

---

## S-1 — Drug-toxicity monitoring is non-functional (BLOCKER)

**Where:** `clinical_reasoning/services/drug_toxicity.py`
**Exposed at:** `clinical_reasoning/views.py:223` (`/api/v1/.../drug_toxicity/`)

Three independent defects each disable the feature:

1. **Wrong prescription status filter.**
   `_get_current_medications` (drug_toxicity.py:249) filters
   `Prescription.objects.filter(status__in=("active","ongoing"))`.
   The real model (`prescriptions/models.py:19-21`) defines only
   `Status = {draft, final}`. `active`/`ongoing` never exist → the queryset is
   always empty.

2. **Wrong model for the drug.**
   The same code calls `.select_related("drug")` and reads `p.dose`,
   `p.frequency`. `Prescription` has **no** `drug`, `dose`, or `frequency`
   field — those live on `PrescriptionItem` (`prescriptions/models.py:107-117`).
   The `select_related("drug")` raises `FieldError`, caught by the bare
   `except Exception: return []` (drug_toxicity.py:264-265).

   **Net effect:** `_get_current_medications()` returns `[]` for every patient.
   No medication is ever evaluated. No toxicity alert can ever fire.

3. **Wrong lab field name.**
   `_get_recent_lab_values` (drug_toxicity.py:297) reads `float(r.numeric_value)`.
   The real field is `LabResult.value_numeric` (`labs/models.py:131`). Accessing
   `r.numeric_value` raises `AttributeError`, which is **not** caught (the guard
   is `except (ValueError, TypeError)`). This function is called *before* the
   medication loop (drug_toxicity.py:218), so for any patient with a lab result
   in the last 90 days the endpoint returns **HTTP 500**.

**Clinical consequence:** the advertised CNI-nephrotoxicity / myelotoxicity /
hyperkalemia / hypogammaglobulinemia surveillance does nothing. A clinician who
trusts "No drug toxicity detected" is being falsely reassured; a clinician who
opens the endpoint on a patient with labs gets a server error.

---

## S-2 — Leukopenia & hypogammaglobulinemia thresholds are inverted (BLOCKER)

**Where:** `drug_toxicity.py:369-393` (`_evaluate_toxicity_rule`)

Every rule is evaluated as *"higher value = worse"*:

```python
if lab_value >= thresholds.get("critical", inf):  severity = "critical"
elif lab_value >= thresholds.get("severe", inf):   severity = "severe"
...
```

That is correct for creatinine, potassium, glucose, ALT, proteinuria. It is
**backwards** for the two "lower = worse" rules:

- **MMF / Cyclophosphamide myelotoxicity (WBC)** — thresholds
  `mild 3.5, moderate 2.5, severe 1.5, critical 0.8` (drug_toxicity.py:83, 95).
  Leukopenia means WBC is *low*. But a **normal** WBC of 7.0 satisfies
  `7.0 >= 0.8` first → graded **critical**. Every patient with a normal count
  would be flagged as critical marrow toxicity.
- **Rituximab hypogammaglobulinemia (IgG)** — thresholds
  `mild 600 … critical 100` (drug_toxicity.py:107). A normal IgG of 1000
  `>= 100` → **critical**.

`ToxicityRule` has no "direction" field, so the engine cannot distinguish the
two cases. Today this is masked by S-1 (no meds are ever retrieved), but if S-1
is fixed naively the system will emit a flood of false-critical alerts → alert
fatigue and loss of clinician trust. **Both must be fixed together.**

---

## S-3 — Treatment-failure & relapse detection crash on real data (BLOCKER)

**Where:** `clinical_reasoning/services/treatment_failure.py:357, 379, 403, 428, 431`
**Also:** `clinical_reasoning/services/disease_validation.py:252`
**Exposed at:** `clinical_reasoning/views.py:241` (`treatment_failure`), `:260` (`relapse_detection`)

Same root cause as S-1.3: these services read `result.numeric_value`
(non-existent) instead of `value_numeric`. The `try/except` guards only catch
`ValueError`/`TypeError`, so the `AttributeError` propagates:

- Patient **with** recent labs → endpoint returns **HTTP 500**.
- Patient **without** recent labs → helper returns `{}`/`None` → report says
  *"no treatment failure"* / *"no relapse"* — a **false negative** presented as
  a clinical conclusion.

Relapse and non-response are exactly the signals a nephrology follow-up clinic
depends on. A monitoring feature that silently reports "no relapse" because it
cannot read the proteinuria it is supposed to be watching is a patient-safety
hazard.

---

## S-4 — Management / monitoring / follow-up plans never reach the clinician (MAJOR)

**Where:** `clinic/views.py:331-361`; template gate `templates/clinic/patient_detail.html:527`

The clinician's patient page builds the three CDS plans only inside:

```python
if profile and profile.disease_trajectory:
    disease_id = profile.disease_trajectory.get("disease_id", "")   # views.py:332
    if disease_id:
        management_plan = generate_management_plan(patient, disease_id)
        ...
```

But `disease_trajectory` **never contains `disease_id`**. Verified two ways:

- `assess_trajectory()` returns only `{trend, detail, confidence,
  kidney_survival_estimate}` (`clinical_reasoning/services/disease_trajectory.py:21-55`).
- Live DB: all `ClinicalProfile.disease_trajectory` rows have keys
  `['trend','detail','confidence','kidney_survival_estimate']` — no `disease_id`.
  The disease identifier lives on `profile.differential[0]["disease_id"]`
  (verified: values `diabeticNephropathy`, `iga`).

Therefore `disease_id` is always `""`, the `if disease_id:` block never runs,
and `management_plan` / `monitoring_plan` / `followup_schedule` are always
`None`. The template's `{% if management_plan %}` then renders **nothing**.

**Clinical consequence:** the flagship output of the whole system — the
KDIGO-aligned personalized treatment plan, monitoring parameters, and follow-up
schedule (which are genuinely well written, see
`GDES_FINAL_KNOWLEDGE_AUDIT.md`) — is invisible in routine use. The single-line
fix is to read the id from `profile.differential[0]`.

---

## S-5 — Silent-failure pattern around CDS generation (MAJOR, pattern)

`clinic/views.py:334-361` wraps each plan generator in
`try: ... except Exception: <plan> = None`. Combined with template gates that
render nothing when a value is `None`, **any** exception in the CDS layer
produces a blank panel with no error, no log surfaced to the user, and no
indication that a recommendation was suppressed. In a decision-support context
"the advice silently disappeared" is more dangerous than "the page errored,"
because the clinician cannot tell the difference between *"no recommendation
applies"* and *"the recommendation engine failed."* Failures should be logged
and a visible "recommendations unavailable" state shown.

---

## S-6 — Patient risk factors never modulate toxicity severity (MINOR)

`_assess_risk_factors` (drug_toxicity.py:304-344) imports `comorbidities.models`
and `allergies.models`. **Neither app exists** (not in `INSTALLED_APPS`, no
directory). Both imports fail into `except Exception: pass`, so diabetes,
hypertension, obesity, and allergy risk are never detected, and the
risk-factor severity boost (drug_toxicity.py:396-398) never triggers. Lower
priority only because S-1 already disables the whole module.

---

## What is safe (verified positives)

- **Prescription workflow** — draft→final immutability, printed-at/by
  provenance, content hashing, reconciliation. Schema-consistent.
- **Pregnancy safety screening** in the management planner
  (`management_plan.py:619-624`) correctly keys on `patient.sex` (real field,
  `patients/models.py:66`) and warns on mycophenolate / cyclophosphamide /
  ACEi-ARB / statins.
- **Lab and eGFR handling in the registry UI** (`clinic/views.py:237-284`) uses
  the correct `value_numeric` field and real test codes.
- **Automatic timestamped backups** (6-hourly, 60 retained) and an audit
  middleware are in place.

---

## Required before pilot (safety gate)

1. Fix S-1, S-2, S-3, S-4 and add **integration** tests that exercise the real
   ORM path (a real `Patient` + `PrescriptionItem` + `LabResult`), not mocks.
2. Fix or explicitly disable S-5 / S-6.
3. If the CDS layer cannot be corrected and re-validated before the pilot start
   date, **feature-flag the entire AI/CDS layer OFF** and run the pilot as a
   registry + prescription system, which is safe today. Do not ship a
   decision-support feature that silently under-reports toxicity and relapse.
