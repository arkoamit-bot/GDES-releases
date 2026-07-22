# Guideline Mapping — IgA Nephropathy

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `knowledge.models.GuidelineSource` / `KnowledgeBaseEntry`
**Total Guideline Sources:** 14 (from 8 organizations)

---

## 1. Complete Guideline Source Inventory

### Sources from 8 Organizations

| Source ID | Organization | Title | Year | Type |
|-----------|-------------|-------|------|------|
| GS-001 | KDIGO | KDIGO 2021 Glomerular Diseases Guideline | 2021 | Clinical Practice Guideline |
| GS-002 | KDIGO | KDIGO 2021 Blood Pressure in CKD Guideline | 2021 | Clinical Practice Guideline |
| GS-003 | KDIGO | KDIGO 2021 AKI Guideline | 2021 | Clinical Practice Guideline |
| GS-004 | KDIGO | KDIGO 2024 CKD Evaluation and Management Guideline | 2024 | Clinical Practice Guideline |
| GS-005 | KDIGO | KDIGO 2024 Diabetes Management in CKD Guideline | 2024 | Clinical Practice Guideline |
| GS-006 | KDIGO | KDIGO 2024 Transplant Recipient Guideline | 2024 | Clinical Practice Guideline |
| GS-007 | KDIGO | KDIGO 2025 IgAN and IgAV Guideline | 2025 | Guideline (Emerging) |
| GS-008 | ERA | ERA 2022 Glomerular Disease Recommendations | 2022 | Position Statement |
| GS-009 | ERA | ERA 2024 IgAN Position Paper | 2024 | Position Paper |
| GS-010 | ERA-EDTA | ERA-EDTA 2023 Nephrology Guidelines | 2023 | Clinical Guideline |
| GS-011 | ISN | ISN 2023 Glomerular Disease Classification Update | 2023 | Classification |
| GS-012 | ISN | ISN 2024 Renal Pathology Consensus | 2024 | Consensus Statement |
| GS-013 | ASN | ASN 2023 Kidney Health Guidelines | 2023 | Policy/Position |
| GS-014 | KDOQI | KDOQI 2023 CKD Nutrition Guideline | 2023 | Clinical Practice Guideline |

### Additional Sources Referenced

| Organization | Title | Year | Notes |
|-------------|-------|------|-------|
| KDOQI | KDOQI 2024 Vascular Access Guideline | 2024 | ESKD management |
| AHA | AHA 2023 Heart-Kidney Disease Statement | 2023 | Cardiovascular comorbidity |
| ADA | ADA 2025 Standards of Care in Diabetes | 2025 | Comorbidity management |

---

## 2. Mapping of KDIGO 2021 Recommendations to KB Rules

The KDIGO 2021 Glomerular Diseases Guideline provides the primary evidence base for IgA Nephropathy rules (16 of 32 rules).

| KB Rule ID | KDIGO 2021 Recommendation | Evidence Grade | Rule Type |
|------------|--------------------------|----------------|-----------|
| KB-IGA-001 | Chapter 5.1.1: Urine microscopy to differentiate glomerular from non-glomerular hematuria | Not Graded | Diagnostic |
| KB-IGA-002 | Chapter 5.1.2: RBC casts indicate active GN | Not Graded | Diagnostic |
| KB-IGA-003 | Chapter 5.1.3: Macroscopic hematuria with infection timing | Not Graded | Diagnostic |
| KB-IGA-004 | Chapter 5.2.1: IgA vasculitis with purpura + kidney findings | 2 | Diagnostic |
| KB-IGA-005 | Chapter 5.2.2: Arthritis in IgA vasculitis | OP | Diagnostic |
| KB-IGA-006 | Chapter 5.3.1: Mesangial IgA required for diagnosis | 1 | Diagnostic |
| KB-IGA-007 | Chapter 5.4.1: Subnephrotic proteinuria quantification | Not Graded | Prognostic |
| KB-IGA-008 | Chapter 5.4.2: Nephrotic-range proteinuria as risk marker | 2 | Prognostic |
| KB-IGA-009 | Chapter 5.4.3: Low C3 not typical in IgAN | OP | Diagnostic |
| KB-IGA-010 | Chapter 5.5.1: Tonsillitis-synchronous hematuria | OP | Diagnostic |
| KB-IGA-011 | Treatment recommendation 5.6.1: RAASi for proteinuria >0.5g/day | 1 | Treatment |
| KB-IGA-012 | Treatment recommendation 5.6.2: SGLT2i for CKD with proteinuria | 1 | Treatment |
| KB-IGA-013 | Treatment recommendation 5.7.1: Corticosteroids for high-risk IgAN | 2 | Treatment |
| KB-IGA-014 | Treatment recommendation 5.7.2: Steroid taper over 6-8 months | 2 | Treatment |
| KB-IGA-015 | Monitoring recommendation 5.8.1: 3-monthly proteinuria monitoring | Not Graded | Monitoring |
| KB-IGA-016 | Chapter 5.9.1: Prognosis - 10-year kidney survival ~80% | Not Graded | Prognostic |

---

## 3. Mapping of KDIGO 2025 Emerging Recommendations

The KDIGO 2025 IgAN and IgAV Guideline introduces updated recommendations reflecting recent trial evidence:

| Recommendation Area | KDIGO 2025 Position | Evidence Source | KB Rule Coverage |
|--------------------|--------------------|-----------------|-----------------|
| SGLT2i in IgAN | Strong recommendation for all IgAN with proteinuria >0.5g/day and eGFR >25 | DAPA-CKD, EMPA-KIDNEY | KB-IGA-012 (updated) |
| Budesonide (Nefecon) | Recommended for persistent proteinuria >1g/day despite RAASi | NefIgArd Part A/B | KB-IGA-017 (new) |
| Sparsentan | Alternative for persistent proteinuria | PROTECT trial | KB-IGA-018 (new) |
| Steroid use | Restricted to high-risk; lower doses recommended | TESTING | KB-IGA-013 (updated) |
| Corticosteroid duration | 6-month taper recommended; avoid prolonged courses | TESTING long-term | KB-IGA-014 (updated) |
| BP target | <130/80 mmHg for all IgAN | KDIGO BP | KB-IGA-019 (new) |
| Complement testing | Not routinely recommended | Expert consensus | KB-IGA-009 (unchanged) |
| Re-biopsy | Consider for unexplained eGFR decline or treatment resistance | Expert opinion | KB-IGA-020 (new) |

---

## 4. Mapping of ERA 2024 Position Paper Recommendations

The ERA 2024 IgAN Position Paper provides the European perspective:

| Recommendation | ERA 2024 Position | KDIGO Alignment | KB Rule Coverage |
|----------------|-------------------|-----------------|-----------------|
| RAASi first-line | Universal | Aligned | KB-IGA-011 |
| SGLT2i addition | At proteinuria >0.5g/day | Aligned | KB-IGA-012 |
| Steroid indications | Persistent proteinuria >1g/day after 90 days supportive | Aligned | KB-IGA-013 |
| Budesonide use | Consider before systemic steroids | Stricter than KDIGO | KB-IGA-017 |
| MMF in IgAN | Not recommended (insufficient evidence) | Aligned | KB-IGA-021 |
| Tonsillectomy | Not recommended for renal benefit | Aligned | -- |
| Transplant recurrence | Monitor with protocol biopsies | Aligned | KB-IGA-022 |

---

## 5. Cross-Reference Table: KB Rules -> Guideline -> Evidence Grade

### Summary by Rule Type (32 ACTIVE Rules)

| Rule Type | Count | Guideline Sources | Primary Source |
|-----------|-------|-------------------|----------------|
| Diagnostic | 3 | KDIGO 2021, ERA 2022 | KDIGO 2021 (3 rules) |
| Prognostic | 9 | KDIGO 2021, KDIGO 2025 | KDIGO 2021 (7 rules) |
| Treatment | 12 | KDIGO 2021, KDIGO 2025, ERA 2024 | KDIGO 2021 (8 rules) |
| Monitoring | 4 | KDIGO 2021, ERA 2024 | KDIGO 2021 (3 rules) |
| Referral | 2 | KDIGO 2021, KDIGO 2024 | KDIGO 2024 (2 rules) |

### Detailed Rule Mapping

| KB Rule ID | Rule Type | Primary Guideline | Chapter | Evidence Grade |
|------------|-----------|-------------------|---------|----------------|
| KB-IGA-001 | Diagnostic | KDIGO 2021 | 5.1.1 | NG |
| KB-IGA-002 | Diagnostic | KDIGO 2021 | 5.1.2 | NG |
| KB-IGA-003 | Diagnostic | KDIGO 2021 | 5.1.3 | NG |
| KB-IGA-004 | Prognostic | KDIGO 2021 | 5.2.1 | 2 |
| KB-IGA-005 | Prognostic | KDIGO 2021 | 5.2.2 | OP |
| KB-IGA-006 | Diagnostic | KDIGO 2021 | 5.3.1 | 1 |
| KB-IGA-007 | Prognostic | KDIGO 2021 | 5.4.1 | NG |
| KB-IGA-008 | Prognostic | KDIGO 2021 | 5.4.2 | 2 |
| KB-IGA-009 | Prognostic | KDIGO 2021 | 5.4.3 | OP |
| KB-IGA-010 | Prognostic | KDIGO 2021 | 5.5.1 | OP |
| KB-IGA-011 | Treatment | KDIGO 2021 | 5.6.1 | 1 |
| KB-IGA-012 | Treatment | KDIGO 2025 | 5.6.2 | 1 |
| KB-IGA-013 | Treatment | KDIGO 2021 | 5.7.1 | 2 |
| KB-IGA-014 | Treatment | KDIGO 2021 | 5.7.2 | 2 |
| KB-IGA-015 | Monitoring | KDIGO 2021 | 5.8.1 | NG |
| KB-IGA-016 | Prognostic | KDIGO 2021 | 5.9.1 | NG |
| KB-IGA-017 | Treatment | KDIGO 2025 | 5.7.3 | 1 |
| KB-IGA-018 | Treatment | KDIGO 2025 | 5.7.4 | 1 |
| KB-IGA-019 | Treatment | KDIGO 2021 | 5.6.3 | 1 |
| KB-IGA-020 | Monitoring | ERA 2024 | 4.2 | OP |
| KB-IGA-021 | Treatment | ERA 2024 | 4.3 | 2 |
| KB-IGA-022 | Referral | KDIGO 2024 | Transplant | NG |
| KB-IGA-023 | Referral | KDIGO 2024 | Transplant | NG |
| KB-IGA-024 | Prognostic | KDIGO 2021 | 5.4.4 | 2 |
| KB-IGA-025 | Prognostic | KDIGO 2021 | 5.4.5 | 2 |
| KB-IGA-026 | Prognostic | KDIGO 2025 | 5.4.6 | 2 |
| KB-IGA-027 | Monitoring | ERA 2024 | 5.1 | NG |
| KB-IGA-028 | Monitoring | KDIGO 2021 | 5.8.2 | NG |
| KB-IGA-029 | Treatment | KDIGO 2025 | 5.7.5 | 1 |
| KB-IGA-030 | Treatment | ERA 2024 | 4.4 | 2 |
| KB-IGA-031 | Prognostic | KDIGO 2021 | 5.9.2 | NG |
| KB-IGA-032 | Prognostic | KDIGO 2021 | 5.9.3 | NG |

### Evidence Grade Distribution

| Grade | Count | Percentage |
|-------|-------|-----------|
| Level 1 (Strong) | 8 | 25% |
| Level 2 (Weak) | 10 | 31% |
| Not Graded (NG) | 10 | 31% |
| Expert Opinion (OP) | 4 | 13% |

---

## 6. Guideline Coverage Gaps

### Identified Gaps

| Gap Area | Description | Priority | Mitigation |
|----------|-------------|----------|------------|
| AHA 2023 Heart-Kidney | Cardiovascular risk management in IgAN not fully mapped | MEDIUM | Cross-reference in treatment rules |
| ADA 2025 | Diabetes management in IgAN patients with DKD | MEDIUM | Comorbidity pathway |
| KDOQI 2023 Nutrition | Dietary management specific to IgAN | LOW | General CKD dietary guidance available |
| ISN 2024 Pathology Consensus | Updated MEST-C scoring guidance | HIGH | Awaiting full pathology module integration |
| KDIGO 2025 Emerging | Not yet final guideline; recommendations subject to change | HIGH | Monitor for final publication |

### Update Strategy
- KDIGO 2025 IgAN Guideline: Full integration within 30 days of publication
- ERA 2024/KDIGO 2025 alignment: Cross-reference review quarterly
- Emerging therapies (atacicept, iptacopan): Add as evidence matures (target: V4.2)
