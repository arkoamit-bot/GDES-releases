# BGDDR — Glomerular Disease & Diabetes Registry (scaffold)

A runnable Django scaffold for the Bangladesh Glomerular Disease & Diabetes
Registry, built for **real-world point-of-care data collection that doubles as a
research platform**. At every follow-up the clinician records the visit, gives
management, orders labs, and prints a bilingual prescription — and that single
act populates the research tables automatically. On top of that spine sit the
longitudinal labs, biopsy pathology, an automatic outcome engine, survival/Cox
analytics, a full audit trail with versioned consent, and a registry-embedded
trial platform with reproducible randomization.

End to end: **enrol → consent → (randomize) → follow-up (prescription + labs +
biopsy) → compute outcomes → analyse by cohort or trial arm** — one system.

## The core idea

**The prescription *is* the follow-up visit.** One `ClinicalEncounter` per visit
is the hub; the printed prescription is one rendered output of it. Finalizing a
prescription does two things at once:

1. **Freezes** an immutable, hashed, versioned clinical document (medico-legal).
2. **Reconciles** the full current-medication list against the patient's open
   `TreatmentExposure` episodes — opening, closing, splitting, or continuing them
   — so you get a research-grade, new-user-cohort exposure history with zero
   extra data entry.

```
Rx item, no open episode      -> OPEN   (start = visit date)
open episode, drug dropped     -> CLOSE  (stop = visit date + reason)
same drug, dose/regimen change -> CHANGE (close old, open new — episode split)
same drug, identical regimen   -> CONTINUE (no-op)
```

## Apps

| App | What it holds |
|-----|---------------|
| `patients` | `Patient` — the registry spine |
| `encounters` | `ClinicalEncounter` (visit hub) + `ClinicalEvent` (dated endpoints) |
| `baseline` | `BaselineAssessment` — at-enrollment snapshot; auto BMI + Asian category |
| `pathology` | `Biopsy` + `GNDiagnosis` + scoring modules (MEST-C, ISN/RPS, FSGS, MN) + consent-gated `BiopsyImage`; **central review** (`PathologyReview`: local/central/adjudication), concordance + Cohen's κ inter-observer agreement |
| `biobank` | `Sample` — serial storage, **biobank-consent gated** |
| `treatments` | `DrugMaster` (formulary + research drug-class bridge), `TreatmentExposure` (research episodes, engine-written) |
| `labs` | `LabTest` catalog, encounter-linked `LabOrder`/`LabOrderItem`, **longitudinal** `LabResult`; versioned CKD-EPI 2021 eGFR derivation + slope |
| `prescriptions` | `Prescription` / `PrescriptionItem`, the **reconciliation engine**, safety checks, bilingual PDF |
| `analytics` | `PatientOutcome` (outcome engine), **survival analysis** (Kaplan-Meier + Greenwood CI, Nelson-Aalen, log-rank, incidence rates), **Cox PH** (multivariable), cohort analysis, individual-patient outcome; `ClinicalEvent` lives in `encounters` |
| `audit` | Per-field **change history** (who/when/old->new) via signals + thread-local actor; versioned, withdrawable `Consent` |
| `studies` | Registry-embedded **trial platform**: `Study`/`StudyArm`/`StudyEnrollment`, eligibility screening, reproducible **stratified permuted-block randomization**, trial-consent gating |
| `safety` | `AdverseEvent` (infections, steroid toxicity, SAEs); **infection incidence** by drug/diabetes (Study 20), per-study DSMB SAE tabulation |
| `scheduling` | Protocol follow-up schedule (§7.6): `ScheduledVisit` on Tuesday-clinic days, ±7-day windows, capacity 15, early safety visits, due/overdue/roster; immunosuppression lab-monitoring schedule (§7.7) |
| `biomarkers` | `BiomarkerKinetics` (§9.3): anti-PLA2R ≥50% decline + seroconversion (immunological remission), complement recovery, anti-dsDNA; Study 6 PLA2R-predicts-remission analysis |
| `exports` | One-row-per-patient **research dataset** (all domains) → CSV/Excel, **de-identified by default**; identified export gated to data managers |

Key code: `prescriptions/services/reconciliation.py`, `…/safety.py`,
`…/finalize.py`, and the print template `prescriptions/templates/prescriptions/prescription.html`.

## Research dataset export (`exports`)

The portfolio's denormalized **one-row-per-patient research dataset** — built from
the start, not bolted on. Each row pulls demographics, baseline, baseline labs,
pathology (diagnosis + MEST-C/ISN/FSGS), ever-exposed drug-class flags, computed
outcomes (eGFR slope, remission, time-to-remission, ESKD/death/composite),
biomarker kinetics, and safety counts — the analysis/ML-ready table that lets you
"find structured outcome" without re-abstracting charts. Booleans export as 0/1.

**De-identified by default** (Study ID only, no name/phone/reg — §13.5/§11.5);
identified export is gated to the `data_manager` role. The **Excel export ships
with a `data_dictionary` sheet** (codebook: type, units, description per column —
Appendix C), so a shared dataset is self-documenting.

```bash
# API (token/session auth)
GET /exports/research-dataset/?fmt=csv          # or fmt=xlsx ; identified=1
GET /exports/data-dictionary/                   # the codebook as JSON
# CLI
python manage.py export_dataset --format xlsx --out research.xlsx
```

## REST API & role-based access (`api`)

A Django REST Framework API at `/api/v1/` with token + session auth and
**role-based access control** (protocol §11). Roles are Django Groups —
`data_manager`, `coordinator`, `investigator`, `pathologist`, `statistician`,
`readonly` — seeded with per-model permissions by `python manage.py seed_roles`.
Reads are open to any authenticated user; **writes are gated per-model by role**
(DjangoModelPermissions).

```bash
# obtain a token
curl -X POST /api/v1/auth/token/ -d "username=...&password=..."
# use it
curl /api/v1/patients/ -H "Authorization: Token <key>"
```

Resources: `patients`, `encounters`, `events`, `lab-results`,
`treatment-exposures`, `biopsies`, `pathology-reviews`, `adverse-events`,
`scheduled-visits` (read/write per role); `prescriptions`, `outcomes`,
`biomarkers` (read-only/computed). Assign a role with
`user.groups.add(Group.objects.get(name="coordinator"))`.

**API writes are audited**: the authenticated DRF user is attributed in the audit
trail, and an optional `X-Change-Reason` request header is recorded as the reason.

## Run it

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_drugs          # nephrology formulary, research-coded
python manage.py seed_labs           # lab test catalog + ordering panels
python manage.py seed_roles          # RBAC roles (Groups + permissions)
python manage.py createsuperuser
python manage.py runserver
```

Then in the admin (`/admin/`): create a Patient → a ClinicalEncounter → a
Prescription with items. Useful endpoints:

- `/prescriptions/<id>/preview/` — rendered HTML prescription
- `/prescriptions/<id>/reconcile/preview/` — JSON diff (writes nothing; preview the impact)
- `POST /prescriptions/<id>/finalize/` — freeze + reconcile
- `/prescriptions/<id>/pdf/` — print-ready PDF

### Analytics (survival / cohort / individual outcome)

```bash
python manage.py compute_outcomes        # (re)build PatientOutcome rows
```

- `/analytics/patient/<patient_id>/outcome/` — individual patient outcome (JSON), `?recompute=1` to refresh
- `/analytics/cohort/survival/?group_by=drug:sglt2i&endpoint=composite_kidney_event` — KM steps + log-rank (JSON)
- `/analytics/cohort/survival/plot/?group_by=diabetes` — the same as an **SVG Kaplan-Meier plot**
- `/analytics/cohort/cox/?covariates=age,diabetes,drug:sglt2i&endpoint=composite_kidney_event` — **multivariable Cox PH** (hazard ratios + 95% CI + p)
- `/analytics/cohort/egfr-slope/?group_by=drug:sglt2i` — **linear mixed-effects** eGFR slope per group + between-group difference (§10.3)
- `/analytics/cohort/cif/?group_by=drug:sglt2i&at_days=365` — **competing-risks** cumulative incidence of the kidney endpoint with death as a competing event (§10.4)
- `/analytics/cohort/summary/?group_by=diagnosis` — per-group baseline/outcome counts

Cox covariate specs: `age`, `female`, `diabetes`, `baseline_egfr`,
`baseline_upcr`, `drug:<class>`. Covariates must vary across the cohort — a
constant covariate is singular and returns a readable 400 error.

`group_by`: `diabetes`, `diagnosis`, `cohort`, `drug:<class>` (e.g. `drug:hcq`,
`drug:finerenone`), or `study:<code>` (by trial arm). `endpoint`:
`composite_kidney_event`, `eskd`, `death`, `sustained_40_decline`,
`sustained_50_decline`, and the **proteinuria-regression** endpoints
`complete_remission`, `partial_remission`, `any_remission`,
`igan_proteinuria_response` (these are "good" events — `1 - KM` is the cumulative
incidence of remission, so the curve gives time-to-proteinuria-remission). The
survival math is pure-Python
and **validated against the published Freireich 6-MP dataset** (KM points +
log-rank chi-square); see `analytics/tests.py`. Operational endpoint definitions
are fixed in `analytics/services/outcomes.py`. **Multivariable Cox PH** is
implemented in pure Python (`analytics/services/cox.py`, Newton-Raphson on the
Breslow partial likelihood) and validated via the score-test/log-rank identity
plus hazard-ratio recovery on the Freireich data.

The protocol's §10.3-10.4 refinements are also pure-Python and validated:
**linear mixed-effects model** for eGFR slope (`mixed_model.py`, Laird-Ware EM,
random intercept + slope), **competing-risks CIF** (`competing_risks.py`,
Aalen-Johansen with variance — validated to reduce to 1-KM without competing
events), and **MICE + Rubin's rules** (`imputation.py`, predictive mean matching).
A full Fine-Gray subdistribution regression and REML are the natural next step
where a reference implementation (R/lme4, cmprsk) is available to validate against.

Run all engine tests: `python manage.py test`

## Bilingual printing

The template is bilingual (English drug/dose lines, Bangla patient instructions
and advice). For correct Bengali in the **PDF**, drop a Unicode Bengali TTF at
`prescriptions/static/prescriptions/fonts/NotoSansBengali-Regular.ttf`
(download from Google Fonts). The HTML preview uses the system font.

PDF rendering uses **WeasyPrint**, which needs native libraries
(cairo / pango / gdk-pixbuf). On Windows install the **GTK3 runtime**
(https://github.com/tschoonj/GTK-for-Windows-Runtime-Installer). The project
runs fine without it — only the `/pdf/` endpoint needs it; everything else
(workflow, reconciliation, HTML preview) works regardless.

## Safety checks (scoped to v1)

`prescriptions/services/safety.py` runs three high-value nephrology checks:
renal dosing vs. cached eGFR, prior-intolerance block, and duplicate-class
therapy. Full drug–drug interaction / CDS is intentionally phase 2.

## Audit trail & consent

Every create/update/delete of the clinical-edit models (Patient, ClinicalEncounter,
ClinicalEvent, Prescription/Item, TreatmentExposure, Consent) is captured in
`audit.AuditLog` — **per-field old->new on update**, attributed to a user.

- Web requests: attribution is automatic via `AuditMiddleware` (uses `request.user`;
  optional `X-Change-Reason` header).
- Scripts / shell / management commands: wrap writes in the actor context:

  ```python
  from audit.local import acting_as
  with acting_as(user, reason="diagnosis correction"):
      patient.save()
  ```

Consent is versioned: `grant_consent()` supersedes the prior current consent of
the same type (a DB constraint enforces one current per type); `withdraw_consent()`
revokes it; `has_consent(patient, type)` is the gate to check before biobank /
genetic / trial actions. See `audit/services/consent.py`. Append-only tables
(LabResult, PatientOutcome) are intentionally **not** audited — their provenance
lives in the rows themselves.

## Registry-embedded trials (`studies`)

Turns the registry into a trial platform. A `Study` defines arms (with allocation
ratios) and a randomization scheme; `enroll(study, patient)` screens for
eligibility, enforces the **trial-consent gate** (`has_consent`), and — for
randomized studies — allocates an arm via a **reproducible seeded sequence**
(stratified permuted blocks). Allocation provenance (stratum, position, who/when)
is stored and the enrollment is audited.

```python
from studies.services.randomization import enroll
enr = enroll(study, patient, by=request.user)   # screens, gates consent, randomizes
```

- Eligibility criteria are pluggable per study code in `studies/services/eligibility.py`
  (ADVANCED-DKD-IgAN and HCQ-IgAN-advanced are worked examples).
- `/studies/<code>/dashboard/` — CONSORT-style funnel + per-arm / per-stratum balance.
- **Analyse by arm** with the existing engine:
  `/analytics/cohort/survival/plot/?group_by=study:<code>&endpoint=composite_kidney_event`
  (intention-to-treat KM + log-rank), or `/analytics/cohort/cox/?...` for adjusted HRs.

This is the full loop the portfolio's "learning health system" vision calls for:
enrol → consent → randomize → follow up (prescription/labs) → compute outcomes →
analyse by arm, all in one system.

## Proteinuria remission (the primary disease-activity outcome)

Remission is **disease-specific**, computed from a proteinuria series in **g/day**
(24-h UTP preferred; spot UPCR g/g used as a ~g/day fallback). Rules live in
`analytics/services/remission.py`, aligned to the GN Master Protocol §9.1 and
KDIGO 2021/2025:

| Disease | Complete | Partial | Other |
|---------|----------|---------|-------|
| IgAN | < 0.3 g/day | (n/a) | response = ≥30% reduction **or** < 0.3; 0.5 g/d target |
| MN / FSGS / MCD | < 0.3 g/day | ≥50% reduction **and** < 3.5 g/day | |
| Lupus | < 0.5 g/day **+ eGFR within 10% of baseline** (15% if baseline reduced), at the remission timepoint | ≥50% reduction & < 3.5 | |

All are *sustained* (a transient dip doesn't count) and stamped with the **first
date achieved**, so they work as time-to-event endpoints. The composite renal
endpoint is the protocol's: earliest of {ESKD (dialysis/transplant **or eGFR < 15**),
**≥50% eGFR decline**, renal death}.

## Safety / adverse events (`safety`)

`AdverseEvent` captures the harms side (protocol §9.4): infections (TB, PJP,
zoster, pneumonia, sepsis…), steroid toxicity, haematologic/hepatic events, with
severity, SAE flag (auto-set on hospitalisation or G4/G5), drug attribution, and
outcome. Endpoints:

- `/safety/summary/` — counts by category / severity / infection type
- `/safety/infection-incidence/?group_by=diabetes` (or `drug:steroid`) — infection
  **incidence density per 100 patient-years** by group (Study 20), using the
  outcome engine's follow-up time as person-time
- `/safety/study/<code>/` — per-arm SAE / infection / death counts for the DSMB

## Biomarker kinetics (`biomarkers`)

`BiomarkerKinetics` is computed per patient from the lab series (like
`PatientOutcome`), implementing protocol §9.3 and portfolio Study 6:

- **anti-PLA2R** (MN): baseline/nadir, % decline, **≥50% decline** (+ date and
  days-from-baseline → the early-response predictor), and **seroconversion to
  negative = immunological remission** (+ date), which precedes proteinuria remission.
- **complement recovery** (LN/C3G): C3/C4 normalisation dates.
- **anti-dsDNA** (LN): normalisation.

Endpoints / analyses:

- `/biomarkers/patient/<id>/` — a patient's kinetics
- `/biomarkers/pla2r-predictor/?within_days=90` — **Study 6**: does an early ≥50%
  anti-PLA2R decline predict 12-month complete remission? Returns the 2×2 table
  with sensitivity / specificity / PPV / NPV / relative risk.
- `…/analytics/cohort/survival/?group_by=biomarker:pla2r_response&endpoint=complete_remission`
  — time-to-proteinuria-remission (KM + log-rank) by early antibody response,
  reusing the survival engine.

Run `python manage.py compute_biomarkers` to (re)build the rows.

## Central pathology review (`pathology`)

Every index biopsy gets a **local** read and a mandatory **central** expert read
(§7.3). `submit_review()` records each; the two are compared field-by-field
(diagnosis, broad group, MEST-C, ISN/RPS class, FSGS variant):

- **concordant** → the biopsy is auto-finalized and the authoritative
  `GNDiagnosis` / `IgANScore` are written from the agreed read;
- **discordant** → flagged for **adjudication**; `adjudicate()` records the
  consensus read, which becomes final.

`/pathology/biopsy/<id>/review/` shows status + concordance, `/pathology/discordant/`
lists biopsies awaiting adjudication, and `/pathology/agreement/` reports
**inter-observer agreement** — Cohen's κ per field across all dual-reviewed
biopsies (§11.3), pure-Python and validated against the textbook κ=0.40 example.

## Follow-up scheduling (`scheduling`)

The prospective-registry operational layer (protocol §7.6–7.7). `generate_schedule`
creates `ScheduledVisit` rows for the protocol timepoints (months 1, 3, 6, 9, 12,
then 6-monthly to 5 years), each **snapped to the nearest Tuesday GN clinic**
within a ±7-day window and respecting the **15-slot session capacity** (a full
Tuesday bumps the visit to another clinic day in-window). Patients on **active
immunosuppression** also get **early safety visits** (weeks 1, 2, 4).

- `/scheduling/due/?as_of=…` and `/scheduling/overdue/` — coordinator worklists
- `/scheduling/roster/?date=…` — a clinic day's roster + capacity headroom
- `/scheduling/monitoring/<patient_id>/` — agent-specific monitoring labs due (§7.7)

Clinic config (weekday, capacity, window) lives in `settings.SCHEDULING`. A
`ClinicalEncounter` fulfils a scheduled visit via `complete_visit()`.

## Note on the GN Master Protocol v2

This build is aligned to `GN_Master_Protocol_v3_Bangladesh_revised.docx` (v2.0):
disease-specific remission + 24-h UTP, composite at 50% decline, randomization
stratification factors `egfr_30` (≥30 vs <30) and `proteinuria_range`
(nephrotic vs non-nephrotic), and **adult-only (≥18)** master eligibility.
**Biobanking was removed in protocol v2** — the `biobank` app is disabled
(commented out of `INSTALLED_APPS`); its code is retained for a future amendment.

## Scope & what's next

All of the original design-review priorities are implemented: prescription +
reconciliation, longitudinal labs with versioned eGFR, the outcome engine,
survival + Cox analytics, per-field audit with versioned consent, and the
registry-embedded trial platform — plus baseline, pathology, and biobank
data-entry. **56 tests pass** (`python manage.py test`).

This is a scaffold, not production: it uses SQLite + the dev server and minimal
auth. Production hardening still to do — PostgreSQL (for the analytics layer /
pgaudit), real authentication + role-based permissions, REST API (DRF) and forms
for data entry beyond the admin, `egfr_slope` → a proper analytics layer (mixed
models, materialized views), Efron ties for Cox, and file storage for
prescription PDFs / biopsy images.

### Labs ↔ prescription loop (verified)

Ordering labs at a visit and entering a creatinine auto-derives a versioned
CKD-EPI 2021 eGFR, refreshes `Patient.latest_egfr`, and that immediately feeds
the prescription's renal-dosing safety check — labs make the next Rx safer with
no manual step. See `labs/services/results.py` and `…/egfr.py`.
```

## Documentation Structure

This repository contains comprehensive documentation organized as follows:

### Root Documentation
- `README.md` — This file (project overview)
- `PROJECT_CONSTITUTION.md` — Project governance and standards
- `PROJECT_CONTEXT.md` — Project context and background
- `TRACK.md` — Project tracking and milestones

### Documentation Directory (`/docs/`)
- **Architecture** (`docs/architecture/`) — System architecture documentation
- **Clinical** (`docs/clinical/`) — Clinical documentation
  - **Diseases** (`docs/clinical/diseases/`) — Disease-specific documentation (195 files)
- **Development** (`docs/development/`) — Development guides
- **Deployment** (`docs/deployment/`) — Deployment documentation
- **Releases** (`docs/releases/`) — Release notes and changelogs
- **Reports** (`docs/reports/`) — Technical reports
- **Workflows** (`docs/workflows/`) — Workflow documentation

### AI Factory Documentation (`/.hermes/`)
- **System** (`.hermes/HERMES_SYSTEM.md`) — Hermes system operating instructions
- **Bootstrap** (`.hermes/HERMES_MASTER_BOOTSTRAP.md`) — Master bootstrap instruction
- **Documentation** (`.hermes/documentation/`) — AI Factory documentation
- **Agents** (`.hermes/agents/`) — Agent definitions
- **Workflows** (`.hermes/workflows/`) — Reusable workflows
- **Prompts** (`.hermes/prompts/`) — Production-ready prompts
- **Memory** (`.hermes/memory/`) — Project knowledge base
- **Reports** (`.hermes/reports/`) — Intelligence reports
- **Scripts** (`.hermes/scripts/`) — Automation scripts

### Documentation Index
See `docs/DOCUMENTATION_INDEX.md` for a comprehensive index of all documentation.
