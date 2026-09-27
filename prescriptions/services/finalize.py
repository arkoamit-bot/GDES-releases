"""
Finalize = the moment of printing. It freezes the prescription (immutable
snapshot + hash), then projects it onto the research exposure table via the
reconciliation engine. One call, both effects.

Phase 3.3: Also creates medication adherence reminders after finalization.
"""
from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from .reconciliation import apply_reconciliation
from .safety import check_prescription


class FinalizeBlocked(Exception):
    def __init__(self, warnings):
        self.warnings = warnings
        super().__init__("Prescription has blocking safety warnings.")


@transaction.atomic
def finalize_prescription(prescription, *, user=None, stop_reasons=None,
                          override_blocks=False):
    """Freeze and reconcile. Raises FinalizeBlocked if a hard safety check
    fails and ``override_blocks`` is False."""
    if prescription.is_final:
        return check_prescription(prescription)

    warnings = check_prescription(prescription)
    if any(w.level == "block" for w in warnings) and not override_blocks:
        raise FinalizeBlocked(warnings)

    # Acceptance: the requested catalogue tests become real lab orders on
    # this visit (linked to an outstanding order for the same test instead of
    # ordering it twice). Drafts never place orders.
    from .issue import SNAPSHOT_VERSION, build_snapshot, commit_test_requests
    commit_test_requests(prescription)

    prescription.status = prescription.Status.FINAL
    prescription.printed_by = user
    prescription.printed_at = timezone.now()
    # Freeze what the printout shows, then hash that content (v2). Later
    # edits to the patient, labs or appointments cannot change this slip.
    prescription.issued_snapshot = build_snapshot(prescription)
    prescription.snapshot_version = SNAPSHOT_VERSION
    prescription.content_hash = prescription.compute_snapshot_hash()
    prescription.content_hash_version = 2
    prescription.save(update_fields=["status", "printed_by", "printed_at",
                                     "content_hash", "content_hash_version",
                                     "issued_snapshot", "snapshot_version"])

    apply_reconciliation(prescription, stop_reasons=stop_reasons)

    # Phase 3.3: Schedule medication adherence reminders
    _schedule_medication_reminders(prescription)

    return warnings


def _schedule_medication_reminders(prescription):
    """Auto-create medication adherence reminders for finalized prescriptions."""
    try:
        from reminders.models import ReminderSchedule, ReminderType, ReminderChannel, ReminderStatus
        patient = prescription.patient
        encounter_date = prescription.encounter.encounter_date
        items = list(prescription.items.select_related("drug").all())

        if not items:
            return

        drug_names = ", ".join(it.drug.generic_name for it in items[:4])
        if len(items) > 4:
            drug_names += f" +{len(items) - 4} more"

        # Create a 7-day follow-up adherence reminder
        from datetime import timedelta
        reminder_date = timezone.now() + timedelta(days=7)

        ReminderSchedule.objects.create(
            patient=patient,
            reminder_type=ReminderType.MEDICATION,
            channel=ReminderChannel.SMS,
            title="Medication adherence check",
            message=(
                f"Dear {patient.name or 'Patient'}, this is a reminder to take "
                f"your medications as prescribed: {drug_names}. "
                f"If you experience any side effects, please contact the clinic."
            ),
            scheduled_at=reminder_date,
            status=ReminderStatus.PENDING,
        )
    except Exception:
        pass  # Reminders app may not be installed; fail silently


def new_version_from(prescription):
    """Real-world edits after printing don't mutate history — they create the
    next immutable version, copying the current medication list forward."""
    items = list(prescription.items.all())
    last_rx = prescription.encounter.prescriptions.order_by("-version").first()
    next_version = (last_rx.version + 1) if last_rx else 1
    clone = prescription.__class__.objects.create(
        encounter=prescription.encounter,
        version=next_version,
        diagnosis_text=prescription.diagnosis_text,
        comorbidities=prescription.comorbidities,
        investigations_advised=prescription.investigations_advised,
        advice=prescription.advice,
    )
    for it in items:
        it.pk = None
        it.prescription = clone
        it.save()
    # Requested tests carry over as requests; ones already ordered stay
    # linked to their order item, so the new version does not re-order them.
    for req in prescription.test_requests.all():
        clone.test_requests.create(test_id=req.test_id, order_item_id=req.order_item_id)
    return clone
