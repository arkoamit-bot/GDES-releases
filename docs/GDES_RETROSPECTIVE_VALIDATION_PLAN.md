# GDES Retrospective Validation Plan

**Glomerular Disease Expert System (GDES) — Phase 1 Clinical Validation**
**BIRDEM Hospital, Department of Nephrology**
**Document Version:** 1.0 | **Date:** July 2026
**Parent Protocol:** GDES Clinical Validation Protocol v1.0

---

## 1. Objective

To retrospectively validate the diagnostic accuracy, management plan concordance, follow-up recommendation quality, and investigation appropriateness of GDES against nephrologist-established clinical decisions using ≥100 historical patient records from the BIRDEM glomerular disease registry.

---

## 2. Study Design

Cross-sectional, blinded comparison study. For each included patient, GDES is presented with clinical data available at the time of the original clinician encounter. GDES outputs (differential diagnosis, management plan, monitoring plan, investigation suggestions) are independently generated and compared against the clinician's documented decisions.

### 2.1 Reference Standard

The reference standard is the **clinician-established final diagnosis and treatment plan** as documented in the patient's medical record (paper or electronic), confirmed by consultant nephrologist review for the validation sample.

---

## 3. Patient Selection

### 3.1 Source Population

All patients with a coded glomerular disease diagnosis in the BIRDEM GDES registry (`patients.models.Patient`) with at least one clinical encounter between **January 2024 and June 2026**.

### 3.2 Inclusion Criteria

1. Age ≥18 years at time of index encounter
2. Confirmed or suspected glomerular disease (IgA nephropathy, membranous nephropathy, lupus nephritis, ANCA-associated vasculitis, FSGS, minimal change disease, or other biopsy-confirmed GN)
3. Complete diagnostic workup available: renal biopsy result, baseline serum creatinine/eGFR, urine protein quantification (UPCR or 24-hour urine protein)
4. At least one documented clinical encounter with a treatment decision
5. Clinician diagnosis documented in the medical record

### 3.3 Exclusion Criteria

1. Age <18 years (pediatric patients require separate validation)
2. Transplant recipients (different clinical pathway)
3. Incomplete baseline data (missing biopsy or missing eGFR at index encounter)
4. Patients with no documented clinician treatment decision
5. Duplicate records or patients already included in a prior validation cycle

### 3.4 Sampling Strategy

**Consecutive sampling** from the registry database, stratified by disease category to ensure adequate representation:

| Disease Category | Target Minimum | Expected Proportion |
|-----------------|---------------|-------------------|
| IgA Nephropathy | 25 cases | 25% |
| Membranous Nephropathy | 20 cases | 20% |
| Lupus Nephritis | 20 cases | 20% |
| ANCA Vasculitis | 15 cases | 15% |
| FSGS / Minimal Change | 10 cases | 10% |
| Other glomerular diseases | 10 cases | 10% |
| **Total** | **≥100 cases** | **100%** |

If consecutive sampling fails to achieve the minimum per-stratum within the first 120 records reviewed, additional targeted sampling from registry entries is permitted.

---

## 4. Data Extraction Methodology

### 4.1 Data Sources Per Patient

For each included patient, data is extracted from:

1. **Medical record (paper/electronic):** Baseline demographics, clinical presentation, biopsy report, laboratory results, clinician diagnosis, treatment plan, follow-up plan, investigations ordered
2. **GDES registry:** Patient model fields (`latest_egfr`, demographics)
3. **GDES runtime:** AI-generated differential, care pathway, monitoring plan, investigation suggestions — generated at the time of validation by feeding extracted clinical data into the reasoning engine

### 4.2 Extraction Process

1. **Record identification:** Registry query identifies eligible patients
2. **Blinded extraction:** Data extractor records clinician decisions into CRF *before* running GDES for that patient
3. **GDES input preparation:** Extracted clinical data (symptoms, labs, biopsy, demographics) is entered into GDES as structured inputs
4. **GDES output capture:** All AI outputs are captured: `ClinicalProfile.differential`, `ClinicalProfile.care_pathway`, `ClinicalProfile.risk_assessment`, `ClinicalProfile.information_gaps`
5. **Comparison:** Pre-extracted clinician data is compared against GDES outputs using the automated comparison framework (`retrospective_validation.py:_compare_ai_vs_clinician`)

### 4.3 Data Collection Instrument — Structured Case Report Form

Each CRF captures the following fields:

**Section A: Patient Demographics**
- Study ID (de-identified)
- Age, Sex, BMI
- Comorbidities (diabetes, hypertension, others)

**Section B: Disease Profile**
- Disease category (coded)
- Biopsy result (MEST-C score for IgA, ISN/RPS class for LN, PLA2R status for MN, ANCA type for AAV)
- Disease severity (mild/moderate/severe based on eGFR and proteinuria)
- Duration of disease at index encounter

**Section C: Baseline Investigations**
- Serum creatinine, eGFR (CKD-EPI)
- Urine protein (UPCR or 24h protein)
- Serum albumin
- Disease-specific markers (PLA2R, ANCA, anti-dsDNA, C3, C4)
- Other relevant investigations

**Section D: Clinician Decisions (Reference Standard)**
- Clinician final diagnosis (narrative + ICD-coded)
- Treatment plan (first-line, second-line)
- Investigation plan (tests ordered at or near index encounter)
- Follow-up schedule (interval + parameters)
- Risk assessment (clinician's clinical judgment)

**Section E: GDES AI Outputs (auto-populated)**
- AI top-1 diagnosis
- AI top-3 differentials
- AI first-line management recommendation
- AI second-line management recommendation
- AI investigation suggestions
- AI follow-up schedule
- AI risk score

**Section F: Comparison Results (auto-calculated)**
- Diagnosis agreement (yes/no, type of disagreement)
- Treatment agreement (exact/compatible/incompatible)
- Investigation overlap (% of clinician-ordered investigations suggested by AI)
- Follow-up interval agreement (within ±2 weeks: yes/no)

**Section G: Disagreement Documentation (if applicable)**
- Disagreement category (coded):
  - `D01`: Insufficient data in GDES input
  - `D02`: Knowledge base gap
  - `D03`: Clinical judgment difference (both defensible)
  - `D04`: Data entry error
  - `D05`: Temporal data mismatch (data not yet available at index encounter)
  - `D06`: GDES error (incorrect rule firing or reasoning)
- Free-text explanation
- Adjudicator resolution

---

## 5. Blinding Procedures

1. **Data extraction blinding:** The person extracting clinician decisions from medical records does not have access to GDES outputs during extraction.
2. **GDES input blinding:** The person entering clinical data into GDES does not have access to the clinician's diagnosis during data entry.
3. **Comparison analysis blinding:** The initial comparison is automated by the system (`retrospective_validation.py`). Disagreement adjudication is performed by a nephrologist blinded to which specific component (AI or clinician) generated each recommendation.
4. **Adjudication:** A panel of 2 consultant nephrologists reviews all disagreements independently. Discordant adjudications are resolved by a third consultant.

---

## 6. Statistical Methods

### 6.1 Primary Analysis

**Diagnostic agreement:**
- Cohen's Kappa (κ) with 95% CI for overall diagnostic agreement
- Percentage agreement (exact match and top-3 match)
- Confusion matrix by disease category

**Management concordance:**
- Percentage agreement (exact match, compatible-pair match, drug-class match)
- Cohen's Kappa for treatment class agreement
- Override frequency analysis

### 6.2 Secondary Analyses

**Sensitivity and specificity per disease:**
For each major disease category (IgA, MN, LN, AAV), construct 2×2 tables:
- True positive: AI correctly identifies disease when clinician diagnosed it
- False positive: AI identifies disease when clinician diagnosed something else
- False negative: AI fails to list disease in top-3 when clinician diagnosed it
- True negative: AI correctly excludes disease

**Investigation appropriateness:**
- Jaccard similarity index between AI-suggested and clinician-ordered investigations
- Percentage of clinician-ordered investigations that were AI-suggested
- Percentage of AI-suggested investigations that were clinician-ordered

**Follow-up accuracy:**
- Mean absolute difference between AI-recommended and guideline-recommended follow-up intervals
- Percentage within ±2 weeks of guideline standard

**Subgroup analyses:**
- By disease category (stratified Kappa values)
- By disease severity (eGFR <30 vs. 30–60 vs. >60)
- By biopsy availability (biopsy-confirmed vs. clinical diagnosis)

### 6.3 Missing Data Handling

- Cases with >20% missing data elements across the CRF are excluded from primary analysis but reported in a sensitivity analysis
- For cases with 5–20% missing data, multiple imputation is not performed; instead, missing fields are treated as "not available" and the GDES `information_gaps` field is assessed
- Complete case analysis is reported alongside the full-cohort analysis

### 6.4 Software

Statistical analyses will be performed using Python (SciPy, statsmodels) or R (irr package for Kappa, epiR for diagnostic test characteristics).

---

## 7. Disagreement Documentation

All cases where AI and clinician disagree are documented using the structured reason coding system (Section 4.3, Section G). The disagreement distribution is reported as:

| Category | Description | Action |
|----------|-------------|--------|
| D01 | Insufficient data | Improve data capture pipeline |
| D02 | Knowledge base gap | Update disease rules |
| D03 | Clinical judgment difference | Acceptable; document as limitation |
| D04 | Data entry error | Correct and re-analyze |
| D05 | Temporal data mismatch | Adjust validation input timing |
| D06 | GDES error | Debug and fix reasoning engine |

---

## 8. Timeline

| Week | Activity |
|------|----------|
| 1 | Protocol finalization, CRF design, ethics amendment (if needed) |
| 2 | CRF pilot testing on 5 cases, inter-rater reliability check |
| 3–4 | Registry query, patient identification, sequential enrollment begins |
| 3–6 | Data extraction and CRF completion (target: ≥25 cases/week) |
| 5 | Interim quality check (50 cases reviewed, metrics preliminary) |
| 6–7 | Remaining extraction completion, GDES output generation for all cases |
| 7–8 | Automated comparison, disagreement adjudication |
| 8 | Statistical analysis and Phase 1 report drafting |
| 9 | Phase 1 report finalization, Phase 2 decision gate |

---

## 9. Expected Outcomes and Benchmarks

| Metric | Minimum Acceptable | Target | Stretch Goal |
|--------|-------------------|--------|-------------|
| Diagnostic agreement (κ) | ≥0.60 (substantial) | ≥0.75 | ≥0.85 |
| Diagnostic accuracy (exact match) | ≥75% | ≥80% | ≥85% |
| Top-3 diagnostic accuracy | ≥90% | ≥95% | ≥98% |
| Management concordance | ≥80% | ≥85% | ≥90% |
| Investigation overlap (Jaccard) | ≥0.50 | ≥0.65 | ≥0.80 |
| Follow-up appropriateness | ≥75% | ≥80% | ≥85% |
| Critical check compliance | 100% | 100% | 100% |

**Decision rules:**
- If all minimum acceptable thresholds are met → proceed to Phase 2
- If any critical check compliance <100% → mandatory system refinement before Phase 2
- If diagnostic κ <0.60 → major knowledge base review required before Phase 2
- If management concordance <80% → targeted rule refinement required

---

## 10. Reporting Format

The Phase 1 retrospective validation report will follow this structure:

1. **Title page** and study registration details
2. **Abstract** (250 words)
3. **Introduction** and rationale
4. **Methods** (this document, summarized)
5. **Results**
   - Cohort characteristics (table)
   - Diagnostic agreement (table, confusion matrix, κ by disease)
   - Management concordance (table)
   - Investigation appropriateness (table)
   - Follow-up accuracy (table)
   - Subgroup analyses (tables)
   - Disagreement analysis (table, figure)
6. **Discussion**
   - Comparison with published CDSS validation studies
   - Strengths and limitations
   - Implications for Phase 2 design
7. **Conclusion** and Phase 2 recommendation
8. **Appendices**
   - Complete CRF template
   - Full confusion matrices per disease
   - Disagreement case summaries (de-identified)

---

*Appendix: GDES System Components Used in Retrospective Validation*

| Component | Function | Key Output |
|-----------|----------|------------|
| `retrospective_validation.py` | Automated AI-vs-clinician comparison | `CaseComparison`, `AgreementMetrics` |
| `disease_validation.py` | Per-disease compliance checks | `DiseaseValidationReport` |
| `audit.py` | Recommendation audit trail | `RecommendationAudit` records |
| `clinical_checks.py` | Data completeness queries | Overdue, missing biopsy, missing eGFR |
| `clinical_reasoning/models.py` | AI output storage | `ClinicalProfile`, `ClinicalInsight` |

*Source code reference: All services under `clinical_reasoning/services/`*

---

*Document prepared as Phase 1 of the GDES Clinical Validation Protocol. Version 1.0 — July 2026.*
