"""
Safety analytics — adverse-event summaries, infection incidence by drug/diabetes
(Study 20), and per-study SAE tabulation for the DSMB.

Person-time comes from the outcome engine's follow-up window, so infection rates
are incidence densities (events per 100 patient-years).
"""
from __future__ import annotations

from collections import Counter

from analytics.models import PatientOutcome
from analytics.services.cohort import split_patients
from safety.models import AdverseEvent


def safety_summary(queryset):
    """Counts of adverse events over a patient queryset."""
    aes = AdverseEvent.objects.filter(patient__in=queryset)
    by_category = Counter(aes.values_list("category", flat=True))
    by_severity = Counter(aes.values_list("severity", flat=True))
    infections = aes.filter(category=AdverseEvent.Category.INFECTION)
    by_infection = Counter(infections.values_list("infection_type", flat=True))
    return {
        "n_patients": queryset.count(),
        "n_events": aes.count(),
        "n_serious": aes.filter(serious=True).count(),
        "n_hospitalizations": aes.filter(hospitalization=True).count(),
        "n_infections": infections.count(),
        "by_category": dict(by_category),
        "by_severity": dict(by_severity),
        "by_infection_type": dict(by_infection),
    }


def _person_years(patients):
    days = (PatientOutcome.objects
            .filter(patient__in=patients, followup_days__isnull=False)
            .values_list("followup_days", flat=True))
    return sum(days) / 365.25 if days else 0.0


def infection_incidence(queryset, group_by="diabetes", *, per=100):
    """Infection incidence density per ``per`` patient-years, split by group
    (e.g. 'diabetes' or 'drug:steroid'). Directly answers Study 20."""
    groups = split_patients(queryset, group_by)
    rows = []
    for label, patients in sorted(groups.items()):
        py = _person_years(patients)
        n_inf = (AdverseEvent.objects
                 .filter(patient__in=patients,
                         category=AdverseEvent.Category.INFECTION).count())
        n_serious_inf = (AdverseEvent.objects
                         .filter(patient__in=patients,
                                 category=AdverseEvent.Category.INFECTION,
                                 serious=True).count())
        rate = round(n_inf / py * per, 2) if py > 0 else None
        rows.append({
            "group": label, "n_patients": len(patients),
            "person_years": round(py, 2), "n_infections": n_inf,
            "n_serious_infections": n_serious_inf,
            f"infections_per_{per}py": rate,
        })
    return {"group_by": group_by, "rows": rows}


def study_safety(study):
    """Per-arm SAE / infection counts for an enrolled study (DSMB review)."""
    from studies.models import StudyEnrollment
    enrolled = (StudyEnrollment.objects
                .filter(study=study, status=StudyEnrollment.Status.ENROLLED,
                        arm__isnull=False)
                .select_related("arm"))
    arm_of = {e.patient_id: e.arm.code for e in enrolled}
    patient_ids = list(arm_of)

    by_arm: dict[str, dict] = {}
    aes = (AdverseEvent.objects.filter(patient_id__in=patient_ids))
    for ae in aes:
        arm = arm_of[ae.patient_id]
        d = by_arm.setdefault(arm, {"events": 0, "serious": 0, "infections": 0,
                                    "deaths": 0})
        d["events"] += 1
        if ae.serious:
            d["serious"] += 1
        if ae.category == AdverseEvent.Category.INFECTION:
            d["infections"] += 1
        if ae.outcome == AdverseEvent.Outcome.FATAL or ae.severity == AdverseEvent.Severity.FATAL:
            d["deaths"] += 1
    return {"study": study.code, "by_arm": by_arm,
            "n_enrolled": len(patient_ids)}
