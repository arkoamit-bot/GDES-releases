# ANCA-Associated Vasculitis Knowledge Governance

**Document ID**: ANCA_KG  
**Version**: 1.0  
**Date**: 2026-07-10  
**Domain**: ANCA-Associated Pauci-Immune Glomerulonephritis  
**Classification**: Knowledge Governance Framework  

---

## 1. Overview

This document defines the governance framework for ANCA-associated vasculitis knowledge management within the BGDDR system. It covers the knowledge lifecycle, versioning protocols, health check standards, quality dashboard metrics, and AAV-specific governance considerations. The framework ensures that AAV knowledge remains accurate, current, and clinically actionable, with particular attention to the rapidly evolving therapeutic landscape (avacopan integration, serotype-specific management, and steroid-minimising strategies).

---

## 2. Knowledge Lifecycle

### 2.1 Lifecycle Stages

```
                    ANCA KNOWLEDGE LIFECYCLE
                    
    [IDENTIFY] --> [CREATE] --> [VALIDATE] --> [PUBLISH]
         ^                                        |
         |                                        v
    [REVIEW] <-- [UPDATE] <-- [MONITOR] <-- [OPERATIONAL]
```

| Stage | Description | Owner | Frequency |
|-------|-------------|-------|-----------|
| Identify | Recognise knowledge gap or update need (new trial, guideline change, safety signal) | Clinical Lead | Ongoing |
| Create | Draft new content or revisions | Knowledge Author | As needed |
| Validate | Clinical accuracy and evidence-based review | Peer Reviewer | Before publish |
| Publish | Release to production | Knowledge Manager | After validation |
| Operational | Content active in clinical workflows | System | Continuous |
| Monitor | Track usage, clinical outcomes, feedback | Analytics | Monthly |
| Update | Revise based on evidence, feedback, or guideline changes | Knowledge Author | As triggered |
| Review | Periodic comprehensive review | Clinical Lead | Biannual |

### 2.2 Trigger Events for Knowledge Updates

| Trigger | Priority | Response Time | Evidence Source |
|---------|----------|---------------|-----------------|
| New RCT in AAV (phase 3) | High | 30 days | NEJM, Lancet, JAMA |
| KDIGO guideline update | High | 60 days | Kidney International |
| EULAR/ACR guideline update | High | 60 days | Annals Rheum Dis, Arthritis Care Res |
| FDA/EMA regulatory action (new drug, label change, safety) | High | 14 days | FDA.gov, EMA.europa.eu |
| Avacopan safety signal or new indication | Critical | 7 days | Pharmacovigilance |
| Rituximab biosimilar approval | Medium | 30 days | Regulatory agencies |
| PLEX protocol change | Medium | 30 days | Apheresis guidelines |
| Serotype-specific management data | Medium | 60 days | Peer-reviewed journals |
| Clinical feedback on error or omission | High | 14 days | Internal reporting |
| Routine biannual review | Medium | 90 days | Scheduled |

### 2.3 Knowledge Ownership

| Knowledge Component | Owner | Reviewer |
|---------------------|-------|----------|
| Disease knowledge (21 fields) | Clinical Lead (Nephrology/Rheumatology) | External Expert |
| KB rules (29 rules) | Clinical Lead | Knowledge Engineer |
| Clinical pathways (6 stages) | Clinical Lead | Pathway Coordinator |
| Clinical cases (8 cases) | Case Author | Clinical Lead |
| Drug knowledge | Clinical Pharmacist | Clinical Lead |
| Guideline mapping | Clinical Lead | Guideline Committee |
| Evidence summaries | Research Lead | Clinical Lead |
| Completeness dashboard | Knowledge Manager | Clinical Lead |

---

## 3. Versioning Protocol

### 3.1 Version Numbering

| Version Type | Format | Example | When |
|-------------|--------|---------|------|
| Major | X.0 | 2.0 | Fundamental restructuring, new paradigm |
| Minor | X.Y | 1.3 | Content additions, significant revisions |
| Patch | X.Y.Z | 1.0.2 | Corrections, typos, formatting |

### 3.2 Current ANCA Knowledge Versions

| Document | Version | Date | Next Review |
|----------|---------|------|-------------|
| ANCA_DISEASE_KNOWLEDGE.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANCA_CLINICAL_PATHWAY.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANCA_DRUG_KNOWLEDGE.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANCA_CLINICAL_CASES.md | 1.0 | 2026-07-10 | 2027-07-10 |
| ANCA_GUIDELINE_MAPPING.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANCA_KNOWLEDGE_GOVERNANCE.md | 1.0 | 2026-07-10 | 2027-07-10 |
| ANCA_COMPLETENESS_DASHBOARD.md | 1.0 | 2026-07-10 | 2027-01-10 |

### 3.3 Version History Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-10 | BGDDR Knowledge Team | Initial release |

---

## 4. Health Check Protocols

### 4.1 Automated Health Checks

| Check | Frequency | Tool | Threshold |
|-------|-----------|------|-----------|
| Document completeness score | Monthly | Completeness dashboard | >=95% |
| Broken internal references | Monthly | Link checker | 0 broken |
| Outdated guideline citations | Monthly | Guideline mapping comparison | <1 year old |
| Drug interaction accuracy | Monthly | Drug knowledge review | 100% accurate |
| Case consistency | Monthly | Case versus pathway validation | All cases map to pathway |

### 4.2 Manual Health Checks

| Check | Frequency | Reviewer | Criteria |
|-------|-----------|----------|----------|
| Clinical accuracy audit | Biannual | External Expert | 100% clinically accurate |
| Guideline concordance | Biannual | Clinical Lead | Aligned with KDIGO/EULAR/ACR |
| Pathway relevance | Annual | Pathway Coordinator | Reflects current practice |
| Case teaching value | Annual | Case Author | Relevant, distinct, educational |

### 4.3 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Completeness score | >=95% | 12-domain dashboard |
| Update response time | <=30 days (high priority) | Trigger-to-publish |
| Accuracy rate | 100% | Audit findings |
| Guideline alignment | >=90% | Cross-reference score |
| User satisfaction | >=4/5 | Survey |

---

## 5. KB Rules Governance

### 5.1 Rule Inventory

| Rule Category | Count | Status |
|---------------|-------|--------|
| Diagnostic rules | 9 | Active |
| Prognostic rules | 5 | Active |
| Treatment rules | 8 | Active |
| Monitoring rules | 3 | Active |
| Referral rules | 2 | Active |
| Exclusion rules | 2 | Active |
| **Total** | **29** | **All active** |

### 5.2 Rule Lifecycle

| Phase | Description |
|-------|-------------|
| Draft | Rule proposed, not yet validated |
| Active | Rule live in clinical decision support |
| Deprecated | Rule superseded by evidence or new agent |
| Archived | Rule removed from active use but retained |

### 5.3 Rule Update Triggers

- New evidence changes diagnostic or treatment paradigm
- Guideline update alters recommendation grade
- Drug approval or withdrawal (e.g., avacopan integration)
- Safety signal requiring rule modification
- Clinical feedback indicating rule inaccuracy

---

## 6. Pathway Governance

### 6.1 Pathway Stages

| Stage | Duration | Actions | Owner |
|-------|----------|---------|-------|
| 1. Diagnosis & Classification | 7 days | 8 actions | Renal Pathologist/Nephrologist |
| 2. Induction Therapy | 120 days | 10 actions | Nephrologist/Infusion Team |
| 3. Remission & Maintenance | 180 days | 8 actions | Nephrologist |
| 4. Long-Term Monitoring | 730 days | 8 actions | Nephrologist |
| 5. Relapse Management | 90 days | 10 actions | Nephrologist |
| 6. ESKD/Transplantation | 365 days | 8 actions | Transplant Team |

### 6.2 Pathway Validation

Each pathway stage requires validation against:
- Evidence from key trials (RAVE, PEXIVAS, ADVOCATE, MAINRITSAN, RITAZAREM)
- Alignment with major guidelines (KDIGO, EULAR, ACR)
- Real-world feasibility (resource availability, local protocols)
- Safety and tolerability of recommended regimens

---

## 7. Change Management Process

### 7.1 Change Request Workflow

1. **Submit**: Clinical Lead or Knowledge Author submits change request via governance portal
2. **Triage**: Knowledge Manager assesses priority (critical/high/medium/low)
3. **Review**: Peer Reviewer evaluates clinical accuracy and evidence basis
4. **Approve**: Clinical Lead approves final content
5. **Publish**: Knowledge Manager updates document version and publishes
6. **Notify**: Relevant stakeholders notified of change
7. **Audit**: Change logged in version history

### 7.2 Emergency Change Protocol

For critical safety issues (drug withdrawal, severe adverse event, dosing error):
1. Immediate notification to Clinical Lead and Knowledge Manager
2. Provisional fix within 24 hours
3. Full validation within 7 days

---

## 8. Audit and Compliance

### 8.1 Internal Audit Schedule

| Audit Type | Frequency | Scope |
|------------|-----------|-------|
| Completeness audit | Monthly | All 7 documents scored |
| Accuracy audit | Biannual | Random 20% of content sampled |
| Guideline alignment audit | Biannual | All guidelines referenced |
| Usage audit | Quarterly | Pathway and rule utility |

### 8.2 Compliance Standards

| Standard | Requirement | Status |
|----------|-------------|--------|
| KB rule accuracy | 100% evidence-based | Compliant |
| Version tracking | All documents versioned | Compliant |
| Review schedule | Within defined intervals | Compliant |
| Clinical approval | Signed off by Clinical Lead | Compliant |
| External validation | Reviewed by subject matter expert | Planned |

---

## 9. Knowledge Retention and Training

### 9.1 Knowledge Transfer

All ANCA knowledge assets are stored in version-controlled markdown documents with a standardised front matter format. Cross-references between documents are maintained through consistent naming conventions and internal links.

### 9.2 Training Requirements

| Role | Required Knowledge Level | Renewal |
|------|--------------------------|---------|
| Nephrologist | Expert (able to treat) | Annually |
| Rheumatologist | Expert (able to treat) | Annually |
| Renal Pathologist | Expert (diagnostic) | Annually |
| Pharmacist | Intermediate (drug knowledge) | Annually |
| Nurse | Basic (monitoring, adverse effects) | Biannually |
| Trainee | Intermediate | During rotation |
