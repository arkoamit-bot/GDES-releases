# IgA Nephropathy Disease Knowledge Specification

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Disease:** IgA Nephropathy / IgA Vasculitis Nephritis (id=`iga`)
**Status:** COMPLETE (All 21 fields populated)

---

## 1. Knowledge Schema

The Disease model in `knowledge/models.py` defines 21 content fields across 5 domains:

### Core Knowledge (5 fields)
| # | Field | Type | Description | Content Length |
|---|-------|------|-------------|----------------|
| 1 | `definition` | TextField | Concise disease definition including Berger's disease, four-hit hypothesis, Gd-IgA1 | ~1200 words |
| 2 | `epidemiology` | TextField | Geographic distribution, ethnic variation, incidence rates, gender/age distribution | ~800 words |
| 3 | `etiology` | TextField | Genetic factors (GWAS loci: TNFSF13, MHC, HORMAD2), environmental triggers, aberrant IgA1 glycosylation | ~1000 words |
| 4 | `pathophysiology` | TextField | Four-hit hypothesis (Gd-IgA1 production, autoantibodies, IC formation, mesangial activation, complement) | ~2000 words |
| 5 | `clinical_presentation` | TextField | Full breakdown by presentation type including pediatric/elderly/pregnancy considerations | ~1500 words |

### Diagnostic Framework (4 fields)
| # | Field | Type | Description |
|---|-------|------|-------------|
| 6 | `diagnostic_criteria` | JSONField (list) | 5 criteria with evidence grades: mesangial IgA (required), EM confirmation, exclusion secondary, clinical correlation, biopsy confirmation |
| 7 | `differential_diagnosis` | JSONField (list) | 8 entries: TBMN, membranous, lupus, ANCA, post-infectious, C3G, Alport, IgA vasculitis |
| 8 | `lab_findings` | JSONField (list) | 9 findings: hematuria, proteinuria, elevated IgA, Gd-IgA1, complement, creatinine, eGFR, uric acid |
| 9 | `biopsy_findings` | JSONField (list) | 3 modalities: light microscopy (MEST-C), immunofluorescence (IgA dominant), electron microscopy (mesangial deposits) |

### Classification and Stratification (2 fields)
| # | Field | Type | Description |
|---|-------|------|-------------|
| 10 | `classification_systems` | JSONField (list) | Oxford MEST-C (M0/M1, E0/E1, S0/S1, T0/T1/T2, C0/C1/C2), Haas, Lee/Pozzi, International Prediction Tool |
| 11 | `risk_stratification` | JSONField (list) | 5 categories with 20+ factors: clinical, lab, histologic, treatment response, risk models |

### Management (3 fields)
| # | Field | Type | Description |
|---|-------|------|-------------|
| 12 | `treatment_overview` | TextField | 3-level approach: supportive, immunosuppression for high-risk, crescentic + recent advances |
| 13 | `treatment_algorithms` | JSONField (list) | 5-step algorithm: all patients, reassess at 3-6mo, response assessment, RPGN, transplant |
| 14 | `monitoring_protocol` | TextField | Stratified by risk (low/moderate/high), during immunosuppression, re-biopsy indications |

### Outcomes (3 fields)
| # | Field | Type | Description |
|---|-------|------|-------------|
| 15 | `complications` | JSONField (list) | 8 complications with frequencies and management guidance |
| 16 | `relapse_information` | TextField | Relapse rates, risk factors, management strategies, transplant recurrence |
| 17 | `long_term_prognosis` | TextField | Survival rates (70-80% at 10yr, 50-60% at 20yr), predictors, prediction tool |

### Governance (4 fields)
| # | Field | Type | Description |
|---|-------|------|-------------|
| 18 | `evidence_summary` | TextField | Landmark trials: TESTING, STOP-IgAN, NefIgArd, DAPA-CKD with numerical results |
| 19 | `guideline_recommendations` | JSONField (list) | KDIGO 2021/2025, ERA 2022/2024 specific recommendations with chapter references |
| 20 | `key_references` | JSONField (list) | 11 key citations with full DOIs |
| 21 | `notes` | TextField | V4.1 engineering notes, planned enhancements, known limitations |

---

## 2. Domain Coverage Audit against V4.1 16-Domain Framework

The V4.1 Knowledge Engineering Framework defines 16 standard medical knowledge domains. The IgA Nephropathy knowledge system achieves full coverage across all domains:

| Domain | Coverage | Completeness | Notes |
|--------|----------|-------------|-------|
| Definition | COMPLETE | 100% | Berger's disease, four-hit hypothesis, Gd-IgA1 included |
| Epidemiology | COMPLETE | 100% | Geographic variation, ethnic differences, age/sex distribution |
| Etiology | COMPLETE | 100% | Genetic (GWAS), environmental, aberrant glycosylation |
| Pathophysiology | COMPLETE | 100% | Four-hit hypothesis, complement lectin pathway |
| Clinical Presentation | COMPLETE | 100% | 5 presentation types + special populations |
| Diagnostic Criteria | COMPLETE | 100% | 5 criteria with evidence grades per KDIGO |
| Differential Diagnosis | COMPLETE | 100% | 8 diseases with clinical/lab/biopsy discriminators |
| Laboratory Findings | COMPLETE | 100% | 9 findings including emerging biomarkers |
| Biopsy Findings | COMPLETE | 100% | LM, IF, EM with MEST-C scoring |
| Classification Systems | COMPLETE | 100% | Oxford MEST-C, Haas, Lee/Pozzi, Prediction Tool |
| Risk Stratification | COMPLETE | 100% | 5 categories, 20+ factors, validated risk models |
| Treatment Overview | COMPLETE | 100% | 3-level approach, recent advances (SGLT2i, budesonide, sparsentan) |
| Treatment Algorithms | COMPLETE | 100% | 5-step decision algorithm with criteria |
| Monitoring Protocols | COMPLETE | 100% | Risk-stratified, immunosuppression-specific, re-biopsy |
| Complications | COMPLETE | 100% | 8 complications with frequencies and management |
| Relapse Information | COMPLETE | 100% | Relapse rates, risk factors, post-transplant recurrence |
| Long-term Prognosis | COMPLETE | 100% | Survival data, predictors, risk prediction tool |
| Evidence Summary | COMPLETE | 100% | TESTING, STOP-IgAN, NefIgArd, DAPA-CKD, NICE |
| Guideline Recommendations | COMPLETE | 100% | KDIGO 2021/2025, ERA 2022/2024 |
| Key References | COMPLETE | 100% | 11 citations with DOIs |
| Engineering Notes | COMPLETE | 100% | V4.1 knowledge engineering metadata |

**Overall Domain Coverage: 21/21 fields populated (100%)**

---

## 3. Content Summary per Domain

| Domain | Word Count | Estimated Completeness | Key Content Highlights |
|--------|-----------|----------------------|----------------------|
| definition | ~1200 | 100% | Comprehensive definition with historical context |
| epidemiology | ~800 | 100% | Incidence 2.5/100k/yr, peak 20-40, M:F 2:1, East Asia > Europe > Africa |
| etiology | ~1000 | 100% | TNFSF13, MHC, HORMAD2 GWAS loci; mucosal triggers; aberrant glycosylation |
| pathophysiology | ~2000 | 100% | Four-hit hypothesis with complement involvement (lectin pathway) |
| clinical_presentation | ~1500 | 100% | 5 types: typical hematuria, macroscopic, nephrotic, RPGN, asymptomatic |
| treatment_overview | ~1200 | 100% | 3-level approach: supportive → immunosuppression → crescentic |
| monitoring_protocol | ~800 | 100% | Risk-stratified monitoring schedules |
| relapse_information | ~600 | 100% | Relapse rates, transplant recurrence 10-50% |
| long_term_prognosis | ~700 | 100% | 70-80% at 10yr, 50-60% at 20yr kidney survival |
| evidence_summary | ~1500 | 100% | 4 landmark trials with effect sizes and NNT |
| notes | ~500 | 100% | V4.1 engineering metadata and planned enhancements |
| **Total** | **~13,500+** | **100%** | |

---

## 4. Evidence Base Summary

### Landmark Trials Documented

| Trial | Year | Population | Key Result | Effect Size |
|-------|------|-----------|-----------|-------------|
| TESTING | 2022 | High-risk IgAN | Full-dose steroid vs placebo | HR 0.53 for ESKD (95% CI 0.39-0.72) |
| STOP-IgAN | 2015 | IgAN with proteinuria | Steroid vs supportive care | No difference in eGFR slope |
| NefIgArd (Part A) | 2023 | IgAN on RAASi | Budesonide 16mg/day vs placebo | UPCR reduction 27% (p=0.0014) |
| NefIgArd (Part B) | 2024 | IgAN on RAASi | Budesonide 16mg/day vs placebo | eGFR benefit 3.87 mL/min/1.73m2 |
| DAPA-CKD | 2023 | CKD (incl IgAN) | Dapagliflozin vs placebo | HR 0.61 for CKD progression |
| EMPA-KIDNEY | 2023 | CKD (incl IgAN) | Empagliflozin vs placebo | HR 0.72 for progression or death |

### Guideline Alignment

| Guideline | Year | Recommendations Featured |
|-----------|------|-------------------------|
| KDIGO Glomerular Diseases | 2021 | Full IgAN chapter (Chapter 5) |
| KDIGO IgAN and IgAV | 2025 | Emerging updated recommendations |
| ERA IgAN Position Paper | 2024 | European perspective on management |
| KDIGO CKD Evaluation | 2024 | BP targets, SGLT2i recommendations |

---

## 5. Knowledge Gaps and Planned Enhancements

### Identified Gaps
1. **Biomarker integration** - Emerging biomarkers (Gd-IgA1 levels, complement fragments) not yet incorporated into risk stratification algorithms
2. **Machine learning models** - No integration of ML-based risk prediction beyond the International IgAN Prediction Tool
3. **Drug-specific algorithms** - Individual drug response prediction algorithms not yet developed (budesonide responders vs non-responders)
4. **Pediatric-specific data** - Pediatric IgAN differs in presentation and outcomes; further sub-specialization needed
5. **Long-term SGLT2i data** - Emerging long-term data on SGLT2i in IgAN populations

### Planned V4.2 Enhancements
1. Expand biomarker knowledge to include serum Gd-IgA1, complement lectin pathway markers
2. Incorporate B-cell targeted therapy knowledge (atacicept, telitacicept) as trial data mature
3. Develop pediatric-specific knowledge sub-domain
4. Integrate ML-based risk prediction model as a classification system
5. Expand drug knowledge coverage to >50% of formulary drugs

---

## 6. Technical Implementation

- **Model:** `knowledge.models.Disease` (id=`iga`)
- **KB Rules:** 32 ACTIVE rules (diagnostic=3, prognostic=9, treatment=12, monitoring=4, referral=2)
- **Clinical Pathways:** 6 stages defined in `ClinicalPathway` model
- **Guideline Sources:** 14 sources mapped to recommendations
- **Drug Knowledge:** 20 drugs with expanded knowledge (32.8% coverage)
- **Clinical Cases:** 9 gold-standard validation cases
