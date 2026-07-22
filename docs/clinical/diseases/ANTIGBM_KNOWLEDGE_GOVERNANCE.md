# Anti-GBM Disease (Goodpasture Syndrome) Knowledge Governance

**Document ID**: ANTIGBM_KG  
**Version**: 1.0  
**Date**: 2026-07-10  
**Domain**: Anti-Glomerular Basement Membrane Antibody Disease  
**Classification**: Knowledge Governance Framework

---

## 1. Overview

This document defines the governance framework for anti-GBM disease knowledge management within the BGDDR system. It covers the knowledge lifecycle, versioning protocols, health check standards, quality dashboard metrics, and anti-GBM-specific governance considerations. The framework ensures that anti-GBM knowledge remains accurate, current, and clinically actionable, with particular attention to the urgent nature of diagnosis and treatment, the evolving role of rituximab, and the exceptional low relapse rate that distinguishes this disease from ANCA vasculitis. Given the rarity of anti-GBM disease (<2 per million), knowledge accuracy is paramount and the consequences of outdated or incorrect guidance are severe.

---

## 2. Knowledge Lifecycle

### 2.1 Lifecycle Stages

```
                    ANTIGBM KNOWLEDGE LIFECYCLE
    
    [IDENTIFY] --> [CREATE] --> [VALIDATE] --> [PUBLISH]
         ^                                        |
         |                                        v
    [REVIEW] <-- [UPDATE] <-- [MONITOR] <-- [OPERATIONAL]
```

| Stage | Description | Owner | Frequency |
|-------|-------------|-------|-----------|
| Identify | Recognise knowledge gap or update need (new case series, guideline change, safety signal) | Clinical Lead | Ongoing |
| Create | Draft new content or revisions | Knowledge Author | As needed |
| Validate | Clinical accuracy and evidence-based review by subject matter expert | Peer Reviewer | Before publish |
| Publish | Release to production | Knowledge Manager | After validation |
| Operational | Content active in clinical workflows | System | Continuous |
| Monitor | Track usage, clinical outcomes, feedback | Analytics | Monthly |
| Update | Revise based on evidence, feedback, or guideline changes | Knowledge Author | As triggered |
| Review | Periodic comprehensive review | Clinical Lead | Biannual |

### 2.2 Trigger Events for Knowledge Updates

| Trigger | Priority | Response Time | Evidence Source |
|---------|----------|---------------|-----------------|
| New RCT or large case series in anti-GBM | High | 30 days | KI, JASN, NDT, CJASN |
| KDIGO guideline update | High | 60 days | Kidney International |
| ASFA guideline update | High | 60 days | Journal of Clinical Apheresis |
| FDA/EMA regulatory action (rituximab for anti-GBM) | High | 14 days | FDA.gov, EMA.europa.eu |
| EULAR/ERA-EDTA update | High | 60 days | Annals Rheum Dis |
| New evidence on rituximab vs CyP | Medium | 30 days | Peer-reviewed journals |
| PLEX protocol change or evidence | Medium | 30 days | Apheresis literature |
| Double-positive disease management data | Medium | 60 days | Peer-reviewed journals |
| Clinical feedback on error or omission | High | 14 days | Internal reporting |
| Routine biannual review | Medium | 90 days | Scheduled |

### 2.3 Knowledge Ownership

| Knowledge Component | Owner | Reviewer |
|---------------------|-------|----------|
| Disease knowledge (21 fields) | Clinical Lead (Nephrology) | External Expert (Renal Immunology) |
| KB rules (28 rules) | Clinical Lead | Knowledge Engineer |
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
| Major | X.0 | 2.0 | Fundamental restructuring, new treatment paradigm |
| Minor | X.Y | 1.3 | Content additions, significant revisions |
| Patch | X.Y.Z | 1.0.2 | Corrections, typos, formatting |

### 3.2 Current Anti-GBM Knowledge Versions

| Document | Version | Date | Next Review |
|----------|---------|------|-------------|
| ANTIGBM_DISEASE_KNOWLEDGE.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANTIGBM_CLINICAL_PATHWAY.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANTIGBM_DRUG_KNOWLEDGE.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANTIGBM_CLINICAL_CASES.md | 1.0 | 2026-07-10 | 2027-07-10 |
| ANTIGBM_GUIDELINE_MAPPING.md | 1.0 | 2026-07-10 | 2027-01-10 |
| ANTIGBM_KNOWLEDGE_GOVERNANCE.md | 1.0 | 2026-07-10 | 2027-07-10 |
| ANTIGBM_COMPLETENESS_DASHBOARD.md | 1.0 | 2026-07-10 | 2027-01-10 |

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
| Outdated guideline citations | Monthly | Guideline mapping comparison | <1 year old for active guidelines |
| Drug interaction accuracy | Monthly | Drug knowledge review | 100% accurate |
| Case consistency | Monthly | Case versus pathway validation | All cases map to pathway |
| Anti-GBM antibody testing protocols | Quarterly | Serology knowledge check | Consistent with EQA standards |

### 4.2 Manual Health Checks

| Check | Frequency | Reviewer | Criteria |
|-------|-----------|----------|----------|
| Clinical accuracy audit | Biannual | External Expert (Renal Immunologist) | 100% clinically accurate |
| Guideline concordance | Biannual | Clinical Lead | Aligned with KDIGO, ASFA, EULAR |
| Pathway relevance | Annual | Pathway Coordinator | Reflects current practice |
| Case teaching value | Annual | Case Author | Relevant, distinct, educational |
| PLEX protocol review | Annual | Apheresis Unit Lead | Consistent with ASFA guidelines |

### 4.3 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Completeness score | >=95% | 12-domain dashboard |
| Update response time (high priority) | <=30 days | Trigger-to-publish |
| Update response time (critical) | <=7 days | Trigger-to-publish |
| Accuracy rate | 100% | Audit findings |
| Guideline alignment | >=90% | Cross-reference score |
| User satisfaction | >=4/5 | Survey |
| KB rule activation | 100% | All 28 rules active |

---

## 5. KB Rules Governance

### 5.1 Rule Inventory

| Rule Category | Count | Status |
|---------------|-------|--------|
| Diagnostic rules | 12 | Active |
| Prognostic rules | 5 | Active |
| Treatment rules | 5 | Active |
| Monitoring rules | 3 | Active |
| Referral rules | 3 | Active |
| **Total** | **28** | **All active** |

### 5.2 Rule Lifecycle

| Phase | Description |
|-------|-------------|
| Draft | Rule proposed, not yet validated |
| Active | Rule live in clinical decision support |
| Deprecated | Rule superseded by evidence or new agent |
| Archived | Rule removed from active use but retained |

### 5.3 Key Rule Examples

| Rule ID | Category | Description |
|---------|----------|-------------|
| ANTIGBM-DX-01 | Diagnostic | Positive anti-GBM ELISA + linear IgG on IF = confirmed diagnosis |
| ANTIGBM-DX-02 | Diagnostic | RPGN + DAH (pulmonary-renal syndrome) requires same-day PLEX |
| ANTIGBM-DX-05 | Diagnostic | Bimodal age: suspect anti-GBM in young males with DAH and elderly females with RPGN |
| ANTIGBM-DX-08 | Diagnostic | Double-positive (anti-GBM + ANCA) requires dual-disease management |
| ANTIGBM-PX-01 | Prognostic | Cr >5.7 mg/dL at presentation predicts <50% renal recovery |
| ANTIGBM-PX-03 | Prognostic | >50% fibrous crescents on biopsy predicts negligible renal recovery |
| ANTIGBM-TX-01 | Treatment | Initiate PLEX same-day; do not wait for full biopsy |
| ANTIGBM-TX-04 | Treatment | Rituximab alternative to CyP in elderly, infection risk, or CyP intolerance |
| ANTIGBM-MN-01 | Monitoring | Monitor anti-GBM q1-2 days during PLEX; guide duration by titre |

### 5.4 Rule Update Triggers

- New evidence changes diagnostic or treatment paradigm
- Guideline update alters recommendation grade
- Drug approval for new anti-GBM indication (rituximab)
- Safety signal requiring rule modification
- Clinical feedback indicating rule inaccuracy

---

## 6. Pathway Governance

### 6.1 Pathway Stages

| Stage | ID | Duration | Actions | Owner |
|-------|----|----------|---------|-------|
| Urgent Diagnosis | ANTIGBM-PATH-01 | 2 days | 8 actions | Nephrologist / Renal Pathologist |
| Induction PLEX+IS | ANTIGBM-PATH-02 | 14 days | 10 actions | Apheresis Unit / Nephrologist |
| Continued Induction | ANTIGBM-PATH-03 | 90 days | 8 actions | Nephrologist |
| Remission/Recovery | ANTIGBM-PATH-04 | 180 days | 8 actions | Nephrologist |
| Long-term/ESKD | ANTIGBM-PATH-05 | 365 days | 8 actions | Nephrologist / Transplant Team |
| Renal Transplant | ANTIGBM-PATH-06 | 365 days | 8 actions | Transplant Team |

### 6.2 Pathway Validation

Each pathway stage requires validation against:
- Evidence from published cohort studies (Levy, Johnson, Cui, Heitz, McAdoo, Hellmark)
- Alignment with major guidelines (KDIGO 2021/2025, ASFA 2023, BSR 2020)
- Real-world feasibility (PLEX availability, resource settings)
- Safety and tolerability of recommended regimens
- Explicit consideration of when to treat and when to palliate (biopsy chronicity)

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

For critical safety issues (PLEX protocol error, dosing error, drug withdrawal):
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

All anti-GBM knowledge assets are stored in version-controlled markdown documents with a standardised front matter format. Cross-references between documents are maintained through consistent naming conventions and internal links. Given the rarity of anti-GBM disease, knowledge retention is particularly important — clinicians may encounter this disease only once or twice in their career.

### 9.2 Training Requirements

| Role | Required Knowledge Level | Renewal |
|------|--------------------------|---------|
| Nephrologist | Expert (able to diagnose and treat same-day) | Annually |
| Apheresis Physician | Expert (PLEX protocols) | Annually |
| Renal Pathologist | Expert (linear IgG identification) | Annually |
| Emergency Physician | Intermediate (recognise pulmonary-renal syndrome) | Biannually |
| Intensive Care Physician | Intermediate (DAH management) | Biannually |
| Pharmacist | Intermediate (drug knowledge, PLEX interactions) | Annually |
| Nurse (Apheresis/Transplant) | Basic (monitoring, adverse effects) | Biannually |
| Trainee | Intermediate | During rotation |

