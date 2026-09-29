## GDES 7.4.0

A feature release. It updates the database (12 migrations); the update takes a
snapshot first and restores it automatically if anything fails, so no data can
be lost. The first start after updating takes a little longer.

### Prescriptions
- **Printed prescription fits the page.** Columns no longer overlap or run off
  the right edge of the PDF. Patient-facing text is larger (12 pt drug names,
  11 pt regimen); fixed wording prints in English.
- **Steroid taper templates.** Each steroid row has an *Insert template*
  dropdown, managed in *Admin → Prescriptions → Taper templates*. Seven
  starting templates are added; the four dose ladders are examples — check and
  edit them before use.
- **The diagnosis carries forward.** A new prescription starts from the last
  finalized prescription's diagnosis (else the working diagnosis), labelled
  with its source and always editable. A newer unfinished draft is offered,
  not substituted.
- **Finalized prescriptions are frozen.** What was issued is stored and
  reprinted exactly; strength and dose are separate fields; investigations
  become lab orders only when the prescription is finalized.

### Biopsy and pathology
- **Structured renal biopsy reports** with any number of findings (light
  microscopy, IF markers and patterns, EM, special stains), amendments and
  addenda that keep earlier revisions.
- **One place per fact.** Primary/secondary is recorded once, on the
  diagnosis; a lupus class or FSGS variant named by the diagnosis is shown
  read-only. Contradictions are refused with a message instead of being saved:
  crescent percentage vs present/absent, Oxford C vs crescents, and the
  positive/negative result vs the diagnosis and report status.
- **Patient pathology summary follows the selected biopsy** and shows its
  source. The working diagnosis changes only when you choose *Adopt
  pathology diagnosis*.

### Records and results
- Comorbidities record *yes / no / not recorded* separately, with where each
  came from. Lab results are recorded once through one service (repeat entry
  needs confirmation; corrections keep the original). Visit blood pressure and
  weight are measurement records. The eGFR calculation for men is corrected
  (CKD-EPI 2021).

### Security
- Content-security policy headers and login rate limiting.

### After updating
- Existing records are not rewritten. A clinic administrator can list older
  records that need review (for example biopsy summaries saved before this
  release) with `reconcile_linked_facts`; it changes nothing unless run with
  `--apply`.
- A biopsy saved earlier with contradictory values must be corrected before it
  can be edited again.
