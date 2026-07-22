"""Lab ordering and results entry views."""
from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ._common import LOGIN, Patient, login_required
from ..forms import LabOrderForm, LabResultsForm


@login_required(login_url=LOGIN)
def lab_order_create(request, pk):
    """Order labs at the patient's latest visit."""
    patient = get_object_or_404(Patient, pk=pk)
    encounter = patient.encounters.order_by("-encounter_date", "-id").first()
    if encounter is None:
        messages.error(request, "Record a follow-up visit first — a lab order belongs to a visit.")
        return redirect("clinic:followup", pk=patient.pk)

    form = LabOrderForm(request.POST or None, patient=patient)
    if request.method == "POST" and form.is_valid():
        cd = form.cleaned_data
        from labs.services.ordering import order_tests
        tests = list(cd.get("custom_tests", []))
        if cd.get("panel"):
            tests += list(cd["panel"].tests.filter(is_active=True, is_derived=False))
        seen = set()
        uniq = []
        for t in tests:
            if t.id not in seen:
                seen.add(t.id)
                uniq.append(t)
        if not uniq:
            messages.error(request, "Choose at least one test.")
            return redirect("clinic:lab_order", pk=patient.pk)
        order = order_tests(encounter, [t.code for t in uniq], notes=cd.get("notes", ""))
        messages.success(request, f"Ordered {len(uniq)} test(s) on {order.ordered_date}.")
        return redirect("clinic:patient_detail", pk=patient.pk)

    return render(request, "clinic/lab_order_form.html",
                  {"active": "patients", "form": form, "patient": patient,
                   "encounter": encounter})


@login_required(login_url=LOGIN)
def lab_results_entry(request, pk):
    """Enter result VALUES for a patient on a date."""
    patient = get_object_or_404(Patient, pk=pk)
    form = LabResultsForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from labs.services.results import record_result
        rows = form.collect()
        result_date = form.cleaned_data["result_date"]
        saved = 0
        for code, value_numeric, value_text in rows:
            try:
                record_result(patient, code, result_date=result_date,
                              value_numeric=value_numeric, value_text=value_text,
                              source="manual")
                saved += 1
            except Exception:
                continue
        if saved:
            messages.success(
                request, f"Recorded {saved} result(s) dated {result_date}."
                + (" eGFR updated." if any(c == "creatinine" for c, *_ in rows) else ""))
            return redirect("clinic:patient_detail", pk=patient.pk)
        messages.error(request, "Enter at least one result value.")
    return render(request, "clinic/lab_results_form.html",
                  {"active": "patients", "form": form, "patient": patient})
