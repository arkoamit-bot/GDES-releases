# GDES Claude Code Review Request

**Version:** 6.5 Release Candidate
**Date:** 2026-07-11
**Purpose:** Request independent architecture and clinical review before pilot

---

## 1. Review Scope

This document requests a comprehensive review of GDES Version 6.5 Release Candidate across 6 domains:

1. Architecture review
2. Domain model review
3. Code quality review
4. Maintainability review
5. Security review
6. Clinical workflow review

---

## 2. Architecture Review

### 2.1 System Overview

- Clean Architecture + DDD pattern
- 30+ Django apps, 72 models
- Primary reasoning engine: `clinical_reasoning/services/engine.py`
- Knowledge base: 209 rules across 18 diseases (`KnowledgeBaseEntry` model)
- Legacy engine deprecated: `decision/services.py` `evaluate_case()`

### 2.2 Key Files to Review

| File | Description |
|---|---|
| `clinical_reasoning/services/engine.py` | Primary reasoning pipeline |
| `clinical_reasoning/services/management_plan.py` | Treatment protocols (9 diseases) |
| `clinical_reasoning/services/monitoring_plan.py` | Monitoring protocols (9 diseases) |
| `clinical_reasoning/services/followup_scheduler.py` | DEPRECATED, duplicate of `followup/` app |
| `clinical_reasoning/services/investigation_engine.py` | Investigation recommendations |
| `clinical_reasoning/services/drug_toxicity.py` | Drug toxicity detection |
| `clinical_reasoning/services/treatment_failure.py` | Treatment failure detection |
| `clinical_reasoning/services/disease_validation.py` | Disease validation framework |
| `clinical_reasoning/views.py` | API endpoints |
| `knowledge/models.py` | `KnowledgeBaseEntry`, `RecommendationAudit`, `RuleReview`, etc. |
| `knowledge/views.py` | Governance dashboard endpoint |
| `knowledge/admin.py` | Admin configuration |
| `decision/services.py` | LEGACY, deprecated `evaluate_case()` |

### 2.3 Questions for Architecture Review

1. Is the Clean Architecture separation clean? Are there violations?
2. Is the reasoning engine pipeline well-structured?
3. Are there circular dependencies between apps?
4. Is the `KnowledgeBaseEntry` model over-loaded with governance fields?
5. Should `RecommendationAudit` be a separate app?
6. Is the 7-state lifecycle appropriate?

---

## 3. Domain Model Review

### 3.1 Clinical Models

- `Patient`, `ClinicalEncounter`, `ClinicalProfile`, `ClinicalInsight`
- `LabResult`, `LabTest`, `Prescription`, `Treatment`
- `FollowUpTask`, `ScheduledVisit`
- `KnowledgeBaseEntry` (209 rules)

### 3.2 Questions for Domain Review

1. Is the `Patient` model complete for nephrology?
2. Are the disease models appropriate?
3. Is `ClinicalProfile` the right aggregation root?
4. Are there missing domain events?
5. Is the knowledge graph (nodes/edges) well-modeled?

---

## 4. Code Quality Review

### 4.1 Test Coverage

- 180 pytest tests, all passing
- Tests in `tests/` directory
- `conftest.py` with `DJANGO_SETTINGS_MODULE`

### 4.2 Questions for Code Quality

1. Are there any code smells or anti-patterns?
2. Is error handling consistent?
3. Are there any race conditions?
4. Is the code following Django/DRF best practices?
5. Are there any N+1 query issues?

---

## 5. Maintainability Review

### 5.1 Questions

1. How easy is it to add a new disease?
2. How easy is it to add a new clinical rule?
3. How easy is it to modify monitoring protocols?
4. Is the codebase well-documented?
5. Are there adequate inline comments?

---

## 6. Security Review

### 6.1 Questions

1. Are there any SQL injection risks?
2. Is authentication/authorization properly implemented?
3. Are there any XSS vulnerabilities?
4. Is patient data properly protected?
5. Are API endpoints properly secured?
6. Are there any secret/key exposure risks?

---

## 7. Clinical Workflow Review

### 7.1 Patient Journey (16 Steps Per Disease)

1. Patient registration
2. Initial labs
3. Differential diagnosis
4. Disease validation
5. Management plan generation
6. Monitoring plan generation
7. Investigation recommendations
8. Follow-up scheduling
9. Drug toxicity monitoring
10. Treatment failure detection
11. Relapse detection
12. Disease trajectory assessment
13. Care gap detection
14. Explainability review
15. Clinical override
16. Outcome tracking

### 7.2 Questions for Clinical Review

1. Is the clinical reasoning logic sound?
2. Are the treatment protocols evidence-based?
3. Are the monitoring intervals appropriate?
4. Is the override mechanism sufficient?
5. Are there any patient safety risks?
6. Is the governance framework adequate for clinical use?

---

## 8. Specific Review Requests

### 8.1 High Priority

1. Review `engine.py` for correctness of the reasoning pipeline
2. Review `management_plan.py` for clinical accuracy of treatment protocols
3. Review `monitoring_plan.py` for appropriateness of monitoring intervals
4. Review `knowledge/models.py` for schema design quality
5. Review the `RecommendationAudit` model for completeness

### 8.2 Medium Priority

1. Review the legacy engine deprecation approach
2. Review the knowledge governance dashboard
3. Review the API endpoint design
4. Review the test suite for completeness

### 8.3 Low Priority

1. Review the documentation quality
2. Review the deployment guide
3. Review the admin configuration

---

## 9. Files to Review

| File | Description |
|---|---|
| `clinical_reasoning/services/engine.py` | Primary reasoning pipeline — orchestrates the full clinical reasoning flow |
| `clinical_reasoning/services/management_plan.py` | Treatment protocol definitions and generation for 9 diseases |
| `clinical_reasoning/services/monitoring_plan.py` | Monitoring protocol definitions and generation for 9 diseases |
| `clinical_reasoning/services/followup_scheduler.py` | Deprecated — duplicates functionality in the `followup/` app |
| `clinical_reasoning/services/investigation_engine.py` | Lab and imaging investigation recommendations |
| `clinical_reasoning/services/drug_toxicity.py` | Drug toxicity detection and alerting logic |
| `clinical_reasoning/services/treatment_failure.py` | Treatment failure detection and escalation logic |
| `clinical_reasoning/services/disease_validation.py` | Disease validation and confirmation framework |
| `clinical_reasoning/views.py` | DRF API endpoints for reasoning engine |
| `knowledge/models.py` | Core knowledge models: `KnowledgeBaseEntry`, `RecommendationAudit`, `RuleReview` |
| `knowledge/views.py` | Knowledge governance dashboard API endpoint |
| `knowledge/admin.py` | Django admin configuration for knowledge models |
| `decision/services.py` | Legacy engine — deprecated `evaluate_case()` function |
| `patients/models.py` | Patient, ClinicalEncounter, ClinicalProfile, ClinicalInsight models |
| `labs/models.py` | LabResult, LabTest models |
| `prescriptions/models.py` | Prescription, Treatment models |
| `followup/models.py` | FollowUpTask, ScheduledVisit models |
| `tests/` | Test suite — 180 pytest tests |
| `tests/conftest.py` | Test configuration with `DJANGO_SETTINGS_MODULE` |

---

## 10. Contact

- **Project:** GDES (Glomerular Disease Expert System)
- **Version:** 6.5 Release Candidate RC1
- **Date:** 2026-07-11
- **Status:** Ready for review
