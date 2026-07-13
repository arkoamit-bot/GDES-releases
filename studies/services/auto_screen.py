"""Automatic eligibility screening.

Objective 4 (research platform) requires every patient to be *automatically*
evaluated for study eligibility. This service runs the encoded eligibility
criteria for the recruiting studies against a patient and records the result as
a screening ``StudyEnrollment`` — so eligible patients surface as trial
candidates without any manual screening step. It is wired to the domain-event
bus (see ``studies/event_handlers.py``) so it re-runs whenever the data that
drives eligibility changes (registration, diagnosis, eGFR, diabetes status, …).

Design decisions:
- Only studies with an **encoded** eligibility function are auto-screened.
  Studies without one are "open" and genuinely need manual screening, so we do
  not assert eligibility for them (that would flag every patient as eligible).
- Clinician decisions are never overwritten: records already in
  ``enrolled`` / ``withdrawn`` / ``completed`` are left untouched.
- We do not create clutter rows for patients who are ineligible and were never
  screened before; we only persist a record once a patient is eligible, and we
  keep existing screening records up to date (including flipping to
  ``ineligible`` if the patient later stops meeting criteria).
"""
from __future__ import annotations

import datetime as dt
import logging

from django.db import transaction

from studies.models import Study, StudyEnrollment
from studies.services.eligibility import ELIGIBILITY, screen

logger = logging.getLogger(__name__)

# Statuses that represent a clinician decision — auto-screen must not touch them.
_LOCKED = {
    StudyEnrollment.Status.ENROLLED,
    StudyEnrollment.Status.WITHDRAWN,
    StudyEnrollment.Status.COMPLETED,
}


@transaction.atomic
def auto_screen_patient(patient) -> dict:
    """Screen one patient against all recruiting studies that have criteria.

    Returns a small summary dict: {created, updated, eligible}.
    """
    recruiting = Study.objects.filter(
        status=Study.Status.RECRUITING,
        code__in=list(ELIGIBILITY.keys()),
    )

    created = updated = eligible_count = 0
    for study in recruiting:
        is_eligible, reasons = screen(study, patient)
        new_status = (
            StudyEnrollment.Status.SCREENED if is_eligible
            else StudyEnrollment.Status.INELIGIBLE
        )

        enr = StudyEnrollment.objects.filter(study=study, patient=patient).first()
        if enr is not None and enr.status in _LOCKED:
            continue  # respect clinician decision

        if enr is None:
            if not is_eligible:
                continue  # don't create clutter rows for never-eligible patients
            StudyEnrollment.objects.create(
                study=study,
                patient=patient,
                status=new_status,
                eligible=True,
                ineligibility_reasons=[],
                screened_date=dt.date.today(),
            )
            created += 1
        else:
            enr.eligible = is_eligible
            enr.ineligibility_reasons = reasons
            enr.status = new_status
            if enr.screened_date is None:
                enr.screened_date = dt.date.today()
            enr.save(update_fields=[
                "eligible", "ineligibility_reasons", "status", "screened_date",
            ])
            updated += 1

        if is_eligible:
            eligible_count += 1

    return {"created": created, "updated": updated, "eligible": eligible_count}


def auto_screen_all() -> dict:
    """Backfill: screen every patient. Used by the management command / one-off ops."""
    from patients.models import Patient

    totals = {"patients": 0, "created": 0, "updated": 0, "eligible": 0}
    for patient in Patient.objects.iterator():
        try:
            r = auto_screen_patient(patient)
        except Exception:
            logger.exception("Auto-screen failed for %s", getattr(patient, "patient_id", "?"))
            continue
        totals["patients"] += 1
        totals["created"] += r["created"]
        totals["updated"] += r["updated"]
        totals["eligible"] += r["eligible"]
    return totals
