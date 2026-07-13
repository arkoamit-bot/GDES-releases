# C3 Glomerulopathy (C3G) — Completeness Dashboard

**Document ID:** C3G-CD-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Quality Assurance  

---

## 1. Document Purpose

This document provides the 12-domain completeness scoring dashboard for C3 Glomerulopathy knowledge within the BGDDR v4.1 framework. Each domain is scored against predefined completeness criteria, with subdomain breakdown, evidence mapping, and gap analysis. The target overall completeness is >=95%.

---

## 2. Scoring Methodology

### 2.1 Scoring Scale

| Score | Meaning | Criteria |
|---|---|---|
| 0.00-0.49 | Incomplete | Missing core elements; requires major revision |
| 0.50-0.79 | Partial | Key elements present but significant gaps |
| 0.80-0.94 | Good | Most elements present; minor gaps |
| 0.95-1.00 | Complete | All elements present; meets target |

### 2.2 Domain Weighting

All 12 domains are equally weighted (8.33% each) for overall score calculation:

```
Overall Score = Sum(Domain Score) / 12
```

### 2.3 Assessment Date

All assessments are performed as of the document release date: **2026-07-10**.

---

## 3. Domain 1: Disease Knowledge (Score: 1.00)

### 3.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 1.1 | 21-field disease record complete | Yes | C3G_DISEASE_KNOWLEDGE.md Section 2 |
| 1.2 | Definition includes dominant C3, alternative complement pathway, subtypes | Yes | Section 2.1 |
| 1.3 | Epidemiology specified for children and adults | Yes | Section 2.2 |
| 1.4 | Aetiology covers genetic, autoantibody, monoclonal | Yes | Section 2.3 (3 categories) |
| 1.5 | Pathophysiology includes complement cascade, C3 convertase, MAC | Yes | Section 2.4 |
| 1.6 | Clinical presentation covers C3GN and DDD | Yes | Section 2.5 |
| 1.7 | Diagnostic criteria list essential and non-essential | Yes | Section 2.6 (7 criteria) |
| 1.8 | Differential diagnosis includes all major entities | Yes | Section 2.7 (7 conditions) |
| 1.9 | Laboratory findings comprehensive | Yes | Section 2.8 |
| 1.10 | Biopsy findings by LM, IF, EM | Yes | Section 2.9 |
| 1.11 | Classification systems (4 systems) | Yes | Section 2.10 |
| 1.12 | Risk stratification (8 factors) | Yes | Section 2.11 |
| 1.13 | Treatment overview covers all agents | Yes | Section 2.12 |
| 1.14 | Treatment algorithm stepwise (7 steps) | Yes | Section 2.13 |
| 1.15 | Monitoring protocol comprehensive | Yes | Section 2.14 |
| 1.16 | Complications (8 items) | Yes | Section 2.15 |
| 1.17 | Relapse information complete | Yes | Section 2.16 |
| 1.18 | Long-term prognosis quantified | Yes | Section 2.17 |
| 1.19 | Evidence summary with studies | Yes | Section 2.18 |
| 1.20 | Guideline recommendations (6 sources) | Yes | Section 2.19 |
| 1.21 | Key references (10 refs) | Yes | Section 2.20 |
| **Total** | | **21/21** | |

### 3.2 Score Calculation

21/21 criteria met: **1.00 (Complete)**

---

## 4. Domain 2: KB Rules (Score: 1.00)

### 4.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 2.1 | 7 diagnostic rules | Yes | Pathway Stage 1 table + KB inventory |
| 2.2 | 2 prognostic rules | Yes | Pathway Stage 1+4 table references |
| 2.3 | 2 genetic rules | Yes | Pathway Stage 2 |
| 2.4 | 12 treatment rules | Yes | Pathway Stage 3+4+5+6 |
| 2.5 | 6 monitoring rules | Yes | Pathway Stage 2+5+6 |
| 2.6 | Total inventory = 26 ACTIVE rules | Yes | Knowledge State summary |
| 2.7 | All rules linked to guideline source | Yes | GUIDELINE_MAPPING Section 12 |
| 2.8 | Rules integrated with pathway stages | Yes | Pathway Section 9 integration table |
| 2.9 | Rules referenced in clinical cases | Yes | Each case maps to rule domain |
| **Total** | | **9/9** | |

### 4.2 Score Calculation

9/9 criteria met: **1.00 (Complete)**

---

## 5. Domain 3: Guideline Integration (Score: 1.00)

### 5.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 3.1 | KDIGO 2021 Chapter 8 fully mapped | Yes | GUIDELINE_MAPPING Section 6 |
| 3.2 | KDIGO 2025 emerging therapies mapped | Yes | Section 7 |
| 3.3 | ERA/EDTA 2022 diagnostic algorithm mapped | Yes | Section 8 |
| 3.4 | ISN 2023 rare GN consensus mapped | Yes | Section 9 |
| 3.5 | Complement Consensus 2023 mapped | Yes | Section 10 |
| 3.6 | Rare Kidney Disease 2019 transplant mapped | Yes | Section 6 (cross-ref) |
| 3.7 | Cross-reference table (6 guidelines x 17 fields) | Yes | Section 3 |
| 3.8 | Recommendation comparison table | Yes | Section 4 |
| 3.9 | Concordance analysis (full/high/moderate/divergent) | Yes | Section 5 |
| 3.10 | Guideline-to-pathway mapping | Yes | Section 11 |
| 3.11 | Guideline-to-KB-rule mapping | Yes | Section 12 |
| 3.12 | Knowledge gaps and future directions | Yes | Section 13 |
| **Total** | | **12/12** | |

### 5.2 Score Calculation

12/12 criteria met: **1.00 (Complete)**

---

## 6. Domain 4: Clinical Pathways (Score: 1.00)

### 6.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 4.1 | 6 stages defined | Yes | CLINICAL_PATHWAY Section 2 |
| 4.2 | Stage 1: Diagnosis & Classification (30d, 7 actions) | Yes | Section 3 |
| 4.3 | Stage 2: Genetic & Autoantibody Workup (60d, 5 actions) | Yes | Section 4 |
| 4.4 | Stage 3: Supportive Therapy (ongoing, 5 actions) | Yes | Section 5 |
| 4.5 | Stage 4: Active Disease Immunosuppression (180d, 7 actions) | Yes | Section 6 |
| 4.6 | Stage 5: Refractory Disease Complement Inhibitors (365d, 8 actions) | Yes | Section 7 |
| 4.7 | Stage 6: Long-Term Monitoring & Transplant (ongoing, 8 actions) | Yes | Section 8 |
| 4.8 | Decision points per stage | Yes | Each stage |
| 4.9 | KB rule integration table | Yes | Section 9 |
| 4.10 | Pathway performance metrics | Yes | Section 10 |
| 4.11 | Special populations covered | Yes | Section 11 |
| **Total** | | **11/11** | |

### 6.2 Score Calculation

11/11 criteria met: **1.00 (Complete)**

---

## 7. Domain 5: Clinical Cases (Score: 1.00)

### 7.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 5.1 | 8 cases total | Yes | CLINICAL_CASES Section 2 |
| 5.2 | C3GN with MGUS (Case 1) | Yes | Section 3 |
| 5.3 | Post-transplant recurrence (Case 2) | Yes | Section 4 |
| 5.4 | Crescentic C3GN RPGN (Case 3) | Yes | Section 5 |
| 5.5 | Refractory C3GN eculizumab (Case 4) | Yes | Section 6 |
| 5.6 | CFH genetic mutation (Case 5) | Yes | Section 7 |
| 5.7 | Paediatric DDD with retinal drusen (Case 6) | Yes | Section 8 |
| 5.8 | C3GN MPGN C3NeF positive (Case 7) | Yes | Section 9 |
| 5.9 | DDD with partial lipodystrophy (Case 8) | Yes | Section 10 |
| 5.10 | Case summary matrix | Yes | Section 11 |
| 5.11 | Cross-reference to pathway stages | Yes | Section 12 |
| **Total** | | **11/11** | |

### 7.2 Score Calculation

11/11 criteria met: **1.00 (Complete)**

---

## 8. Domain 6: Drug Knowledge (Score: 1.00)

### 8.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 6.1 | All drug classes covered | Yes | DRUG_KNOWLEDGE Section 2 |
| 6.2 | Corticosteroids: dosing, AE, management | Yes | Section 3 |
| 6.3 | MMF: dosing, AE, key advantage | Yes | Section 4 |
| 6.4 | Cyclophosphamide: dosing, AE, contraindications | Yes | Section 5 |
| 6.5 | Rituximab: regimens, AE, monitoring | Yes | Section 6 |
| 6.6 | Eculizumab: dosing, AE, monitoring (CH50) | Yes | Section 7 |
| 6.7 | Iptacopan: dosing, monitoring | Yes | Section 8 |
| 6.8 | Pegcetacoplan: dosing, re-biopsy protocol | Yes | Section 9 |
| 6.9 | Plasma therapy (FFP and PLEX) | Yes | Section 10 |
| 6.10 | Supportive medications (RAASi, statins, diuretics) | Yes | Section 11 |
| 6.11 | Vaccination guidance (meningococcal mandatory) | Yes | Section 12 |
| 6.12 | Drug selection algorithm by scenario | Yes | Section 13 |
| 6.13 | Drug summary table | Yes | Section 14 |
| **Total** | | **13/13** | |

### 8.2 Score Calculation

13/13 criteria met: **1.00 (Complete)**

---

## 9. Domain 7: Risk Stratification (Score: 1.00)

### 9.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 7.1 | 8 risk factors enumerated | Yes | DISEASE_KNOWLEDGE Section 2.11 |
| 7.2 | Histologic pattern as risk factor | Yes | Section 2.11 row 1 |
| 7.3 | Proteinuria impact described | Yes | Section 2.11 row 2 |
| 7.4 | eGFR at diagnosis as risk factor | Yes | Section 2.11 row 3 |
| 7.5 | Age-specific risk (children vs adults) | Yes | Section 2.11 row 4 |
| 7.6 | C3NeF as uncertain risk factor | Yes | Section 2.11 row 5 |
| 7.7 | MGUS association as high risk | Yes | Section 2.11 row 6 |
| 7.8 | Genetic vs acquired distinction | Yes | Section 2.11 row 7 |
| 7.9 | Treatment response prediction | Yes | Section 2.11 row 8 |
| 7.10 | Prognostic rules (C3G-PR-01 to PR-02) | Yes | CLINICAL_PATHWAY Section 3-4 |
| 7.11 | Risk stratification in clinical cases | Yes | Case 3 (crescents), Case 5 (genetic) |
| **Total** | | **11/11** | |

### 9.2 Score Calculation

11/11 criteria met: **1.00 (Complete)**

---

## 10. Domain 8: Evidence Integration (Score: 1.00)

### 10.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 8.1 | Evidence summary with study categories | Yes | DISEASE_KNOWLEDGE Section 2.18 |
| 8.2 | Key clinical studies cited | Yes | DISEASE_KNOWLEDGE Section 4.1 |
| 8.3 | Key references (10) with DOI/author/year | Yes | DISEASE_KNOWLEDGE Section 2.20 |
| 8.4 | Evidence linked to guideline recommendations | Yes | GUIDELINE_MAPPING Section 4 |
| 8.5 | Knowledge gaps documented | Yes | DISEASE_KNOWLEDGE Section 4.2 |
| 8.6 | GRADE/evidence level per treatment | Yes | DRUG_KNOWLEDGE Section 2 |
| 8.7 | Trial details in clinical cases | Yes | Case 4 (eculizumab), Case 5 (CFH) |
| 8.8 | Phase 2 evidence for complement inhibitors | Yes | GUIDELINE_MAPPING Section 7 |
| **Total** | | **8/8** | |

### 10.2 Score Calculation

8/8 criteria met: **1.00 (Complete)**

---

## 11. Domain 9: Monitoring (Score: 1.00)

### 11.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 9.1 | C3/C4 complement monitoring schedule | Yes | CLINICAL_PATHWAY Stage 6 |
| 9.2 | MMF monitoring (CBC monthly) | Yes | DRUG_KNOWLEDGE Section 4.4 |
| 9.3 | Steroid monitoring (BP, glucose, bone density) | Yes | DRUG_KNOWLEDGE Section 3.3 |
| 9.4 | Cyclophosphamide monitoring (CBC, urinalysis weekly) | Yes | DRUG_KNOWLEDGE Section 5.4 |
| 9.5 | Rituximab monitoring (CD19, IgG, HBV) | Yes | DRUG_KNOWLEDGE Section 6.4 |
| 9.6 | Eculizumab monitoring (CH50) | Yes | DRUG_KNOWLEDGE Section 7.4 |
| 9.7 | Complement inhibitor: meningococcal vaccination | Yes | DRUG_KNOWLEDGE Section 12 |
| 9.8 | Re-biopsy for histologic response | Yes | CLINICAL_PATHWAY Stage 5 |
| 9.9 | DDD ophthalmology screening | Yes | CLINICAL_PATHWAY Stage 6 |
| 9.10 | MGUS surveillance (annual SPEP/UPEP/sFLC) | Yes | CLINICAL_PATHWAY Stage 6 |
| **Total** | | **10/10** | |

### 11.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 12. Domain 10: Complications and Safety (Score: 1.00)

### 12.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 10.1 | 8 complication categories enumerated | Yes | DISEASE_KNOWLEDGE Section 2.15 |
| 10.2 | CKD progression to ESKD | Yes | Section 2.15 item 1 |
| 10.3 | Infection risk from complement deficiency | Yes | Section 2.15 item 2 |
| 10.4 | Immunosuppression toxicity | Yes | Section 2.15 item 3 |
| 10.5 | Complement inhibitor complications | Yes | Section 2.15 item 4 |
| 10.6 | MGUS progression | Yes | Section 2.15 item 5 |
| 10.7 | Acquired partial lipodystrophy | Yes | Section 2.15 item 6 |
| 10.8 | Retinal drusen / visual impairment | Yes | Section 2.15 item 7 |
| 10.9 | Post-transplant recurrence (highest of all GNs) | Yes | Section 2.15 item 8 |
| 10.10 | Safety monitoring in drug knowledge | Yes | DRUG_KNOWLEDGE Sections 3-9 |
| **Total** | | **10/10** | |

### 12.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 13. Domain 11: Classification (Score: 1.00)

### 13.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 11.1 | C3G subtype classification (DDD vs C3GN) | Yes | DISEASE_KNOWLEDGE Section 2.10 |
| 11.2 | Aetiologic classification (Genetic/Autoantibody/Monoclonal) | Yes | Section 2.10 |
| 11.3 | Histologic pattern classification | Yes | Section 2.10 |
| 11.4 | Disease activity classification (Active vs Chronic) | Yes | Section 2.10 |
| 11.5 | C3GN vs DDD comparison table | Yes | DISEASE_KNOWLEDGE Section 5 |
| 11.6 | Consistent definitions across all documents | Yes | Cross-document validated |
| 11.7 | C3GN definition (mesangial/subepithelial deposits) | Yes | CLINICAL_PATHWAY Stage 1 |
| 11.8 | DDD definition (intramembranous ribbon-like deposits) | Yes | CLINICAL_PATHWAY Stage 1 |
| 11.9 | Classification used in clinical cases | Yes | Cases 1-8 |
| **Total** | | **9/9** | |

### 13.2 Score Calculation

9/9 criteria met: **1.00 (Complete)**

---

## 14. Domain 12: Long-Term Outcomes (Score: 1.00)

### 14.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 12.1 | Renal survival quantified (50-60% at 10 years) | Yes | DISEASE_KNOWLEDGE Section 2.17 |
| 12.2 | ESKD progression rate (30-50% untreated) | Yes | Section 2.17 |
| 12.3 | Risk factors for progression | Yes | Section 2.17 |
| 12.4 | Spontaneous remission rate (<10%) | Yes | Section 2.17 |
| 12.5 | DDD in children better prognosis | Yes | Section 2.17 |
| 12.6 | Post-transplant recurrence (50-80%) | Yes | Section 2.16 |
| 12.7 | Allograft loss from recurrence (30-50%) | Yes | Section 2.16 |
| 12.8 | Long-term monitoring pathway (Stage 6) | Yes | CLINICAL_PATHWAY Section 8 |
| 12.9 | Transplant management with pre-emptive therapy | Yes | CLINICAL_PATHWAY Section 8 |
| 12.10 | Case 2 demonstrates post-transplant recurrence | Yes | CLINICAL_CASES Section 4 |
| **Total** | | **10/10** | |

### 14.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 15. Overall Completeness Score

### 15.1 Domain Score Summary

| # | Domain | Score | Weight | Weighted Score |
|---|---|---|---|---|
| 1 | Disease Knowledge | 1.00 | 8.33% | 8.33 |
| 2 | KB Rules | 1.00 | 8.33% | 8.33 |
| 3 | Guideline Integration | 1.00 | 8.33% | 8.33 |
| 4 | Clinical Pathways | 1.00 | 8.33% | 8.33 |
| 5 | Clinical Cases | 1.00 | 8.33% | 8.33 |
| 6 | Drug Knowledge | 1.00 | 8.33% | 8.33 |
| 7 | Risk Stratification | 1.00 | 8.33% | 8.33 |
| 8 | Evidence Integration | 1.00 | 8.33% | 8.33 |
| 9 | Monitoring | 1.00 | 8.33% | 8.33 |
| 10 | Complications & Safety | 1.00 | 8.33% | 8.33 |
| 11 | Classification | 1.00 | 8.33% | 8.33 |
| 12 | Long-Term Outcomes | 1.00 | 8.33% | 8.33 |
| **Overall** | | **1.00** | **100%** | **100.00%** |

### 15.2 Final Result

| Metric | Result | Target | Status |
|---|---|---|---|
| Overall Completeness Score | **100.00%** | >=95% | PASS |

### 15.3 Interpretation

All 12 domains have achieved 100% completeness at the v1.0 release. No gaps, omissions, or deficiencies were identified across the criteria assessed. The target threshold of >=95% has been exceeded.

### 15.4 Domain Score Visualisation

```
Disease Knowledge      [####################] 100%
KB Rules               [####################] 100%
Guideline Integration  [####################] 100%
Clinical Pathways      [####################] 100%
Clinical Cases         [####################] 100%
Drug Knowledge         [####################] 100%
Risk Stratification    [####################] 100%
Evidence Integration   [####################] 100%
Monitoring             [####################] 100%
Complications & Safety [####################] 100%
Classification         [####################] 100%
Long-Term Outcomes     [####################] 100%
                        ------+------
                Overall | 100% | PASS
                        ------+------
```

---

## 16. Gap Analysis and Improvement Register

### 16.1 Current Gaps (v1.0)

No gaps identified at v1.0 release. All criteria are fully satisfied.

### 16.2 Improvement Register (Future Enhancements)

| ID | Improvement | Target Domain | Priority | Target Version |
|---|---|---|---|---|
| IMP-01 | Add paediatric-specific complement inhibitor dosing | Drug Knowledge | Medium | v1.1.0 |
| IMP-02 | Include cost-effectiveness data for complement inhibitors | Drug Knowledge | Low | v1.1.0 |
| IMP-03 | Expand genetic testing interpretation guide | Risk Stratification | Medium | v1.1.0 |
| IMP-04 | Add rare C3G variant cases (Case 9-10) | Clinical Cases | Low | v1.2.0 |
| IMP-05 | Include novel biomarker monitoring protocols | Monitoring | Medium | v1.1.0 |
| IMP-06 | Add pregnancy-specific pathway branch | Clinical Pathway | Medium | v1.1.0 |

### 16.3 Reassessment Schedule

| Assessment | Date | Scope |
|---|---|---|
| v1.0 baseline | 2026-07-10 | All 12 domains |
| Quarterly update | 2026-10-10 | Review for new evidence |
| Annual reassessment | 2027-07-10 | Full 12-domain scoring |
| Trigger-based | As needed | Major guideline or complement inhibitor trial publication |
