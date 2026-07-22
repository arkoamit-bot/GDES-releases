# Clinical Validation Library
**Document ID:** GDES-V4.2-CVL-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Clinical Validation

---

## 1. Validation Library Overview

This library provides the gold-standard test suite for the GDES V4.2 clinical reasoning engine. It extends the V4.1 gold-standard cases (8 per disease, 184 total) to a comprehensive 620+ case library with full reasoning chain expectations, enabling automated regression testing of differential diagnosis, treatment selection, monitoring planning, and explainability.

### 1.1 Validation Objectives

| Objective | Metric | Target |
|---|---|---|
| **Diagnostic Accuracy** | Top-1 match | ≥85% |
| **Diagnostic Accuracy** | Top-3 match | ≥95% |
| **Treatment Concordance** | Regimen matches expected | ≥90% |
| **Monitoring Completeness** | All expected parameters included | ≥95% |
| **Urgency Assessment** | Correct urgency tier | ≥90% |
| **Explainability Fidelity** | Reasoning chain steps match | ≥80% |
| **Regression Prevention** | No metric degradation | 100% pass |

### 1.2 Case Categories and Target Distribution

| Category | Target | % | Description |
|---|---|---|---|
| Typical Disease | 200 | 32% | Classic presentations |
| Atypical Disease | 80 | 13% | Variant/non-classic |
| Early Disease | 60 | 10% | Subclinical/early detection |
| Late/Advanced Disease | 60 | 10% | ESRD, severe complications |
| Relapse | 40 | 6% | Recurrence patterns |
| Treatment-Resistant | 30 | 5% | Refractory scenarios |
| Mixed Pathology | 30 | 5% | Overlap syndromes |
| Transplant Cases | 50 | 8% | Post-transplant complexity |
| Rare Diseases | 20 | 3% | Low-prevalence conditions |
| Pediatric | 30 | 5% | Age-specific presentations |
| Pregnancy | 20 | 3% | Pregnancy-specific management |
| **Total** | **620** | **100%** | Expandable to 1000 |

---

## 2. Case Structure Specification

Every validation case MUST conform to this YAML schema. Cases failing schema validation are rejected from the library.

### 2.1 Required Sections

```yaml
# ==========================================
# CASE METADATA
# ==========================================
case_id: "CASE-IGA-TYP-001"           # Format: CASE-{DISEASE_ID}-{CATEGORY}-{NNN}
title: "Classic IgA Nephropathy in Young Adult"
disease_id: "iga"                      # Must match one of 23 disease IDs
presentation_type: "typical"           # typical|atypical|early|advanced|relapse|resistant|mixed|transplant|pediatric|pregnancy|rare
category: "Typical Disease"
version: "1.0"
status: "published"                    # draft|internal_review|clinical_review|approved|published|retired
author: "Dr. Jane Smith, MD"
reviewer: "Dr. John Doe, MD"
review_date: "2026-06-15"
source: "clinic"                       # clinic|literature|synthetic|expert_consensus
is_gold_standard: true
tags: ["iga", "young_adult", "macroscopic_hematuria", "early_disease"]
tags_must_match_disease: true

# ==========================================
# CLINICAL PRESENTATION (INPUT TO ENGINE)
# ==========================================
clinical_presentation:
  demographics:
    age: 24
    sex: "male"
    ethnicity: "European"
    pregnancy_status: "N/A"
  
  history:
    chief_complaint: "Cola-colored urine for 2 days"
    hpi: "24-year-old male presents with sudden onset dark urine 1 day after upper respiratory infection. No flank pain, dysuria, or fever. No prior kidney disease. No family history of kidney disease. No recent medications except ibuprofen 400mg PRN for URI symptoms."
    past_medical_history: []
    medications: ["Ibuprofen 400mg PRN"]
    allergies: "NKDA"
    social_history: "Non-smoker, occasional alcohol"
    family_history: "Father with hypertension"
  
  examination:
    bp: "128/82"
    hr: 78
    temp: 36.8
    weight: 75
    height: 180
    general: "Well-appearing young male"
    cardiovascular: "Regular rate and rhythm, no murmur"
    lungs: "Clear to auscultation bilaterally"
    abdomen: "Soft, non-tender, no CVA tenderness"
    extremities: "No edema"
    skin: "No rash, no palpable purpura"
  
  laboratory_data:
    serum_creatinine: 0.95
    egfr_ckdepi: 105
    bun: 14
    electrolytes: {na: 140, k: 4.2, cl: 102, co2: 24}
    calcium: 9.4
    phosphate: 3.8
    albumin: 4.2
    total_protein: 7.0
    upcr: 0.8
    uacr: 450
    hematuria: "3+ (dysmorphic RBCs 80%, RBC casts 2-3/hpf)"
    serum_iga: 420
    gd_iga1: "elevated"
    c3: 110
    c4: 28
    anca: "negative"
    anti_gbm: "negative"
    ana: "negative"
    ds_dna: "negative"
    hbsag: "negative"
    anti_hcv: "negative"
    hiv: "negative"
    spep: "normal"
    cryoglobulins: "negative"
  
  biopsy_data:
    indication: "Nephrotic-range proteinuria with active sediment"
    light_microscopy: "15 glomeruli, 2 globally sclerotic. Mesangial hypercellularity in 12/13 (M1). No endocapillary hypercellularity (E0). Segmental sclerosis in 1/13 (S1). Tubular atrophy/interstitial fibrosis <25% (T0). No crescents (C0)."
    immunofluorescence: "Mesangial IgA 3+, IgG 1+, C3 2+, C4 trace, kappa/lambda polyclonal. No IgM, no fibrinogen."
    electron_microscopy: "Mesangial electron-dense deposits. Foot process effacement <30%. No subepithelial, subendothelial, or intramembranous deposits. GBM normal thickness."
    diagnosis: "IgA Nephropathy, Oxford MEST-C: M1 E0 S1 T0 C0"
  
  imaging:
    renal_ultrasound: "Normal kidney size and echogenicity. No hydronephrosis."

# ==========================================
# EXPECTED REASONING CHAIN (GOLD STANDARD OUTPUT)
# ==========================================
expected_reasoning_chain:
  - step: 1
    phase: "Syndrome Identification"
    input_features:
      - "macroscopic_hematuria"
      - "post_infectious_timing"
      - "dysmorphic_rbcs"
      - "rbc_casts"
      - "proteinuria_subnephrotic"
    output_syndromes:
      - syndrome_id: "SYND-NT"
        name: "Nephritic Syndrome"
        confidence: 0.95
      - syndrome_id: "SYND-MH"
        name: "Macroscopic Hematuria"
        confidence: 0.92
    reasoning: "Post-URI macroscopic hematuria with dysmorphic RBCs and RBC casts = classic nephritic presentation"
    evidence_citations:
      - "CLINICAL_SYNDROME_LIBRARY.md: SYND-NT diagnostic criteria"
      - "CLINICAL_SYNDROME_LIBRARY.md: SYND-MH diagnostic criteria"
  
  - step: 2
    phase: "Differential Generation"
    input_syndrome: "SYND-NT"
    output_differential:
      - disease_id: "iga"
        score: 0.72
        supporting_evidence:
          - "post_infectious_hematuria"
          - "mesangial_IgA_dominant_IF"
          - "mesangial_deposits_EM"
          - "elevated_serum_IgA"
          - "elevated_Gd-IgA1"
        opposing_evidence:
          - "young_male"
          - "no_hepatic_disease"
          - "no_IBD"
      - disease_id: "antiGbm"
        score: 0.08
        supporting_evidence:
          - "hematuria"
          - "rbc_casts"
        opposing_evidence:
          - "anti_gbm_negative"
          - "no_pulmonary_symptoms"
      - disease_id: "anca"
        score: 0.05
        supporting_evidence:
          - "rbc_casts"
        opposing_evidence:
          - "anca_negative"
          - "no_systemic_vasculitis"
      - disease_id: "lupus"
        score: 0.04
        supporting_evidence:
          - "proteinuria"
        opposing_evidence:
          - "ana_negative"
          - "no_full_house_IF"
          - "male"
          - "no_systemic_features"
      - disease_id: "irgn"
        score: 0.03
        supporting_evidence:
          - "post_infectious_timing"
          - "hematuria"
        opposing_evidence:
          - "c3_normal"
          - "chronicity_on_biopsy"
          - "no_strep_evidence"
      - disease_id: "c3"
        score: 0.02
        supporting_evidence:
          - "mesangial_deposits"
        opposing_evidence:
          - "c3_normal"
          - "IgA_dominant_not_C3"
      - disease_id: "thinBasementMembrane"
        score: 0.03
        supporting_evidence:
          - "hematuria"
          - "young_male"
        opposing_evidence:
          - "proteinuria"
          - "mesangial_hypercellularity"
          - "IgA_deposits"
      - disease_id: "alport"
        score: 0.01
        supporting_evidence:
          - "hematuria"
          - "young_male"
        opposing_evidence:
          - "no_hearing_loss"
          - "no_ocular_abnormalities"
          - "no_family_history"
          - "IgA_deposits"
      - disease_id: "drugInducedGn"
        score: 0.02
        supporting_evidence:
          - "recent_ibuprofen"
        opposing_evidence:
          - "timing_not_consistent"
          - "no_eosinophils"
          - "IgA_dominant"
    confidence: 0.89
  
  - step: 3
    phase: "Evidence Weighting"
    method: "Bayesian updating with likelihood ratios from biopsy findings"
    key_likelihood_ratios:
      - finding: "Mesangial IgA dominant (IF)"
        lr_plus: 45
        diseases_supported: ["iga"]
      - finding: "Mesangial deposits (EM)"
        lr_plus: 38
        diseases_supported: ["iga"]
      - finding: "ANCA negative"
        lr_minus: 0.05
        diseases_opposed: ["anca"]
      - finding: "Anti-GBM negative"
        lr_minus: 0.02
        diseases_opposed: ["antiGbm"]
      - finding: "C3 normal"
        lr_minus: 0.1
        diseases_opposed: ["c3", "lupus", "irgn"]
    final_posteriors:
      iga: 0.94
      antiGbm: 0.01
      anca: 0.01
      lupus: 0.01
      irgn: 0.01
      c3: 0.01
      thinBasementMembrane: 0.01
      alport: 0.005
      drugInducedGn: 0.005
  
  - step: 4
    phase: "Diagnosis Ranking"
    output_ranking:
      - disease_id: "iga"
        probability: 0.94
        classification: "Definite"
      - disease_id: "antiGbm"
        probability: 0.01
        classification: "Excluded"
      - disease_id: "anca"
        probability: 0.01
        classification: "Excluded"
      - disease_id: "lupus"
        probability: 0.01
        classification: "Excluded"
  
  - step: 5
    phase: "Treatment Selection"
    primary_diagnosis: "iga"
    expected_treatment:
      first_line:
        - drug: "Ramipril"
          dose: "5mg daily, titrate to max tolerated"
          rationale: "First-line antiproteinuric, KDIGO 1B"
          monitoring:
            - parameter: "K, Cr"
              timing: "1-2 weeks after initiation, then 3-monthly"
            - parameter: "Blood pressure"
              timing: "Monthly x3, then 3-monthly"
              target: "<130/80"
        - drug: "Losartan"
          alternative: true
          rationale: "Alternative if ACEi intolerant"
      second_line:
        - drug: "Budesonide (Nefecon)"
          dose: "16mg daily x 9 months"
          indication: "High-risk features (proteinuria >1g, MEST-C M1/S1)"
          evidence: "NefIgArd trial, KDIGO 2024 suggestion"
      not_recommended:
        - drug: "Prednisolone"
          reason: "Proteinuria <1g, no crescents - KDIGO suggests against"
        - drug: "Cyclophosphamide"
          reason: "Not indicated without crescentic transformation"
  
  - step: 6
    phase: "Monitoring Plan"
    expected_monitoring:
      - parameter: "UPCR"
        frequency: "3-monthly"
        target: "<0.5 g/g or >50% reduction"
      - parameter: "eGFR"
        frequency: "3-monthly"
        target: "Stable or <3 mL/min/yr decline"
      - parameter: "Blood pressure"
        frequency: "Monthly x3, then 3-monthly"
        target: "<130/80"
      - parameter: "Serum K+, Cr"
        frequency: "1-2 weeks after ACEi start, then 3-monthly"
      - parameter: "Gd-IgA1"
        frequency: "Annual (if available)"
        target: "Trend monitoring"
  
  - step: 7
    phase: "Outcome Prediction"
    expected_outcome:
      prognosis: "Favorable - low-risk MEST-C (M1 E0 S1 T0 C0), proteinuria <1g"
      5yr_esrd_risk: "<5%"
      relapse_risk: "30-40% with URI triggers"
      key_monitoring: "Annual surveillance for progression"

# ==========================================
# VALIDATION CRITERIA (AUTOMATED CHECKS)
# ==========================================
validation_criteria:
  diagnostic_accuracy:
    top_1_match: true
    top_3_match: true
    top_1_disease_id: "iga"
    top_3_disease_ids: ["iga", "antiGbm", "anca", "lupus"]
    min_confidence: 0.85
  
  treatment_concordance:
    first_line_match: true
    first_line_drugs: ["Ramipril", "Losartan"]
    second_line_match: true
    second_line_drugs: ["Budesonide (Nefecon)"]
    not_recommended_match: true
    not_recommended_drugs: ["Prednisolone", "Cyclophosphamide"]
  
  monitoring_completeness:
    required_parameters: ["UPCR", "eGFR", "Blood pressure", "Serum K+", "Serum Cr"]
    frequency_match: true
    targets_match: true
  
  urgency_assessment:
    expected_urgency: "routine"  # routine|urgent|emergent
  
  explainability_fidelity:
    min_reasoning_steps: 5
    required_phases: ["Syndrome Identification", "Differential Generation", "Evidence Weighting", "Diagnosis Ranking", "Treatment Selection"]
    step_order_match: true

# ==========================================
# CLINICAL OUTCOME (FOR RETROSPECTIVE VALIDATION)
# ==========================================
clinical_outcome:
  diagnosis_confirmed: "IgA Nephropathy"
  treatment_given:
    - drug: "Ramipril"
      dose: "5mg daily → 10mg daily"
      duration: "ongoing"
    - drug: "Losartan"
      given: false
    - drug: "Budesonide (Nefecon)"
      given: false
  followup:
    - timepoint: "3 months"
      upcr: 0.3
      egfr: 102
      bp: "122/78"
    - timepoint: "12 months"
      upcr: 0.25
      egfr: 100
      bp: "118/76"
  final_outcome: "Remission - proteinuria <0.5g/g, stable renal function at 2 years"
```

---

## 3. Per-Disease Case Requirements

### 3.1 Case Distribution by Disease

| Disease ID | Typical | Atypical | Early | Late | Relapse | Resistant | Mixed | Transplant | Pediatric | Pregnancy | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| iga | 10 | 4 | 3 | 2 | 2 | 1 | 1 | 2 | 2 | 1 | 28 |
| anca | 10 | 4 | 2 | 3 | 2 | 2 | 2 | 1 | 1 | 1 | 28 |
| antiGbm | 6 | 2 | 1 | 2 | 1 | 1 | 1 | 0 | 1 | 0 | 15 |
| c3 | 8 | 3 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 22 |
| cryoglobulinemic | 6 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 0 | 17 |
| denseDepositDisease | 5 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 15 |
| diabeticNephropathy | 10 | 3 | 2 | 4 | 1 | 1 | 1 | 2 | 1 | 2 | 27 |
| drugInducedGn | 8 | 3 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 0 | 20 |
| fibrillaryGlomerulonephritis | 6 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 17 |
| fsgs | 10 | 4 | 2 | 3 | 2 | 3 | 2 | 2 | 2 | 1 | 31 |
| hivan | 6 | 2 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 16 |
| irgn | 8 | 3 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 0 | 21 |
| lupus | 10 | 4 | 2 | 3 | 2 | 2 | 3 | 2 | 2 | 2 | 32 |
| mcd | 8 | 3 | 3 | 2 | 3 | 2 | 1 | 1 | 3 | 1 | 27 |
| membranous | 10 | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 1 | 1 | 28 |
| mpgn | 8 | 3 | 2 | 2 | 1 | 1 | 2 | 1 | 1 | 0 | 21 |
| thinBasementMembrane | 8 | 3 | 3 | 1 | 1 | 0 | 1 | 1 | 2 | 1 | 21 |
| alport | 6 | 2 | 2 | 2 | 1 | 0 | 1 | 1 | 3 | 0 | 18 |
| antibodyMediatedRejection | 8 | 3 | 2 | 2 | 2 | 2 | 1 | 4 | 1 | 0 | 25 |
| tCellMediatedRejection | 8 | 3 | 2 | 2 | 1 | 1 | 1 | 3 | 1 | 0 | 22 |
| bkVirusNephropathy | 6 | 2 | 1 | 2 | 1 | 1 | 1 | 3 | 0 | 0 | 17 |
| cniToxicity | 6 | 2 | 1 | 2 | 1 | 1 | 1 | 3 | 0 | 0 | 17 |
| transplantGlomerulopathy | 6 | 2 | 1 | 3 | 1 | 1 | 1 | 3 | 0 | 0 | 18 |
| **TOTAL** | **200** | **80** | **60** | **60** | **40** | **30** | **30** | **50** | **30** | **20** | **620** |

### 3.2 Disease-Specific Requirements

Each disease MUST have cases covering:

**IgA Nephropathy (`iga`):**
- Post-infectious macroscopic hematuria (typical)
- Asymptomatic microscopic hematuria + proteinuria (early)
- Nephrotic-range proteinuria with M1/S1 (advanced)
- Crescentic IgAN (rapid)
- Steroid-responsive vs steroid-resistant (relapse/resistant)
- Recurrent macroscopic hematuria (relapse)
- IgAN in pregnancy (pregnancy)
- Pediatric IgAN (pediatric)
- IgAN post-transplant recurrence (transplant)

**ANCA Vasculitis (`anca`):**
- MPO-ANCA GN (typical)
- PR3-ANCA with pulmonary involvement (mixed)
- ANCA-negative pauci-immune GN (atypical)
- RPGN requiring dialysis (advanced)
- Relapse during taper (relapse)
- Refractory to CYC/RTX (resistant)
- Overlap with anti-GBM (mixed)
- Post-transplant recurrence (transplant)
- Pediatric ANCA (pediatric)
- Pregnancy with ANCA (pregnancy)

**Anti-GBM (`antiGbm`):**
- Classic RPGN with pulmonary hemorrhage (typical)
- Renal-limited anti-GBM (atypical)
- Early diagnosis pre-dialysis (early)
- Dialysis-dependent at presentation (late)
- Relapse post-treatment (relapse)
- Refractory to PLEX/CYC (resistant)
- Double-positive anti-GBM/ANCA (mixed)

**C3 Glomerulopathy (`c3`):**
- DDD (typical)
- C3GN (typical)
- Factor H mutation (early/genetic)
- C3NeF positive (typical)
- Post-infectious mimic (atypical)
- Post-transplant recurrence (transplant)
- Pediatric C3G (pediatric)

... [similar detailed requirements for all 23 diseases]

---

## 4. Validation Test Suite

### 4.1 Automated Test Execution

```python
# Pseudocode for validation runner
def run_validation_suite():
    results = []
    for case in load_gold_standard_cases():
        # 1. Feed clinical presentation to engine
        engine_output = clinical_reasoning_engine.evaluate(case.clinical_presentation)
        
        # 2. Compare diagnostic accuracy
        diag_score = score_diagnostic_accuracy(
            engine_output.differential,
            case.expected_reasoning_chain,
            case.validation_criteria.diagnostic_accuracy
        )
        
        # 3. Compare treatment concordance
        tx_score = score_treatment_concordance(
            engine_output.treatment_plan,
            case.expected_reasoning_chain,
            case.validation_criteria.treatment_concordance
        )
        
        # 4. Compare monitoring plan
        mon_score = score_monitoring_completeness(
            engine_output.monitoring_plan,
            case.validation_criteria.monitoring_completeness
        )
        
        # 5. Compare urgency
        urgency_score = score_urgency(
            engine_output.urgency,
            case.validation_criteria.urgency_assessment
        )
        
        # 6. Compare explainability
        explain_score = score_explainability(
            engine_output.reasoning_trace,
            case.expected_reasoning_chain,
            case.validation_criteria.explainability_fidelity
        )
        
        # 7. Aggregate
        case_result = ValidationResult(
            case_id=case.case_id,
            diagnostic_accuracy=diag_score,
            treatment_concordance=tx_score,
            monitoring_completeness=mon_score,
            urgency_assessment=urgency_score,
            explainability_fidelity=explain_score,
            overall_pass=all([
                diag_score >= 0.85,
                tx_score >= 0.90,
                mon_score >= 0.95,
                urgency_score >= 0.90,
                explain_score >= 0.80
            ])
        )
        results.append(case_result)
    
    return ValidationReport(results)
```

### 4.2 Scoring Functions

#### Diagnostic Accuracy Scoring

```python
def score_diagnostic_accuracy(engine_diff, expected_chain, criteria):
    # Extract expected final ranking from step 4
    expected_ranking = expected_chain.step(4).output_ranking
    
    # Check top-1
    top1_match = engine_diff[0].disease_id == criteria.top_1_disease_id
    
    # Check top-3
    top3_ids = [d.disease_id for d in engine_diff[:3]]
    top3_match = all(d in top3_ids for d in criteria.top_3_disease_ids)
    
    # Check confidence
    conf_ok = engine_diff[0].confidence >= criteria.min_confidence
    
    return (top1_match + top3_match + conf_ok) / 3.0
```

#### Treatment Concordance Scoring

```python
def score_treatment_concordance(engine_tx, expected_chain, criteria):
    expected_tx = expected_chain.step(5).expected_treatment
    
    # First-line
    fl_engine = set(engine_tx.first_line.drugs)
    fl_expected = set(criteria.first_line_drugs)
    fl_match = fl_expected.issubset(fl_engine)
    
    # Second-line
    sl_engine = set(engine_tx.second_line.drugs)
    sl_expected = set(criteria.second_line_drugs)
    sl_match = sl_expected.issubset(sl_engine)
    
    # Not recommended
    nr_engine = set(engine_tx.not_recommended.drugs)
    nr_expected = set(criteria.not_recommended_drugs)
    nr_match = nr_expected.issubset(nr_engine)
    
    return (fl_match + sl_match + nr_match) / 3.0
```

#### Monitoring Completeness Scoring

```python
def score_monitoring_completeness(engine_mon, criteria):
    engine_params = {m.parameter: m for m in engine_mon.parameters}
    required = set(criteria.required_parameters)
    
    # All required present
    present = required.issubset(set(engine_params.keys()))
    
    # Frequency match
    freq_ok = all(
        engine_params[p].frequency == criteria.required_frequency[p]
        for p in required
    )
    
    # Targets match
    targets_ok = all(
        engine_params[p].target == criteria.required_targets[p]
        for p in required
    )
    
    return (present + freq_ok + targets_ok) / 3.0
```

#### Explainability Fidelity Scoring

```python
def score_explainability(engine_trace, expected_chain, criteria):
    # Check step count
    step_count_ok = len(engine_trace) >= criteria.min_reasoning_steps
    
    # Check phase names
    engine_phases = [s.phase for s in engine_trace]
    required_phases = set(criteria.required_phases)
    phases_ok = required_phases.issubset(set(engine_phases))
    
    # Check order
    expected_order = [s.phase for s in expected_chain.steps]
    order_ok = engine_phases == expected_order
    
    # Check evidence citations (at least one per step)
    citations_ok = all(len(s.evidence_citations) > 0 for s in engine_trace)
    
    return (step_count_ok + phases_ok + order_ok + citations_ok) / 4.0
```

---

## 5. Regression Testing Framework

### 5.1 Test Execution Pipeline

```yaml
# .github/workflows/validation.yml
name: Clinical Validation Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 0'  # Weekly Sunday 2 AM
  workflow_dispatch:

jobs:
  validation:
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements-validation.txt
      
      - name: Load gold standard cases
        run: python -m validation.load_cases
      
      - name: Run validation suite
        run: python -m validation.run_suite --output validation_report.json
      
      - name: Check regression
        run: python -m validation.check_regression validation_report.json
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: validation-report
          path: validation_report.json
      
      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('validation_report.json'));
            const body = `## Clinical Validation Results\n
            **Overall:** ${report.overall_pass ? '✅ PASS' : '❌ FAIL'}\n
            **Cases Tested:** ${report.total_cases}\n
            **Passed:** ${report.passed}\n
            **Failed:** ${report.failed}\n
            **Diagnostic Accuracy:** ${report.metrics.diagnostic_accuracy:.1%}\n
            **Treatment Concordance:** ${report.metrics.treatment_concordance:.1%}\n
            **Monitoring Completeness:** ${report.metrics.monitoring_completeness:.1%}\n
            **Urgency Assessment:** ${report.metrics.urgency_assessment:.1%}\n
            **Explainability:** ${report.metrics.explainability_fidelity:.1%}\n`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });
```

### 5.2 Regression Detection

```python
def check_regression(current_report, baseline_report):
    """Fail if any metric drops >2% from baseline"""
    metrics = [
        'diagnostic_accuracy',
        'treatment_concordance', 
        'monitoring_completeness',
        'urgency_assessment',
        'explainability_fidelity'
    ]
    
    regressions = []
    for m in metrics:
        current = current_report.metrics[m]
        baseline = baseline_report.metrics[m]
        drop = baseline - current
        if drop > 0.02:  # 2% threshold
            regressions.append({
                'metric': m,
                'baseline': baseline,
                'current': current,
                'drop': drop
            })
    
    if regressions:
        raise RegressionError(f"Regression detected: {regressions}")
    
    return True
```

### 5.3 Metrics Dashboard

| Metric | Current | Baseline | Delta | Status |
|---|---|---|---|---|
| Diagnostic Accuracy (Top-1) | 87% | 85% | +2% | ✅ |
| Diagnostic Accuracy (Top-3) | 96% | 95% | +1% | ✅ |
| Treatment Concordance | 92% | 91% | +1% | ✅ |
| Monitoring Completeness | 97% | 96% | +1% | ✅ |
| Urgency Assessment | 93% | 92% | +1% | ✅ |
| Explainability Fidelity | 84% | 82% | +2% | ✅ |
| **Overall Pass Rate** | **91%** | **89%** | **+2%** | **✅** |

---

## 6. Case Library Management

### 6.1 Case Lifecycle

```
DRAFT → EXPERT_REVIEW → CLINICAL_REVIEW → APPROVED → PUBLISHED → RETIRED
                ↓              ↓
            REVISED        REVISED
```

### 6.2 Quality Gates for Publication

| Gate | Requirement |
|---|---|
| **Schema Validation** | Must pass YAML schema validation |
| **Expert Review** | At least 1 nephrology expert reviewer |
| **Clinical Review** | At least 1 board-certified nephrologist |
| **De-identification** | All PHI removed (HIPAA Safe Harbor) |
| **Gold Standard Flag** | Must have `is_gold_standard: true` for regression suite |
| **Version Assignment** | Semantic version assigned |
| **Changelog Entry** | Document what changed from previous version |

### 6.3 Case Metadata Index

Searchable index fields:
- `case_id`, `disease_id`, `presentation_type`, `category`
- `age_range`, `sex`, `ethnicity`, `pregnancy_status`
- `key_findings` (e.g., "crescents", "nephrotic_range", "ANCA_positive")
- `tags`
- `source`, `author`, `reviewer`, `review_date`

---

## 7. Expansion Roadmap

### 7.1 Phase 1: Core 620 Cases (Current)

- All 23 diseases covered per distribution table
- All 10 categories represented
- Full reasoning chain for each

### 7.2 Phase 2: 1000 Cases (Months 6-12)

| Expansion Area | Additional Cases | Rationale |
|---|---|---|
| Geographic/ethnic variation | +100 | APOL1, Asian IgAN, African FSGS |
| Rare presentations | +80 | Anti-GBM relapse, DDD in transplant |
| Multi-morbidity | +80 | CKD + heart failure + diabetes |
| Pediatric subspecialty | +40 | Congenital, hereditary |
| Pregnancy complexity | +30 | Lupus flare, TMA, preeclampsia overlap |
| Transplant nuances | +50 | BK + rejection, DSA + CNI toxicity |

### 7.3 Phase 3: Continuous Expansion (Ongoing)

- Monthly literature surveillance for new case reports
- Quarterly expert panel for emerging patterns
- Annual external validation against real-world cohorts

---

## 8. API for External Validation

### 8.1 Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/validation/cases` | GET | List all gold-standard cases (paginated) |
| `/validation/cases/{case_id}` | GET | Full case details |
| `/validation/cases/{case_id}/run` | POST | Execute case against engine |
| `/validation/report/latest` | GET | Latest validation report |
| `/validation/report/{run_id}` | GET | Specific run report |
| `/validation/metrics` | GET | Current metric values |

### 8.2 Integration Example

```python
# External system validating their engine
import requests

cases = requests.get("https://gdes.example.com/validation/cases").json()

results = []
for case in cases:
    if case['disease_id'] == 'iga' and case['presentation_type'] == 'typical':
        # Feed to external engine
        engine_output = external_engine.evaluate(case['clinical_presentation'])
        
        # Score locally using GDES criteria
        score = score_case(engine_output, case)
        results.append({
            'case_id': case['case_id'],
            'score': score,
            'pass': score >= 0.80
        })

print(f"External engine pass rate: {sum(r['pass'] for r in results)/len(results):.1%}")
```

---

## 9. Governance

### 9.1 Case Authorship Standards

- **Lead Author:** Must be board-certified nephrologist
- **Co-Authors:** May include fellows, pharmacists, pathologists
- **Reviewer:** Independent nephrologist not involved in authoring
- **COI:** All authors must declare COI per governance framework

### 9.2 Review Criteria

| Criterion | Weight |
|---|---|
| Clinical accuracy | 30% |
| Reasoning chain completeness | 25% |
| Evidence citation quality | 15% |
| Guideline alignment | 15% |
| De-identification completeness | 10% |
| Schema compliance | 5% |

### 9.3 Retirement Policy

Cases are retired when:
- Clinical practice has fundamentally changed (e.g., new first-line therapy)
- Case no longer represents current standard of care
- Better replacement case exists
- Retired cases remain in archive with clear "RETIRED" flag

---

## 10. Appendices

### Appendix A: Full Case Catalog (Sample)

| Case ID | Disease | Category | Key Features |
|---|---|---|---|
| CASE-IGA-TYP-001 | iga | Typical | Post-URI macroscopic hematuria, M1E0S1T0C0 |
| CASE-IGA-ATY-001 | iga | Atypical | Elderly, no hematuria, proteinuria dominant |
| CASE-IGA-EAR-001 | iga | Early | Incidental microscopic hematuria, proteinuria <0.5g |
| CASE-IGA-ADV-001 | iga | Advanced | Nephrotic syndrome, M1E1S1T1C1 |
| CASE-IGA-RAP-001 | iga | Rapid | Crescentic IgAN, >50% crescents, RPGN |
| CASE-IGA-REL-001 | iga | Relapse | Recurrent macroscopic hematuria post-URI |
| CASE-IGA-RES-001 | iga | Resistant | Proteinuria >3g despite max ACEi/ARB + SGLT2i |
| CASE-IGA-MIX-001 | iga | Mixed | IgAN + ANCA overlap |
| CASE-IGA-TXR-001 | iga | Transplant | Recurrent IgAN in allograft at 3 years |
| CASE-IGA-PED-001 | iga | Pediatric | 12yo boy, macroscopic hematuria, M0E0S0T0C0 |
| CASE-IGA-PREG-001 | iga | Pregnancy | 28yo pregnant, proteinuria 1.5g, bp 140/90 |

[... 610 more cases ...]

### Appendix B: Validation Report Template

```markdown
# Validation Report - {timestamp}

## Executive Summary
- **Engine Version:** {engine_version}
- **Cases Tested:** {total_cases}
- **Overall Pass Rate:** {pass_rate:.1%}
- **Status:** {PASS/FAIL}

## Domain Results
| Metric | Target | Achieved | Status |
|---|---|---|---|
| Diagnostic Accuracy (Top-1) | ≥85% | {diag_acc:.1%} | {PASS/FAIL} |
| Diagnostic Accuracy (Top-3) | ≥95% | {diag_acc3:.1%} | {PASS/FAIL} |
| Treatment Concordance | ≥90% | {tx_concord:.1%} | {PASS/FAIL} |
| Monitoring Completeness | ≥95% | {mon_complete:.1%} | {PASS/FAIL} |
| Urgency Assessment | ≥90% | {urgency:.1%} | {PASS/FAIL} |
| Explainability Fidelity | ≥80% | {explain:.1%} | {PASS/FAIL} |

## Failed Cases
| Case ID | Disease | Failure Domain | Details |
|---|---|---|---|
| ... | ... | ... | ... |

## Regression Check
- **Baseline Run:** {baseline_run_id}
- **Current Run:** {current_run_id}
- **Regressions Detected:** {count}
- **Details:** {regression_details}

## Recommendations
1. ...
2. ...
```

---

## 11. Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Validation Lead | | | |
| Clinical Director | | | |
| Chief Medical Informatics Officer | | | |

---

**End of Document**  
**Next Review:** 2026-10-10  
**Governance Lead:** Clinical Validation Team