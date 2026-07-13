"""
GN management workflow engine — the phase state machine (workflow step 5).

Keeps `Patient.current_phase` in sync with what happens clinically:

    (register) ──► ACTIVE ──complete──► REMISSION ──stable──► POST_REMISSION
                     ▲                                              │
                     └──────────────── RELAPSE ◄────(record_relapse)┘

The clinician can always override the phase explicitly on a visit; otherwise it
is derived from their per-visit response assessment. This is the *clinician-
driven* side of the hybrid model — the lab-based outcome engine
(analytics/services/outcomes.py) still computes remission/relapse independently,
so the two can be compared (clinical vs. biochemical concordance).
"""
from __future__ import annotations

import datetime as dt

from patients.workflow import (ClinicianResponse, DiseasePhase,
                               RegistrationStatus)


def register_patient(patient, date=None, by=None):
    """Register a suspected patient into structured GN follow-up (step 4)."""
    patient.registration_status = RegistrationStatus.REGISTERED
    patient.registration_date = date or dt.date.today()
    if not patient.current_phase:
        patient.current_phase = DiseasePhase.ACTIVE
    patient.save(update_fields=["registration_status", "registration_date",
                                "current_phase", "updated_at"])
    return patient


def derive_phase(patient, response, explicit=""):
    """Next phase given the current phase + the visit's clinician response.
    `explicit` (a DiseasePhase value) always wins — clinician override."""
    if explicit:
        return explicit
    cur = patient.current_phase or DiseasePhase.ACTIVE
    if response == ClinicianResponse.COMPLETE:
        return DiseasePhase.REMISSION
    if response == ClinicianResponse.STABLE and cur in (
            DiseasePhase.REMISSION, DiseasePhase.POST_REMISSION):
        return DiseasePhase.POST_REMISSION
    # partial / none / not-assessed: hold the current phase (a true relapse out
    # of remission is documented explicitly via record_relapse()).
    return cur or DiseasePhase.ACTIVE


def apply_visit(encounter):
    """Advance the patient's phase from a saved follow-up encounter. Writes the
    derived phase back onto the encounter so the visit carries the trajectory."""
    patient = encounter.patient
    if patient.registration_status != RegistrationStatus.REGISTERED:
        return  # phase is only meaningful once registered
    new = derive_phase(patient, encounter.clinician_response,
                       explicit=encounter.disease_phase)
    if new != encounter.disease_phase:
        encounter.disease_phase = new
        encounter.save(update_fields=["disease_phase"])
    if new != patient.current_phase:
        patient.current_phase = new
        patient.save(update_fields=["current_phase", "updated_at"])


def record_relapse(patient, relapse_date, relapse_type, *, criteria="",
                   action_taken="", encounter=None, by=None):
    """Document a relapse (step 5E): create the RelapseEpisode, emit a matching
    ClinicalEvent so the survival engine sees it, and flip the phase to RELAPSE
    (re-entering active management)."""
    from encounters.models import ClinicalEvent, RelapseEpisode

    rel = RelapseEpisode.objects.create(
        patient=patient, encounter=encounter, relapse_date=relapse_date,
        relapse_type=relapse_type, criteria=criteria, action_taken=action_taken)
    ClinicalEvent.objects.create(
        patient=patient, event_type=ClinicalEvent.Type.RELAPSE,
        event_date=relapse_date, encounter=encounter,
        notes=f"{rel.get_relapse_type_display()}"
              + (f" — {criteria}" if criteria else ""))
    patient.current_phase = DiseasePhase.RELAPSE
    patient.save(update_fields=["current_phase", "updated_at"])
    return rel
