# Field ownership map

Maintained record of which model owns each clinical fact, and how every other
screen, export and consumer reuses it. Introduced with the 2026-09-27
entry-linkage work (`docs/CLAUDE_OPUS_ENTRY_LINKAGE_HISTOPATHOLOGY_PRINT_REVIEW_2026-09-27.md`).
Update this file whenever a field gains a new writer.

**Rule:** one owner writes a fact; everyone else reads it with its source and
date, or links to it. A second editable copy of the same fact is a defect.

| Concept | Owner (the one writer) | How others reuse it | Notes |
|---|---|---|---|
| Name, hospital ID, DOB, sex, contact | `Patient` (patient form, API, admin) | Read live on screens; frozen into `Prescription.issued_snapshot` at finalization | Hospital ID stays separate from `patient_id`. |
| Current comorbidities (11 conditions) | `Patient` fields, three-state (True / False / None) + `Patient.condition_provenance` | `patients.comorbidity.comorbidity_items()` for summary, prompts, Rx print choices | A `False` without a provenance stamp is a legacy default and reads as *not recorded*. Changes are stamped automatically in `Patient.save()`. |
| Enrollment comorbidity snapshot | `BaselineAssessment` columns, captured once at baseline creation (`comorbidity_snapshot_at/_source`) | Exports (enrollment characteristics) | Never rewritten by later saves. Correct only via `patients.comorbidity.correct_baseline_snapshot()` (reason required, audited). Pre-existing rows are labelled `legacy_mirror`. |
| Smoking | `Patient.smoking_status` (current) / `BaselineAssessment.smoking` (snapshot) | as above | |
| Diabetes type | `Patient.diabetes_status` | Baseline duration flags `unknown` type for confirmation | A DM duration no longer sets Type 2. |
| Working (clinical) diagnosis | `Patient.primary_diagnosis` (clinician) | Prescription diagnosis fallback (after the last finalized prescription's); cohort grouping | Prefilled once from pathology when empty; changed from pathology only by explicit **Adopt pathology diagnosis** (audited). |
| Pathology summary (biopsy dx, broad group, primary/secondary, MEST-C, ISN/RPS) | `pathology.services.projection.project_pathology()` → `Patient.*` + `pathology_source_biopsy` + `pathology_projection_state` | Read-only on the patient form once a biopsy exists; linked to its source biopsy | Selection: newest final (concordant/adjudicated) biopsy, else newest with a diagnosis (provisional). A newer pending biopsy never displaces a final one. Scores only when they belong to the diagnosis family. Runs from guided entry, review finalization, amendment, API and admin (model signals). |
| Biopsy procedure / specimen | `Biopsy` | Anchor for reports, scores, reviews, images | A repeat biopsy is a new `Biopsy`. |
| Adopted interpretation of a biopsy | `GNDiagnosis` + score panels (`IgANScore`, `LupusPathology`, `FSGSPathology`, `MembranousPathology`) | Projection, exports, reasoning | Finalized reads (`pathology.services.review._finalize`) write diagnosis **and** every applicable panel. |
| Report text, provenance, adequacy by modality, modality status, findings | `PathologyReport` revision + `PathologyFinding` rows (`pathology.services.report`) | Report detail page, API `/api/v1/pathology-reports/`, findings export, reasoning | Amendment/addendum = new revision superseding the old (kept). Legacy single-choice IF/EM converted by `reconcile_linked_facts --apply` as `origin=legacy`. |
| Local / central / adjudication reads | `PathologyReview` (one per role) | Concordance, kappa, report page | Disagreement stays visible; never merged. |
| Diagnosis qualifiers (FSGS variant, lupus class) | The diagnosis value, via `pathology.diagnosis.QUALIFIERS` (exact map); the panel asks only when the label does not state it | Entry form shows a stated qualifier read-only (`qualifier_table()`); contradiction = form error | Mixed III+V / IV+V preserved. No substring guessing. A variant never implies primary/secondary. |
| Primary / secondary (any diagnosis) | `GNDiagnosis.primary_secondary` — one control, on the diagnosis (2026-09-29) | `FSGSPathology.primary_secondary` is a projection (`pathology.diagnosis.project_fsgs_panel`), read-only in admin, not on the FSGS form | A label that states it ("FSGS - primary", "Membranous … secondary/associated") must agree; amendment and review finalization set it from the label (`sync_stated_primary_secondary`). Genetic / unknown are never forced into a binary. An old page's panel value fills a blank or must agree. |
| Crescents (present / %, count, Oxford C) | `Biopsy.crescents_present` (three-state) + `Biopsy.crescent_pct`; count on the report; C on `IgANScore` | Rules in `pathology.consistency` for the form, amendment, API (`BiopsySerializer.validate`) and admin (`Biopsy.clean`) | A positive % or count needs *present*; *present* cannot carry 0; unknown % stays blank. C0 = no crescents, C1/C2 = crescents seen; the C1/C2 boundary is not derived. IFTA / global sclerosis are shown beside MEST-C as evidence only. |
| Biopsy result category (diagnostic yield) | `Biopsy.result_category`, entered, never inferred | Registration gate (positive → registered, negative → excluded) | Checked against the diagnosis, adequacy and report status (`pathology.consistency.result_category_errors`): only labels that state GN / no GN are judged. Positive/negative need a final or preliminary report. |
| Laboratory results (incl. HbA1c, creatinine) | `LabResult` via `labs.services.results.record_result()` (results page, baseline form, API, admin, FHIR, reconciliation) | Trends, latest value, exports, reasoning | Idempotency key per submission; same-value same-day re-entry needs explicit "repeat" confirmation; corrections supersede (`correct_result`) and keep lineage; default manager returns current rows only (`LabResult.all_objects` for history). |
| Derived eGFR + `Patient.latest_egfr` | Derived by the lab service (CKD-EPI 2021, versioned) | Read-only cache on Patient | Re-derived when the creatinine is corrected. |
| Baseline HbA1c | The linked `LabResult` (`BaselineAssessment.hba1c_result`), else nearest result within −90/+30 days (`labs.services.baseline`) | Baseline form, exports (`hba1c`, `hba1c_date`, `hba1c_source`) | `BaselineAssessment.hba1c` is legacy only (not editable). |
| UACR / UPCR / 24-h protein | Separate `LabResult` tests | Reasoning keeps them as separate variables | Never interchangeable. |
| Visit BP / weight / pulse | `clinical.VitalSign` rows (several per visit) | `ClinicalEncounter.selected_vital` + projected `systolic_bp`/`diastolic_bp`/`weight_kg` (read-only projection) → print, reasoning | Follow-up form and API writes create a reading (`encounters.services.vitals`). Baseline BP is the enrollment measurement and is never rewritten by a visit. |
| Presenting syndromes | `BaselineAssessment.presentation_syndromes` (primary first, then additional) | Legacy scalar `presentation_syndrome` is a projection of the primary | Additional presentations survive unrelated edits; explicit clear clears the scalar. |
| Next appointment | `ClinicalEncounter.next_due_date` via `encounters.services.scheduling.set_next_visit()` | Prescription form (shows it), follow-up engine tasks/reminders, print | Research protocol windows (`ScheduledVisit`) are separate and untouched. |
| Investigations requested on a prescription | `PrescriptionTestRequest` (catalogue test ids) | At finalization → `LabOrderItem` (linked to an outstanding order at the same visit, else new) | Drafts never place orders. Non-catalogue tests stay as text. |
| Prescription diagnosis | `Prescription.diagnosis_text`, in that prescription's snapshot | New prescription prefill (`prescriptions.services.diagnosis_prefill`): last finalized prescription of the same patient (no later visit) → working diagnosis → blank, with its source shown | Editing it never changes older prescriptions, the working diagnosis or pathology. A newer draft is offered, not substituted; other recorded diagnoses are shown with **Use this**. Custom/legacy text is kept as its own option. |
| Printed comorbidities | `Prescription.comorbidities` = print selection from the patient record + prescription-only notes | Snapshot | Omitting one is not a clinical deletion; record-owned conditions are never carried from an old slip. |
| Product strength vs administered dose | `PrescriptionItem.strength` / `dose` + `dose_unit` | `regimen_dose` → reconciliation signature and `TreatmentExposure.dose` (+ `strength`) | Blank dose = one unit of the product per frequency slot. Legacy rows where dose == strength read as "not separately stated". |
| Issued prescription content | `Prescription.issued_snapshot` (+ v2 content hash) | Rendering of finalized prescriptions | Prescriptions finalized before 2026-09-27 have no snapshot; they render live with a visible notice and are never back-filled. v1 hashes unchanged. Archived PDFs are never overwritten. |
| Advice | `Prescription.advice` (patient instructions) / `ClinicalEncounter.advice` (visit note) | Both printed, labelled separately | |

## Consumers checked

- Clinical reasoning (`knowledge.services.extract_patient_features`):
  lab codes via `labs.codes` (interpretation, not presence; aliases; newest
  result per test by result → sample → entry date); biopsy features from
  structured findings (`pathology.services.reasoning`); diagnosis-derived
  expectations are `biopsy_inferred` and labelled as inferences in matched rules.
- Exports: pathology columns from the one selected biopsy
  (`pathology_diagnosis`, `pathology_biopsy_date`, `pathology_state`); the
  repeated findings are a separate child table (`?table=findings`,
  `export_dataset --table findings`).
- Events: one `pathology.report_changed` per biopsy aggregate, after commit.
