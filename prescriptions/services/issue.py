"""What a prescription says when it is issued, and the orders it places.

build_snapshot() assembles everything the printout shows from the linked
records -- patient identity, the visit and its selected vitals, the latest
eGFR with its source result, the printed comorbidities, every item with its
strength AND dose, the investigations, advice and the next appointment.
Drafts render from it live; finalization freezes it on the prescription
(issued_snapshot), so a later edit to the patient, a new lab result or a moved
appointment never changes a prescription already issued.

commit_test_requests() turns the draft's requested catalogue tests into real
LabOrderItems at finalization (the clinician's acceptance), linking to an
outstanding order for the same test at the same visit instead of ordering it
twice. It only processes requests not yet linked, so a retry is a no-op.
"""
from __future__ import annotations

from django.conf import settings

SNAPSHOT_VERSION = 1


def _iso(d):
    return d.isoformat() if d else None


def _egfr(patient):
    from labs.models import LabResult
    r = (LabResult.objects.filter(patient=patient, test__code="egfr",
                                  value_numeric__isnull=False)
         .order_by("-result_date", "-created_at").first())
    if r is not None:
        return {"value": str(r.value_numeric.normalize() if hasattr(r.value_numeric, "normalize")
                             else r.value_numeric),
                "date": _iso(r.result_date), "result_id": r.pk,
                "formula": r.formula_version}
    if patient.latest_egfr is not None:
        return {"value": str(patient.latest_egfr), "date": None, "result_id": None,
                "formula": ""}
    return None


def _vitals(encounter):
    v = getattr(encounter, "selected_vital", None)
    source = f"vital:{v.pk}" if v is not None else "encounter"
    if encounter.systolic_bp is None and encounter.weight_kg is None:
        return None
    return {"systolic": encounter.systolic_bp, "diastolic": encounter.diastolic_bp,
            "weight_kg": str(encounter.weight_kg) if encounter.weight_kg is not None else None,
            "source": source}


def build_snapshot(rx) -> dict:
    """The printable content of ``rx``, from the current linked records."""
    encounter = rx.encounter
    patient = encounter.patient
    printer = rx.printed_by
    items = []
    for it in rx.items.select_related("drug").order_by("sort_order", "id"):
        items.append({
            "generic": it.drug.generic_name, "brand": it.brand,
            "strength": it.strength, "dose": it.administered_dose,
            "route": it.route_value, "frequency": it.frequency,
            "timing": it.get_timing_display(), "duration": it.duration,
            "instruction_bn": it.instruction_bn, "taper_notes": it.taper_notes,
            "drug_id": it.drug_id,
        })
    requests = list(rx.test_requests.select_related("test", "order_item__order"))
    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "patient": {
            "name": patient.name, "patient_id": patient.patient_id,
            "hospital_id": patient.hospital_id, "sex": patient.get_sex_display(),
            "diabetes": (patient.get_diabetes_status_display()
                         if patient.diabetes_status and patient.diabetes_status != "none" else ""),
        },
        "encounter": {"date": _iso(encounter.encounter_date),
                      "type": encounter.get_encounter_type_display(),
                      "id": encounter.pk},
        "vitals": _vitals(encounter),
        "egfr": _egfr(patient),
        "diagnosis": rx.diagnosis_text,
        "comorbidities": rx.comorbidities,
        "items": items,
        "investigations": [
            {"test": r.test.name, "test_id": r.test_id,
             "order_item_id": r.order_item_id,
             "ordered_date": _iso(r.order_item.order.ordered_date) if r.order_item else None}
            for r in requests],
        "investigations_text": rx.investigations_advised,
        "advice": rx.advice,
        "visit_note": encounter.advice,
        "stop_notes": rx.stop_notes,
        "next_visit": _iso(encounter.next_due_date),
        "prescriber": ((printer.get_full_name() or printer.username) if printer else ""),
        "clinic": dict(getattr(settings, "CLINIC", {}) or {}),
    }


def commit_test_requests(rx):
    """Place the requested tests as lab orders on the prescription's visit."""
    from labs.models import LabOrder, LabOrderItem

    pending = list(rx.test_requests.filter(order_item__isnull=True).select_related("test"))
    if not pending:
        return []
    encounter = rx.encounter
    outstanding = {}
    for item in (LabOrderItem.objects.filter(
            order__encounter=encounter,
            order__status__in=[LabOrder.Status.ORDERED, LabOrder.Status.COLLECTED])
            .select_related("order").order_by("order__ordered_date", "id")):
        if not item.is_resulted:
            outstanding.setdefault(item.test_id, item)
    order = None
    linked = []
    for req in pending:
        item = outstanding.get(req.test_id)
        if item is None:
            if order is None:
                order = LabOrder.objects.create(
                    encounter=encounter, patient=encounter.patient,
                    ordered_date=encounter.encounter_date,
                    notes=f"Requested on prescription v{rx.version}")
            item = LabOrderItem.objects.create(order=order, test=req.test)
            outstanding[req.test_id] = item
        req.order_item = item
        req.save(update_fields=["order_item"])
        linked.append(item)
    return linked


def view_model(rx) -> dict:
    """What the template renders: the frozen snapshot for a prescription
    issued with one, the live content otherwise (drafts, and prescriptions
    finalized before snapshots existed -- flagged, never back-filled)."""
    if rx.is_final and rx.snapshot_version and rx.issued_snapshot:
        return {"s": rx.issued_snapshot, "frozen": True, "legacy_live": False}
    return {"s": build_snapshot(rx), "frozen": False,
            "legacy_live": bool(rx.is_final)}
