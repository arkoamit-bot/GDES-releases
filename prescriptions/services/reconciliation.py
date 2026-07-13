"""
Medication reconciliation — the heart of the prescription↔registry bridge.

The clinician edits a FULL current-medication list and prints it. This engine
diffs that list against the patient's currently-open TreatmentExposure episodes
and projects the differences:

    drug on Rx, no open episode        -> OPEN a new episode (start = visit date)
    open episode, drug absent from Rx  -> CLOSE it (stop = visit date, + reason)
    same drug, dose/regimen changed    -> CHANGE: close old, open new (episode split)
    same drug, identical regimen       -> CONTINUE (no-op)

So the single act of prescribing maintains a research-grade, new-user-cohort
exposure history with zero extra data entry. The projection is idempotent:
a prescription carries `reconciled_at`, and exposures record which encounter
opened/closed them.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from treatments.models import StopReason, TreatmentExposure


@dataclass
class PlannedAction:
    action: str                 # "open" | "close" | "change" | "continue"
    drug_id: int
    drug_name: str
    detail: str = ""
    exposure_id: int | None = None   # existing episode affected (close/change/continue)


@dataclass
class ReconciliationPlan:
    prescription_id: int
    as_of: object               # date
    actions: list[PlannedAction] = field(default_factory=list)

    @property
    def opens(self):
        return [a for a in self.actions if a.action == "open"]

    @property
    def closes(self):
        return [a for a in self.actions if a.action == "close"]

    @property
    def changes(self):
        return [a for a in self.actions if a.action == "change"]

    @property
    def continues(self):
        return [a for a in self.actions if a.action == "continue"]

    @property
    def drugs_being_stopped(self):
        """drug_id -> drug_name for items the clinician must give a stop reason."""
        return {a.drug_id: a.drug_name for a in self.closes}

    def summary(self):
        return {
            "open": len(self.opens), "close": len(self.closes),
            "change": len(self.changes), "continue": len(self.continues),
        }


def _open_exposures_by_drug(patient):
    by_drug: dict[int, TreatmentExposure] = {}
    qs = (TreatmentExposure.objects
          .filter(patient=patient, ongoing=True)
          .select_related("drug"))
    for exp in qs:
        # Engine invariant: at most one ongoing episode per drug.
        by_drug[exp.drug_id] = exp
    return by_drug


def plan_reconciliation(prescription) -> ReconciliationPlan:
    """Pure diff — computes what *would* change, writes nothing. Safe to call on
    a draft to preview the impact before finalizing."""
    patient = prescription.patient
    as_of = prescription.encounter.encounter_date
    open_by_drug = _open_exposures_by_drug(patient)

    plan = ReconciliationPlan(prescription_id=prescription.id, as_of=as_of)
    seen_drug_ids: set[int] = set()

    for item in prescription.items.select_related("drug").all():
        seen_drug_ids.add(item.drug_id)
        exp = open_by_drug.get(item.drug_id)
        if exp is None:
            plan.actions.append(PlannedAction(
                "open", item.drug_id, item.drug.generic_name,
                detail=f"{item.dose} {item.frequency}".strip()))
        elif exp.signature == item.signature:
            plan.actions.append(PlannedAction(
                "continue", item.drug_id, item.drug.generic_name,
                detail="unchanged", exposure_id=exp.id))
        else:
            plan.actions.append(PlannedAction(
                "change", item.drug_id, item.drug.generic_name,
                detail=f"{exp.dose} {exp.frequency} → {item.dose} {item.frequency}".strip(),
                exposure_id=exp.id))

    for drug_id, exp in open_by_drug.items():
        if drug_id not in seen_drug_ids:
            plan.actions.append(PlannedAction(
                "close", drug_id, exp.drug_name,
                detail="not on current prescription", exposure_id=exp.id))

    return plan


class AlreadyReconciled(Exception):
    pass


@transaction.atomic
def apply_reconciliation(prescription, *, stop_reasons=None, force=False):
    """Project the prescription onto TreatmentExposure. Idempotent unless
    ``force``. ``stop_reasons`` maps drug_id -> StopReason for drugs being
    discontinued (defaults to OTHER if not supplied)."""
    if prescription.reconciled_at and not force:
        raise AlreadyReconciled(
            f"Prescription {prescription.id} already reconciled at "
            f"{prescription.reconciled_at}."
        )

    stop_reasons = stop_reasons or {}
    patient = prescription.patient
    encounter = prescription.encounter
    as_of = encounter.encounter_date
    open_by_drug = _open_exposures_by_drug(patient)
    seen_drug_ids: set[int] = set()

    def _open(item):
        TreatmentExposure.objects.create(
            patient=patient, drug=item.drug, drug_name=item.drug.generic_name,
            dose=item.dose, dose_unit=item.dose_unit, frequency=item.frequency,
            route=item.route_value, start_date=as_of, ongoing=True,
            opened_by_encounter=encounter,
        )

    def _close(exp, reason):
        exp.ongoing = False
        exp.stop_date = as_of
        exp.stop_reason = reason
        exp.closed_by_encounter = encounter
        exp.save(update_fields=["ongoing", "stop_date", "stop_reason",
                                "closed_by_encounter"])

    for item in prescription.items.select_related("drug").all():
        seen_drug_ids.add(item.drug_id)
        exp = open_by_drug.get(item.drug_id)
        if exp is None:
            _open(item)
        elif exp.signature != item.signature:
            _close(exp, StopReason.DOSE_CHANGE)   # episode split
            _open(item)
        # identical regimen -> leave the open episode untouched

    for drug_id, exp in open_by_drug.items():
        if drug_id not in seen_drug_ids:
            reason = stop_reasons.get(drug_id) or StopReason.OTHER
            _close(exp, reason)

    prescription.reconciled_at = timezone.now()
    prescription.save(update_fields=["reconciled_at"])
    return plan_reconciliation  # caller can re-plan if needed
