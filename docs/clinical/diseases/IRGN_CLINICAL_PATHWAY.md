# Infection-Related Glomerulonephritis (IRGN) — Clinical Pathway Specification

**Document ID:** IRGN-CP-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Clinical Pathways  

---

## 1. Document Purpose

This document defines the complete 6-stage clinical pathway for Infection-Related Glomerulonephritis management within the BGDDR v4.1 decision support framework. Each stage specifies duration, actions, decision points, and integration with KB rules.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis & Classification (0-14 days)
   |   Actions: D1-D6
   v
STAGE 2: Acute Management & Supportive Care (0-30 days)
   |   Actions: S1-S6
   v
+----+----+----+----+----+
|                        |
Resolution           Atypical/Refractory
   |                        |
STAGE 3:              STAGE 4:
Monitoring for        Atypical/Refractory
Resolution (90d)      Immunosuppression (180d)
   |                        |
   +----+----+----+----+----+
               |
          +----+----+
          |         |
    Crescentic/   Long-Term
    RPGN (5)      Follow-Up (6)
          |
STAGE 5: Crescentic/RPGN: Intensive Therapy (90d)
          |
          v
STAGE 6: Long-Term Follow-Up & Outcomes (365d+)
   Actions: F1-F7
```


## 01. Diagnosis and Classification

**Duration:** 14 days  
**Goal:** Establish diagnosis of IRGN: confirm acute nephritic syndrome, latent period, low C3 with normal C4, evidence of infection. Classify by severity and aetiology.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Clinical assessment: history of infection, latent period, nephritic syndrome | KDIGO 2021 Ch 9 | IRGN-DX-01 |
| D2 | Laboratory workup: urinalysis, Cr/eGFR, C3/C4/CH50, ASO/anti-DNAse B | KDIGO 2021 Ch 9 | IRGN-DX-03 |
| D3 | Diagnose: nephritic syndrome + latent period + low C3 + normal C4 + strep serology | KDIGO 2021 Ch 9 | IRGN-DX-01 |
| D4 | Assess severity: Cr level, BP, urine output, proteinuria | ERA/EDTA 2022 | IRGN-PR-01 |
| D5 | Biopsy decision: atypical features (anuria, Cr >3.0, nephrotic-range, low C3 >3 wks) | KDIGO 2025 | IRGN-DX-04 |
| D6 | Identify infection source: throat/skin culture, serology, blood cultures | IDSA 2021 | IRGN-DX-06 |


## 02. Acute Management and Supportive Care

**Duration:** 30 days  
**Goal:** Provide supportive care: BP control, diuretics for volume overload, fluid/sodium restriction. Treat active infection. Monitor for complications.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| S1 | Hospitalise if hypertensive, oliguric, Cr elevated, or complications | KDIGO 2021 Ch 9 | IRGN-TX-01 |
| S2 | BP control: target <130/80; amlodipine/nifedipine/labetalol | KDIGO 2021 Ch 9 | IRGN-TX-03 |
| S3 | Diuretics: furosemide for oedema/volume overload | KDIGO 2021 Ch 9 | IRGN-TX-04 |
| S4 | Fluid and sodium restriction: <2g Na/day | KDIGO 2021 Ch 9 | IRGN-TX-01 |
| S5 | Antibiotics: treat active infection (penicillin for GAS 10 days) | IDSA 2021 | IRGN-TX-02 |
| S6 | Daily monitoring: BP, urine output, weight, dipstick | KDIGO 2021 Ch 9 | IRGN-MON-01 |


## 03. Monitoring for Resolution

**Duration:** 90 days  
**Goal:** Monitor clinical and laboratory parameters for expected spontaneous resolution. Track C3 normalisation (typically 4-8 weeks). Assess for complications.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| R1 | Weekly: Cr/eGFR, C3, UPCR, BP | KDIGO 2021 Ch 9 | IRGN-MON-01 |
| R2 | Assess C3 normalisation by 4-8 weeks | KDIGO 2021 Ch 9 | IRGN-MON-02 |
| R3 | Monitor diuresis: spontaneous resolution of oliguria by 2-3 weeks | ERA/EDTA 2022 | IRGN-PR-01 |
| R4 | Taper antihypertensives as BP normalises | KDIGO 2021 Ch 9 | IRGN-TX-03 |
| R5 | Identify non-resolving features: persistent proteinuria, HTN, low C3 >8 wks | KDIGO 2025 | IRGN-PR-04 |


## 04. Atypical/Refractory: Immunosuppression Consideration

**Duration:** 180 days  
**Goal:** For patients with persistent nephrotic-range proteinuria, incomplete recovery, or atypical features. Consider steroids and/or MMF.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| A1 | Re-biopsy if not done: assess for crescents, chronic changes | KDIGO 2021 Ch 9 | IRGN-DX-04 |
| A2 | If nephrotic-range proteinuria >3 months: ACEi/ARB | KDIGO 2021 Ch 9 | IRGN-TX-09 |
| A3 | Consider steroid trial: prednisone 0.5-1 mg/kg/day 8-12 wks | KDIGO 2021 Ch 9 | IRGN-TX-06 |
| A4 | Consider MMF for steroid-dependent/resistant proteinuria | ISN 2023 | IRGN-TX-06 |
| A5 | Re-evaluate for complement abnormality if C3 persistently low | KDIGO 2025 | IRGN-PR-04 |


## 05. Crescentic/RPGN: Intensive Therapy

**Duration:** 90 days  
**Goal:** For patients with >50% crescents on biopsy or rapidly progressive GN (RPGN). Intensive immunosuppression with pulse steroids, cyclophosphamide, and possibly plasma exchange.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| C1 | Confirm crescents >50% or RPGN on biopsy | KDIGO 2021 Ch 9 | IRGN-PR-02 |
| C2 | Pulse methylprednisolone 10-30 mg/kg/day IV x3 | KDIGO 2021 Ch 9 | IRGN-TX-06 |
| C3 | Oral prednisone 0.5-1 mg/kg/day taper over 3-6 mo | KDIGO 2021 Ch 9 | IRGN-TX-06 |
| C4 | IV cyclophosphamide 500-750 mg/m2 monthly x3-6 | KDIGO 2021 Ch 9 | IRGN-TX-07 |
| C5 | Consider PLEX if dialysis-dependent or pulmonary haemorrhage | KDIGO 2021 Ch 9 | IRGN-TX-08 |
| C6 | Dialysis as needed; temporary in most cases | KDIGO 2021 Ch 9 | IRGN-TX-05 |
| C7 | Weekly: Cr, UPCR, C3, CBC | ERA/EDTA 2022 | IRGN-MON-01 |


## 06. Long-Term Follow-Up and Outcomes

**Duration:** 365 days  
**Goal:** Structured follow-up to detect persistent abnormalities, manage complications, and determine need for ongoing care. Discharge if fully recovered at 12 months.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| F1 | Follow-up at 3, 6, 12 months: Cr, UPCR, BP, urinalysis | KDIGO 2021 Ch 9 | IRGN-MON-03 |
| F2 | If all normal at 12 months: discharge to primary care | KDIGO 2021 Ch 9 | IRGN-MON-03 |
| F3 | If persistent proteinuria >0.5 g/day: ACEi/ARB | KDIGO 2021 Ch 9 | IRGN-TX-09 |
| F4 | If persistent HTN: long-term antihypertensives | KDIGO 2021 Ch 9 | IRGN-TX-03 |
| F5 | If Cr not recovered: CKD management | KDIGO 2021 | IRGN-MON-04 |
| F6 | Patient education: infection hygiene, sore throat management | EULAR 2022 | IRGN-REF-01 |
| F7 | If ESKD: dialysis, transplant (defer 12 mo post-recovery) | KDIGO 2025 | IRGN-TX-05 |

| IRGN-PATH-01 | Diagnosis and Classification | 5-7 |
| IRGN-PATH-02 | Acute Management and Supportive Care | 5-7 |
| IRGN-PATH-03 | Monitoring for Resolution | 5-7 |
| IRGN-PATH-04 | Atypical/Refractory: Immunosuppression Consideration | 5-7 |
| IRGN-PATH-05 | Crescentic/RPGN: Intensive Therapy | 5-7 |
| IRGN-PATH-06 | Long-Term Follow-Up and Outcomes | 5-7 |


---

## Pathway Performance Metrics

| Metric | Target | Measurement |
|---|---|---|
| Time to diagnosis | <14 days | Referral to diagnosis |
| Supportive care within 24h | >95% | Stage 2 entry |
| Steroid use only for crescentic >50% | 100% adherence | Stage 5 entry |
| C3 normalisation at 8 weeks | >85% children | Lab monitoring |
| Full recovery at 12 months (children) | >90% | Cr, UPCR normal |
| Adult renal survival at 1 year | >80% | No ESKD |
