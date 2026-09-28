# IgA Nephropathy / IgA Vasculitis Nephritis — Clinical Pathway Specification
**Document ID:** IGA-CP-v1.0
**Date:** 2026-07-10
**Version:** 1.0
**Status:** Final
**Domain:** Clinical Pathways
---
## 1. Document Purpose
6-stage clinical pathway for IgA nephropathy management.
---
## 2. Pathway Overview
```
STAGE 1: Presentation & Diagnosis (30d) -> STAGE 2: Risk Stratification (90d) -> STAGE 3: Supportive Therapy (90d) -> STAGE 4: Immunosuppression (180d) -> STAGE 5: Long-term Monitoring (365d) -> STAGE 6: ESKD / Transplantation (365d)
```
## 01. Presentation & Diagnosis
**Duration:** 30 days
**Goal:** Initial clinical presentation of IgA Nephropathy. Includes evaluation of hematuria (microscopic or macroscopic), proteinuria quantification, renal function assessment, and decision for kidney biopsy.
### Actions
**Next stages:** iga_risk_stratification
**Criteria to proceed:** ['Biopsy-confirmed dominant/co-dominant IgA deposition with MEST-C score reported', 'Complete lab panel including eGFR, proteinuria, albumin, BP', 'Exclusion of secondary causes (lupus, HSP, liver disease, HIV)']
## 02. Risk Stratification
**Duration:** 90 days
**Goal:** Structured risk assessment using clinical, laboratory, and histologic parameters to guide treatment decisions. Apply International IgAN Prediction Tool.
### Actions
**Next stages:** iga_supportive_therapy, iga_immunosuppression
**Criteria to proceed:** ['Minimum 3 months optimized RAASi therapy completed', 'Proteinuria reassessed after RAASi optimization', 'MEST-C score available and incorporated into risk model']
## 03. Supportive Therapy
**Duration:** 90 days
**Goal:** Optimized supportive care foundation for all IgA Nephropathy patients regardless of risk category. This is the cornerstone of management and must be optimized BEFORE considering immunosuppression.
### Actions
**Next stages:** iga_risk_reassessment, iga_immunosuppression
**Criteria to proceed:** ['RAASi at stable maximally tolerated dose for minimum 3 months', 'SGLT2i initiated if eligible', 'BP at or near target', 'Dietary and lifestyle counseling provided and documented']
## 04. Immunosuppression
**Duration:** 180 days
**Goal:** Immunosuppressive therapy for high-risk IgA Nephropathy patients with persistent proteinuria >1 g/day despite optimized supportive care, or rapidly progressive disease.
### Actions
**Next stages:** iga_monitoring
**Criteria to proceed:** ['High-risk categorization confirmed after optimized supportive therapy', 'Contraindications to immunosuppression excluded (active infection, uncontrolled diabetes, severe osteoporosis, recent malignancy)', 'Informed consent obtained discussing risks/benefits']
## 05. Long-term Monitoring
**Duration:** 365 days
**Goal:** Structured follow-up with regular assessment of disease activity, treatment response, and complications. Frequency determined by risk category.
### Actions
**Next stages:** iga_eskd_transplant
**Criteria to proceed:** ['Stable or improving disease trajectory', 'Treatment response assessed: proteinuria reduction >50% is favorable', 'If progressive despite therapy, refer for advanced CKD management']
## 06. ESKD / Transplantation
**Duration:** 365 days
**Goal:** Management of end-stage kidney disease from IgA Nephropathy, including RRT planning, transplant evaluation, and management of post-transplant recurrence.
### Actions
**Next stages:** N/A (final stage)
**Criteria to proceed:** ['eGFR persistently <20 mL/min or symptomatic ESKD', 'Transplant workup completed', 'Patient educated about recurrence risk and RRT options']
---