# Calcineurin Inhibitor Nephrotoxicity — Clinical Pathway Specification
**Document ID:** CNI-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways
---
## 1. Document Purpose
6-stage clinical pathway for CNI toxicity management.
---
## 2. Pathway Overview
```
STAGE 1: Diagnosis and Biopsy Confirmation (14d) -> STAGE 2: Acute CNI Toxicity — Dose Reduction (30d) -> STAGE 3: Chronic CNI Toxicity — Conversion Evaluation (90d) -> STAGE 4: Supportive Management (365d) -> STAGE 5: Advanced CNI Toxicity — CKD Management (365d) -> STAGE 6: Long-Term Surveillance After Conversion (730d)
```

## 01. Diagnosis and Biopsy Confirmation
**Duration:** 14 days
**Goal:** Confirm CNI toxicity: biopsy showing arteriolar hyalinosis, striped fibrosis. Exclude rejection.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| D1 | Graft biopsy: assess arteriolar hyalinosis, striped fibrosis, microcalcification | KDIGO 2021 | CNI-DX-02 |
| D2 | C4d stain + DSA: exclude concurrent ABMR | KDIGO 2021 | CNI-DX-05 |
| D3 | Assess t-score: should be 0 in pure CNI toxicity. If >0, suspect TCMR | KDIGO 2021 | CNI-DX-06 |
| D4 | Assess g+ptc: should be 0 in pure CNI toxicity. If >0, exclude ABMR | KDIGO 2021 | CNI-EX-01 |
| D5 | Grade severity: hyalinosis extent, IFTA%, UPCR, eGFR | Banff 2019 | CNI-PR-01 |
| D6 | Check CNI trough and review cumulative exposure | KDIGO 2021 | CNI-MON-01 |
**Next stages:** CNI-PATH-02, CNI-PATH-03, CNI-PATH-06
**Criteria to proceed:** CNI toxicity confirmed

## 02. Acute CNI Toxicity — Dose Reduction
**Duration:** 30 days
**Goal:** Reduce CNI dose for acute, haemodynamic CNI toxicity (high trough + Cr rise).
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| T1 | Reduce CNI dose by 25-50%. Tacrolimus target 4-6 ng/mL | KDIGO 2021 | CNI-TX-01 |
| T2 | Recheck Cr in 1-2 weeks — improvement expected within days | KDIGO 2021 | CNI-TX-01 |
| T3 | Check K+, Mg — CNI can cause hyperkalaemia and hypomagnesaemia | KDIGO 2021 | CNI-TX-01 |
| T4 | If recurrent acute toxicity: consider CNI-free or CNI-minimised regimen | AST 2023 | CNI-TX-04 |
**Next stages:** CNI-PATH-03, CNI-PATH-04, CNI-PATH-06
**Criteria to proceed:** Acute toxicity resolved or managed

## 03. Chronic CNI Toxicity — Conversion Evaluation
**Duration:** 90 days
**Goal:** Evaluate for conversion to belatacept or mTOR inhibitor. Biopsy-proven chronic CNI toxicity.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| E1 | Assess suitability for belatacept: EBV serostatus, eGFR, IFTA% | AST 2023 | CNI-REF-01 |
| E2 | Check UPCR — assess baseline proteinuria before conversion | KDIGO 2021 | CNI-MON-02 |
| E3 | Belatacept conversion: 5 mg/kg IV Days 1, 15, 29, then Q4 weeks | AST 2023 | CNI-TX-02 |
| E4 | If belatacept not suitable: mTOR inhibitor conversion (sirolimus/everolimus) | AST 2023 | CNI-TX-03 |
| E5 | If conversion not possible: CNI minimisation + MMF intensification | KDIGO 2021 | CNI-TX-04 |
**Next stages:** CNI-PATH-04, CNI-PATH-05, CNI-PATH-06
**Criteria to proceed:** Conversion or minimisation plan initiated

## 04. Supportive Management
**Duration:** 365 days
**Goal:** BP control, RAASi, metabolic management. Protect remaining renal function.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| S1 | RAASi for proteinuria and BP target <130/80 | KDIGO 2021 | CNI-TX-05 |
| S2 | Manage hyperkalaemia: dietary K restriction, patiromer, fludrocortisone if needed | KDIGO 2021 | CNI-TX-05 |
| S3 | Manage diabetes: if new-onset, consider tacrolimus to cyclosporine switch | AST 2023 | CNI-TX-05 |
| S4 | Monitor UPCR Q3-6 months — screen for worsening proteinuria | KDIGO 2021 | CNI-MON-02 |
| S5 | Avoid nephrotoxins: NSAIDs, contrast | KDIGO 2021 | CNI-TX-05 |
**Next stages:** CNI-PATH-05, CNI-PATH-06
**Criteria to proceed:** Supportive care established

## 05. Advanced CNI Toxicity — CKD Management
**Duration:** 365 days
**Goal:** Advanced irreversible injury (eGFR <30, IFTA >50%). Prepare for graft failure.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| C1 | Accept advanced CNI toxicity as irreversible | KDIGO 2021 | CNI-PR-02 |
| C2 | CKD management: anaemia, MBD, nutrition | KDIGO 2021 | CNI-TX-05 |
| C3 | RRT planning: eGFR <20 | KDIGO 2021 | CNI-REF-01 |
| C4 | Re-transplant: use belatacept-based IS for new graft to prevent recurrence | AST 2023 | CNI-REF-01 |
**Next stages:** CNI-PATH-06
**Criteria to proceed:** CKD managed or RRT initiated

## 06. Long-Term Surveillance After Conversion
**Duration:** 730 days
**Goal:** Monitor DSA, graft function, and metabolic parameters after CNI conversion.
### Actions
| ID | Action | Evidence | KB Rule |
|---|---|---|---|
| L1 | DSA at 3, 6, 12 months post-conversion — de novo DSA risk | KDIGO 2021 | CNI-MON-03 |
| L2 | eGFR, UPCR, BP Q3 months | KDIGO 2021 | CNI-MON-02 |
| L3 | Belatacept dose: 5 mg/kg Q4 weeks (maintenance) | AST 2023 | CNI-TX-02 |
| L4 | Cardiovascular risk management — leading cause of death | KDIGO 2021 | CNI-TX-05 |
| L5 | For-cause biopsy: Cr rise, new DSA, or proteinuria | KDIGO 2021 | CNI-DX-05 |
**Next stages:** N/A (final stage)
**Criteria to proceed:** N/A (final stage)

---
