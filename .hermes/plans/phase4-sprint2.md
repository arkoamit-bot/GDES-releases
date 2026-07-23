# Phase 4, Sprint 2: Strengthen Clinical Reasoning

## Overview
Enhance the clinical reasoning engine with disease-specific care gaps, care pathway stages, and improved explainability with guideline references.

## Focus Areas

### 1. Disease-Specific Care Gaps (care_pathway.py)

**Current:** `detect_care_gaps()` only checks generic monitoring gaps, follow-up, and core investigations.

**Add:** New helper function `_check_disease_specific_gaps(patient, features, primary_disease)` that returns disease-specific gaps:
- **IgA Nephropathy**: "Consider tonsillectomy if recurrent tonsillitis", "Screen for hematuria flares"
- **Membranous**: "Monitor PLA2R antibody titers every 3 months", "Screen for thromboembolism"
- **Lupus Nephritis**: "Monitor complement C3/C4 levels", "Screen for extra-renal lupus activity"
- **ANCA Vasculitis**: "Monitor ANCA titers", "Check for ENT involvement"
- **Diabetic Nephropathy**: "Optimize glycemic control (HbA1c target <7%)", "Annual foot exam"
- **FSGS**: "Assess for genetic causes if family history", "Monitor for nephrotic syndrome complications"
- **MCD**: "Taper steroids slowly", "Monitor for relapse"
- **C3 Glomerulopathy**: "Monitor complement levels", "Screen for acquired partial lipodystrophy"

### 2. Care Pathway Stages (care_pathway_engine.py)

**Current:** `PathwayStage` dataclass is defined but no stages are registered.

**Add:** Define actual pathway stages for common glomerular diseases:
- `PATHWAY_STAGES` dict with stages per disease: "diagnosis", "induction", "maintenance", "relapse", "remission", "ckd_progression", "esrd"
- `get_pathway_stages(disease_id)` function returning disease-specific stages
- `determine_current_stage(patient, features, disease_id)` function

### 3. Enhanced Explainability (explainability.py)

**Improve:** `_extract_guideline_support()` should include:
- Year of guideline reference
- Confidence level of recommendation (1A, 1B, 2C, etc.)
- Link to more detailed guidance
- For rejected alternatives, mention why they were excluded

### 4. Guideline Reference Updates

Review `_extract_guideline_support()` and ensure all disease entries have KDIGO 2021/2024 references.

## Files to Modify
- `clinical_reasoning/services/care_pathway.py`
- `clinical_reasoning/services/care_pathway_engine.py`
- `clinical_reasoning/services/explainability.py`
- `clinical_reasoning/tests/test_services.py` (add tests)

## Acceptance Criteria
- [ ] `detect_care_gaps()` returns disease-specific gaps for at least 8 diseases
- [ ] `get_pathway_stages()` returns defined stages for at least 5 diseases
- [ ] `determine_current_stage()` accurately maps patient data to a stage
- [ ] Explainability output includes guideline year and evidence grade
- [ ] All existing tests pass
- [ ] Ruff lint passes

## Quality Gates
- `python -m pytest clinical_reasoning/tests/ --tb=short -q`
- `python -m ruff check clinical_reasoning/`
