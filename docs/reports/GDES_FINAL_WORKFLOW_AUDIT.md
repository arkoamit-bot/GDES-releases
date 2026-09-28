# GDES_FINAL_WORKFLOW_AUDIT.md

**System:** GDES
**Reviewer:** Claude Code (independent)
**Date:** 2026-07-12
**Scope:** The end-to-end patient journey defined in the audit request.

---

## The journey, step by step

| Step | Implemented? | Where | Notes |
|------|--------------|-------|-------|
| Registration | ✅ | `clinic` patient_form, `patients.Patient` | Solid; validation on DOB/enrollment. |
| Clinical assessment | ✅ | `encounters.ClinicalEncounter`, baseline | BP, edema grade, features captured. |
| Laboratory entry | ✅ | `labs` (order → result), `clinic/lab_*` | Correct schema; eGFR derivation present. |
| Imaging | ⚠️ partial | no dedicated imaging model found | Captured only as free text / not a first-class step. |
| Kidney biopsy | ✅ | `pathology.Biopsy`, `GNDiagnosis`, `IgANScore` | MEST-C / crescents captured. |
| AI differential diagnosis | ⚠️ works but not surfaced well | `clinical_reasoning` engine → `ClinicalProfile.differential` | Runs; top-disease id present. See W-1. |
| Suggested investigations | ⚠️ API-only | `investigation_engine.py` | Not shown in clinician UI. |
| Diagnosis confirmation | ✅ | `pathology` / `primary_diagnosis` | Manual confirmation supported. |
| Management plan | ❌ **not reaching UI** | `management_plan.py` (good content) | **Blocked by S-4** — never renders. |
| Prescription | ✅ | `prescriptions` | Strong: draft/final, PDF, reconciliation. |
| Monitoring plan | ❌ **not reaching UI** | `monitoring_plan.py` | Same S-4 gate. |
| Automatic follow-up | ⚠️ | `followup` engine + `followup_scheduler.py` | Schedule generation blocked by S-4 gate in UI. |
| SMS reminder | ⚠️ framework only | `reminders` app | "SMS-ready" but no gateway; manual/stub. |
| Clinical review | ✅ | encounters / relapse forms | Manual documentation works. |
| Outcome recording | ✅ | `analytics.PatientOutcome`, `compute_outcomes` | Remission/relapse/survival computed. |
| Research enrollment | ✅ | `studies` (eligibility, randomization) | Works; deferred export item noted separately. |

**Overall:** the *registry* half of the journey (register → assess → lab →
biopsy → prescribe → follow-up documentation → outcome → research) is
**complete and usable**. The *decision-support* half (differential →
investigations → management → monitoring → auto follow-up → SMS) is
**built but not connected to the clinician's screen**.

---

## W-1 — The CDS steps are logically connected in code but not in the UI

The engine (`engine.py:reason_about_patient`) does chain the steps correctly:
features → rule evaluation → differential → trajectory → care gaps →
reasoning chain → risk → insights. That chain is sound.

The break is at presentation: as detailed in the Clinical Safety audit (S-4),
`clinic/views.py:332` reads the disease id from the wrong field, so the
downstream management/monitoring/follow-up panels never populate. From the
nephrologist's chair, the journey therefore **stops at "prescription"** — the
system does not visibly carry them into a management/monitoring/follow-up plan.

---

## W-2 — Profile generation is not obviously triggered in the routine flow

`reason_about_patient` is invoked from: an event handler
(`event_handlers.py:34`), a Celery task (`tasks.py`), and several API actions
(`views.py:52/76/103/212`). The clinician's patient-detail view **reads** an
existing `ClinicalProfile` but does not create one (`clinic/views.py:217-220`
just does `get`, falling back to `None`). If no event/API call has run for a
patient, the profile — and therefore every CDS panel — is simply absent. Only
3 of 8 patients in the live DB have a profile. **The pilot needs a defined,
automatic trigger** (e.g. regenerate on encounter/lab/biopsy save) so CDS is
present without a manual API poke.

---

## W-3 — Would it work in a busy nephrology clinic?

- **Data entry ergonomics are good**: guided `clinic` forms, a progress strip
  (`views.py:364-379`), lab pivot table, and eGFR/proteinuria trend charts on
  one page. This is genuinely clinic-friendly.
- **Click cost is acceptable** for the registry path.
- **Risk:** because CDS output is currently blank (S-4) or requires an API call
  (W-2), a busy clinician will perceive the "expert system" as *not doing
  anything*. Once S-4/W-2 are fixed, the same page becomes strong.

---

## W-4 — Unnecessary / redundant steps

- Two follow-up mechanisms coexist: the `followup` engine (protocol library)
  and `clinical_reasoning/services/followup_scheduler.py`. For a single-center
  pilot, pick one and disable the other to avoid divergent schedules.
- `SMS reminder` is a step in the stated journey but has no delivery backend.
  Either label it "manual reminder log" for the pilot or remove it from the
  advertised workflow to avoid implying automated messaging that does not exist.

---

## Workflow verdict

The **registry workflow is pilot-ready**. The **CDS workflow is one wiring fix
(S-4) plus one trigger decision (W-2) away** from being usable. Until then, the
journey is honestly described as *"a strong glomerular-disease registry with a
decision-support layer that is present in code but not yet surfaced to the
clinician."* Do not advertise the CDS steps to pilot users until they render.
