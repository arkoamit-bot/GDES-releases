# GDES User Experience Review — Design Document

**Version:** 7.1  
**Date:** 2026-07-12  
**Status:** Draft  
**Author:** GDES Clinical Informatics Team

---

## 1. Purpose

This document defines the structured methodology for evaluating the user experience of the Glomerular Disease Expert System (GDES) as it transitions from software engineering to clinical deployment. The UX review will identify usability barriers, quantify workflow efficiency, and produce an evidence-based improvement roadmap for the pilot at BIRDEM Hospital.

## 2. Objectives

1. **Establish baseline usability** before clinician pilot deployment using validated instruments (SUS).
2. **Identify workflow friction** in core clinical tasks — patient registration, encounter entry, AI recommendation review, investigation ordering, follow-up planning, patient history access, and report generation.
3. **Quantify interaction cost** per task (time, clicks, errors, cognitive load) across clinician roles (nephrologist, coordinator, data manager).
4. **Measure recommendation clarity** and clinician trust in AI-generated clinical reasoning outputs.
5. **Detect early patterns of alert fatigue** and override behaviour that inform the continuous knowledge improvement cycle.
6. **Produce prioritised improvement recommendations** with an impact-vs-effort classification.

## 3. Evaluation Domains

| Domain | Description | Key Indicators |
|--------|-------------|----------------|
| Navigation efficiency | Time to locate key functions from the sidebar, tab system, and global search | Time-to-target, mis-navigation count |
| Click count per task | Number of interactions required to complete each defined clinical task | Clicks, scroll depth |
| Data entry burden | Effort required for structured clinical data capture (baseline, labs, treatment forms) | Fields per form, validation error rate, time per field |
| Recommendation clarity | Clinician comprehension of AI recommendations, rationale, and evidence | Self-reported clarity (1–5), comprehension quiz accuracy |
| Traceability usability | Ease of tracing a recommendation back to KB rules, guideline sources, and evidence | Time to trace, confidence in traceability (1–5) |
| Alert fatigue | Frequency and relevance of clinical alerts (drug toxicity, treatment failure, safety) | Alert-to-action ratio, alert dismissal rate |
| Training requirements | Time and support needed for new users to become proficient | Time-to-competency, support tickets |

## 4. Task Definitions

The following seven tasks represent the core clinical workflows to evaluate. Each task has defined start and end points, expected artefacts, and success criteria.

### 4.1 Patient Registration
- **Start:** User navigates to patient creation form.
- **Steps:** Complete demographics, baseline clinical data, consent form, duplicate check.
- **End:** Patient record created with valid `patient_id` (e.g., BGD-00001).
- **Success:** Record saved, duplicate check passed, patient visible in worklist.

### 4.2 Clinical Encounter Entry
- **Start:** User opens an existing patient record and selects "Add Visit" or equivalent.
- **Steps:** Enter clinical encounter data (vitals, symptoms, clinical notes, examination findings).
- **End:** Encounter saved, clinical profile updated.
- **Success:** Encounter recorded, `ClinicalProfile.last_updated` refreshed.

### 4.3 AI Recommendation Review
- **Start:** User opens the clinical reasoning panel for a patient.
- **Steps:** Review differential diagnosis, treatment recommendations, evidence grades, and reasoning chain.
- **End:** User acknowledges or overrides at least one recommendation.
- **Success:** Recommendation understood (clarity score ≥ 4), override reason captured if applicable.

### 4.4 Investigation Ordering
- **Start:** User identifies a recommended investigation (e.g., renal biopsy, lab panel).
- **Steps:** Select investigation, confirm indication, review prior results.
- **End:** Investigation ordered or deferral documented.
- **Success:** Investigation linked to recommendation, order saved.

### 4.5 Follow-Up Plan Review
- **Start:** User accesses the follow-up scheduling view for a patient.
- **Steps:** Review AI-suggested follow-up schedule, adjust timing, confirm next visit.
- **End:** Follow-up schedule saved.
- **Success:** Next visit date recorded, follow-up reminders configured.

### 4.6 Patient History Access
- **Start:** User opens a patient record from the worklist or search.
- **Steps:** Navigate through tabs (baseline, labs, pathology, treatment, timeline, clinical reasoning).
- **End:** User locates a specific historical data point (e.g., last eGFR, biopsy date).
- **Success:** Data located in ≤ 3 tab switches, time-to-data < 15 seconds.

### 4.7 Report Generation
- **Start:** User navigates to the export/analytics view.
- **Steps:** Select cohort filters, choose output format, generate report.
- **End:** Report downloaded or displayed.
- **Success:** Report contains complete data for selected cohort, generation time < 30 seconds.

## 5. Methodology

### 5.1 Structured Observation
A trained observer accompanies the clinician during live clinical sessions, recording:
- Task completion sequences
- Navigation paths (sidebar → tab → form → save)
- Hesitation points (pauses > 3 seconds, repeated clicks, back-navigation)
- Verbalised frustrations

### 5.2 Task Analysis
For each defined task, record:
- Total time from task start to completion
- Number of clicks, page loads, and form submissions
- Number of fields completed vs. skipped
- Number of validation errors encountered
- Error recovery actions

### 5.3 System Usability Scale (SUS) Survey
Administer the standard 10-item SUS questionnaire after each evaluation round. Items use a 1–5 Likert scale (Strongly Disagree → Strongly Agree). The SUS produces a composite score (0–100) benchmarked against industry norms:

| SUS Score Range | Interpretation |
|-----------------|---------------|
| 80–100 | Excellent — users can recommend |
| 68–79 | Good — above average |
| 50–67 | Fair — needs improvement |
| 0–49 | Poor — major redesign required |

### 5.4 Cognitive Walkthrough
A human-computer interaction specialist performs a cognitive walkthrough of the seven defined tasks, evaluating:
- Is the correct action visible at each step?
- Can the user associate the action with the intended outcome?
- Is feedback provided after each action?
- Is error recovery straightforward?

## 6. Participants

### 6.1 Recruitment
- **Target:** 3–5 clinicians per evaluation round.
- **Roles:** At least 1 nephrologist (consultant), 1 nephrology registrar, 1 clinical coordinator, 1 data manager.
- **Inclusion:** Active BIRDEM nephrology staff, no prior GDES experience (baseline), or ≥ 2 weeks GDES exposure (mid/post-pilot).
- **Exclusion:** System developers, project leads (to avoid bias).

### 6.2 Consent
- Written informed consent for observation, screen recording, and survey participation.
- De-identification of all recorded data before analysis.
- Participants may withdraw at any time without impact on clinical duties.

## 7. Evaluation Schedule

| Round | Timing | Purpose | Instruments |
|-------|--------|---------|-------------|
| Baseline | Pre-pilot (Week −2 to 0) | Establish pre-deployment usability baseline using a mock-up or demo instance | SUS, task analysis (on mock tasks), cognitive walkthrough |
| Mid-pilot | Pilot Month 2 | Evaluate usability with real clinical data, identify critical issues | SUS, structured observation, task analysis, think-aloud |
| Post-pilot | Pilot Month 4–5 | Measure improvement after iterations, validate fixes | SUS, task analysis, satisfaction survey, cognitive walkthrough |

## 8. Data Collection Instruments

### 8.1 Observation Checklist

A per-task checklist completed by the trained observer:

| # | Observation Item | Yes/No | Notes |
|---|-----------------|--------|-------|
| 1 | User located the task entry point without assistance | | |
| 2 | User completed task without errors | | |
| 3 | User required > 3 attempts to complete a form field | | |
| 4 | User expressed confusion about a UI element | | |
| 5 | User utilised the global search function | | |
| 6 | User navigated to the wrong page before completing the task | | |
| 7 | User verbalised satisfaction or frustration | | |
| 8 | Task was completed within the expected time threshold | | |

### 8.2 SUS Questionnaire (10 Items)

1. I think I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think I would need technical support to use this system.
5. I found the various functions were well integrated.
6. I thought there was too much inconsistency in the system.
7. I would imagine most people would learn to use this system quickly.
8. I found the system very awkward to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

### 8.3 Task-Specific Feedback Form

For each completed task, the participant rates:

| Dimension | Scale | Question |
|-----------|-------|----------|
| Ease | 1–5 | How easy was this task? (1 = very difficult, 5 = very easy) |
| Time | 1–5 | Did the task take an appropriate amount of time? (1 = far too long, 5 = just right) |
| Clarity | 1–5 | Were the labels and instructions clear? |
| Confidence | 1–5 | How confident are you in the output/completion? |
| Free text | — | What would you change about this task? |

### 8.4 Think-Aloud Protocol

During mid-pilot evaluation, participants verbalise their thought process while completing tasks:
- "What are you trying to do now?"
- "What do you expect to happen when you click that?"
- "What is confusing you right now?"
- "On a scale of 1–5, how confident are you in this recommendation?"

## 9. Metrics

### 9.1 Per-Task Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Time to complete | Seconds from task start to successful completion | < 120 seconds for routine tasks |
| Click count | Total UI interactions (clicks, taps, keystrokes that trigger actions) | < 15 per task |
| Error count | Validation errors, mis-clicks requiring recovery | < 2 per task |
| Task completion rate | % of attempts resulting in successful completion without assistance | ≥ 90% |
| User satisfaction | Mean Likert rating (1–5) from task-specific feedback | ≥ 4.0 |

### 9.2 System-Level Metrics

| Metric | Target |
|--------|--------|
| Overall SUS score | ≥ 68 (good) by post-pilot |
| SUS improvement from baseline to post-pilot | ≥ +15 points |
| Alert-to-action ratio (recommendations reviewed vs. overridden) | ≥ 0.7 (70% accepted) |
| Mean time for recommendation review | < 60 seconds |

## 10. Analysis Methods

### 10.1 Qualitative Analysis
- **Thematic analysis** of think-aloud transcripts, free-text feedback, and observer notes.
- Coding framework: navigation, data entry, recommendation trust, alert fatigue, training, integration with existing workflow.
- Inter-rater reliability check on a random 20% of transcripts (target Cohen's kappa ≥ 0.7).

### 10.2 Quantitative Analysis
- Descriptive statistics (mean, median, SD) for time, clicks, errors, and satisfaction per task.
- Paired comparisons across evaluation rounds (baseline → mid → post).
- SUS score computation and benchmarking.
- Task completion rate by clinician role.
- Correlation analysis: SUS score vs. experience (years in nephrology), SUS score vs. digital literacy.

## 11. Improvement Prioritisation Framework

All identified issues are mapped to a 2×2 impact-vs-effort matrix:

| | **Low Effort** | **High Effort** |
|---|---|---|
| **High Impact** | **Quick Wins** — Implement immediately (e.g., rename ambiguous buttons, add missing tooltips) | **Major Projects** — Plan for next sprint (e.g., redesign patient search flow, add inline lab result previews) |
| **Low Impact** | **Fill-Ins** — Implement if capacity permits (e.g., colour tweaks, microcopy improvements) | **Deprioritise** — Document and revisit (e.g., full mobile redesign, advanced keyboard shortcuts) |

Priority score = Impact (1–5) × (6 − Effort), ranked descending.

## 12. Reporting Template

Each evaluation round produces a standardised report:

### UX Evaluation Report Structure

1. **Executive Summary** — Key findings, top 3 improvements, overall SUS score.
2. **Methodology** — Participants, tasks evaluated, instruments used.
3. **Quantitative Results** — Per-task metrics table, SUS score breakdown.
4. **Qualitative Findings** — Top 5 themes with representative quotes.
5. **Critical Issues** — Issues requiring immediate attention before pilot continuation.
6. **Improvement Recommendations** — Prioritised list with impact/effort classification.
7. **Appendix** — Raw SUS scores, observation checklists, think-aloud transcripts (redacted).

## 13. Expected Findings and Improvement Targets

Based on similar clinical decision support system deployments in nephrology:

| Finding | Expected Prevalence | Improvement Target (Post-Pilot) |
|---------|---------------------|---------------------------------|
| Navigation confusion between dashboard and clinic views | 40–60% of users | Reduce to < 15% |
| Excessive clicks for patient history access | 50% of users report friction | Reduce average clicks from > 5 to ≤ 3 |
| Data entry fatigue on baseline forms (30+ fields) | 60–80% of users | Add smart defaults and conditional visibility |
| Recommendation clarity concerns (evidence grading opaque) | 30–50% of users | Improve explanation text, add inline guideline quotes |
| Alert fatigue from low-priority alerts | 20–40% of users | Implement configurable alert thresholds |
| Time to first useful action on login | > 2 minutes | Reduce to < 45 seconds via personalised worklist |

## 14. Resource Requirements

| Resource | Allocation |
|----------|-----------|
| UX evaluator (trained observer) | 2 days per evaluation round |
| Statistician (SUS analysis, quantitative metrics) | 1 day per round |
| Participant compensation | BHD 20 gift card per clinician per round |
| Screen recording software | OBS Studio (open-source) |
| Transcription service | Otter.ai or Whisper for think-aloud sessions |
| Report preparation | 2 days post each evaluation round |

## 15. Governance

- UX review protocol reviewed and approved by the GDES Clinical Advisory Board.
- All participant data stored on encrypted local drives, accessible only to the UX team.
- De-identified aggregate results shared with the development team weekly during the pilot.
- Final UX evaluation report included in the pilot completion deliverables.

---

**Document Status:** Draft  
**Next Review:** Pre-pilot planning meeting  
**Distribution:** GDES Clinical Advisory Board, Development Team, BIRDEM Nephrology Department
