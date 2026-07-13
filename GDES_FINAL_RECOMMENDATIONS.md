# GDES_FINAL_RECOMMENDATIONS.md

**System:** GDES (Glomerular Disease Expert System)
**Reviewer:** Claude Code — independent final review before clinical pilot
**Date:** 2026-07-12

This document consolidates the prioritized, code-freeze-compatible actions from
the six companion audits. Every item is a **correction**, not a feature — each
targets patient safety, clinician workflow, or pilot reliability, consistent
with the stated review philosophy and code-freeze policy.

---

## P0 — Blockers (must fix, or disable the CDS layer, before pilot)

| ID | Action | File(s) | Fix size |
|----|--------|---------|:--------:|
| **B-1** | Read active meds from `PrescriptionItem` (not `Prescription`); use real statuses (`draft`/`final`, and the item is on a finalized prescription) and fields (`drug`, `dose`, `frequency` live on the item). | `clinical_reasoning/services/drug_toxicity.py:245-265` | small |
| **B-2** | Replace `numeric_value` → `value_numeric` everywhere. | `drug_toxicity.py:297`; `treatment_failure.py:357,379,403,428,431`; `disease_validation.py:252` | trivial |
| **B-3** | Add a "direction" to toxicity rules; evaluate WBC (leukopenia) and IgG (hypogammaglobulinemia) as *lower = worse*. Add a test: normal WBC on MMF ⇒ **no** critical alert. | `drug_toxicity.py:27-150,369-393` | small |
| **B-4** | Take the disease id from `profile.differential[0]["disease_id"]`, not `profile.disease_trajectory`. | `clinic/views.py:332` | one line |
| **B-5** | Add `@pytest.mark.django_db` **integration** tests exercising real ORM reads for toxicity / treatment-failure / relapse (do not mock `_get_current_medications` / `_get_recent_lab_values`). | `tests/` | medium |

> If B-1…B-5 cannot be completed and re-validated before the pilot start date,
> **feature-flag the AI/CDS layer OFF and run a registry-only pilot** (safe
> today) — see `GDES_FINAL_PILOT_READINESS_REPORT.md`, Path B.

---

## P1 — Major (fix before relying on CDS / advertising governance)

| ID | Action | Reference |
|----|--------|-----------|
| **M-1** | Stop swallowing CDS exceptions silently — log and show an explicit "recommendations unavailable" state instead of a blank panel. | `clinic/views.py:334-361` (S-5) |
| **M-2** | Add an automatic `ClinicalProfile` regeneration trigger on encounter/lab/biopsy save, so CDS is present without a manual API call. | W-2 |
| **G-1** | Have a named clinical reviewer approve the active knowledge base: populate `approved_by`, `date_validated`, and `next_review_date`. Currently 0/618. | K-2 |
| **G-2** | Set a real `confidence_score` (it is a constant `0.0` on all 625 rows) **or** hide any "confidence" figure in the UI until it is real. | K-2 |
| **G-3** | Retire `TEST-*` fixture rules from the ACTIVE set; designate one canonical seed command as the pilot knowledge base. | K-4 |

---

## P2 — Minor (cleanup; safe under code freeze)

| ID | Action | Reference |
|----|--------|-----------|
| C-1 | Remove `decision` app from `INSTALLED_APPS` (deprecated, URL-disabled). | A-1 |
| C-2 | Repair `_assess_risk_factors` (references non-existent `comorbidities`/`allergies` apps) or remove the dead risk-factor boost. | S-6 |
| C-3 | Centralize lab/med/feature reads behind one tested accessor to prevent future schema drift. | A-2 |
| C-4 | Fix `disease_name = entry.entry_id` so raw rule IDs don't surface as disease names. | K-1b |
| C-5 | Either wire a real SMS gateway or relabel "SMS reminder" as a manual reminder log; don't imply automated messaging. | W-4 |
| C-6 | Document and enforce "one active machine at a time" for the OneDrive-synced SQLite DB. | Pilot R-1 |

---

## Explicitly NOT recommended

Per the review philosophy, no new diseases, no new modules, no UI redesign, no
architecture redesign. The knowledge content and the registry design are good;
the work is corrective, not expansive.

---

## Final question

> **Would you personally approve GDES for a controlled single-center clinical
> pilot in a nephrology department?**

### **APPROVED WITH MAJOR CORRECTIONS**

**Justification.**

- The **registry, prescription, laboratory, pathology, outcomes, and research
  core is clinically safe, schema-correct, well-tested in its own right, and
  clinic-usable today.** On that basis a *registry* pilot could start now.

- The **AI / clinical-decision-support layer is currently unsafe to rely on**:
  drug-toxicity surveillance never reads medications or labs (S-1), its
  leukopenia/hypogammaglobulinemia logic is inverted (S-2), treatment-failure
  and relapse detection crash on real labs or return false negatives (S-3), and
  the flagship management/monitoring/follow-up plans never render for the
  clinician (S-4). None of this was caught because the 195-test suite mocks out
  the broken paths.

- Crucially, **these are bounded wiring and schema-name defects, not design
  failures.** The corrections are small, local, and fully specified above
  (B-1…B-5). No redesign is required. The knowledge base is broad and its
  clinical content is current and correct; its only real gap is governance
  *operation* (reviewer sign-off, real confidence, review schedule).

Therefore I cannot give an unconditional **APPROVED** (the CDS layer would harm
patient trust and could mislead), and **NOT APPROVED** overstates the problem
(the safe registry path is genuinely ready and the CDS fixes are days, not
months, of work). The correct call is **APPROVED WITH MAJOR CORRECTIONS**:

1. Complete P0 (B-1…B-5) and validate end-to-end; **or**
2. Launch registry-only with the CDS layer flagged OFF (Path B), adding the CDS
   as a validated increment once P0/P1 are done.

Under **no** circumstances should the CDS layer go live in its current state.
