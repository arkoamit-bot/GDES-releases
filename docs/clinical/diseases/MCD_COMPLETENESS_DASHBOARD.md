# Minimal Change Disease (MCD) — Completeness Dashboard

**Document ID:** MCD-CD-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Quality Assurance  

---

## 1. Document Purpose

This document provides the 12-domain completeness scoring dashboard for Minimal Change Disease knowledge within the BGDDR v4.1 framework. Each domain is scored against predefined completeness criteria, with subdomain breakdown, evidence mapping, and gap analysis. The target overall completeness is >=95%.

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
| 1.1 | 21-field disease record complete | Yes | MCD_DISEASE_KNOWLEDGE.md Section 2 |
| 1.2 | Definition includes podocytopathy, FP effacement, no deposits | Yes | Section 2.1 |
| 1.3 | Epidemiology specified for children and adults | Yes | Section 2.2 |
| 1.4 | Primary and secondary aetiologies enumerated | Yes | Section 2.3 (6 categories) |
| 1.5 | Pathophysiology includes T-cell, IL-13, CD80, B-cell | Yes | Section 2.4 |
| 1.6 | Clinical presentation covers full spectrum | Yes | Section 2.5 |
| 1.7 | Diagnostic criteria list 6 elements | Yes | Section 2.6 |
| 1.8 | Differential diagnosis includes all major entities | Yes | Section 2.7 (7 conditions) |
| 1.9 | Laboratory findings comprehensive (10 items) | Yes | Section 2.8 |
| 1.10 | Biopsy findings by LM, IF, EM | Yes | Section 2.9 |
| 1.11 | Classification systems (4 systems) | Yes | Section 2.10 |
| 1.12 | Risk stratification (7 factors) | Yes | Section 2.11 |
| 1.13 | Treatment overview covers all agents | Yes | Section 2.12 |
| 1.14 | Treatment algorithm stepwise | Yes | Section 2.13 |
| 1.15 | Monitoring protocol drug-specific | Yes | Section 2.14 |
| 1.16 | Complications (9 items) | Yes | Section 2.15 |
| 1.17 | Relapse information complete | Yes | Section 2.16 |
| 1.18 | Long-term prognosis quantified | Yes | Section 2.17 |
| 1.19 | Evidence summary with trials | Yes | Section 2.18 |
| 1.20 | Guideline recommendations (5 sources) | Yes | Section 2.19 |
| 1.21 | Key references (10 refs) | Yes | Section 2.20 |
| **Total** | | **21/21** | |

### 3.2 Score Calculation

21/21 criteria met: **1.00 (Complete)**

---

## 4. Domain 2: KB Rules (Score: 1.00)

### 4.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 2.1 | 9 diagnostic rules | Yes | Pathway Stage 1 table + KB inventory |
| 2.2 | 5 prognostic rules | Yes | Pathway Stage 1+3 table references |
| 2.3 | 8 treatment rules | Yes | Pathway Stage 2+4+5 table references |
| 2.4 | 4 monitoring rules | Yes | Pathway Stage 2+6 table references |
| 2.5 | 1 referral rule | Yes | Stage 6 (transition/prognosis) |
| 2.6 | 1 exclusion rule | Yes | Stage 1 (secondary cause screen) |
| 2.7 | Total inventory = 28 ACTIVE rules | Yes | Knowledge State summary |
| 2.8 | All rules linked to guideline source | Yes | GUIDELINE_MAPPING Section 12 |
| 2.9 | Rules integrated with pathway stages | Yes | Pathway Section 9 integration table |
| 2.10 | Rules referenced in clinical cases | Yes | Each case maps to rule domain |
| **Total** | | **10/10** | |

### 4.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 5. Domain 3: Guideline Integration (Score: 1.00)

### 5.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 3.1 | KDIGO 2021 Chapter 5 fully mapped | Yes | GUIDELINE_MAPPING Section 6 |
| 3.2 | KDIGO 2025 emerging therapies mapped | Yes | Section 10 |
| 3.3 | IPNA 2023 paediatric algorithm mapped | Yes | Section 7 |
| 3.4 | ASN 2022 adult-focused mapped | Yes | Section 8 |
| 3.5 | ISN 2023 consensus mapped | Yes | Section 9 |
| 3.6 | Cross-reference table (5 guidelines x 21 fields) | Yes | Section 3 |
| 3.7 | Recommendation comparison table | Yes | Section 4 |
| 3.8 | Concordance analysis (high/moderate/divergent) | Yes | Section 5 |
| 3.9 | Guideline-to-pathway mapping | Yes | Section 11 |
| 3.10 | Guideline-to-KB-rule mapping | Yes | Section 12 |
| 3.11 | Knowledge gaps and future directions | Yes | Section 13 |
| **Total** | | **11/11** | |

### 5.2 Score Calculation

11/11 criteria met: **1.00 (Complete)**

---

## 6. Domain 4: Clinical Pathways (Score: 1.00)

### 6.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 4.1 | 6 stages defined | Yes | CLINICAL_PATHWAY Section 2 |
| 4.2 | Stage 1: Diagnosis & Classification (14d, 7 actions) | Yes | Section 3 |
| 4.3 | Stage 2: Initial Steroid Therapy (120d, 8 actions) | Yes | Section 4 |
| 4.4 | Stage 3: Response Assessment & Taper (90d, 8 actions) | Yes | Section 5 |
| 4.5 | Stage 4: FR/SD Management (365d, 10 actions) | Yes | Section 6 |
| 4.6 | Stage 5: Steroid-Resistant/Refractory (180d, 10 actions) | Yes | Section 7 |
| 4.7 | Stage 6: Long-Term Monitoring (730d, 8 actions) | Yes | Section 8 |
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
| 5.2 | Classic childhood MCD (Case 1) | Yes | Section 3 |
| 5.3 | Frequently relapsing MCD (Case 2) | Yes | Section 4 |
| 5.4 | Steroid-dependent MCD (Case 3) | Yes | Section 5 |
| 5.5 | Adult-onset MCD with AKI (Case 4) | Yes | Section 6 |
| 5.6 | NSAID-induced secondary MCD (Case 5) | Yes | Section 7 |
| 5.7 | MCD secondary to Hodgkin lymphoma (Case 6) | Yes | Section 8 |
| 5.8 | Steroid-resistant to FSGS (Case 7) | Yes | Section 9 |
| 5.9 | Long-term remission after rituximab (Case 8) | Yes | Section 10 |
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
| 6.3 | CNI: cyclosporine and tacrolimus | Yes | Section 4 |
| 6.4 | MMF: dosing, AE, key advantage | Yes | Section 5 |
| 6.5 | Cyclophosphamide: dosing, AE, contraindications | Yes | Section 6 |
| 6.6 | Rituximab: regimens, AE, monitoring | Yes | Section 7 |
| 6.7 | Levamisole: dosing, AE (children) | Yes | Section 8 |
| 6.8 | Supportive medications (RAASi, diuretics, statins) | Yes | Section 9 |
| 6.9 | Vaccination guidance | Yes | Section 10 |
| 6.10 | Drug selection algorithm by scenario | Yes | Section 11 |
| 6.11 | Drug knowledge summary table | Yes | Section 12 |
| 6.12 | Drug interactions documented (CNI) | Yes | Section 4.4 |
| 6.13 | Monitoring parameters per drug | Yes | Sections 3-7 |
| **Total** | | **13/13** | |

### 8.2 Score Calculation

13/13 criteria met: **1.00 (Complete)**

---

## 9. Domain 7: Risk Stratification (Score: 1.00)

### 9.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 7.1 | 7 risk factors enumerated | Yes | DISEASE_KNOWLEDGE Section 2.11 |
| 7.2 | Steroid response as most critical factor | Yes | Section 2.11 row 1 |
| 7.3 | Relapse risk (FR/SD) defined | Yes | Section 2.11 row 2 |
| 7.4 | Adult onset risk described | Yes | Section 2.11 row 3 |
| 7.5 | AKI at presentation as risk factor | Yes | Section 2.11 row 4 |
| 7.6 | Secondary causes risk ranking | Yes | Section 2.11 row 5 |
| 7.7 | Hypertension as prognostic factor | Yes | Section 2.11 row 6 |
| 7.8 | Second-line agent response | Yes | Section 2.11 row 7 |
| 7.9 | Prognostic rules (MCD-PR-01 to PR-04) | Yes | CLINICAL_PATHWAY Section 3-5 |
| 7.10 | Risk stratification in clinical cases | Yes | Case 4 (AKI), Case 7 (FSGS) |
| **Total** | | **10/10** | |

### 9.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 10. Domain 8: Evidence Integration (Score: 1.00)

### 10.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 8.1 | Evidence summary with trial categories | Yes | DISEASE_KNOWLEDGE Section 2.18 |
| 8.2 | RCT evidence cited (prednisone, MMF, CNI, rituximab) | Yes | DISEASE_KNOWLEDGE Section 4.1 |
| 8.3 | Key references (10) with DOI/author/year | Yes | DISEASE_KNOWLEDGE Section 2.20 |
| 8.4 | Evidence linked to guideline recommendations | Yes | GUIDELINE_MAPPING Section 4 |
| 8.5 | Knowledge gaps documented | Yes | DISEASE_KNOWLEDGE Section 4.2 |
| 8.6 | GRADE/evidence level per treatment | Yes | DRUG_KNOWLEDGE Section 2 |
| 8.7 | Trial details in clinical cases | Yes | Case 3 (RITURNS), Case 7 (IMPORT) |
| 8.8 | KDIGO 2025 emerging evidence captured | Yes | GUIDELINE_MAPPING Section 10 |
| **Total** | | **8/8** | |

### 10.2 Score Calculation

8/8 criteria met: **1.00 (Complete)**

---

## 11. Domain 9: Monitoring (Score: 1.00)

### 11.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 9.1 | Steroid monitoring protocol (BP, glucose, bone, growth, eyes) | Yes | DRUG_KNOWLEDGE Section 3 |
| 9.2 | CNI monitoring (trough, Cr, BP, K+, Mg) | Yes | DRUG_KNOWLEDGE Section 4.3 |
| 9.3 | Cyclophosphamide monitoring (CBC, LFT weekly) | Yes | DRUG_KNOWLEDGE Section 6 |
| 9.4 | MMF monitoring (CBC) | Yes | DRUG_KNOWLEDGE Section 5 |
| 9.5 | Rituximab monitoring (CD19, IgG, HBV) | Yes | DRUG_KNOWLEDGE Section 7.3 |
| 9.6 | Urine dipstick frequency (daily induction, weekly taper) | Yes | CLINICAL_PATHWAY Stage 2-3 |
| 9.7 | Relapse surveillance schedule | Yes | CLINICAL_PATHWAY Stage 6 |
| 9.8 | Growth monitoring in children | Yes | CLINICAL_PATHWAY Stage 4 |
| 9.9 | Bone density monitoring (DEXA) | Yes | CLINICAL_PATHWAY Stage 2 |
| 9.10 | Vaccination management guidance | Yes | DRUG_KNOWLEDGE Section 10 |
| **Total** | | **10/10** | |

### 11.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 12. Domain 10: Complications and Safety (Score: 1.00)

### 12.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 10.1 | 9 complication categories enumerated | Yes | DISEASE_KNOWLEDGE Section 2.15 |
| 10.2 | Steroid toxicity detailed | Yes | Section 2.15 item 1 |
| 10.3 | Infection risk documented | Yes | Section 2.15 item 2 |
| 10.4 | AKI as complication | Yes | Section 2.15 item 3 |
| 10.5 | VTE risk documented | Yes | Section 2.15 item 4 |
| 10.6 | Hyperlipidemia documented | Yes | Section 2.15 item 5 |
| 10.7 | Relapse as complication | Yes | Section 2.15 item 6 |
| 10.8 | CNI toxicity detailed | Yes | Section 2.15 item 7 |
| 10.9 | Cyclophosphamide toxicity (cystitis, gonadal, malignancy) | Yes | Section 2.15 item 8 |
| 10.10 | Rituximab infusion reactions | Yes | Section 2.15 item 9 |
| 10.11 | Safety monitoring in drug knowledge | Yes | DRUG_KNOWLEDGE Sections 3-7 |
| **Total** | | **11/11** | |

### 12.2 Score Calculation

11/11 criteria met: **1.00 (Complete)**

---

## 13. Domain 11: Classification (Score: 1.00)

### 13.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 11.1 | Steroid response classification (SSNS/SD/FR/SRNS) | Yes | DISEASE_KNOWLEDGE Section 2.10 |
| 11.2 | Aetiological classification (Primary/Secondary) | Yes | Section 2.10 |
| 11.3 | Relapse frequency classification | Yes | Section 2.10 |
| 11.4 | Age group classification | Yes | Section 2.10 |
| 11.5 | Classification diagram (steroid response flow) | Yes | DISEASE_KNOWLEDGE Section 6 |
| 11.6 | Consistent definitions across all documents | Yes | Cross-document validated |
| 11.7 | FR definition (2 in 6mo or 4 in 12mo) | Yes | CLINICAL_PATHWAY Stage 3 |
| 11.8 | SD definition (relapse during taper or within 2wk) | Yes | CLINICAL_PATHWAY Stage 3 |
| 11.9 | SRNS definition (no remission at 16wk child, 24wk adult) | Yes | CLINICAL_PATHWAY Stage 5 |
| 11.10 | Classification used in clinical cases | Yes | Cases 1-8 |
| **Total** | | **10/10** | |

### 13.2 Score Calculation

10/10 criteria met: **1.00 (Complete)**

---

## 14. Domain 12: Long-Term Outcomes (Score: 1.00)

### 14.1 Criteria

| # | Criterion | Met | Evidence Location |
|---|---|---|---|
| 12.1 | Renal survival quantified (>90% at 10 years) | Yes | DISEASE_KNOWLEDGE Section 2.17 |
| 12.2 | Mortality rate documented (<2%) | Yes | Section 2.17 |
| 12.3 | ESKD progression (exceptional) | Yes | Section 2.17 |
| 12.4 | FSGS transition rate (~20% resistant) | Yes | Section 2.17 |
| 12.5 | Morbidity from steroid toxicity | Yes | Section 2.17 |
| 12.6 | Pregnancy outcomes documented | Yes | Section 2.17 |
| 12.7 | Relapse rate by age group | Yes | Section 2.16 |
| 12.8 | Long-term monitoring pathway (Stage 6) | Yes | CLINICAL_PATHWAY Section 8 |
| 12.9 | Transition to adult care addressed | Yes | CLINICAL_PATHWAY Section 8 |
| 12.10 | Case 8 demonstrates long-term remission durability | Yes | CLINICAL_CASES Section 10 |
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
| IMP-01 | Add patient-facing education summary | Disease Knowledge | Low | v1.1.0 |
| IMP-02 | Include cost-effectiveness data for drug selection | Drug Knowledge | Low | v1.1.0 |
| IMP-03 | Expand genetic testing section | Risk Stratification | Medium | v1.1.0 |
| IMP-04 | Add rare secondary cause cases (Case 9-10) | Clinical Cases | Low | v1.2.0 |
| IMP-05 | Include novel biomarker monitoring protocols | Monitoring | Medium | v1.1.0 |
| IMP-06 | Add pregnancy-specific pathway branch | Clinical Pathway | Medium | v1.1.0 |

### 16.3 Reassessment Schedule

| Assessment | Date | Scope |
|---|---|---|
| v1.0 baseline | 2026-07-10 | All 12 domains |
| Quarterly update | 2026-10-10 | Review for new evidence |
| Annual reassessment | 2027-07-10 | Full 12-domain scoring |
| Trigger-based | As needed | Major guideline publication (e.g., KDIGO 2028) |
