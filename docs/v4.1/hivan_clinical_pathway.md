# HIV-Associated Nephropathy (HIVAN) — Clinical Pathway Specification

**Document ID:** HIV-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways

---

## 1. Document Purpose

6-stage clinical pathway for HIVAN management.

---

## 2. Pathway Overview

```
STAGE 1: Diagnosis and Staging (14d) -> STAGE 2: ART Initiation and RAASi (90d) -> STAGE 3: Response Assessment and Adjustments (180d) -> STAGE 4: Advanced CKD and Dialysis Planning (365d) -> STAGE 5: Kidney Transplant (365d) -> STAGE 6: Long-Term HIV and Renal Monitoring (730d)
```

## 01. Diagnosis and Staging

**Duration:** 14 days
**Goal:** Confirm HIVAN: renal biopsy + HIV serology + APOL1 genotyping.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Renal biopsy: collapsing FSGS, microcysts, TRI on EM | KDIGO 2021 | HIV-DX-01 |
| D2 | IF: confirm negative for immune complexes | KDIGO 2021 | HIV-DX-06 |
| D3 | HIV serology: ELISA + Western blot (or known HIV+) | KDIGO 2021 | HIV-DX-04 |
| D4 | APOL1 genotyping: G1/G1, G1/G2, or G2/G2 | ASN 2022 | HIV-PR-01 |
| D5 | CD4 count, HIV viral load | DHHS 2024 | HIV-PR-02 |
| D6 | Assess eGFR, UPCR, BP, renal ultrasound | KDIGO 2021 | HIV-DX-05 |
| D7 | Exclude HIV-IC GN by IF; exclude TDF toxicity by drug history | ISN 2023 | HIV-EX-01 |

**Next stages:** HIV-PATH-02, HIV-PATH-06
**Criteria to proceed:** Diagnosis confirmed; start ART and RAASi

## 02. ART Initiation and RAASi

**Duration:** 90 days
**Goal:** Start ART immediately regardless of CD4. Start RAASi for proteinuria.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Start ART: INSTI (dolutegravir 50 mg daily) + dual NRTI (TAF 25 mg + FTC 200 mg) | DHHS 2024 | HIV-TX-01 |
| T2 | Start ACEi/ARB: ramipril 2.5-10 mg daily for proteinuria | KDIGO 2021 | HIV-TX-02 |
| T3 | BP target <130/80; add CCB/thiazide if needed | KDIGO 2021 | HIV-TX-03 |
| T4 | Monitor HIV viral load, CD4 monthly | DHHS 2024 | HIV-MON-01 |
| T5 | Monitor K+, Cr 2-4 wks after RAASi start | KDIGO 2021 | HIV-MON-02 |

**Next stages:** HIV-PATH-03, HIV-PATH-04, HIV-PATH-06
**Criteria to proceed:** ART and RAASi initiated

## 03. Response Assessment and Adjustments

**Duration:** 180 days
**Goal:** Assess renal and virologic response to ART. Adjust therapy if suboptimal.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| R1 | Q1-3 months: eGFR, UPCR, BP, HIV viral load, CD4 | KDIGO 2021 | HIV-MON-02 |
| R2 | Monitor ART nephrotoxicity: TDF tubular, ATV stones | DHHS 2024 | HIV-MON-03 |
| R3 | Consider prednisone if collapsing GN progresses despite ART + RAASi (limited evidence) | KDIGO 2021 | HIV-TX-04 |
| R4 | ART adherence support: counseling, pill reminders | IDSA 2023 | HIV-REF-01 |

**Next stages:** HIV-PATH-04, HIV-PATH-05, HIV-PATH-06
**Criteria to proceed:** Therapy adjusted based on response

## 04. Advanced CKD and Dialysis Planning

**Duration:** 365 days
**Goal:** ESKD preparation when eGFR <20. Dialysis and transplant evaluation.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | RRT planning: eGFR <20 — discuss HD, PD, transplant | KDIGO 2021 | HIV-TX-05 |
| E2 | Transplant evaluation: undetectable viral load, CD4 >200 x6 months | ASN/IDSA 2023 | HIV-TX-05 |
| E3 | HIV+ patients do well on HD and PD — no isolation required | KDIGO 2021 | HIV-REF-01 |
| E4 | RAASi titration as eGFR declines | KDIGO 2021 | HIV-TX-02 |

**Next stages:** HIV-PATH-05, HIV-PATH-06
**Criteria to proceed:** RRT planning complete

## 05. Kidney Transplant

**Duration:** 365 days
**Goal:** Kidney transplant for ESKD patients with controlled HIV.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| K1 | Transplant evaluation: controlled HIV essential | ASN/IDSA 2023 | HIV-TX-05 |
| K2 | Standard transplant surgery — HIV not a contraindication | KDIGO 2021 | HIV-TX-05 |
| K3 | Post-transplant: standard immunosuppression + HIV viral load Q1-3 months | ASN/IDSA 2023 | HIV-MON-04 |
| K4 | No HIVAN recurrence in allograft if HIV controlled | KDIGO 2021 | HIV-MON-04 |

**Next stages:** HIV-PATH-06
**Criteria to proceed:** Transplant completed

## 06. Long-Term HIV and Renal Monitoring

**Duration:** 730 days
**Goal:** Lifelong: HIV + nephrology co-management. Viral suppression is key.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Q3 months: HIV viral load, CD4, eGFR, UPCR, BP | DHHS 2024 | HIV-MON-01 |
| L2 | Continue ART and RAASi lifelong | KDIGO 2021 | HIV-TX-01 |
| L3 | Monitor for ART nephrotoxicity | DHHS 2024 | HIV-MON-03 |
| L4 | Post-transplant: transplant + HIV monitoring | ASN/IDSA 2023 | HIV-MON-04 |
| L5 | Cardiovascular risk management (HIV + CKD = high risk) | KDIGO 2021 | HIV-TX-03 |

**Next stages:** None (final stage)
**Criteria to proceed:** N/A (final stage)

