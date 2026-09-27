# Claude Code Opus: Link Repeated Entry, Expand Renal Histopathology, Improve Prescription Print

Date: 2026-09-27

Workspace: `E:\OneDrive\Project Claude\BGDDR\bgddr`

## Implementation Request

Implement the user's three requests in the existing BGDDR/GDES application:

1. Link identical clinical facts across forms and remove repeated manual entry.
2. Allow a renal histopathology report to contain multiple findings and additional details.
3. Make printed prescriptions modestly larger and easier to read.

The central problem is competing writable records, not merely repeated labels. A value entered once must reach the patient summary, visit, prescription, clinical reasoning, research export, and API through an explicit ownership rule. Preserve separate dates, specimens, clinical interpretations, independent pathology reads, and issued prescription history.

This handoff contains a source review and reproducible synthetic evidence. Application changes have NOT been implemented. Continue from the current working files; do not replace the application or repeat work already present.

## Evidence And Boundaries

- Reviewed guided forms, templates and save handlers; patient/baseline/encounter/clinical models; pathology models and review services; laboratory services and API serializers; prescription creation, reconciliation, rendering and finalization; feature extraction, exports, scheduling, and relevant audit/event wiring.
- HEAD resolved to `e004959c026d810a82aa34b03a4cb672d6fb4320`. `git status --short` failed with `fatal: .git/index: unable to map index file: Invalid argument`. Findings concern files read in the working directory; a clean checkout or an exact match to HEAD cannot be claimed. Do not reset or replace the index as part of this feature work without accounting for existing changes.
- Existing focused tests: **57 passed**, 5 warnings, 12.59 seconds, across `tests/test_comorbidity_carry_forward.py`, `tests/test_lupus_class_single_source.py`, and `tests/test_medication_single_source.py`.
- Additional existing module tests: **87 passed, 3 failed**, 11 warnings, 4 subtests passed, 19.48 seconds, across `baseline/tests.py`, `labs/tests.py`, `pathology/tests.py`, `prescriptions/tests.py`, and `exports/tests.py`. See the failure details below.
- Review probes: **13 passed**, 7 warnings, 6.39 seconds. Here a pass means the suspected undesirable behavior was reproduced, NOT that the behavior is correct. File: `docs/reviews/2026-09-27-entry-linkage/review_probes.py`.
- Tests used Django's isolated test database and a temporary `BGDDR_DATA_DIR`. The 13 probes disable domain-event dispatch to isolate persistence/feature extraction and avoid integrations. Existing tests ran with their normal event handling. Neither set establishes end-to-end asynchronous refresh correctness.
- No live patient records were inspected or migrated. No authenticated browser journey, visual PDF inspection, physical print test, packaged desktop build, PostgreSQL concurrency test, or full test suite was completed. Screen findings are from templates and server-rendered test responses.

## Findings, In Priority Order

### P1: Biopsy summaries and adjudicated scores can contradict each other

**Reproduced.** `clinic/views.py:695` only copies pathology values when the corresponding Patient field is empty. Enter an IgA biopsy, then a later minimal-change biopsy: the latest biopsy changes, while both Patient diagnosis strings remain IgA. The source review also shows that `PatientForm` makes these supposedly synchronized histology fields editable once a biopsy or an existing value is present (`clinic/forms.py:122`, `:159`).

**Reproduced.** `pathology/services/review.py:87` finalizes `GNDiagnosis` and sometimes `IgANScore`, but not `LupusPathology`, `FSGSPathology`, or Patient summaries. A class III biopsy adjudicated to class IV ends with final diagnosis IV, lupus score III, and Patient ISN/RPS III.

Consequences: prescription defaults use Patient diagnosis (`clinic/views.py:1145` area); cohort grouping uses Patient diagnosis (`analytics/services/cohort.py:40`); exports take Patient primary diagnosis and scores from the latest biopsy (`exports/services/dataset.py:94`, `:130`). One exported row can combine incompatible authorities.

**Required:** distinguish working clinical diagnosis from pathology diagnosis. Add explicit source-biopsy/source-review linkage for pathology projections. Use one projection service for guided entry, amendment, review finalization, API and admin. Define the selected biopsy and review state rather than blindly choosing the last inserted row. A newer pending biopsy must not silently replace an accepted final interpretation; show it as pending. Permit explicit clinician adoption of a pathology conclusion into the working diagnosis. Show pathology-derived summaries read-only with a link to their source.

### P1: Existing comorbidity consolidation cannot represent a correction or a stable baseline

**Reproduced.** `patients/comorbidity.py:75` skips False, and `:100` ORs current Patient flags with baseline flags. A hypertension flag corrected to False still appears as hypertension if baseline was True. Separately, a new current malignancy flag is copied into the old baseline when an unrelated baseline note is saved (`baseline/models.py:119`, `:135`).

The current design simultaneously treats baseline as a historical snapshot and a live mirror. Exports read baseline flags (`exports/services/dataset.py:107`), while current summaries merge both. This can leave exports stale or retrospectively change enrollment characteristics.

**Required:** Patient owns current comorbidity state with explicit present/absent/unknown semantics and correction provenance. Baseline owns an enrollment snapshot with date and source. Stop recurring two-way fallback/mirroring once a legacy value has been reconciled. A current change must not rewrite baseline. An explicit correction of the baseline must be a separate audited action. Preserve old raw Boolean values; do not declare every historical False to be a verified negative.

Prescription comorbidities remain another editable checklist/free-text copy (`clinic/views.py:953`, `:1117`); the previous Rx is unioned into current prefill. Separate current structured conditions, intentional print inclusion choices, and the immutable issued snapshot. A condition omitted from a printout is not a clinical deletion; a condition added while prescribing must either update the shared record through the proper action or be clearly marked prescription-only.

### P1: Linked observations lose their actual meaning in clinical reasoning

**Reproduced.** A Negative ANCA result emits the `anca` feature; a Positive `anti_dsdna` result does not emit `anaDsDna`. `knowledge/services.py:156` checks presence of a test row without its result; `:168` uses inconsistent aliases, including mixed-case `anti_dsDNA` after lowercasing the input.

**Reproduced.** Selecting the existing EM option `foot_process_effacement` does not emit `podocyteEffacement`, because `knowledge/services.py:204` searches for the substring `podocyte`.

**Source-inspected additional issue:** biopsy features are inferred from the diagnosis label (`knowledge/services.py:187`), including an IF finding of full-house from a lupus diagnosis, rather than necessarily being observed findings. IF options and future multiple findings will be ineffective unless this consumer is updated.

**Required:** centralize code/alias mapping; retain numeric value, interpretation, unit, sample/report dates and provenance. Interpret positive/negative/equivocal/not-performed explicitly. Read structured observed biopsy findings. Keep diagnosis-derived expectations separate and labeled as inferences. Select observations by an explicit date policy per test; the current global last-20 loop ordered by nullable sample date is not a suitable canonical current-result selector. Do not collapse urinary albumin, total protein, ACR, PCR and 24-hour protein into interchangeable variables.

### P1: API lab entry bypasses the existing derivation service

**Reproduced at serializer level.** Saving creatinine through `api/serializers.py:LabResultSerializer` creates no eGFR result and does not update Patient eGFR. `api/views.py:LabResultViewSet` uses ordinary model persistence through the shared viewset. The guided pages call `labs/services/results.py:56` instead.

**Required:** one validated result-recording/correction service across guided entry, API, import and admin. Preserve the existing creatinine-to-versioned-eGFR derivation and cache refresh. Corrections must supersede prior observations and their derivations with lineage, not overwrite measured history. Audit the FHIR and admin paths explicitly when adapting them. Test full persistence and downstream consumers, not only the helper.

### P1: Near-duplicate medication fields are already being conflated

**Source-inspected.** `clinic/views.py:968` saves `dose=strength_val`. `PrescriptionItem` still has separate strength and dose fields (`prescriptions/models.py:115` onward), and reconciliation uses dose in the signature. The print template renders strength, not a separate dose (`prescriptions/templates/prescriptions/prescription.html:135`).

Product strength and administered dose are different facts. For example, a 5 mg tablet and two tablets per administration must remain expressible without changing the product strength. Frequency and timing are also distinct; neither substitutes for dose quantity.

**Required:** retain and correctly label product strength, dose/quantity, dose unit, route, frequency, duration and taper. Keep routine entry short through sensible product defaults and a compact administration control. Do not infer a historical dose from ambiguous strings during migration. Preserve lossless clinician-authored schedules. Test print and exposure reconciliation with dose changes at unchanged product strength. This is a functional correction, separate from the font-size change.

### P2: HbA1c has two unrelated writable stores

**Reproduced through the baseline route.** Baseline HbA1c 8.2 creates no `LabResult`. A same-date HbA1c result of 7.1 can coexist, and export still reports 8.2. Locations: `baseline/models.py:71`; `templates/clinic/baseline_form.html:50` area; `clinic/forms.py:588`; `exports/services/dataset.py:107`.

**Required:** record HbA1c through the same laboratory service as other results. The baseline view selects/links the actual baseline observation using a documented enrollment window and displays its date; it must not simply substitute today's latest result. Preserve legacy values as sourced legacy observations when their date/unit is known; flag ambiguity and conflicts for review.

### P2: Equivalent lab entry paths can duplicate a measurement

**Reproduced.** Submitting the same albumin result form twice creates two rows. `labs/services/results.py:64` always inserts. Baseline inline lab fields are not loaded with previously recorded observations on edit; `_save_labs` runs again for each supplied value (`clinic/views.py:75`, `:485`). Separate forms can therefore enter the same source report again.

**Required:** share the result-entry component and command service. Show existing linked results with date/source and explicit Add new / Correct actions. Add request idempotency and source-report/specimen identity where available. Do NOT add uniqueness on patient+test+date or delete identical numeric results: legitimate repeat measurements can have the same value on the same day. Historical potential duplicates require a report and explicit resolution. `_save_labs` and standalone entry also swallow individual failures; show field-level failures and truthful partial-save state so users do not retry the whole panel blindly.

### P2: Visit observations and VitalSign records are disconnected

**Reproduced.** A VitalSign of 180/100 linked to an encounter leaves `ClinicalEncounter.systolic_bp` empty; feature extraction does not see that measurement. Owners currently overlap across `baseline/models.py:63`, `encounters/models.py:39`, `clinical/models.py:28`, and `clinical/serializers.py`. Print reads the encounter fields.

**Required:** use existing VitalSign rows as the dated measurement owner and an explicit selected-measurement link for each encounter's display/print. Adapt legacy encounter scalars as compatibility projections. Link a baseline encounter/measurement when it is actually the same visit. Preserve multiple measurements, their order and recorded times; do not merge baseline BP with a later visit BP merely because labels match. Expose this shared component within the existing forms, without creating a second visit entry workflow.

### P2: Diagnosis labels repeat classification fields without enforcing agreement

**Reproduced.** A biopsy with diagnosis `FSGS - primary`, generic primary/secondary `primary`, and FSGS-panel primary/secondary `secondary` saves successfully. Other FSGS choices encode variant while `FSGSPathology.variant` independently asks it again. Locations: `patients/choices.py:147`, `pathology/models.py:116`, `:176`, `clinic/views.py:752`.

Lupus diagnosis/class reconciliation already exists at `pathology/lupus.py` and `clinic/views.py:659`; preserve and extend that pattern beyond the one guided path. Do not remove the existing mixed III+V and IV+V support.

**Required:** one structured diagnosis family with qualifiers for class/variant/primary-secondary where appropriate. An existing diagnosis choice may prefill the corresponding qualifier, but contradictory entry must be rejected or explicitly reconciled. Use stable code mappings with legacy aliases; do not derive clinical classifications by substring alone. Broad group, pathogenesis group, cohort, etiology and specific diagnosis are related but not universal synonyms. Auto-suggest only validated mappings, retain mixed/uncertain cases and an explained override.

### P2: Prescribed investigations are not linked to lab orders

**Reproduced.** Selecting Serum creatinine on a prescription writes only `investigations_advised`; it creates no `LabOrder`. Structured orders are entered separately through `clinic/views.py:2152`. Prescription entry joins display names into text (`:937`), while the template submits test names, not stable test IDs (`templates/clinic/prescription_form.html:62`).

**Required:** select tests once from the catalog; link draft prescription requests to the encounter's intended orders, and commit actual orders at the defined clinician acceptance/finalization step. Saving an unissued draft must not silently place an order. Print from the accepted linked orders. Preserve genuine non-catalog investigations as typed text. Prevent double creation on retry, include existing outstanding orders, and distinguish repeat requests from duplicates. Attach returned results to order items when known.

### P2: Prescription entry can replace an already chosen follow-up date

**Reproduced.** The prescription GET always supplies today + four weeks (`clinic/views.py:1036`) even when the encounter already has a next date. Submitting it writes that default onto the encounter (`:944`). The same date is requested on `FollowupForm`.

**Required:** show the encounter's selected next visit by default; editing it from either screen calls one scheduling action. Keep protocol target dates/windows, a booked appointment, and a clinician recommendation distinct. Link them through `scheduling.ScheduledVisit` / `followup.FollowUpTask` as appropriate, so reminders and the printed date agree about the selected appointment. Do not overwrite independent research protocol visits. Record the actor and reason for a changed appointment.

### P2: Simplifying a multi-value field already discards stored data

**Reproduced.** A baseline containing `[nephrotic, aki]` is loaded as only the first value (`clinic/forms.py:249`) and a routine save replaces it with a one-element list (`:276`). The legacy scalar is a further lossy mapping (`baseline/models.py:108` onward).

**Required:** retain a primary presenting syndrome plus additional presentations where already recorded or clinically needed. Do not silently truncate legacy lists. Keep symptoms, measured signs, clinician syndromes and automatically classified syndromes separate, with reusable observations and clear provenance. Explicitly handle clearing so a blank canonical value does not leave a stale legacy scalar.

### P2/P3: Histopathology capacity and prescription readability

**Source-inspected user-facing limitations.** `Biopsy.if_pattern` and `em_findings` are single-choice fields (`pathology/models.py:68`, `:85`; `clinic/forms.py:323`). A global notes field exists, but cannot hold several separately coded EM/IF findings for retrieval or analysis. Most lesion Booleans default to False, so unassessed and absent cannot be distinguished. Percentage fields have no explicit 0-100 validators. Biopsy detail from the patient page goes to the admin (`templates/clinic/patient_detail.html:1433`), rather than a full clinical report view.

Print body is 14.5 px (about 10.9 pt), drug name 15 px (11.25 pt), instructions/tapers 13 px (9.75 pt), and advice 12.5 px (9.4 pt). An earlier comment says typography was enlarged; the actual sizes still leave patient instructions small. Detailed implementation requirements follow.

## Field Ownership And Linkage Map

Use this inventory as the implementation checklist. "Reuse" means display or prefill from the owner with source/date, not another independently saved value.

| Concept | Current entry/storage | Target owner and treatment |
|---|---|---|
| Name, hospital ID, DOB, sex, contact | Patient form, API, admin | Patient; reuse in every visit and print snapshot. Keep hospital identifier separate from registry ID. |
| Enrollment date / registration date | Patient / GN registration action | Distinct events; label explicitly. Link baseline encounter to enrollment rather than forcing dates equal. |
| Current comorbidities and smoking | Patient, legacy baseline, Rx text | Explicit current state on Patient; dated baseline snapshot; Rx inclusion/snapshot. |
| Diabetes type and duration | Patient status / baseline duration | Linked but distinct. Duration must not silently set type 2 (`baseline/models.py:140`). Preserve unknown type and clinician confirmation. |
| Infection history and viral serology | Patient chronic infection/HBV/HIV; labs | Distinct condition history and dated assay evidence. Link results to clinician review; a single test does not automatically establish all chronic infection facts. |
| Retinopathy and fundoscopy | Patient flag / baseline exam | Condition versus dated examination and grade. Link supported findings; preserve unknown and not assessed. |
| Working diagnosis | Patient / prescription diagnosis | Clinician-owned diagnosis linked to supporting evidence; issued prescription stores the chosen wording. |
| Biopsy diagnosis and disease scores | GNDiagnosis, score panels, Patient strings, reviews | Biopsy/report-specific interpretations; selected final review projects typed scores and read-only summaries. |
| Local / central / adjudication reads | PathologyReview | Keep independent; never deduplicate away disagreement or overwrite a reviewer from another read. |
| Cohort / broad group / pathogenesis / etiology | Patient and GNDiagnosis dropdowns | Related classification axes; versioned suggestions and consistency rules, not forced equality. |
| Systolic/diastolic BP, weight, height, pulse | Baseline, encounter, VitalSign | Dated measurement records with selected encounter and baseline links. BMI is derived with source measurements. |
| Oedema grade / oedema symptom | Baseline, visit, symptom list | Same-observation UI coordination; severity and reported symptom retain their different meanings. |
| Presenting syndrome / symptoms / classified syndrome | Baseline JSON+scalar, ClinicalAssessment | Primary and additional clinician presentations; derived classification separately labeled. |
| RBC casts / active sediment | Baseline checkbox, potential lab observations | Link microscopy evidence; active sediment is broader than RBC casts and must not be equated with it. |
| HbA1c | Baseline scalar / LabResult | Dated LabResult; baseline references the appropriate historical result. |
| Creatinine and derived eGFR | Inline labs / results / API / Patient cache | LabResult + derived lineage; one recording service; Patient cache is read-only. |
| UACR, UPCR, 24-h urine protein | LabResult | Separate measurements and units; do not deduplicate by approximate clinical meaning. |
| Serum anti-PLA2R / tissue PLA2R | LabResult / MembranousPathology | Separate specimen/assay facts; link in the report display but never force agreement. |
| Lab investigation requests | Rx text / LabOrderItem | Structured accepted requests linked to an encounter; print snapshot from those requests. |
| Existing medication and newly prescribed medication | TreatmentExposure / PrescriptionItem | Preserve external medication entry and finalization/reconciliation; share current medication display. |
| Product strength / administered dose | Currently copied together | Distinct typed facts; both available to print and reconciliation. |
| Advice | Encounter advice / prescription advice | Separate visit note from patient instructions; offer explicit reuse rather than retyping or concatenating duplicates. |
| Next visit | Encounter / Rx date / schedules / tasks | Shared selected appointment with distinct protocol recommendation/window metadata. |
| Clinician response / calculated remission | Encounter / PatientOutcome | Preserve independent assessments, dates, definitions and disagreements. |
| Phase / relapse episode / clinical event | Patient, encounter, relapse, event | Workflow service owns projections. Keep event/episode identity; do not ask the same relapse twice. |

Preserve useful work already implemented: baseline no longer asks the eleven comorbidity checkboxes; free-text drug history is retained read-only with structured medication carry-forward; follow-up no longer asks the inline lab panel; lupus class reconciliation exists; panel/custom lab order selections are deduplicated by test ID; prescription reconciliation already maintains treatment exposure episodes. Extend these authorities instead of adding parallel ones.

## Renal Histopathology Implementation

### Data And Workflow

Keep `Biopsy` as the procedure/specimen anchor and the existing disease-specific score models. Add a versioned report/interpretation layer for the local, central and adjudication reads, with structured findings attached to a particular report revision. Use a child finding model for repeatable descriptors and marker results; use typed fields for existing high-value scores/counts. Avoid a single unvalidated JSON blob or a comma-separated multi-select string.

Record report identifier, reporting laboratory/pathologist, specimen date, report date, native/transplant context, modality availability, and original report text. Keep existing `BiopsyImage` consent behavior for image attachments. Add a patient-facing-within-the-clinical-app report detail view and an audited amend/addendum action; a repeat biopsy is a new procedure, not a replacement of the earlier one. Preserve independent reviewer findings and disagreements.

Provide an **Add finding** action in each relevant section, allowing multiple coexisting findings, an optional typed severity/extent/site, and free-text elaboration. Permit unknown or unusual findings as Other + description without forcing a false coded diagnosis. Make additional fields optional unless needed for the selected report state. Draft, inadequate and pending reports must be recordable without inventing a definite GN diagnosis.

### Initial Capture Set

These are proposed capture fields, not automatic diagnostic rules. Have the clinical/pathology owner validate the terminology and report layout during acceptance.

| Section | Capture requirements |
|---|---|
| Specimen/adequacy | Cortex/medulla and number of cores where supplied; total glomeruli by modality where supplied; global and segmental sclerosis counts; report-specific adequacy and limitations. Do not add counts across modalities as if they were the same glomeruli. |
| Light microscopy: glomerular | Multiple findings for mesangial/endocapillary hypercellularity, segmental/global sclerosis, necrosis, cellular/fibrocellular/fibrous crescents, capillary-wall thickening/spikes/double contours, nodular lesions, thrombi; Other + narrative. |
| Tubulointerstitial | IFTA, tubular atrophy and interstitial fibrosis where separately reported; inflammation, acute tubular injury, casts and other lesions. Link overlapping summary measures without replacing distinct reported measurements. |
| Vessels | Arteriosclerosis, arteriolar hyalinosis, vascular inflammation and thrombotic microangiopathy features; site/extent and narrative. |
| IF/IHC | Repeatable marker rows for IgG, IgA, IgM, C3, C1q, kappa, lambda and fibrin/fibrinogen; additional markers as needed. Each row supports intensity, distribution, compartment and pattern. Keep observed marker results distinct from interpreted patterns such as full-house or pauci-immune. |
| EM | Multiple deposit locations (mesangial, subendothelial, subepithelial, intramembranous), foot-process effacement and extent if reported, GBM thickness/architecture, organized deposits, tubuloreticular inclusions and other findings; supporting narrative. |
| Special stains / disease scores | Reuse current MEST-C, lupus class/activity/chronicity, FSGS qualifier and MN antigen/stage models; allow additional reported special stains such as Congo red or DNAJB9 through typed repeatable findings. Do not auto-compute a disease score from incomplete descriptors. |
| Conclusion | Primary pathological diagnosis, additional/coexisting diagnosis where needed, comment, limitations, review state and signature/date provenance. Keep DKD + GN representable. |

For each modality/marker, distinguish not done, unavailable, pending, inadequate, and performed. Within performed findings, distinguish present, absent and indeterminate where applicable. A blank field is not a negative finding. Do not pre-check negatives.

Enforce nonnegative counts, count <= the explicitly applicable total, 0-100 percentages, valid score ranges, supported units, and appropriate modality/status combinations in the shared service and API as well as forms. Use denominator-specific calculations only when the relationship is known. Preserve reported versus calculated percentages when rounding produces a discrepancy; surface the discrepancy instead of silently replacing the report. Use warnings for clinical interpretation conflicts that cannot be settled by arithmetic.

The broad LM/immune-histology/EM organization is consistent with KDIGO's general biopsy assessment guidance, which also recognizes limited EM availability. The detailed capture set above is a proposed software specification, not a claim that KDIGO mandates every field: [KDIGO 2021, Chapter 1](https://kdigo.org/wp-content/uploads/2017/02/KDIGO-Glomerular-Diseases-Guideline-2021-English.pdf).

### Legacy Migration And Consumers

- Preserve the original scalar IF/EM values and notes. Convert each recognized scalar into one structured legacy finding, tagged with its source. Preserve unrecognized historical text as narrative. Never guess that an old False meant examined-and-absent.
- Migrate only into the known local/legacy interpretation; do not manufacture a central expert read, report date or signature.
- Extend `pathology/services/review.py` so finalization projects all applicable typed score models and selected summaries coherently. A disease change must not leave obsolete scores appearing current. Preserve older scores on their original report revision.
- Refresh consumers after the complete report transaction commits. Existing Biopsy-created signals can fire before its diagnosis/scores are saved; GNDiagnosis/score/review changes are not all present in `events/signal_handlers.py`'s event map. Emit one explicit report-changed/finalized event for a complete aggregate and test event-enabled consumers.
- Update `knowledge/services.py`, report summaries, API serialization, admin, clinical reasoning and exports together. Export repeated findings as a child table keyed by patient/biopsy/report revision/finding, with a dictionary; retain the existing patient-level dataset as a documented projection. Do not multiply patient-level analysis rows when joining findings.

## Prescription Typography And Rendering

Edit `prescriptions/templates/prescriptions/prescription.html`, the wrapper, and shared rendering only as needed. All supported routes should use the same print scale: in-app browser print, downloaded HTML, WeasyPrint PDF and xhtml2pdf fallback.

Proposed starting sizes, to be visually checked rather than treated as a clinical standard:

| Element | Current | Proposed |
|---|---:|---:|
| Main body / medication values | 14.5 px, about 10.9 pt | 12 pt (16 px) |
| Drug/brand name | 15 px, 11.25 pt | 12.5-13 pt |
| Patient instructions / taper | 13 px, 9.75 pt | 12 pt |
| Advice and stop instructions | 12.5 px, about 9.4 pt | 12 pt |
| Patient identity / vitals / generic subtitle | 12.5 px | 10.5-11 pt |
| Table headings | 11 px | 10-10.5 pt |
| Audit/version footer | 10 px | At least 8.5-9 pt |

Use literal pt sizes in the print stylesheet if needed for PDF fallback compatibility. Keep A4 and sensible margins around the current 12-14 mm. Allow a second page instead of shrinking all text to force one page. Use repeatable table headings, stable column widths, long-word wrapping, and page-break rules that keep a normal medication line with its instructions/taper. Exceptionally long instructions may continue clearly; they must not be clipped by an unsplittable block taller than a page.

The preview currently injects a whole HTML document with unscoped body/table styles inside the app page (`preview_wrapper.html:64` area). Scope the print content through a shared fragment or isolate it in an appropriate frame so typography does not alter navigation. The wrapper and standalone template currently declare different print margins. Remove stray blank pages/hidden-content space and hide print buttons in printed output, including the HTML-download button from `prescriptions/pdf.py`.

Verify 1, 5, 10 and 15 medication lines; long combination-product names and strengths; explicit dose different from strength; multiline taper; English/Bangla advice; long names; stopped medications; and draft/final markers. Inspect rendered pages at actual size. Verify Bangla glyphs and shaping with the deployed font and each supported backend. Report unsupported fallback behavior honestly instead of accepting a successful PDF call as proof of readable output.

Keep saved issued artifacts and clinical content immutable. Source inspection shows current rendering reads live Patient/encounter values and `compute_hash()` omits several printed fields (`prescriptions/models.py:87`, `prescriptions/pdf.py:render_prescription_html`). The field-linkage work must not make historical prescriptions change when the shared record changes. Introduce a versioned issued-content snapshot and source references for new finalized prescriptions; never fabricate historical snapshots for old prescriptions whose original context cannot be recovered. A style-only change must not silently change the clinical hash or overwrite an archived original PDF.

## Implementation Sequence

1. Record current field ownership in a maintained mapping and establish corrected-behavior regression cases from this review. Retain the existing 57 tests where their assertions remain clinically meaningful; explicitly replace the tests that currently enshrine lossy semantics, including automatic type-2 inference from duration and indefinite legacy fallback.
2. Add source links and the narrow shared commands/readers for conditions, measurements, laboratory recording and pathology projection. Use transactions for complete aggregates, idempotent retries, actor/reason audit and after-commit events. Use existing app boundaries; do not add a generic cross-app entity framework.
3. Reconcile existing data with an idempotent dry-run migration command. Report source row IDs, disagreements, unresolved records and proposed mappings; preserve original values and audit. Do not choose the latest `updated_at` as universal authority, delete suspected duplicates, or drop old columns in the first migration. Unknown values remain unknown. Test interrupted/repeated execution and rollback on a copy.
4. Change guided forms to reuse those authorities, show existing facts with source/date and Edit at source actions, and retain correct visit-specific entry. Ensure a visit/prescription/order explicitly selects its intended encounter rather than always attaching to the patient's latest encounter. Apply patient/site ownership validation to every new link and route using the app's existing permission model.
5. Expand histopathology and its full report/amendment workflow. Include review-state projection, disease-score consistency, audit, event refresh, export and reasoning adapters in the same deliverable.
6. Link prescription diagnosis, comorbidity inclusion, accepted investigation requests and next appointment; retain distinct dosing facts and issued snapshots. Implement typography as a separately reviewable change so visual acceptance is straightforward.
7. Run focused integration tests and visual print checks, then the project's required broader checks. Report pre-existing versus introduced failures separately. Package/deploy only after validation; no live data migration is authorized by this review note itself.

## Acceptance Cases

- Enter a current condition once; it appears consistently on patient, baseline context, visit and a new Rx. Explicitly correct it; it does not return from a legacy baseline or old Rx. Previously issued Rx and baseline enrollment facts retain their historical state.
- Import legacy baseline-only information with unknown provenance; present it for reconciliation, retain original values and record the decision. A new current condition must not appear as present at enrollment merely because baseline notes are edited.
- HbA1c entered through either UI lands in the same longitudinal record. Baseline references the correct dated observation. Two different same-date reports remain distinguishable.
- Retry a result request and obtain one observation/derivation set; explicitly add a genuine same-day repeat and obtain two. A corrected result leaves the original and supersession lineage readable.
- Creatinine via UI, API, admin and supported import produces consistent unit conversion, eGFR version/lineage, latest-value selection and safety inputs. Run relevant cases with normal events enabled after fixing the services.
- The same dated BP/weight measurement is visible in visit, print and clinical reasoning. A second reading is retained; a follow-up observation cannot rewrite enrollment measurement history.
- A second biopsy and an adjudicated lupus-class change produce coherent source-linked summaries/scores/exports. An older accepted biopsy and a newer pending one remain separately identifiable. Local and central disagreements remain visible.
- Contradictory FSGS primary-secondary/variant or lupus-class entries cannot be silently stored as though they agree. An unrelated score panel is not accidentally attached as current disease evidence.
- Save and reopen a report with at least two EM findings and multiple IF marker/location rows, plus Other text, a modality not performed, and a mixed lesion. View, API, amendment, export and reasoning retain every finding and state.
- Negative ANCA is not interpreted as positive evidence; the canonical anti-dsDNA code is recognized; the exact EM option emitted by the form reaches feature extraction. Unmeasured findings are not manufactured from a diagnosis name.
- Edit only an unrelated baseline note; all additional legacy presenting syndromes survive. Declaring a new primary presentation does not delete the rest without an explicit action.
- Select investigations once; accepted orders, pending result status and printed tests agree. Draft save/retry does not duplicate or prematurely issue orders.
- An existing next-visit date appears unchanged in prescription entry. An explicit change updates linked appointment displays/reminders consistently and preserves independent protocol windows.
- Enter a product strength and a different administered dose; both survive save, versioning, print and exposure reconciliation. No automatic `dose = strength` assumption remains in the canonical save path.
- Print large and small regimens in English and Bangla at the proposed larger size, with no missing dose/route/frequency/duration, clipped advice, detached taper, UI chrome or unintended blank pages.
- Old issued prescriptions remain reproducible to the extent their original artifacts exist; current Patient/lab/appointment edits do not silently alter new issued snapshots. Unrecoverable legacy context is explicitly identified.

## Existing Test Failures And Additional Safety Finding

The module run failed three existing lab tests:

1. `EgfrFormulaTests.test_ckd_epi_2021_reference_values`: expected formula label `CKD-EPI-2021-creatinine`, got `CKD-EPI 2021 (local fallback)`.
2. `LabResultTests.test_creatinine_derives_egfr_and_updates_patient`: same formula-label mismatch.
3. `LabResultTests.test_latest_egfr_tracks_most_recent`: Patient cache `19.2` versus derived result `19.1618`, reflecting different stored precision.

These are not proof that the newest result was selected incorrectly. Resolve the intended formula/provenance and precision contracts before changing assertions.

Inspection of that fallback also found a separate numerical defect at `labs/services/egfr.py:39`: alpha is fixed to -0.241 for both sexes. NIDDK specifies -0.241 for females and -0.302 for males. A direct local probe at male age 60 and creatinine 0.6 mg/dL returned **107.811697**, versus **110.511494** from the published equation. This discrepancy is relevant to lab consolidation and should be fixed and independently tested before clinical release. Do not rewrite historic derived results without retaining the original formula/version and a governed correction trail. Reference: [NIDDK adult eGFR equations](https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/adults).

## Reproducing This Review

From the workspace in PowerShell, isolate mutable runtime files:

```powershell
$env:BGDDR_DATA_DIR = Join-Path $env:TEMP 'bgddr-entry-review-20260927'
$env:CELERY_BROKER_URL = ''

& .\venv\Scripts\python.exe -m pytest tests/test_comorbidity_carry_forward.py tests/test_lupus_class_single_source.py tests/test_medication_single_source.py -q --disable-warnings

& .\venv\Scripts\python.exe -m pytest baseline/tests.py labs/tests.py pathology/tests.py prescriptions/tests.py exports/tests.py -q --disable-warnings

& .\venv\Scripts\python.exe -m pytest docs/reviews/2026-09-27-entry-linkage/review_probes.py -q --disable-warnings
```

The probe file deliberately asserts current defects and is outside ordinary discovery. Keep it as review evidence; create corrected-behavior regression tests in the appropriate normal test modules. Passing probes after implementation would mean those defects still exist.

## Required Handoff Back

Provide changed files and migrations, the final ownership map, a dry-run reconciliation report with unresolved conflicts, exact completed test counts and failures, before/after synthetic print samples with visual-QA results, and a list of any unsupported backends or unresolved clinical terminology. Separate implementation, local verification, clinical acceptance, packaging and deployment status. Do not claim the full application is validated from the focused results above.
