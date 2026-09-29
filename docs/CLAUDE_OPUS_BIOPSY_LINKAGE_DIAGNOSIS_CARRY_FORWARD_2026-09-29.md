# Claude Code Opus: biopsy field linkage and prescription diagnosis carry-forward

Date: 29 September 2026. Target: **GDES/BGDDR**, `E:\OneDrive\Project Claude\BGDDR\bgddr`.

## User request

Implement these two concrete corrections:

1. On `http://192.168.7.55:8080/patients/1/biopsy/`, logically link related variables and remove duplicate/near-duplicate entry controls.
2. On `http://192.168.7.55:8080/patients/1/prescription/`, carry the diagnosis from the previous entry into the next prescription.

Apply to all patients through the existing routes, not just patient 1. This is a source-verified implementation handoff; application changes have not been made in this review.

## Evidence and scope

The supplied server identifies itself as GDES. Opening the biopsy URL redirected to sign-in, so the deployed authenticated form and deployed revision were not verified. Local `clinic/urls.py:18,24` matches both requested routes.

Reviewed local HEAD: `e004959c026d810a82aa34b03a4cb672d6fb4320`. Existing staged/unstaged work in `analytics/services/prediction.py` and `analytics/tests/`, and earlier untracked review artifacts, were preserved. These findings concern the files currently in the checkout.

Fresh isolated SQLite evidence: **24 existing lupus-linkage tests passed; 4 new required-behavior probes failed**, in 12.94 seconds. These four failures are reproducible defects:

| Probe | Current result |
|---|---|
| Previous finalized prescription says `FSGS - primary`, Patient main diagnosis says `IgA nephropathy` | New prescription prefill is `IgA nephropathy`; previous prescription diagnosis is ignored. |
| Diagnosis/classification says FSGS primary, FSGS panel says secondary | POST succeeds and stores the conflict. |
| Crescents checkbox omitted, crescent percentage 25 | POST succeeds with `crescents_present=False` and `crescent_pct=25`. |
| Global sclerosis 150%, IFTA 120% | POST succeeds and stores both impossible percentages. |

Probe and log: `docs/reviews/2026-09-29-biopsy-prescription/probes.py` and `results.log`. Domain-event dispatch was disabled for these new probes to isolate persistence and avoid integrations; asynchronous projection/refresh was not tested. No real patient was edited. No full GDES suite, PostgreSQL, live authenticated journey, or clinical rule validation was performed here.

This handoff refines the biopsy and diagnosis work from `docs/CLAUDE_OPUS_ENTRY_LINKAGE_HISTOPATHOLOGY_PRINT_REVIEW_2026-09-27.md`. Keep its field-ownership, repeatable findings, review-provenance, and immutable-print requirements; do not repeat its broader redesign before fixing these pages.

## A. Biopsy: one entry location per fact, with explicit links

### Current owners and required changes

| Current fields | Required ownership and screen behavior |
|---|---|
| `GNDiagnosis.diagnosis`, `broad_group`, `pathogenesis_group`, `primary_secondary`, `secondary_cause` | The diagnosis record owns classification. Use a reviewed structured mapping to propose classifications where unambiguous. Render derived classifications read-only, with their source. Keep genuinely independent/uncertain classifications editable, and flag incompatible combinations on the server. Do not use loose substring matching as a new clinical classifier. |
| FSGS diagnosis wording, `GNDiagnosis.primary_secondary`, `FSGSPathology.primary_secondary` | One primary/secondary control. Remove the FSGS panel's competing writer and project the canonical value for compatibility. A diagnosis explicitly stating primary/secondary must agree. Preserve genetic/uncertain states; do not force them into a binary choice. |
| FSGS diagnosis wording and `FSGSPathology.variant` | State an explicit variant once and derive its displayed label wherever repeated. Etiology and morphology remain separate facts: a variant alone must not imply primary/secondary status. |
| Lupus class embedded in diagnosis and `LupusPathology.isn_rps_class` | Extend the existing `pathology/lupus.py` reconciliation. For qualified diagnoses, show the class as derived text instead of a second selector. For an unqualified lupus diagnosis, one class selector may complete it. Preserve mixed classes. All write paths must agree, including review/adjudication. |
| `crescents_present`, `crescent_pct`, Oxford `C` | Use one coherent lesion section with explicit present/absent/unknown/not assessed state and percentage/count evidence. Positive percentage cannot coexist with absent. Unknown percentage must not become zero. Oxford C remains a classification tied to its applicable report criteria; only derive it through an approved rule with sufficient inputs. |
| `ifta_pct` and Oxford `T`; global sclerosis and Oxford `S` | Link their evidence and flag relevant inconsistencies. Do not remove a field merely because it is related: report percentage and a disease-specific grade are not automatically interchangeable; global and segmental sclerosis are distinct. No guessed score thresholds. |
| IF pattern and EM findings | Keep IF and EM separate, with test-performance status. Support multiple observations per report, as specified in the earlier handoff. Use shared structured finding rows for their consumers, retaining original text. A single dropdown must not discard coexisting findings. |
| Membranous diagnosis qualifiers and tissue PLA2R/THSD7A results | Link to the actual test/source/specimen. Do not treat a serum antibody result and tissue staining as duplicate observations or infer an observed stain from a diagnosis label. |
| Patient pathology summaries (`biopsy_diagnosis`, `gn_broad_group`, `gn_primary_secondary`, `oxford_mestc`, `isn_rps_class`) | Read-only source-linked projections of the selected biopsy/review. Keep the patient's working clinical diagnosis distinct. Do not fill-once and leave stale, and do not replace an accepted conclusion with a newer pending report automatically. |

### Concrete implementation locations

- `clinic/forms.py:323-389`: biopsy, diagnosis and disease-specific forms currently expose almost every model field independently. Replace competing inputs with shared controls and derived display.
- `templates/clinic/biopsy_form.html:26-76`: loops render all diagnosis/core fields and all optional score blocks. Move to explicit sections: report identity/adequacy; observed findings; diagnosis/classification; applicable disease scores; review/source.
- `clinic/views.py:659-692`: existing lupus reconciliation is a useful pattern to extend.
- `clinic/views.py:736-805`: save handler treats any changed score form as active and saves models sequentially. Introduce a single atomic pathology command, with cross-form validation before writing. Preserve typed values on error.
- `clinic/views.py:695-732`: `_sync_biopsy_to_patient` fills only blank Patient fields and can leave old summaries. Replace with the source-linked projection authority defined in the earlier review.
- `pathology/models.py:58-65`: add 0–100 percentage validation and appropriate database constraints, plus nonnegative/count-consistency rules. Unknown must remain representable.
- `pathology/models.py:118-187`: diagnosis and disease-panel classification must share one owner. Update API/admin/review consumers, not only HTML.

Show relevant disease panels from the selected diagnosis and explicit additional diagnoses. If changing the diagnosis makes already-entered scores inapplicable, explain the conflict and require explicit resolution before saving; hiding a panel must not silently delete or silently retain incompatible data. Preserve genuine mixed pathology and independent local/central/adjudication reads.

Do not infer a positive/negative biopsy result category or registration transition from incomplete form fields. Validate report adequacy, diagnosis and diagnostic-yield combinations using the programme's approved definitions, because this route currently changes registry membership based on `result_category`.

### Migration and acceptance

1. Inventory conflicting legacy pairs and invalid percentages. Retain original values with provenance; do not overwrite them by precedence without review.
2. Establish the canonical owner and a compatibility projection. Remove redundant editable controls first; remove storage only after API, exports, feature extraction and adjudication have migrated.
3. Tests must cover the three reproduced contradictions, agreeing values, all unknown/not-done states, mixed lupus classes, FSGS variants, diagnosis changes, repeatable IF/EM findings, and transaction rollback on a failed score save.
4. Verify biopsy -> review/adjudication -> patient summary -> prescription suggestion -> clinical features/export. A form-only fix is insufficient.
5. Re-run the 24 lupus tests and add an authenticated browser check showing that one edit updates the related displays and cannot save contradictory values.

## B. Carry diagnosis into the next prescription

**Root cause:** `clinic/views.py:1044` already retrieves the previous prescription for medicines/advice, but `:1142` supplies `default_diagnosis` solely from `patient.primary_diagnosis`. The POST at `:952` saves the entered diagnosis only to the prescription. Consequently a clinician's previous prescription diagnosis is never the next default. `templates/clinic/prescription_form.html:33-37` also offers only catalogued choices, so a legacy/custom diagnosis can render as blank even when supplied.

### Required behavior

- Preserve a bound form's submitted diagnosis, including an intentional clear, when validation fails. Never reapply defaults over current edits.
- When resuming an existing draft, use that draft's saved diagnosis. Make draft resumption explicit; do not silently substitute an unrelated incomplete draft for an issued prescription.
- For a new prescription, prefill the most recent applicable prior finalized prescription's nonempty diagnosis for the same patient, ordered by clinical encounter date and deterministic version/id ties. Exclude later encounters when entering a historical visit.
- If a more recent saved draft exists, offer to resume that draft with its diagnosis. If there is no applicable prior prescription diagnosis, fall back to the patient's working diagnosis; otherwise leave unknown visibly blank.
- Keep the prefill editable. Display a small source label such as “Carried from prescription dated …”; carry-forward is a convenience, not an assertion that the diagnosis was newly confirmed today.
- Preserve custom/legacy or combined diagnosis text even if it is not in `SPECIFIC_GN_DIAGNOSIS`: include its actual value in the control or provide a supported free-text option. Never lose it through a dropdown mismatch.
- Save the accepted diagnosis into the new prescription's own snapshot. Changing it there must not rewrite prior prescriptions or silently change the pathology diagnosis. If adopting it as the patient's working diagnosis is offered, use an explicit, separate action with provenance.
- If pathology review or the patient's working diagnosis changed since the previous prescription, show the newer fact alongside the carried text for clinician review; do not silently replace either source.

Do not change medication carry-forward while fixing the diagnosis. Reuse prescription creation/finalization and snapshot mechanisms.

### Acceptance cases

1. The diagnosis-prefill probe passes: a previous prescription's FSGS diagnosis survives into the next form even when Patient still carries an older IgA diagnosis.
2. Resumed draft, first-ever prescription, blank previous diagnosis, and a previous custom diagnosis all preserve the intended source/value.
3. A new clinician edit wins over the prefill and survives a validation error elsewhere.
4. Another patient's prescription and a future-dated encounter cannot provide the diagnosis.
5. Saving/finalizing the next prescription prints the accepted diagnosis; an old prescription's diagnosis, hash and reprint remain unchanged.

## Reproduction and handback

From the GDES root, set `BGDDR_DATA_DIR` to a disposable local directory, then run:

```powershell
python -m pytest docs/reviews/2026-09-29-biopsy-prescription/probes.py tests/test_lupus_class_single_source.py -q -s
```

The four new probes assert required behavior and currently fail. Promote corrected behavior into permanent tests. Return a concise correction report with changed files, the field-owner mapping, migration/conflict handling, test results, and authenticated browser evidence. Do not claim these two live pages are fixed until the correct GDES build has actually been deployed and checked.
