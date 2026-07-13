# GDES Clinical Validation Protocol

**Glomerular Disease Expert System (GDES) — Version 7.1**
**BIRDEM Hospital, Department of Nephrology**
**Document Version:** 1.0 | **Date:** July 2026
**Protocol Status:** Draft for Ethics Committee Review

---

## 1. Introduction

### 1.1 Background

The Glomerular Disease Expert System (GDES) is a clinical decision support system (CDSS) developed for the management of glomerular diseases at BIRDEM Hospital, Dhaka, Bangladesh. GDES integrates a clinical reasoning engine, disease-specific validation checklists (KDIGO 2021/2024), automated follow-up scheduling, and a research platform into a unified Django-based application. As of Version 7.1, the system comprises 195 passing automated tests across all core modules.

### 1.2 Rationale for Clinical Validation

Software engineering completeness (functional tests, integration tests) does not establish clinical utility or safety. GDES must undergo structured clinical validation to demonstrate:

- Diagnostic concordance with expert nephrologist assessments
- Appropriateness of management, investigation, and monitoring recommendations
- Fidelity of follow-up scheduling and research data capture
- Acceptable safety profile for patient-adjacent use

### 1.3 Objectives

1. To evaluate the diagnostic accuracy of GDES differential diagnoses against nephrologist gold-standard diagnoses
2. To measure agreement between AI-generated management plans and clinician treatment decisions
3. To assess follow-up recommendation accuracy and monitoring plan adequacy
4. To validate research data quality and guideline adherence across the GDES knowledge base
5. To identify and characterize systematic disagreements for targeted system refinement

---

## 2. Validation Framework Overview

The validation follows a sequential two-phase design:

| Phase | Design | Sample | Duration | Primary Outcome |
|-------|--------|--------|----------|-----------------|
| **Phase 1: Retrospective** | Cross-sectional, blinded comparison | ≥100 historical records | 4–6 weeks | Diagnostic agreement rate |
| **Phase 2: Prospective Pilot** | Single-center, interventional (AI-assisted care) | 150–200 patient encounters | 3–6 months | Guideline adherence & safety |

Phase 2 proceeds only if Phase 1 meets predefined success criteria (Section 6).

---

## 3. Validation Domains

Each domain maps to specific GDES components and validation checkpoints.

### 3.1 Diagnostic Accuracy

**GDES component:** `ClinicalProfile.differential` field, reasoning engine (`clinical_reasoning/services/engine.py`), disease validation service (`clinical_reasoning/services/disease_validation.py`)

**Assessment:** Whether the GDES top-ranked differential diagnosis matches the clinician-established final diagnosis.

**Metrics:**
- Top-1 diagnostic accuracy (exact match)
- Top-3 diagnostic accuracy (correct diagnosis within top 3)
- Cohen's Kappa (κ) for categorical agreement
- Sensitivity, specificity, PPV, NPV per disease category

### 3.2 Management Plan Agreement

**GDES component:** `ClinicalProfile.care_pathway` field, audit trail (`clinical_reasoning/services/audit.py`), `audit_management_plan()`

**Assessment:** Whether GDES first-line and second-line treatment recommendations are therapeutically compatible with clinician decisions.

**Metrics:**
- Drug-class concordance rate
- Therapeutic compatibility score (compatible pairs mapped in `retrospective_validation.py:_treatments_compatible`)
- Override frequency and reasons

### 3.3 Follow-Up Recommendation Accuracy

**GDES component:** `ClinicalInsight` (category: `monitoring`, `care_gap`), `ClinicalProfile.milestones`

**Assessment:** Whether recommended follow-up intervals, monitoring parameters, and escalation criteria align with guideline standards (KDIGO 2021/2024).

**Metrics:**
- Follow-up interval appropriateness (within ±2 weeks of guideline-recommended interval)
- Monitoring parameter completeness (percentage of required parameters captured)
- Escalation pathway completeness per `DISEASE_VALIDATION_CHECKS` pathway checks

### 3.4 Research Data Quality

**GDES component:** `ClinicalProfile.features_snapshot`, `reasoning_chain`, `information_gaps`

**Assessment:** Completeness, consistency, and usability of GDES-generated data for research purposes.

**Metrics:**
- Field completion rate across research-relevant data elements
- Internal consistency (cross-field validation)
- Data freshness (recency of `last_updated` timestamps)

### 3.5 Guideline Adherence

**GDES component:** Disease-specific validation checklists (`disease_validation.py:DISEASE_VALIDATION_CHECKS`), `RecommendationAudit` records

**Assessment:** Whether GDES recommendations conform to current KDIGO, AARF, and local protocol standards.

**Metrics:**
- Validation score per disease (weighted compliance %)
- Critical check failure rate
- Guideline version currency

---

## 4. Data Sources and Collection Methods

| Data Source | Module | Collection Method |
|-------------|--------|-------------------|
| Patient demographics & diagnoses | `patients.models.Patient` | Registry extraction |
| Lab results (eGFR, UPCR, PLA2R, ANCA, dsDNA, C3/C4) | `labs.models.LabResult` | Automated pull via `_gather_patient_data()` |
| Prescriptions & medications | `prescriptions.models.Prescription` | Automated pull via `_gather_patient_data()` |
| Vital signs (BP, weight) | `vitals.models.VitalSign` | Automated pull via `_gather_patient_data()` |
| Biopsy reports | `pathology.models.Biopsy` | Manual extraction + structured CRF |
| Clinical encounters | `encounters.models.ClinicalEncounter` | Manual extraction + structured CRF |
| AI differential & care pathway | `ClinicalProfile` JSON fields | GDES runtime generation |
| Clinician decisions | `clinical_decisions.models.ClinicalDecision` | Manual extraction from paper/electronic records |
| Audit trail | `knowledge.models.RecommendationAudit` | Automated capture |

### 4.1 Structured Case Report Forms (CRF)

For each validation case, a standardized CRF captures:

1. **Patient identifier** (de-identified for validation)
2. **Disease category** (IgA nephropathy, membranous, lupus nephritis, ANCA vasculitis, other)
3. **Disease severity** (mild/moderate/severe based on eGFR and proteinuria)
4. **Biopsy result** (MEST-C, ISN/RPS class, PLA2R status, ANCA type)
5. **Clinician diagnosis** (narrative + coded)
6. **Clinician treatment plan** (narrative + coded)
7. **Clinician follow-up plan** (interval + parameters)
8. **Clinician investigations ordered**
9. **GDES AI outputs** (auto-generated from system for each domain)
10. **Comparison results** (auto-calculated agreement metrics)

---

## 5. Statistical Analysis Plan

### 5.1 Primary Analysis

**Diagnostic agreement:** Cohen's Kappa with 95% confidence interval. Interpretation per Landis & Koch: <0.00 poor, 0.00–0.20 slight, 0.21–0.40 fair, 0.41–0.60 moderate, 0.61–0.80 substantial, 0.81–1.00 almost perfect.

**Management concordance:** Percentage agreement with exact and compatible-pair matching. Kappa for categorical treatment class agreement.

### 5.2 Secondary Analyses

- **Sensitivity/Specificity per disease category:** 2×2 confusion matrices for each major glomerular disease
- **Subgroup analyses:** By disease type, disease severity (eGFR <30, 30–60, >60), and clinician experience level (junior registrar vs. consultant)
- **Disagreement characterization:** Structured reason coding for all disagreements (insufficient data, knowledge base gap, clinical judgment difference, data entry error)
- **Missing data impact:** Sensitivity analysis excluding cases with >20% missing data elements

### 5.3 Sample Size Justification

For detecting a diagnostic agreement rate of 80% (κ = 0.75) with a 95% CI width of ±8%:

- **n = 100** yields 95% CI: 72.1%–87.9%
- **n = 150** yields 95% CI: 73.5%–86.5%

We target **≥100 retrospective cases** (minimum viable) and **150–200 prospective encounters** for adequate precision. Disease-specific subgroup analyses (IgA, MN, LN, AAV) require ≥20 cases each; the sample is stratified to ensure this.

---

## 6. Outcome Measures and Definitions

| Outcome | Definition | Success Threshold |
|---------|------------|-------------------|
| Diagnostic agreement rate | Top-1 AI diagnosis matches clinician final diagnosis | ≥80% |
| Management concordance rate | AI treatment class matches clinician (exact or compatible) | ≥85% |
| Follow-up appropriateness | AI-recommended interval within ±2 weeks of guideline standard | ≥80% |
| Investigation relevance | AI-suggested investigations are guideline-indicated | ≥90% |
| Critical check compliance | No critical validation checks failed (`critical` severity in `DISEASE_VALIDATION_CHECKS`) | 100% |
| Guideline adherence score | Weighted compliance across all disease validation checks | ≥75% |
| Safety alerts (prospective) | False-positive safety alerts per 100 encounters | <5 |
| Clinician acceptance rate (prospective) | AI recommendations accepted without modification | ≥70% |

---

## 7. Quality Control Procedures

1. **Dual data entry:** 10% of retrospective CRFs independently entered by a second reviewer; discrepancy rate must be <5%.
2. **Automated validation checks:** Pre-analysis data quality scripts verify field completeness, date logic, and value ranges.
3. **Blinding:** During retrospective validation, the comparison analyst is blinded to GDES outputs until clinician data is fully captured.
4. **Audit trail integrity:** All `RecommendationAudit` records are timestamped and immutable; completeness verified against reasoning engine call logs.
5. **Inter-rater reliability:** For subjective disagreement coding, two reviewers independently classify reasons; κ ≥ 0.60 required for agreement coding reliability.

---

## 8. Timeline and Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| Protocol finalization & ethics submission | Week 1 | Approved protocol, ethics application |
| CRF design & pilot testing | Week 2 | Finalized CRFs, pilot on 5 cases |
| Retrospective data extraction (Phase 1) | Weeks 3–6 | ≥100 completed CRFs |
| Retrospective analysis & report | Weeks 7–8 | Phase 1 validation report |
| Phase 2 decision gate | Week 9 | Go/no-go decision |
| Prospective pilot setup & training | Weeks 9–11 | Trained clinicians, configured system |
| Prospective data collection (Phase 2) | Weeks 12–24 | 150–200 encounter records |
| Prospective analysis & final report | Weeks 25–28 | Final validation report |

---

## 9. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **Principal Investigator** | Protocol oversight, ethics liaison, final report approval |
| **Clinical Validation Lead** | Day-to-day coordination, CRF review, disagreement adjudication |
| **Data Extraction Team** | Paper/electronic record abstraction into CRFs |
| **Biostatistician** | Sample size calculation, statistical analysis, report generation |
| **GDES Technical Lead** | System configuration, AI output generation, data export |
| **Nephrology Consultants (≥3)** | Gold-standard diagnosis assignment, clinical judgment adjudication |
| **Nursing Coordinator** | Patient scheduling, prospective data collection support |

---

## 10. Ethics and Data Governance

### 10.1 Ethics Approval

This protocol requires approval from the BIRDEM Institutional Review Board (IRB) prior to any patient data collection. The retrospective phase uses de-identified historical records; the prospective phase involves clinical workflow modification with informed consent.

### 10.2 Data Protection

- All patient identifiers are replaced with study-specific codes; a master linkage file is held separately by the Principal Investigator
- Data is stored on password-protected, encrypted institutional servers
- Access is restricted to named study personnel
- The study complies with Bangladesh National Research Ethics Guidelines and institutional data governance policies

### 10.3 Patient Safety (Prospective Phase)

GDES operates as a **decision support** tool only. All AI recommendations require clinician review and explicit acceptance before implementation. GDES does not autonomously prescribe, order investigations, or modify treatment. A clinician override mechanism is built into every recommendation pathway (`override_allowed` flag in `RecommendationAudit`). Safety alerts are generated for any critical-severity recommendations that are overridden.

---

## 11. Reporting

### 11.1 Phase 1 Report

The retrospective validation report will include:

1. Executive summary with headline agreement metrics
2. Patient cohort demographics and disease distribution
3. Diagnostic accuracy results (confusion matrix, κ, sensitivity/specificity per disease)
4. Management concordance results
5. Follow-up and investigation agreement rates
6. Disagreement analysis (structured reason coding, frequency, patterns)
7. Subgroup analyses
8. Recommendations for system refinement

### 11.2 Final Report

The prospective pilot report will include all Phase 1 components plus:

1. Usability metrics (consultation time, clinician acceptance)
2. Safety profile (adverse events, false-positive alerts)
3. Guideline adherence improvement (pre- vs. post-GDES)
4. Patient follow-up completion rates
5. Research data quality metrics
6. Post-pilot refinement recommendations
7. Recommendation for scale-up or further development

---

## Appendix A: Disease-Specific Validation Checklist Summary

| Disease | Total Checks | Critical | Major | Guideline Reference |
|---------|-------------|----------|-------|---------------------|
| IgA Nephropathy | 10 | 4 | 6 | KDIGO 2021 GN 4.1 |
| Membranous Nephropathy | 8 | 3 | 5 | KDIGO 2021 GN 4.2 |
| Lupus Nephritis | 9 | 4 | 5 | KDIGO 2024 LN |
| ANCA Vasculitis | 10 | 4 | 6 | KDIGO 2024 AAV |

*Source: `clinical_reasoning/services/disease_validation.py:DISEASE_VALIDATION_CHECKS`*

## Appendix B: Key System Components for Validation

| Component | File | Purpose |
|-----------|------|---------|
| Disease validation engine | `clinical_reasoning/services/disease_validation.py` | Per-disease compliance checking |
| Retrospective validation engine | `clinical_reasoning/services/retrospective_validation.py` | AI vs. clinician comparison |
| Audit trail | `clinical_reasoning/services/audit.py` | Recommendation traceability |
| Clinical checks | `clinical_reasoning/services/clinical_checks.py` | Data completeness utilities |
| Clinical profile model | `clinical_reasoning/models.py` | Per-patient AI output storage |
| Clinical insight model | `clinical_reasoning/models.py` | Categorized recommendation storage |

---

*Document prepared for BIRDEM IRB submission. Version 1.0 — July 2026.*
