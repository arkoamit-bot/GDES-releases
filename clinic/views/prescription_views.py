"""Prescription views: create prescription, list prescriptions."""
from __future__ import annotations

import datetime as dt

from django.contrib import messages
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render

from ._common import (LOGIN, DrugMaster, Patient, Prescription, PrescriptionItem,
                      login_required)
from .forms import AdviceTemplate


# --- Prescription (guided create) -------------------------------------------

@login_required(login_url=LOGIN)
def prescription_create(request, pk):
    """Guided prescription entry: a draft Prescription on the patient's latest
    visit + its items, then hand off to the existing preview/finalize/PDF flow."""
    patient = get_object_or_404(Patient, pk=pk)
    encounter = patient.encounters.order_by("-encounter_date", "-id").first()
    if encounter is None:
        messages.error(request, "Record a follow-up visit first — a prescription belongs to a visit.")
        return redirect("clinic:followup", pk=patient.pk)

    if request.method == "POST":
        last = encounter.prescriptions.aggregate(m=Max("version"))["m"] or 0

        # Merge multi-select investigations + free text
        inv_list = request.POST.getlist("investigations_advised")
        inv_text = (request.POST.get("investigations_advised_text") or "").strip()
        investigations = ", ".join(filter(None, inv_list))
        if inv_text:
            investigations = (investigations + ", " + inv_text).strip(", ")

        # Update encounter next_due_date if provided
        next_due = request.POST.get("next_due_date")
        if next_due:
            encounter.next_due_date = next_due
            encounter.save(update_fields=["next_due_date"])

        rx = Prescription.objects.create(
            encounter=encounter, version=last + 1,
            diagnosis_text=(request.POST.get("diagnosis_text") or "").strip(),
            comorbidities=", ".join(
                filter(None, request.POST.getlist("comorbidities")
                       + [(request.POST.get("comorbidities_text") or "").strip()]))[:240],
            investigations_advised=investigations,
            advice=(request.POST.get("advice") or "").strip(),
            stop_notes=(request.POST.get("stop_notes") or "").strip(),
        )
        valid_drug_ids = set(
            DrugMaster.objects.values_list("id", flat=True))
        n = 0
        for i in range(1, 12 + 1):  # MAX_PRESCRIPTION_ITEMS
            drug_id = request.POST.get(f"drug_{i}")
            if not drug_id or not drug_id.isdigit() or int(drug_id) not in valid_drug_ids:
                continue
            strength_val = (request.POST.get(f"strength_{i}") or "").strip()
            PrescriptionItem.objects.create(
                prescription=rx, drug_id=int(drug_id),
                brand=(request.POST.get(f"brand_{i}") or "").strip(),
                strength=strength_val,
                dose=strength_val,
                route=(request.POST.get(f"route_{i}") or "").strip().upper(),
                frequency=(request.POST.get(f"frequency_{i}") or "").strip(),
                timing=(request.POST.get(f"timing_{i}") or "after"),
                duration=(request.POST.get(f"duration_{i}") or "").strip(),
                instruction_bn=(request.POST.get(f"instruction_{i}") or "").strip(),
                sort_order=i,
            )
            n += 1
        if n == 0:
            rx.delete()
            messages.error(request, "Add at least one medication.")
            return redirect("clinic:prescription", pk=patient.pk)
        messages.success(request, f"Draft prescription created with {n} item(s). "
                         "Review it, then Finalize to freeze and reconcile the medication history.")
        return redirect("prescriptions:preview", pk=rx.pk)

    drugs = list(DrugMaster.objects.filter(is_active=True).order_by("generic_name"))
    from treatments.models import DrugClass
    _SUPPORTIVE = {DrugClass.RAASI, DrugClass.SGLT2I, DrugClass.FINERENONE,
                   DrugClass.DIURETIC, DrugClass.STATIN}
    _DISEASE = {DrugClass.STEROID, DrugClass.HCQ, DrugClass.MMF,
                DrugClass.AZATHIOPRINE, DrugClass.CYCLOPHOSPHAMIDE,
                DrugClass.CNI, DrugClass.RITUXIMAB}
    _DIABETES = {DrugClass.INSULIN, DrugClass.METFORMIN, DrugClass.SULFONYLUREA,
                 DrugClass.DPP4I, DrugClass.GLP1}
    _grouped = _SUPPORTIVE | _DISEASE | _DIABETES
    drug_groups = [
        ("Supportive therapy", [d for d in drugs if d.drug_class in _SUPPORTIVE]),
        ("Disease-specific / immunosuppression",
         [d for d in drugs if d.drug_class in _DISEASE]),
        ("Antidiabetic / glycaemic", [d for d in drugs if d.drug_class in _DIABETES]),
        ("Other", [d for d in drugs if d.drug_class not in _grouped]),
    ]
    drug_groups = [(label, items) for label, items in drug_groups if items]
    default_next = (dt.date.today() + dt.timedelta(weeks=4)).isoformat()
    from patients import choices
    from labs.models import LabTest

    # Carry-forward
    prev = (Prescription.objects.filter(encounter__patient=patient)
            .order_by("-created_at").prefetch_related("items").first())
    prev_items = list(prev.items.order_by("sort_order")) if prev else []
    item_by_drug = {it.drug_id: it for it in prev_items}

    carried, seen = [], set()
    for exp in (patient.exposures.filter(ongoing=True)
                .select_related("drug").order_by("drug__generic_name")):
        it = item_by_drug.get(exp.drug_id)
        carried.append(dict(
            drug_id=exp.drug_id, brand=(it.brand if it else ""),
            strength=(it.strength if it and it.strength else exp.dose),
            dose=exp.dose, route=(it.route_value if it else exp.route),
            frequency=exp.frequency or (it.frequency if it else ""),
            timing=(it.timing if it else ""), duration=(it.duration if it else ""),
            instruction=(it.instruction_bn if it else "")))
        seen.add(exp.drug_id)
    for it in prev_items:
        if it.drug_id not in seen:
            carried.append(dict(
                drug_id=it.drug_id, brand=it.brand, strength=it.strength,
                dose=it.dose, route=it.route_value, frequency=it.frequency,
                timing=it.timing, duration=it.duration, instruction=it.instruction_bn))
            seen.add(it.drug_id)

    rows_data = []
    for idx in range(1, 12 + 1):
        row = {"i": idx}
        if idx - 1 < len(carried):
            row.update(carried[idx - 1])
        rows_data.append(row)

    _class_labels = dict(DrugClass.choices)
    drug_data = {
        str(d.pk): {
            "brands": d.brand_names or [],
            "routes": d.routes,
            "default_route": d.default_route or "PO",
            "strengths": d.available_strengths or [],
            "strengths_by_route": d.strengths_by_route or {},
            "freq": d.default_frequency or "",
            "cls": d.drug_class if d.drug_class != DrugClass.OTHER else "",
            "cls_label": _class_labels.get(d.drug_class, ""),
            "egfr_caution": (int(d.egfr_caution_below)
                             if d.egfr_caution_below is not None else None),
        }
        for d in drugs
    }
    prefill_invest = set()
    if prev and prev.investigations_advised:
        prefill_invest = {s.strip() for s in prev.investigations_advised.split(",") if s.strip()}

    initial_visible = min(12, max(3, len(carried) + 1))

    comorbidity_options = ["Hypertension", "Diabetes mellitus", "Bronchial asthma",
                           "Hypothyroidism", "Dyslipidaemia", "Ischaemic heart disease",
                           "COPD", "CKD"]
    prefill_comorbid = set()
    if patient.hypertension:
        prefill_comorbid.add("Hypertension")
    if patient.autoimmune_disease:
        prefill_comorbid.add("Autoimmune disease")
    if patient.chronic_infection:
        prefill_comorbid.add("Chronic infection")
    if patient.diabetes_status not in ("", "none", None):
        prefill_comorbid.add("Diabetes mellitus")
    if prev and prev.comorbidities:
        prefill_comorbid |= {s.strip() for s in prev.comorbidities.split(",") if s.strip()}
    comorbid_extra = ", ".join(sorted(c for c in prefill_comorbid
                                      if c not in comorbidity_options))

    return render(request, "clinic/prescription_form.html", {
        "active": "prescriptions", "patient": patient, "encounter": encounter,
        "drugs": drugs, "drug_groups": drug_groups,
        "rows_data": rows_data, "drug_data": drug_data,
        "timings": PrescriptionItem.Timing.choices,
        "default_diagnosis": patient.primary_diagnosis or "",
        "diagnosis_choices": choices.SPECIFIC_GN_DIAGNOSIS,
        "lab_tests": LabTest.objects.filter(is_active=True).order_by("name"),
        "default_next_visit": default_next,
        "prefill_invest": prefill_invest, "prefill_advice": prev.advice if prev else "",
        "carried_count": len(carried), "initial_visible": initial_visible,
        "patient_egfr": (float(patient.latest_egfr)
                         if patient.latest_egfr is not None else None),
        "advice_templates": list(
            AdviceTemplate.objects.filter(is_active=True)
            .values("title", "body")),
        "comorbidity_options": comorbidity_options,
        "prefill_comorbid": prefill_comorbid, "comorbid_extra": comorbid_extra,
    })


# --- Prescriptions list -----------------------------------------------------

@login_required(login_url=LOGIN)
def prescriptions_list(request):
    rx = (Prescription.objects.select_related("encounter", "encounter__patient")
          .order_by("-created_at")[:100])
    return render(request, "clinic/prescriptions_list.html",
                  {"active": "prescriptions", "prescriptions": rx})
