"""Lab ordering and results entry views.
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    LOGIN,
    LabOrderForm,
    LabResultsForm,
    Patient,
    get_object_or_404,
    login_required,
    messages,
    redirect,
    render,
)


@login_required(login_url=LOGIN)
def lab_order_create(request, pk):
    """Order labs at the patient's latest visit. Choose a panel and/or
    individual tests; creates a LabOrder + LabOrderItem rows linked to the
    encounter."""
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
        # dedupe by id while preserving order
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
    """Enter result VALUES for a patient on a date — independent of a visit, so
    diagnostic serology (before biopsy) and results brought to a follow-up both
    have a home. Entering creatinine auto-derives eGFR + refreshes latest_egfr."""
    from labs.models import LabResult
    from labs.services.results import record_panel

    patient = get_object_or_404(Patient, pk=pk)
    form = LabResultsForm(request.POST or None)
    ctx = {"active": "patients", "form": form, "patient": patient}
    if request.method == "POST" and form.is_valid():
        rows = form.collect()
        result_date = form.cleaned_data["result_date"]
        if not rows:
            messages.error(request, "Enter at least one result value.")
        else:
            outcome = record_panel(
                patient, rows, result_date=result_date,
                token=form.cleaned_data.get("form_token") or "",
                entry_path=LabResult.EntryPath.GUIDED,
                entered_by=request.user,
                allow_repeat=bool(form.cleaned_data.get("confirm_repeat")))
            if outcome.saved:
                messages.success(
                    request, f"Recorded {len(outcome.saved)} result(s) dated {result_date}."
                    + (" eGFR updated." if any(r.test.code == "creatinine"
                                               for r in outcome.saved) else ""))
            for code, msg in outcome.failed.items():
                messages.error(request, f"{code}: not saved — {msg}")
            if outcome.existing or outcome.failed:
                # Truthful partial state: show what is on file and what is
                # still outstanding instead of redirecting as if all saved.
                if outcome.saved:
                    messages.info(request, "The results listed as saved are recorded; "
                                  "re-submitting will not record them twice.")
                ctx.update(duplicates=outcome.existing)
            else:
                return redirect("clinic:patient_detail", pk=patient.pk)
    day = (form.cleaned_data.get("result_date") if form.is_bound and form.is_valid()
           else None)
    if day:
        ctx["existing"] = list(LabResult.objects.filter(patient=patient, result_date=day)
                               .exclude(source=LabResult.Source.DERIVED)
                               .select_related("test").order_by("test__name"))
        ctx["existing_date"] = day
    return render(request, "clinic/lab_results_form.html", ctx)
