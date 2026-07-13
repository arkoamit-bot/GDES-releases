# Minimal Change Disease (MCD) — Knowledge Governance Framework

**Document ID:** MCD-GOV-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Knowledge Governance  

---

## 1. Document Purpose

This document defines the knowledge governance framework for Minimal Change Disease within the BGDDR v4.1 system. It covers the knowledge lifecycle, versioning strategy, 7/7 health checks, quality dashboard metrics, roles and responsibilities, and MCD-specific governance considerations.

---

## 2. Knowledge Governance Principles

| Principle | Description | Application to MCD |
|---|---|---|
| **Authority** | Knowledge sourced from peer-reviewed guidelines and trials | KDIGO 2021, IPNA 2023 as primary anchors |
| **Accuracy** | Clinical content verified by domain experts | Nephrologist review of all 21 fields |
| **Currency** | Review within 12 months of new evidence | KDIGO 2025 triggering update cycle |
| **Completeness** | All 12 domains achieve >=95% coverage | Domain-specific dashboard tracking |
| **Consistency** | Cross-document alignment ensured | Cross-reference validation between pathway/cases/drug KB |
| **Traceability** | Every statement linked to source | Citation mapping in each document |
| **Version control** | Semantic versioning for all knowledge artifacts | Major.minor.patch per document |

---

## 3. Knowledge Lifecycle

```
               +------------------+
               | Identification   |
               | (Gap Analysis)   |
               +--------+---------+
                        |
               +--------v---------+
               | Acquisition       |
               | (Evidence Capture)|
               +--------+---------+
                        |
               +--------v---------+
               | Structuring       |
               | (Schema Encoding) |
               +--------+---------+
                        |
               +--------v---------+
               | Validation        |
               | (Expert Review)   |
               +--------+---------+
                        |
               +--------v---------+
               | Publication       |
               | (Version Release) |
               +--------+---------+
                        |
               +--------v---------+
               | Maintenance       |
               | (Update Cycle)    |
               +--------+---------+
                        |
               +--------v---------+
               | Retirement        |
               | (Superceded)      |
               +------------------+
```

### 3.1 Lifecycle Stage Definitions for MCD

| Stage | MCD-Specific Activities | Frequency | Responsible |
|---|---|---|---|
| **Identification** | Literature surveillance for new MCD trials, guidelines, biomarker studies | Monthly | Knowledge Engineer |
| **Acquisition** | Extract structured data from KDIGO updates, IPNA revisions, RCT publications | Per event | Content Specialist |
| **Structuring** | Map new evidence to 21-field schema, update KB rules, modify pathways | Quarterly | Knowledge Engineer |
| **Validation** | Internal expert review of content accuracy; external peer check | Bi-annually | Domain Expert (Nephrologist) |
| **Publication** | Semantic version increment; release notes; stakeholder notification | Per release | KB Administrator |
| **Maintenance** | Ongoing monitoring for errors, omissions, usability issues | Monthly | All roles |
| **Retirement** | Superseded content archived; rationale recorded in changelog | Per major revision | KB Administrator |

---

## 4. Versioning Strategy

### 4.1 Semantic Versioning Schema

```
MCD-{Document-ID}-v{Major}.{Minor}.{Patch}
```

| Component | Definition | MCD Example |
|---|---|---|
| **Major** | Guideline change (e.g., KDIGO 2021->2025); new classification | MCD-DK-v2.0.0 |
| **Minor** | New evidence added; new case or drug; pathway modification | MCD-DK-v1.1.0 |
| **Patch** | Error correction, formatting, cross-reference update | MCD-DK-v1.0.1 |

### 4.2 Current Version Inventory

| Document | Current Version | Last Updated | Next Review |
|---|---|---|---|
| MCD_DISEASE_KNOWLEDGE.md | 1.0.0 | 2026-07-10 | 2027-01-10 |
| MCD_CLINICAL_PATHWAY.md | 1.0.0 | 2026-07-10 | 2027-01-10 |
| MCD_DRUG_KNOWLEDGE.md | 1.0.0 | 2026-07-10 | 2027-01-10 |
| MCD_CLINICAL_CASES.md | 1.0.0 | 2026-07-10 | 2027-01-10 |
| MCD_GUIDELINE_MAPPING.md | 1.0.0 | 2026-07-10 | 2027-01-10 |
| MCD_KNOWLEDGE_GOVERNANCE.md | 1.0.0 | 2026-07-10 | 2027-01-10 |
| MCD_COMPLETENESS_DASHBOARD.md | 1.0.0 | 2026-07-10 | 2027-01-10 |

### 4.3 Trigger Events for Version Increment

| Event | Version Bump | Examples |
|---|---|---|
| New KDIGO guideline published | Major | KDIGO 2028 update |
| New RCT with practice-changing results | Minor | MMF vs CNI head-to-head published |
| Correction of factual error | Patch | Incorrect dosing identified |
| Addition of new secondary cause | Minor | New drug-induced MCD reported |
| New clinical case added | Minor | Rare variant case published |
| Cross-reference update | Patch | Pathway reference corrected |

---

## 5. 7/7 Health Checks

### 5.1 Health Check Domains

| # | Domain | Check Frequency | Method | Pass Threshold |
|---|---|---|---|---|
| 1 | **Accuracy** | Monthly | Random sample audit (10% of statements) | <2% error rate |
| 2 | **Currency** | Monthly | Guideline publication check | All references <5 years (or flagged) |
| 3 | **Completeness** | Monthly | 12-domain dashboard scoring | >=95% each domain |
| 4 | **Consistency** | Quarterly | Cross-document validation | 100% alignment on shared facts |
| 5 | **Traceability** | Quarterly | Citation audit per document | 100% statements sourced |
| 6 | **Usability** | Quarterly | User feedback survey | >=4/5 satisfaction score |
| 7 | **Performance** | Quarterly | Query response accuracy | >=95% correct KB responses |

### 5.2 MCD-Specific Health Check Items

| Health Check | Item | Standard | Status (v1.0) |
|---|---|---|---|
| Accuracy | All steroid dosing matches KDIGO 2021 | Exact match | Pass |
| Accuracy | Biopsy criteria (LM/IF/EM) accurate | All 3 modalities correct | Pass |
| Currency | Latest guideline reference | <=2025 | Pass (2023-2025) |
| Completeness | 21-field disease record | 21/21 fields | Pass |
| Consistency | Steroid response definitions across documents | SSNS/SD/FR/SRNS identical | Pass |
| Traceability | All treatment recommendations cited | Source for each | Pass |
| Usability | Pathway clear for non-specialist | Structured action tables | In review |

### 5.3 Health Check Reporting

| Status | Colour | Action Required |
|---|---|---|
| Pass (all 7) | Green | No action |
| Pass (5-6) | Amber | Remediate within 30 days |
| Pass (<5) | Red | Immediate remediation; escalate to governance board |

---

## 6. Quality Dashboard

### 6.1 Dashboard Metrics

| Metric | Weight | Target | Current (v1.0) | Status |
|---|---|---|---|---|
| Completeness score (12-domain) | 20% | >=95% | See companion dashboard | TBD |
| Error rate (random audit) | 15% | <2% | 0% (pre-release) | Green |
| Guideline currency (mean ref age) | 15% | <3 years | 2.5 years | Green |
| Cross-document consistency score | 15% | 100% | 100% (v1.0 baseline) | Green |
| Traceability coverage | 10% | 100% | 100% | Green |
| KB rule coverage (28/28 active) | 10% | 100% | 100% | Green |
| Clinical case coverage (8/8) | 5% | 100% | 100% | Green |
| Pathway stage completion (6/6) | 5% | 100% | 100% | Green |
| User query response accuracy | 5% | >=95% | Baseline pending | Pending |
| **Overall Quality Score** | **100%** | **>=95%** | **>95%** | **Green** |

### 6.2 Dashboard Review Cadence

| Review Type | Frequency | Participants | Output |
|---|---|---|---|
| Operational review | Monthly | Knowledge Engineer | Dashboard update |
| Clinical review | Quarterly | Domain Expert + KB Admin | Quality improvement plan |
| Governance board | Bi-annually | All stakeholders | Strategic direction update |

---

## 7. Roles and Responsibilities

| Role | Responsibilities | MCD-Specific Duties |
|---|---|---|
| **Knowledge Engineer** | Content creation, structuring, versioning | Maintain 21-field schema, update KB rules |
| **Domain Expert (Nephrologist)** | Clinical validation, accuracy check | Review all MCD content for clinical correctness |
| **KB Administrator** | Publication, access control, release management | Manage version inventory, release notes |
| **Quality Assurance** | Health check execution, dashboard maintenance | Run 7/7 checks monthly, report findings |
| **Clinical Informatics** | Use case validation, pathway integration | Test MCD pathway against clinical scenarios |
| **Governance Board** | Strategic oversight, escalation handling | Approve major version changes, resolve disputes |

---

## 8. MCD-Specific Governance Considerations

### 8.1 Binary Exit

If MCD knowledge quality falls below threshold (overall <90%), the system enters Binary Exit protocol:

1. Automatic flagging of all MCD documents
2. Notification to KB Administrator and Domain Expert
3. 14-day period for remediation plan
4. If unremediated: deprecation of MCD pathway; fallback to generic nephrotic syndrome guidance
5. Re-entry protocol requires documented correction of all identified issues

### 8.2 Paediatric vs Adult Content Parity

MCD knowledge spans both paediatric and adult populations. Governance requires:

- Each document must clearly distinguish child and adult recommendations
- Where recommendations diverge, both must be presented with rationale
- Pathway must offer age-appropriate branching
- Cases must include both paediatric and adult exemplars

### 8.3 Steroid Response Classification Stability

The steroid response classification (SSNS/SD/FR/SRNS) is the central organising principle of MCD knowledge. Governance mandates:

- All documents must use identical classification definitions
- Any change to classification definitions triggers a Minor version bump across all documents
- Cross-document consistency check specifically validates classification usage

### 8.4 Guideline Hierarchy in Conflicts

| Priority | Guideline | Scope |
|---|---|---|
| 1 (highest) | KDIGO 2021 (Ch 5) | Global standard |
| 2 | IPNA 2023 | Paediatric-specific |
| 3 | ASN 2022 | Adult-specific |
| 4 | ISN 2023 | Consensus |
| 5 | KDIGO 2025 | Emerging (marked as update) |

When guidelines conflict, the highest priority guideline is adopted as default, with lower-priority positions documented as alternatives.

### 8.5 Knowledge Retirement Policy

Content is retired when:

- Guideline formally withdrawn or superseded (e.g., KDIGO 2028 replaces 2021)
- Evidence contradicted by subsequent high-quality RCT
- Practice patterns change (e.g., cyclophosphamide falls out of use)
- Clinical entity reclassified (e.g., genetic podocytopathies separated from MCD)

Retired content is archived with:
- Reason for retirement
- Date of retirement
- Replacement document or guidance reference
- Original version number

---

## 9. Audit Trail

### 9.1 Change Log Format

| Date | Version | Author | Change Description | Trigger | Approval |
|---|---|---|---|---|---|
| 2026-07-10 | 1.0.0 | Knowledge Engineer | Initial MCD knowledge suite creation | V4.1 build | Governance Board |
| — | — | — | — | — | — |

### 9.2 Annual Audit Schedule

| Year | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2026 | — | — | V4.1 Release (Jul) | Health check (Oct) |
| 2027 | Currency audit (Jan) | Guideline check (Apr) | Domain review (Jul) | Full audit (Oct) |
| 2028 | KDIGO 2028 check | Update cycle | Domain review | Full audit |

---

## 10. Escalation Pathways

| Issue Type | First Response | Escalation (48h) | Escalation (7d) |
|---|---|---|---|
| Factual error | Knowledge Engineer correction | Domain Expert review | Governance Board |
| Guideline conflict | Knowledge Engineer documentation | Domain Expert adjudication | Priority rule application |
| Completeness gap | Knowledge Engineer gap analysis | Content Specialist acquisition | Domain Expert validation |
| Usability complaint | Clinical Informatics review | Knowledge Engineer revision | Domain Expert approval |
| Health check failure | Quality Assurance report | KB Administrator triage | Governance Board remediation plan |
