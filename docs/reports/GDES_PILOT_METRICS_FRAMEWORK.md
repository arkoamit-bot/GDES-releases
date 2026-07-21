# GDES Pilot Evaluation Metrics Framework

**Version:** 7.0
**Date:** 2026-07-11

---

## 1. Clinical Metrics

| Metric | Definition | Data Source | Target |
|--------|-----------|-------------|--------|
| Diagnostic Agreement | % AI top differential matches clinician final diagnosis | RecommendationAudit + Patient.primary_diagnosis | >80% |
| Guideline Adherence | % recommendations following KDIGO guidance | RecommendationAudit.evidence_grade != "OP" | >90% |
| Management Agreement | % AI management plan accepted without override | RecommendationAudit.approval_status != "overridden" | >85% |
| Follow-up Compliance | % scheduled follow-up visits completed | ScheduledVisit.status vs FollowUpTask.status | >70% |
| Override Rate | % recommendations overridden by clinician | RecommendationAudit.approval_status = "overridden" | <15% |
| Override Justification | % overrides with documented reason | RecommendationAudit.override_reason != "" | 100% |

## 2. Operational Metrics

| Metric | Definition | Data Source | Target |
|--------|-----------|-------------|--------|
| Consultation Duration | Time from patient open to reason generated | Timestamp diff | <5 min |
| User Satisfaction | Clinician satisfaction survey (1-5 scale) | Survey form | >4.0 |
| Clicks to Recommendation | Number of clicks to view a recommendation | UI analysis | <3 |
| Response Time | Time for reasoning engine to return | Engine profiling | <1 second |
| System Stability | Uptime during pilot hours | Server logs | >99% |
| Data Entry Time | Time to enter a complete lab panel | Timer study | <2 min |

## 3. Research Metrics

| Metric | Definition | Data Source | Target |
|--------|-----------|-------------|--------|
| Registry Completeness | % patients with complete baseline data | Patient fields completeness | >90% |
| Missing Data Rate | % required fields empty across all patients | NULL field count | <10% |
| Cohort Generation | Ability to generate disease cohorts from KB | Patient.primary_diagnosis distribution | All 18 diseases |
| Dataset Quality | Completeness of exported research datasets | Export validation | >95% |

## 4. Knowledge Quality Metrics

| Metric | Definition | Data Source | Target |
|--------|-----------|-------------|--------|
| Rule Accuracy | % KB rules producing correct recommendations | Retrospective validation | >85% |
| Evidence Grade Distribution | % rules with Level 1 or Level 2 evidence | KnowledgeBaseEntry.evidence_grade | >60% |
| Knowledge Freshness | Average age of KB rules | KnowledgeBaseEntry.effective_date | <2 years |
| Review Coverage | % rules with assigned reviewer | KnowledgeBaseEntry.approved_by IS NOT NULL | >80% |

## 5. Metrics Collection

- **RecommendationAudit:** auto-collected for every recommendation
- **ClinicalEncounter:** timestamps for duration metrics
- **FollowUpTask:** status tracking for compliance
- **Export:** JSON/CSV export from admin dashboard

## 6. Reporting

- **Weekly:** override rate, diagnostic agreement, system stability
- **Monthly:** full metrics dashboard
- **End of pilot:** comprehensive evaluation report
