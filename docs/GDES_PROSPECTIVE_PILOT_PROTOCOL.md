# GDES Prospective Pilot Protocol

**Glomerular Disease Expert System (GDES) — Phase 2 Clinical Validation**
**BIRDEM Hospital, Department of Nephrology, Dhaka, Bangladesh**
**Document Version:** 1.0 | **Date:** July 2026
**Parent Protocol:** GDES Clinical Validation Protocol v1.0
**Prerequisite:** Phase 1 (Retrospective Validation) must meet predefined success criteria

---

## 1. Objective

To prospectively evaluate the clinical utility, safety, usability, and guideline-adherence impact of GDES as a clinical decision support tool in routine nephrology outpatient practice at BIRDEM Hospital over a 3–6 month pilot period.

---

## 2. Study Design

Prospective, single-center, interventional (AI-assisted care) study with a pre-post design. GDES is integrated into the clinical workflow for the intervention period. A 3-month pre-intervention baseline period (retrospective) provides comparative data for guideline adherence and follow-up completion metrics.

---

## 3. Setting

BIRDEM Hospital, Department of Nephrology — outpatient glomerular disease clinic. BIRDEM is a 700-bed tertiary care center and the national referral center for diabetic and kidney diseases in Bangladesh. The nephrology department manages approximately 200–300 glomerular disease patients per month.

---

## 4. Study Duration

| Phase | Duration | Description |
|-------|----------|-------------|
| Pre-pilot preparation | 3 weeks | System setup, clinician training, ethics finalization |
| Baseline data collection | 3 months (retrospective) | Pre-intervention metrics from existing records |
| Prospective pilot enrollment | 3–6 months | Active GDES-assisted clinical encounters |
| Post-pilot analysis & reporting | 1 month | Data analysis, report drafting |

---

## 5. Patient Population

### 5.1 Inclusion Criteria

1. Age ≥18 years
2. Attending the nephrology outpatient clinic at BIRDEM
3. Confirmed or clinically suspected glomerular disease (any type)
4. At least one serum creatinine, urine protein quantification, and clinical encounter documented
5. Able and willing to provide informed consent (for prospective data collection component)

### 5.2 Exclusion Criteria

1. Age <18 years
2. Kidney transplant recipients (different clinical pathway not covered by GDES)
3. Patients already enrolled in the retrospective validation phase (to avoid contamination)
4. Emergency/acute presentations requiring immediate nephrology consultation (GDES is designed for outpatient chronic disease management)
5. Patients whose treating clinician declines participation

### 5.3 Estimated Enrollment

**Target:** 150–200 patient encounters over 3–6 months

**Rationale:** At an estimated 40–60 eligible glomerular disease encounters per month, 3 months yields 120–180 encounters; extending to 6 months ensures ≥200.

---

## 6. Clinician Recruitment and Training

### 6.1 Eligible Clinicians

All nephrology consultants, registrars, and senior house officers involved in the glomerular disease outpatient clinic. Minimum target: 6–10 clinicians.

### 6.2 Training Program

| Session | Duration | Content |
|---------|----------|---------|
| **Session 1: System overview** | 90 minutes | GDES capabilities, limitations, clinical workflow integration |
| **Session 2: Hands-on demonstration** | 60 minutes | Live case walkthrough: data entry → AI output → interpretation |
| **Session 3: Override and documentation** | 30 minutes | How to accept/modify/override AI recommendations; documentation requirements |
| **Session 4: Safety protocols** | 30 minutes | Reporting adverse events, system failures, patient safety concerns |
| **Total training** | 3.5 hours | Per clinician |

### 6.3 Competency Assessment

Each clinician must complete a supervised test case (passing = correct interpretation of AI outputs and appropriate override decisions) before independent use.

---

## 7. Workflow Integration

### 7.1 Clinical Workflow

```
Patient arrives → Nurse records vitals → Clinician opens GDES
    → GDES generates ClinicalProfile (differential, care pathway, monitoring)
    → Clinician reviews AI outputs alongside clinical assessment
    → Clinician makes treatment decision (may accept, modify, or override AI)
    → Clinician documents decision (standard clinical note + GDES interaction log)
    → GDES records RecommendationAudit entry
    → Follow-up scheduling via GDES
```

### 7.2 System Access Points

- **Clinician workstation:** Web-based GDES interface during clinic hours
- **Mobile access:** For reviewing AI outputs during ward rounds or follow-up calls
- **Printed summaries:** Optional patient-friendly care pathway summaries

### 7.3 Integration with Existing Systems

GDES reads from and writes to the existing BIRDEM clinical data infrastructure:
- **Reads:** Patient demographics, lab results, prescriptions, vitals, biopsy reports, clinical encounters
- **Writes:** `ClinicalProfile` (AI outputs), `ClinicalInsight` (recommendations), `RecommendationAudit` (audit trail)
- **Does not modify:** Existing clinical decision records, prescriptions, or orders (read-only integration with existing clinical systems during pilot)

---

## 8. Data Collection Points

### 8.1 Primary Data Collection

| Data Element | Collection Method | Frequency |
|-------------|-------------------|-----------|
| **Consultation time** | Time-stamp logging (GDES open → GDES close) | Every encounter |
| **AI recommendation acceptance** | Clinician interaction log (accept/modify/override) | Every encounter |
| **Override reason** | Structured drop-down + free text | When overridden |
| **Clinician usability rating** | Post-encounter Likert scale (1–5) | Weekly sample (≥20% of encounters) |
| **System availability** | Automated uptime monitoring | Continuous |
| **Data completeness** | Automated field completion check | Every encounter |

### 8.2 Secondary Data Collection

| Data Element | Collection Method | Frequency |
|-------------|-------------------|-----------|
| **Guideline adherence** | Disease validation checklist score (`DISEASE_VALIDATION_CHECKS`) | Every encounter |
| **Patient compliance** | Follow-up attendance rate | Monthly |
| **Follow-up completion** | Scheduled vs. actual visit comparison | Monthly |
| **Lab monitoring adherence** | Ordered vs. guideline-recommended labs | Monthly |
| **Clinical outcomes** | eGFR trend, proteinuria trend, relapse events | Monthly |
| **Adverse events** | Clinician-reported safety events | Continuous |
| **False-positive alerts** | AI safety alerts subsequently overridden without clinical basis | Weekly review |

---

## 9. Endpoints

### 9.1 Primary Endpoints

1. **Guideline adherence improvement:** Change in disease validation checklist score (weighted compliance %) from baseline to pilot period, measured per disease category
2. **AI recommendation acceptance rate:** Proportion of GDES recommendations accepted without modification by the treating clinician
3. **Safety profile:** Rate of clinically significant false-positive safety alerts (alerts that triggered unnecessary clinical action or concern)

### 9.2 Secondary Endpoints

1. **Consultation time impact:** Change in mean consultation time (GDES session duration) compared to historical average (if measurable)
2. **Follow-up completion rate:** Proportion of scheduled follow-up visits attended, compared to pre-intervention baseline
3. **Lab monitoring adherence:** Proportion of guideline-indicated labs ordered at each visit, compared to baseline
4. **Clinician usability score:** Mean Likert rating across all participating clinicians
5. **System reliability:** System uptime percentage, mean time to AI output generation
6. **Clinician override frequency and reasons:** Distribution of override categories
7. **Research data quality:** Field completion rate for research-relevant data elements in `ClinicalProfile.features_snapshot`

### 9.3 Exploratory Endpoints

1. **eGFR trajectory:** Mean eGFR slope during pilot vs. pre-intervention (requires ≥6 months follow-up)
2. **Proteinuria response rate:** Proportion achieving target proteinuria (<1 g/day for IgA, <3.5 g/day for MN)
3. **Time to treatment escalation:** For patients requiring escalation, time from clinical indicator to treatment modification
4. **Patient satisfaction:** Patient-reported experience (if ethics-approved for patient survey)

---

## 10. Sample Size Estimation

For the primary endpoint of guideline adherence improvement:

- **Baseline guideline adherence (estimated from retrospective data):** 65%
- **Target improvement:** 15 percentage points (to 80%)
- **Effect size (Cohen's h):** 0.33 (medium)
- **α = 0.05 (two-sided), Power = 0.80**
- **Required sample:** 146 encounters (paired pre-post analysis)

**Target enrollment: 150–200 encounters** provides adequate power for primary analysis with buffer for exclusions and subgroup analyses.

---

## 11. Safety Monitoring and Stopping Rules

### 11.1 Safety Oversight

A **Data Safety Monitoring Board (DSMB)** comprising 2 senior nephrologists (not involved in daily GDES use) and 1 biostatistician will review safety data at predefined intervals.

### 11.2 Stopping Rules

The pilot will be suspended or terminated if any of the following occur:

1. **Patient safety event:** Any serious adverse event (SAE) judged to be probably or definitely related to GDES-influenced clinical decision-making
2. **Systematic harmful recommendation:** ≥3 cases where GDES recommendation, if followed, would have caused patient harm (as judged by DSMB)
3. **Unacceptable false-positive rate:** >10% of safety alerts are false-positive, causing clinical alarm fatigue
4. **Clinician non-acceptance:** Overall acceptance rate drops below 40%, indicating fundamental clinical distrust
5. **System failure:** >5% downtime during clinic hours, or data integrity breach

### 11.3 Reporting of Safety Events

- **Immediate:** Any SAE reported to PI and DSMB within 24 hours
- **Weekly:** Aggregate safety metrics reviewed by PI
- **Monthly:** Formal safety report to DSMB and IRB

---

## 12. Data Management Plan

### 12.1 Data Collection

- All GDES interactions are logged automatically in the database (`RecommendationAudit`, `ClinicalInsight`, `ClinicalProfile`)
- Clinician override reasons captured via structured forms in the GDES interface
- Manual data entry (patient surveys, consultation timing) via REDCap or equivalent validated data capture system

### 12.2 Data Quality

- Real-time validation rules on data entry fields (range checks, required field enforcement)
- Weekly data quality reports (completeness, consistency, timeliness)
- Monthly data cleaning and lock cycle

### 12.3 Data Storage and Security

- All data stored on BIRDEM institutional servers (encrypted, access-controlled)
- De-identified analysis dataset created for statistical analysis
- Data retained for minimum 5 years per institutional policy
- Compliance with Bangladesh data protection regulations

---

## 13. Statistical Analysis Plan

### 13.1 Primary Analysis

**Guideline adherence improvement:** Paired comparison (baseline vs. pilot) using McNemar's test for binary outcomes and paired t-test or Wilcoxon signed-rank test for continuous compliance scores.

**AI recommendation acceptance:** Descriptive statistics (proportion with 95% CI). Logistic regression to identify predictors of override (disease type, clinician experience, recommendation category).

**Safety profile:** Descriptive statistics (event rates with 95% CI).

### 13.2 Secondary Analyses

- **Consultation time:** Paired t-test or Wilcoxon signed-rank test
- **Follow-up completion:** Chi-square test (baseline vs. pilot)
- **Usability scores:** Descriptive statistics, trend over time (linear regression)
- **Subgroup analyses:** By disease category, clinician experience level, disease severity
- **Multivariable analysis:** Mixed-effects logistic regression (clinician as random effect) to assess independent predictors of AI acceptance

### 13.3 Interim Analysis

A planned interim analysis at the midpoint of the pilot (approximately 75–100 encounters) will review:
- Enrollment rate
- Preliminary safety data
- AI acceptance rate
- Any emerging systematic issues

The DSMB may recommend continuation, protocol modification, or early termination based on interim findings.

---

## 14. Expected Challenges and Mitigations

| Challenge | Mitigation |
|-----------|------------|
| **Clinician resistance to AI** | Emphasize CDS role (not replacement); involve clinicians in system design; provide adequate training; demonstrate early wins |
| **Workflow disruption** | Integrate GDES as optional tool, not mandatory; optimize UI for speed (<2 minutes per encounter); provide quick-reference cards |
| **Data entry burden** | Automate data pull from existing systems; minimize manual entry fields; batch processing for non-urgent data |
| **GDES knowledge gaps for local context** | Include Bangladesh-specific treatment protocols and drug availability in knowledge base; regular updates |
| **Internet/system downtime** | Offline mode for viewing last-generated outputs; graceful degradation; backup data entry on paper |
| **Patient volume variability** | Flexible enrollment period (3–6 months); rolling enrollment; multiple clinic sessions |
| **Loss to follow-up** | Automated reminders via GDES follow-up module; phone contact for missed visits; community health worker support |
| **Ethical concerns about AI in clinical care** | Strict CDS-only role; clinician final authority; transparent patient communication; robust safety monitoring |

---

## 15. Pilot Success Criteria

The pilot is deemed successful if **all** of the following are met:

| Criterion | Threshold |
|-----------|-----------|
| Primary endpoint: guideline adherence improvement | Statistically significant improvement (p <0.05) with ≥10 percentage point increase |
| AI recommendation acceptance rate | ≥70% |
| Serious adverse events related to GDES | 0 |
| False-positive safety alert rate | <5% |
| Clinician usability score (mean Likert) | ≥3.5 / 5.0 |
| System uptime | ≥95% during clinic hours |
| Data completeness | ≥90% of required fields populated |
| Follow-up completion rate | ≥75% (vs. baseline) |

**Decision rules:**
- All criteria met → proceed to scale-up planning
- 1–2 criteria borderline (within 10% of threshold) → targeted refinement + extended pilot
- Any criterion substantially failed → major system revision before re-pilot

---

## 16. Post-Pilot Refinement Process

Following pilot completion and analysis:

1. **System refinement:** Address all identified knowledge gaps, UI issues, and workflow friction points
2. **Knowledge base updates:** Incorporate clinical judgment differences identified in override analysis
3. **Algorithm tuning:** Adjust recommendation confidence thresholds based on acceptance data
4. **Local protocol integration:** Finalize Bangladesh-specific clinical pathways informed by pilot data
5. **Publication preparation:** Draft manuscripts for peer-reviewed nephrology journals
6. **Scale-up planning:** Design multi-center validation or department-wide rollout

---

## 17. Ethics Approval Requirements

1. **Primary ethics approval:** BIRDEM IRB review and approval for the prospective pilot protocol
2. **Amendments:** Any protocol modifications submitted as amendments to IRB
3. **Informed consent:** Written informed consent from all participating clinicians; verbal consent from patients (documented) for the data collection component
4. **Patient notification:** Patients informed that their clinician has access to an AI decision support tool during consultation; right to opt out documented
5. **Adverse event reporting:** SAEs reported to IRB within 72 hours per institutional policy
6. **Data governance:** Study registered with BIRDEM research governance office; data management plan approved by institutional data protection officer

---

## Appendix A: GDES System Components in Prospective Pilot

| Component | Module | Role in Pilot |
|-----------|--------|--------------|
| Clinical reasoning engine | `clinical_reasoning/services/engine.py` | Generates differential diagnosis and care pathway |
| Disease validation | `clinical_reasoning/services/disease_validation.py` | Real-time compliance checking per encounter |
| Audit trail | `clinical_reasoning/services/audit.py` | Records every recommendation for safety monitoring |
| Clinical checks | `clinical_reasoning/services/clinical_checks.py` | Identifies data gaps, overdue patients |
| Follow-up automation | Follow-up module | Schedules and tracks follow-up visits |
| Research platform | Research module | Captures structured data for research output |
| Clinical profile | `clinical_reasoning/models.py` | Stores per-patient AI intelligence |
| Clinical insight | `clinical_reasoning/models.py` | Categorized recommendations for clinician review |

## Appendix B: Clinician Override Reason Codes

| Code | Category | Description |
|------|----------|-------------|
| O01 | Patient preference | Patient requested different approach |
| O02 | Clinical judgment | Clinician assessed patient-specific factors not captured by AI |
| O03 | Drug availability | Recommended drug not available locally |
| O04 | Contraindication | Patient has contraindication not documented in GDES |
| O05 | Cost | Patient cannot afford recommended treatment |
| O06 | Comorbidity | Clinician balancing multiple comorbidities |
| O07 | Guideline update | Clinician following more recent guideline than GDES |
| O08 | AI error | GDES recommendation is clinically inappropriate |
| O09 | Incomplete data | GDES lacking key clinical information |
| O10 | Other | Free-text specification required |

## Appendix C: Usability Rating Scale

Clinicians rate the following after each sampled encounter (1 = Strongly Disagree, 5 = Strongly Agree):

1. GDES outputs were easy to interpret
2. GDES recommendations were clinically relevant
3. GDES improved my confidence in clinical decisions
4. GDES did not disrupt my clinical workflow
5. I would recommend GDES to colleagues
6. I would like to continue using GDES after the pilot

---

*Document prepared for BIRDEM IRB submission. Version 1.0 — July 2026.*
