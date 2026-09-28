# IgA Nephropathy Clinical Pathway Library

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Disease:** IgA Nephropathy / IgA Vasculitis Nephritis (id=`iga`)
**Pathways Model:** `knowledge.models.ClinicalPathway`

---

## 1. Complete 6-Stage Pathway Overview

The IgA Nephropathy clinical pathway defines the complete care journey from initial presentation through ESKD management. All stages are defined in the `ClinicalPathway` model and seeded via `seed_v4_knowledge.py`.

### Text-Based Pathway Diagram

```
STAGE 1: PRESENTATION & DIAGNOSIS
  [Duration: 30 days | 8 required actions]
  |
  v
STAGE 2: RISK STRATIFICATION
  [Duration: 90 days | 7 required actions]
  |
  +--(low risk)--> STAGE 5: LONG-TERM MONITORING
  |                    [Duration: 365 days | 10 required actions]
  |                    |
  |                    +--(progression)--> STAGE 4: IMMUNOSUPPRESSION
  |                    |
  |                    +--(ESKD)--> STAGE 6: ESKD / TRANSPLANT
  |
  +--(high risk)--> STAGE 3: SUPPORTIVE THERAPY
  |                    [Duration: 90 days | 10 required actions]
  |                    |
  |                    +--(persistent proteinuria >1g/d)--> STAGE 4
  |                    |
  |                    +--(adequate response)--> STAGE 5
  |
  +--(crescentic/RPGN)--> STAGE 4: IMMUNOSUPPRESSION
                             [Duration: 180 days | 10 required actions]
                             |
                             +--> STAGE 5: LONG-TERM MONITORING
                             |
                             +--> STAGE 6: ESKD / TRANSPLANT

STAGE 5: LONG-TERM MONITORING
  [Duration: 365 days (repeating) | 10 required actions]
  |
  +--(progression to ESKD)--> STAGE 6: ESKD / TRANSPLANT
                                  [Duration: 365 days (repeating) | 8 required actions]
```

---

## 2. Detailed Per-Stage Breakdown

### Stage 1: Presentation & Diagnosis

| Property | Value |
|----------|-------|
| **Stage ID** | IGA-PATH-01 |
| **Expected Duration** | 30 days |
| **Next Stages** | Stage 2 |

**Required Actions (8):**
1. Urine microscopy for RBC morphology and casts
2. UPCR or ACR quantification (spot or 24-hour)
3. eGFR and serum creatinine measurement
4. Serum albumin, complement levels (C3, C4)
5. Kidney biopsy with immunofluorescence (mesangial IgA)
6. Light microscopy with Oxford MEST-C scoring
7. Electron microscopy for mesangial electron-dense deposits
8. Exclusion of secondary causes (lupus serology, ANCA, HBV/HCV, HIV)

**Criteria to Proceed to Stage 2:**
- Biopsy-confirmed diagnosis of IgA nephropathy (dominant or co-dominant mesangial IgA on IF)
- Complete laboratory baseline established

**Warnings:**
- Delay in biopsy may miss crescentic disease in rapidly progressive cases
- Inadequate IF tissue may miss diagnosis (repeat biopsy if clinically indicated)
- In children, consider non-invasive diagnosis if typical presentation with macroscopic hematuria

### Stage 2: Risk Stratification

| Property | Value |
|----------|-------|
| **Stage ID** | IGA-PATH-02 |
| **Expected Duration** | 90 days |
| **Next Stages** | Stage 3 (high risk), Stage 5 (low risk) |

**Required Actions (7):**
1. Calculate 5-year ESKD risk using International IgAN Prediction Tool
2. Assess Oxford MEST-C score and classify risk category
3. Quantify proteinuria >1g/day despite 90 days of supportive care
4. Check BP control status (<130/80 mmHg target)
5. Evaluate eGFR trajectory (stable vs declining >3 mL/min/1.73m2/year)
6. Assess for clinical indications for immunosuppression
7. Document risk category: low, moderate, high, or crescentic

**Criteria to Proceed:**
- Risk stratification completed with all parameters
- Decision on supportive therapy vs immunosuppression pathway

**Warnings:**
- Risk prediction tools have C-statistics ~0.75-0.82; use as adjunct to clinical judgment
- Rapidly declining eGFR (>5 mL/min/1.73m2/year) may indicate need for urgent immunosuppression regardless of other parameters
- Reassess risk if proteinuria changes >30% from baseline

### Stage 3: Supportive Therapy

| Property | Value |
|----------|-------|
| **Stage ID** | IGA-PATH-03 |
| **Expected Duration** | 90 days |
| **Next Stages** | Stage 4 (if persistent proteinuria >1g/day), Stage 5 (if adequate response) |

**Required Actions (10):**
1. Initiate RAASi (ACEi/ARB) titrated to maximum tolerated dose
2. Add SGLT2i if eGFR >25 mL/min/1.73m2 (dapagliflozin 10mg or empagliflozin 10mg)
3. BP target <130/80 mmHg (consider CCB or diuretic add-on if needed)
4. Dietary salt restriction (<5g NaCl/day)
5. Dietary protein restriction (0.8g/kg/day if progressive CKD)
6. Lifestyle modification: smoking cessation, exercise, weight management
7. Statin therapy if LDL >2.6 mmol/L (>100 mg/dL)
8. Vaccination: influenza (annual), pneumococcal, COVID-19
9. Avoid nephrotoxins (NSAIDs, aminoglycosides, IV contrast with caution)
10. Patient education on disease and monitoring

**Criteria to Proceed:**
- 90 days of optimized supportive therapy completed
- Reassessment of proteinuria and eGFR performed

**Warnings:**
- Monitor for RAASi side effects: hyperkalemia, cough, angioedema
- SGLT2i: hold during acute illness (sick day rules)
- Pregnancy: RAASi contraindicated; discuss contraception
- Declining eGFR >30% after RAASi initiation typically stabilizes; do not discontinue unless symptomatic

### Stage 4: Immunosuppression

| Property | Value |
|----------|-------|
| **Stage ID** | IGA-PATH-04 |
| **Expected Duration** | 180 days |
| **Next Stages** | Stage 5 (after induction), Stage 6 (if ESKD develops) |

**Required Actions (10):**
1. Confirm indication: persistent proteinuria >1g/day after 90 days supportive therapy OR crescentic RPGN
2. Consider corticosteroid course: prednisolone 0.5-1mg/kg/day tapering over 6-8 months (per KDIGO 2021)
3. For crescentic disease: methylprednisolone 1g IV x3 pulses then oral taper
4. Consider enteric budesonide (Nefecon) 16mg/day for appropriate candidates (KDIGO 2025)
5. Consider sparsentan 200-400mg/day for persistent proteinuria (PROTECT trial)
6. Cyclophosphamide for severe crescentic IgAN (rarely needed)
7. MMF as steroid-sparing option (limited evidence in IgAN)
8. Monitor treatment response: monthly eGFR and UPCR during induction
9. Monitor for immunosuppression side effects: infections, glucose, bone density
10. Plan steroid taper duration and schedule

**Criteria to Proceed to Stage 5:**
- Completed 6-month induction course
- Remission assessment: complete (UPCR <0.3), partial (UPCR <1.0), or no response

**Warnings:**
- TESTING trial: full-dose steroids increased serious adverse events (HR 2.53)
- STOP-IgAN: no benefit of immunosuppression in patients with eGFR <30
- Budesonide: primarily gut-acting; limited data in crescentic disease
- Steroid taper over minimum 6 months; abrupt cessation causes adrenal crisis
- Monitor for infection: PCP prophylaxis if on high-dose steroids >4 weeks

### Stage 5: Long-Term Monitoring

| Property | Value |
|----------|-------|
| **Stage ID** | IGA-PATH-05 |
| **Expected Duration** | 365 days (repeating cycle) |
| **Next Stages** | Stage 4 (if relapse), Stage 6 (if ESKD develops) |

**Required Actions (10):**
1. 3-monthly: eGFR, UPCR/ACR, BP measurement
2. 6-monthly: serum albumin, electrolytes
3. Annual: complete blood count, lipid profile, uric acid
4. Monitor for treatment side effects if on immunosuppression
5. Supportive therapy optimization: RAASi, SGLT2i continued
6. Re-evaluate risk stratification annually
7. Assess for re-biopsy indications: unexplained eGFR decline, new active sediment
8. Immunization schedule: influenza annually, pneumococcal according to guidelines
9. Prepare for renal replacement therapy when eGFR <30
10. Consider transplant referral when eGFR <30 and declining

**Warnings:**
- Proteinuria increase >50% from nadir may indicate relapse
- eGFR decline >5 mL/min/1.73m2/year requires re-evaluation
- Pregnancy in IgAN: high-risk; pre-conception counseling needed
- Contrast-induced AKI risk: discuss with radiologist; pre-hydration

### Stage 6: ESKD / Transplantation

| Property | Value |
|----------|-------|
| **Stage ID** | IGA-PATH-06 |
| **Expected Duration** | 365 days (repeating cycle) |
| **Next Stages** | None (terminal stage) |

**Required Actions (8):**
1. Dialysis access planning (AV fistula creation >6 months before anticipated need)
2. AV fistula maturation monitoring
3. Transplant evaluation: cardiac, infectious, urologic workup
4. HLA typing and panel reactive antibody testing
5. Discuss IgA recurrence risk post-transplant (10-50%)
6. Pre-transplant nephrectomy discussion (rarely indicated)
7. Transplant waitlist management
8. If transplanted: monitor for recurrent IgAN (protocol biopsies at 1, 3, 5 years)

**Warnings:**
- Recurrent IgAN: 10-50% at 5 years; graft loss from recurrence ~5-10%
- Risk factors for recurrence: rapid native progression, young age, high MEST-C scores
- No proven therapy for recurrent IgAN; RAASi and SGLT2i mainstay
- Living donor transplantation preferred with appropriate counseling on recurrence

---

## 3. Clinical Workflow Description

The IgA clinical pathway follows the KDIGO 2021/2025 management approach:

1. **Diagnosis triggers pathway entry** - All patients with biopsy-confirmed IgAN enter at Stage 1
2. **Risk assessment determines track** - Stage 2 separates patients into low-risk (directly to monitoring) and high-risk (to supportive therapy)
3. **Supportive therapy is universal** - All patients receive RAASi + SGLT2i optimization
4. **Immunosuppression is selective** - Only for persistent proteinuria >1g/day after supportive therapy, or crescentic disease
5. **Monitoring is lifelong** - Even in remission, patients remain in Stage 5 with periodic reassessment
6. **ESKD pathway** - Timely preparation for RRT and transplantation with recurrence counseling

---

## 4. Pathway Validation Status

| Validation Aspect | Status | Details |
|-------------------|--------|---------|
| Model Implementation | VALIDATED | `ClinicalPathway` model in `knowledge/models.py` |
| Seed Data | VALIDATED | Seeded via `seed_v4_knowledge.py` PATHWAYS dictionary |
| Stage Sequence | VALIDATED | 6 stages with correct ordering and transitions |
| Required Actions | VALIDATED | 8/7/10/10/10/8 actions per stage |
| Duration Values | VALIDATED | 30/90/90/180/365/365 days |
| Next Stage Links | VALIDATED | All transitions validated against clinical logic |
| Criteria to Proceed | VALIDATED | Clinically appropriate transition criteria |
| Warnings | VALIDATED | Safety warnings aligned with KDIGO recommendations |
| Cross-disease Applicability | PLANNED | Templates designed for extension to membranous, lupus, FSGS |

---

## 5. Planned Pathway Expansions

| Disease | Priority | Stage Count | Status |
|---------|----------|-------------|--------|
| Membranous Nephropathy | HIGH | 6 | Template designed, content pending |
| Lupus Nephritis | HIGH | 7 | Template designed, content pending |
| FSGS | MEDIUM | 5 | Template designed, content pending |
| ANCA Vasculitis | MEDIUM | 6 | Template designed, content pending |
| Minimal Change Disease | LOW | 4 | Not yet scoped |
| C3 Glomerulopathy | LOW | 4 | Not yet scoped |

The pathway template pattern (Presentation -> Risk Stratification -> Supportive -> Immunosuppression -> Monitoring -> ESKD) is designed for reuse across all glomerular diseases with disease-specific modifications to actions, durations, and criteria.
