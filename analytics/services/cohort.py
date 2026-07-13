"""
Cohort analysis — split a patient population by a research dimension and compare
outcomes, with survival curves and a log-rank test between groups.

Grouping dimensions (``group_by``):
  "diabetes"          diabetic vs non-diabetic  (BIRDEM's distinguishing niche)
  "diagnosis"         by primary GN diagnosis
  "cohort"            by registry cohort field
  "drug:<class>"      ever-exposed vs never-exposed to a DrugMaster drug_class,
                      e.g. "drug:sglt2i", "drug:hcq", "drug:finerenone"
"""
from __future__ import annotations

from dataclasses import dataclass, field

from treatments.models import TreatmentExposure
from patients.models import Patient

from analytics.models import PatientOutcome
from . import survival as S
from . import cox as C
from .competing_risks import cif_at, compare_cif_at, cumulative_incidence, final_cif
from .mixed_model import egfr_slope_lmm


def _exposed_patient_ids(drug_class):
    return set(TreatmentExposure.objects
              .filter(drug__drug_class=drug_class)
              .values_list("patient_id", flat=True))


def split_patients(queryset, group_by: str) -> dict[str, list]:
    groups: dict[str, list] = {}
    if group_by == "diabetes":
        for p in queryset:
            label = "Non-diabetic" if p.diabetes_status == "none" else "Diabetic"
            groups.setdefault(label, []).append(p)
    elif group_by == "diagnosis":
        for p in queryset:
            groups.setdefault(p.primary_diagnosis or "Unspecified", []).append(p)
    elif group_by == "cohort":
        for p in queryset:
            groups.setdefault(p.cohort or "Unassigned", []).append(p)
    elif group_by.startswith("drug:"):
        drug_class = group_by.split(":", 1)[1]
        exposed = _exposed_patient_ids(drug_class)
        for p in queryset:
            label = f"{drug_class} exposed" if p.id in exposed else f"{drug_class} unexposed"
            groups.setdefault(label, []).append(p)
    elif group_by == "biomarker:pla2r_response":
        # Early (>=50% within 90d) anti-PLA2R responders vs not — Study 6.
        from biomarkers.models import BiomarkerKinetics
        bks = {bk.patient_id: bk for bk in BiomarkerKinetics.objects
               .filter(patient__in=queryset, pla2r_baseline__isnull=False)}
        for p in queryset:
            bk = bks.get(p.id)
            if bk is None:
                continue
            label = ("PLA2R early responder" if bk.early_pla2r_responder()
                     else "PLA2R non-responder")
            groups.setdefault(label, []).append(p)
    elif group_by.startswith("study:"):
        # Intention-to-treat grouping by randomized arm for a study's enrollees.
        from studies.models import StudyEnrollment
        study_code = group_by.split(":", 1)[1]
        arm_by_patient = dict(
            StudyEnrollment.objects
            .filter(study__code=study_code, status=StudyEnrollment.Status.ENROLLED,
                    arm__isnull=False)
            .values_list("patient_id", "arm__code"))
        for p in queryset:
            if p.id in arm_by_patient:
                groups.setdefault(f"arm:{arm_by_patient[p.id]}", []).append(p)
    else:
        raise ValueError(f"Unknown group_by: {group_by!r}")
    return groups


@dataclass
class GroupResult:
    label: str
    n: int
    n_events: int
    person_years: float
    incidence_per_100py: float | None
    median_survival_days: float | None
    km: list = field(default_factory=list)

    def km_as_dicts(self):
        return [vars(s) for s in self.km]


@dataclass
class CohortSurvival:
    endpoint: str
    group_by: str
    groups: list[GroupResult]
    logrank: dict | None = None   # populated when exactly two groups


def _durations_events(patients, endpoint):
    durations, events = [], []
    for p in patients:
        outcome = getattr(p, "outcome", None) or _safe_outcome(p)
        if outcome is None:
            continue
        de = outcome.duration_event(endpoint)
        if de is None or de[0] is None or de[0] < 0:
            continue
        durations.append(de[0])
        events.append(de[1])
    return durations, events


def _safe_outcome(patient):
    return PatientOutcome.objects.filter(patient=patient).first()


def cohort_survival(queryset, group_by: str, endpoint: str) -> CohortSurvival:
    groups = split_patients(queryset, group_by)
    results: list[GroupResult] = []
    series_by_label = {}

    for label, patients in sorted(groups.items()):
        durations, events = _durations_events(patients, endpoint)
        series_by_label[label] = (durations, events)
        km = S.kaplan_meier(durations, events) if durations else []
        rate, n_events, py = S.incidence_rate(durations, events) if durations else (None, 0, 0.0)
        results.append(GroupResult(
            label=label, n=len(durations), n_events=n_events,
            person_years=py, incidence_per_100py=(round(rate, 2) if rate else None),
            median_survival_days=S.median_survival(km), km=km))

    cohort = CohortSurvival(endpoint=endpoint, group_by=group_by, groups=results)

    # Log-rank when exactly two non-empty groups.
    nonempty = [(lbl, s) for lbl, s in series_by_label.items() if s[0]]
    if len(nonempty) == 2:
        (l1, (d1, e1)), (l2, (d2, e2)) = nonempty
        lr = S.logrank_test(d1, e1, d2, e2)
        cohort.logrank = {
            "group1": l1, "group2": l2,
            "chi_square": lr.chi_square, "p_value": lr.p_value, "df": lr.df,
            "observed_group1": lr.observed_group1,
            "expected_group1": lr.expected_group1,
        }
    return cohort


# --- Cox proportional-hazards -------------------------------------------------
def _age_at(patient, on_date):
    if not patient.dob or not on_date:
        return None
    return (on_date.year - patient.dob.year
            - ((on_date.month, on_date.day) < (patient.dob.month, patient.dob.day)))


def _covariate_value(patient, outcome, spec, exposed_cache):
    """Resolve one covariate spec to a float, or None if unavailable.

    Supported specs: age, female, diabetes, baseline_egfr, baseline_upcr,
    drug:<class> (ever-exposed 1/0).
    """
    if spec == "age":
        return _age_at(patient, outcome.index_date)
    if spec == "female":
        return 1.0 if patient.sex == "F" else 0.0
    if spec == "diabetes":
        return 0.0 if patient.diabetes_status == "none" else 1.0
    if spec == "baseline_egfr":
        return float(outcome.baseline_egfr) if outcome.baseline_egfr is not None else None
    if spec == "baseline_upcr":
        return float(outcome.baseline_upcr) if outcome.baseline_upcr is not None else None
    if spec.startswith("drug:"):
        drug_class = spec.split(":", 1)[1]
        if drug_class not in exposed_cache:
            exposed_cache[drug_class] = _exposed_patient_ids(drug_class)
        return 1.0 if patient.id in exposed_cache[drug_class] else 0.0
    raise ValueError(f"Unknown covariate spec: {spec!r}")


def build_cox_design(queryset, covariate_specs, endpoint):
    """Build (X, durations, events, names, n_dropped) for cox_fit. Patients
    missing the endpoint window or any covariate are dropped."""
    X, durations, events = [], [], []
    dropped = 0
    exposed_cache = {}
    for p in queryset:
        outcome = _safe_outcome(p)
        if outcome is None:
            dropped += 1
            continue
        de = outcome.duration_event(endpoint)
        if de is None or de[0] is None or de[0] < 0:
            dropped += 1
            continue
        row = [_covariate_value(p, outcome, s, exposed_cache) for s in covariate_specs]
        if any(v is None for v in row):
            dropped += 1
            continue
        X.append(row)
        durations.append(de[0])
        events.append(de[1])
    return X, durations, events, list(covariate_specs), dropped


def cox_regression(queryset, covariate_specs, endpoint):
    """Fit a multivariable Cox model over a cohort. Returns (CoxResult-as-dict,
    meta) or raises ValueError with a readable message."""
    X, durations, events, names, dropped = build_cox_design(
        queryset, covariate_specs, endpoint)
    if not X:
        raise ValueError("No patients with complete data for these covariates/endpoint.")
    result = C.cox_fit(X, durations, events, names)
    meta = {"endpoint": endpoint, "covariates_requested": list(covariate_specs),
            "n_dropped_incomplete": dropped}
    return result.as_dict(), meta


def cohort_egfr_slope(queryset, group_by: str):
    """Mixed-model eGFR slope comparison between two groups (protocol §10.3)."""
    from labs.models import LabResult
    groups = split_patients(queryset, group_by)
    series_by_group = {}
    for label, patients in groups.items():
        sl = []
        for p in patients:
            s = [(r.result_date, float(r.value_numeric))
                 for r in LabResult.series(p, "egfr") if r.value_numeric is not None]
            if len(s) >= 2:
                sl.append(s)
        if sl:
            series_by_group[label] = sl
    if len(series_by_group) != 2:
        return {"error": "Need exactly two groups with longitudinal eGFR data.",
                "groups_with_data": list(series_by_group)}
    return egfr_slope_lmm(series_by_group)


def _competing_record(outcome):
    """(time_days, status) for competing-risks CIF: 1 = kidney event (ESKD or
    >=50% eGFR decline), 2 = death (competing), 0 = censored."""
    if not outcome or not outcome.index_date or not outcome.last_contact_date:
        return None
    idx = outcome.index_date
    kidney = min([d for d in (outcome.eskd_date, outcome.sustained_50_date) if d],
                 default=None)
    candidates = []
    if kidney:
        candidates.append((kidney, 1))
    if outcome.death_date:
        candidates.append((outcome.death_date, 2))
    if candidates:
        d, status = min(candidates)
        return ((d - idx).days, status)
    return ((outcome.last_contact_date - idx).days, 0)


def cohort_competing_risks(queryset, group_by: str, *, at_days=365):
    """Cause-specific cumulative incidence of the kidney endpoint with death as a
    competing risk (protocol §10.4), per group, with a pointwise comparison."""
    groups = split_patients(queryset, group_by)
    data_by_group, rows = {}, []
    for label, patients in sorted(groups.items()):
        recs = [r for r in (_competing_record(_safe_outcome(p)) for p in patients) if r]
        data_by_group[label] = recs
        steps = cumulative_incidence(recs, cause=1) if recs else []
        n_events = sum(1 for _, s in recs if s == 1)
        n_competing = sum(1 for _, s in recs if s == 2)
        rows.append({"label": label, "n": len(recs), "n_kidney_events": n_events,
                     "n_competing_deaths": n_competing,
                     f"cif_at_{at_days}d": cif_at(steps, at_days),
                     "final_cif": final_cif(steps)})
    out = {"group_by": group_by, "at_days": at_days, "groups": rows}
    nonempty = [(k, v) for k, v in data_by_group.items() if v]
    if len(nonempty) == 2:
        out["comparison"] = compare_cif_at(nonempty[0][1], nonempty[1][1], at_days)
    return out


def cohort_summary(queryset, group_by: str) -> list[dict]:
    """Baseline + outcome summary per group (counts, not survival)."""
    groups = split_patients(queryset, group_by)
    rows = []
    for label, patients in sorted(groups.items()):
        outcomes = [o for o in (_safe_outcome(p) for p in patients) if o]
        n = len(outcomes)
        def rate(attr):
            return sum(1 for o in outcomes if getattr(o, attr)) if n else 0
        egfrs = [float(o.baseline_egfr) for o in outcomes if o.baseline_egfr is not None]
        rows.append({
            "group": label, "n_patients": len(patients), "n_with_outcome": n,
            "baseline_egfr_mean": round(sum(egfrs) / len(egfrs), 1) if egfrs else None,
            "eskd": rate("eskd"), "death": rate("death"),
            "composite_kidney_event": rate("composite_kidney_event"),
            "complete_remission": sum(1 for o in outcomes
                                      if o.remission_status == "complete"),
        })
    return rows
