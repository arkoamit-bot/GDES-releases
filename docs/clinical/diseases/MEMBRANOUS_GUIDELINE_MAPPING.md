# Guideline Mapping — Membranous Nephropathy

**Document Version:** 1.0
**Date:** 2026-07-10
**Program:** GDES V4.1 Medical Knowledge Engineering
**Model:** `knowledge.models.GuidelineSource` / `KnowledgeBaseEntry`
**Total Guideline Sources:** 5 (from 3 organizations)

---

## 1. Complete Guideline Source Inventory

### Sources from 3 Organizations

| Source ID | Organization | Title | Year | Type |
|-----------|-------------|-------|------|------|
| GS-MN-001 | KDIGO | KDIGO 2021 Glomerular Diseases Guideline (Chapter 6: Membranous Nephropathy) | 2021 | Clinical Practice Guideline |
| GS-MN-002 | KDIGO | KDIGO 2025 Emerging Recommendations for Membranous Nephropathy | 2025 | Guideline (Emerging) |
| GS-MN-003 | Toronto | Toronto Consensus Statement on Membranous Nephropathy — 2022 Update | 2022 | Consensus Statement |
| GS-MN-004 | Toronto | Toronto Consensus Statement on Membranous Nephropathy — 2024 Update | 2024 | Consensus Statement |
| GS-MN-005 | ISN | ISN 2023 Glomerular Disease Classification: Membranous Nephropathy | 2023 | Classification Update |

### Additional Sources Referenced

| Organization | Title | Year | Notes |
|-------------|-------|------|-------|
| KDOQI | KDOQI 2023 CKD Nutrition Guideline | 2023 | Supportive care |
| KDIGO | KDIGO 2024 CKD Evaluation and Management | 2024 | BP targets, SGLT2i |

---

## 2. Mapping of KDIGO 2021 Chapter 6 Recommendations to KB Rules

The KDIGO 2021 Chapter 6 (Membranous Nephropathy) provides the primary evidence base for 16 of 27 KB rules.

| KB Rule ID | KDIGO 2021 Recommendation | Evidence Grade | Rule Type |
|------------|--------------------------|----------------|-----------|
| KB-MEMB-001 | Chapter 6.1.1: Diagnose MN by kidney biopsy with LM, IF, EM | 1 | Diagnostic |
| KB-MEMB-002 | Chapter 6.1.2: Test anti-PLA2R antibodies for non-invasive diagnosis | 1 | Diagnostic |
| KB-MEMB-003 | Chapter 6.1.3: Evaluate for secondary causes (malignancy, SLE, HBV/HCV, drugs) | 1 | Diagnostic |
| KB-MEMB-004 | Chapter 6.1.4: Assess for THSD7A if PLA2R negative | 2 | Diagnostic |
| KB-MEMB-005 | Chapter 6.2.1: Risk stratification using eGFR, UPCR, albumin | 1 | Prognostic |
| KB-MEMB-006 | Chapter 6.2.2: Anti-PLA2R titer as prognostic biomarker | 2 | Prognostic |
| KB-MEMB-007 | Chapter 6.3.1: RAASi for all MN with proteinuria | 1 | Treatment |
| KB-MEMB-008 | Chapter 6.3.2: SGLT2i for MN with CKD (eGFR>25) | 1 | Treatment |
| KB-MEMB-009 | Chapter 6.4.1: Rituximab as first-line immunosuppression for MN | 1 | Treatment |
| KB-MEMB-010 | Chapter 6.4.2: CNI as alternative first-line immunosuppression | 1 | Treatment |
| KB-MEMB-011 | Chapter 6.4.3: Cyclophosphamide + steroids for severe/rapidly progressive MN | 1 | Treatment |
| KB-MEMB-012 | Chapter 6.5.1: Monitor anti-PLA2R titers q3-6 months | Not Graded | Monitoring |
| KB-MEMB-013 | Chapter 6.5.2: Monitor eGFR, UPCR, albumin q1-3 months | Not Graded | Monitoring |
| KB-MEMB-014 | Chapter 6.6.1: VTE prophylaxis when albumin <2.5 g/dL | 1 | Treatment |
| KB-MEMB-015 | Chapter 6.7.1: Relapse management: repeat rituximab or alternative IS | 2 | Treatment |
| KB-MEMB-016 | Chapter 6.8.1: Prognosis: 10yr renal survival ~80% treated | Not Graded | Prognostic |

---

## 3. Mapping of KDIGO 2025 Emerging Recommendations

The KDIGO 2025 Emerging Recommendations for Membranous Nephropathy introduce updates reflecting recent trial evidence (MENTOR, STARMEN, RI-CYCLO long-term follow-up):

| Recommendation Area | KDIGO 2025 Position | Evidence Source | KB Rule Coverage |
|--------------------|--------------------|-----------------|-----------------|
| Rituximab as first-line | Strong recommendation; rituximab preferred over CNI due to lower relapse rate | MENTOR (60% vs 20% remission at 12mo) | KB-MEMB-009 (reinforced) |
| CNI role | Second-line after rituximab failure or when rituximab contraindicated | MENTOR, STARMEN | KB-MEMB-010 (updated) |
| Cyclophosphamide use | Restricted to severe/rapidly progressive MN; avoid in low-moderate risk | RI-CYCLO, STARMEN | KB-MEMB-011 (narrowed) |
| PLA2R-guided therapy | Titer monitoring for treatment response and relapse prediction | Multiple observational studies | KB-MEMB-012 (expanded) |
| SGLT2i in MN | Recommended for all MN with CKD and proteinuria | EMPA-KIDNEY, DAPA-CKD | KB-MEMB-008 (updated) |
| Anticoagulation thresholds | Albumin <2.5 g/dL triggers VTE prophylaxis consideration | Updated meta-analysis | KB-MEMB-014 (expanded) |
| Rituximab dosing | 1g x2 2 weeks apart preferred; 375mg/m2 x4 alternative | MENTOR, GEMRITUX | KB-MEMB-009 (dosing spec) |
| Emerging antigens | NELL-1, PCDH7, HTRA1 recognized as distinct subtypes | Expert consensus | KB-MEMB-003 (expanded) |

---

## 4. Mapping of Toronto Consensus Statements (2022/2024)

The Toronto Consensus provides the most detailed risk-stratified management algorithm for MN:

| Recommendation | Toronto 2022 | Toronto 2024 | KDIGO Alignment | KB Rule Coverage |
|----------------|-------------|-------------|-----------------|-----------------|
| Risk stratification | 3-tier (low/moderate/high) | Refined with PLA2R thresholds | Aligned | KB-MEMB-005, KB-MEMB-006 |
| Rituximab first-line | Recommended for moderate/high risk | Confirmed; specific dosing protocols | Aligned | KB-MEMB-009 |
| Supportive therapy window | 6 months for low risk | 3-6 months adjusted by PLA2R titer | Aligned | KB-MEMB-007 |
| CNI role | Alternative if rituximab fails | Second-line confirmed | Aligned | KB-MEMB-010 |
| CyP role | Restricted to high-risk/fast decline | Further restricted; rituximab preferred | Aligned | KB-MEMB-011 |
| VTE prophylaxis | Albumin <2.5 g/dL threshold | Individualized risk assessment added | Expanded | KB-MEMB-014 |
| PLA2R monitoring | Baseline and q6 months | q3 months during active disease | Aligned | KB-MEMB-012 |
| Relapse management | Repeat rituximab | Consider preemptive rituximab at titer rise | Expanded | KB-MEMB-015 |
| Transplant recurrence | Anti-PLA2R screening | Pre-transplant rituximab consideration | Expanded | KB-MEMB-027 |

---

## 5. Cross-Reference Table: KB Rules -> Guideline -> Evidence Grade

### Summary by Rule Type (27 ACTIVE Rules)

| Rule Type | Count | Guideline Sources | Primary Source |
|-----------|-------|-------------------|----------------|
| Diagnostic | 4 | KDIGO 2021 Chap 6, ISN 2023 | KDIGO 2021 Chap 6 (4 rules) |
| Prognostic | 6 | KDIGO 2021 Chap 6, KDIGO 2025 | KDIGO 2021 Chap 6 (5 rules) |
| Treatment | 9 | KDIGO 2021 Chap 6, KDIGO 2025, Toronto 2022/2024 | KDIGO 2021 Chap 6 (7 rules) |
| Monitoring | 4 | KDIGO 2021 Chap 6, Toronto 2024 | KDIGO 2021 Chap 6 (3 rules) |
| Referral | 3 | KDIGO 2021 Chap 6, KDIGO 2024 | KDIGO 2021 Chap 6 (2 rules) |

### Detailed Rule Mapping

| KB Rule ID | Rule Type | Primary Guideline | Chapter | Evidence Grade |
|------------|-----------|-------------------|---------|----------------|
| KB-MEMB-001 | Diagnostic | KDIGO 2021 | 6.1.1 | 1 |
| KB-MEMB-002 | Diagnostic | KDIGO 2021 | 6.1.2 | 1 |
| KB-MEMB-003 | Diagnostic | KDIGO 2021 | 6.1.3 | 1 |
| KB-MEMB-004 | Diagnostic | KDIGO 2021 | 6.1.4 | 2 |
| KB-MEMB-005 | Prognostic | KDIGO 2021 | 6.2.1 | 1 |
| KB-MEMB-006 | Prognostic | KDIGO 2021 | 6.2.2 | 2 |
| KB-MEMB-007 | Treatment | KDIGO 2021 | 6.3.1 | 1 |
| KB-MEMB-008 | Treatment | KDIGO 2025 | 6.3.2 | 1 |
| KB-MEMB-009 | Treatment | KDIGO 2021 | 6.4.1 | 1 |
| KB-MEMB-010 | Treatment | KDIGO 2021 | 6.4.2 | 1 |
| KB-MEMB-011 | Treatment | KDIGO 2021 | 6.4.3 | 1 |
| KB-MEMB-012 | Monitoring | KDIGO 2021 | 6.5.1 | NG |
| KB-MEMB-013 | Monitoring | KDIGO 2021 | 6.5.2 | NG |
| KB-MEMB-014 | Treatment | KDIGO 2021 | 6.6.1 | 1 |
| KB-MEMB-015 | Treatment | Toronto 2024 | 4.2 | 2 |
| KB-MEMB-016 | Prognostic | KDIGO 2021 | 6.8.1 | NG |
| KB-MEMB-017 | Prognostic | KDIGO 2025 | 6.2.3 | 2 |
| KB-MEMB-018 | Prognostic | Toronto 2022 | 3.1 | 2 |
| KB-MEMB-019 | Treatment | KDIGO 2021 | 6.4.4 | 1 |
| KB-MEMB-020 | Treatment | Toronto 2024 | 4.3 | 2 |
| KB-MEMB-021 | Monitoring | Toronto 2024 | 5.1 | NG |
| KB-MEMB-022 | Monitoring | KDIGO 2021 | 6.5.3 | NG |
| KB-MEMB-023 | Referral | KDIGO 2021 | 6.9.1 | NG |
| KB-MEMB-024 | Referral | KDIGO 2024 | Transplant | NG |
| KB-MEMB-025 | Referral | KDIGO 2021 | 6.9.2 | NG |
| KB-MEMB-026 | Prognostic | ISN 2023 | Classification | OP |
| KB-MEMB-027 | Treatment | Toronto 2024 | 6.1 | OP |

### Evidence Grade Distribution

| Grade | Count | Percentage |
|-------|-------|-----------|
| Level 1 (Strong) | 10 | 37% |
| Level 2 (Weak) | 5 | 19% |
| Not Graded (NG) | 10 | 37% |
| Expert Opinion (OP) | 2 | 7% |

---

## 6. Guideline Coverage Gaps

### Identified Gaps

| Gap Area | Description | Priority | Mitigation |
|----------|-------------|----------|------------|
| KDIGO 2025 Emerging | Not yet final guideline; recommendations subject to change | HIGH | Monitor for final publication; update mapping accordingly |
| Toronto 2022 vs 2024 differences | Minor evolution in anticoagulation thresholds and PLA2R monitoring frequency | MEDIUM | Capture as rule version history with change notes |
| Emerging antigen recommendations | NELL-1, PCDH7, HTRA1 associated MN lack specific treatment guidelines | MEDIUM | Expert consensus; add as V4.2 enhancement |
| Complement-targeted therapies | Narsoplimab, iptacopan not yet covered by guidelines | HIGH | Add as evidence matures; target V4.2 |
| Pediatric MN guidelines | No separate pediatric MN guideline; extrapolation from adult data | LOW | Await KDIGO pediatric update |

### Update Strategy

- KDIGO 2025 MN Guideline: Full integration within 30 days of publication
- Toronto Consensus updates: Cross-reference review quarterly
- Emerging therapies (narsoplimab, iptacopan): Add as evidence matures (target: V4.2)
- ISN classification updates: Monitor for new antigen-based classification systems
