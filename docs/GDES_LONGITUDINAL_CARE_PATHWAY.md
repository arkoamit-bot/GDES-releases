# GDES Longitudinal Care Pathway — Design Document

**Version:** 1.0  
**Date:** 2026-07-12  
**Status:** Proposed  
**Target Release:** V7.2  
**Author:** GDES Engineering & Clinical Informatics  

---

## 1. Executive Summary

The GDES care pathway system currently provides generic 8-stage pathway definitions (`clinical_reasoning/services/care_pathway_engine.py:35-99`) with basic gap detection (`clinical_reasoning/services/care_pathway.py`). Pathway state is stored as a JSON blob on `ClinicalProfile.care_pathway`, milestones are an unordered JSON list on `ClinicalProfile.milestones`, and there is no stage completion tracking, no disease-specific pathway definitions, and no longitudinal encounter-to-encounter state persistence.

This document proposes transforming the care pathway into a fully tracked, disease-specific, event-driven longitudinal care management system. The design introduces normalized database models for pathway instances, stage completions, and milestones; disease-specific pathway templates for every supported GN; automated clinical alert triggers; and deep integration with the existing followup app and scheduling system.

---

## 2. Current State Analysis

### 2.1 Existing Architecture

| Component | Location | Capability | Limitation |
|---|---|---|---|
| Pathway stages | `care_pathway_engine.py:35-99` | 8 hardcoded `PathwayStage` dataclasses | Not disease-specific; no persistence |
| Stage detection | `care_pathway_engine.py:111-128` | Maps `disease_phase` + eGFR to stage | Re-derived every call; no state tracking |
| Gap detection | `care_pathway.py:12-29` | Checks core labs, monitoring, treatment | Static; no temporal awareness |
| Milestone detection | `disease_milestones.py:32-56` | Detects 7 milestone types | Stored as JSON list; first-only dedup |
| Management plan | `management_plan.py:522-566` | Disease-specific treatment protocols | No integration with pathway stage |
| Pathway model | `knowledge/models.py:426-449` | `ClinicalPathway` (disease FK, stages) | Defines templates; not instantiated per patient |
| ClinicalProfile | `clinical_reasoning/models.py:11-38` | `care_pathway` (JSON), `milestones` (JSON) | Unstructured; no relational tracking |

### 2.2 Key Limitations

1. **No disease-specific pathways.** The 8 generic stages apply identically to IgAN, membranous, lupus nephritis, and ANCA vasculitis. Each disease has distinct staging criteria, monitoring cadences, treatment milestones, and transition rules that the generic model cannot express.

2. **Milestones are ephemeral JSON.** `disease_milestones.py:140-156` merges milestones in-memory and saves to `ClinicalProfile.milestones`. They cannot be queried, filtered, or reported on relationally. No audit trail exists for when milestones were detected.

3. **No stage completion tracking.** When `determine_current_stage()` (line 111) returns a new stage, there is no record of when the previous stage began, when it ended, which actions were completed, or what outcome triggered the transition.

4. **No longitudinal encounter linkage.** Care gaps detected in `care_pathway.py` are computed at call-time with no memory of what was found at prior encounters. The same gaps may be re-flagged indefinitely.

5. **Followup integration is loose.** `FollowUpTask` (`followup/models.py:39-85`) exists independently of pathway stages. Tasks are not derived from pathway requirements, and task completion does not update pathway state.

---

## 3. Proposed Design

### 3.1 New Database Models

#### 3.1.1 PatientPathwayInstance

One record per patient per disease. Tracks the patient's active journey through a clinical pathway.

```python
class PatientPathwayInstance(models.Model):
    """A patient's active or completed journey through a disease-specific pathway."""
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        DISCONTINUED = "discontinued", "Discontinued"
        TRANSFERRED = "transferred", "Transferred"

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="pathway_instances")
    pathway = models.ForeignKey(
        "knowledge.ClinicalPathway", on_delete=models.PROTECT,
        related_name="instances",
        help_text="The first stage of the disease-specific pathway template")
    disease = models.ForeignKey(
        "knowledge.Disease", on_delete=models.PROTECT,
        related_name="patient_pathways")
    current_stage = models.ForeignKey(
        "knowledge.ClinicalPathway", on_delete=models.PROTECT,
        related_name="current_at",
        help_text="Current stage in the pathway")
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.ACTIVE)

    enrolled_date = models.DateField(help_text="When the patient entered this pathway")
    stage_entered_date = models.DateField(help_text="When the current stage began")
    expected_next_review_date = models.DateField(
        null=True, blank=True,
        help_text="Next scheduled assessment based on stage duration")

    metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Pathway-level metadata (risk score, deviation count, etc.)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-enrolled_date"]
        indexes = [
            models.Index(fields=["patient", "status"]),
            models.Index(fields=["disease", "status"]),
            models.Index(fields=["current_stage", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "disease"],
                condition=models.Q(status="active"),
                name="uniq_active_pathway_per_disease")
        ]

    def __str__(self):
        return f"{self.patient.patient_id} — {self.disease.name} ({self.status})"
```

#### 3.1.2 PathwayStageCompletion

Immutable audit record. One row per action completed at each stage.

```python
class PathwayStageCompletion(models.Model):
    """Record of an action completed at a specific pathway stage."""
    class Outcome(models.TextChoices):
        ACHIEVED = "achieved", "Achieved"
        PARTIALLY_ACHIEVED = "partial", "Partially achieved"
        NOT_ACHIEVED = "not_achieved", "Not achieved"
        SKIPPED = "skipped", "Skipped (clinician override)"
        CONTRAINDICATED = "contraindicated", "Contraindicated"

    instance = models.ForeignKey(
        PatientPathwayInstance, on_delete=models.CASCADE,
        related_name="stage_completions")
    stage = models.ForeignKey(
        "knowledge.ClinicalPathway", on_delete=models.PROTECT,
        related_name="completions")
    action_name = models.CharField(
        max_length=100,
        help_text="Action identifier matching required_actions (e.g. 'biopsy', 'egfr')")
    action_label = models.CharField(max_length=300, blank=True)

    outcome = models.CharField(
        max_length=20, choices=Outcome.choices, default=Outcome.ACHIEVED)
    outcome_details = models.JSONField(
        default=dict, blank=True,
        help_text="Structured outcome data (e.g. biopsy result, eGFR value)")

    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True)
    completed_at = models.DateTimeField(auto_now_add=True)
    encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Encounter where this action was completed")

    class Meta:
        ordering = ["instance", "stage__stage_order", "completed_at"]
        indexes = [
            models.Index(fields=["instance", "stage"]),
            models.Index(fields=["stage", "action_name"]),
        ]

    def __str__(self):
        return f"{self.instance} — {self.action_name} ({self.outcome})"
```

#### 3.1.3 DiseaseMilestone (normalized)

Replaces the JSON list on `ClinicalProfile.milestones`. The JSON field is retained for backward compatibility but becomes a denormalized cache.

```python
class DiseaseMilestone(models.Model):
    """Normalized disease milestone for a patient."""
    class MilestoneType(models.TextChoices):
        DIAGNOSIS = "diagnosis", "Initial diagnosis"
        BIOPSY = "biopsy", "Biopsy performed"
        REMISSION = "remission", "Remission achieved"
        PARTIAL_REMISSION = "partial_remission", "Partial remission achieved"
        RELAPSE = "relapse", "Disease relapse"
        ESKD = "eskd", "End-stage kidney disease"
        TREATMENT_STARTED = "treatment_started", "Treatment initiated"
        TREATMENT_SWITCHED = "treatment_switched", "Treatment changed"
        TREATMENT_COMPLETED = "treatment_completed", "Treatment course completed"
        TRANSPLANT = "transplant", "Kidney transplant"
        DEATH = "death", "Patient death"

    class Confidence(models.TextChoices):
        HIGH = "high", "High confidence"
        MODERATE = "moderate", "Moderate confidence"
        LOW = "low", "Low confidence"

    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="disease_milestones")
    milestone_type = models.CharField(
        max_length=25, choices=MilestoneType.choices, db_index=True)
    label = models.CharField(max_length=300)
    date_identified = models.DateField(null=True, blank=True)
    confidence = models.CharField(
        max_length=10, choices=Confidence.choices, default=Confidence.MODERATE)

    details = models.JSONField(default=dict, blank=True)
    source_encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True)
    source_clinical_event = models.ForeignKey(
        "encounters.ClinicalEvent", on_delete=models.SET_NULL,
        null=True, blank=True)

    detected_by = models.CharField(
        max_length=50, blank=True,
        help_text="Service that detected this milestone (e.g. 'disease_milestones')")
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "date_identified"]
        indexes = [
            models.Index(fields=["patient", "milestone_type"]),
            models.Index(fields=["patient", "date_identified"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "milestone_type", "date_identified"],
                name="uniq_milestone_per_patient_date")
        ]

    def __str__(self):
        return f"{self.patient.patient_id} — {self.label}"
```

### 3.2 Disease-Specific Pathway Templates

Each disease receives a full pathway defined in `knowledge.ClinicalPathway` records. The following table defines the IgAN pathway as a reference implementation; all supported diseases follow the same pattern.

#### IgAN Pathway Stages

| stage_id | stage_name | order | expected_duration_days | required_actions | next_stages | criteria_to_proceed |
|---|---|---|---|---|---|---|
| `igan-assessment` | Initial Assessment | 1 | 30 | `biopsy`, `serology`, `urinalysis`, `egfr`, `risk_stratification` | `igan-supportive` | Biopsy confirmed IgAN |
| `igan-supportive` | Supportive Care | 2 | 180 | `raas_blockade`, `sglt2i_initiation`, `bp_control`, `lifestyle_modification` | `igan-response-assess` | Max tolerated RAASi + SGLT2i for ≥3 months |
| `igan-response-assess` | Response Assessment | 3 | 90 | `proteinuria_assessment`, `egfr_trend`, `risk_reclassification` | `igan-remission`, `igan-high-risk`, `igan-ckd` | Proteinuria response at 3-6 months |
| `igan-remission` | Remission | 4 | 730 | `maintenance_tx`, `quarterly_monitoring`, `vaccination_review` | `igan-relapse`, `igan-ckd` | Sustained proteinuria <1g/day |
| `igan-high-risk` | High-Risk / Targeted Therapy | 5 | 120 | `targeted_therapy`, `monthly_monitoring`, `response_assessment` | `igan-remission`, `igan-ckd` | Budesonide or sparsentan course completed |
| `igan-relapse` | Relapse | 6 | 90 | `reinduction`, `adherence_assessment`, `intensified_monitoring` | `igan-remission`, `igan-ckd` | Proteinuria <1g/day re-achieved |
| `igan-ckd` | CKD Management | 7 | 1825 | `nephroprotection`, `bp_control`, `cv_screening`, `ckd_mbd_screening` | `igan-eskd` | eGFR stable or acceptable decline |
| `igan-eskd` | ESKD / RRT | 8 | null | `rrt_access`, `transplant_evaluation`, `palliative_care` | `igan-post-transplant` | Access established |
| `igan-post-transplant` | Post-Transplant | 9 | null | `immunosuppression`, `rejection_monitoring`, `iga-recurrence-screening` | `igan-ckd` | Stable graft function |

#### Disease Pathway Coverage Matrix

| Disease | Stages | Key Differentiators |
|---|---|---|
| IgA Nephropathy | 9 stages | Response assessment at 3-6 months; targeted therapy (budesonide/sparsentan) stage |
| Membranous Nephropathy | 8 stages | PLA2R-guided staging; rituximab-first with serological response assessment |
| Minimal Change Disease | 7 stages | Steroid response assessment at 4/8/16 weeks; frequent relapser pathway |
| FSGS | 8 stages | Steroid resistance assessment; CNI trial stage; genetic testing trigger |
| Lupus Nephritis | 9 stages | ISN/RPS class-driven; maintenance vs. induction branching; dual monitoring (renal + systemic) |
| ANCA Vasculitis | 8 stages | BVAS-driven staging; rituximab maintenance; relapse surveillance |
| Anti-GBM Disease | 6 stages | Emergency pathway; PLEX duration; dialysis independence assessment |
| C3 Glomerulopathy | 7 stages | Complement pathway evaluation; clinical trial enrollment stage |

### 3.3 Automated Triggers and Alerts

The pathway engine generates alerts based on temporal and clinical triggers. These integrate with the existing `FollowUpTask` model and `ClinicalInsight` model.

#### Trigger Definitions

| Trigger ID | Condition | Alert Type | Priority | Action |
|---|---|---|---|---|
| `missed-appointment` | `ScheduledVisit.status == "missed"` | `FollowUpTask` (visit_due) | urgent | Re-schedule within 7 days |
| `overdue-lab` | `FollowUpTask` for lab due > 7 days overdue | `FollowUpTask` escalation | urgent | Escalate to coordinator |
| `egfr-decline` | eGFR drop > 15% from baseline within 3 months | `ClinicalInsight` (monitoring) | high | Trigger pathway reassessment |
| `proteinuria-increase` | UPCR increase > 50% from nadir | `ClinicalInsight` (monitoring) | high | Consider relapse staging |
| `relapse-detection` | Proteinuria returns to nephrotic range after remission | `ClinicalInsight` + milestone | high | Enter relapse stage |
| `treatment-toxicity` | Adverse event grade ≥ 3 during immunosuppression | `ClinicalInsight` (safety) | critical | Treatment review within 48h |
| `non-response` | No proteinuria reduction at 6 months of therapy | `ClinicalInsight` (therapeutic) | high | Step-up therapy assessment |
| `stage-duration-exceeded` | Time in stage > 2× expected_duration_days | Pathway alert | medium | Clinical review trigger |
| `vaccination-gap` | No influenza/pneumococcal vaccination in 12 months | `FollowUpTask` (vaccination_due) | routine | Schedule vaccination |
| `ckd-progression` | eGFR < 45 with declining trajectory | `ClinicalInsight` (prognostic) | high | CKD-MBD + anemia screening |

#### Trigger Engine Architecture

```python
# clinical_reasoning/services/pathway_triggers.py

class PathwayTriggerEngine:
    """Event-driven trigger evaluation for pathway instances."""

    def evaluate_all(self, instance: PatientPathwayInstance, features: dict) -> list[dict]:
        """Run all trigger checks and return alerts."""
        alerts = []
        alerts.extend(self._check_missed_visits(instance))
        alerts.extend(self._check_overdue_labs(instance))
        alerts.extend(self._check_egfr_decline(instance, features))
        alerts.extend(self._check_proteinuria_change(instance, features))
        alerts.extend(self._check_relapse(instance, features))
        alerts.extend(self._check_stage_overstay(instance))
        alerts.extend(self._check_treatment_toxicity(instance))
        alerts.extend(self._check_non_response(instance, features))
        return alerts

    def _check_egfr_decline(self, instance, features) -> list[dict]:
        """Alert if eGFR drops >15% from stage baseline."""
        baseline_egfr = instance.metadata.get("stage_baseline_egfr")
        current_egfr = features.get("latest_egfr")
        if baseline_egfr and current_egfr:
            decline_pct = (baseline_egfr - current_egfr) / baseline_egfr * 100
            if decline_pct > 15:
                return [{
                    "trigger": "egfr-decline",
                    "priority": "high",
                    "message": f"eGFR declined {decline_pct:.0f}% from stage baseline",
                    "action": "Pathway reassessment recommended",
                }]
        return []
```

### 3.4 Care Gap Detection Enhancements

The existing `detect_care_gaps()` in `care_pathway.py` is enhanced to be pathway-aware:

```python
# Enhanced care gap detection
def detect_pathway_gaps(instance: PatientPathwayInstance, features: dict) -> list[dict]:
    """Detect care gaps specific to the current pathway stage."""
    gaps = []
    stage = instance.current_stage

    # 1. Required actions not yet completed at this stage
    completed_actions = set(
        instance.stage_completions
        .filter(stage=stage, outcome="achieved")
        .values_list("action_name", flat=True)
    )
    for action in stage.required_actions:
        if action not in completed_actions:
            gaps.append({
                "field": action,
                "importance": "high",
                "category": "pathway_requirement",
                "message": f"Required action '{action}' not completed at stage '{stage.stage_name}'",
                "recommendation": f"Complete {action} before proceeding",
            })

    # 2. Stage duration exceeded
    days_in_stage = (date.today() - instance.stage_entered_date).days
    if stage.expected_duration_days and days_in_stage > stage.expected_duration_days * 1.5:
        gaps.append({
            "field": "stage_duration",
            "importance": "medium",
            "category": "pathway_timing",
            "message": f"Patient has been in '{stage.stage_name}' for {days_in_stage} days "
                       f"(expected {stage.expected_duration_days})",
            "recommendation": "Review pathway progression criteria",
        })

    # 3. Expected monitoring not performed
    gaps.extend(_check_monitoring_schedule(instance, features))

    return gaps
```

### 3.5 Longitudinal Encounter Linkage

Each `ClinicalEncounter` links to the pathway instance and records the pathway state at encounter time:

```python
# Addition to encounters/models.py
class ClinicalEncounter(models.Model):
    # ... existing fields ...
    pathway_instance = models.ForeignKey(
        "pathways.PatientPathwayInstance", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="encounters")
    pathway_stage_at_encounter = models.ForeignKey(
        "knowledge.ClinicalPathway", on_delete=models.SET_NULL,
        null=True, blank=True)
    pathway_actions_completed = models.JSONField(
        default=list, blank=True,
        help_text="Actions completed during this encounter for the pathway")
```

### 3.6 Followup App Integration

Pathway triggers generate `FollowUpTask` records directly:

```python
def create_pathway_tasks(instance: PatientPathwayInstance):
    """Generate FollowUpTask records from pathway stage requirements."""
    stage = instance.current_stage
    required_actions = stage.required_actions or []

    action_task_map = {
        "quarterly_monitoring": ("lab_due", "Quarterly monitoring labs"),
        "monthly_monitoring": ("lab_due", "Monthly monitoring labs"),
        "bp_control": ("visit_due", "Blood pressure assessment"),
        "vaccination_review": ("vaccination_due", "Vaccination status review"),
        "transplant_evaluation": ("visit_due", "Transplant evaluation"),
        "screening": ("lab_due", "Screening investigations"),
    }

    for action in required_actions:
        task_type, reason = action_task_map.get(action, ("visit_due", action))
        due = instance.expected_next_review_date or date.today()

        if not FollowUpTask.objects.filter(
            patient=instance.patient,
            task_type=task_type,
            status__in=("pending", "overdue"),
            reason__icontains=action,
        ).exists():
            FollowUpTask.objects.create(
                patient=instance.patient,
                task_type=task_type,
                priority="routine",
                reason=reason,
                clinical_reason=f"Pathway stage '{stage.stage_name}' requires {action}",
                due_date=due,
                protocol_label=f"{stage.stage_id}:{action}",
            )
```

---

## 4. Service Layer Architecture

### 4.1 PathwayEngine (rewrite)

The existing `care_pathway_engine.py` functions are refactored into a class-based engine:

```python
class PathwayEngine:
    """Central orchestrator for pathway lifecycle management."""

    def __init__(self, patient):
        self.patient = patient
        self.features = extract_features(patient)

    def get_active_pathway(self) -> PatientPathwayInstance | None:
        return PatientPathwayInstance.objects.filter(
            patient=self.patient, status="active"
        ).select_related("current_stage", "disease").first()

    def enroll_in_pathway(self, disease_id: str) -> PatientPathwayInstance:
        """Enroll patient in a disease-specific pathway starting at stage 1."""
        ...

    def advance_stage(self, instance: PatientPathwayInstance,
                      target_stage_id: str, clinician=None) -> dict:
        """Transition to next stage with validation and audit."""
        ...

    def evaluate_triggers(self, instance: PatientPathwayInstance) -> list[dict]:
        """Run all automated trigger checks."""
        return PathwayTriggerEngine().evaluate_all(instance, self.features)

    def get_pathway_summary(self, instance: PatientPathwayInstance) -> dict:
        """Build complete longitudinal summary."""
        ...

    def detect_deviations(self, instance: PatientPathwayInstance) -> list[dict]:
        """Detect deviations from expected pathway."""
        ...
```

### 4.2 Integration Points

| Existing Component | Integration |
|---|---|
| `disease_milestones.py` | Milestones now saved to `DiseaseMilestone` model; JSON on `ClinicalProfile` updated for backward compat |
| `management_plan.py` | `generate_management_plan()` reads current stage to determine monitoring intensity |
| `care_pathway.py` | `detect_care_gaps()` delegates to `detect_pathway_gaps()` when active pathway exists |
| `care_pathway_engine.py` | `determine_current_stage()` now reads from `PatientPathwayInstance.current_stage` |
| `FollowUpTask` | Tasks generated from pathway requirements; task completion triggers stage re-evaluation |
| `ScheduledVisit` | Visits linked to pathway stages; missed visits trigger pathway alerts |
| `ClinicalInsight` | RESEARCH category insights generated from pathway state |
| `ClinicalProfile.care_pathway` | Updated as denormalized cache of active pathway state |

---

## 5. Implementation Plan

### Phase 1: Database Foundation (Week 1-2)

| Task | Files | Depends On |
|---|---|---|
| Create `PatientPathwayInstance` model | `pathways/models.py` (new app) | — |
| Create `PathwayStageCompletion` model | `pathways/models.py` | — |
| Create `DiseaseMilestone` model | `pathways/models.py` | — |
| Add `pathway_instance` FK to `ClinicalEncounter` | `encounters/migrations/` | — |
| Run migrations, verify constraints | — | All above |
| Write model unit tests (15+ tests) | `pathways/tests/` | — |

### Phase 2: Disease-Specific Pathway Templates (Week 2-3)

| Task | Files | Depends On |
|---|---|---|
| Populate IgAN pathway (9 stages) | `knowledge/fixtures/pathways_iga.json` | Phase 1 |
| Populate MN pathway (8 stages) | `knowledge/fixtures/pathways_membranous.json` | Phase 1 |
| Populate MCD pathway (7 stages) | `knowledge/fixtures/pathways_mcd.json` | Phase 1 |
| Populate FSGS, LN, AAV, anti-GBM, C3G | `knowledge/fixtures/pathways_*.json` | Phase 1 |
| Management command: `load_pathway_templates` | `knowledge/management/commands/` | Fixtures |
| Validate all pathways have valid `next_stages` DAG | `pathways/validation.py` | Fixtures |

### Phase 3: Pathway Engine Rewrite (Week 3-4)

| Task | Files | Depends On |
|---|---|---|
| Implement `PathwayEngine` class | `pathways/engine.py` | Phase 1-2 |
| Implement `PathwayTriggerEngine` | `pathways/triggers.py` | Phase 1 |
| Milestone normalization service | `pathways/milestone_service.py` | Phase 1 |
| Pathway-aware care gap detection | `pathways/gap_detection.py` | Phase 1-2 |
| Integration with `ClinicalProfile` cache | `clinical_reasoning/services/` | Phase 1 |
| Comprehensive test suite (40+ tests) | `pathways/tests/` | All above |

### Phase 4: Followup Integration (Week 4-5)

| Task | Files | Depends On |
|---|---|---|
| `create_pathway_tasks()` service | `pathways/task_generation.py` | Phase 3 |
| Task completion -> stage re-evaluation | `followup/signals.py` | Phase 3 |
| Encounter linkage to pathway | `encounters/services/` | Phase 1 |
| SMS/email alert integration | `communication/services/` | Phase 3-4 |

### Phase 5: Migration and Validation (Week 5-6)

| Task | Files | Depends On |
|---|---|---|
| Data migration: existing patients into pathway instances | `pathways/migrations/` | Phase 1-4 |
| Backward-compatible `ClinicalProfile` sync | `pathways/sync.py` | Phase 1 |
| Clinical validation with 10 reference cases | `pathways/tests/validation/` | Phase 1-4 |
| Performance testing with 1000+ patients | `pathways/tests/performance/` | Phase 1-4 |

---

## 6. Success Criteria

| Metric | Target | Measurement |
|---|---|---|
| Disease-specific pathways defined | 8 diseases | Count of `ClinicalPathway` records with unique `disease` FK |
| Pathway enrollment rate | >90% of new patients | `PatientPathwayInstance` count / new patient count |
| Stage completion tracking | 100% of required actions logged | `PathwayStageCompletion` records per stage |
| Alert trigger accuracy | >95% clinically relevant | Clinician review of 50 random alerts |
| False positive alert rate | <5% | Alerts dismissed as clinically irrelevant / total alerts |
| Missed visit detection | 100% within 24 hours | Time from `ScheduledVisit` overdue to alert creation |
| Longitudinal milestone tracking | 100% normalized | `DiseaseMilestone` records vs. JSON list entries |
| Backward compatibility | `ClinicalProfile.care_pathway` always reflects active state | Automated sync test |
| Test coverage | >95% on pathway module | Coverage report |
| Performance | <500ms for pathway evaluation per patient | Benchmark with 1000-patient cohort |

---

## 7. Risk Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Migration breaks existing `ClinicalProfile.care_pathway` consumers | High | Maintain JSON sync; run both read paths in parallel during V7.2 |
| Pathway templates are clinically inaccurate | High | Clinical review gate: all pathway definitions require nephrologist sign-off before activation |
| Alert fatigue from too many triggers | Medium | Configurable alert thresholds; per-disease tuning; alert suppression for resolved items |
| Performance degradation with complex queries | Medium | Index strategy documented; `select_related` / `prefetch` enforced in engine |
| Backward-incompatible API changes | Medium | Version all API responses; `care_pathway` JSON field retained |

---

## 8. Appendix: API Surface

### New Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/pathways/patient/<patient_id>/active/` | Get active pathway instance |
| POST | `/api/pathways/patient/<patient_id>/enroll/` | Enroll in a disease pathway |
| POST | `/api/pathways/<instance_id>/advance/` | Transition to next stage |
| POST | `/api/pathways/<instance_id>/complete-action/` | Record action completion |
| GET | `/api/pathways/<instance_id>/gaps/` | List current care gaps |
| GET | `/api/pathways/<instance_id>/alerts/` | List active alerts |
| GET | `/api/pathways/<instance_id>/milestones/` | List disease milestones |
| GET | `/api/pathways/<instance_id>/summary/` | Full longitudinal summary |
| GET | `/api/pathways/disease/<disease_id>/template/` | Pathway template definition |

### Existing Endpoints Modified

| Endpoint | Change |
|---|---|
| `/api/clinical-reasoning/<patient_id>/profile/` | `care_pathway` field now populated from active `PatientPathwayInstance` |
| `/api/clinical-reasoning/<patient_id>/milestones/` | Returns `DiseaseMilestone` records instead of JSON list |
| `/api/followup/tasks/` | Tasks generated from pathway requirements include `protocol_label` |
