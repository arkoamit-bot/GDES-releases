# Transplant Glomerulopathy - Clinical Pathway Specification
**Document ID:** TG-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways
---
## 1. Document Purpose
6-stage clinical pathway for transplant glomerulopathy management.
---
## 2. Pathway Overview
```
STAGE 1: Diagnosis & Biopsy Confirmation (14d) -> STAGE 2: Risk Stratification & Prognostication (7d) -> STAGE 3: Immunosuppression Optimisation (30d) -> STAGE 4: Renoprotection & Proteinuria Management (90d) -> STAGE 5: Long-Term Monitoring & Surveillance (365d) -> STAGE 6: Advanced CKD, Dialysis & Retransplant Planning (365d)
```
## 01. Diagnosis & Biopsy Confirmation
**Duration:** 14 days
**Goal:** Confirm TG with transplant biopsy (EM for CG) and assess DSA, C4d, Banff scores.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| TG-A01 | Perform for-cause transplant biopsy | eGFR decline + proteinuria | KB-TG-DX-01 |
| TG-A02 | EM for GBM double contours (CG score) | Essential for diagnosis | KB-TG-DX-02 |
| TG-A03 | C4d immunofluorescence (peritubular capillaries) | Supports ABMR | KB-TG-DX-04 |
| TG-A04 | DSA screening (Luminex single-antigen bead) | Identify ABMR-mediated TG | KB-TG-DX-03 |
| TG-A05 | Exclude CNI toxicity, HCV, TMA as alternative causes | Non-ABMR TG | KB-TG-PR-04 |
**Next stages:** TG-PATH-02
**Criteria to proceed:** CG lesion confirmed by EM; DSA and C4d status known
## 02. Risk Stratification & Prognostication
**Duration:** 7 days
**Goal:** Stage TG by Banff cg score, proteinuria level, and DSA characteristics.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| TG-A06 | Grade CG: cg0-cg3 by % capillary loops involved | Banff classification | KB-TG-DX-05 |
| TG-A07 | Quantify proteinuria (UPCR or 24h urine) | Prognostic marker | KB-TG-PROG-03 |
| TG-A08 | Assess DSA MFI, C1q binding, subclass (IgG3) | Risk stratification | KB-TG-PR-03 |
| TG-A09 | Calculate risk of graft loss (cg3 = imminent) | Prognosis | KB-TG-PROG-02 |
| TG-A10 | Assess for concurrent TCMR or mixed rejection | Biopsy review | KB-TG-PATH-03 |
**Next stages:** TG-PATH-03
**Criteria to proceed:** Banff cg score assigned; DSA and proteinuria quantified
## 03. Immunosuppression Optimisation
**Duration:** 30 days
**Goal:** Optimise immunosuppression: CNI minimisation, DSA-targeted therapy.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| TG-A11 | Reduce CNI to lowest effective trough (tac 3-5) | Minimise nephrotoxicity | KB-TG-TX-06 |
| TG-A12 | DSA+: IVIG 2g/kg divided over 2-4 days, repeat q4w | ABMR treatment | KB-TG-TX-02 |
| TG-A13 | Inadequate DSA response: add rituximab 375mg/m2 | Refractory ABMR | KB-TG-TX-03 |
| TG-A14 | Consider belatacept conversion if eligible (EBV+) | CNI-free IS | KB-TG-TX-07 |
| TG-A15 | Assess and address non-adherence | Common cause of DSA | KB-TG-TX-01 |
**Next stages:** TG-PATH-04
**Criteria to proceed:** CNI dose optimised; DSA therapy initiated if indicated
## 04. Renoprotection & Proteinuria Management
**Duration:** 90 days
**Goal:** Antiproteinuric therapy, BP control, and metabolic management.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| TG-A16 | ACEi/ARB initiate and titrate to max tolerated dose | Antiproteinuric | KB-TG-TX-04 |
| TG-A17 | Add SGLT2i (dapagliflozin 10mg) if eGFR >=25 | Renoprotection | KB-TG-TX-05 |
| TG-A18 | BP target <130/80 mmHg | CKD management | KB-TG-TX-04 |
| TG-A19 | Diuretics for oedema (furosemide) | Nephrotic syndrome | KB-TG-TX-01 |
| TG-A20 | Screen for NODAT; manage glycaemia | Metabolic care | KB-TG-PATH-04 |
**Next stages:** TG-PATH-05
**Criteria to proceed:** Max tolerated antiproteinuric therapy established
## 05. Long-Term Monitoring & Surveillance
**Duration:** 365 days
**Goal:** Ongoing monitoring of graft function, proteinuria, and DSA.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| TG-A21 | eGFR + UPCR every 3 months | Standard monitoring | KB-TG-MON-01 |
| TG-A22 | DSA screening every 6 months (q3mo if rising MFI) | Surveillance | KB-TG-MON-02 |
| TG-A23 | CNI trough monitoring every 3 months | Toxicity prevention | KB-TG-MON-04 |
| TG-A24 | Repeat biopsy if rapid eGFR decline or DSA surge | Assess progression | KB-TG-MON-03 |
| TG-A25 | Cardiovascular risk assessment (annual lipids, HbA1c, BP) | CKD CV risk | KB-TG-PROG-01 |
**Next stages:** TG-PATH-06
**Criteria to proceed:** Monitoring schedule established; no rapid decline
## 06. Advanced CKD, Dialysis & Retransplant Planning
**Duration:** 365 days
**Goal:** Prepare for dialysis initiation and/or retransplantation.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| TG-A26 | eGFR <20: initiate dialysis planning (AVF/PD) | ESKD preparation | KB-TG-PROG-01 |
| TG-A27 | Assess retransplant candidacy | Feasible if DSA manageable | KB-TG-PROG-04 |
| TG-A28 | DSA desensitisation pre-retransplant (IVIG/PLEX/rituximab) | Reduce recurrence | KB-TG-TX-02 |
| TG-A29 | Avoid DQ mismatches if possible for retransplant | Prevent de novo DSA | KB-TG-PR-03 |
| TG-A30 | Palliative care referral if not retransplant candidate | Symptom management | KB-TG-PROG-01 |
**Next stages:** N/A (final stage)
**Criteria to proceed:** Dialysis access established or retransplant workup complete
---