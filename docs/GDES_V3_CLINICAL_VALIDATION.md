# GDES V3 Clinical Validation

## Purpose
Validate all 10 disease workflows against 7 guideline sources to ensure clinical correctness and trustworthiness.

## Disease Workflows
| # | Disease | Guidelines | Status |
|---|---|---|---|
| 1 | Lupus Nephritis (LN) | KDIGO 2024, EULAR/ERA-EDTA | ✅ Validated |
| 2 | IgA Nephropathy (IgAN) | KDIGO 2024 | ✅ Validated |
| 3 | Membranous Nephropathy (MN) | KDIGO 2024 | ✅ Validated |
| 4 | ANCA Vasculitis/GN | KDIGO 2024 | ✅ Validated |
| 5 | FSGS | KDIGO 2024 | ✅ Validated |
| 6 | Minimal Change Disease | KDIGO 2024 | ✅ Validated |
| 7 | Diabetic Kidney Disease | KDIGO 2024, ADA Standards | ✅ Validated |
| 8 | C3 Glomerulopathy | KDIGO 2024 | ✅ Validated |
| 9 | Infection-Related GN | ISN/ASN Guidelines | ✅ Validated |
| 10 | Thrombotic Microangiopathy | KDIGO 2024, ASH | ✅ Validated |

## Validation Protocol
1. **Rule coverage**: Every KnowledgeBaseEntry for a disease is reviewed against current guidelines
2. **Scoring accuracy**: Rule scores produce correct differential rankings
3. **Care gap detection**: All clinically relevant gaps are identified
4. **Milestone accuracy**: Disease milestones fire at the correct clinical thresholds
5. **Pathway transitions**: Stage transitions follow clinically valid paths

## Evidence Grading
- `1a` — Systematic review of RCTs
- `1b` — Individual RCT
- `2a` — Systematic review of cohort studies
- `2b` — Individual cohort study
- `3` — Case-control studies
- `4` — Case series
- `5` — Expert opinion without explicit critical appraisal
- `NG` — Not graded

## Test Coverage
```bash
pytest tests/test_clinical_validation.py -v --co
```
