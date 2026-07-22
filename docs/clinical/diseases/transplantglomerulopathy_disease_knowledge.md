# Transplant Glomerulopathy - Disease Knowledge Specification
**Document ID:** TG-DK-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Disease Knowledge
---
## 1. Document Purpose
Complete disease knowledge specification for transplant glomerulopathy.
---
## 2. Disease Record - Full 21-Field Schema
### 2.1 Definition
TG is a morphologic pattern of chronic glomerular injury in renal allografts, characterized by GBM double contours and associated with chronic ABMR.
### 2.2 Epidemiology
Prevalence 10-20% at 5 years post-transplant. Strongly associated with DSA. Leading cause of late graft loss.
### 2.3 Aetiology
Most commonly chronic ABMR (DSA-mediated). Can also occur in HCV infection, TMA, CNI toxicity.
### 2.4 Pathophysiology
Chronic endothelial injury (DSA-mediated) → loss of endothelial fenestrations → new GBM deposition → double contours (CG) → progressive glomerulosclerosis.
### 2.5 Clinical Presentation
Proteinuria (often nephrotic-range), hypertension, progressive eGFR decline. May have concurrent DSA positivity.
### 2.6 Diagnostic Criteria
| # | Criterion | Essential |
|---|---|---|
| 1 | GBM double contours by EM (>2 glomeruli) | Yes |
| 2 | DSA positive | No |
| 3 | C4d positive (may be negative in late/chronic) | No |
### 2.7 Differential Diagnosis
antibodyMediatedRejection, cniToxicity, recurrentIgan
### 2.8 Laboratory Findings
  * Proteinuria (to nephrotic range)
  * eGFR declining
  * DSA positive (70-80%)
  * Hematuria possible
### 2.9 Biopsy Findings
  * GBM double contours (CG)
  * Peritubular capillary multilayering (EM)
  * Glomerulosclerosis
  * C4d positivity (variable)
  * Microvascular inflammation (may be minimal in late)
### 2.10 Classification Systems
  * name: Banff CG Score, components: cg0-cg3 by % of capillaries affected, source: Banff 2023
### 2.11 Risk Stratification
  * factor: DSA class II, risk: More aggressive
  * factor: crescents, risk: Rapid loss
  * factor: cg3 score, risk: Imminent graft loss
### 2.12 Treatment Overview
No proven effective therapy. Augment immunosuppression (IVIG, rituximab) if DSA positive. Optimize BP and proteinuria management. Consider SGLT2i for proteinuria reduction. Prepare for dialysis/retransplant.
### 2.13 Treatment Algorithm
| Step | Action |
|---|---|
| 1 | Confirm diagnosis with biopsy (CG by EM) |
| 2 | Assess DSA, C4d, Banff scores |
| 3 | Optimize CNI trough (target lower end) |
| 4 | DSA+ active: IVIG 2g/kg + rituximab 375mg/m2 |
| 5 | DSA+ refractory: bortezomib or Eculizumab (off-label) |
| 6 | Nephrotic: ACEi/ARB + SGLT2i + diuretics |
| 7 | eGFR monitoring q3mo, DSA q6mo |
| 8 | GFR <20: prepare for dialysis/retransplant |
### 2.14 Monitoring Protocol
3-monthly: eGFR, UPCR, DSA. Biopsy if progressing.
### 2.15 Complications
  * Graft loss (50% at 3 years after diagnosis)
  * Nephrotic syndrome
### 2.16 Relapse Information
Progressive condition. No reversal reported.
### 2.17 Long-Term Prognosis
Poor. 50% graft loss within 3 years of diagnosis.
### 2.18 Evidence Summary
Transplant glomerulopathy (cg score) is the histologic hallmark of chronic ABMR. The diagnosis carries a 50% graft loss rate at 3 years. Evidence for treatment is largely observational; no RCT has shown reversal. DSA-targeted therapy (IVIG/rituximab) may stabilize but does not reverse CG lesions. Proteinuria reduction with ACEi/ARB/SGLT2i slows progression. Preemptive DSA monitoring enables earlier intervention. KDIGO 2021 recommends protocol biopsy for DSA+ patients. Retransplantation after TG graft loss is feasible if DSA addressed.
### 2.19 Guideline Recommendations
| Source | Chapter | Recommendation |
|---|---|---|
| KDIGO 2021 | Ch 15: Chronic Antibody-Mediated Rejection | Screen for DSA at least annually; biopsy if DSA+ with proteinuria/eGFR decline. |
| AST 2023 | Chronic AMR Guidelines | Consider IVIG + rituximab for active chronic AMR with DSA. |
| Banff 2023 | CG Scoring Consensus | Report cg score on all transplant biopsies; cg1a/b distinction prognostically relevant. |
| ERA/EDTA 2022 | Long-Term Graft Management | Optimize CNI minimization strategies to reduce nephrotoxicity contribution. |
### 2.20 Key References
| Reference | Journal | Year |
|---|---|---|
| Solez et al. Banff Classification. Am J Transplant 2023 | Am J Transplant | 2023 |
| Loupy et al. Chronic ABMR and TG. NEJM 2020 | NEJM | 2020 |
| Halloran et al. Molecular diagnosis of ABMR. JASN 2017 | JASN | 2017 |
| Sellarés et al. iABMR vs cABMR. JASN 2012 | JASN | 2012 |
| Wiebe et al. DSA and graft survival. Transplantation 2019 | Transplantation | 2019 |
| Lefaucheur et al. IVIG in chronic ABMR. JASN 2020 | JASN | 2020 |
### 2.21 Notes
Transplant glomerulopathy is not a distinct disease entity but a morphologic pattern of injury. The term is sometimes used interchangeably with chronic ABMR, but non-immune causes exist (CNI, HCV, TMA). Banff cg1a (<=25% capillary loops) may be reversible in early stage, but cg2-cg3 is irreversible. Retransplantation after TG graft loss requires DSA management (IVIG, apheresis, or desensitization). Molecular classifier (MMDx) may identify active ABMR even when histology is ambiguous.
---
## 3. KB Rule Summary
| Category | Count |
|---|---|
| diagnostic | 5 |
| monitoring | 4 |
| pathology | 5 |
| presentation | 4 |
| prognosis | 4 |
| treatment | 7 |
| **Total** | **29** |