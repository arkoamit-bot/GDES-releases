# GDES Research Publication Plan

**Version:** 7.1  
**Date:** 2026-07-12  
**Status:** Draft  
**Author:** GDES Clinical Informatics Team

---

## 1. Publication Strategy Overview

The GDES pilot at BIRDEM Hospital generates unique data at the intersection of nephrology, clinical informatics, and digital health in a low-resource setting. This plan defines a structured strategy for translating pilot data into peer-reviewed publications, conference presentations, and grey literature that establish GDES as a validated clinical decision support system for glomerular diseases.

**Target output:** Minimum 3 manuscripts submitted within 12 months of pilot completion, with 1–2 additional manuscripts in preparation.

## 2. Target Journals

| Journal | Impact Factor (est.) | Focus | Target Manuscripts |
|---------|---------------------|-------|-------------------|
| *Nephrology Dialysis Transplantation* | ~10 | Nephrology, clinical outcomes | Diagnostic agreement, management adherence |
| *Clinical Journal of the American Society of Nephrology* (CJASN) | ~10 | Nephrology, clinical practice | AI-assisted management, follow-up improvement |
| *Kidney International* | ~19 | Nephrology research | Registry completeness, low-resource informatics |
| *Journal of the American Medical Informatics Association* (JAMIA) | ~7 | Clinical informatics | Workflow efficiency, research automation |
| *BMC Medical Informatics and Decision Making* | ~4 | Digital health, informatics | Implementation experience, workflow study |
| *Digital Health* | ~5 | Digital health innovation | Low-resource setting informatics |
| *Kidney Medicine* | ~5 | Nephrology practice, ASN | Clinical implementation, before-after studies |

## 3. Study Manuscripts

### 3.1 Diagnostic Agreement Study

**Title:** Agreement Between AI-Assisted and Clinician Diagnosis in Biopsy-Proven Glomerular Diseases: A Prospective Diagnostic Accuracy Study

| Element | Detail |
|---------|--------|
| **Research Question** | Does the GDES clinical reasoning engine agree with expert nephrologist diagnosis in biopsy-proven glomerular disease? |
| **Primary Endpoint** | Cohen's kappa (κ) for agreement between AI top-1 diagnosis and biopsy-confirmed diagnosis |
| **Study Design** | Prospective diagnostic agreement study; cross-sectional |
| **Population** | All patients with kidney biopsy and AI recommendation during the pilot period |
| **Data Requirements** | `ClinicalProfile.differential`, `Patient.primary_diagnosis`, biopsy report, `RecommendationAudit` records |
| **Analysis Plan** | κ statistic (95% CI), sensitivity/specificity per disease, confusion matrix, subgroup analysis by disease prevalence |
| **Sample Size** | Minimum 80 biopsy-confirmed patients (power: κ ≥ 0.6 with 80% power, α = 0.05) |
| **Authorship** | Lead: nephrology consultant; co-informaticist; biostatistician; GDES developer |
| **Target Journal** | NDT or CJASN |

### 3.2 AI-Assisted Management Study

**Title:** Impact of AI-Driven Clinical Decision Support on Guideline Adherence in Glomerular Disease Management: A Controlled Before-and-After Study

| Element | Detail |
|---------|--------|
| **Research Question** | Does GDES improve adherence to KDIGO and local guidelines for glomerular disease treatment compared to usual care? |
| **Primary Endpoint** | Guideline adherence score (% of guideline-concordant management actions) |
| **Study Design** | Controlled before-and-after: 6-month pre-GDES period vs. 6-month GDES period |
| **Population** | Patients with active glomerular disease under nephrology care at BIRDEM |
| **Data Requirements** | Treatment records pre/post, `RecommendationAudit.approval_status`, prescription forms, `ClinicalInsight` records |
| **Analysis Plan** | Chi-squared test for adherence proportions, interrupted time series, multivariable logistic regression adjusting for disease severity |
| **Sample Size** | ≥ 100 patients in each period (pre vs. post) |
| **Authorship** | Lead: nephrology consultant; clinical informaticist; biostatistician; data manager |
| **Target Journal** | CJASN or Kidney Medicine |

### 3.3 Follow-Up Improvement Study

**Title:** Automated Follow-Up Scheduling Improves Visit Adherence in Chronic Glomerular Disease: A Before-and-After Implementation Study

| Element | Detail |
|---------|--------|
| **Research Question** | Does automated follow-up scheduling via GDES reduce missed appointments and improve clinical outcomes? |
| **Primary Endpoint** | Proportion of patients with follow-up visit within 30 days of scheduled date |
| **Study Design** | Before-and-after implementation |
| **Population** | Patients with active follow-up during pre-automation and post-automation periods |
| **Data Requirements** | Follow-up visit dates (actual vs. scheduled), `followup_form` data, missed visit records |
| **Analysis Plan** | Proportion comparison (z-test), Kaplan-Meier analysis of time-to-missed-visit, Cox regression for risk factors of non-adherence |
| **Authorship** | Lead: clinical coordinator; nephrology consultant; informaticist |
| **Target Journal** | BMC Medical Informatics and Decision Making |

### 3.4 Registry Completeness Study

**Title:** Structured Data Capture vs. Free-Text Documentation: Impact on Data Quality in a Glomerular Disease Registry

| Element | Detail |
|---------|--------|
| **Research Question** | Does structured data capture in GDES improve completeness, consistency, and computability compared to conventional free-text records? |
| **Primary Endpoint** | Data completeness index (% of mandatory fields populated), data consistency (inter-rater reliability on extracted data) |
| **Study Design** | Retrospective comparison: pre-GDES paper/electronic records vs. GDES-structured records |
| **Population** | Patients enrolled in both pre-GDES and GDES periods at BIRDEM |
| **Data Requirements** | Field-level completeness metrics, data export from `Patient` and related models, quality audit records |
| **Analysis Plan** | Completeness index comparison (paired t-test or Wilcoxon), inter-rater κ for data extraction, time-to-data-entry comparison |
| **Authorship** | Lead: data manager; informaticist; nephrology consultant |
| **Target Journal** | Journal of Clinical Epidemiology or BMC Medical Informatics |

### 3.5 Clinical Workflow Efficiency Study

**Title:** Time-Motion Analysis of AI-Assisted Nephrology Clinical Workflow: A Prospective Observational Study

| Element | Detail |
|---------|--------|
| **Research Question** | How does GDES affect the time required for core nephrology clinical tasks (patient review, recommendation evaluation, documentation)? |
| **Primary Endpoint** | Mean time per clinical encounter (minutes), with and without GDES |
| **Study Design** | Prospective time-motion study; direct observation |
| **Population** | Nephrologists and registrars conducting clinical encounters during the pilot |
| **Data Requirements** | UX review time-motion data, task completion logs, screen recording timestamps |
| **Analysis Plan** | Paired comparison (within-clinician, pre/post), Mann-Whitney U for independent groups, task decomposition analysis |
| **Authorship** | Lead: informaticist; nephrology consultant; UX evaluator |
| **Target Journal** | JAMIA or BMC Medical Informatics |

### 3.6 Research Automation Study

**Title:** Automated Cohort Identification for Glomerular Disease Research: Comparing Algorithmic vs. Manual Chart Review

| Element | Detail |
|---------|--------|
| **Research Question** | Can GDES automated cohort identification replace manual chart review for nephrology research eligibility screening? |
| **Primary Endpoint** | Sensitivity and specificity of automated cohort identification vs. manual chart review (gold standard) |
| **Study Design** | Diagnostic accuracy study; cross-sectional |
| **Population** | Random sample of 200 patient records screened for 3 predefined research cohort criteria |
| **Data Requirements** | `analytics.cohort` service output, manual screening records, `Patient` model data |
| **Analysis Plan** | Sensitivity, specificity, PPV, NPV, F1 score, time-to-screen comparison |
| **Authorship** | Lead: research coordinator; informaticist; nephrology consultant |
| **Target Journal** | JAMIA or Digital Health |

### 3.7 Low-Resource Setting Informatics Study

**Title:** Implementation of a Clinical Decision Support System for Glomerular Disease in a Low-Resource Nephrology Setting: Lessons from Bangladesh

| Element | Detail |
|---------|--------|
| **Research Question** | What are the enablers, barriers, and lessons learned from implementing a rule-based CDS for nephrology in a resource-constrained setting? |
| **Primary Endpoint** | Qualitative: thematic analysis of implementation experience; Quantitative: system uptime, adoption rate, user satisfaction |
| **Study Design** | Mixed-methods implementation science study (CFIR framework) |
| **Population** | All clinical users, IT support staff, hospital administration involved in GDES deployment |
| **Data Requirements** | UX evaluation reports, system logs, interview transcripts, SUS scores, deployment metrics |
| **Analysis Plan** | CFIR framework thematic analysis, process evaluation, cost-effectiveness estimation (implementation cost per patient-year of data quality gained) |
| **Authorship** | Lead: nephrology consultant (Bangladesh); co-PI (international); informaticist; implementation scientist |
| **Target Journal** | Kidney International or Digital Health |

## 4. Manuscript Preparation Timeline

| Phase | Timeframe (from pilot start) | Activities |
|-------|------------------------------|------------|
| **Data maturation** | Months 1–4 | Pilot execution, data collection, quality assurance, UX reviews |
| **First analyses** | Months 3–5 | Preliminary analyses for Studies 3.1 (diagnostic agreement) and 3.5 (workflow efficiency) — these use early data |
| **Manuscript drafting — Wave 1** | Months 5–7 | Draft manuscripts for Studies 3.1, 3.5, and 3.7 (implementation experience) |
| **Wave 1 submission** | Months 7–9 | Submit Studies 3.1, 3.5, 3.7 |
| **Second analyses** | Months 6–9 | Full analyses for Studies 3.2 (management adherence) and 3.4 (registry completeness) — require complete pilot data |
| **Manuscript drafting — Wave 2** | Months 9–11 | Draft manuscripts for Studies 3.2, 3.3, 3.4 |
| **Wave 2 submission** | Months 11–13 | Submit Studies 3.2, 3.3, 3.4 |
| **Wave 3 (if data permits)** | Months 12–15 | Study 3.6 (research automation) and supplementary analyses |

## 5. Data Policies

### 5.1 Data Embargo
- All pilot data subject to a 90-day embargo after pilot completion before external data sharing.
- Internal analysis permitted during the embargo period.
- De-identified datasets for collaborative analysis require PI approval.

### 5.2 Data Access
- Primary access: GDES research team at BIRDEM.
- Collaborative access: Formal data access request to the GDES Data Governance Committee.
- Public data: De-identified aggregate data released with manuscript publication (supplementary materials).

### 5.3 Data Management
- All analyses performed on the GDES development/staging server (not production).
- Analysis scripts version-controlled in the repository (`analytics/services/`).
- Reproducible analysis: Jupyter notebooks or Python scripts accompanying each manuscript.

## 6. Authorship Guidelines

Following ICMJE recommendations:

| Criterion | Requirement |
|-----------|-------------|
| Substantial contributions to conception/design, or data acquisition, or analysis/interpretation | Required for all authors |
| Drafting the work or revising it critically for important intellectual content | Required for all authors |
| Final approval of the version to be published | Required for all authors |
| Agreement to be accountable for all aspects of the work | Required for all authors |

**GDES-specific conventions:**
- Developer contributions qualify under "analysis/interpretation" and "drafting" (informatics manuscripts).
- Clinical users contributing to data collection qualify under "data acquisition."
- Ghost authorship excluded; all contributors acknowledged.
- Corresponding author: lead clinical investigator at BIRDEM.

## 7. Presentation Plan

### 7.1 Conferences

| Conference | Timing | Target Study | Format |
|-----------|--------|-------------|--------|
| **ERA-EDTA Congress** | June (annual) | Diagnostic agreement, workflow efficiency | Oral presentation or poster |
| **ASN Kidney Week** | November (annual) | Management adherence, registry completeness | Poster; abstract for late-breaking if results strong |
| **ISN World Congress of Nephrology** | Biennial (March) | Implementation experience, low-resource informatics | Symposium proposal or poster |
| **MEDINFO** | Biennial (July) | Workflow efficiency, research automation | Full paper or poster |
| **HIMSS Asia-Pacific** | Varies | Implementation, informatics | Exhibition poster |
| **Bangladesh Society of Nephrology** | Annual | All studies | Oral presentation to local community |

### 7.2 Conference Abstract Timeline

| Abstract Deadline | Target Conference | Studies |
|-------------------|-------------------|---------|
| ~6 months post-pilot start | ERA-EDTA (if aligned) | 3.1, 3.5 |
| ~9 months post-pilot start | ASN Kidney Week | 3.1, 3.2, 3.7 |
| ~12 months post-pilot start | ISN WCN or MEDINFO | 3.2, 3.3, 3.4, 3.6 |

## 8. Resource Requirements

| Resource | Estimated Need | Cost Estimate |
|----------|---------------|---------------|
| Biostatistician time | 30–40 days over 12 months | BHD 3,000–4,000 (or institutional collaboration) |
| Medical writing support | 15–20 days (manuscript editing, formatting) | BHD 1,500–2,000 |
| Publication fees (open access) | 3–5 manuscripts × BHD 400–800 | BHD 1,200–4,000 |
| Conference registration and travel | 2–3 international conferences | BHD 3,000–6,000 |
| Abstract submission fees | 5–8 abstracts | BHD 200–400 |
| Research coordinator time | 50% FTE during pilot + 25% post-pilot | Institutional allocation |
| **Total estimated budget** | | **BHD 9,000–17,000** |

## 9. Success Criteria

| Metric | Target |
|--------|--------|
| Manuscripts submitted within 12 months of pilot completion | ≥ 3 |
| Manuscripts accepted within 18 months | ≥ 2 |
| Conference presentations within 12 months | ≥ 3 |
| First/last author position for BIRDEM investigators | ≥ 2 of 3 submissions |
| Open access publication | All manuscripts |

## 10. Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Insufficient sample size for diagnostic agreement study | Pool data across multiple disease groups; use Bayesian estimation for small subgroups |
| Pilot interruption reducing data volume | Ensure minimum 3-month pilot data before first manuscript submission |
| Authorship disputes | Early authorship agreement signed by all team members before pilot start |
| Journal rejection | Pre-select 2–3 target journals per manuscript; prepare rapid re-submission plan |
| Data quality issues limiting analysis | Continuous data quality monitoring during pilot; pre-specified sensitivity analyses |

---

**Document Status:** Draft  
**Next Review:** GDES Research Committee meeting  
**Distribution:** GDES Principal Investigator, BIRDEM Nephrology Department, Statistical Analysis Team
