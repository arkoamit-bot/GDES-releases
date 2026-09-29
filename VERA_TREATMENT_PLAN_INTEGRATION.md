# VERA_TREATMENT_PLAN_INTEGRATION.md

# Vera Health Advanced Treatment Recommendation Integration

Version: 2.0

Status: Implementation Ready

Priority: Critical

Target System:
Glomerular Disease Expert System (GDES)

---

# Objective

Upgrade the Vera Health integration from a simple "verification engine" into an independent AI clinical consultant.

Vera should not only verify the GDES management plan, but also independently generate a complete, evidence-based treatment recommendation using patient-specific clinical data.

The clinician can then compare:

• GDES Recommendation
• Vera Recommendation

before making the final decision.

The clinician always retains responsibility for patient management.

---

# Overall Workflow

Current

GDES
    ↓
Verify with Vera
    ↓
Verification Only

Replace with

GDES Recommendation
        ↓
Verify with Vera
        ↓
Vera independently analyses patient
        ↓
Vera returns

• Diagnosis
• Disease severity
• Risk category
• Treatment recommendation
• Drug doses
• Monitoring plan
• Follow-up plan
• Guideline references
• Agreement with GDES

---

# Vera Input Data

When "Verify with Vera" is clicked, automatically send all relevant patient data.

Never require manual re-entry.

---

## Patient Demographics

Age

Sex

Weight (kg)

Height (cm)

BMI

Body Surface Area

Pregnancy status

Ethnicity (if relevant)

Smoking status

Alcohol use

---

## Kidney Disease

Primary diagnosis

Disease subtype

Disease phase

Biopsy findings

Disease duration

Current CKD Stage

AKI status

Dialysis status

Transplant status

---

## Laboratory Data

Serum Creatinine

eGFR

UACR

UPCR

24-hour Urine Protein

Albumin

Potassium

Sodium

Bicarbonate

Calcium

Phosphate

Magnesium

Hemoglobin

WBC

Platelets

HbA1c

Glucose

CRP

ESR

Liver Function Tests

Lipid Profile

Urinalysis

Urine Microscopy

Complement Levels

ANA

ANCA

Anti-GBM

PLA2R

Anti-dsDNA

Other disease-specific biomarkers

---

## Vital Signs

Blood Pressure

Heart Rate

Temperature

Weight

Recent Weight Change

---

## Current Medication

Medication

Dose

Frequency

Route

Start Date

Indication

Known allergies

Drug intolerances

---

## Comorbidities

Diabetes

Hypertension

Heart Failure

Coronary Disease

Stroke

Liver Disease

Cancer

Pregnancy

Active Infection

Other significant conditions

---

# Vera Clinical Analysis

Vera should independently determine

Diagnosis

Disease Activity

Disease Severity

CKD Stage

AKI Stage

Risk Category

Prognosis

Need for Hospital Admission

Need for Urgent Referral

Need for Biopsy

Need for Additional Investigation

Need for Medication Adjustment

---

# Vera Treatment Plan

Generate a structured treatment plan.

---

## Medication Recommendation

For every medication include

Drug Name

Indication

Recommended Dose

Maximum Dose

Dose Frequency

Route

Duration

Monitoring Requirements

Contraindications

Drug Interactions

Evidence Level

Guideline Reference

Clinical Notes

---

Example

Drug

Losartan

Recommended Dose

50 mg once daily

Suggested Range

25–100 mg/day

Dose Adjustment

Recommended due to eGFR 42 mL/min/1.73m²

Monitoring

Creatinine

Potassium

Blood Pressure

Evidence

KDIGO 2024

---

# Dose Individualisation

Drug doses must be personalised using

Age

Sex

Weight

Height

BMI

Body Surface Area

eGFR

Creatinine Clearance

Dialysis Status

Transplant Status

Liver Function

Pregnancy

Drug Allergies

Current Medications

Relevant Laboratory Values

Never return a generic drug dose if patient-specific dosing is available.

---

# Medication Safety

Vera should automatically check

Drug Interactions

Duplicate Therapy

Maximum Dose

Renal Dose Adjustment

Hepatic Dose Adjustment

Pregnancy Safety

Paediatric Dosing

Geriatric Dosing

QT Prolongation Risk

Hyperkalaemia Risk

Bleeding Risk

Nephrotoxicity

Contraindications

High-Risk Medications

Monitoring Requirements

---

# Monitoring Plan

Recommend

Laboratory monitoring

Blood pressure monitoring

Weight monitoring

Urine protein monitoring

Medication monitoring

Adverse event monitoring

Suggested monitoring intervals

---

# Follow-up Plan

Recommend

Follow-up interval

Required investigations

Expected treatment targets

Criteria for escalation

Criteria for admission

Criteria for referral

---

# Guideline References

Each recommendation should include

Guideline

Version

Recommendation Grade

Evidence Level

Publication Year

Knowledge Base Version

---

Example

KDIGO 2024

Recommendation Grade

1B

Evidence

High

---

# GDES Comparison

Automatically compare

Diagnosis

Risk Stratification

Medication

Dose

Monitoring

Follow-up

Safety

Investigations

Guideline Compliance

Agreement Percentage

Highlight every difference.

---

Example

Drug

Mycophenolate

GDES

500 mg twice daily

Vera

750 mg twice daily

Reason

Dose adjusted for body weight and eGFR.

---

# Confidence

Provide

Overall Confidence

Diagnosis Confidence

Treatment Confidence

Dose Confidence

Monitoring Confidence

Display as percentages.

---

# Explainability

Every recommendation must include

Clinical reasoning

Supporting guideline

Evidence

Patient-specific factors

Why this dose was selected

Why alternative drugs were not selected

---

# Traceability

Every recommendation should include

Recommendation ID

Knowledge Base Version

Guideline Version

Verification Timestamp

Verification Engine

Model Version

---

# UI Layout

Display

================================================

GDES Recommendation

================================================

Treatment Plan

[...]

================================================

Verify with Vera

================================================

Vera Clinical Review

Diagnosis

Risk Assessment

Treatment Recommendation

Medication Recommendations

Personalised Drug Doses

Monitoring Plan

Follow-up Plan

Safety Checks

Evidence

Agreement with GDES

Clinical Differences

================================================

---

# Future Support

Design architecture to support

KDIGO

ERA

ASN

KDOQI

ISN

ADA

ESC

AHA

NICE

Country-specific guidelines

Hospital protocols

without architectural changes.

---

# Development Requirements

Create

services/vera_client.py

services/vera_mapper.py

services/vera_comparison.py

services/vera_dosing.py

services/vera_safety.py

services/vera_guidelines.py

services/vera_monitoring.py

services/vera_followup.py

Keep Vera integration isolated from UI code.

---

# Testing

Implement automated tests for

✓ API request mapping

✓ Patient data serialization

✓ Dose calculation validation

✓ Renal dose adjustment

✓ Weight-based dosing

✓ Age-based dosing

✓ Sex-specific recommendations

✓ Drug interaction detection

✓ Contraindication detection

✓ Guideline comparison

✓ Agreement scoring

✓ Monitoring recommendations

✓ Follow-up recommendations

Target overall test coverage >95%.

---

# Acceptance Criteria

✓ One-click verification.

✓ All relevant patient data automatically transmitted.

✓ Independent Vera clinical assessment.

✓ Patient-specific medication recommendations.

✓ Drug doses individualised using age, sex, weight, renal function and other relevant clinical variables.

✓ Automatic renal dose adjustment.

✓ Comprehensive medication safety review.

✓ Monitoring and follow-up plans generated.

✓ Every recommendation linked to supporting guidelines and evidence.

✓ Side-by-side comparison between GDES and Vera.

✓ Full audit trail and traceability.

✓ Extensible architecture for future guideline and AI engine updates.