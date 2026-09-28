# Knowledge Governance Framework V2
**Document ID:** GDES-V4.2-GOV-002
**Version:** 2.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Knowledge Governance

---

## 1. Governance Philosophy

V4.1 established per-disease governance (author, reviewer, approval status). V4.2 elevates governance to the *knowledge ecosystem* level — governing reusable objects, cross-disease relationships, and the reasoning engine itself.

### 1.1 Core Principles

| Principle | V4.1 Application | V4.2 Enhancement |
|---|---|---|
| **Authority** | KDIGO primary per disease | Multi-organization hierarchy with explicit precedence |
| **Accuracy** | Expert review per disease | Methodology + clinical dual review for all objects |
| **Currency** | 12-month disease review | Object-level freshness with automated alerts |
| **Completeness** | 21 fields per disease | 12-domain ecosystem quality metrics |
| **Traceability** | Rule→guideline link | Full provenance graph: author→review→evidence→guideline→object→version |
| **Accountability** | Named author/reviewer | Role-based RACI with qualifications and COI |
| **Transparency** | Disease-level changelog | Public knowledge graph with versioned objects |
| **Interoperability** | Internal formats | FHIR/SNOMED/LOINC mapping; open export |

### 1.2 Governance Scope

**In Scope (V4.2):**
- All 12 reusable knowledge object types
- Cross-disease relationships (syndrome↔disease, drug↔disease, etc.)
- Clinical reasoning engine configuration
- Validation library and test suite
- Quality dashboard and metrics

**Out of Scope:**
- Patient data governance (separate FHIR/clinical governance)
- Infrastructure/security governance (separate IT governance)
- Regulatory submission governance (separate medical device governance)

---

## 2. Knowledge Object Lifecycle

### 2.1 Object Types and Lifecycle States

| Object Type | States | Typical Duration |
|---|---|---|
| **Disease** | `draft` → `internal_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 2-4 weeks |
| **Syndrome** | `draft` → `internal_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 2-3 weeks |
| **Pathology Entity** | `draft` → `internal_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 1-2 weeks |
| **Lab Entity** | `draft` → `internal_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 1-2 weeks |
| **Drug** | `draft` → `pharmacist_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 2-3 weeks |
| **Monitoring Protocol** | `draft` → `internal_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 1-2 weeks |
| **Complication** | `draft` → `internal_review` → `clinical_review` → `approved` → `published` → `superseded` → `archived` | 1-2 weeks |
| **Guideline Source** | `pending` → `parsed` → `mapped` → `validated` → `active` → `retired` | 2-4 weeks |
| **Validation Case** | `draft` → `expert_review` → `approved` → `published` → `retired` | 2-4 weeks |
| **KB Rule** | `draft` → `under_review` → `approved` → `active` → `superseded` → `retired` | 1-2 weeks |

### 2.2 Valid Transitions

```
draft → internal_review → clinical_review → approved → published
                ↓              ↓              ↓          ↓
             archived      draft          draft      superseded → archived
                                              ↓
                                         retired
```

**Rules:**
- Only `published` objects are visible to the reasoning engine
- `superseded` objects remain queryable but flagged
- `archived` objects are hidden from engine but retained for audit
- `retired` objects are deleted from engine but metadata preserved

### 2.3 Transition Triggers

| From → To | Trigger | Required Actions |
|---|---|---|
| `draft` → `internal_review` | Author submits | Methodology reviewer assigned |
| `internal_review` → `clinical_review` | Methodology pass | Clinical reviewer assigned |
| `internal_review` → `draft` | Changes requested | Author revisited | Author revises |
| `clinical_review` → `approved` | Clinical sign-off | Governance lead approval |
| `clinical_review` → `draft` | Changes requested | Author revises |
| `approved` → `published` | Scheduled release | Version increment, changelog |
| `published` → `superseded` | New version published | Migration plan, deprecation notice |
| `published` → `archived` | Obsolete, no replacement | Archive reason documented |
| `superseded` → `archived` | Grace period expired | Final archive |

---

## 3. Roles and Responsibilities (RACI)

### 3.1 Role Definitions

| Role | Qualifications | Time Commitment | Primary Responsibilities |
|---|---|---|---|
| **Governance Lead** | Board-certified nephrologist + 5yr informatics | 4 hrs/week | Overall framework; escalation; release approval |
| **Disease Curator** (23) | Nephrology fellowship; disease expertise | 3 hrs/week | Disease object accuracy; case curation; KB rules |
| **Syndrome Curator** (4) | Nephrology + general medicine | 2 hrs/week | Syndrome objects; DDx tables |
| **Pathology Curator** (2) | Renal pathologist | 2 hrs/week | Pathology entities; biopsy standards |
| **Lab Curator** (2) | Clinical chemist / nephrologist | 2 hrs/week | Lab entities; reference ranges |
| **Pharmacist Reviewer** (2) | Clinical pharmacist, transplant/nephrology | 3 hrs/week | Drug objects; renal dosing; interactions |
| **Clinical Reviewer** (6) | Board-certified nephrologist | 3 hrs/week | Clinical sign-off on all objects |
| **Methodology Reviewer** (2) | Medical informatics / epidemiology | 2 hrs/week | Evidence grading; bias assessment; study quality |
| **Validation Engineer** (2) | Software engineer + clinical background | 4 hrs/week | Test suite; CI/CD; regression detection |
| **Data Steward** (1) | Health informatics + privacy | 2 hrs/week | De-identification; IRB; metadata standards |

### 3.2 RACI Matrix

| Activity | Gov Lead | Disease Curator | Syndrome Curator | Path Curator | Lab Curator | Pharm Reviewer | Clin Reviewer | Method Reviewer | Val Engineer | Data Steward |
|---|---|---|---|---|---|---|---|---|---|---|
| **Author object** | I | R/A (disease) | R/A (syndrome) | R/A (path) | R/A (lab) | R/A (drug) | C | C | I | I |
| **Methodology review** | A | C | C | C | C | C | I | R | I | I |
| **Clinical review** | A | C | C | C | C | C | R | C | I | I |
| **Approve for publication** | R/A | I | I | I | I | I | C | I | I | I |
| **Assign version** | R | I | I | I | I | I | I | I | I | I |
| **De-identify case** | A | C | I | I | I | I | C | I | I | R |
| **COI declaration** | R | R | R | R | R | R | R | R | R | I |
| **Run validation** | A | I | I | I | I | I | C | I | R | I |
| **Analyze failures** | A | R | R | R | R | R | C | C | R | I |
| **Release decision** | R/A | C | C | C | C | C | C | C | C | I |

---

## 4. Review and Approval Workflow

### 4.1 Standard Workflow (All Objects)

```
┌─────────────┐
│   DRAFT     │  Author creates object using template
└──────┬──────┘
       │ submit
       ▼
┌──────────────────┐
│ INTERNAL REVIEW  │  Methodology Reviewer checks:
└──────┬───────────┘  • Evidence grading (GRADE/Oxford)
       │             • Study quality assessment
       │ pass        • Bias/confounding evaluation
       │             • Statistical appropriateness
       ▼
┌───────────────────┐
│ CLINICAL REVIEW   │  Clinical Reviewer checks:
└──────┬────────────┘  • Clinical accuracy
       │               • Guideline alignment
       │ pass          • Practical applicability
       │               • Safety considerations
       ▼
┌─────────────┐
│  APPROVED   │  Governance Lead final sign-off
└──────┬──────┘  • Completeness check
       │         • Cross-object consistency
       │ publish │ Compliance verification
       ▼
┌─────────────┐
│  PUBLISHED  │  Version assigned, changelog, engine deployment
└─────────────┘
```

### 4.2 Expedited Workflow (Urgent Updates)

For critical safety updates (e.g., new FDA black box warning, guideline reversal):

```
DRAFT → CLINICAL REVIEW (bypass methodology) → EMERGENCY APPROVAL (Gov Lead) → PUBLISHED
```

**Requirements:**
- Clinical Reviewer + Governance Lead dual sign-off
- 24-hour maximum cycle time
- Post-publication methodology review within 7 days
- Full audit trail retained

### 4.3 Batch Workflow (Guideline Updates)

When KDIGO/ERA publish new guidelines:

```
1. GuidelineSource created (status: pending)
2. Parsing pipeline extracts rule candidates
3. Disease Curators review candidates for their diseases
4. Methodology Reviewers grade evidence
5. Clinical Reviewers validate recommendations
6. Batch approval → versioned KB rules deployed
7. Old rules → superseded with migration mapping
```

---

## 5. Conflict of Interest Management

### 5.1 Declaration Requirements

**Mandatory at authoring for ALL authors:**
- Financial: Consulting, speakers bureau, advisory boards, equity, royalties, grants
- Intellectual: Patents, guidelines authorship, competing protocols
- Institutional: Employer relationships with relevant companies
- Personal: Family financial interests

### 5.2 COI Thresholds and Actions

| COI Type | Threshold | Action |
|---|---|---|
| **Financial** | >$5,000/yr from relevant company | Recuse from authoring related drugs; independent reviewer assigned |
| **Guideline Authorship** | Author of guideline being implemented | Must declare; independent methodology review required |
| **Patent/IP** | Related to object content | Full transparency; independent clinical review |
| **Institutional** | Employer has commercial interest | Disclosure only; no automatic recusal |

### 5.3 COI Registry

- Public registry of all declarations (anonymized for privacy)
- Annual re-attestation
- Audit trail for all COI-related decisions

---

## 6. Evidence Grading Standards

### 6.1 Mandatory Grading Systems

| Question Type | Primary System | Secondary System |
|---|---|---|
| **Treatment** | GRADE | SORT |
| **Diagnosis/Prognosis** | Oxford CEBM | QUADAS-2 (diagnostic) |
| **Etiology/Harm** | Newcastle-Ottawa | GRADE (observational) |
| **Expert Opinion** | Explicitly labeled "Expert Opinion" | N/A |

### 6.2 Evidence Table Requirements

Every treatment/diagnostic recommendation MUST include:

```yaml
evidence_summary:
  - recommendation: "ACEi first-line for proteinuric IgAN"
    grade: "1B"
    evidence_type: "RCT"
    studies:
      - citation: "STOP-IgAN Trial, Lancet 2015"
        design: "RCT"
        n: 162
        population: "IgAN, proteinuria >0.75g/d"
        intervention: "Ramipril vs supportive"
        outcome: "Proteinuria reduction 40% vs 10%"
        quality: "Low risk of bias"
        grade_contribution: "Major"
    guideline_sources:
      - source: "KDIGO 2021"
        chapter: "3.1.1"
        quote: "We recommend ACEi or ARB for IgAN with proteinuria >0.5g/d"
    last_reviewed: "2026-06-01"
    next_review: "2027-06-01"
```

### 6.3 Downgrading/Upgrading Rules

| Factor | Downgrade | Upgrade |
|---|---|---|
| **Risk of Bias** | Serious (-1), Very serious (-2) | N/A |
| **Inconsistency** | Unexplained heterogeneity (-1) | N/A |
| **Indirectness** | Population/intervention/outcome mismatch (-1) | N/A |
| **Imprecision** | Wide CI crossing decision threshold (-1) | N/A |
| **Publication Bias** | Suspected (-1) | N/A |
| **Large Effect** | N/A | RR >2 or <0.5 (+1), RR >5 or <0.2 (+2) |
| **Dose-Response** | N/A | Clear gradient (+1) |
| **Confounding** | N/A | Residual confounding would reduce effect (+1) |

---

## 7. Version Control and Change Management

### 7.1 Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH[-prerelease]`

| Version Bump | Trigger | Examples |
|---|---|---|
| **MAJOR** | Breaking change to object schema or reasoning logic | Disease model field added/removed; new node type |
| **MINOR** | New content, non-breaking | New disease; new syndrome; new drug; new cases |
| **PATCH** | Corrections, clarifications | Typo fix; evidence grade correction; reference update |

### 7.2 Change Classification

| Class | Description | Review Required |
|---|---|---|
| **Correction** | Factual error fix (wrong dose, wrong reference) | Expedited clinical review |
| **Enhancement** | New content, expanded explanation | Standard workflow |
| **New Evidence** | New trial/guideline incorporated | Methodology + clinical review |
| **Guideline Update** | KDIGO/ERA new version | Batch workflow |
| **Breaking Change** | Schema change, node type added/removed | Architecture review + Gov Lead approval |

### 7.3 Migration for Breaking Changes

1. **Impact Analysis** — Identify all downstream objects, rules, cases, engine logic
2. **Migration Plan** — Automated scripts + manual review checklist
3. **Parallel Run** — Old and new versions simultaneously for 30 days
4. **Validation** — Full regression test suite pass
5. **Cutover** — Single deployment with rollback capability
6. **Post-Deploy Monitoring** — 7-day intensive monitoring

---

## 8. Quality Assurance

### 8.1 Automated Checks (CI/CD Pipeline)

| Check | Trigger | Failure Action |
|---|---|---|
| **Schema Validation** | Every commit | Block merge |
| **Required Fields** | Every commit | Block merge |
| **Evidence Grade Validity** | Every commit | Block merge |
| **Guideline Linkage** | Every commit | Warning (not block) |
| **COI Declaration** | Every commit | Block merge |
| **COI-Author Match** | Every commit | Warning |
| **Cross-Reference Integrity** | Nightly | JIRA ticket |
| **Orphan Node Detection** | Weekly | JIRA ticket |
| **Freshness Audit** | Monthly | Alert to curators |
| **Full Regression Suite** | Per release | Block release |

### 8.2 Manual Audits

| Audit | Frequency | Scope | Owner |
|---|---|---|---|
| **Peer Audit** | Quarterly | 10% random sample of published objects | Disease Curator (cross-disease) |
| **Clinical Accuracy Audit** | Semi-annual | All objects modified in period | Clinical Reviewer |
| **Evidence Grading Audit** | Annual | All treatment recommendations | Methodology Reviewer |
| **External Audit** | Annual | Full system by independent body | External consultant |
| **Governance Compliance** | Annual | RACI adherence, COI registry, versioning | Governance Lead |

### 8.3 Metrics for QA

| Metric | Target |
|---|---|
| **Time to publish (standard)** | <21 days |
| **Time to publish (expedited)** | <24 hours |
| **Rejection rate (internal review)** | <15% |
| **Rejection rate (clinical review)** | <10% |
| **Post-publication corrections** | <2% of objects/year |
| **Critical safety corrections** | 0 |
| **Audit findings (critical)** | 0 |
| **Audit findings (major)** | <3/year |

---

## 9. Risk Register

| Risk ID | Risk Description | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| **R1** | Outdated knowledge used in clinical decision | High | High | Automated freshness alerts; 12-month mandatory review | Gov Lead | Active |
| **R2** | Single point of failure (key curator leaves) | Medium | High | Backup curators; documented handoff; knowledge transfer | Gov Lead | Active |
| **R3** | Unreviewed COI biases recommendations | Low | High | Mandatory COI; independent review for declared COI | Gov Lead | Active |
| **R4** | Inconsistent evidence grading across curators | Medium | Medium | Standardized rubrics; methodology reviewer; calibration exercises | Method Reviewer | Active |
| **R5** | Breaking change breaks engine/validation | Low | Critical | Semantic versioning; parallel run; full regression | Val Engineer | Active |
| **R6** | Guideline conflict (KDIGO vs ERA) not resolved | Medium | Medium | Explicit disagreement documentation; consensus process | Gov Lead | Active |
| **R7** | Validation library drifts from clinical reality | Medium | High | Monthly literature surveillance; quarterly case refresh | Val Engineer | Active |
| **R8** | Data privacy breach in case library | Low | Critical | De-identification pipeline; IRB oversight; access logging | Data Steward | Active |
| **R9** | Orphan knowledge objects undetected | Medium | Medium | Weekly automated scan; monthly manual review | Gov Lead | Active |
| **R10** | Engine reasoning not explainable | Low | High | Explainability layer mandatory; test coverage | Val Engineer | Active |

---

## 10. Compliance and Accreditation

### 10.1 Standards Alignment

| Standard | Alignment Approach |
|---|---|
| **AMA GEC** | Governance framework mapped to GEC requirements |
| **NICE** | Evidence grading aligns with NICE methodology |
| **KDIGO** | Primary guideline source; update tracking |
| **FDA SaMD** | Documentation supports future regulatory submission |
| **ISO 80001** | Risk management for medical IT networks |
| **HIPAA/GDPR** | No PHI in knowledge objects; case library de-identified |

### 10.2 Audit Trail Requirements

Every object change MUST log:
- Timestamp (UTC)
- User (authenticated)
- Action (create/update/transition/delete)
- Before/after values (JSON diff)
- Reason (free text + controlled vocabulary)
- Approver (for transitions)

Retention: 10 years minimum.

---

## 11. Implementation Roadmap

| Phase | Timeline | Deliverables |
|---|---|---|
| **Phase 1: Foundation** | Months 1-2 | Governance framework approved; RACI assigned; templates created; COI registry live |
| **Phase 2: Workflow Automation** | Months 3-4 | Review workflow in system; automated checks in CI/CD; versioning engine |
| **Phase 3: Evidence Grading** | Months 4-5 | Grading rubrics implemented; evidence tables mandatory |
| **Phase 4: Validation Integration** | Months 5-6 | Validation library governed; test suite in CI/CD |
| **Phase 5: Dashboard & Monitoring** | Months 6-7 | Quality dashboard live; alerting configured |
| **Phase 6: External Readiness** | Months 8-9 | Audit documentation; external auditor engaged |
| **Phase 7: Steady State** | Month 10+ | Monthly ops; quarterly reviews; annual audit |

---

## 12. Appendices

### Appendix A: Object Authoring Templates

Each object type has a standardized YAML template with:
- Required fields (validated)
- Optional fields
- Controlled vocabulary references
- Example completed object

### Appendix B: Reviewer Checklists

**Methodology Reviewer Checklist:**
- [ ] Evidence grading correct (GRADE/Oxford)
- [ ] Study quality assessed (RoB tool)
- [ ] Bias/confounding evaluated
- [ ] Applicability to target population
- [ ] Grade matches evidence strength
- [ ] Guideline quote accurate and cited

**Clinical Reviewer Checklist:**
- [ ] Clinical facts accurate
- [ ] Recommendations align with guidelines
- [ ] Safety considerations addressed
- [ ] Dosing/renal adjustments correct
- [ ] Monitoring parameters appropriate
- [ ] Patient populations correctly specified

### Appendix C: Escalation Path

```
Author → Disease Curator → Governance Lead → Clinical Advisory Board → Executive Sponsor
```

### Appendix D: Glossary

| Term | Definition |
|---|---|
| **Knowledge Object** | Any reusable clinical entity (disease, syndrome, drug, pathology, etc.) |
| **Edge** | Relationship between two knowledge objects |
| **Provenance** | Complete history of object creation, review, modification |
| **Superseded** | Object replaced by newer version but retained for reference |
| **Archived** | Object removed from engine, retained for audit |
| **RACI** | Responsible, Accountable, Consulted, Informed |

---

## 13. Sign-Off

| Role | Name | Signature | Date |
|---|---|---|---|
| Governance Lead | | | |
| Clinical Director | | | |
| Chief Medical Informatics Officer | | | |
| Quality Assurance Lead | | | |

---

**End of Document**  
**Next Review:** 2026-10-10  
**Governance Lead:** Knowledge Governance Team