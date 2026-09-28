# Membranous Nephropathy Clinical Pathway Library

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Disease:** Membranous Nephropathy (id=`membranous`)
**Pathways Model:** `knowledge.models.ClinicalPathway`

---

## 1. Complete 6-Stage Pathway Overview

The Membranous Nephropathy clinical pathway defines the complete care journey from initial presentation through ESKD management. All stages are defined in the `ClinicalPathway` model and seeded via `seed_v4_knowledge.py`.

### Text-Based Pathway Diagram

```
STAGE 1: DIAGNOSIS & EVALUATION
  [Duration: 30 days | 8 required actions]
  |
  v
STAGE 2: RISK STRATIFICATION
  [Duration: 14 days | 6 required actions]
  |
  +--(low risk)----> STAGE 3: SUPPORTIVE THERAPY
  |                      [Duration: 30 days | 8 required actions]
  |                      |
  |                      +--(remission)--> STAGE 5: MONITORING & FOLLOW-UP
  |                      |
  |                      +--(persistent proteinuria)--> STAGE 4: IMMUNOSUPPRESSION
  |
  +--(moderate risk)---> STAGE 3: SUPPORTIVE THERAPY
  |                      [Duration: 30 days | 8 required actions]
  |                      |
  |                      +--(persistent nephrotic)--> STAGE 4: IMMUNOSUPPRESSION
  |
  +--(high risk)-------> STAGE 4: IMMUNOSUPPRESSION
  |                      [Duration: 180 days | 8 required actions]
  |                      |
  |                      +--(response)--> STAGE 5: MONITORING & FOLLOW-UP
  |                      |
  |                      +--(no response)--> STAGE 6: RESISTANT / ESKD
  |
  +--(secondary cause)--> Treat underlying cause, then reassess

STAGE 5: MONITORING & FOLLOW-UP
  [Duration: 730 days (repeating) | 8 required actions]
  |
  +--(relapse)---------------> STAGE 4: IMMUNOSUPPRESSION
  |
  +--(progression to ESKD)---> STAGE 6: RESISTANT / ESKD

STAGE 6: RESISTANT DISEASE / ESKD
  [Duration: 365 days (repeating) | 8 required actions]
```

---

## 2. Detailed Per-Stage Breakdown

### Stage 1: Diagnosis & Evaluation

| Property | Value |
|----------|-------|
| **Stage ID** | MEMB-PATH-01 |
| **Expected Duration** | 30 days |
| **Next Stages** | Stage 2 |

**Required Actions (8):**

1. Quantify proteinuria (UPCR or 24-hour urine collection)
2. Serum albumin, eGFR, creatinine measurement
3. Anti-PLA2R antibody testing (ELISA, >20 RU/mL diagnostic)
4. Anti-THSD7A antibody testing if PLA2R-negative
5. Kidney biopsy with light microscopy, immunofluorescence, electron microscopy
6. Exclude secondary causes: malignancy screening (age >60, weight loss), autoimmune serology (ANA, anti-dsDNA), HBV/HCV/HIV serology, drug history review
7. Lipid profile (total cholesterol, LDL, HDL, triglycerides)
8. Assess for VTE risk: D-dimer, lower extremity Doppler if clinically indicated

**Criteria to Proceed to Stage 2:**

- Biopsy-confirmed diagnosis of membranous nephropathy
- Complete baseline laboratory and serologic workup
- Anti-PLA2R/THSD7A status determined
- Secondary causes evaluated

**Warnings:**

- Inadequate biopsy tissue may miss subepithelial deposits; EM is essential for definitive diagnosis
- Anti-PLA2R >20 RU/mL is 95% specific; biopsy may be deferred in high-titer patients with contraindications
- Paraneoplastic MN requires thorough malignancy workup in patients >60 years or with atypical features
- VTE risk is highest among all glomerular diseases; low threshold for imaging

### Stage 2: Risk Stratification

| Property | Value |
|----------|-------|
| **Stage ID** | MEMB-PATH-02 |
| **Expected Duration** | 14 days |
| **Next Stages** | Stage 3 (low/moderate risk), Stage 4 (high risk) |

**Required Actions (6):**

1. Classify KDIGO risk category: low (eGFR>60, UPCR<3.5, albumin>3.0), moderate (eGFR>60, UPCR 3.5-8, albumin 2.0-3.0), high (eGFR<60 or UPCR>8 or albumin<2.0)
2. Assess anti-PLA2R titer level: low (20-200), moderate (200-1000), high (>1000 RU/mL)
3. Calculate Toronto Risk Score for disease progression
4. Evaluate biopsy Ehrenreich-Churg stage and chronicity
5. Assess comorbidity burden: diabetes, cardiovascular disease, malignancy risk
6. Determine treatment eligibility: discuss risks and benefits of immunosuppression

**Criteria to Proceed:**

- Risk category assigned (low, moderate, or high)
- Treatment plan determined based on risk stratification

**Warnings:**

- High anti-PLA2R titers (>1000 RU/mL) predict low spontaneous remission (<10%)
- Rapidly declining eGFR (>5 mL/min/1.73m2/year) may indicate high-risk regardless of proteinuria
- Re-stratify if clinical status changes >30% from baseline
- Patients with secondary MN due to malignancy should follow oncology-directed pathway

### Stage 3: Supportive Therapy

| Property | Value |
|----------|-------|
| **Stage ID** | MEMB-PATH-03 |
| **Expected Duration** | 30 days (with monitoring out to 6 months for low-risk) |
| **Next Stages** | Stage 4 (if persistent nephrotic syndrome), Stage 5 (if remission) |

**Required Actions (8):**

1. Initiate RAASi (ACEi/ARB) titrated to maximum tolerated dose for proteinuria reduction
2. Add SGLT2i if eGFR >25 mL/min/1.73m2 and tolerating RAASi
3. Diuretic therapy for edema management (loop diuretics, thiazides as needed)
4. Anticoagulation for VTE prophylaxis if serum albumin <2.5 g/dL (consider warfarin or DOAC)
5. Statin therapy for dyslipidemia (LDL target <2.6 mmol/L)
6. Dietary counseling: sodium restriction (<2g/day), moderate protein intake (0.8-1.0 g/kg/day)
7. Vaccination: influenza (annual), pneumococcal, COVID-19
8. Patient education: disease nature, monitoring schedule, warning signs (thrombosis, infection)

**Criteria to Proceed:**

- Minimum 3-6 months of optimized supportive therapy for low/moderate risk patients
- If spontaneous remission achieved (UPCR <0.3, albumin >3.5): proceed to Stage 5
- If persistent nephrotic syndrome (UPCR >3.5): proceed to Stage 4 for IS consideration

**Warnings:**

- Anticoagulation decision requires balancing VTE risk vs bleeding risk; discuss with hematology if uncertain
- RAASi may cause hyperkalemia; monitor potassium 1-2 weeks after initiation and dose changes
- SGLT2i: hold during acute illness (sick day rules)
- Spontaneous remission occurs in 20-30% within 2 years; active surveillance is appropriate for low-risk patients

### Stage 4: Immunosuppressive Therapy

| Property | Value |
|----------|-------|
| **Stage ID** | MEMB-PATH-04 |
| **Expected Duration** | 180 days (induction phase, may extend to 24 months for complete response) |
| **Next Stages** | Stage 5 (if response), Stage 6 (if resistant) |

**Required Actions (8):**

1. Confirm indication: moderate-to-high risk primary MN with persistent nephrotic syndrome after 3-6 months supportive therapy
2. Rituximab (first-line): 1g IV x2 doses 2 weeks apart, or 375mg/m2 weekly x4 (per MENTOR protocol)
3. Alternative: Calcineurin inhibitor (Cyclosporine 3.5mg/kg/day or Tacrolimus 0.05-0.1mg/kg/day) for 12 months
4. Alternative: Cyclophosphamide + alternating prednisolone (modified Ponticelli regimen) for severe/rapidly progressive disease
5. Prednisolone taper: 0.5mg/kg/day tapering over 6 months (used with CyP protocol)
6. Monitor PLA2R titers: q1-2 months during induction as early response biomarker
7. Adverse effect monitoring: CBC, LFTs, glucose, BP at each visit during induction
8. Assess treatment response at 6 months: complete remission (UPCR <0.3), partial remission (UPCR <3.5, >50% reduction), no response

**Criteria to Proceed to Stage 5:**

- Completed induction course (minimum 6 months)
- Remission assessment documented
- If no response by 6-12 months, evaluate for Stage 6

**Warnings:**

- Rituximab infusion reactions: premedicate with antihistamine, acetaminophen; have resuscitation equipment available
- Late-onset neutropenia after rituximab: monitor CBC monthly for 6 months post-infusion
- CNI nephrotoxicity: monitor trough levels and eGFR q1-2 weeks during titration
- Cyclophosphamide: cumulative dose limit 36g or 12-week course; monitor for hemorrhagic cystitis, malignancy, gonadal toxicity
- Live vaccines contraindicated during and for 6 months after rituximab

### Stage 5: Monitoring & Follow-up

| Property | Value |
|----------|-------|
| **Stage ID** | MEMB-PATH-05 |
| **Expected Duration** | 730 days (repeating cycle, 2-year main cycle with lifelong monitoring) |
| **Next Stages** | Stage 4 (if relapse), Stage 6 (if ESKD develops) |

**Required Actions (8):**

1. 3-monthly: eGFR, UPCR/ACR, serum albumin, anti-PLA2R titer
2. 6-monthly: BP measurement, tolerability assessment, medication adherence
3. Annual: lipid profile, HbA1c, CBC, LFTs
4. Monitor for relapse: rising PLA2R titers precede clinical relapse by 3-6 months
5. Supportive therapy optimization: continue RAASi, SGLT2i, statins
6. Re-evaluate risk stratification annually or if clinical status changes
7. Malignancy surveillance per age-appropriate guidelines (especially if previous secondary MN)
8. Long-term immunosuppression safety monitoring: infection surveillance, bone density assessment

**Warnings:**

- Rising anti-PLA2R titer predicts relapse with 80-90% sensitivity; consider preemptive therapy in high-risk patients
- VTE risk persists even in remission if nephrotic syndrome recurs
- Pregnancy in MN: high-risk; pre-conception counseling essential; RAASi must be discontinued
- Immunosuppression-related infections: PCP prophylaxis if on steroids >4 weeks or CNI + steroid combination
- Relapse rates after rituximab: 25-40% at 5 years; ongoing monitoring required even after successful remission

### Stage 6: Resistant Disease / ESKD

| Property | Value |
|----------|-------|
| **Stage ID** | MEMB-PATH-06 |
| **Expected Duration** | 365 days (repeating cycle) |
| **Next Stages** | None (terminal stage) |

**Required Actions (8):**

1. Define treatment resistance: failure to achieve partial or complete remission after at least 2 lines of immunosuppression (e.g., rituximab + CNI or CyP)
2. Re-biopsy to assess chronicity and rule out alternative diagnosis or superimposed disease
3. Consider repeat anti-PLA2R titer to determine if immunologic non-response
4. Evaluate for second-line IS: consider MMF for steroid-sparing, calcineurin inhibitor switch, or low-dose IL-2 trial
5. Dialysis access planning when eGFR <20-25 mL/min/1.73m2
6. Transplant evaluation: assess for recurrence risk (30-40% in primary MN), determine timing
7. Pre-transplant anti-PLA2R titer check: high titers associated with post-transplant recurrence
8. If transplanted: monitor for recurrent MN (protocol biopsies or PLA2R surveillance); consider rituximab preemptive

**Warnings:**

- Resistant MN has poor prognosis: 50% progress to ESKD within 5-10 years
- Post-transplant recurrence rate 30-40% in primary MN; highest in first 2 years
- High pre-transplant anti-PLA2R titers predict recurrence; consider pre-transplant rituximab
- Malignancy screening intensified in treatment-resistant patients (paraneoplastic MN may present late)
- No standard third-line therapy exists; enrollment in clinical trials recommended

---

## 3. Clinical Workflow Description

The Membranous Nephropathy clinical pathway follows the KDIGO 2021 Chapter 6 management approach:

1. **Diagnosis triggers pathway entry** - All patients with biopsy-confirmed MN enter at Stage 1
2. **Risk stratification determines IS timing** - Stage 2 separates patients into low-risk (watchful waiting with supportive therapy), moderate-risk (supportive first, IS if persistent), and high-risk (prompt IS initiation)
3. **Supportive therapy is universal** - All patients receive RAASi + SGLT2i optimization, diuretics, anticoagulation if indicated
4. **Rituximab is first-line immunosuppression** - Stage 4 offers risk-stratified IS with rituximab as preferred agent per MENTOR trial
5. **PLA2R-guided monitoring** - Stage 5 leverages anti-PLA2R titers as early biomarker for relapse prediction
6. **Resistant disease pathway** - Stage 6 addresses treatment resistance with re-biopsy, alternative agents, and transplant evaluation

---

## 4. Pathway Validation Status

| Validation Aspect | Status | Details |
|-------------------|--------|---------|
| Model Implementation | VALIDATED | `ClinicalPathway` model in `knowledge/models.py` |
| Seed Data | VALIDATED | Seeded via `seed_v4_knowledge.py` PATHWAYS dictionary |
| Stage Sequence | VALIDATED | 6 stages with correct ordering and transitions |
| Required Actions | VALIDATED | 8/6/8/8/8/8 actions per stage |
| Duration Values | VALIDATED | 30/14/30/180/730/365 days |
| Next Stage Links | VALIDATED | All transitions validated against clinical logic |
| Criteria to Proceed | VALIDATED | Clinically appropriate transition criteria |
| Warnings | VALIDATED | Safety warnings aligned with KDIGO and Toronto Consensus recommendations |

---

## 5. Cross-Disease Applicability

| Disease | Priority | Stage Count | Status |
|---------|----------|-------------|--------|
| Lupus Nephritis | HIGH | 7 | Template designed, content pending |
| FSGS | MEDIUM | 5 | Template designed, content pending |
| ANCA Vasculitis | MEDIUM | 6 | Template designed, content pending |
| Minimal Change Disease | LOW | 4 | Not yet scoped |
| C3 Glomerulopathy | LOW | 4 | Not yet scoped |

The pathway template pattern (Diagnosis -> Risk Stratification -> Supportive -> Immunosuppression -> Monitoring -> Resistant/ESKD) is designed for reuse across all glomerular diseases with disease-specific modifications to actions, durations, and criteria.
