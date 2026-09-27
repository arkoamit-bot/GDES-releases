"""Visit measurements: VitalSign rows own them, the encounter points at one.

Before this, a VitalSign linked to a visit and the visit's own BP/weight
columns were independent stores: a reading entered as a VitalSign never
reached the encounter, so the printout and clinical reasoning (which read the
encounter) did not see it.

Now every reading is a VitalSign (multiple per visit, in order, with times).
The encounter's ``selected_vital`` is the one it displays and prints, and its
legacy ``systolic_bp`` / ``diastolic_bp`` / ``weight_kg`` columns are a
projection of that reading. Baseline measurements are not merged in: a later
visit never rewrites the enrollment measurement.
"""
from __future__ import annotations

from django.db import transaction

PROJECTED = {"systolic_bp": "bp_systolic", "diastolic_bp": "bp_diastolic",
             "weight_kg": "weight_kg"}


def project(encounter, vital) -> list[str]:
    """Copy the selected reading onto the encounter's compatibility columns."""
    changed = []
    for enc_field, vital_field in PROJECTED.items():
        value = getattr(vital, vital_field) if vital is not None else None
        if getattr(encounter, enc_field) != value:
            setattr(encounter, enc_field, value)
            changed.append(enc_field)
    if encounter.selected_vital_id != (vital.pk if vital is not None else None):
        encounter.selected_vital = vital
        changed.append("selected_vital")
    if changed:
        encounter.save(update_fields=changed)
    return changed


def on_vital_saved(vital):
    """First reading of a visit becomes its selected reading; re-saving the
    selected reading refreshes the projection. A second reading is kept but
    does not silently replace the one the visit already shows."""
    from encounters.models import ClinicalEncounter
    encounter = ClinicalEncounter.objects.get(pk=vital.encounter_id)
    if encounter.selected_vital_id in (None, vital.pk):
        project(encounter, vital)


def select(encounter, vital, *, reason: str = "", user=None):
    """Explicitly choose which reading the visit displays and prints."""
    from audit.local import acting_as
    if vital.encounter_id != encounter.pk:
        raise ValueError("That reading belongs to a different visit.")
    with acting_as(user, reason=reason or "Selected displayed visit reading"):
        return project(encounter, vital)


def reselect_after_delete(encounter):
    encounter.refresh_from_db()
    if encounter.selected_vital_id is None:
        latest = encounter.vitals.order_by("-measured_at", "-recorded_at", "-id").first()
        project(encounter, latest)


@transaction.atomic
def record_visit_vitals(encounter, *, systolic=None, diastolic=None, weight_kg=None,
                        heart_rate=None, measured_at=None, source="visit_form",
                        select_it=True):
    """The one command the visit form (and API adapters) use to add a reading."""
    from clinical.models import VitalSign
    if all(v is None for v in (systolic, diastolic, weight_kg, heart_rate)):
        return None
    vital = VitalSign(encounter=encounter, bp_systolic=systolic, bp_diastolic=diastolic,
                      weight_kg=weight_kg, heart_rate=heart_rate,
                      measured_at=measured_at, source=source)
    vital.save()
    if select_it:
        encounter.refresh_from_db()
        project(encounter, vital)
    return vital


def adopt_legacy_encounter_values(encounter):
    """Represent an encounter's legacy BP/weight columns as a VitalSign row
    (used by reconcile_linked_facts). Idempotent: skips encounters that
    already have a selected reading or no values."""
    if encounter.selected_vital_id or all(
            getattr(encounter, f) is None for f in PROJECTED):
        return None
    return record_visit_vitals(
        encounter, systolic=encounter.systolic_bp, diastolic=encounter.diastolic_bp,
        weight_kg=encounter.weight_kg, source="legacy")
