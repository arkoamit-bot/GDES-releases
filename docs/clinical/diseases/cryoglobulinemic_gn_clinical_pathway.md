# Cryoglobulinemic GN — Clinical Pathway Specification

**Document ID:** CRYO-CP-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Clinical Pathways  

---

## 1. Document Purpose

This document defines the complete 6-stage clinical pathway for Cryoglobulinemic GN management within the BGDDR v4.1 decision support framework. Each stage specifies duration, actions, decision points, and integration with KB rules.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis & Classification (30 days)
   |   Actions: D1-D6
   v
STAGE 2: Mild-Moderate Disease: DAA Therapy (180 days)
   |   Actions: M1-M4
   v
+----+----+----+----+----+
|                        |
Moderate-Severe:      Mild Response: 
Rituximab + DAA (3)   Continue DAA (2)
   |                        |
   +----+----+----+----+----+
                |
           +----+----+
           |         |
     Severe/RPGN  Non-HCV/Type I
     Intensive (4)  Management (5)
           |
           v
STAGE 6: Long-Term Monitoring & Outcomes (730d+)
   Actions: L1-L6
```

## 01. Diagnosis and Classification

**Duration:** 30 days  
**Goal:** Establish CryoGN diagnosis: positive cryoglobulins, very low C4, MPGN biopsy, identify aetiology (HCV vs non-HCV).

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Clinical assessment: purpura, arthralgia, neuropathy, nephritic syndrome | KDIGO 2021 Ch 10 | CRYO-DX-01 |
| D2 | Lab: cryoglobulins, C3/C4/CH50, RF, HCV serology/RNA | KDIGO 2021 Ch 10 | CRYO-DX-02 |
| D3 | Renal biopsy: MPGN pattern, cryoglobulin thrombi, IgG+IgM+C3 IF | KDIGO 2021 Ch 10 | CRYO-DX-03 |
| D4 | Classify: cryoglobulin type (I/II/III), HCV vs non-HCV aetiology | ERA/EDTA 2022 | CRYO-DX-05 |
| D5 | Assess severity: Cr, proteinuria, extra-renal vasculitis, cryocrit, C4 | ISN 2023 | CRYO-PR-01 |
| D6 | Biopsy for severe/atypical: confirm >30% crescents if RPGN | KDIGO 2025 | CRYO-PR-03 |

## 02. Mild-Moderate Disease: DAA Therapy

**Duration:** 180 days  
**Goal:** First-line treatment for mild-moderate HCV-associated CryoGN: direct-acting antivirals.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| M1 | Initiate pangenotypic DAA: glecaprevir/pibrentasvir or sofosbuvir/velpatasvir 12 wks | EASL 2020 | CRYO-TX-01 |
| M2 | Monitor HCV RNA at week 4, end of treatment, SVR12 | EASL 2020 | CRYO-MON-03 |
| M3 | Supportive: RAASi if proteinuria, diuretics if oedema | KDIGO 2021 | CRYO-TX-06 |
| M4 | Monthly: Cr, UPCR, C4, RF, cryocrit, LFT | KDIGO 2021 Ch 10 | CRYO-MON-01 |

## 03. Moderate-Severe Disease: Rituximab + DAA

**Duration:** 180 days  
**Goal:** For moderate-severe CryoGN (Cr 2.0-3.0, moderate vasculitis): rituximab + steroids + DAA.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| R1 | Rituximab 375 mg/m2 IV weekly x4 | ACR 2021 | CRYO-TX-02 |
| R2 | Methylprednisolone 500 mg IV x3 then oral prednisone taper | KDIGO 2021 | CRYO-TX-03 |
| R3 | DAAs started concurrently (if HCV+) | EASL 2020 | CRYO-TX-01 |
| R4 | PCP prophylaxis (TMP/SMX) during immunosuppression | KDIGO 2021 | CRYO-MON-01 |

## 04. Severe/RPGN: Intensive Therapy

**Duration:** 90 days  
**Goal:** For severe CryoGN with RPGN, dialysis dependency, or life-threatening vasculitis.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| S1 | Pulse methylprednisolone 500-1000 mg IV x3 | KDIGO 2021 | CRYO-TX-03 |
| S2 | Rituximab 375 mg/m2 IV weekly x4 | ACR 2021 | CRYO-TX-02 |
| S3 | Plasma exchange 1.5 vol x5-7 if dialysis-dependent | ERA/EDTA 2022 | CRYO-TX-04 |
| S4 | Cyclophosphamide IV 500-750 mg/m2 if refractory to rituximab | KDIGO 2021 | CRYO-TX-05 |
| S5 | Dialysis as needed (temporary in most) | KDIGO 2021 | CRYO-TX-04 |

## 05. Non-HCV/Type I CryoGN Management

**Duration:** 180 days  
**Goal:** For non-HCV-associated CryoGN: treat underlying SLE, Sjogren, lymphoma. Type I: treat plasma cell dyscrasia.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| N1 | Identify underlying cause: SLE, Sjogren, lymphoma, plasma cell dyscrasia | ISN 2023 | CRYO-DX-07 |
| N2 | SLE/Jogren: steroids + rituximab | ACR 2021 | CRYO-TX-02 |
| N3 | Type I: bortezomib/dexamethasone or daratumumab-based | ERA/EDTA 2022 | CRYO-TX-07 |
| N4 | Lymphoma: treat NHL per haematology protocol | ISN 2023 | CRYO-REF-01 |

## 06. Long-Term Monitoring and Outcomes

**Duration:** 730 days  
**Goal:** Long-term follow-up: monitor for relapse, HCV SVR durability, lymphoma surveillance.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Cr, UPCR, C4, RF, cryocrit q3-6 months | KDIGO 2021 Ch 10 | CRYO-MON-01 |
| L2 | C4 monitoring: falling C4 predicts relapse | ERA/EDTA 2022 | CRYO-MON-02 |
| L3 | HCV RNA annually if SVR12 achieved | EASL 2020 | CRYO-MON-03 |
| L4 | Lymphoma surveillance: CBC, SPEP, LDH annually if persistent monoclonal | ISN 2023 | CRYO-MON-04 |
| L5 | Liver ultrasound annually (HCC surveillance) if cirrhotic | AASLD 2018 | CRYO-REF-01 |
| L6 | Patient education: avoid cold exposure (cryoglobulin precipitation) | KDIGO 2021 | CRYO-REF-01 |

| Stage ID | Stage Name | Duration (days) |
|---|---|---|
| CRYO-PATH-01 | Diagnosis and Classification | 30 |
| CRYO-PATH-02 | Mild-Moderate Disease: DAA Therapy | 180 |
| CRYO-PATH-03 | Moderate-Severe Disease: Rituximab + DAA | 180 |
| CRYO-PATH-04 | Severe/RPGN: Intensive Therapy | 90 |
| CRYO-PATH-05 | Non-HCV/Type I CryoGN Management | 180 |
| CRYO-PATH-06 | Long-Term Monitoring and Outcomes | 730 |


---

## Pathway Performance Metrics

| Metric | Target | Measurement |
|---|---|---|
| Time to diagnosis | <30 days | Referral to diagnosis |
| DAA initiation in HCV+ | >95% | Stage 2 entry |
| Rituximab use for moderate-severe | 100% adherence | Stage 3 entry |
| HCV SVR12 rate | >95% | Lab monitoring |
| Renal remission at 12 months | >80% | Cr, UPCR normalisation |
| Lymphoma surveillance compliance | >90% | Annual surveillance |
