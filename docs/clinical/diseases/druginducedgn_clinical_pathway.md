# Drug-Induced Glomerular Disease — Clinical Pathway Specification

**Document ID:** DRG-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways

---

## 1. Document Purpose

6-stage clinical pathway for Drug-Induced GN management.

---

## 2. Pathway Overview

```
STAGE 1: Identification and Diagnosis (14d) -> STAGE 2: Drug Withdrawal and Specific Management (90d) -> STAGE 3: Response Monitoring (180d) -> STAGE 4: Persistent Proteinuria or CKD (365d) -> STAGE 5: ESKD Preparation and Transplant (365d) -> STAGE 6: Long-Term Surveillance (730d)
```

## 01. Identification and Diagnosis

**Duration:** 14 days
**Goal:** Identify offending drug. Renal biopsy to confirm pattern of injury.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Comprehensive drug history: prescription, OTC, supplements, illicit drugs | KDIGO 2021 | DRG-DX-01 |
| D2 | Renal biopsy: determine pattern (MCD, MN, collapsing FSGS, ATIN, lupus-like, FSGS) | KDIGO 2021 | DRG-DX-02 |
| D3 | IF: PLA2R for NSAID-related MN; full-house for anti-TNF lupus | KDIGO 2021 | DRG-EX-01 |
| D4 | EM: foot process effacement (MCD), TRI (IFN), subepithelial deposits (MN) | KDIGO 2021 | DRG-DX-02 |
| D5 | Assess severity: eGFR, UPCR, BP, IFTA | KDIGO 2021 | DRG-PR-04 |

**Next stages:** DRG-PATH-02, DRG-PATH-04, DRG-PATH-06
**Criteria to proceed:** Drug identified; initiate withdrawal


## 02. Drug Withdrawal and Specific Management

**Duration:** 90 days
**Goal:** Immediately discontinue offending drug. Specific management per drug class.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Discontinue NSAID, pamidronate, IFN, ICI, anti-TNF, or heroin | KDIGO 2021 | DRG-TX-01 |
| T2 | Lithium-MCD: switch to valproate or atypical antipsychotic (psychiatry consult) | ERA/EDTA 2022 | DRG-TX-05 |
| T3 | ICI-ATIN: prednisone 1 mg/kg/day tapered over 4-8 weeks | ASN/KDIGO 2023 | DRG-TX-03 |
| T4 | Prednisone for persistent NSAID-MCD >12 weeks | KDIGO 2021 | DRG-TX-04 |
| T5 | Start RAASi for persistent proteinuria after drug cessation | KDIGO 2021 | DRG-TX-02 |
| T6 | BP target <130/80 | KDIGO 2021 | DRG-TX-07 |

**Next stages:** DRG-PATH-03, DRG-PATH-04, DRG-PATH-06
**Criteria to proceed:** Drug withdrawn; monitor response


## 03. Response Monitoring

**Duration:** 180 days
**Goal:** Monitor proteinuria, eGFR, BP after drug withdrawal. Assess need for ongoing therapy.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| M1 | Q1 month: eGFR, UPCR, BP for 3 months then Q3 months until stable | KDIGO 2021 | DRG-MON-01 |
| M2 | Lithium levels Q3 months (if continuing lithium) | ERA/EDTA 2022 | DRG-MON-02 |
| M3 | ICI rechallenge monitoring: Cr, UPCR monthly for 3 months | ASN/KDIGO 2023 | DRG-MON-03 |
| M4 | Counsel to avoid re-exposure to same drug class | KDIGO 2021 | DRG-TX-01 |

**Next stages:** DRG-PATH-04, DRG-PATH-05, DRG-PATH-06
**Criteria to proceed:** Response assessed


## 04. Persistent Proteinuria or CKD

**Duration:** 365 days
**Goal:** Manage persistent injury despite drug withdrawal. RAASi and supportive care.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | RAASi for persistent proteinuria >=0.5 g/day | KDIGO 2021 | DRG-TX-02 |
| E2 | Prednisone for collapsing FSGS or refractory MCD | ISN 2023 | DRG-TX-06 |
| E3 | CKD management: BP, anemia, bone metabolism | KDIGO 2021 | DRG-TX-07 |
| E4 | Q3-6 monthly monitoring if persistent injury | KDIGO 2021 | DRG-MON-01 |

**Next stages:** DRG-PATH-05, DRG-PATH-06
**Criteria to proceed:** Supportive care established


## 05. ESKD Preparation and Transplant

**Duration:** 365 days
**Goal:** ESKD planning if irreversible sclerosing disease. No recurrence if drug avoided.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | RRT planning: eGFR <20 — CKD irreversible if FSGS/collapsing GN | KDIGO 2021 | DRG-TX-01 |
| E2 | Kidney transplant: no disease recurrence if offending drug avoided | KDIGO 2021 | DRG-TX-01 |
| E3 | Transplant: excellent outcomes for drug-induced GN (no immune disease) | ISN 2023 | DRG-TX-02 |

**Next stages:** DRG-PATH-06
**Criteria to proceed:** Transplant or dialysis initiated


## 06. Long-Term Surveillance

**Duration:** 730 days
**Goal:** Lifelong avoidance of offending drug. Annual renal monitoring.

### Actions

| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | Q3-12 months: eGFR, UPCR, BP — drug-induced GN does not relapse if drug avoided | KDIGO 2021 | DRG-MON-01 |
| L2 | Lifelong avoidance of offending drug class | KDIGO 2021 | DRG-TX-01 |
| L3 | Cardiovascular risk management | KDIGO 2021 | DRG-TX-07 |
| L4 | Patient education: medical alert for drug allergy | ISN 2023 | DRG-TX-01 |

**Next stages:** N/A (final stage)
**Criteria to proceed:** N/A (final stage)


---
