# Clinical Usability Review
## GDES Version 5.0 — Workstream 9

**Date:** 2026-07-11
**Reviewers:** GDES Review Team (Nephrologist, Pathologist, Clinical Pharmacologist, Health Informatics Specialist)

---

## Review Methodology

The system was evaluated from the perspective of a practicing nephrologist performing routine clinical tasks: patient registration, follow-up visit, biopsy entry, prescription, and research query.

---

## 1. Data Entry Intuition

| Aspect | Rating | Finding |
|--------|--------|---------|
| Patient registration | ✅ Good | 2-step wizard, live duplicate check, auto-ID generation |
| Baseline assessment | ✅ Good | 5 organized fieldsets (A-E), logical progression from history → exam → labs |
| Follow-up visit | ✅ Good | Carry-forward from previous visit. Previous labs displayed. Auto-phase advancement. |
| Biopsy form | ✅ Good | Composite form with conditional score blocks (only relevant scores shown based on diagnosis) |
| Prescription form | ⚠️ Moderate | 12-row medication grid is complex. Drug picker grouped by class is helpful but the form has 459 lines of JS — risk of browser performance issues on older machines. |
| Lab results | ✅ Good | Creatinine → auto-eGFR, serology with paired numeric+qualitative fields |
| Adverse event | ✅ Good | Auto-flag SAE on hospitalization or Grade ≥4 |
| **Overall** | **4.5/5** — Forms are well-organized, use carry-forward, and show conditional logic. Prescription form is the most complex. |

---

## 2. Follow-up Visit Efficiency

| Aspect | Rating | Finding |
|--------|--------|---------|
| Retrieve patient | ✅ Fast | Quick-jump search in top bar, HTMX live patient list |
| View previous data | ✅ Good | Carry-forward banner shows last visit + last labs |
| Enter new data | ✅ Good | Compact form with pre-filled carry-forward values |
| See recommendations | ❌ Missing | No CDS output displayed during follow-up visit. Clinician must leave the visit flow to see differential, risk, or treatment recommendations. |
| Complete visit | ✅ Good | Auto-advances disease phase state machine |
| **Overall** | **3.5/5** — Visit entry is efficient BUT clinical decision support is invisible during the visit. |

---

## 3. Recommendation Clarity

| Aspect | Rating | Finding |
|--------|--------|---------|
| Differential diagnosis | ❌ Hidden | Available via `/api/v1/profiles/<id>/` or quality page. Not on patient hub. |
| Treatment recommendation | ❌ Hidden | Graph-derived treatment stored in care_pathway but not displayed. |
| Risk assessment | ❌ Hidden | Progression/relapse/kidney survival scores in ClinicalProfile but not in UI. |
| Information gaps | ❌ Hidden | Missing data that would improve confidence — not shown to clinician. |
| Drug safety warnings | ✅ Good | Duplicate-class and renal-dose warnings in prescription form. |
| **Overall** | **2/5** — Critical clinical decision support data is computed but invisible. This is the single biggest usability gap. |

---

## 4. Alert Visibility

| Aspect | Rating | Finding |
|--------|--------|---------|
| Dashboard alerts | ✅ Good | Worklist shows due/overdue visits, stats cards show registry metrics |
| Drug safety alerts | ✅ Good | Inline warnings in prescription form for duplicate class + renal dose |
| Critical lab alerts | ✅ Good | Trend alerts (eGFR rapid decline, creatinine spike) logged and displayed |
| Missed visit alerts | ✅ Good | Dashboard worklist shows overdue patients with red badge |
| Relapse alerts | ❌ Missing | Computed (via trajectory analysis) but not shown to clinician |
| Research opportunity alerts | ❌ Missing | Computed (via protocol matching) but not shown |
| Data quality alerts | ❌ Missing | Computed (via quality page) but not proactively shown |
| **Overall** | **3/5** — Operational alerts (visits, labs) work well. Clinical alerts (relapse, research, quality) are computed but not surfaced. |

---

## 5. Click Efficiency

| Aspect | Rating | Finding |
|--------|--------|---------|
| Navigation depth to patient hub | ✅ 2 clicks | Dashboard → Patient list → Patient hub (or Quick-jump → Patient hub) |
| Navigation depth to new visit | ✅ 3 clicks | Patient hub → Follow-up tab → "New Visit" |
| Navigation depth to prescription | ✅ 3 clicks | Patient hub → Treatment tab → "New Prescription" |
| Navigation depth to research | ✅ 2 clicks | Sidebar → Research → Analytics |
| Unnecessary clicking | ⚠️ Moderate | Quality page requires manual navigation; several clicks to see clinical reasoning output |
| Carry-forward | ✅ Good | Visit form pre-fills from previous visit |
| **Overall** | **4/5** — Navigation is efficient. Main pain point is accessing CDS output. |

---

## 6. Clinical Workflow Fidelity

| Workflow Step | System Match | Finding |
|--------------|-------------|---------|
| Patient Presentation | ✅ Good | Registration → Baseline captures presentation data |
| Clinical Assessment | ✅ Good | Baseline + Follow-up forms match clinical workflow |
| Investigations | ✅ Good | Lab ordering + results entry |
| Differential Diagnosis | ❌ Disconnected | System computes differential but does not present it in the clinical workflow |
| Kidney Biopsy | ✅ Good | Composite form matches real workflow (diagnosis → scores) |
| Final Diagnosis | ✅ Good | Biopsy-driven auto-registration |
| Treatment | ✅ Good | Prescription form with drug safety |
| Monitoring | ⚠️ Partial | Monitoring plans computed but not executed |
| Follow-up | ✅ Good | Visit form with carry-forward + phase advancement |
| Outcome | ✅ Good | Automated outcome computation |
| **Overall** | **4/5** — The workflow mirrors clinical practice well. The main disconnect is the invisible differential/Tx recommendation step. |

---

## 7. Pain Points Identified

### Critical (Must Fix Before V1.0)

| # | Pain Point | Location | Impact |
|---|-----------|----------|--------|
| 1 | Clinical decision support (differential, risk, treatment recs) not visible on patient hub | `patient_detail.html` Overview tab | CDS invisible to clinicians |
| 2 | Follow-up interval computed but not auto-scheduled | `care_pathway.py` → no execution | Manual scheduling only |
| 3 | Monitoring plans from graph not executed as lab orders/visits | `graph_reasoning.py` → no execution | Monitoring gaps |

### Moderate (Should Fix)

| # | Pain Point | Location | Impact |
|---|-----------|----------|--------|
| 4 | Drug-drug interactions not checked at prescription time | `prescription_form.html` | Safety gap |
| 5 | Quality/recommendation data requires 3+ clicks to find | `/clinic/quality/` | Poor discoverability |
| 6 | Prescription form JS-heavy (459 lines) | `prescription_form.html` | Potential performance issues |

### Minor (Nice to Fix)

| # | Pain Point | Location | Impact |
|---|-----------|----------|--------|
| 7 | No quick "Recompute profile" button on patient hub | `patient_detail.html` | Must wait for event trigger |
| 8 | Lab results entry could auto-generate follow-up interval | `lab_results_form.html` | Missed automation opportunity |

---

## 8. Recommendations

### High Priority

1. **Add a "Clinical Reasoning" section to the patient hub Overview tab** — show top 3 differential diagnoses, risk summary, treatment recommendations, and information gaps. Consume the existing `ClinicalProfile` API or create an HTMX partial.

2. **Surface monitoring plans in the prescription flow** — when a drug is selected, show its monitoring protocol requirements inline (e.g., "This drug requires monthly eGFR and quarterly CBC"). Use the existing graph traversal output.

3. **Add drug interaction warnings** — query `DrugIntelligence.drug_interactions` when a new drug is added to a regimen and show an inline warning.

### Medium Priority

4. **Add a "Reasoning" button to the patient hub** — one-click access to the full reasoning chain, evidence summary, and information gaps.

5. **Add proactive alert badges** to the sidebar for: patients with suspected relapse, patients matching trial protocols, patients with critical data gaps.

### Low Priority

6. **Add "Recompute profile" button** to the patient hub (in addition to the automatic event-driven recomputation).

---

## Usability Score Summary

| Dimension | Score (1-5) |
|-----------|-------------|
| Data entry intuition | 4.5 |
| Follow-up visit efficiency | 3.5 |
| Recommendation clarity | 2.0 |
| Alert visibility | 3.0 |
| Click efficiency | 4.0 |
| Workflow fidelity | 4.0 |
| **Overall** | **3.5/5** |

**The system is usable for data entry and follow-up, but its clinical decision support output is effectively invisible to the end user.** Fixing this (surfacing CDS on the patient hub) is the single highest-impact usability improvement before V1.0.
