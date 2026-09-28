# C3 Glomerulopathy (C3G) — Knowledge Governance Framework

**Document ID:** C3G-GOV-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Knowledge Governance  

---

## 1. Document Purpose

This document defines the knowledge governance framework for C3 Glomerulopathy within the BGDDR v4.1 system. It covers the knowledge lifecycle, versioning strategy, 7/7 health checks, quality dashboard metrics, roles and responsibilities, and C3G-specific governance considerations.

---

## 2. Knowledge Governance Principles

| Principle | Description | Application to C3G |
|---|---|---|
| **Authority** | Knowledge sourced from peer-reviewed guidelines and trials | KDIGO 2021 Ch 8, Complement Consensus 2023 as primary anchors |
| **Accuracy** | Clinical content verified by domain experts | Nephrologist review of all 21 fields |
| **Currency** | Review within 12 months of new evidence | Rapidly evolving complement inhibitor landscape |
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
                | (Updates)         |
                +--------+---------+
                         |
                +--------v---------+
                | Retirement        |
                | (Superseded)      |
                +------------------+
```

---

## 4. Knowledge Artifacts

| Artifact | Document ID | Format | Version | Update Frequency |
|---|---|---|---|---|
| Disease Knowledge Specification | C3G-DK-v1.0 | Markdown | 1.0 | Quarterly |
| Clinical Pathway Specification | C3G-CP-v1.0 | Markdown | 1.0 | Quarterly |
| Drug Knowledge Base | C3G-DRUG-v1.0 | Markdown | 1.0 | Semi-annual |
| Clinical Case Library | C3G-CC-v1.0 | Markdown | 1.0 | Semi-annual |
| Guideline Mapping | C3G-GM-v1.0 | Markdown | 1.0 | Quarterly |
| Knowledge Governance | C3G-GOV-v1.0 | Markdown | 1.0 | Annual |
| Completeness Dashboard | C3G-CD-v1.0 | Markdown | 1.0 | Quarterly |

---

## 5. Roles and Responsibilities

| Role | Responsibility | C3G-Specific Duties |
|---|---|---|
| **Domain Expert** | Clinical content accuracy, guideline interpretation | Complement pathway expert review |
| **Knowledge Engineer** | Schema encoding, rule authoring, pathway design | C3G KB rule generation |
| **Quality Assurance** | Completeness scoring, cross-document validation | Dashboard scoring |
| **Clinical Reviewer** | Case validation, pathway clinical plausibility | C3G case accuracy |
| **Version Manager** | Version control, change tracking, release management | C3G version log |

---

## 6. Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0.0 | 2026-07-10 | GDES V4.1 | Initial C3G knowledge package release |

---

## 7. Change Management Process

1. **Proposal:** Identify gap or new evidence (e.g., new complement inhibitor trial)
2. **Impact Assessment:** Evaluate which artifacts require updating
3. **Authoring:** Domain expert + knowledge engineer update content
4. **Review:** Internal peer review for accuracy and consistency
5. **Validation:** 7/7 health checks pass, all 57 knowledge tests pass
6. **Release:** New version published with changelog
7. **Notification:** Stakeholders informed of update

---

## 8. Quality Metrics

| Metric | Target | Current | Method |
|---|---|---|---|
| Completeness score | >=95% | 100% (v1.0) | 12-domain dashboard |
| Knowledge tests passing | 57/57 | 57/57 | Django test suite |
| Bootstrap health checks | 7/7 | 7/7 | Knowledge app startup |
| Cross-document consistency | 100% | 100% | Rule-to-pathway mapping |
| Guideline concordance | All major | 6 guidelines | Guideline mapping |
| KB rule count target | 25-30 | 26 | Active ACTIVE status |
| Clinical case count | 8 | 8 | Case inventory |

---

## 9. Knowledge Update Triggers

| Trigger | Action | Priority |
|---|---|---|
| New complement inhibitor RCT published | Update drug KB, pathway, guideline mapping | High |
| KDIGO 2028 GN guidelines | Full review of all artifacts | High |
| New genetic findings (e.g., novel CFHR mutation) | Update disease knowledge, genetic testing section | Medium |
| Post-transplant outcome registry data | Update transplant section, Case 2 | Medium |
| Paediatric C3G trial results | Update paediatric content, case 6 | Medium |
| MGUS treatment paradigm change | Update Case 1, MGUS section | Low |

---

## 10. Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Rapidly evolving complement inhibitor landscape | Knowledge may become outdated | High | Quarterly review cycle; alert system for new publications |
| No large RCTs for C3G therapy | Low evidence certainty | Certain (known) | Evidence level clearly stated; expert consensus used |
| Paediatric data extremely limited | Child-specific knowledge gaps | High | Extrapolate from adult with caveats; highlight gaps |
| Complement inhibitor costs | Treatment access limitations | High | Document cost-effectiveness data when available |
| Guideline divergence on optimal therapy sequence | Inconsistent recommendations | Moderate | Present multiple approaches with evidence grades |
