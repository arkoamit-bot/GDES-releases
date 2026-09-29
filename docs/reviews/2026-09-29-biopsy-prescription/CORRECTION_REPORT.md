# Correction report: biopsy field linkage and prescription diagnosis carry-forward

Handoff: `docs/CLAUDE_OPUS_BIOPSY_LINKAGE_DIAGNOSIS_CARRY_FORWARD_2026-09-29.md`.
Branch: `claude/opus-linkage-histopathology-review-7c2d25` (already carries the
2026-09-27 entry-linkage work, which the handoff builds on).

## Starting point on this branch

The handoff was written against `e004959`. On this branch, two of its four
probes already passed before this change: percentages above 100 were rejected
(model validators added on 2026-09-27), and an FSGS primary/secondary
contradiction was reported. Still failing were the **diagnosis prefill**
(prefill came from the patient's working diagnosis) and the **crescent
contradiction** (a positive percentage saved with crescents not assessed).

## Results

- Probes (`probes.py`) and the 24 lupus tests: **28 passed**
  (`results_after_fix.log`; the reviewer's original is `results.log`).
- New permanent tests: `tests/test_biopsy_linkage_carry_forward.py`.
- `pytest`: 1020 passed, 2 skipped, 11 xfailed. `manage.py test`: 735 run, one
  failure, `test_extreme_egfr_impact`, which also fails on `main`.
- `ruff check .` clean; `makemigrations --check`: no changes (no schema change).

## Field owners (see `docs/FIELD_OWNERSHIP_MAP.md`)

| Fact | Owner | Change |
|---|---|---|
| Primary / secondary | `GNDiagnosis.primary_secondary` | The FSGS panel no longer asks it; `FSGSPathology.primary_secondary` is projected from the owner on every write path (entry, amendment, review finalization) and is read-only in admin. |
| FSGS variant, ISN/RPS class | The diagnosis label (`QUALIFIERS`), else the panel | A stated value is shown read-only on the form, from an explicit table (`qualifier_table()`); the old substring/regex matching in the page is gone. |
| Crescents | `Biopsy.crescents_present` + `crescent_pct` | One set of rules (`pathology/consistency.py`) used by the form, amendment, API and admin. |
| Result category | `Biopsy.result_category` (entered) | Checked against diagnosis, adequacy and report status; never inferred. |
| Prescription diagnosis | `Prescription.diagnosis_text` | Prefill from the last finalized prescription (`prescriptions/services/diagnosis_prefill.py`). |

## Behaviour now

Biopsy:
- 25 % crescents with crescents *absent* or *not assessed* is refused with a
  message; *present* with 0 % or a count of 0 is refused; an unreported
  percentage stays blank.
- Oxford C0 with crescents recorded, or C1/C2 with crescents absent, is
  refused. The C1/C2 boundary and T/IFTA thresholds are **not** derived; IFTA
  and global sclerosis are shown beside MEST-C as evidence only (global
  sclerosis is labelled as distinct from Oxford S).
- Result category: positive needs a diagnosis and cannot carry a "no GN"
  label; negative cannot carry a specific-GN label or an inadequate specimen;
  positive/negative need a final or preliminary report, so a draft or pending
  report no longer changes registry membership. Diagnoses whose GN status is
  not stated by the label (e.g. tubulointerstitial nephritis, Alport) are not
  judged.
- A page opened before the update still posts the FSGS panel's old field: it
  fills a blank owner or must agree; it is never silently dropped.
- Everything saves in one transaction (a failing score save rolls back the
  biopsy; tested).

Prescription:
- Prefill order: last finalized prescription of the same patient with a
  diagnosis (visit date, version, id; no later visit) → working diagnosis →
  blank. The source is shown ("Carried from the prescription of …").
- A newer saved draft is offered with a link, not substituted. The working
  diagnosis and the selected biopsy's diagnosis are shown beside the carried
  text when they differ, each with **Use this**; nothing is changed at source.
- A custom/legacy diagnosis is kept as its own option ("… (as recorded)").
- A refused save ("Add at least one medication") now shows the form again
  with the typed diagnosis (including a deliberate clear) and advice, instead
  of redirecting and re-defaulting.
- Finalizing prints the accepted diagnosis; older prescriptions' text, hash
  and reprint are unchanged (tested). Medication carry-forward is unchanged.

## Found while deploying: the pathology summary never updated on the server

The inventory on the clinic server showed patient BGD-00001's pathology
summary blank although both biopsies say "Lupus nephritis class III". The
projection hook was a function defined inside `PathologyConfig.ready()` and
connected with Django's default weak reference; in the server process it was
garbage-collected, so **no biopsy save on the server ever re-projected the
patient summary** (the audit log has no projection write at all). Locally the
closure happened to survive, so tests passed. Fixed: a module-level receiver,
connected with `weak=False` (`pathology/apps.py`), and a regression test that
fails on the old wiring. After deploying, the affected patients were
re-projected with the existing `project_pathology()` service.

## Legacy data

`manage.py reconcile_linked_facts` has a new section,
`biopsy_conflicting_values`: out-of-range percentages, crescent/Oxford C and
result-category contradictions, primary/secondary disagreements (label vs
record, panel vs record) and variant disagreements. **Report only** — stored
values are left as they are for review. Editing such a biopsy now requires
resolving its contradiction.

## Not done, and why

- **Database CHECK constraints** for 0–100 %: not added in this change. A
  constraint migration fails on any existing out-of-range row, which would
  block the desktop updater on real data. Run the inventory first; add the
  constraints once it is empty.
- **Broad group / pathogenesis derivation**: stay editable. There is no
  clinician-reviewed mapping from diagnosis to these axes in the code, and the
  handoff forbids inventing one.
- **Membranous PLA2R/THSD7A linkage to a specimen/test**: unchanged; tissue
  stains stay on the membranous panel, serum antibodies stay lab results, and
  nothing infers one from the other or from the diagnosis label.
- A review read that changes the diagnosis to one that does not state
  primary/secondary keeps the earlier value on the owner (it is not cleared
  automatically).

## Browser evidence (local, synthetic, authenticated)

On a disposable local database with a synthetic patient (working diagnosis
IgA nephropathy; finalized prescription "FSGS - primary"), signed in:

- New prescription: diagnosis "FSGS - primary", labelled "Carried from the
  prescription of 01 Sep 2026 (v1)", with "Working diagnosis on the patient
  record: IgA nephropathy — Use this". Clicking **Use this** set IgA
  nephropathy and removed the "carried from" label.
- Biopsy: choosing "FSGS - primary" set primary/secondary to Primary,
  read-only, and opened the FSGS panel (variant only). Entering 25 % crescents
  with crescents not assessed showed an inline warning and the MEST-C panel's
  evidence line updated; saving was refused by the server with the message and
  every entry kept. Setting Crescents = Present saved; the biopsy page shows
  "Primary / secondary: Primary" and "Crescents: Present (25.0%)".

The clinic server at `http://192.168.7.55:8080` must be updated and checked
before these two live pages are called fixed.
