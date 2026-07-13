# GDES Research Automation Engine — Design Document

**Version:** 1.0  
**Date:** 2026-07-12  
**Status:** Proposed  
**Target Release:** V7.3  
**Author:** GDES Engineering & Clinical Informatics  

---

## 1. Executive Summary

GDES currently provides basic research intelligence through `clinical_reasoning/services/research_intelligence.py`: cohort discovery via hardcoded patient filters, protocol matching using a simple scoring heuristic, and research opportunity detection from milestone patterns. The `studies` app handles post-enrollment management (randomization, arm allocation) well but has no automated pre-enrollment eligibility screening.

This document proposes a structured eligibility screening engine with formal inclusion/exclusion criteria models, automated patient-to-study matching with missing-variable detection, research follow-up compliance tracking, export-ready dataset generation, and a recruitment dashboard — transforming the registry from a passive data repository into an active research recruitment and management platform.

---

## 2. Current State Analysis

### 2.1 Existing Research Capabilities

| Component | Location | Capability | Limitation |
|---|---|---|---|
| Cohort discovery | `research_intelligence.py:10-59` | 10 hardcoded cohort queries | No dynamic criteria; no study linkage |
| Protocol matching | `research_intelligence.py:72-91` | Score-based (diagnosis + phase + age) | No structured eligibility rules; no exclusion logic |
| Research opportunities | `research_intelligence.py:117-163` | 4 opportunity types from milestones | Pattern-based; not study-specific |
| Study model | `studies/models.py:18-73` | `Study` with `target_diagnoses` (CSV), `eligible_phases` (CSV) | No structured criteria; no inclusion/exclusion rules |
| StudyArm | `studies/models.py:75-91` | Arm definitions with allocation ratio | Well-designed; no changes needed |
| StudyEnrollment | `studies/models.py:94-135` | Screening + randomization workflow | Manual screening; no automated eligibility evaluation |
| ClinicalInsight (RESEARCH) | `clinical_reasoning/models.py:50` | Research insight category | Underutilized; no automatic generation |

### 2.2 Key Gaps

1. **No structured eligibility criteria.** Study eligibility is expressed only through `target_diagnoses` (comma-separated string) and `eligible_phases` (comma-separated string). Real clinical trials have 15-30 inclusion/exclusion criteria spanning demographics, labs, comorbidities, medications, disease severity, and treatment history. There is no way to represent these in the current schema.

2. **No automated eligibility screening.** `match_patient_to_protocols()` computes a 0-100 score based on diagnosis, phase, interventional preference, and age. It does not evaluate specific criteria, cannot exclude patients who fail exclusion rules, and produces no structured reason for ineligibility.

3. **No missing variable detection.** When a patient lacks data needed for eligibility assessment (e.g., no PLA2R antibody for membranous MN), the system silently ignores the gap rather than reporting which data points would enable screening.

4. **No research follow-up compliance.** Once enrolled, there is no mechanism to track research-specific visit schedules, protocol deviations, or data completeness requirements beyond the general `ScheduledVisit` system.

5. **No dataset export.** No structured mechanism to generate analysis-ready datasets from the registry for research collaborators or regulatory submissions.

---

## 3. Proposed Design

### 3.1 New Database Models

#### 3.1.1 InclusionCriterion

Structured inclusion criteria linked to a study. Each criterion is a boolean rule evaluated against patient features.

```python
class InclusionCriterion(models.Model):
    """A single inclusion criterion for a study, expressed as a structured rule."""
    class DataType(models.TextChoices):
        NUMERIC = "numeric", "Numeric comparison"
        CATEGORICAL = "categorical", "Categorical match"
        BOOLEAN = "boolean", "Boolean flag"
        DATE_RANGE = "date_range", "Date range"
        COMPOSITE = "composite", "Composite rule"
        LAB_VALUE = "lab_value", "Lab value comparison"

    class Operator(models.TextChoices):
        EQ = "eq", "Equals"
        NEQ = "neq", "Not equals"
        GT = "gt", "Greater than"
        GTE = "gte", "Greater than or equal"
        LT = "lt", "Less than"
        LTE = "lte", "Less than or equal"
        IN = "in", "In list"
        NOT_IN = "not_in", "Not in list"
        CONTAINS = "contains", "Contains"
        BETWEEN = "between", "Between (inclusive)"

    study = models.ForeignKey(
        "studies.Study", on_delete=models.CASCADE,
        related_name="inclusion_criteria")
    order = models.PositiveSmallIntegerField(
        default=0, help_text="Evaluation order (lower = evaluated first)")

    label = models.CharField(
        max_length=300, help_text="Human-readable criterion (e.g. 'Age 18-75 years')")
    description = models.TextField(blank=True)

    feature_key = models.CharField(
        max_length=100,
        help_text="Patient feature to evaluate (e.g. 'age_years', 'egfr', 'diagnosis', 'upcr')")
    data_type = models.CharField(max_length=15, choices=DataType.choices)
    operator = models.CharField(max_length=10, choices=Operator.choices)
    value = models.JSONField(
        help_text="Comparison value(s): number, string, list, or {min, max} for BETWEEN")

    is_mandatory = models.BooleanField(
        default=True,
        help_text="If False, criterion is preferred but not required for eligibility")
    category = models.CharField(
        max_length=50, blank=True,
        help_text="Grouping (e.g. 'demographics', 'disease', 'labs', 'treatment_history')")

    class Meta:
        ordering = ["study", "order"]
        verbose_name_plural = "inclusion criteria"
        indexes = [
            models.Index(fields=["study", "order"]),
        ]

    def __str__(self):
        return f"Inclusion: {self.label} ({self.study.code})"

    def evaluate(self, patient_features: dict) -> tuple[bool, str]:
        """Evaluate this criterion against patient features.

        Returns (met: bool, reason: str).
        """
        feature_value = patient_features.get(self.feature_key)
        if feature_value is None:
            return False, f"Missing data for {self.feature_key}"

        try:
            return self._compare(feature_value)
        except (TypeError, ValueError) as e:
            return False, f"Evaluation error: {e}"

    def _compare(self, feature_value) -> tuple[bool, str]:
        ops = {
            "eq": lambda v, c: (v == c, f"{v} == {c}"),
            "neq": lambda v, c: (v != c, f"{v} != {c}"),
            "gt": lambda v, c: (float(v) > float(c), f"{v} > {c}"),
            "gte": lambda v, c: (float(v) >= float(c), f"{v} >= {c}"),
            "lt": lambda v, c: (float(v) < float(c), f"{v} < {c}"),
            "lte": lambda v, c: (float(v) <= float(c), f"{v} <= {c}"),
            "in": lambda v, c: (v in c, f"{v} in {c}"),
            "not_in": lambda v, c: (v not in c, f"{v} not in {c}"),
            "contains": lambda v, c: (c in v, f"'{c}' in '{v}'"),
            "between": lambda v, c: (c["min"] <= float(v) <= c["max"],
                                     f"{c['min']} <= {v} <= {c['max']}"),
        }
        return ops[self.operator](feature_value, self.value)
```

#### 3.1.2 ExclusionCriterion

Mirrors `InclusionCriterion` but defines conditions that disqualify a patient.

```python
class ExclusionCriterion(models.Model):
    """A single exclusion criterion for a study."""
    # Same fields as InclusionCriterion
    study = models.ForeignKey(
        "studies.Study", on_delete=models.CASCADE,
        related_name="exclusion_criteria")
    order = models.PositiveSmallIntegerField(default=0)

    label = models.CharField(max_length=300)
    description = models.TextField(blank=True)

    feature_key = models.CharField(max_length=100)
    data_type = models.CharField(max_length=15, choices=InclusionCriterion.DataType.choices)
    operator = models.CharField(max_length=10, choices=InclusionCriterion.Operator.choices)
    value = models.JSONField()

    is_mandatory = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True)

    # Exclusion-specific fields
    severity = models.CharField(
        max_length=15,
        choices=[("absolute", "Absolute"), ("relative", "Relative")],
        default="absolute",
        help_text="Absolute: always exclude. Relative: exclude unless override approved.")

    class Meta:
        ordering = ["study", "order"]
        verbose_name_plural = "exclusion criteria"
        indexes = [
            models.Index(fields=["study", "order"]),
        ]

    def __str__(self):
        return f"Exclusion: {self.label} ({self.study.code})"

    def evaluate(self, patient_features: dict) -> tuple[bool, str]:
        """Evaluate exclusion criterion. Returns (excluded: bool, reason: str)."""
        feature_value = patient_features.get(self.feature_key)
        if feature_value is None:
            # Missing data for exclusion = not excluded (benefit of the doubt)
            return False, f"Cannot assess: missing {self.feature_key}"
        try:
            return InclusionCriterion._compare(self, feature_value)
        except (TypeError, ValueError) as e:
            return False, f"Evaluation error: {e}"
```

#### 3.1.3 EligibilityScreening

Audit trail for every eligibility evaluation.

```python
class EligibilityScreening(models.Model):
    """Record of a patient eligibility screening against a study."""
    class Result(models.TextChoices):
        ELIGIBLE = "eligible", "Eligible"
        INELIGIBLE = "ineligible", "Ineligible"
        INDETERMINATE = "indeterminate", "Indeterminate (missing data)"
        PENDING_REVIEW = "pending_review", "Pending clinician review"

    study = models.ForeignKey(
        "studies.Study", on_delete=models.CASCADE,
        related_name="screenings")
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="eligibility_screenings")
    enrollment = models.OneToOneField(
        "studies.StudyEnrollment", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="screening")

    result = models.CharField(max_length=15, choices=Result.choices)
    inclusion_met = models.JSONField(
        default=list, blank=True,
        help_text="List of {criterion_id, met, reason} for each inclusion criterion")
    exclusion_met = models.JSONField(
        default=list, blank=True,
        help_text="List of {criterion_id, met, reason} for each exclusion criterion")
    missing_data = models.JSONField(
        default=list, blank=True,
        help_text="List of feature_keys required but missing from patient data")

    overall_score = models.FloatField(
        default=0.0,
        help_text="Composite eligibility score (0-100)")
    clinician_override = models.BooleanField(
        default=False,
        help_text="Whether a clinician manually overrode the result")
    override_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True)
    override_reason = models.TextField(blank=True)

    screened_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Screening result expiry (re-screening recommended after)")

    class Meta:
        ordering = ["-screened_at"]
        indexes = [
            models.Index(fields=["study", "result"]),
            models.Index(fields=["patient", "study"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["study", "patient"],
                condition=models.Q(clinician_override=False),
                name="uniq_auto_screening_per_study_patient")
        ]

    def __str__(self):
        return f"Screening: {self.patient.patient_id} for {self.study.code} — {self.result}"
```

#### 3.1.4 ResearchFollowUp

Research-specific follow-up schedule separate from clinical visits.

```python
class ResearchFollowUp(models.Model):
    """Research-specific follow-up visit for an enrolled patient."""
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        MISSED = "missed", "Missed"
        CANCELLED = "cancelled", "Cancelled"

    enrollment = models.ForeignKey(
        "studies.StudyEnrollment", on_delete=models.CASCADE,
        related_name="research_followups")
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.CASCADE,
        related_name="research_followups")

    visit_label = models.CharField(
        max_length=50,
        help_text="Protocol visit label (e.g. 'Screening', 'Week 4', 'Month 6')")
    visit_day = models.IntegerField(
        help_text="Day relative to enrollment (0 = enrollment, 28 = Week 4)")
    due_date = models.DateField()
    window_start = models.DateField()
    window_end = models.DateField()

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True)

    # Data completeness tracking
    required_data_points = models.JSONField(
        default=list, blank=True,
        help_text="List of required data elements for this visit")
    completed_data_points = models.JSONField(
        default=list, blank=True,
        help_text="List of data elements actually captured")
    data_completeness_pct = models.FloatField(
        default=0.0, help_text="Percentage of required data captured")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "visit_day"]
        indexes = [
            models.Index(fields=["enrollment", "status"]),
            models.Index(fields=["patient", "status", "due_date"]),
        ]

    def __str__(self):
        return f"{self.patient.patient_id} — {self.visit_label} ({self.status})"

    def compute_completeness(self):
        """Compute data completeness percentage."""
        if not self.required_data_points:
            self.data_completeness_pct = 100.0
            return
        captured = set(self.completed_data_points)
        required = set(self.required_data_points)
        self.data_completeness_pct = len(captured & required) / len(required) * 100
```

### 3.2 Eligibility Screening Engine

```python
# studies/services/eligibility.py

class EligibilityScreeningEngine:
    """Automated patient-to-study eligibility evaluation."""

    def __init__(self, patient):
        self.patient = patient
        self.features = self._extract_features(patient)

    def screen_study(self, study: Study) -> EligibilityScreening:
        """Run full eligibility screening against a study."""
        inclusion_results = []
        exclusion_results = []
        missing_data = []

        # Evaluate inclusion criteria
        for criterion in study.inclusion_criteria.order_by("order"):
            met, reason = criterion.evaluate(self.features)
            inclusion_results.append({
                "criterion_id": criterion.pk,
                "label": criterion.label,
                "met": met,
                "reason": reason,
                "mandatory": criterion.is_mandatory,
            })
            if not met and "Missing data" in reason:
                missing_data.append(criterion.feature_key)

        # Evaluate exclusion criteria
        for criterion in study.exclusion_criteria.order_by("order"):
            excluded, reason = criterion.evaluate(self.features)
            exclusion_results.append({
                "criterion_id": criterion.pk,
                "label": criterion.label,
                "excluded": excluded,
                "reason": reason,
                "severity": criterion.severity,
            })
            if excluded and "Cannot assess" not in reason:
                missing_data.append(criterion.feature_key) if "missing" in reason.lower() else None

        # Determine overall result
        result = self._determine_result(inclusion_results, exclusion_results, missing_data)

        # Compute score
        score = self._compute_score(inclusion_results, exclusion_results, missing_data)

        screening = EligibilityScreening.objects.create(
            study=study,
            patient=self.patient,
            result=result,
            inclusion_met=inclusion_results,
            exclusion_met=exclusion_results,
            missing_data=list(set(missing_data)),
            overall_score=score,
        )

        # Auto-generate research insight
        if result == "eligible":
            self._create_research_insight(study, screening)

        return screening

    def screen_all_studies(self) -> list[dict]:
        """Screen patient against all recruiting/active studies."""
        results = []
        for study in Study.objects.filter(status__in=["recruiting", "active"]):
            screening = self.screen_study(study)
            results.append({
                "study_code": study.code,
                "study_title": study.title,
                "result": screening.result,
                "score": screening.overall_score,
                "missing_data_count": len(screening.missing_data),
            })
        return sorted(results, key=lambda x: -x["score"])

    def _determine_result(self, inclusion_results, exclusion_results, missing_data) -> str:
        # Absolute exclusion met -> ineligible
        for ex in exclusion_results:
            if ex["excluded"] and ex["severity"] == "absolute":
                return "ineligible"

        # Mandatory inclusion not met -> ineligible
        for inc in inclusion_results:
            if not inc["met"] and inc["mandatory"]:
                return "ineligible"

        # Missing critical data -> indeterminate
        if missing_data:
            return "indeterminate"

        return "eligible"

    def _compute_score(self, inclusion_results, exclusion_results, missing_data) -> float:
        total = len(inclusion_results) + len(exclusion_results)
        if total == 0:
            return 0.0
        met_count = sum(1 for r in inclusion_results if r["met"])
        not_excluded = sum(1 for r in exclusion_results if not r["excluded"])
        return round((met_count + not_excluded) / total * 100, 1)

    def _extract_features(self, patient) -> dict:
        """Extract all features relevant for eligibility evaluation."""
        from datetime import date
        features = {
            "diagnosis": getattr(patient, "primary_diagnosis", ""),
            "phase": getattr(patient, "current_phase", ""),
            "sex": getattr(patient, "sex", ""),
            "egfr": float(patient.latest_egfr) if patient.latest_egfr else None,
        }
        if patient.dob:
            features["age_years"] = (date.today() - patient.dob).days / 365.25

        # Lab features
        from labs.models import LabResult
        latest_labs = {}
        for code in ("upcr", "utp_24h", "albumin", "creatinine", "pla2r", "anca_mpo", "anca_pr3"):
            lab = LabResult.objects.filter(
                patient=patient, test__code=code
            ).order_by("-result_date").first()
            if lab and lab.value_numeric is not None:
                latest_labs[code] = float(lab.value_numeric)
        features.update(latest_labs)

        # Treatment features
        from treatments.models import TreatmentExposure
        treatments = list(
            TreatmentExposure.objects.filter(patient=patient)
            .values_list("treatment_name", flat=True)
        )
        features["treatments_tried"] = treatments
        features["treatment_count"] = len(treatments)

        # Biopsy features
        features["has_biopsy"] = patient.biopsies.exists() if hasattr(patient, 'biopsies') else False

        # Comorbidities (placeholder for structured data)
        features["diabetes"] = getattr(patient, "diabetes_status", "none") != "none"
        features["hypertension"] = getattr(patient, "hypertension", False)

        return features

    def _create_research_insight(self, study, screening):
        """Auto-generate a RESEARCH ClinicalInsight for eligible patients."""
        from clinical_reasoning.models import ClinicalInsight
        ClinicalInsight.objects.create(
            patient=self.patient,
            category="research",
            priority="medium",
            title=f"Eligible for study: {study.title}",
            description=f"Patient meets eligibility criteria for {study.code} "
                       f"(score: {screening.overall_score}%). "
                       f"{len(screening.missing_data)} data points missing.",
            reasoning=f"Automated eligibility screening identified this patient as eligible.",
            evidence=[{
                "study_id": study.id,
                "screening_id": screening.pk,
                "score": screening.overall_score,
            }],
            actionable=True,
        )
```

### 3.3 Enhanced Cohort Discovery

The existing `discover_cohorts()` is replaced with a dynamic, criteria-driven engine:

```python
# studies/services/cohort_discovery.py

class DynamicCohortDiscovery:
    """Criteria-driven cohort discovery across the registry."""

    def discover_for_study(self, study: Study) -> dict:
        """Find all potential candidates for a study."""
        candidates = Patient.objects.all()

        # Apply study-level filters (fast pre-filter)
        if study.target_diagnoses:
            diagnoses = [d.strip() for d in study.target_diagnoses.split(",")]
            candidates = candidates.filter(primary_diagnosis__in=diagnoses)

        # Screen each candidate
        results = []
        for patient in candidates:
            engine = EligibilityScreeningEngine(patient)
            screening = engine.screen_study(study)
            results.append({
                "patient_id": patient.patient_id,
                "result": screening.result,
                "score": screening.overall_score,
                "missing_data": screening.missing_data,
            })

        eligible = [r for r in results if r["result"] == "eligible"]
        indeterminate = [r for r in results if r["result"] == "indeterminate"]

        return {
            "study_code": study.code,
            "total_screened": len(results),
            "eligible": len(eligible),
            "indeterminate": len(indeterminate),
            "ineligible": len(results) - len(eligible) - len(indeterminate),
            "enrollment_gap": max(0, (study.target_enrollment or 0) - study.enrollments.filter(
                status="enrolled").count()),
            "candidates": results,
        }

    def discover_rare_disease_cohorts(self) -> list[dict]:
        """Find patients with rare GN suitable for registry studies."""
        rare_diagnoses = Patient.objects.exclude(
            primary_diagnosis__in=["", "LN", "IgAN", "MCD", "MN", "MPGN"]
        ).values_list("primary_diagnosis", flat=True).distinct()

        cohorts = []
        for dx in rare_diagnoses:
            count = Patient.objects.filter(primary_diagnosis=dx).count()
            cohorts.append({
                "diagnosis": dx,
                "patient_count": count,
                "registry_eligible": count >= 3,  # minimum for natural history
                "suggested_study_type": "observational" if count < 20 else "quasi_experimental",
            })
        return sorted(cohorts, key=lambda c: -c["patient_count"])
```

### 3.4 Missing Variable Detection and Reporting

```python
# studies/services/missing_data.py

class MissingDataDetector:
    """Detect missing variables that would enable eligibility screening."""

    def analyze_study_gaps(self, study: Study) -> dict:
        """Report which data points are most frequently missing for a study."""
        all_feature_keys = set()
        for criterion in list(study.inclusion_criteria.all()) + list(study.exclusion_criteria.all()):
            all_feature_keys.add(criterion.feature_key)

        missing_counts = {key: 0 for key in all_feature_keys}
        total_patients = Patient.objects.count()

        for patient in Patient.objects.all():
            features = EligibilityScreeningEngine(patient)._extract_features(patient)
            for key in all_feature_keys:
                if features.get(key) is None:
                    missing_counts[key] += 1

        return {
            "study_code": study.code,
            "total_patients": total_patients,
            "missing_summary": [
                {
                    "feature_key": key,
                    "missing_count": count,
                    "missing_pct": round(count / total_patients * 100, 1) if total_patients else 0,
                    "impact": self._assess_impact(key, study),
                }
                for key, count in sorted(missing_counts.items(), key=lambda x: -x[1])
            ],
            "top_recommendation": self._prioritize_data_collection(missing_counts, total_patients),
        }

    def patient_registry_completeness(self, patient) -> dict:
        """Score data completeness for research eligibility across all studies."""
        from studies.models import Study
        feature_scores = {}
        for study in Study.objects.filter(status__in=["recruiting", "active"]):
            all_keys = set()
            for c in study.inclusion_criteria.all():
                all_keys.add(c.feature_key)
            for c in study.exclusion_criteria.all():
                all_keys.add(c.feature_key)

            features = EligibilityScreeningEngine(patient)._extract_features(patient)
            for key in all_keys:
                if key not in feature_scores:
                    feature_scores[key] = {"present": 0, "total": 0}
                feature_scores[key]["total"] += 1
                if features.get(key) is not None:
                    feature_scores[key]["present"] += 1

        completeness = {}
        for key, scores in feature_scores.items():
            completeness[key] = round(scores["present"] / scores["total"] * 100, 1)

        overall = sum(completeness.values()) / len(completeness) if completeness else 0
        return {
            "patient_id": patient.patient_id,
            "overall_completeness_pct": round(overall, 1),
            "field_completeness": completeness,
            "data_gaps": [k for k, v in completeness.items() if v < 100],
        }

    def _assess_impact(self, feature_key, study) -> str:
        for c in study.inclusion_criteria.filter(feature_key=feature_key, is_mandatory=True):
            return "critical (mandatory inclusion criterion)"
        for c in study.exclusion_criteria.filter(feature_key=feature_key, is_mandatory=True):
            return "high (mandatory exclusion criterion)"
        return "moderate"

    def _prioritize_data_collection(self, missing_counts, total_patients) -> str:
        if not missing_counts:
            return "Data collection sufficient"
        worst = max(missing_counts, key=missing_counts.get)
        pct = missing_counts[worst] / total_patients * 100 if total_patients else 0
        return f"Priority: collect {worst} ({pct:.0f}% missing)"
```

### 3.5 Export-Ready Dataset Generation

```python
# studies/services/dataset_export.py

class DatasetExporter:
    """Generate analysis-ready datasets from the registry."""

    def export_study_dataset(self, study: Study, include_screening: bool = True) -> dict:
        """Generate a one-row-per-patient dataset for a study."""
        enrolled_patients = Patient.objects.filter(
            enrollments__study=study,
            enrollments__status__in=["enrolled", "completed"]
        ).distinct()

        rows = []
        for patient in enrolled_patients:
            row = self._extract_analysis_row(patient)
            if include_screening:
                screening = EligibilityScreening.objects.filter(
                    patient=patient, study=study
                ).order_by("-screened_at").first()
                if screening:
                    row["screening_score"] = screening.overall_score
                    row["missing_data_count"] = len(screening.missing_data)
            rows.append(row)

        return {
            "study_code": study.code,
            "n_patients": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
            "rows": rows,
            "generated_at": str(dt.datetime.now()),
        }

    def export_cohort_dataset(self, filters: dict) -> dict:
        """Export a custom cohort dataset with flexible filters."""
        patients = Patient.objects.all()
        if filters.get("diagnoses"):
            patients = patients.filter(primary_diagnosis__in=filters["diagnoses"])
        if filters.get("phases"):
            patients = patients.filter(current_phase__in=filters["phases"])
        if filters.get("enrolled_after"):
            patients = patients.filter(enrollment_date__gte=filters["enrolled_after"])

        return {
            "n_patients": patients.count(),
            "rows": [self._extract_analysis_row(p) for p in patients],
        }

    def _extract_analysis_row(self, patient) -> dict:
        row = {
            "patient_id": patient.patient_id,
            "diagnosis": getattr(patient, "primary_diagnosis", ""),
            "phase": getattr(patient, "current_phase", ""),
            "sex": getattr(patient, "sex", ""),
            "enrollment_date": str(getattr(patient, "enrollment_date", "")),
        }
        if patient.dob:
            row["age_at_enrollment"] = round(
                (datetime.date.today() - patient.dob).days / 365.25, 1)

        row["latest_egfr"] = float(patient.latest_egfr) if patient.latest_egfr else None
        from labs.models import LabResult
        upcr = LabResult.objects.filter(
            patient=patient, test__code__in=("upcr", "utp_24h")
        ).order_by("-result_date").first()
        row["latest_upcr"] = float(upcr.value_numeric) if upcr and upcr.value_numeric else None

        # Outcome linkage
        if hasattr(patient, "outcome"):
            o = patient.outcome
            row["complete_remission"] = o.complete_remission
            row["eskd"] = o.eskd
            row["death"] = o.death
            row["egfr_slope"] = float(o.egfr_slope) if o.egfr_slope else None
        return row
```

### 3.6 Registry Completeness Scoring

```python
# studies/services/completeness.py

class RegistryCompletenessScorer:
    """Score data completeness for research readiness."""

    REQUIRED_FIELDS = {
        "demographics": ["dob", "sex", "enrollment_date", "primary_diagnosis"],
        "labs": ["egfr", "upcr", "albumin", "creatinine"],
        "biopsy": ["has_biopsy", "histological_diagnosis"],
        "treatment": ["treatment_history", "current_treatment"],
        "outcomes": ["latest_egfr_date", "remission_status"],
    }

    def score_patient(self, patient) -> dict:
        scores = {}
        features = self._extract_all_fields(patient)
        for category, fields in self.REQUIRED_FIELDS.items():
            present = sum(1 for f in fields if features.get(f) is not None)
            scores[category] = round(present / len(fields) * 100, 1)

        overall = sum(scores.values()) / len(scores)
        return {
            "patient_id": patient.patient_id,
            "overall_score": round(overall, 1),
            "category_scores": scores,
            "fields_missing": [f for f, v in features.items() if v is None],
        }

    def score_registry(self) -> dict:
        patients = Patient.objects.all()
        patient_scores = [self.score_patient(p) for p in patients]
        return {
            "total_patients": len(patient_scores),
            "mean_completeness": round(
                sum(s["overall_score"] for s in patient_scores) / len(patient_scores), 1
            ) if patient_scores else 0,
            "category_averages": {
                cat: round(sum(s["category_scores"][cat] for s in patient_scores) / len(patient_scores), 1)
                for cat in self.REQUIRED_FIELDS
            } if patient_scores else {},
            "below_80pct": sum(1 for s in patient_scores if s["overall_score"] < 80),
        }
```

---

## 4. Service Layer Architecture

### 4.1 Component Integration

| Existing Component | Integration |
|---|---|
| `studies.models.Study` | New FK relationships to `InclusionCriterion`, `ExclusionCriterion` |
| `studies.models.StudyEnrollment` | `screening` OneToOne from `EligibilityScreening` |
| `research_intelligence.discover_cohorts()` | Replaced by `DynamicCohortDiscovery` |
| `research_intelligence.match_patient_to_protocols()` | Replaced by `EligibilityScreeningEngine.screen_all_studies()` |
| `research_intelligence.detect_research_opportunities()` | Enhanced to consider study-specific criteria |
| `ClinicalInsight` (RESEARCH) | Auto-generated on eligibility detection |
| `FollowUpTask` (research_visit_due) | Generated from `ResearchFollowUp` schedule |

### 4.2 New Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/studies/<code>/screening/potential/` | List potential candidates |
| POST | `/api/studies/<code>/screen/patient/<id>/` | Run eligibility screening |
| GET | `/api/studies/<code>/missing-data/` | Missing variable analysis |
| GET | `/api/studies/<code>/dataset/` | Export analysis-ready dataset |
| GET | `/api/studies/recruitment-dashboard/` | Recruitment metrics |
| GET | `/api/patient/<id>/research-eligibility/` | Patient eligibility across all studies |
| GET | `/api/patient/<id>/registry-completeness/` | Data completeness score |
| GET | `/api/studies/cohort-discovery/` | Dynamic cohort discovery |
| POST | `/api/studies/<code>/generate-followups/` | Generate research visit schedule |

### 4.3 Management Commands

| Command | Description |
|---|---|
| `screen_all_patients` | Batch-screen all patients against all recruiting studies |
| `generate_research_followups` | Generate `ResearchFollowUp` schedules for enrolled patients |
| `export_study_dataset` | Export CSV/JSON dataset for a study |
| `registry_completeness_report` | Generate completeness scorecard |

---

## 5. Implementation Plan

### Phase 1: Eligibility Models (Week 1-2)

| Task | Files | Depends On |
|---|---|---|
| Create `InclusionCriterion` model | `studies/models.py` | — |
| Create `ExclusionCriterion` model | `studies/models.py` | — |
| Create `EligibilityScreening` model | `studies/models.py` | — |
| Create `ResearchFollowUp` model | `studies/models.py` | — |
| Run migrations | — | All above |
| Unit tests for criterion evaluation (25+ tests) | `studies/tests/` | — |

### Phase 2: Screening Engine (Week 2-3)

| Task | Files | Depends On |
|---|---|---|
| Implement `EligibilityScreeningEngine` | `studies/services/eligibility.py` | Phase 1 |
| Feature extraction service | `studies/services/features.py` | Phase 1 |
| Auto-insight generation | Integration with `ClinicalInsight` | Phase 1 |
| Populate IgAN study criteria (20+ criteria) | `studies/fixtures/criteria_iga.json` | Phase 1 |
| Populate MN study criteria | `studies/fixtures/criteria_membranous.json` | Phase 1 |
| Screening engine test suite (30+ tests) | `studies/tests/` | Phase 1-2 |

### Phase 3: Cohort Discovery & Missing Data (Week 3-4)

| Task | Files | Depends On |
|---|---|---|
| Implement `DynamicCohortDiscovery` | `studies/services/cohort_discovery.py` | Phase 2 |
| Implement `MissingDataDetector` | `studies/services/missing_data.py` | Phase 1 |
| Registry completeness scorer | `studies/services/completeness.py` | Phase 1 |
| Management commands | `studies/management/commands/` | Phase 1-3 |
| Test suite (20+ tests) | `studies/tests/` | Phase 1-3 |

### Phase 4: Dataset Export & Research Follow-up (Week 4-5)

| Task | Files | Depends On |
|---|---|---|
| Implement `DatasetExporter` | `studies/services/dataset_export.py` | Phase 1 |
| Research follow-up generation | `studies/services/research_followup.py` | Phase 1 |
| CSV/JSON export endpoints | `studies/views.py` | Phase 1-4 |
| Research visit compliance tracking | `studies/services/compliance.py` | Phase 4 |
| Integration with `FollowUpTask` | `followup/signals.py` | Phase 4 |

### Phase 5: Dashboard & Validation (Week 5-6)

| Task | Files | Depends On |
|---|---|---|
| Recruitment dashboard view | `studies/views.py`, templates | Phase 1-4 |
| HTMX partials for real-time metrics | `studies/templates/studies/partials/` | Phase 1-4 |
| Clinical validation: 10 study protocols | `studies/tests/validation/` | Phase 1-4 |
| Performance benchmark: 1000 patients × 5 studies | `studies/tests/performance/` | Phase 1-4 |

---

## 6. Success Criteria

| Metric | Target | Measurement |
|---|---|---|
| Eligibility screening accuracy | >95% concordance with manual review | Compare 50 screenings with nephrologist |
| Screening speed | <2 seconds per patient per study | Benchmark with 1000-patient cohort |
| Missing data detection | 100% of required features flagged | Validate against criterion definitions |
| Auto-generated insights | >80% clinically actionable | Clinician review of 50 RESEARCH insights |
| Dataset export completeness | 100% of required fields present | Validate exported datasets |
| Registry completeness score | >85% mean across all fields | Automated score on live data |
| Research follow-up compliance | >90% visits completed on time | Compliance rate from `ResearchFollowUp` |
| Cohort discovery recall | >95% of eligible patients identified | Validation against manual chart review |

---

## 7. Risk Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Criterion definitions are clinically inaccurate | High | All criteria require nephrologist review; version-controlled with audit trail |
| Performance degradation with large patient cohorts | Medium | Pre-filter by diagnosis/phase before full screening; async batch screening |
| False-positive eligibility (patient screened eligible but fails detailed review) | Medium | Screening is advisory; final eligibility requires clinician confirmation |
| Data privacy in dataset export | High | Export requires authenticated + authorized access; PHI fields anonymizable |
| Criteria maintenance burden | Medium | Template-based criteria per disease; copy-from-study for similar protocols |
