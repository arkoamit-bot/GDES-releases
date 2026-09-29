# GDES_VERA_MANUAL_REVIEW_UI_UPDATE.md

# GDES Vera Manual Review UI Enhancement

Version: 1.1

Status: Production Ready

Priority: High

Target Module:
Patient Detail → Personalized Management Plan → Vera Integration

---

# Objective

Improve the Vera Health integration so that it accurately represents the current workflow.

GDES generates the complete clinical recommendation.

Vera is an optional, independent external clinical AI that the clinician may consult manually.

The interface must never imply that Vera has analysed the patient unless Vera has actually done so.

---

# Design Principles

The interface must clearly distinguish

• GDES Clinical Recommendation

from

• Independent Vera Review

Avoid any wording that could mislead clinicians into believing Vera has automatically reviewed the patient.

---

# Replace Header

Current

Vera Consulted

Replace With

Independent Vera Review

or

Vera Health Review

Never display

Vera Consulted

because no automated consultation has occurred.

---

# Account Information

Replace

Vera Consulted

arko.amit@gmail.com

with

--------------------------------

Vera Health

Account

arko.amit@gmail.com

Status

Ready for Independent Review

--------------------------------

If no email exists

Display

Not Connected

---

# Review Status

Replace

Manual Review Required

with

Independent Clinical Review

Display

GDES has generated an evidence-based treatment recommendation using current clinical guidelines.

If desired, obtain an independent clinical opinion from Vera Health before finalising management.

The treating physician remains responsible for all clinical decisions.

---

# New Case Summary Card

Insert before

Open Vera Health Website

Display

================================================

Case Summary

Diagnosis

IgA Nephropathy

Patient

45 years

Male

Weight

72 kg

eGFR

71.9 mL/min/1.73m²

Proteinuria

1.8 g/day

Blood Pressure

126/78 mmHg

================================================

Populate automatically from patient data.

---

# Open Vera Button

Replace

Open Vera Health Website

with

Open Vera for Independent Review

Description

Launches Vera Health in the default browser.

Authentication and review occur entirely within Vera.

No patient data are transmitted automatically.

---

# Information Box

Display

================================================

About Vera Review

GDES recommendations are generated from the integrated clinical knowledge base.

Vera Health is an independent external clinical AI.

Review the case in Vera if an additional opinion is desired.

================================================

---

# After Returning From Vera

Add

Button

✓ Vera Review Completed

Selecting this button opens

================================================

Independent Review Summary

Did Vera suggest any changes?

○ No changes

○ Minor changes

○ Major changes

================================================

---

# If No Changes

Store

Independent review completed.

No clinically significant changes recommended.

Timestamp

Reviewer

Patient ID

---

# If Changes Were Suggested

Allow clinician to document

Medication Changes

Dose Changes

Monitoring Changes

Follow-up Changes

Diagnostic Changes

Additional Comments

Save in audit trail.

---

# Vera Comparison Placeholder

Add new panel

================================================

Independent Vera Findings

No imported Vera recommendations.

Current version supports manual review only.

Future versions will support structured comparison through official Vera integration.

================================================

---

# Audit Trail

Record

Review completed

Review date

Reviewer

Vera account

Summary

Clinical comments

Do not store

Passwords

OTP

Browser session

Cookies

---

# Browser Launch

Button

Open Vera for Independent Review

Automatically

Open default browser

Navigate to Vera login page

Do not

Inject JavaScript

Read browser cookies

Automate login

Capture OTP

Scrape Vera pages

---

# Future Ready

Design UI so the following can be added later without redesign

Automatic Vera import

Treatment comparison

Dose comparison

Guideline comparison

Agreement score

Evidence comparison

Clinical reasoning comparison

---

# UI Layout

================================================

GDES Clinical Recommendation

------------------------------------------------

Treatment Plan

Monitoring

Contraindications

Evidence

================================================

Independent Vera Review

------------------------------------------------

Account

Status

Case Summary

About Vera Review

Open Vera for Independent Review

✓ Vera Review Completed

Independent Review Summary

================================================

---

# Visual Indicators

Green

Review completed

Blue

Ready for review

Grey

Not connected

Never display

Fake confidence

Mock verification

Placeholder recommendation

Simulated agreement

Artificial comparison

---

# Acceptance Criteria

✓ "Vera Consulted" removed.

✓ Clear distinction between GDES and Vera.

✓ Account status displayed.

✓ Independent review explanation added.

✓ Automatic patient summary generated.

✓ Browser opens Vera website.

✓ No patient data automatically transmitted.

✓ Clinician can document Vera review outcome.

✓ Review stored in audit trail.

✓ UI prepared for future official Vera integration.

✓ No misleading wording implying Vera has analysed the patient.