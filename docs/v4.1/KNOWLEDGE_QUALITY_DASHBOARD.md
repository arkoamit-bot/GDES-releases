# Knowledge Quality Dashboard
**Document ID:** GDES-V4.2-KQD-001
**Version:** 1.0
**Date:** 2026-07-10
**Status:** Final
**Domain:** Knowledge Quality Metrics

---

## 1. Dashboard Purpose

This dashboard replaces the V4.1 per-disease completeness dashboards with a unified, cross-disease quality measurement framework. It measures the *ecosystem health* of the knowledge graph — connectivity, traceability, freshness, and clinical utility — not just per-disease field completion.

---

## 2. Quality Dimensions (12 Domains)

| Domain | Code | Description | Weight | Measurement Method |
|---|---|---|---|---|
| **D1: Disease Coverage** | `disease_coverage` | % of 23 baseline diseases with complete knowledge objects | 10% | Automated schema validation |
| **D2: Knowledge Graph Connectivity** | `graph_connectivity` | Cross-disease edges per node; orphan node ratio | 12% | Graph traversal analysis |
| **D3: Evidence Quality** | `evidence_quality` | % edges with evidence grade ≥2B; citation completeness | 12% | Edge property audit |
| **D4: Guideline Traceability** | `guideline_traceability` | % treatment edges linked to guideline source | 10% | Edge property audit |
| **D5: Clinical Validation** | `clinical_validation` | Case pass rates; explainability fidelity | 15% | Test suite execution |
| **D6: Differential Diagnosis Coverage** | `ddx_coverage` | Syndrome-disease mapping completeness; decision tree coverage | 8% | Graph query audit |
| **D7: Drug Knowledge Completeness** | `drug_completeness` | % drugs with full 16-field profile; renal dosing tables | 7% | Drug model validation |
| **D8: Monitoring Protocol Coverage** | `monitoring_coverage` | % disease-drug pairs with monitoring protocol | 6% | Protocol linkage audit |
| **D9: Complication Knowledge** | `complication_coverage` | Disease-complication edges with risk factors/prevention | 5% | Complication model validation |
| **D10: Pathology & Lab Reusability** | `pathology_lab_reusability` | Pathology/lab entities linked to ≥3 diseases | 5% | Reusability index |
| **D11: Knowledge Freshness** | `freshness` | % edges reviewed <12 months; guideline currency | 5% | Date audit |
| **D12: Governance Compliance** | `governance_compliance` | Author/reviewer attribution; COI declarations; version control | 5% | Metadata audit |

**Total Weight: 100%**

---

## 3. Metric Definitions and Scoring

### D1: Disease Coverage

```python
def score_disease_coverage():
    required_diseases = 23
    complete_diseases = 0
    for disease in Disease.objects.filter(is_active=True):
        if all_disease_fields_populated(disease) \
           and disease.kb_rules.filter(status='active').count() >= 25 \
           and disease.pathways.count() == 6 \
           and disease.cases.filter(is_gold_standard=True).count() >= 8:
            complete_diseases += 1
    return complete_diseases / required_diseases
```

**Target:** 1.0 (23/23)  
**Pass Threshold:** 0.95 (22/23)

### D2: Knowledge Graph Connectivity

```python
def score_graph_connectivity():
    G = build_knowledge_graph()
    total_nodes = G.number_of_nodes()
    total_edges = G.number_of_edges()
    
    # Orphan detection
    orphans = [n for n in G.nodes() if G.degree(n) < 2]
    orphan_ratio = len(orphans) / total_nodes
    
    # Cross-disease connectivity
    cross_disease_edges = sum(1 for u,v in G.edges() 
                              if G.nodes[u].get('type') == 'disease' 
                              and G.nodes[v].get('type') == 'disease')
    avg_cross_connections = cross_disease_edges / len([n for n in G.nodes() 
                                                        if G.nodes[n].get('type') == 'disease'])
    
    # Composite score
    connectivity_score = (1 - orphan_ratio) * 0.6 + min(avg_cross_connections / 10, 1.0) * 0.4
    return connectivity_score
```

**Target:** ≥0.85  
**Pass Threshold:** ≥0.70

### D3: Evidence Quality

```python
def score_evidence_quality():
    edges = KnowledgeBaseEntry.objects.filter(status='active')
    total = edges.count()
    if total == 0: return 0
    
    high_quality = edges.filter(
        evidence_grade__in=['1A','1B','2A','2B'],
        guideline_chapter__isnull=False,
        evidence_entries__isnull=False
    ).distinct().count()
    
    return high_quality / total
```

**Target:** ≥0.85  
**Pass Threshold:** ≥0.70

### D4: Guideline Traceability

```python
def score_guideline_traceability():
    treatment_edges = KnowledgeBaseEntry.objects.filter(
        rule_type='treatment', status='active'
    )
    total = treatment_edges.count()
    if total == 0: return 0
    
    traced = treatment_edges.filter(
        guideline_chapter__isnull=False
    ).exclude(guideline_chapter='').count()
    
    return traced / total
```

**Target:** 1.0  
**Pass Threshold:** 0.95

### D5: Clinical Validation

```python
def score_clinical_validation():
    results = ValidationTestSuite.run_all()
    metrics = {
        'differential_top1': results.differential_top1_accuracy,
        'differential_top3': results.differential_top3_accuracy,
        'treatment_concordance': results.treatment_concordance,
        'monitoring_completeness': results.monitoring_completeness,
        'urgency_accuracy': results.urgency_accuracy,
        'explainability_fidelity': results.explainability_fidelity
    }
    
    weights = {
        'differential_top1': 0.3,
        'differential_top3': 0.2,
        'treatment_concordance': 0.2,
        'monitoring_completeness': 0.15,
        'urgency_accuracy': 0.1,
        'explainability_fidelity': 0.05
    }
    
    return sum(metrics[k] * weights[k] for k in metrics)
```

**Target:** ≥0.85 composite  
**Pass Threshold:** ≥0.75

### D6: Differential Diagnosis Coverage

```python
def score_ddx_coverage():
    syndromes = Syndrome.objects.all()
    total = syndromes.count()
    if total == 0: return 0
    
    covered = 0
    for s in syndromes:
        ddx_table = get_ddx_table(s.id)
        if ddx_table and len(ddx_table) >= 5:
            # Check required columns
            required_cols = ['disease', 'supporting', 'opposing', 'likelihood', 'investigations', 'urgency']
            if all(c in ddx_table.columns for c in required_cols):
                covered += 1
    
    return covered / total
```

**Target:** 1.0 (all 16 syndromes)  
**Pass Threshold:** 0.875 (14/16)

### D7: Drug Knowledge Completeness

```python
def score_drug_completeness():
    drugs = DrugMaster.objects.filter(is_active=True)
    total = drugs.count()
    if total == 0: return 0
    
    complete = 0
    for d in drugs:
        fields = ['mechanism', 'indications', 'contraindications', 'renal_dosing',
                  'dialysis_dosing', 'transplant_considerations', 'pregnancy',
                  'lactation', 'interactions', 'lab_monitoring', 'vaccination_advice',
                  'common_ae', 'serious_ae', 'stopping_criteria', 'evidence_level',
                  'guideline_references']
        if all(getattr(d, f, None) for f in fields):
            complete += 1
    
    return complete / total
```

**Target:** ≥0.80 (40/50 drugs)  
**Pass Threshold:** ≥0.60 (30/50)

### D8: Monitoring Protocol Coverage

```python
def score_monitoring_coverage():
    disease_drug_pairs = DiseaseDrugPair.objects.all()
    total = disease_drug_pairs.count()
    if total == 0: return 0
    
    covered = disease_drug_pairs.filter(
        monitoring_protocol__isnull=False
    ).count()
    
    return covered / total
```

**Target:** ≥0.90  
**Pass Threshold:** ≥0.75

### D9: Complication Knowledge

```python
def score_complication_coverage():
    disease_comp_edges = DiseaseComplication.objects.all()
    total = disease_comp_edges.count()
    if total == 0: return 0
    
    complete = disease_comp_edges.filter(
        frequency__isnull=False,
        risk_factors__isnull=False,
        prevention__isnull=False,
        early_detection__isnull=False,
        treatment__isnull=False
    ).count()
    
    return complete / total
```

**Target:** ≥0.80  
**Pass Threshold:** ≥0.65

### D10: Pathology & Lab Reusability

```python
def score_pathology_lab_reusability():
    pathology_entities = PathologyEntity.objects.all()
    lab_entities = LabEntity.objects.all()
    
    # Reusability = linked to ≥3 diseases
    reusable_path = pathology_entities.filter(diseases__count__gte=3).count()
    reusable_lab = lab_entities.filter(diseases__count__gte=3).count()
    
    total_reusable = reusable_path + reusable_lab
    total_entities = pathology_entities.count() + lab_entities.count()
    
    if total_entities == 0: return 0
    return total_reusable / total_entities
```

**Target:** ≥0.70  
**Pass Threshold:** ≥0.50

### D11: Knowledge Freshness

```python
def score_freshness():
    edges = KnowledgeBaseEntry.objects.filter(status='active')
    total = edges.count()
    if total == 0: return 0
    
    cutoff = timezone.now().date() - timedelta(days=365)
    fresh = edges.filter(
        Q(effective_date__gte=cutoff) | 
        Q(updated_at__gte=cutoff) |
        Q(versions__created_at__gte=cutoff)
    ).distinct().count()
    
    # Also check guideline currency
    guidelines = GuidelineSource.objects.all()
    current_guidelines = guidelines.filter(
        Q(retired_date__isnull=True) | Q(retired_date__gte=timezone.now().date())
    ).count()
    guideline_currency = current_guidelines / guidelines.count() if guidelines.count() > 0 else 1
    
    return (fresh / total) * 0.7 + guideline_currency * 0.3
```

**Target:** ≥0.90  
**Pass Threshold:** ≥0.75

### D12: Governance Compliance

```python
def score_governance_compliance():
    kbs = KnowledgeBaseEntry.objects.filter(status='active')
    total = kbs.count()
    if total == 0: return 0
    
    compliant = kbs.filter(
        author__isnull=False,
        reviews__status='approved',
        reviews__reviewer__isnull=False,
        coi_declaration__isnull=False
    ).distinct().count()
    
    return compliant / total
```

**Target:** 1.0  
**Pass Threshold:** 0.95

---

## 4. Composite Score Calculation

```python
def compute_composite_score():
    weights = {
        'disease_coverage': 0.10,
        'graph_connectivity': 0.12,
        'evidence_quality': 0.12,
        'guideline_traceability': 0.10,
        'clinical_validation': 0.15,
        'ddx_coverage': 0.08,
        'drug_completeness': 0.07,
        'monitoring_coverage': 0.06,
        'complication_coverage': 0.05,
        'pathology_lab_reusability': 0.05,
        'freshness': 0.05,
        'governance_compliance': 0.05
    }
    
    scores = {k: globals()[f'score_{k}']() for k in weights}
    composite = sum(scores[k] * weights[k] for k in weights)
    
    return {
        'composite': composite,
        'domains': scores,
        'weights': weights,
        'status': 'PASS' if composite >= 0.80 else 'FAIL',
        'timestamp': timezone.now().isoformat()
    }
```

### Quality Grades

| Composite Score | Grade | Interpretation |
|---|---|---|
| ≥0.95 | A+ | Exemplary — reference standard |
| 0.90-0.94 | A | Excellent — production ready |
| 0.85-0.89 | B+ | Very Good — minor gaps |
| 0.80-0.84 | B | Good — meets production threshold |
| 0.70-0.79 | C | Needs Improvement — targeted remediation |
| <0.70 | F | Critical — not production ready |

---

## 5. Dashboard Visualization (Admin UI)

### 5.1 Executive Summary Panel

```
┌─────────────────────────────────────────────────────────────────┐
│ GDES V4.2 KNOWLEDGE QUALITY DASHBOARD                          │
│ Generated: 2026-07-10 14:32 UTC | Engine: v4.2.0               │
├─────────────────────────────────────────────────────────────────┤
│ COMPOSITE SCORE: 0.87  ████████████████████░░  GRADE: B+        │
├─────────────────────────────────────────────────────────────────┤
│ D1 Disease Coverage      ████████████████████  1.00  PASS       │
│ D2 Graph Connectivity    ████████████████░░░░  0.82  PASS       │
│ D3 Evidence Quality      ██████████████████░░  0.88  PASS       │
│ D4 Guideline Traceability ████████████████████  1.00  PASS       │
│ D5 Clinical Validation   ███████████████░░░░░  0.79  FAIL*      │
│ D6 DDx Coverage          ████████████████████  1.00  PASS       │
│ D7 Drug Completeness     ████████████████░░░░  0.84  PASS       │
│ D8 Monitoring Coverage   ██████████████████░░  0.87  PASS       │
│ D9 Complication Coverage ████████████████░░░░  0.76  PASS       │
│ D10 Path/Lab Reusability ████████████████░░░░  0.78  PASS       │
│ D11 Freshness            ████████████████████  0.94  PASS       │
│ D12 Governance           ████████████████████  1.00  PASS       │
└─────────────────────────────────────────────────────────────────┘
* D5 below 0.80 threshold — see validation report
```

### 5.2 Drill-Down Views

| View | Description |
|---|---|
| **Disease Detail** | Per-disease breakdown of all 12 domains |
| **Edge Audit** | Edge-by-edge evidence/guideline/freshness status |
| **Validation Failures** | Case-by-case failure analysis with reasoning traces |
| **Orphan Nodes** | Nodes with <2 connections — remediation queue |
| **Freshness Timeline** | Review dates by disease/domain |
| **Governance Register** | Author/reviewer/COI status per entry |

---

## 6. Automated Monitoring & Alerting

### 6.1 Scheduled Checks

| Check | Frequency | Alert Threshold | Action |
|---|---|---|---|
| Composite Score | Daily | <0.80 | Email to Governance Lead |
| Orphan Nodes | Weekly | >0 | JIRA ticket auto-creation |
| Freshness Audit | Monthly | Any edge >365 days | Review assignment |
| Guideline Currency | Quarterly | Any retired guideline in use | Update required |
| Validation Regression | Per Release | Any metric drop >2% | Block release |

### 6.2 Alert Channels

| Channel | Recipients | Format |
|---|---|---|
| Email | Governance Lead, Disease Curators | Summary + links |
| Slack | Clinical Engineering Team | Real-time alerts |
| JIRA | Disease Curators | Actionable tickets |
| Dashboard | All stakeholders | Real-time UI |

---

## 7. API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/quality/composite` | GET | Current composite score + domain breakdown |
| `/quality/domain/{domain_code}` | GET | Deep dive on single domain |
| `/quality/disease/{disease_id}` | GET | Per-disease quality report |
| `/quality/trends` | GET | Historical scores (30/90/365 days) |
| `/quality/orphans` | GET | List of under-connected nodes |
| `/quality/freshness` | GET | Edges due for review |
| `/quality/validation/latest` | GET | Latest validation test run results |
| `/quality/report` | GET | Full PDF/HTML report generation |

---

## 8. Historical Benchmarks

| Date | Composite | Grade | Notes |
|---|---|---|---|
| 2026-07-10 (V4.2 Launch) | 0.87 | B+ | Baseline — D5 needs work |
| 2026-10-10 (Q4 Review) | Target: 0.90 | A | Post-validation expansion |
| 2027-01-10 (V4.3 Target) | Target: 0.93 | A | Full governance maturity |

---

## 9. Remediation Playbooks

| Domain | Common Failures | Remediation Steps |
|---|---|---|
| D2 Graph Connectivity | Orphan syndrome nodes | Add `presents_as` edges from syndromes to diseases |
| D3 Evidence Quality | Missing evidence entries | Run evidence import pipeline; assign curators |
| D5 Clinical Validation | Low top-1 accuracy | Analyze failure cases; augment KB rules; add cases |
| D7 Drug Completeness | Missing renal dosing | Pharmacist review; populate from FDA/EMA labels |
| D11 Freshness | Stale edges | Automated reviewer assignment; 90-day review cycle |
| D12 Governance | Missing COI declarations | Mandate at authoring; CI check on commit |

---

## 10. Governance

| Role | Dashboard Access | Alert Receipt |
|---|---|---|
| Governance Lead | Full admin | All |
| Disease Curators | Own disease + composite | Own disease |
| Clinical Reviewers | Validation domain | Validation failures |
| Engineering | All domains | System alerts |
| Leadership | Executive summary only | Monthly digest |

**Review Cadence:** Monthly operational, Quarterly strategic, Annual external audit.

---

**End of Document**  
**Next Review:** 2026-10-10  
**Governance Lead:** Knowledge Quality Team