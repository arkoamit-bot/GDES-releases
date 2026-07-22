# Diabetic Kidney Disease — Clinical Pathway Specification

**Document ID:** DKD-CP-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Clinical Pathways  

---

## 1. Document Purpose

6-stage clinical pathway for Diabetic Kidney Disease management within BGDDR v4.1.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis & Staging (90d)
   |   Actions: D1-D6
   v
STAGE 2: First-Line Therapy Initiation (180d)
   |   Actions: T1-T4
   v
+----+----+----+----+
|         |         |
Persistent   Adequate  Atypical
Albuminuria  Response  Features
   |         |         |
STAGE 3:    |    STAGE 5:
Add-on      |    Biopsy Decision
Therapy     |    if indicated
   |         |         |
   +----+----+         |
        |              |
    STAGE 6:      STAGE 4: Advanced
    Long-Term     CKD G4-G5
    & CV Care     Management
```

## 01. Diagnosis and Staging

**Duration:** 90 days  
**Goal:** Establish DKD diagnosis: persistent albuminuria + bland sediment + diabetes. Stage by eGFR (G1-G5) and ACR (A1-A3).

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Confirm diabetes: type, duration, HbA1c, glucose levels | ADA 2025 | DKD-DX-03 |
| D2 | Albuminuria: ACR on 2 of 3 morning specimens over 3-6 mo | KDIGO 2024 | DKD-DX-01 |
| D3 | eGFR: CKD-EPI equation; stage G1-G5 | KDIGO 2024 | DKD-DX-02 |
| D4 | Urinalysis: confirm bland sediment (no RBC casts) | KDIGO 2024 | DKD-DX-04 |
| D5 | Ophthalmology: diabetic retinopathy screening | ADA 2025 | DKD-DX-05 |
| D6 | Assess CV risk: lipids, BP, smoking, CVD history | ESC/EASD 2023 | DKD-PR-04 |

## 02. First-Line Pharmacotherapy Initiation

**Duration:** 180 days  
**Goal:** Start foundational therapy: RAASi + SGLT2i combination. Optimize glycemic control.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Initiate RAASi: ACEi/ARB at low dose, titrate q2-4 wks to max tolerated | KDIGO 2024 | DKD-TX-01 |
| T2 | Add SGLT2i: dapagliflozin 10 mg or empagliflozin 10 mg daily | KDIGO 2024 | DKD-TX-02 |
| T3 | SGLT2i monitoring: volume status, K+, eGFR minor dip expected | KDIGO 2024 | DKD-TX-08 |
| T4 | Glycemic optimization: metformin (eGFR >30), GLP-1 RA if needed | ADA 2025 | DKD-TX-07 |

## 03. Add-On Therapy for Persistent Albuminuria

**Duration:** 180 days  
**Goal:** For persistent ACR >=30 despite RAASi + SGLT2i: add finerenone. Optimize BP.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| A1 | Check K+ and eGFR: finerenone candidate if eGFR >=25, K+ <5.0 | KDIGO 2024 | DKD-TX-03 |
| A2 | Start finerenone 10 mg daily; titrate to 20 mg if K+ tolerated | KDIGO 2024 | DKD-TX-03 |
| A3 | BP management: add amlodipine/thiazide if >130/80 | KDIGO 2024 | DKD-TX-04 |
| A4 | Statin: atorvastatin 20-80 mg or rosuvastatin 10-40 mg | ESC/EASD 2023 | DKD-TX-06 |

## 04. Management of Advanced CKD (G4-G5)

**Duration:** 365 days  
**Goal:** For eGFR <30: manage complications, prepare for RRT, adjust medications.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| C1 | Medication dose adjustment: metformin stop if eGFR <30, insulin adjust | ADA 2025 | DKD-TX-07 |
| C2 | Anemia management: Hb target 10-11.5, iron repletion, ESA if indicated | KDIGO 2024 | DKD-MON-01 |
| C3 | CKD-MBD: phosphate binders, vitamin D, PTH monitoring | KDIGO 2024 | DKD-MON-01 |
| C4 | Metabolic acidosis: NaHCO3 if HCO3 <22 | KDIGO 2024 | DKD-MON-01 |
| C5 | RRT planning: access creation (AVF/AVG), transplant evaluation | ERA/EDTA 2022 | DKD-REF-01 |

## 05. Atypical Presentation — Biopsy Decision

**Duration:** 90 days  
**Goal:** Active sediment, rapid eGFR decline, or nephrotic-range proteinuria — consider biopsy to exclude superimposed GN.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| B1 | Biopsy indication: active sediment, rapid decline, sudden UPCR increase | KDIGO 2021 | DKD-MON-04 |
| B2 | If non-diabetic GN found: treat per GN guideline | KDIGO 2021 | DKD-EX-01 |
| B3 | If pure DKD confirmed: intensify risk factor control | KDIGO 2024 | DKD-TX-01 |
| B4 | Immunosuppression only if superimposed GN confirmed | KDIGO 2021 | DKD-EX-01 |

## 06. Long-Term Monitoring and CV Protection

**Duration:** 730 days  
**Goal:** Sustained triple therapy monitoring. CV risk reduction. Yearly screening.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Q3 months: HbA1c, eGFR, ACR, K+, BP, weight | KDIGO 2024 | DKD-MON-01 |
| L2 | Q6 months: lipids, Hb, HCO3, albumin | KDIGO 2024 | DKD-MON-02 |
| L3 | Annual: ophthalmology, foot exam, ECG | ADA 2025 | DKD-MON-02 |
| L4 | K+ monitoring: 2-4 wks after RAASi/finerenone change | KDIGO 2024 | DKD-MON-03 |
| L5 | Lifestyle counseling: diet, exercise, smoking cessation | ESC/EASD 2023 | DKD-REF-01 |
| L6 | Annual CV risk assessment; adjust statin/antiplatelet | ESC/EASD 2023 | DKD-PR-04 |

| Stage ID | Stage Name | Duration (days) |
|---|---|---|
| DKD-PATH-01 | Diagnosis and Staging | 90 |
| DKD-PATH-02 | First-Line Pharmacotherapy Initiation | 180 |
| DKD-PATH-03 | Add-On Therapy for Persistent Albuminuria | 180 |
| DKD-PATH-04 | Management of Advanced CKD (G4-G5) | 365 |
| DKD-PATH-05 | Atypical Presentation — Biopsy Decision | 90 |
| DKD-PATH-06 | Long-Term Monitoring and CV Protection | 730 |


---

## Pathway Performance Metrics

| Metric | Target | Measurement |
|---|---|---|
| DKD diagnosis within 90 days | >90% | Referral to diagnosis |
| RAASi + SGLT2i initiation | >80% | Prescription rate in eligible |
| Triple therapy (RAASi+SGLT2i+finerenone) in A3 | >60% | Appropriate candidates |
| ACR regression at 12 months | >40% | ACR reduction >30% |
| Annual retinopathy screening | >85% | Documented exam |
| CV event rate reduction | >20% | vs historical rates |
