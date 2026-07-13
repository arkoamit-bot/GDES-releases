"""Create a structured lab order at a visit — the 'record the lab' step.

This is what the clinician triggers alongside the prescription; the printed Rx
can carry the same tests as free text in `investigations_advised`, while this
gives the registry the structured, fulfillable order.
"""
from __future__ import annotations

from django.db import transaction

from labs.models import LabOrder, LabOrderItem, LabPanel, LabTest


@transaction.atomic
def order_panel(encounter, panel_code, *, notes=""):
    panel = LabPanel.objects.get(code=panel_code)
    order = LabOrder.objects.create(
        encounter=encounter, patient=encounter.patient,
        ordered_date=encounter.encounter_date, notes=notes)
    for test in panel.tests.filter(is_active=True, is_derived=False):
        LabOrderItem.objects.create(order=order, test=test)
    return order


@transaction.atomic
def order_tests(encounter, test_codes, *, notes=""):
    order = LabOrder.objects.create(
        encounter=encounter, patient=encounter.patient,
        ordered_date=encounter.encounter_date, notes=notes)
    for code in test_codes:
        LabOrderItem.objects.create(order=order, test=LabTest.objects.get(code=code))
    return order
