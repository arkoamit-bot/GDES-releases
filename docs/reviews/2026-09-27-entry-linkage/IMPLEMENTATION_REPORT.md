# Entry linkage, renal histopathology, prescription print — implementation report

Date: 2026-09-27 · Branch `claude/opus-linkage-histopathology-review-7c2d25`,
based on the reviewed commit `e004959` (the worktree was 29 commits behind it
and was moved onto it before any change).

Review: `docs/CLAUDE_OPUS_ENTRY_LINKAGE_HISTOPATHOLOGY_PRINT_REVIEW_2026-09-27.md`.
Ownership map: `docs/FIELD_OWNERSHIP_MAP.md`.

## Status, separated

| Area | Status |
|---|---|
| Implementation | Done for every finding in the review (details below). |
| Local verification | Automated tests (counts below); visual check of the HTML print route in a browser at A4 size; programmatic check of the xhtml2pdf fallback PDFs. |
| Clinical acceptance | **Not done.** Histopathology capture set, terminology, legacy diagnosis aliases, the −90/+30-day HbA1c window and the print layout need sign-off by the clinical/pathology owners. |
| Packaging | **Not done.** No desktop build was produced. |
| Deployment / live data | **Not done and not authorized.** No live record was read, reconciled or migrated. `reconcile_linked_facts` was run only on synthetic data. |

## Commits

1. `b820265` Track the exports app (it was silently ignored: `/Exports/` matched
   `exports/` on case-insensitive Windows) + review evidence.
2. `56f8071` Restore the CKD-EPI 2021 contract (male α −0.302, 0.1 rounding,
   version stamp). Fixes the three pre-existing lab test failures.
3. `d463eb1` Linkage + structured histopathology (all P1/P2 findings).
4. Print change (typography, isolated preview, English-only wording) —
   separate commit for visual review, with this report.

## Migrations (all additive; no column dropped, no value rewritten)

| App | Migration | Notes |
|---|---|---|
| patients | 0009 | Conditions become three-state (existing values unchanged); `condition_provenance`; pathology source/state/timestamp; diabetes "type not recorded". |
| pathology | 0009 | Lesion flags nullable (existing `False` kept); 0–100 validators; `PathologyReport`, `PathologyFinding`. |
| labs | 0002 | Supersession lineage, `is_current`, idempotency key (partial unique), provenance fields; default manager = current rows. |
| baseline | 0004, 0005 | Snapshot metadata, `hba1c_result`, `baseline_encounter`; 0005 only labels existing rows `legacy_mirror`. |
| encounters / clinical | 0004 / 0002 | `selected_vital`; VitalSign `measured_at`, `source`. |
| prescriptions | 0008 | Issued snapshot, hash version, `PrescriptionTestRequest`. |
| treatments | 0008 | Exposure `dose` widened to 120, `strength` added. |

## Finding-by-finding

| Review finding | What changed | Main files |
|---|---|---|
| P1 biopsy summaries vs adjudicated scores | One projection service with source link + state; final review wins over newer pending; working diagnosis separate with explicit audited adoption; finalization writes all panels; read-only pathology fields on the patient form; admin/API edits re-project via signals. | `pathology/services/projection.py`, `pathology/services/review.py`, `pathology/apps.py`, `clinic/forms.py`, `clinic/views.py` |
| P1 comorbidity correction / baseline | Three-state current state + per-field provenance on Patient; baseline snapshot taken once; audited `correct_baseline_snapshot`; legacy fallback only for never-recorded conditions and flagged. Rx prints a selection; record-owned items never carried from old slips. | `patients/models.py`, `patients/comorbidity.py`, `baseline/models.py` |
| P1 reasoning semantics | `labs/codes.py` (aliases, interpretation, per-test latest by explicit date policy); UPCR/UACR/24-h separate; biopsy features from findings; diagnosis expectations labelled as inferences in matched rules. | `knowledge/services.py`, `pathology/services/reasoning.py` |
| P1 API lab entry bypass | API, admin, FHIR import, baseline and results page all use `record_result`/`correct_result`; API update = supersede with reason; API delete refused. | `labs/services/results.py`, `api/serializers.py`, `labs/admin.py`, `fhir/import_fhir.py` |
| P1 strength vs dose | Separate dose + unit; `regimen_dose` drives reconciliation; legacy rows continue without spurious splits; no dose inferred for history. | `prescriptions/models.py`, `prescriptions/services/reconciliation.py`, form/view |
| P2 HbA1c two stores | Recorded as LabResult and linked; documented enrollment window; export reports value/date/source. | `labs/services/baseline.py`, `exports/services/dataset.py` |
| P2 duplicate lab entry | Per-form idempotency token; same-value same-date needs explicit repeat confirmation; existing results shown; per-field failures reported truthfully; nothing deduplicated in the database. | results page, baseline form |
| P2 vitals disconnected | VitalSign owns readings; encounter selects one; legacy columns are its projection; follow-up form and API create readings. | `encounters/services/vitals.py` |
| P2 diagnosis qualifiers | Exact qualifier map + curated legacy aliases (whole phrases only); FSGS contradictions rejected; unrelated panels need a coexisting diagnosis or reason; mixed lupus classes kept. | `pathology/diagnosis.py` |
| P2 investigations vs orders | Catalogue tests by id as structured requests; orders placed at finalization, linked to outstanding orders, retry-safe; print from requests. | `prescriptions/services/issue.py` |
| P2 next visit overwritten | Prescription shows the visit's selected date; one audited scheduling action; protocol visits untouched; reminders follow via the existing follow-up engine. | `encounters/services/scheduling.py` |
| P2 syndromes truncated | Primary + additional presentations; missing-field posts keep stored extras; explicit clear clears the scalar; scalar-only rows lifted. | `clinic/forms.py`, `baseline/models.py` |
| P2/P3 histopathology capacity | Report revisions, repeatable findings per section (incl. IF marker rows vs interpreted patterns, EM, special stains, Other), modality status, per-modality counts, validation, report page, amend/addendum, API, admin (read-only), findings export + dictionary, legacy conversion, one after-commit event. | `pathology/models.py`, `pathology/findings.py`, `pathology/services/report.py`, templates |
| Print readability | 12 pt patient-facing text (see table), point sizes for all routes, repeating headers, rows kept with tapers, word-preserving wrapping, isolated preview frame, print-hidden download button, English-only fixed wording (per request during implementation), issued snapshot, archived PDF never overwritten. | `prescriptions/templates/prescriptions/*.html`, `prescriptions/pdf.py`, `prescriptions/templatetags/rx_print.py` |
| Additional safety (eGFR) | Local CKD-EPI 2021 corrected; `decision/` calculator (which had copied the defect and pinned it in a test) now uses the same implementation. | `labs/services/egfr.py`, `decision/services.py` |

Also fixed in passing: `Patient.clean` referenced an unimported
`ValidationError`; the Vera prompt read a non-existent `gn_diagnosis`
attribute (the biopsy diagnosis never reached the prompt).

## Tests

Same environment as the review (temporary `BGDDR_DATA_DIR`, empty
`CELERY_BROKER_URL`, isolated test databases). Base = `e004959`.

| Run | Base | After |
|---|---|---|
| `python manage.py test` | 716 run, **3 failed** (the eGFR tests), 1 skipped | 716 run, **OK**, 1 skipped |
| `python -m pytest -q` (repo testpaths) | 557 passed | 650 passed, 0 failed |
| Review's focused set (3 files) | 57 passed | 57 passed |
| Review's module set (5 files) | 87 passed, 3 failed | 90 passed |
| Review probes (defects reproduced) | 13 "passed" | 13 failed = no defect reproduces |

Pre-existing, not introduced: running `knowledge/tests.py` together with the
other app `tests.py` modules under pytest fails 4 knowledge tests on the base
commit and on this branch alike (test-isolation issue); they pass under
`manage.py test` and alone. "MedEx sync failed" log lines are expected output
of a sync-failure test on both.

New corrected-behaviour tests:
`tests/test_entry_linkage_pathology.py`, `tests/test_entry_linkage_records.py`,
`tests/test_entry_linkage_prescriptions.py`, `tests/test_reconcile_linked_facts.py`,
`tests/test_egfr_reference.py`.

Existing tests changed because they pinned lossy semantics (each marked
in place with the reason): Type-2 inference from DM duration; `dose == strength`
(two tests); the defective male eGFR value in `decision/tests.py`; the print
size guard (now points); `tests/test_knowledge_integration.py` fixture, which
recorded ANCA/anti-GBM as a bare `1` and relied on presence meaning positive.

The 13 review probes now all fail — each at its defect assertion — meaning
none of the reproduced defects remains. They are kept unchanged as evidence.

## Print samples and visual QA

Generator: `docs/reviews/2026-09-27-entry-linkage/print_samples.py`
(synthetic patients; 1, 5, 10, 15 lines; long combination product name and
strength; dose different from strength; 6-line taper; long patient name;
stopped medications; draft and final). Rendered before (at `d463eb1`) and
after the print change.

| Element | Before | After |
|---|---:|---:|
| Body / medication values | 14.5 px (10.9 pt) | 12 pt |
| Drug/brand name | 15 px | 12.5 pt |
| Instructions / taper | 13 px | 12 pt |
| Advice, stop notes, visit note | 12.5 px | 12 pt |
| Identity, vitals, generic subtitle | 12.5 px | 10.5 pt |
| Table headings | 11 px | 10 pt |
| Audit/version footer | 10 px | 8.5 pt |

Visual QA (browser, A4 viewport 794×1123 CSS px = actual size at 96 dpi):
header columns separate cleanly; long names wrap; the taper stays with its
drug; combination strengths wrap between ingredients (a single word wider
than the column, "(Conventional", still breaks); draft watermark and banner
present; download button is screen-only. Found and fixed during QA: cramped
Route/Frequency headers, mid-word breaks, wrapped visit type.

xhtml2pdf fallback: page counts 1/2/2/3 for the 1/5/10/15-line samples (same
as before); after the English-only change no missing glyphs remain (the "℞",
the arrow and a zero-width break were replaced because the fallback's base
fonts lack them).

### Unsupported / unverified

- **WeasyPrint** is not usable in this environment (GTK libraries missing),
  so the primary PDF route was not rendered or inspected.
- **Bangla in the PDF fallback**: xhtml2pdf printed all Bangla as ■ boxes
  (before and after): no Bengali TTF is bundled at `BENGALI_FONT_PATH`, and
  xhtml2pdf cannot shape Bengali conjuncts even with a font. Fixed wording is
  now English, but clinician-typed Bangla (instructions/advice) will still not
  print through this fallback. Browser print uses system fonts and rendered
  Bangla correctly here.
- No physical print test; no in-app preview screenshot with a real login
  (covered by a server-rendered test instead).

## Reconciliation (dry run)

`python manage.py reconcile_linked_facts [--json out.json] [--apply]`.
Run only on synthetic legacy data: `reconcile_dryrun_synthetic.txt` (next to
this file). Unresolved by design in that sample: a legacy baseline-only
hypertension (needs clinician confirmation), a working diagnosis differing
from the re-projected pathology diagnosis (clinician adoption), two identical
albumin rows (duplicate or genuine repeat — decided by a person, nothing
deleted), and a male eGFR derived with the defective fallback (governed
re-derivation). `--apply` was tested for idempotence and non-destruction on a
copy of that data only. Run the dry run yourself on a copy of the live
database, review it, and decide before any `--apply`.

## Clinical terminology to confirm

- The finding vocabulary (`pathology/findings.py`) and report layout.
- Legacy diagnosis aliases (`pathology/diagnosis.py`), e.g. "FSGS" → FSGS
  family only; "Membranous nephropathy" → MN family with PLA2R status unknown.
- HbA1c enrollment window −90/+30 days around the baseline date.
- Diagnosis → expected-finding inferences used (labelled) by reasoning.
- "Type not recorded" diabetes state and its confirmation workflow.
