# BGDDR User Manual

Bangladesh Glomerular Disease and Diabetes Registry  
BIRDEM General Hospital - Department of Nephrology

Version: 2026-07-06  
Application: BGDDR single-user Windows desktop app

This manual explains how to use BGDDR in day-to-day clinical work and registry
operations: starting the app, logging in, registering patients, recording
baseline and follow-up data, writing prescriptions, entering labs and biopsies,
managing consent, enrolling patients into studies, reviewing analytics, exporting
data, and performing administrator tasks.

For installation and packaging details, see `DESKTOP_DEPLOYMENT.md`. This manual
assumes the app is already installed or running from `BGDDR.exe`.

---

## Table of Contents

1. Purpose of BGDDR
2. First Launch and Login
3. Roles and Access
4. Navigation Overview
5. Daily Clinic Workflow
6. Patient Registration
7. Patient Detail Page
8. Baseline Assessment
9. Follow-up Visits
10. Laboratory Orders and Results
11. Biopsy and Pathology
12. Prescriptions
13. Treatment Exposure History
14. Consent
15. Admissions and Relapse
16. Adverse Events and Safety
17. Scheduling and Worklist
18. Studies and Randomization
19. Outcomes and Analytics
20. Data Export
21. User and Role Administration
22. Reference Data Administration
23. Backup and Restore
24. Data Quality and Audit Trail
25. Troubleshooting
26. Quick Reference
27. Glossary

---

## 1. Purpose of BGDDR

BGDDR is both a clinical workflow application and a research registry. The app is
designed around one practical idea:

**The prescription is the visit.**

At each patient encounter, the clinician records the visit, writes the current
full prescription, orders or records investigations, and schedules the next
review. When the prescription is finalized, BGDDR also updates the research-grade
medication exposure table automatically. This means routine clinical work creates
structured longitudinal research data without duplicate entry.

BGDDR supports:

- Patient registration and longitudinal GN/diabetes follow-up.
- Baseline demographic, clinical, comorbidity, presentation, examination, and
  serology capture.
- Clinical encounters with response status, disease phase, treatment adjustment,
  advice, and next due date.
- Laboratory ordering and longitudinal results, including automatic eGFR
  derivation from serum creatinine.
- Biopsy records, GN diagnosis, Oxford MEST-C, lupus class, FSGS variant, and
  membranous nephropathy features.
- Bilingual prescription printing with safety checks and immutable finalization.
- Medication exposure reconstruction from prescriptions.
- Consent versioning and withdrawal.
- Registry-embedded observational studies and randomized trials.
- Safety events, infection incidence, and study safety summaries.
- Outcomes, survival analysis, Cox regression, eGFR slope, competing risks, and
  cohort summaries.
- De-identified and identified exports to CSV, Excel, and SPSS.
- Audit trail, user roles, backup, and restore.

---

## 2. First Launch and Login

### Start the Desktop App

1. Open the BGDDR folder.
2. Double-click `BGDDR.exe`.
3. A small status window appears saying the registry is running.
4. Your browser opens at `http://127.0.0.1:8000/`.

Keep the status window open while using the app. Use its Stop button to shut down
the local server cleanly.

### First Administrator Account

On the first launch, the app asks you to create the first administrator account.
This account is the main superuser. It can access all modules, the Django admin
site, backup/restore tools, reference data, and user management.

Recommended practice:

- Use a named account rather than a shared password where possible.
- Store the first administrator password securely.
- Create separate accounts for clinicians, coordinators, statisticians, and
  other staff.

### Login

1. Go to `http://127.0.0.1:8000/login/`.
2. Enter username and password.
3. Click Sign in.

After login, the dashboard opens. Use Logout from the top-right account menu when
finished.

### Password Reset

Users can request password reset from `/password-reset/` if email/reset settings
are configured. An administrator can also reset passwords from:

- `Admin -> Users -> select user -> change password`
- or from a shell: `python manage.py changepassword <username>`

---

## 3. Roles and Access

BGDDR uses role-based access control. Roles are stored as Django groups and are
assigned through user profiles or invitations.

| Role | Typical user | Main purpose |
|---|---|---|
| Data Manager | Registry lead, admin | Full data management; can perform identified exports |
| Coordinator | Study/clinic coordinator | Patient registration, visits, labs, consent, enrolment |
| Investigator | Clinician, PI | Clinical entry, prescriptions, outcomes review |
| Pathologist | Renal pathologist | Biopsy and central pathology review |
| Statistician | Analyst | Analytics and de-identified exports |
| Read-only | Auditor, observer | View-only access |
| Superuser | System administrator | Full access including admin and maintenance |

The first account created by `BGDDR.exe` is a superuser. Superusers bypass normal
role restrictions, so they should be limited to trusted administrators.

---

## 4. Navigation Overview

The app uses a patient-centered workflow. The sidebar and patient pages are the
main navigation surfaces.

### Sidebar Sections

| Section | Use |
|---|---|
| Dashboard | Registry overview, quick links, counts, and worklist summary |
| Patients | Search, register, edit, and open patient records |
| Worklist | Due visits, overdue visits, and clinic roster |
| Prescriptions | Recent prescriptions and prescription follow-up |
| Analytics | Survival, Cox, eGFR slope, competing risks, and cohort tools |
| Studies | Study portfolio, recruitment funnel, and study dashboards |
| Safety | Adverse event summaries and infection incidence |
| Pathology | Biopsy review, discordant cases, and agreement statistics |
| Biomarkers | Patient biomarker trends and PLA2R predictor |
| Export | Research dataset downloads |
| Admin | Back-office data and system administration |

### Header Tools

Use the header to:

- Return to the dashboard.
- Jump quickly to a patient by ID or name.
- Open the user profile.
- Log out.

---

## 5. Daily Clinic Workflow

The recommended daily workflow is:

1. Open Worklist and identify due or overdue patients.
2. Open the patient record.
3. Update patient demographics if needed.
4. Record the follow-up visit.
5. Order investigations or enter available lab results.
6. Record adverse events, admission, relapse, consent, or study enrolment if
   relevant.
7. Write the full current prescription.
8. Review safety warnings.
9. Finalize and print or download the prescription.
10. Confirm the next due date.

Important rule for prescriptions:

**Each prescription should contain the patient's complete current regimen, not
only the changed medicines.** The reconciliation engine compares the finalized
prescription against previous open medication episodes.

---

## 6. Patient Registration

Open:

- `Patients -> Add patient`
- or `/patients/add/`

### Required and Common Fields

| Field | Notes |
|---|---|
| Name | Patient's name |
| Hospital ID | Hospital/BIRDEM registration number, optional but recommended |
| Phone | Useful for duplicate detection and follow-up |
| Sex | Male, Female, or Other |
| Date of birth | Used for age and eGFR derivation |
| Enrollment date | Registry entry date |
| Cohort | Patient category |
| Diabetes status | No diabetes, Type 1, Type 2, or other/secondary |
| Primary diagnosis | Curated GN diagnosis list |

The patient ID is generated automatically in the format `BGD-00001`,
`BGD-00002`, and so on. Do not type this manually.

### Duplicate Check

As patient details are entered, BGDDR can detect likely duplicates using name,
phone, hospital ID, and other matching fields. Review possible matches before
saving a new patient.

### After Saving

After saving, BGDDR opens the patient detail page. From there, you can add:

- Baseline assessment.
- Follow-up encounter.
- Lab order.
- Lab results.
- Biopsy.
- Prescription.
- Consent.
- Study enrolment.
- Adverse event.
- Admission.
- Relapse.
- Treatment exposure.

---

## 7. Patient Detail Page

The patient detail page is the main working screen for a single patient.

It displays:

- Patient identity and demographics.
- Registration status and disease phase.
- Latest renal function where available.
- Baseline summary.
- Encounters and visit history.
- Lab trends and result tables.
- Prescriptions.
- Treatment exposures.
- Biopsies and pathology.
- Study enrolments.
- Consents.
- Outcomes.
- Safety events.

Common actions:

| Button/action | Use |
|---|---|
| Edit | Correct demographic or core patient details |
| Baseline | Add or update baseline assessment |
| Follow-up | Record a visit |
| Lab order | Order tests for a visit |
| Enter results | Enter lab/serology results |
| Biopsy | Add biopsy and pathology details |
| Prescription | Write a prescription for an encounter |
| Consent | Record or withdraw consent |
| Enrol in study | Screen/enrol patient into a study |
| Treatment | Add external or prior medication exposure |
| Adverse event | Record safety event |
| Admission | Record inpatient work-up |
| Relapse | Record relapse episode |
| Recompute outcomes | Refresh derived outcome row |

---

## 8. Baseline Assessment

Open:

- Patient page -> Baseline
- or `/patients/<id>/baseline/`

Baseline is the enrolment-time clinical snapshot. It should be completed as early
as possible because it feeds outcomes, analyses, and exports.

### Sections Captured

| Section | Examples |
|---|---|
| Social/demographic | Residence division, education, occupation, income |
| Medical history | Hypertension, CVD, previous kidney disease, autoimmune disease |
| Diabetes burden | Duration, HbA1c, retinopathy, neuropathy, diabetic foot |
| Anthropometry/vitals | Height, weight, BMI, BP, pulse, temperature |
| Presentation | Syndrome, symptoms, oedema, urinary sediment |
| Examination | Volume status, skin, joint, fundoscopy |
| Point-of-care labs | Creatinine, proteinuria, albumin, Hb, potassium |
| Serology | ANA, anti-dsDNA, ANCA, anti-PLA2R, anti-GBM, ASO, C3, C4, Gd-IgA1 |

### Automatic Calculations

BGDDR automatically:

- Calculates BMI from height and weight.
- Classifies BMI using Asian cutoffs.
- Converts creatinine from umol/L to mg/dL if that unit is selected.
- Derives eGFR when creatinine is entered.
- Stores lab values as longitudinal LabResult rows.

### Good Practice

- Enter dates accurately.
- Use dropdowns rather than free text where available.
- Enter creatinine with the correct unit.
- Record both numeric serology values and qualitative reads when available.
- Use notes only for information that does not fit structured fields.

---

## 9. Follow-up Visits

Open:

- Patient page -> Follow-up
- or `/patients/<id>/followup/`

Each clinic visit should be recorded as a Clinical Encounter.

### Main Fields

| Field | Use |
|---|---|
| Encounter date | Date patient was seen |
| Encounter type | Baseline/enrollment, scheduled follow-up, unscheduled/sick visit |
| Seen by | Clinician responsible for the encounter |
| Clinic location | Clinic/site/room, if needed |
| BP and weight | Longitudinal clinical measures |
| Oedema grade | 0 none to 4 anasarca |
| Symptoms | Frothy urine, haematuria, breathlessness, etc. |
| Clinician response | Clinical assessment at the visit |
| Disease phase | Current phase; can be left blank if workflow sets it |
| Treatment adjusted | Tick if therapy changed |
| Advice | Prints on prescription; Bangla text is supported |
| Next due date | Drives dashboard and worklist |

### After Saving

After a follow-up is saved, you can:

- Write a prescription linked to that visit.
- Order labs.
- Enter lab results.
- Record adverse events.
- Record relapse or admission if relevant.

---

## 10. Laboratory Orders and Results

BGDDR separates ordering tests from receiving results.

### Lab Order

Open:

- Patient page -> Lab order
- or `/patients/<id>/lab-order/`

Use this when tests are requested at a visit.

You can:

- Choose a predefined lab panel.
- Add individual tests.
- Add notes such as urgency or special instructions.

The order links to the encounter and patient. Its status is updated as results
are recorded.

### Lab Results

Open:

- Patient page -> Enter results
- or `/patients/<id>/lab-results/`

Use this when results are available, even if they were not ordered inside BGDDR.

Result groups include:

- Kidney function and urine.
- Immunology/serology.
- Infection screen.
- Metabolic tests.
- Other active tests from the catalog.

### Creatinine and eGFR

Creatinine may be entered in:

- mg/dL
- umol/L

When creatinine is saved, BGDDR stores it canonically in mg/dL and derives eGFR
using CKD-EPI 2021. The latest eGFR is cached on the patient record and is used
in prescription renal-safety checks.

### Proteinuria

Proteinuria values feed remission and outcome logic. Use the most reliable
available measure:

- 24-hour urine total protein when available.
- UPCR as fallback.
- UACR where relevant.

### Qualitative Results

Some tests use qualitative values such as:

- Positive.
- Negative.
- Equivocal.
- Low.
- Normal.
- High.

For serology, enter both the numeric value and the qualitative read when both are
available.

---

## 11. Biopsy and Pathology

Open:

- Patient page -> Biopsy
- or `/patients/<id>/biopsy/`

### Core Biopsy Data

Record:

- Biopsy date.
- Adequacy.
- Number of glomeruli.
- Global sclerosis.
- IFTA.
- Crescents or necrosis.
- Vascular lesions.
- IF pattern.
- EM findings.
- Notes.

### GN Diagnosis

Enter the structured GN diagnosis and broad group. This drives disease-specific
analyses and export variables.

### Disease-Specific Scoring

Where applicable, complete:

- IgA nephropathy: Oxford MEST-C.
- Lupus nephritis: ISN/RPS class and activity/chronicity fields.
- FSGS: variant.
- Membranous nephropathy: stage/features.

### Pathology Review

Open:

- `Pathology -> Biopsy review`
- `/pathology/biopsy/<id>/review/`
- `/pathology/discordant/`
- `/pathology/agreement/`

The pathology section supports local review, central review, adjudication,
discordance tracking, and agreement statistics.

---

## 12. Prescriptions

Open:

- Patient page -> Prescription
- or `/patients/<id>/prescription/`

Prescription is the most important daily workflow. It produces the printable
clinical prescription and updates the research exposure history.

### Before Writing a Prescription

Confirm that:

- The correct patient is open.
- A follow-up encounter exists for the visit date.
- Recent labs are entered if they affect safety decisions.
- Current medications are known.

### Prescription Fields

| Field | Use |
|---|---|
| Diagnosis | Printed diagnosis text |
| Comorbidities | Relevant comorbidities printed on the slip |
| Drug rows | Full current regimen |
| Investigations advised | Tests ordered or advised |
| Advice | General advice; Bangla supported |
| Stop notes | Reasons for stopped medications |

### Medication Rows

For each medication, enter:

- Drug.
- Brand, if needed.
- Strength.
- Dose.
- Route.
- Frequency.
- Timing.
- Duration.
- Bangla instruction.

Leave unused rows blank.

### Always Enter the Full Current Regimen

BGDDR compares the finalized prescription with the patient's open medication
episodes.

| What happens in prescription | What BGDDR does |
|---|---|
| New drug appears | Opens a new exposure episode |
| Same drug and same regimen continues | Keeps episode open |
| Dose/frequency/route changes | Closes old episode and opens a new one |
| Previously open drug is missing | Closes the episode |

If you only enter changed medicines, BGDDR will think the omitted medicines were
stopped. Therefore, every finalized prescription should list all medicines the
patient should continue taking.

### Draft, Preview, and Finalize

1. Save the prescription as a draft.
2. Open Preview.
3. Review diagnosis, medicine rows, advice, investigations, and patient details.
4. Check safety warnings.
5. Finalize only when correct.

Finalization:

- Marks the prescription as final.
- Generates a stable content hash.
- Prevents silent editing of the finalized clinical document.
- Reconciles treatment exposure episodes.
- Enables printing or PDF download.

### Printing and PDF

Use:

- `/prescriptions/<id>/preview/`
- `/prescriptions/<id>/pdf/`
- `/prescriptions/<id>/html/`

The PDF route uses the app's PDF renderer. If PDF dependencies are unavailable,
the HTML version can still be printed from the browser.

### Common Prescription Mistakes

| Mistake | Consequence | Prevention |
|---|---|---|
| Entering only changed drugs | Omitted drugs may be closed as stopped | Enter full current regimen |
| Wrong creatinine unit in labs | eGFR and safety warning may be wrong | Check unit before saving labs |
| Finalizing too early | Final document becomes immutable | Use Preview carefully |
| Missing next due date | Patient may not appear correctly on worklist | Set next due date in encounter |
| Using free text instead of formulary drug | Exposure classification may be incomplete | Choose from DrugMaster dropdown |

---

## 13. Treatment Exposure History

Open:

- Patient page -> Treatment
- or `/patients/<id>/treatment/`

Treatment exposures are research-grade medication episodes. Most in-clinic
exposures are created automatically by prescription reconciliation.

Use manual Treatment entry for:

- Prior medications before registry entry.
- External prescriptions from another clinic.
- Medications known from records but not prescribed in BGDDR.

Manual exposure fields include:

- Drug.
- Dose.
- Frequency.
- Route.
- Start date.
- Stop date.
- Ongoing status.
- Stop reason.

There should be only one ongoing episode per patient per drug. Close an old
episode before adding a new ongoing episode for the same drug.

---

## 14. Consent

Open:

- Patient page -> Consent
- or `/patients/<id>/consent/`

BGDDR stores consent as a versioned, withdrawable record.

### Consent Types

| Type | Meaning |
|---|---|
| Registry | Participation in the registry |
| Biobank | Sample storage |
| Genetic | Genetic testing |
| Imaging | Digital pathology/imaging |
| Trial | Registry-embedded trial participation |

### Recording Consent

1. Choose consent type.
2. Select ICF version.
3. Enter consent date, or leave blank to default to today.
4. Add scope or notes if useful.
5. Save.

When a new consent of the same type is granted, it supersedes the previous
current version. The version chain is retained.

### Withdrawing Consent

Use the Withdraw action beside the current consent. Withdrawal preserves the
history and marks the consent inactive.

### Trial Consent Gate

For randomized trials or studies configured to require trial consent, BGDDR will
not enrol the patient until active Trial consent exists.

---

## 15. Admissions and Relapse

### Admission

Open:

- Patient page -> Admission
- or `/patients/<id>/admission/`

Use Admission for inpatient work-up episodes. Capture:

- Admit date.
- Discharge date.
- Ward.
- Reason.
- Related biopsy.
- Whether baseline was captured before discharge.
- Discharge advice.

### Relapse

Open:

- Patient page -> Relapse
- or `/patients/<id>/relapse/`

Use Relapse to document flare/relapse episodes. Capture:

- Relapse date.
- Relapse type.
- Criteria.
- Action taken.

Recording a relapse also supports outcome and disease-phase tracking.

---

## 16. Adverse Events and Safety

Open:

- Patient page -> Adverse event
- or `/patients/<id>/adverse-event/`
- Sidebar -> Safety

### Adverse Event Fields

| Field | Use |
|---|---|
| Onset date | Date event began |
| Category | Infection, steroid toxicity, haematologic, hepatic, nephrotoxicity, etc. |
| Infection type | Required when category is infection |
| Description | Short clinical description |
| Severity | Mild to fatal |
| Hospitalization | Marks event serious |
| Outcome | Recovered, recovering, ongoing, fatal, etc. |
| Suspected drug | Supports infection/safety by agent analysis |
| Relatedness | Unrelated to definite |
| Encounter | Optional linked visit |
| Notes | Additional details |

BGDDR automatically marks an event serious if:

- Hospitalization is ticked.
- Severity is life-threatening.
- Severity is fatal.

### Safety Pages

| Page | Use |
|---|---|
| `/safety/summary/` | Overall adverse-event summary |
| `/safety/infection-incidence/` | Infection incidence analysis |
| `/safety/study/<code>/` | Study-specific safety summary |

---

## 17. Scheduling and Worklist

Scheduling is driven mainly by encounter `next_due_date`.

Open:

- Sidebar -> Worklist
- `/clinic/worklist/`
- `/scheduling/due/`
- `/scheduling/overdue/`
- `/scheduling/roster/`

Use Worklist to:

- Find patients due today or soon.
- Identify overdue patients.
- Review clinic roster.
- Prioritize follow-up calls.

Good practice:

- Enter a next due date at every follow-up.
- Update the date if the appointment changes.
- Use the worklist at the beginning of clinic.

---

## 18. Studies and Randomization

Open:

- Sidebar -> Studies
- Patient page -> Enrol in study
- `/clinic/studies/`
- `/patients/<id>/enroll/`
- `/studies/<code>/dashboard/`

### Study Types

| Type | Behavior |
|---|---|
| Observational | Enrols eligible patients, no randomization |
| Quasi-experimental | Enrols without random allocation |
| Randomized controlled trial | Requires arms and randomization scheme |

### Enrolling a Patient

1. Open patient.
2. Click Enrol in study.
3. Choose study.
4. Set screened/enrolled dates if needed.
5. Save.

BGDDR then:

- Screens eligibility where coded.
- Checks trial consent if required.
- Randomizes if the study is randomized.
- Records arm, stratum, sequence position, user, and timestamp.

### Study Statuses

| Status | Meaning |
|---|---|
| Planning | Defined but not open |
| Recruiting | Open for enrolment |
| Active | Follow-up ongoing, closed to recruitment |
| Closed | Study closed |

Only studies not closed are listed in the enrolment form.

### Preloaded Study Portfolio

BGDDR includes a preloaded GN/diabetes research portfolio. Examples include:

- BGDDR-REGISTRY.
- ADVANCED-DKD-IGAN.
- HCQ-IGAN-ADVANCED.
- MMF-IGAN.
- MEST-C-PREDICTOR.
- RTX-MN-DOSE.
- LN-IMPLEMENTATION.
- IGAN-BUDESONIDE.
- MN-RTX-CNI.
- FSGS-STEROID-CNI.
- SGLT2-GN.
- FINERENONE-GN.

The administrator can refresh these with:

`python manage.py seed_studies`

---

## 19. Outcomes and Analytics

BGDDR computes outcomes from baseline, lab, event, treatment, and follow-up data.

Open:

- Sidebar -> Analytics
- Patient page -> Recompute outcomes
- `/clinic/analytics/`

### Patient Outcome

Endpoint:

`/analytics/patient/<patient_id>/outcome/`

Use this to inspect one patient's computed outcome row. Add `?recompute=1` to
refresh.

### Cohort Analytics Endpoints

| Endpoint | Purpose |
|---|---|
| `/analytics/cohort/survival/` | Kaplan-Meier survival and log-rank |
| `/analytics/cohort/survival/plot/` | SVG survival plot |
| `/analytics/cohort/cox/` | Cox proportional hazards model |
| `/analytics/cohort/egfr-slope/` | eGFR slope mixed model |
| `/analytics/cohort/cif/` | Competing-risk cumulative incidence |
| `/analytics/cohort/summary/` | Cohort summary table |

### Common Grouping Options

- Diabetes.
- Diagnosis.
- Cohort.
- Drug class, such as `drug:sglt2i` or `drug:hcq`.
- Study arm, such as `study:MN-RTX-CNI`.

### Common Endpoints

- Composite kidney event.
- ESKD.
- Death.
- Sustained 40% eGFR decline.
- Sustained 50% eGFR decline.
- Complete remission.
- Partial remission.
- Any remission.
- IgAN proteinuria response.

### Recomputing Outcomes

Use Recompute outcomes after major data corrections such as:

- Backfilled labs.
- Added hard endpoint events.
- Corrected baseline values.
- Corrected diagnosis.

---

## 20. Data Export

Open:

- Sidebar -> Export
- `/clinic/export/`
- `/exports/research-dataset/`
- `/exports/data-dictionary/`

BGDDR exports a one-row-per-patient research dataset.

### Export Formats

| Format | Use |
|---|---|
| CSV | Plain analysis-ready data |
| Excel | Workbook with dataset and data dictionary |
| SPSS SAV | Labelled SPSS file with variable/value labels |

### De-identified by Default

The standard export excludes direct identifiers. It is suitable for analysis and
sharing within approved research workflows.

### Identified Export

Identified export includes fields such as name/phone/hospital identifiers and is
restricted to Data Manager or equivalent privileged users.

### Command-Line Export

From the app folder:

```powershell
python manage.py export_dataset
python manage.py export_dataset --format xlsx
python manage.py export_dataset --format sav
python manage.py export_dataset --identified --format xlsx
```

Command-line exports are written into the `Exports/` folder.

---

## 21. User and Role Administration

Open:

- Sidebar -> Admin
- `/users/`
- `/users/invite/`
- `/admin/`

### Invite a User

Recommended workflow:

1. Open Users -> Invite user.
2. Enter email.
3. Select role.
4. Save.
5. Send the invitation link to the user.
6. User opens the link and sets a password.

### Manage Existing Users

Administrators can:

- View user list.
- Change role.
- Update profile.
- Reset password.
- Disable accounts by removing active status in the admin.

### Profile

Users can open `/profile/` to edit:

- Department.
- Phone.

---

## 22. Reference Data Administration

Open:

- `/admin/`

The admin site is used for reference data and back-office maintenance.

### Drug Formulary

Admin model:

- Treatments -> Drug masters.

Fields include:

- Generic name.
- Brand names.
- Drug class.
- Available strengths.
- Default frequency.
- Default route.
- Available routes.
- Strengths by route.
- Renal dose adjustment flag.
- eGFR caution threshold.
- Active status.

Drug class is important because analytics uses it to classify exposures.

### Lab Tests

Admin model:

- Labs -> Lab tests.

Fields include:

- Code.
- Name.
- LOINC.
- Default unit.
- Value type.
- Reference range.
- Derived flag.
- Active status.

Do not enter eGFR as a manual test if it is configured as derived. Creatinine
drives eGFR calculation.

### Lab Panels

Admin model:

- Labs -> Lab panels.

Panels allow one-click lab ordering.

### Advice Templates

Admin model:

- Prescriptions -> Advice templates.

Use these for reusable prescription advice snippets such as steroid counseling,
sick-day rules, nephrotic diet, and infection precautions.

### Studies

Admin models:

- Studies -> Studies.
- Studies -> Study arms.
- Studies -> Study enrollments.

For randomized trials, define:

- Study code.
- Title.
- Status.
- Primary endpoint.
- Randomization scheme.
- Block multipliers.
- Stratification variables.
- Random seed.
- Trial consent requirement.
- Arms and allocation ratios.

---

## 23. Backup and Restore

BGDDR is designed for single-user SQLite desktop operation. Data lives beside the
executable unless `BGDDR_DATA_DIR` is set.

### Automatic Backups

The desktop launcher takes:

- One backup at startup.
- Periodic backups while running, default every 6 hours.

Backups are stored in:

`Backups/`

The newest backups are retained according to the configured retention limit.

### Manual Backup

From the app folder:

```powershell
python manage.py backup_db
python manage.py backup_db --list
```

### Restore

Stop BGDDR before restoring.

```powershell
python manage.py restore_db --list
python manage.py restore_db <backup-file-name> --yes
```

Before restore, BGDDR creates a pre-restore safety snapshot so the restore can be
reversed if needed.

### OneDrive Use

If the BGDDR folder is inside OneDrive, data and backups can sync. However:

- Open the app in only one computer at a time.
- Wait for sync to complete before opening on another computer.
- Do not edit or replace `db.sqlite3` while BGDDR is running.

---

## 24. Data Quality and Audit Trail

### Audit Trail

BGDDR records changes with:

- Model/object.
- Action.
- Field name.
- Old value.
- New value.
- User.
- Timestamp.
- Change reason where provided.

API writes can also carry a change reason using the `X-Change-Reason` header.

### Data Quality Checks

Use the Quality page and admin review to look for:

- Duplicate patients.
- Missing baseline assessments.
- Missing next due dates.
- Missing diagnosis.
- Missing consent for trial participants.
- Patients with labs but no baseline.
- Unfinalized prescriptions.
- Open medication episodes that do not match current clinical reality.

### Data Entry Principles

- Prefer dropdown values over free text.
- Enter dates carefully.
- Use correct lab units.
- Finalize prescriptions only after review.
- Keep identifiers accurate.
- Record reasons for stopping important therapies.
- Recompute outcomes after major backfilled data entry.

---

## 25. Troubleshooting

### App Does Not Open

Check:

- Is `BGDDR.exe` blocked by Windows security?
- Is the `_internal` folder present if using the folder build?
- Is another copy already running?
- Is port 8000 already in use?

If port 8000 is busy, set another port before launch:

```powershell
$env:BGDDR_PORT = "8001"
.\BGDDR.exe
```

### Browser Opens but Page Does Not Load

Try:

- Wait 10-20 seconds after launch.
- Refresh the browser.
- Open `http://127.0.0.1:8000/` manually.
- Check `Logs/bgddr.log`.

### Forgot Admin Password

From the app folder:

```powershell
python manage.py changepassword <username>
```

or use another superuser to reset it in Admin -> Users.

### PDF Prescription Fails

Use the HTML prescription route and print from the browser. PDF rendering depends
on local PDF/native libraries; the clinical workflow and HTML print view can
still work.

### Lab Result Does Not Update eGFR

Check:

- The test code is `creatinine`.
- The value is numeric.
- The correct unit was selected.
- Date of birth and sex are present on the patient record.

### Patient Not in Worklist

Check:

- The follow-up encounter has `next_due_date`.
- The date is not blank.
- You are viewing the correct worklist window.

### Study Enrolment Fails

Check:

- Study is not closed.
- Patient meets eligibility rules.
- Trial consent exists if required.
- Patient is not already enrolled in that study.
- RCT arms are configured.

### Export Fails

Check:

- You have permission for the requested export.
- Use de-identified export if you are not a Data Manager.
- For SPSS export, ensure `pyreadstat` is installed in source mode.

---

## 26. Quick Reference

| Task | Where |
|---|---|
| Start app | Double-click `BGDDR.exe` |
| Login | `/login/` |
| Add patient | `/patients/add/` |
| Find patient | Patients page or header quick search |
| Edit patient | Patient page -> Edit |
| Baseline | Patient page -> Baseline |
| Follow-up | Patient page -> Follow-up |
| Lab order | Patient page -> Lab order |
| Enter lab results | Patient page -> Enter results |
| Biopsy | Patient page -> Biopsy |
| Prescription | Patient page -> Prescription |
| Finalize prescription | Prescription preview -> Finalize |
| Prescription PDF | `/prescriptions/<id>/pdf/` |
| Consent | Patient page -> Consent |
| Study enrolment | Patient page -> Enrol in study |
| Adverse event | Patient page -> Adverse event |
| Worklist | `/clinic/worklist/` |
| Analytics | `/clinic/analytics/` |
| Export | `/clinic/export/` |
| Invite user | `/users/invite/` |
| Admin | `/admin/` |
| Backup list | `python manage.py backup_db --list` |
| Restore list | `python manage.py restore_db --list` |

---

## 27. Glossary

| Term | Meaning |
|---|---|
| BGDDR | Bangladesh Glomerular Disease and Diabetes Registry |
| Encounter | A dated clinical visit |
| Baseline | Enrolment-time clinical snapshot |
| LabResult | A dated laboratory value |
| Prescription | Versioned printable clinical document |
| Finalized prescription | Immutable prescription that has been reconciled |
| Treatment exposure | Research medication episode derived from prescriptions or manual entry |
| Reconciliation | Diffing prescription medicines against open exposure episodes |
| eGFR | Estimated glomerular filtration rate |
| UPCR | Urine protein creatinine ratio |
| UACR | Urine albumin creatinine ratio |
| UTP | Urine total protein |
| IFTA | Interstitial fibrosis and tubular atrophy |
| MEST-C | Oxford IgA nephropathy histologic score |
| RCT | Randomized controlled trial |
| SAE | Serious adverse event |
| CIF | Cumulative incidence function |
| ICF | Informed consent form |

---

## Appendix A. Recommended Clinic Checklist

Before clinic:

- Open BGDDR.
- Check Worklist.
- Confirm recent backup exists.
- Confirm printer/PDF workflow if prescriptions will be printed.

For each patient:

- Confirm identity.
- Open patient record.
- Update demographics if needed.
- Record follow-up.
- Enter available labs.
- Record adverse events or admissions.
- Update consent/study enrolment if relevant.
- Write complete current prescription.
- Review and finalize.
- Print or save prescription.
- Confirm next due date.

After clinic:

- Review unfinalized prescriptions.
- Review missing next due dates.
- Check overdue list for follow-up calls.
- Allow OneDrive sync to complete before closing laptop or moving computers.

---

## Appendix B. Administrator Maintenance Checklist

Weekly:

- Confirm backups are being created.
- Review duplicate patient warnings.
- Review user access and inactive accounts.
- Review unfinalized prescriptions.
- Review missing baseline or diagnosis fields.

Monthly:

- Export de-identified research dataset.
- Review data dictionary changes.
- Review study recruitment.
- Review safety summaries.
- Review audit trail for unusual changes.

Before a study opens:

- Confirm study definition.
- Confirm arms and ratios for RCTs.
- Confirm trial consent form version.
- Test enrolment on a non-production/demo patient if available.
- Confirm exports contain required fields.

---

## Appendix C. Files and Folders

Typical desktop package:

```text
BGDDR/
  BGDDR.exe
  _internal/
  db.sqlite3
  Backups/
  Exports/
  Media/
  Logs/
```

| Item | Meaning |
|---|---|
| `BGDDR.exe` | Desktop launcher |
| `_internal/` | Bundled Python/app files for folder build |
| `db.sqlite3` | Main local database |
| `Backups/` | Automatic and manual database backups |
| `Exports/` | Command-line export outputs |
| `Media/` | Uploaded/generated files |
| `Logs/` | Application log files |

Do not delete or move `db.sqlite3` while the app is running.

