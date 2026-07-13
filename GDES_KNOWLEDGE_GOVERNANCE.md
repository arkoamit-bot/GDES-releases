# GDES Knowledge Governance

**Version:** 6.5 Release Candidate  
**Date:** 2026-07-11

---

## 1. Knowledge Base Overview

The GDES clinical decision support engine is driven by a structured knowledge base of **209 rules** spanning **18 glomerular and tubulointerstitial diseases**.

### Core Diseases (9) — Full Clinical Decision Support

| Disease | ID |
|---|---|
| IgA Nephropathy | IgAN |
| Membranous Nephropathy | MN |
| Focal Segmental Glomerulosclerosis | FSGS |
| Minimal Change Disease | MCD |
| Lupus Nephritis | LN |
| ANCA-Associated Vasculitis | AAV |
| Anti-GBM Disease | anti-GBM |
| Infection-Related GN | infection_related_gn |
| C3 Glomerulopathy | c3glomerulopathy |

### Additional Diseases (9) — Basic Profiles

| Disease | ID |
|---|---|
| Diabetic Nephropathy | diabetic_nephropathy |
| Hypertensive Nephrosclerosis | hypertensive_nephrosclerosis |
| Acute Interstitial Nephritis | acute_interstitial_nephritis |
| Acute Tubular Necrosis | ATN |
| Thrombotic Microangiopathy | TMA |
| Light Chain Cast Nephropathy | light_chain_cast_nephropathy |
| Fibrillary GN | fibrillary_gn |
| Amyloidosis | amyloidosis |
| Diabetic Nephropathy with GN | diabetic_nephropathy_with_gn |

---

## 2. Rule Structure

Each rule is stored as a `KnowledgeBaseEntry` with the following fields:

| Field | Description |
|---|---|
| `entry_id` | Unique identifier (e.g. `KB-IGA-001`) |
| `disease_id` | FK to the disease model |
| `rule_data` | JSON blob: conditions, weights, explanations |
| `source` | FK to `GuidelineSource` |
| `evidence_grade` | `1` (strong), `2` (moderate), `NG` (no grade), `OP` (expert opinion) |
| `rule_type` | `diagnostic`, `treatment`, `monitoring`, `referral`, `prognostic`, `exclusion` |
| `status` | 7-state lifecycle: draft → under_review → approved → active → superseded → archived → retired |
| `effective_date` | Date the rule becomes effective |
| `retired_date` | Date the rule was retired (if applicable) |
| `tags` | Categorical tags for filtering |
| `review_notes` | Free-text notes from reviewers |
| `guideline_chapter` | Chapter reference within the source guideline |
| `guideline_paragraph` | Paragraph reference within the source guideline |
| `guideline_quote` | Verbatim quote from the guideline text |
| `evidence_url` | URL to the supporting evidence |
| `author` | Person or entity that authored the rule |
| `approved_by` | Person or entity that approved the rule |
| `approved_at` | Timestamp of approval |
| `next_review_date` | Scheduled date for next review |
| `confidence_score` | Numeric confidence (0.0–1.0) |
| `explanation` | Human-readable explanation of the rule's rationale |
| `override_allowed` | Whether clinicians may override this rule |
| `recommendation_id` | ID linking to the source guideline recommendation |
| `knowledge_version` | Version string of the knowledge base at time of entry |
| `date_validated` | Date the rule was last validated |

### Rule Data JSON Structure

```json
{
  "conditions": [
    { "field": "serum_creatinine", "operator": ">=", "value": 1.5, "unit": "mg/dL" }
  ],
  "weights": { "treatment_efficacy": 0.85, "risk_level": 0.7 },
  "explanations": {
    "en": "Elevated creatinine warrants nephrology referral per KDIGO 2021."
  }
}
```

---

## 3. Guideline Sources

All knowledge base rules are linked to published clinical guidelines via `GuidelineSource` foreign keys.

| Guideline | Coverage |
|---|---|
| **KDIGO 2021** | IgAN, MN, FSGS, MCD, LN, AAV, anti-GBM |
| **KDIGO 2024 Updates** | Updated recommendations for IgAN, MN, C3 glomerulopathy |
| **Disease-Specific Guidelines** | JNC guidelines (hypertension), ADA standards (diabetes), ASH guidelines (TMA), amyloidosis consensus |

Each source record stores: title, authors, publication year, journal, DOI/PMID, version, and full-text reference.

---

## 4. Version Control

### KnowledgeBaseVersion Model

| Field | Description |
|---|---|
| `version_number` | Semver string (e.g. `6.5.0`) |
| `rule_data` | Full JSON snapshot of the knowledge base at this version |
| `rule_data_diff` | Computed diff against the previous version |
| `change_summary` | Human-readable summary of changes |
| `changed_by` | Author of the version |

### Behavior

- Every mutation to a `KnowledgeBaseEntry` creates a new `KnowledgeBaseVersion` record.
- Version history is tracked per entry, enabling per-rule rollback.
- `compute_diff` generates a structured diff between any two versions, showing added, modified, and retired rules.
- Restore/rollback: any prior version can be restored as the current active state.

---

## 5. Testing & Validation

### RuleTestResult

Each rule can be tested against known patient cases. `RuleTestResult` records:

| Field | Description |
|---|---|
| `entry_id` | FK to `KnowledgeBaseEntry` |
| `test_case_id` | Identifier of the patient test case |
| `expected_outcome` | What the rule should produce |
| `actual_outcome` | What the rule actually produced |
| `passed` | Boolean pass/fail |
| `timestamp` | When the test was executed |

### Validation Functions

| Function | Description |
|---|---|
| `validate_all` | Validates the JSON schema of every active `rule_data` entry |
| `test_all` | Runs all active rules against the full test case suite |
| `pass_rate_by_disease` | Aggregates pass rates per disease for dashboards |

---

## 6. Knowledge Graph

### Nodes (6 Types)

| Type | Description |
|---|---|
| `disease` | Glomerular and tubulointerstitial diseases |
| `symptom` | Clinical signs and symptoms |
| `lab_test` | Laboratory and imaging investigations |
| `treatment` | Therapeutic interventions |
| `complication` | Disease complications and sequelae |
| `guideline` | Published guideline references |

### Edges (8 Types)

| Type | Description |
|---|---|
| `causes` | Disease → symptom/complication |
| `treats` | Treatment → disease/symptom |
| `monitors` | Lab test → disease state |
| `contraindicates` | Treatment ⊘ treatment/condition |
| `associates` | Disease ↔ disease (comorbidity) |
| `progresses_to` | Disease stage → later stage |
| `requires` | Diagnosis → required test |
| `excludes` | Finding ⊘ alternative diagnosis |

### Graph Operations

| Operation | Description |
|---|---|
| `populate_from_models` | Auto-populates graph nodes and edges from existing Django models |
| `find_paths` | Traverses graph between two nodes to find clinical reasoning paths |
| `get_reasoning_chain` | Returns the step-by-step reasoning chain for a given clinical scenario |
| `get_differential` | Generates a differential diagnosis from a set of findings |
| `syndrome_match` | Pattern-matches a clinical presentation against known syndrome profiles |

---

## 7. Evidence Engine

### EvidenceEntry Model

| Field | Description |
|---|---|
| `title` | Publication title |
| `authors` | Author list |
| `journal` | Journal name |
| `year` | Publication year |
| `doi` | Digital Object Identifier |
| `pmid` | PubMed ID |
| `evidence_level` | GRADE level |

### Functions

| Function | Description |
|---|---|
| `grade_evidence` | Performs full GRADE assessment on an evidence entry |
| `suggest_evidence_grade` | Auto-suggests a GRADE level based on study design and type |
| `generate_citation` | Produces an APA-style citation from an `EvidenceEntry` |

---

## 8. Dashboard

### `GET /api/v1/knowledge-base/governance_stats/`

Returns aggregated governance statistics:

| Section | Metrics |
|---|---|
| **Status Breakdown** | Count of rules in each lifecycle state: draft, under_review, approved, active, superseded, archived, retired |
| **Disease Coverage** | Number of rules per disease |
| **Evidence Grade Distribution** | Count of rules by evidence grade (1, 2, NG, OP) |
| **Rule Type Distribution** | Count of rules by type (diagnostic, treatment, monitoring, referral, prognostic, exclusion) |
| **Governance Coverage** | Percentage of rules with: author, approved_by, confidence_score, explanation, recommendation_id, next_review_date |
| **Review Workflow** | Pending / approved / rejected counts and overall approval rate |
| **Override Statistics** | Count of rules where override is allowed vs. disallowed |
| **Recommendation Audit** | Approval status breakdown, override rate, average confidence score |
| **Version Activity** | Count of entries that have never been versioned |

---

## 9. Seed Data

`seed_knowledge_base.py` loads **209 rules** across all 18 diseases via a Django management command:

```bash
python manage.py seed_knowledge_base
```

Each seeded rule includes:

- `conditions` — clinical criteria (lab values, histology, clinical features)
- `weights` — scoring weights for treatment and risk
- `explanations` — human-readable rationale
- `evidence_grade` — linked to the supporting evidence
- `guideline_references` — chapter, paragraph, and verbatim quotes from source guidelines

Rules are idempotent: re-running the command updates existing entries rather than creating duplicates.

---

*End of document.*
