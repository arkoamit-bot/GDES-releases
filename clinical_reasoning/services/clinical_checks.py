"""Shared clinical utility functions to eliminate N+1 and duplicated logic."""
from datetime import date, timedelta

from django.db.models import Exists, OuterRef, Q


def patients_missing_biopsy_queryset(Patient):
    """Return a queryset of patients without any biopsy."""
    from pathology.models import Biopsy
    return Patient.objects.filter(
        ~Exists(Biopsy.objects.filter(patient=OuterRef("pk")))
    )


def patients_missing_egfr_queryset(Patient):
    """Return a queryset of patients with null latest_egfr."""
    return Patient.objects.filter(latest_egfr__isnull=True)


def patients_overdue_queryset(Patient, days: int = 180):
    """Return a queryset of patients without a recent encounter."""
    from encounters.models import ClinicalEncounter
    cutoff = date.today() - timedelta(days=days)
    has_recent = Exists(
        ClinicalEncounter.objects.filter(
            patient=OuterRef("pk"), encounter_date__gte=cutoff
        )
    )
    return Patient.objects.filter(
        Q(~has_recent) | Q(encounters__isnull=True)
    ).distinct()


def check_biopsy_exists(patient) -> bool:
    try:
        return patient.biopsies.exists()
    except Exception:
        return False


def check_egfr_exists(patient) -> bool:
    return getattr(patient, "latest_egfr", None) is not None


def check_overdue_visit(patient, days: int = 180) -> tuple[bool, date | None]:
    """Returns (is_overdue, latest_encounter_date)."""
    try:
        latest = patient.encounters.order_by("-encounter_date").first()
        if latest is None:
            return True, None
        cutoff = date.today() - timedelta(days=days)
        if latest.encounter_date and latest.encounter_date < cutoff:
            return True, latest.encounter_date
        return False, latest.encounter_date
    except Exception:
        return True, None


def has_active_treatment(patient) -> bool:
    try:
        from treatments.models import TreatmentExposure
        return TreatmentExposure.objects.filter(patient=patient, ongoing=True).exists()
    except Exception:
        return False
