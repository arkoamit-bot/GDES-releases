# GDES Pilot Workflow Optimization

**Version:** 7.0  
**Date:** 2026-07-11

## 1. Current UI Assessment

### Tab Structure (12 tabs)
1. **Overview** — Key vitals, demographics, reasoning summary, follow-up tasks, eGFR/proteinuria chart
2. **Clinical Reasoning** — Differential diagnosis, risk assessment, information gaps, care pathway, treatment recommendations, care gaps
3. **CDS Plans** — Management plan (first/second/rescue), monitoring protocol, follow-up schedule
4. **Traceability** — Recommendation audit trail with governance metadata (NEW in V7)
5. **Visits** — Follow-up visits, relapses, admissions
6. **Prescriptions** — Prescription history
7. **Labs** — Lab results pivoted date x test
8. **Safety** — Adverse events
9. **Biopsies** — Biopsy records
10. **Research** — Study enrollments, drug exposures, monitoring plans
11. **Consent** — Consent status cards
12. **Audit Log** — Audit trail

### Click Analysis
| Action | Path | Clicks |
|--------|------|--------|
| View recommendation | Patient list > Patient detail > Clinical Reasoning tab | 2 |
| View management plan | Patient list > Patient detail > CDS Plans tab | 2 |
| View traceability | Patient list > Patient detail > Traceability tab | 2 |
| Override recommendation | Patient list > Patient detail > Traceability tab > Override > Confirm | 4 |

### Navigation Assessment
- Patient list search is HTMX-powered (live search)
- Tab switching is client-side JavaScript (instant)
- No page reloads for tab switching

## 2. Optimization Recommendations

### Keep As-Is (Already Optimal)
- Patient list live search
- Tab-based navigation (no page reloads)
- Overview tab with key vitals and chart
- Clinical Reasoning tab with differential and risk

### Simplify
- Merge **Biopsies** into **Labs** tab (12 > 11 tabs)
- Merge **Consent** into **Research** tab (11 > 10 tabs)

### Enhance
- Add **Quick Actions** bar to Overview tab (New Visit, New Lab, New Prescription)
- Add badge counts to all tabs (currently only Visits, Prescriptions, Traceability have counts)
- Add **Last updated** timestamp to Clinical Reasoning and CDS Plans tabs

### Data Entry
- Auto-populate common fields from previous encounters
- Lab entry form with disease-specific default panels
- One-click **Run Reasoning** button on patient detail

## 3. Response Time Assessment

| Operation | Target |
|-----------|--------|
| SQLite patient detail query | <100ms |
| Clinical reasoning engine | <500ms/patient |
| Management plan generation | <200ms |
| Monitoring plan generation | <200ms |
| Follow-up schedule generation | <200ms |
| Investigation recommendations | <200ms |

## 4. Pilot Recommendations

1. Keep **10 tabs** (after merging Biopsies+Labs, Consent+Research)
2. Add **Quick Actions** bar to Overview
3. Add **badge counts** to all tabs
4. Auto-populate lab panels from disease profile
