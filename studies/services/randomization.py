"""
Randomization + enrollment engine.

Allocations are produced by a deterministic, seeded sequence so they are
reproducible and auditable: given the study seed, the stratum, and the arm
definitions, the n-th allocation is fixed. Supported schemes:

    simple            independent weighted draws
    block             permuted blocks (balance within each block)
    stratified_block  permuted blocks within strata (balance + comparability)

Enrolment enforces two gates before allocating: the patient must pass screening,
and (for trials that require it) trial consent must be on file. Allocation is
recorded with who/when, and the whole StudyEnrollment is audited like any other
clinical record.
"""
from __future__ import annotations

import datetime as dt
import random
import zlib

from django.db import transaction
from django.utils import timezone

from audit.models import Consent
from audit.services.consent import has_consent
from studies.models import Study, StudyArm, StudyEnrollment

from .eligibility import screen


class ConsentRequired(Exception):
    def __init__(self, study, patient):
        super().__init__(
            f"Trial consent (TRIAL) is required before enrolling "
            f"{patient.patient_id} in {study.code}.")


class AlreadyEnrolled(Exception):
    pass


# --- stratification ----------------------------------------------------------
def _egfr_stratum(egfr):
    if egfr is None:
        return "unknown"
    egfr = float(egfr)
    if egfr >= 60:
        return "ge60"
    if egfr >= 30:
        return "30to59"
    if egfr >= 15:
        return "15to29"
    return "lt15"


def _factor(patient, factor):
    if factor == "diabetes":
        return "DM" if patient.diabetes_status != "none" else "noDM"
    if factor == "egfr_stratum":
        return _egfr_stratum(patient.latest_egfr)
    if factor == "egfr_30":
        # Protocol §5.3 cut-point: eGFR >= 30 vs < 30 mL/min/1.73m2.
        e = patient.latest_egfr
        return "unknown" if e is None else ("ge30" if float(e) >= 30 else "lt30")
    if factor == "proteinuria_range":
        # Nephrotic (>= 3.5 g/day-equiv) vs non-nephrotic, from latest outcome.
        from analytics.models import PatientOutcome
        o = PatientOutcome.objects.filter(patient=patient).first()
        p = o.latest_upcr if o else None
        return "unknown" if p is None else ("nephrotic" if float(p) >= 3.5 else "nonnephrotic")
    if factor == "gn_subtype":
        from analytics.services.remission import disease_key
        return disease_key(patient.primary_diagnosis or "")
    if factor == "sex":
        return patient.sex or "U"
    raise ValueError(f"Unknown stratification factor: {factor!r}")


def compute_stratum(study, patient):
    if study.randomization_scheme != Study.Scheme.STRATIFIED_BLOCK or not study.stratify_by:
        return "all"
    return "|".join(f"{f}={_factor(patient, f)}" for f in study.stratify_by)


# --- allocation sequence -----------------------------------------------------
def _stratum_rng(study, stratum):
    base = (int(study.random_seed) * 1000003) ^ zlib.crc32(stratum.encode("utf-8"))
    return random.Random(base & 0xFFFFFFFFFFFF)


def _ratio_unit(arms):
    unit = []
    for a in arms:
        unit += [a.code] * a.ratio
    return unit


def generate_sequence(study, arms, stratum, n):
    """The first n allocations for a stratum — deterministic given the seed."""
    rng = _stratum_rng(study, stratum)
    unit = _ratio_unit(arms)
    if not unit:
        return []
    if study.randomization_scheme == Study.Scheme.SIMPLE:
        return [rng.choice(unit) for _ in range(n)]
    multipliers = study.block_multipliers or [1]
    seq = []
    while len(seq) < n:
        block = unit * rng.choice(multipliers)
        rng.shuffle(block)
        seq.extend(block)
    return seq[:n]


def _next_position(study, stratum, exclude_pk=None):
    qs = StudyEnrollment.objects.filter(
        study=study, stratum=stratum, arm__isnull=False)
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return qs.count()


# --- public API --------------------------------------------------------------
@transaction.atomic
def enroll(study, patient, *, by=None, screened_date=None, enrolled_date=None,
           require_consent=None):
    """Screen and enrol a patient. For randomized studies this also allocates an
    arm via the seeded sequence. Returns the StudyEnrollment.

    Raises ConsentRequired if trial consent is needed and absent, ValueError if
    the patient is already enrolled."""
    today = dt.date.today()
    existing = (StudyEnrollment.objects.select_for_update()
                .filter(study=study, patient=patient).first())
    if existing and existing.status == StudyEnrollment.Status.ENROLLED:
        raise AlreadyEnrolled(
            f"{patient.patient_id} already enrolled in {study.code}.")

    enr = existing or StudyEnrollment(study=study, patient=patient)
    enr.screened_date = screened_date or today

    eligible, reasons = screen(study, patient)
    enr.eligible = eligible
    enr.ineligibility_reasons = reasons
    if not eligible:
        enr.status = StudyEnrollment.Status.INELIGIBLE
        enr.save()
        return enr

    needs_consent = (study.requires_trial_consent
                     if require_consent is None else require_consent)
    if needs_consent and not has_consent(patient, Consent.Type.TRIAL):
        enr.status = StudyEnrollment.Status.SCREENED
        enr.save()
        raise ConsentRequired(study, patient)

    if study.is_randomized:
        stratum = compute_stratum(study, patient)
        position = _next_position(study, stratum, exclude_pk=enr.pk)
        arms = study.arms_ordered()
        if not arms:
            raise ValueError(f"Study {study.code} has no arms to allocate.")
        seq = generate_sequence(study, arms, stratum, position + 1)
        arm_code = seq[position]
        enr.arm = next(a for a in arms if a.code == arm_code)
        enr.stratum = stratum
        enr.sequence_position = position
        enr.randomized_by = by
        enr.randomized_at = timezone.now()

    enr.status = StudyEnrollment.Status.ENROLLED
    enr.enrolled_date = enrolled_date or today
    enr.save()
    return enr


def withdraw(enrollment, *, withdrawn_date=None):
    enrollment.status = StudyEnrollment.Status.WITHDRAWN
    enrollment.withdrawn_date = withdrawn_date or dt.date.today()
    enrollment.save(update_fields=["status", "withdrawn_date"])
    return enrollment


def study_dashboard(study):
    """CONSORT-style counts: screening funnel, per-arm and per-stratum balance."""
    enrollments = list(study.enrollments.select_related("arm"))
    by_status = {}
    for e in enrollments:
        by_status[e.status] = by_status.get(e.status, 0) + 1

    by_arm, by_stratum_arm = {}, {}
    for e in enrollments:
        if e.arm:
            by_arm[e.arm.code] = by_arm.get(e.arm.code, 0) + 1
            key = e.stratum or "all"
            by_stratum_arm.setdefault(key, {})
            by_stratum_arm[key][e.arm.code] = by_stratum_arm[key].get(e.arm.code, 0) + 1

    return {
        "study": study.code, "title": study.title,
        "scheme": study.randomization_scheme,
        "target_enrollment": study.target_enrollment,
        "screened": len(enrollments),
        "by_status": by_status,
        "enrolled_by_arm": by_arm,
        "balance_by_stratum": by_stratum_arm,
    }
