# REAL_VERA_HEALTH_INTEGRATION.md

# Real Vera Health Clinical AI Integration

Version: 1.0

Status: Production Integration Specification

Priority: Critical

Target:
Glomerular Disease Expert System (GDES)

---

# Objective

Replace the current Local Simulation Engine with the official Vera Health Clinical AI Platform.

The production integration shall provide an independent, evidence-based clinical review using the official Vera Health API and latest clinical knowledge.

The clinician remains the final decision maker.

---

# High-Level Architecture

Current

GDES
    ↓
Local Simulation
    ↓
Verification

Replace With

GDES
    ↓
Vera Integration Layer
    ↓
Official Vera Health API
    ↓
Clinical AI Engine
    ↓
Evidence Engine
    ↓
Treatment Recommendation
    ↓
Comparison Engine
    ↓
Display Results

---

# Remove Local Simulation

Completely remove all rule-based mock verification logic.

Delete or retire

- Local simulation engine
- Hardcoded medication recommendations
- Mock agreement scoring
- Placeholder confidence scores
- Development treatment rules

Development mode should only indicate API connectivity status.

No clinical recommendation should originate from local simulation rules.

---

# Authentication

Use the dedicated Vera Authentication Service.

Workflow

User clicks

Verify with Vera

↓

If not authenticated

Prompt for email

↓

Authenticate with Vera

↓

Receive

- Access Token
- Refresh Token

↓

Store encrypted refresh token

↓

Automatically reconnect for future sessions

Never store passwords.

---

# API Communication

Implement a dedicated service layer.

Create

services/

vera_client.py

Responsibilities

- Authentication
- Token refresh
- Patient serialization
- API requests
- Response validation
- Error handling
- Logging

No UI component should communicate directly with Vera APIs.

---

# Patient Data Mapping

Automatically send structured patient data.

Include

Patient demographics

Diagnosis

Biopsy

Laboratory values

Vital signs

Current medications

Allergies

Comorbidities

Renal function

Pregnancy status

Previous therapies

Disease activity

Disease severity

Proteinuria

Blood pressure

Immunosuppressive history

All available structured clinical data.

Never require duplicate manual entry.

---

# Vera Clinical Tasks

Request the following analyses.

Diagnosis confirmation

Disease classification

Disease severity

CKD stage

AKI stage

Risk prediction

Medication review

Dose optimisation

Contraindication analysis

Drug interaction review

Monitoring recommendations

Follow-up recommendations

Evidence review

Guideline comparison

Safety review

---

# Personalised Medication Plan

Require Vera to generate patient-specific recommendations.

Drug selection must consider

Age

Sex

Weight

Height

BMI

Body Surface Area

eGFR

Creatinine Clearance

Dialysis

Transplant

Pregnancy

Current medications

Drug allergies

Laboratory abnormalities

Liver function

Relevant comorbidities

Return

Drug

Indication

Recommended dose

Dose range

Frequency

Route

Duration

Renal adjustment

Hepatic adjustment

Monitoring

Contraindications

Interactions

Evidence level

Guideline reference

Clinical rationale

Do not accept generic dosing recommendations when patient-specific dosing is available.

---

# Guideline Requirements

Every recommendation must cite its source.

Supported guideline sources include

KDIGO

ERA

KDOQI

ASN

ISN

ADA

ESC

AHA

NICE

National guidelines

Hospital protocols (future)

Each recommendation must include

Guideline

Version

Recommendation grade

Evidence level

Publication year

Knowledge base version

Reference identifier if available

---

# Explainability

Every recommendation must answer

Why was this treatment recommended?

Why was this drug selected?

Why was this dose selected?

Why were alternatives rejected?

Which patient factors influenced the recommendation?

Which guideline supports it?

Which evidence supports it?

---

# Safety Review

Require Vera to perform

Drug interaction screening

Duplicate therapy detection

Renal dose adjustment

Hepatic dose adjustment

Pregnancy safety

Breastfeeding safety

Paediatric dosing

Geriatric dosing

Maximum dose validation

Contraindication detection

QT prolongation risk

Hyperkalaemia risk

Bleeding risk

Nephrotoxicity review

Vaccination considerations (where applicable)

Required monitoring

---

# Comparison with GDES

Compare

Diagnosis

Risk category

Disease stage

Medication selection

Drug doses

Monitoring

Follow-up

Guideline adherence

Safety

Investigations

Return

Agreement percentage

Differences

Clinical significance

Suggested changes

Reasons for disagreement

Evidence supporting each difference

Do not calculate agreement by counting matching medications.

Agreement should be based on clinical reasoning.

---

# UI Requirements

Replace

Development Mode

with

Connected to Vera Health

Show

Verification Status

Confidence

Agreement

Knowledge Version

Guideline Version

Model Version

Verification Time

Processing Time

API Status

Never display

Mock

Simulation

Placeholder

Fake confidence

Dummy data

---

# Error Handling

If Vera API is unavailable

Display

Unable to contact Vera Health.

Verification could not be completed.

Please try again later.

Do not generate replacement clinical advice locally.

---

# Performance Requirements

Target response time

<5 seconds

Maximum timeout

30 seconds

Retry

One automatic retry

Log failures

Gracefully handle network interruptions

---

# Security

Use HTTPS only.

Validate TLS certificates.

Encrypt all stored tokens.

Never log

Patient identifiers

Access tokens

Refresh tokens

Authentication secrets

Follow

HIPAA

GDPR

Local privacy regulations

---

# Audit Trail

Store

Verification ID

Patient ID

Recommendation ID

Timestamp

Knowledge version

Guideline version

Model version

Agreement score

Verification status

Do not store authentication tokens.

---

# Logging

Log

Authentication success

Authentication failure

API latency

API availability

Verification completed

Verification failed

Do not log protected health information unless required for secure auditing.

---

# Future Extensibility

Design the integration so additional AI engines can be added without changing the UI.

Example providers

Vera Health

OpenAI Clinical (future)

Microsoft Healthcare AI

Hospital-specific AI engines

Institutional guideline engines

Use a provider interface

ClinicalAIProvider

Each provider implements

authenticate()

verify()

generate_treatment_plan()

generate_monitoring_plan()

generate_followup_plan()

compare_with_gdes()

health_check()

This allows switching providers with configuration only.

---

# Acceptance Criteria

✓ Local simulation engine removed.

✓ Official Vera Health API integrated.

✓ Secure authentication implemented.

✓ Automatic token refresh implemented.

✓ Patient data automatically mapped.

✓ Independent Vera clinical reasoning performed.

✓ Patient-specific treatment recommendations generated.

✓ Individualised drug dosing based on age, sex, weight, renal function and other relevant clinical variables.

✓ Comprehensive medication safety review completed.

✓ Evidence and guideline citations returned for every recommendation.

✓ Side-by-side comparison with GDES displayed.

✓ Complete audit trail recorded.

✓ Robust error handling implemented.

✓ Provider architecture supports future clinical AI integrations without redesign.