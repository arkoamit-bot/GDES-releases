# Fibrillary Glomerulonephritis (FGN) — Clinical Pathway Specification

**Document ID:** FGN-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways

---

## 1. Document Purpose

6-stage clinical pathway for Fibrillary GN management.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis and Classification (30d) -> STAGE 2: MGRS-Associated FGN — Clone-Directed Therapy (180d) -> STAGE 2: Idiopathic/Autoimmune FGN — Supportive and Immunosuppression (360d) -> STAGE 4: Monitoring and MGRS Surveillance (365d) -> STAGE 5: ESKD Preparation and Transplant (365d) -> STAGE 6: Long-Term Follow-Up (730d)
```

## 01. Diagnosis and Classification

**Duration:** 30 days
**Goal:** Confirm FGN: renal biopsy with EM + Congo Red + DNAJB9. Classify by etiology.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Renal biopsy: EM for fibril diameter (10-20 nm), random orientation — diagnostic | KDIGO 2021 | FGN-DX-01 |
| D2 | Congo Red staining: must be negative | KDIGO 2021 | FGN-DX-02 |
| D3 | DNAJB9 IHC/IF: positive confirms FGN | ISN 2023 | FGN-DX-03 |
| D4 | IF: IgG, C3, C1q, kappa/lambda light chains | KDIGO 2021 | FGN-DX-04 |
| D5 | MGRS workup: SPEP, IFE, sFLC | KDIGO 2021 | FGN-DX-06 |
| D6 | Autoimmune workup: ANA, anti-dsDNA, C3/C4, Crohn evaluation if GI symptoms | ERA/EDTA 2022 | FGN-DX-05 |
| D7 | Exclude amyloidosis (Congo Red negative) and immunotactoid GN (fibril size <30 nm) | ISN 2023 | FGN-EX-01 |

**Next stages:** FGN-PATH-02, FGN-PATH-06
**Criteria to proceed:** Diagnosis confirmed; initiate treatment based on etiology

## 02. MGRS-Associated FGN — Clone-Directed Therapy

**Duration:** 180 days
**Goal:** MGRS-associated FGN: Rituximab for CD20+ clone; daratumumab/bortezomib for plasma cell clone.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| C1 | Hematology consult: characterize clone (CD20+ B cell vs plasma cell) | KDIGO 2021 | FGN-TX-02 |
| C2 | Rituximab 375 mg/m2 IV weekly x4 for CD20+ clone | KDIGO 2021 | FGN-TX-02 |
| C3 | Daratumumab 16 mg/kg IV weekly x8 or bortezomib-based for plasma cell clone | ISN 2023 | FGN-TX-02 |
| C4 | Start RAASi: ACEi/ARB for proteinuria | KDIGO 2021 | FGN-TX-01 |
| C5 | BP target <130/80 | KDIGO 2021 | FGN-TX-05 |

**Next stages:** FGN-PATH-04, FGN-PATH-05, FGN-PATH-06
**Criteria to proceed:** Clone-directed therapy initiated; monitor response

## 02. Idiopathic/Autoimmune FGN — Supportive and Immunosuppression

**Duration:** 360 days
**Goal:** Idiopathic FGN: supportive care. Autoimmune-associated: treat underlying disease. Consider immunosuppression for crescentic FGN.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| S1 | RAASi for proteinuria — cornerstone therapy | KDIGO 2021 | FGN-TX-01 |
| S2 | Treat underlying autoimmune disease per guidelines | ERA/EDTA 2022 | FGN-TX-03 |
| S3 | Consider prednisone + MMF/CYC for crescentic FGN (limited evidence) | ISN 2023 | FGN-TX-04 |
| S4 | BP target <130/80 | KDIGO 2021 | FGN-TX-05 |
| S5 | Q3 monthly monitoring: eGFR, UPCR, BP | KDIGO 2021 | FGN-MON-01 |

**Next stages:** FGN-PATH-04, FGN-PATH-05, FGN-PATH-06
**Criteria to proceed:** Supportive therapy established

## 04. Monitoring and MGRS Surveillance

**Duration:** 365 days
**Goal:** Regular monitoring of renal function, proteinuria, and underlying MGRS/autoimmune disease.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| M1 | Q3-6 months: eGFR, UPCR, BP | KDIGO 2021 | FGN-MON-01 |
| M2 | SPEP/IFE/sFLC Q6 months for MGRS patients | KDIGO 2021 | FGN-MON-02 |
| M3 | Autoimmune disease monitoring per subspecialty | ERA/EDTA 2022 | FGN-MON-04 |
| M4 | Malignancy screening if indicated | ISN 2023 | FGN-MON-02 |

**Next stages:** FGN-PATH-05, FGN-PATH-06
**Criteria to proceed:** Surveillance ongoing

## 05. ESKD Preparation and Transplant

**Duration:** 365 days
**Goal:** RRT planning when eGFR <20. Transplant with recurrence counseling.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | RRT planning: eGFR <20 — discuss HD, PD, transplant | KDIGO 2021 | FGN-TX-06 |
| E2 | Transplant counseling: 30-40% recurrence risk; consider treating MGRS pre-transplant | ERA/EDTA 2022 | FGN-TX-06 |
| E3 | Post-transplant recurrence monitoring: Q1 month x6 then Q3 months | KDIGO 2021 | FGN-MON-03 |
| E4 | Protocol biopsy at 12 months: DNAJB9 IF for recurrence surveillance | ISN 2023 | FGN-MON-03 |

**Next stages:** FGN-PATH-06
**Criteria to proceed:** Transplant or dialysis initiated

## 06. Long-Term Follow-Up

**Duration:** 730 days
**Goal:** Lifelong follow-up: nephrology, hematology (if MGRS), transplant surveillance.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Q3-6 months: eGFR, UPCR, BP | KDIGO 2021 | FGN-MON-01 |
| L2 | Post-transplant: UPCR, eGFR, protocol biopsy | KDIGO 2021 | FGN-MON-03 |
| L3 | MGRS: SPEP/IFE/sFLC Q6 months with hematology | KDIGO 2021 | FGN-MON-02 |
| L4 | Cardiovascular risk management | KDIGO 2021 | FGN-TX-05 |
| L5 | Rare GN registry enrolment | ERA/EDTA 2022 | FGN-REF-01 |

**Next stages:** None (final stage)
**Criteria to proceed:** N/A (final stage)

