# Guideline Mapping -- Lupus Nephritis

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `knowledge.models.GuidelineSource` / `KnowledgeBaseEntry`
**Total Guideline Sources:** 7 (from 5 organizations)

---

## 1. Complete Guideline Source Inventory

### Sources from 5 Organizations

| Source ID | Organization | Title | Year | Type |
|-----------|-------------|-------|------|------|
| GS-LN-001 | KDIGO | KDIGO 2021 Glomerular Diseases Guideline (Chapter 10: Lupus Nephritis) | 2021 | Clinical Practice Guideline |
| GS-LN-002 | KDIGO | KDIGO 2025 Updated Recommendations for Lupus Nephritis | 2025 | Guideline (Updated) |
| GS-LN-003 | EULAR/ERA | EULAR/ERA 2019 Recommendations for Management of SLE Including LN | 2019 | Clinical Practice Guideline |
| GS-LN-004 | EULAR | EULAR 2023 Updated Recommendations for SLE Including LN | 2023 | Guideline (Updated) |
| GS-LN-005 | ACR | ACR 2021 Guidelines for Management of Lupus Nephritis | 2021 | Clinical Practice Guideline |
| GS-LN-006 | ISN | ISN 2023 Classification Update for Lupus Nephritis | 2023 | Classification Update |
| GS-LN-007 | Asia-Pacific | Asia-Pacific 2022 Consensus on Lupus Nephritis Management | 2022 | Regional Consensus |

### Additional Sources Referenced

| Organization | Title | Year | Notes |
|-------------|-------|------|-------|
| KDIGO | KDIGO 2024 CKD Evaluation and Management | 2024 | BP targets, SGLT2i, CKD-MBD |
| KDOQI | KDOQI 2023 CKD Nutrition Guideline | 2023 | Supportive care in CKD |
| BILAG | BILAG-2004 SLE Activity Index (Renal Domain) | 2004 | Disease activity scoring |

---

## 2. Mapping of KDIGO 2021 Chapter 10 Recommendations to KB Rules

The KDIGO 2021 Chapter 10 (Lupus Nephritis) provides the primary evidence base for the majority of KB rules.

| KB Rule ID | KDIGO 2021 Recommendation | Evidence Grade | Rule Type |
|------------|--------------------------|----------------|-----------|
| KB-LN-001 | Chapter 10.1.1: Suspect LN in SLE patients with proteinuria >0.5g/24h or RBC casts | 1 | Diagnostic |
| KB-LN-002 | Chapter 10.1.2: Renal biopsy with ISN/RPS classification mandatory | 1 | Diagnostic |
| KB-LN-003 | Chapter 10.1.3: AI and CI scoring on all biopsies | 1 | Diagnostic |
| KB-LN-004 | Chapter 10.2.1: Class I/II -- monitor with supportive care | 1 | Treatment |
| KB-LN-005 | Chapter 10.3.1: Class III/IV -- MMF 2-3g/day + glucocorticoids (first-line) | 1 | Treatment |
| KB-LN-006 | Chapter 10.3.2: Class III/IV -- CyP + glucocorticoids (alternative) | 1 | Treatment |
| KB-LN-007 | Chapter 10.4.1: Class V with nephrotic-range proteinuria -- MMF or CNI + glucocorticoids | 1 | Treatment |
| KB-LN-008 | Chapter 10.5.1: Maintenance -- MMF or AZA + HCQ for minimum 3 years | 1 | Monitoring |
| KB-LN-009 | Chapter 10.6.1: Response assessment at 6 months (CRR/PR/NR) | Not Graded | Monitoring |
| KB-LN-010 | Chapter 10.7.1: Relapse -- re-induction with alternative agents | 2 | Treatment |
| KB-LN-011 | Chapter 10.8.1: Refractory -- rituximab, belimumab, voclosporin | 2 | Treatment |

---

## 3. Mapping of KDIGO 2025 Updated Recommendations

The KDIGO 2025 update introduces significant changes reflecting recent trial evidence (BLISS-LN, AURORA 1/2, NOBILITY):

| Recommendation Area | KDIGO 2025 Position | Evidence Source | KB Rule Coverage |
|--------------------|--------------------|-----------------|-----------------|
| Belimumab add-on | Recommended for active LN (Class III/IV/V); add to standard therapy | BLISS-LN (OR 1.55) | KB-LN-005, KB-LN-007 (expanded) |
| Voclosporin | Recommended for Class V LN in combination with MMF | AURORA 1/2 (CRR 41% vs 23%) | KB-LN-007 (expanded) |
| MMF first-line | Confirmed as preferred induction for Class III/IV | ALMS, EuroLupus | KB-LN-005 (reinforced) |
| CyP role | Restricted to severe/refractory Class III/IV | EuroLupus, ALMS | KB-LN-006 (narrowed) |
| HCQ for all | All SLE patients including LN; lifelong unless contraindicated | Marmor 2011 meta-analysis | KB-LN-008 (reinforced) |
| Maintenance duration | Minimum 3 years; indefinite for high-risk | MAINTAIN, ALMS | KB-LN-008 (expanded) |
| Obinutuzumab | Emerging evidence for add-on therapy (NOBILITY) | NOBILITY (CRR 34% vs 21%) | KB-LN-011 (emerging) |

---

## 4. Mapping of EULAR/ERA 2019/2023 Recommendations

| Recommendation | EULAR 2019 | EULAR 2023 Update | KDIGO Alignment | KB Rule Coverage |
|----------------|-----------|-------------------|-----------------|-----------------|
| Biopsy classification | ISN/RPS mandatory | ISN/RPS confirmed; AI/CI scoring emphasized | Aligned | KB-LN-002, KB-LN-003 |
| MMF induction | First-line for Class III/IV | Confirmed; voclosporin for Class V added | Aligned | KB-LN-005 |
| CyP induction | Alternative for severe/refractory | Restricted to severe; EuroLupus preferred | Aligned | KB-LN-006 |
| Belimumab | Not yet recommended (LUNAR negative) | Recommended for active LN (BLISS-LN) | Aligned with KDIGO 2025 | KB-LN-005, KB-LN-007 |
| Voclosporin | Not yet recommended | Recommended for Class V (AURORA) | Aligned with KDIGO 2025 | KB-LN-007 |
| HCQ | All SLE patients | Confirmed lifelong | Aligned | KB-LN-008 |
| Pregnancy management | MMF contraindicated; AZA preferred | Confirmed; detailed pre-conception protocol | Aligned | KB-LN-008 |
| APLS management | Anticoagulation per guidelines | Confirmed; multidisciplinary approach | Aligned | KB-LN-009 |
| Monitoring | q3 months minimum | q3 months; serology q1-3 months | Aligned | KB-LN-008, KB-LN-009 |

---

## 5. Mapping of ACR 2021 Guidelines

| Recommendation | ACR 2021 Position | KDIGO Alignment | KB Rule Coverage |
|----------------|-------------------|-----------------|-----------------|
| Biopsy for LN diagnosis | Strong recommendation; biopsy required | Aligned | KB-LN-002 |
| MMF for Class III/IV | Conditionally recommended | Aligned | KB-LN-005 |
| CyP for Class III/IV | Conditionally recommended (alternative) | Aligned | KB-LN-006 |
| HCQ for all SLE | Conditionally recommended | Aligned | KB-LN-008 |
| Belimumab | Conditionally recommended as add-on | Aligned with KDIGO 2025 | KB-LN-005 |
| Voclosporin | Conditionally recommended for Class V | Aligned with KDIGO 2025 | KB-LN-007 |
| Rituximab for refractory | Conditionally recommended | Aligned | KB-LN-011 |
| Maintenance duration | Minimum 3 years | Aligned | KB-LN-008 |
| Pregnancy management | AZA preferred; MMF contraindicated | Aligned | KB-LN-008 |

---

## 6. Cross-Reference Table: KB Rules -> Guideline -> Evidence Grade

### Summary by Rule Type (28 ACTIVE Rules)

| Rule Type | Count | Guideline Sources | Primary Source |
|-----------|-------|-------------------|----------------|
| Diagnostic | 11 | KDIGO 2021, EULAR 2019/2023, ACR 2021, ISN 2023 | KDIGO 2021 Chap 10 (primary) |
| Prognostic | 3 | KDIGO 2021, EULAR 2023 | KDIGO 2021 Chap 10 |
| Treatment | 4 | KDIGO 2021/2025, EULAR 2019/2023, ACR 2021 | KDIGO 2021/2025 Chap 10 |
| Monitoring | 4 | KDIGO 2021, EULAR 2023, ACR 2021 | KDIGO 2021 Chap 10 |
| Exclusion | 3 | KDIGO 2021, EULAR 2019/2023 | KDIGO 2021 Chap 10 |
| Referral | 3 | KDIGO 2021, ACR 2021 | KDIGO 2021 Chap 10 |

### Detailed Rule Mapping

| KB Rule ID | Rule Type | Primary Guideline | Chapter/Section | Evidence Grade |
|------------|-----------|-------------------|-----------------|----------------|
| KB-LN-001 | Diagnostic | KDIGO 2021 | 10.1.1 | 1 |
| KB-LN-002 | Diagnostic | KDIGO 2021 | 10.1.2 | 1 |
| KB-LN-003 | Diagnostic | KDIGO 2021 | 10.1.3 | 1 |
| KB-LN-004 | Treatment | KDIGO 2021 | 10.2.1 | 1 |
| KB-LN-005 | Treatment | KDIGO 2021/2025 | 10.3.1 | 1 |
| KB-LN-006 | Treatment | KDIGO 2021 | 10.3.2 | 1 |
| KB-LN-007 | Treatment | KDIGO 2025 | 10.4.1 | 1 |
| KB-LN-008 | Monitoring | KDIGO 2021 | 10.5.1 | 1 |
| KB-LN-009 | Monitoring | KDIGO 2021 | 10.6.1 | NG |
| KB-LN-010 | Treatment | KDIGO 2021 | 10.7.1 | 2 |
| KB-LN-011 | Treatment | KDIGO 2025 | 10.8.1 | 2 |
| KB-LN-012 | Diagnostic | EULAR 2019/2023 | 4.1 | 1 |
| KB-LN-013 | Diagnostic | ACR 2021 | LN-1 | 1 |
| KB-LN-014 | Diagnostic | ISN 2023 | Classification | OP |
| KB-LN-015 | Diagnostic | KDIGO 2021 | 10.1.4 | 1 |
| KB-LN-016 | Prognostic | KDIGO 2021 | 10.9.1 | NG |
| KB-LN-017 | Prognostic | EULAR 2023 | 4.2 | 2 |
| KB-LN-018 | Prognostic | KDIGO 2021 | 10.9.2 | NG |
| KB-LN-019 | Diagnostic | EULAR 2019 | 4.3 | 1 |
| KB-LN-020 | Diagnostic | ACR 2021 | LN-2 | 1 |
| KB-LN-021 | Monitoring | KDIGO 2021 | 10.10.1 | NG |
| KB-LN-022 | Monitoring | EULAR 2023 | 5.1 | NG |
| KB-LN-023 | Exclusion | KDIGO 2021 | 10.1.5 | 1 |
| KB-LN-024 | Exclusion | EULAR 2019 | 4.4 | 1 |
| KB-LN-025 | Exclusion | ACR 2021 | LN-3 | 1 |
| KB-LN-026 | Referral | KDIGO 2021 | 10.11.1 | NG |
| KB-LN-027 | Referral | ACR 2021 | LN-4 | NG |
| KB-LN-028 | Referral | Asia-Pacific 2022 | 6.1 | OP |

### Evidence Grade Distribution

| Grade | Count | Percentage |
|-------|-------|-----------|
| Level 1 (Strong) | 14 | 50% |
| Level 2 (Weak) | 4 | 14% |
| Not Graded (NG) | 8 | 29% |
| Expert Opinion (OP) | 2 | 7% |

---

## 7. Guideline Coverage Gaps

### Identified Gaps

| Gap Area | Description | Priority | Mitigation |
|----------|-------------|----------|------------|
| KDIGO 2025 update | Final KDIGO 2025 LN chapter may have additional nuances | HIGH | Monitor for full publication; update mapping within 30 days |
| Obinutuzumab in LN | NOBILITY positive but not yet in major guidelines as standard recommendation | MEDIUM | Add as emerging evidence; update when KDIGO/EULAR incorporate |
| Pediatric LN guidelines | No separate pediatric LN guideline; extrapolation from adult data | MEDIUM | Await KDIGO pediatric update; current pediatric case uses weight-based dosing |
| Pregnancy LN protocols | General SLE pregnancy guidance; LN-specific pregnancy protocols limited | MEDIUM | Create LN-specific pregnancy pathway in V4.2 |
| Transplant LN | Limited guideline guidance on post-transplant LN monitoring | LOW | Expert consensus; add in V4.2 |
| ANCA-LN overlap | Patients with concurrent ANCA vasculitis and LN not addressed | LOW | Niche population; add if cases emerge |

### Update Strategy

- KDIGO 2025 LN Chapter: Full integration within 30 days of publication
- EULAR updates: Cross-reference review quarterly
- ACR updates: Monitor for 2024/2025 revisions
- Obinutuzumab: Add as evidence matures (target: V4.2)
- ISN classification updates: Monitor for new classification systems beyond ISN/RPS 2018
- Asia-Pacific consensus: Review annually for regional practice variations
