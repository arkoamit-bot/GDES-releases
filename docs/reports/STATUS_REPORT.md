# BGDDR — Critical Status Report
_Assessment date: 2026-06-25 · Updated: 2026-06-25 (Items 1–5 completed)_

> **Update — Item 4 done.** Multi-user authentication: `users` app with
> `UserProfile` (role, department, phone), invitation system (token-based,
> 7-day expiry), custom login/logout/password-reset pages, profile editing,
> user list & invite admin pages. Replaces admin-only login. Django Groups
> synced with roles. `invite_user` management command for CLI invitations.

> **Validation completed (2026-06-25):** `validate_patients` run against the 224
> imported records. **100% flagged** — 221 lack baselines, 219 have no encounters,
> 91 missing diagnosis, 11 missing DOB/enrollment date. **Duplicates found:**
> `000000` duplicates `BGD-00001` (same name/phone/hospital_id); `API-DM` shares
> phone/hospital_id with Wasim. Cleanup scripts and CSV export provided.

> **Previous updates:** Item 3 (production settings, PDF fallback, file storage,
> patient validation, deployment guide), Item 2 (lab ordering + analytics HTML),
> Item 1 (all 7 modules got pages).

## How this was assessed
Originally static analysis (apps, URLs, views, templates, SQLite contents, tests).
**As of the Item 1 update the app is run here** — deps were installed
(`Django`, `djangorestframework`, `django-jazzmin`; WeasyPrint is imported lazily
so only the PDF view needs GTK), `manage.py check` passes, and pages are rendered
against the real DB via Django's test client. So the Item 1 results are observed,
not inferred. The PDF/print path was not exercised (needs the GTK runtime).

---

## 1. Snapshot

- **Architecture:** Django 5 + Django REST Framework, 17 apps, SQLite dev DB,
  `jazzmin` admin theme. Pure-Python statistics (no scipy/R dependency).
- **Tests:** ~113 test functions across 13 apps (survival math validated against
  the published Freireich dataset).
- **Database today (`db.sqlite3`):**
  | Table | Rows |
  |---|---|
  | patients | **224** |
  | lab results | **1079** |
  | computed outcomes | **220** |
  | clinical encounters | 5 |
  | baseline assessments | 3 |
  | prescriptions | 4 |
  | biopsies | 7 |
  | users | 6 |

  → A large patient list (looks bulk-imported) but **almost no longitudinal
  clinical entry** (encounters/baselines/biopsies are single digits). Most
  analytics will be sparse or empty in real use until data entry happens.

---

## 2. What is DONE and working

**Backend / domain (strong):**
- Full data model for the registry spine: Patient, ClinicalEncounter, Baseline,
  Labs (LabTest/Order/Result with CKD-EPI 2021 eGFR), Pathology (Biopsy + scoring
  + central review), Treatments (DrugMaster + TreatmentExposure), Prescriptions.
- Computational engines, unit-tested: prescription→exposure **reconciliation**,
  **outcome** engine, **survival** (KM+CI, log-rank, Nelson-Aalen), **Cox PH**,
  **linear mixed-effects eGFR slope**, **competing-risks CIF**, **MICE imputation**,
  **remission** rules, **biomarker kinetics**, **scheduling**, pathology
  concordance + Cohen's κ.
- **Audit trail** (per-field change history) + **versioned consent**.
- **REST API** at `/api/v1/` with token auth and role-based permissions
  (`seed_roles`).
- Seed commands: `seed_drugs`, `seed_labs`, `seed_roles`; compute commands:
  `compute_outcomes`, `compute_biomarkers`; `export_dataset`.

**User-facing (the spine only):**
- **Admin** (`/admin/`, themed) — every model is editable here. This is the only
  complete data-entry surface.
- **Dashboard** (`/`) — counts, due/overdue worklist, quick links.
- **Clinic guided pages** (HTML): Patients list, Patient detail (with eGFR/
  proteinuria trend chart), Add/Edit patient, **Baseline (+labs)**,
  **Follow-up (+labs, auto eGFR)**, **Prescription** create → preview → finalize →
  PDF, Analytics landing (with a live Kaplan-Meier SVG), Export landing
  (CSV/XLSX download).

---

## 3. What is NOT working — and why links "don't open"

> ✅ **RESOLVED (Item 1 + Item 2).** Every module now has an HTML page; advanced
> analytics (Cox, eGFR-slope, CIF) also have HTML result pages. The underlying JSON
> APIs are kept intact for programmatic use. The text below is retained to document
> the original problem.

**Root cause (original):** seven feature modules were **API-only**. Their views returned raw
`JsonResponse`/SVG/file downloads — there are **no HTML pages** (verified: 0
`render()` calls in `analytics`, `scheduling`, `safety`, `studies`, `pathology`,
`biomarkers`, `exports`). So when a link points at them, the browser shows raw
JSON or a download, which reads as "broken."

Concretely:
- **Dashboard "Due / Overdue" quick-links** → `/scheduling/due/`, `/overdue/`
  return **JSON**.
- **Studies, Safety, Pathology, Biomarkers** → JSON only, **and not in the
  sidebar at all** → effectively unreachable for a normal user.
- **Analytics** → only the KM plot renders (as an `<img>` SVG); the **Cox**,
  **cohort summary**, **eGFR-slope**, **CIF** links open **raw JSON**.
  → **Now fixed:** Cox, eGFR-slope and CIF each have an HTML results page
  (`/clinic/analytics/cox/`, `/egfr-slope/`, `/cif/`).
- **Export** → CSV/XLSX download links and a JSON data-dictionary (these work as
  intended, but the dictionary "page" is raw JSON).

**Other real gaps / risks:**
- **PDF printing** needs WeasyPrint + the **GTK3 runtime** on Windows; without it
  the `/pdf/` view falls back to **xhtml2pdf** (pure-Python) or an **HTML
  download** the user can open and print. Everything else works.
  _(Inferred from requirements/README; fallback chain verified in code.)_
> **Auth** — custom login/logout/password-reset pages, invitation system,
> profile editing, user list & invite admin. Django Groups synced with roles.
> `invite_user` management command for CLI invitations. **Done in Item 4.**
- ~~**Auth is admin-login only** (`login_url="/admin/login/"`), 6 users, no~~
  ~~production authentication/SSO or self-service accounts.~~
- **Dev server + SQLite** — the README itself lists PostgreSQL, real auth, file
  storage and an analytics materialized layer as "still to do."
- **Data-entry coverage is partial in the guided UI:** baseline, follow-up and
  prescription have friendly pages; **biopsy, treatment, outcomes, adverse
  events, ~~lab ordering~~, studies enrolment, consent** are admin-only.
  → **Now fixed:** biopsy, adverse events, lab ordering, study enrolment, consent
  and treatment all have guided forms. Outcomes are auto-computed.
- The **224 patients** look bulk-imported with little supporting clinical data —
  needs validation/dedupe and confirmation of the import field mapping.

---

## 4. Completion estimate

| Layer | Done |
|---|---|
| Domain models + computational engines | **~85%** (built + tested; Fine-Gray / REML / Efron-ties noted as future) |
| Clinician-facing UI | **~75%** (spine + all 7 analysis/operational modules + advanced analytics HTML pages + guided data-entry + multi-user auth) |
| Production readiness (auth, DB, deploy, file storage, validation, migration scripts) | **~90%** |
| **Overall → usable day-to-day clinical tool** | **~85%** |

The intellectual/hard part (the validated analytics + reconciliation engine) is
largely done. Infrastructure (auth, deployment, migration, PDF fallback) is
complete. Remaining work: **clean the 224 imported patients** (dedupe, fill
missing fields, enter baselines/visits) and **run the PostgreSQL migration** when
ready for multi-user.

---

## 5. What must be done before you can "start working"

**A. Make the existing engines usable (highest value, mostly UI) — ✅ DONE (Item 1):**
1. ✅ HTML pages render the engine outputs as tables/charts:
   - ✅ **Scheduling:** due / overdue / roster worklist (`/clinic/worklist/`).
   - ✅ **Analytics:** cohort summary + survival tables + KM plot; Cox/eGFR-slope/CIF
     all have **dedicated HTML result pages** (`/clinic/analytics/cox/`,
     `/egfr-slope/`, `/cif/`) instead of raw JSON.
   - ✅ **Studies:** trial dashboard (funnel, arm balance, stratum) — `/clinic/studies/`.
   - ✅ **Safety:** AE summary + infection incidence — `/clinic/safety/`.
   - ✅ **Pathology:** review status, discordant list, κ agreement — `/clinic/pathology/`.
   - ✅ **Biomarkers:** PLA2R predictor (2×2 + metrics) — `/clinic/biomarkers/`.
   - ~~_Remaining nicety:_ Cox/eGFR-slope/CIF still open raw JSON; per-patient~~
     ~~biomarker/outcome detail not yet on the patient page.~~ **Done in Item 2.**
2. ✅ Added to the **sidebar nav**; dashboard quick-links/cards now point to pages.

**B. Close data-entry gaps — ✅ DONE (Item 2):**
3. ✅ All guided forms built: adverse events, biopsy, lab ordering, study
   enrolment, consent, and treatment. Outcomes are auto-computed.
   - ✅ **Adverse events** — guided report form at
     `/patients/<pk>/adverse-event/` (SAE auto-flagged on hospitalisation/G4–G5;
     drug & encounter dropdowns scoped to the patient). Listed on the patient
     page with a "Report AE" action; feeds the cohort Safety page. Verified:
     form 200, POST creates + redirects, SAE auto-flag confirmed.
   - ✅ **Biopsy** — guided entry at `/patients/<pk>/biopsy/`: core biopsy +
     lesion descriptors + the **GN diagnosis** (the driver of disease-specific
     remission rules) + optional **MEST-C / ISN-RPS / FSGS / MN** score blocks
     that only save when filled (the relevant block auto-opens from the chosen
     diagnosis). New biopsies enter central review as `pending`. Listed on the
     patient page with review-status badges. Verified: form 200, POST creates
     biopsy + diagnosis + only the touched score block, others correctly skipped.
   - ✅ **Study enrolment** — guided screen-and-enrol at `/patients/<pk>/enroll/`.
     Delegates to `studies.services.randomization.enroll` (screening + trial-
     consent gate + seeded arm allocation); surfaces every outcome as a message
     (enrolled → arm/stratum · ineligible → reasons · consent-required ·
     already-enrolled). Open studies listed with type/scheme/consent/arms.
     Enrolments shown on the patient page with status badges. Verified: form 200,
     POST screens + records the enrolment with its outcome, redirects.
   - ✅ **Consent** — guided grant/withdraw at `/patients/<pk>/consent/`
     (reuses `audit.services.consent`). Records versioned consent (a new ICF
     version **supersedes** the current one, keeping the chain), withdraws the
     current one, and shows per-type status + full history. TRIAL consent here
     unblocks trial enrolment. Patient page shows a per-type consent strip.
     Verified: grant → `has_consent` True; re-grant → new current version with
     `supersedes` set and exactly one current row; withdraw → `has_consent` False.
   - ✅ **Lab ordering** — guided order form at `/patients/<pk>/lab-order/`
     (panel + custom tests, linked to the latest encounter). Lab orders listed on
     the patient page with status badges. Verified: form 200, POST creates order
     + redirects, deduplicates panel + custom tests.
   - _Remaining:_ outcomes are auto-computed (no manual entry needed).

**C. Operational / production — _DONE_ (Item 3):**
4. ✅ **Production settings** (`bgddr.settings_prod`) — PostgreSQL, Whitenoise,
   security hardening (HSTS, secure cookies, HSTS, CSP-ready), logging to
   rotating file, `SECRET_KEY` from env, `ALLOWED_HOSTS` env-driven.
5. ✅ **PDF fallback chain** — `render_prescription_pdf` tries WeasyPrint
   first, then xhtml2pdf (pure-Python, no native deps), then falls back to an
   HTML download the user can open in a browser and print. The HTML preview
   (`/preview/`) always works. A new `html_download` endpoint (`/html/`) is
   linked on the patient page alongside PDF.
6. ✅ **File storage** — `MEDIA_URL` / `MEDIA_ROOT` configured; finalized
   prescription PDFs saved to `media/prescriptions/` via `save_prescription_pdf`.
   Dev server serves media; production uses nginx / S3.
7. ✅ **Patient validation** — `manage.py validate_patients` checks the 224
   imported patients for exact duplicates (name, phone, hospital_id), missing
   critical fields (dob, sex, enrollment, diagnosis), and coverage gaps
   (baseline, encounters, labs). Returns non-zero exit code if duplicates exist
   (useful as a CI / pre-deploy gate). Optional `--csv` export for manual review.
8. ✅ **Deployment guide** — `DEPLOYMENT.md` covers environment variables,
   PostgreSQL migration, gunicorn / IIS, Whitenoise static files, backup, and
   health checks.

**_Remaining before routine clinical use:_**
- Run `validate_patients` against the real import and resolve any duplicates.
- Decide single-PC vs multi-user deployment; if multi-user, configure PostgreSQL
  and real auth (LDAP/SSO or Django's built-in auth with invitation tokens).
- Install GTK3 on the server for best-quality PDFs, or rely on xhtml2pdf/HTML
  fallback.

**D. Governance:**
9. Coordinate with whoever else is editing this (`UI_Improvements.md`, the
   `clinic` app) to avoid clobbering.
10. Strategic: this overlaps with the FastAPI **BIRDEM GN Registry** and the
    **GNModule** PWA — decide which is the system of record before investing more.

---

## 6. One-line verdict
A **strong, well-tested analytics/registry engine** whose clinician UI now
**covers all major modules and guided data-entry forms** (Items 1 & 2 done) on top
of the patient/visit/prescription spine. Production hardening and multi-user
authentication are in place (Items 3 & 4: settings, PDF fallback, file storage,
patient validation, deployment guide, invitation-based auth, role profiles).
**Validation of the 224 imported patients has been run** (Item 5): 100% flagged
for review, 221 lack baselines, 219 have no encounters, duplicates found
(`000000` = `BGD-00001`; `API-DM` shares phone/hospital_id). Cleanup scripts
(`cleanup_dups.sql`, `patient_issues.csv`) and PostgreSQL migration script
(`migrate_to_postgres.py`) are ready. Before **routine clinical use** it still
needs: resolve the duplicates, fill missing critical fields, enter baselines/
visits for real patients, and migrate to PostgreSQL when ready for multi-user.
