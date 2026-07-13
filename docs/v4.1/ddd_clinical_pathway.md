# Dense Deposit Disease (DDD) — Clinical Pathway Specification

**Document ID:** DDD-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways

---

## 1. Document Purpose

6-stage clinical pathway for Dense Deposit Disease management.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis and Complement Workup (30d) -> STAGE 2: Supportive Therapy and RAASi (180d) -> STAGE 3: Complement-Directed Therapy (360d) -> STAGE 4: Monitoring and Surveillance (365d) -> STAGE 5: ESKD Preparation and Transplant (365d) -> STAGE 6: Long-Term Multidisciplinary Follow-Up (730d)
```

## 01. Diagnosis and Complement Workup

**Duration:** 30 days
**Goal:** Confirm DDD: renal biopsy with EM, complement studies, genetic testing.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Renal biopsy: EM for dense intramembranous deposits (pathognomonic) | KDIGO 2021 | DDD-DX-01 |
| D2 | IF: confirm C3-dominant with negative/trace immunoglobulins | KDIGO 2021 | DDD-DX-02 |
| D3 | Complement workup: C3, C4, C3NeF, CH50, CFH, CFI, anti-CFH antibodies | KDIGO 2021 | DDD-DX-03 |
| D4 | Genetic testing: CFH, CFI, MCP, CFHR5 gene panel | KDIGO 2025 | DDD-DX-05 |
| D5 | Assess severity: eGFR, UPCR, BP, crescents | KDIGO 2021 | DDD-PR-02 |
| D6 | Ophthalmology: baseline fundoscopy for drusen | ISN 2023 | DDD-MON-03 |
| D7 | Exclude C3GN: deposit location on EM (intramembranous = DDD) | ISN 2023 | DDD-EX-01 |

**Next stages:** DDD-PATH-02, DDD-PATH-06
**Criteria to proceed:** Diagnosis confirmed; initiate treatment

## 02. Supportive Therapy and RAASi

**Duration:** 180 days
**Goal:** RAASi for proteinuria. BP management. Consider prednisone in children.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Start ACEi/ARB: titrate to max tolerated dose for proteinuria reduction | KDIGO 2021 | DDD-TX-01 |
| T2 | BP management: target <130/80; add CCB/thiazide if needed | KDIGO 2021 | DDD-TX-07 |
| T3 | Consider prednisone: children with nephrotic syndrome; limited adult benefit | ERA/EDTA 2022 | DDD-TX-02 |
| T4 | Diuretics for edema if nephrotic | KDIGO 2021 | DDD-TX-01 |

**Next stages:** DDD-PATH-03, DDD-PATH-04, DDD-PATH-06
**Criteria to proceed:** Supportive therapy established; assess response

## 03. Complement-Directed Therapy

**Duration:** 360 days
**Goal:** Eculizumab for rapidly progressive DDD or crescentic disease. PLEX for anti-CFH DDD.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| C1 | Start eculizumab: 900 mg IV weekly x4 then 1200 mg q2w — if crescentic or rapidly declining eGFR | KDIGO 2025 | DDD-TX-03 |
| C2 | Meningococcal vaccination: ACWY + MenB (mandatory before eculizumab) | KDIGO 2025 | DDD-MON-04 |
| C3 | CH50 monitoring: target <10% for adequate complement blockade | KDIGO 2025 | DDD-MON-04 |
| C4 | PLEX + immunosuppression for anti-CFH antibody-mediated DDD | ISN 2023 | DDD-TX-05 |
| C5 | Add MMF as steroid-sparing if prednisone required long-term | ERA/EDTA 2022 | DDD-TX-04 |

**Next stages:** DDD-PATH-04, DDD-PATH-05, DDD-PATH-06
**Criteria to proceed:** Complement therapy initiated

## 04. Monitoring and Surveillance

**Duration:** 365 days
**Goal:** Regular complement monitoring, proteinuria, eGFR, ophthalmology.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| M1 | Q1-3 months: eGFR, UPCR, C3, C3NeF, BP | KDIGO 2021 | DDD-MON-02 |
| M2 | Q3 months: C3, CH50 (if on eculizumab) | KDIGO 2025 | DDD-MON-01 |
| M3 | Annual fundoscopy: monitor for drusen/macular degeneration | ISN 2023 | DDD-MON-03 |
| M4 | Monitor growth in children: height, weight, pubertal stage | ERA/EDTA 2022 | DDD-MON-06 |

**Next stages:** DDD-PATH-05, DDD-PATH-06
**Criteria to proceed:** Surveillance ongoing

## 05. ESKD Preparation and Transplant

**Duration:** 365 days
**Goal:** RRT planning when eGFR <20. Transplant with recurrence counseling.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | RRT planning: eGFR <20 — discuss HD, PD, transplant | KDIGO 2021 | DDD-TX-06 |
| E2 | Transplant counseling: 40-50% recurrence risk; avoid live-related donor | ERA/EDTA 2022 | DDD-TX-06 |
| E3 | Pre-transplant complement: C3, C3NeF, CH50 | KDIGO 2025 | DDD-MON-01 |
| E4 | Post-transplant recurrence surveillance: Q1 month x6 then Q3 months | KDIGO 2021 | DDD-MON-05 |
| E5 | Eculizumab for post-transplant recurrence if indicated | KDIGO 2025 | DDD-TX-03 |

**Next stages:** DDD-PATH-06
**Criteria to proceed:** Transplant or dialysis initiated

## 06. Long-Term Multidisciplinary Follow-Up

**Duration:** 730 days
**Goal:** Lifelong follow-up: nephrology, complement genetics, ophthalmology.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Q3-6 months: eGFR, UPCR, BP, C3, C3NeF | KDIGO 2021 | DDD-MON-02 |
| L2 | Annual fundoscopy: drusen progression | ISN 2023 | DDD-MON-03 |
| L3 | Post-transplant: complement + proteinuria monitoring lifelong | KDIGO 2021 | DDD-MON-05 |
| L4 | Rare GN registry: enrol for long-term data collection | ERA/EDTA 2022 | DDD-REF-01 |
| L5 | Cardiovascular risk management: lipids, BP, smoking cessation | KDIGO 2021 | DDD-TX-07 |

**Next stages:** None (final stage)
**Criteria to proceed:** N/A (final stage)

