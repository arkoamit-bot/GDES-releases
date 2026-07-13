# Knowledge Integration Report

## Knowledge Base Architecture

### Models
| Model | Purpose | Key Fields |
|---|---|---|
| `GuidelineSource` | Clinical guideline metadata | abbreviation, version_year, url |
| `KnowledgeBaseEntry` | Individual clinical rule | entry_id, disease_id, rule_data (JSON), evidence_grade, status, guideline_chapter/paragraph/quote |
| `KnowledgeBaseVersion` | Version history for rules | version_number, rule_data, rule_data_diff, change_summary |
| `RuleTemplate` | Condition template schemas | template_id, category, condition_schema (JSON Schema) |
| `RuleReview` | Approval workflow | status, reviewer, review_notes |
| `RuleTestResult` | Rule test outcomes | matched, expected_score, actual_score, test_input, test_output |
| `GuidelineDocument` | Imported guideline documents | document_type, content, parsed_rules |
| `EvidenceEntry` | Evidence/literature references | evidence_level, doi, pmid, summary |

Source: `knowledge/models.py`

### Integration Points

#### 1. Clinical Reasoning Pipeline
```
engine.py:34  → extract_patient_features(patient)   [knowledge/services.py]
engine.py:35  → evaluate_patient_rules(patient)       [knowledge/services.py]
```

- `extract_patient_features(patient)` (knowledge/services.py): Reads Patient model fields + related lab/biopsy data; returns feature dict with proteinuria, albumin, sediment, eGFR trend, age_group, disease_phase, lab findings, biopsy findings
- `evaluate_patient_rules(patient)` (knowledge/services.py): Evaluates all ACTIVE KnowledgeBaseEntry rules against extracted features; returns DiseaseScore dataclass sorted by total_score
- `evaluate_entry(entry, features)`: Evaluates a single rule's conditions against features; supports 11 operators (eq, neq, contains, not_contains, gt, gte, lt, lte, in, exists, not_exists)

#### 2. Decision Engine
```
decision/views.py  →  evaluate case  →  knowledge rules for traceability
```

DecisionResult stores `traceability` (list of KB entries applied), enabling audit of AI recommendations.

#### 3. Explainability
```
explainability.py:96  → _extract_matched_rules(differential)  → top-3 matched rules
explainability.py:108 → _extract_guideline_support(differential) → unique guideline sources
explainability.py:120 → _assess_evidence_quality(differential) → grade distribution
```

### Knowledge Quality Framework

#### Rule Scoring (`knowledge_quality.py:13`)
Quality dimensions (0-100):
| Dimension | Method | Weight |
|---|---|---|
| Completeness | disease_id + source + evidence_grade + conditions + explanation | 25% |
| Clarity | explanation length + conditions count + weight presence | 25% |
| Evidence | evidence_grade mapping (1=100, 2=75, OP=50, NG=25) | 25% |
| Testability | condition field + operator presence | 25% |

Grade mapping: A ≥85, B ≥70, C ≥50, D <50

#### Conflict Detection (`knowledge_quality.py:103`)
Pairs of ACTIVE rules for same disease checked for contradictory conditions:
- `eq` vs `neq`, `gt` vs `lt`, `exists` vs `not_exists`
- Returns list of conflict dicts with severity "medium"

#### Coverage Analysis (`knowledge_quality.py:163`)
Reports: total_rules, unique_diseases, unique_sources, rules per disease/source/grade

### Gaps & Recommendations

1. **No rule calibration workflow**: Scores are static; no mechanism to adjust weights based on clinical validation results
2. **Conflict detection is field-level only**: Two rules with `proteinuria > 3.5` and `proteinuria < 3.0` are flagged as conflict even if context differs (e.g., different disease)
3. **No rule retirement automation**: KnowledgeBaseEntry has `retired_date` field but no automated retirement based on guideline version changes
4. **RuleTemplate condition_schema not enforced**: Templates define JSON Schema but `KnowledgeBaseEntry.rule_data` is free-form JSON
5. **EvidenceEntry not linked to Explainability**: Evidence references aren't surfaced in explainability reports
