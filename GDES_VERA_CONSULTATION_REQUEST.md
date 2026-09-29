# GDES_VERA_CONSULTATION_REQUEST.md

# GDES → Vera Structured Clinical Consultation Request

**Version:** 1.0  
**Priority:** High  
**Status:** Clinical Workflow Enhancement  
**Target Module:** Personalized Management Plan → Consult Vera Health

---

# Objective

Transform the current "Open Vera Health" workflow into a structured clinical consultation.

Instead of simply opening the Vera website, GDES shall automatically generate a comprehensive, structured consultation note that the clinician can copy, print, or upload into Vera.

The consultation request should resemble a formal nephrology referral from one specialist to another.

The objective is to provide Vera with complete clinical context so it can generate a personalised, evidence-based management plan.

---

# Clinical Workflow

Current

```
Generate GDES Plan
        ↓
Open Vera Website
        ↓
Manual Review
```

Replace with

```
Generate GDES Plan
        ↓
Generate Vera Consultation Request
        ↓
Preview Consultation Note
        ↓
Copy / Print / Export
        ↓
Open Vera Website
        ↓
Paste Consultation
        ↓
Receive Independent Opinion
        ↓
Clinician Reviews Both Plans
        ↓
Final Clinical Decision
```

---

# New Button

Replace

```
Open Vera Health Website
```

with

```
Generate Vera Consultation
```

After the consultation note is generated, provide

```
Copy Consultation

Open Vera Health

Print Consultation

Export PDF
```

---

# Consultation Document Structure

## 1. Consultation Header

Display

```
Independent Clinical Consultation Request

Requesting System
Glomerular Disease Expert System (GDES)

Consultation Type
Independent AI Clinical Review

Purpose
Development of an evidence-based personalised treatment plan.

Generated

Date

Time

Case ID

Patient Identifier
```

---

## 2. Patient Demographics

Automatically include

- Age
- Sex
- Height
- Weight
- BMI
- Body Surface Area
- Ethnicity (if available)
- Pregnancy status
- Smoking status
- Relevant family history

---

## 3. Primary Diagnosis

Include

Primary renal diagnosis

Disease subtype

Date of diagnosis

Disease duration

Current disease phase

Disease activity

Histological diagnosis

Pathology classification

Oxford MEST-C

ISN/RPS

NIH Activity Index

NIH Chronicity Index

Any disease-specific pathology scores

---

## 4. Presenting Clinical Features

Automatically summarise

Symptoms

Signs

Blood pressure

Oedema

Proteinuria

Haematuria

Nephrotic syndrome

AKI

CKD

Systemic manifestations

Disease progression

---

## 5. Laboratory Summary

### Kidney Function

Serum creatinine

eGFR

Blood urea

Creatinine trend

---

### Urine

UPCR

UACR

24-hour urine protein

Urinalysis

Microscopy

---

### Electrolytes

Sodium

Potassium

Bicarbonate

Calcium

Phosphate

Magnesium

---

### Haematology

Haemoglobin

White cells

Platelets

---

### Biochemistry

Albumin

Liver function

Lipids

HbA1c

CRP

ESR

---

### Immunology

ANA

ANCA

Anti-GBM

PLA2R

C3

C4

dsDNA

Other disease-specific biomarkers

---

## 6. Current Medications

For every medication include

Drug

Dose

Frequency

Route

Duration

Indication

---

## 7. Drug Allergies

Automatically include

Drug

Reaction

Severity

---

## 8. Comorbidities

Include

Diabetes

Hypertension

Heart failure

Coronary artery disease

Liver disease

Malignancy

Pregnancy

Active infection

Previous transplant

Dialysis

Other significant illnesses

---

## 9. Current GDES Clinical Assessment

Automatically summarise

Disease severity

CKD stage

AKI stage

Risk category

Prognosis

Current response to treatment

Evidence supporting diagnosis

---

## 10. Current GDES Management Plan

Summarise

Supportive care

Immunosuppressive therapy

Blood pressure target

Proteinuria target

Lifestyle advice

Monitoring

Follow-up

Contraindicated medications

Expected treatment goals

---

# Consultation Questions to Vera

Display the following request exactly.

---

## Independent Clinical Review Requested

Please independently review this patient and provide your evidence-based clinical opinion.

---

### Diagnosis

Please confirm or revise the diagnosis.

Identify any alternative diagnoses.

Recommend any additional investigations if required.

---

### Disease Severity

Assess

Disease activity

Chronicity

Risk category

CKD stage

AKI stage

Long-term prognosis

---

### Personalised Treatment Plan

Please generate a complete treatment plan.

Include

First-line therapy

Second-line therapy

Rescue therapy

Supportive therapy

Lifestyle recommendations

Patient education

Vaccination recommendations where appropriate

---

### Personalised Drug Dosing

Please individualise all medication doses based on

Age

Sex

Height

Weight

BMI

Body surface area

Renal function

eGFR

Liver function

Pregnancy status

Drug allergies

Current medications

Relevant comorbidities

For every medication provide

Drug

Recommended dose

Frequency

Route

Duration

Renal adjustment

Hepatic adjustment

Monitoring

Clinical rationale

---

### Medication Safety Review

Please evaluate

Drug interactions

Contraindications

Duplicate therapy

Renal dose adjustment

Pregnancy safety

Geriatric considerations

Paediatric considerations

Monitoring requirements

Important adverse effects

---

### Monitoring Plan

Recommend

Laboratory monitoring

Monitoring frequency

Treatment targets

Alert thresholds

---

### Follow-up

Recommend

Follow-up interval

Required investigations

Escalation criteria

Referral criteria

Hospitalisation criteria if applicable

---

### Evidence

For every recommendation provide

Guideline

Version

Recommendation grade

Evidence level

Supporting trial

Publication year

---

### Comparison with GDES

Please compare your recommendations with the attached GDES management plan.

Highlight

Areas of agreement

Areas of disagreement

Suggested modifications

Clinical rationale

---

### Overall Opinion

Please provide

Summary

Important clinical considerations

Safety concerns

Additional recommendations

---

# Footer

Automatically append

```
This consultation request was generated automatically by the
Glomerular Disease Expert System (GDES).

The enclosed GDES recommendations are intended to provide
clinical context and should not influence an independent review.

Please generate an entirely independent evidence-based opinion.

Final clinical responsibility remains with the treating physician.
```

---

# User Interface

Buttons

```
Preview Consultation

Copy Consultation

Print Consultation

Export PDF

Open Vera Health
```

---

# Export Formats

Support

- Clipboard
- PDF
- DOCX
- Plain text

---

# Future Compatibility

The consultation generator shall be independent of Vera.

Future destinations may include

- Vera Health
- ChatGPT Clinical
- Claude Clinical
- Microsoft Healthcare AI
- Hospital Expert Systems
- Human nephrology consultation

No redesign should be required.

---

# Acceptance Criteria

✓ Structured consultation note automatically generated.

✓ All available clinical data automatically populated.

✓ Complete GDES management plan included.

✓ Standardised clinical questions generated.

✓ Personalised dosing request included.

✓ Guideline and evidence request included.

✓ Ready for copy, print, PDF, or DOCX export.

✓ Compatible with future AI consultation platforms.

✓ No manual rewriting of case summaries required.