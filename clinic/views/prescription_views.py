"""Prescription views: create prescription, list prescriptions.
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    AdviceTemplate,
    DrugMaster,
    LOGIN,
    MAX_PRESCRIPTION_ITEMS,
    Patient,
    Prescription,
    PrescriptionItem,
    TaperTemplate,
    _clip,
    get_object_or_404,
    is_systemic_steroid,
    login_required,
    messages,
    redirect,
    render,
)


DOSE_UNITS = [("", "—"), ("tab", "tab"), ("cap", "cap"), ("ml", "mL"), ("mg", "mg"),
              ("g", "g"), ("mcg", "mcg"), ("unit", "unit(s)"), ("drop", "drop(s)"),
              ("puff", "puff(s)"), ("sachet", "sachet"), ("vial", "vial"),
              ("amp", "amp"), ("spoon", "spoon")]


def _requested_tests(values):
    """Catalogue tests from the posted investigation values: test ids (the
    current form) or exact test names (older pages), de-duplicated by id."""
    from labs.models import LabTest
    ids, names = [], []
    for v in values:
        v = (v or "").strip()
        if not v:
            continue
        (ids if v.isdigit() else names).append(v)
    tests = list(LabTest.objects.filter(pk__in=[int(i) for i in ids], is_active=True))
    if names:
        tests += list(LabTest.objects.filter(name__in=names, is_active=True))
    seen, out = set(), []
    for t in tests:
        if t.pk not in seen:
            seen.add(t.pk)
            out.append(t)
    return out


@login_required(login_url=LOGIN)
def prescription_create(request, pk):
    """Guided prescription entry: a draft Prescription on the patient's latest
    visit + its items, then hand off to the existing preview/finalize/PDF flow.
    Print the FULL current regimen each visit — that set is what finalize
    reconciles into TreatmentExposure episodes.

    Linked, not re-typed: the next appointment is the visit's own (changing it
    goes through encounters.services.scheduling); catalogue investigations are
    structured requests that become lab orders at finalization; the printed
    comorbidities are a selection from the patient record plus clearly
    prescription-only notes; product strength and dose are separate facts."""
    from django.db import transaction
    from django.db.models import Max

    from encounters.services.scheduling import set_next_visit, suggested_next_visit
    from labs.models import LabOrderItem, LabTest
    from patients.comorbidity import comorbidity_items, structured_labels
    from prescriptions.models import PrescriptionTestRequest

    patient = get_object_or_404(Patient, pk=pk)
    encounter = patient.encounters.order_by("-encounter_date", "-id").first()
    if encounter is None:
        messages.error(request, "Record a follow-up visit first — a prescription belongs to a visit.")
        return redirect("clinic:followup", pk=patient.pk)

    bound = None   # what the clinician typed, when a POST is shown again
    if request.method == "POST":
        valid_drug_ids = set(DrugMaster.objects.values_list("id", flat=True))
        rows = []
        for i in range(1, MAX_PRESCRIPTION_ITEMS + 1):
            drug_id = request.POST.get(f"drug_{i}")
            # Skip empty rows and reject anything that isn't a known drug id.
            if not drug_id or not drug_id.isdigit() or int(drug_id) not in valid_drug_ids:
                continue
            rows.append(i)
        if not rows:
            # Shown again with the clinician's entries, not re-defaulted: an
            # intentionally cleared diagnosis stays cleared.
            messages.error(request, "Add at least one medication.")
            bound = {"diagnosis": (request.POST.get("diagnosis_text") or "").strip(),
                     "advice": (request.POST.get("advice") or "").strip()}

    if request.method == "POST" and bound is None:
        f = PrescriptionItem._meta.get_field
        with transaction.atomic():
            last = encounter.prescriptions.aggregate(m=Max("version"))["m"] or 0

            # Next appointment: one scheduling action. Unchanged -> untouched.
            next_due = (request.POST.get("next_due_date") or "").strip()
            if next_due:
                set_next_visit(encounter, next_due, user=request.user,
                               reason=(request.POST.get("next_due_reason") or "").strip(),
                               source="prescription")

            rx = Prescription.objects.create(
                encounter=encounter, version=last + 1,
                diagnosis_text=(request.POST.get("diagnosis_text") or "").strip(),
                comorbidities=", ".join(
                    filter(None, request.POST.getlist("comorbidities")
                           + [(request.POST.get("comorbidities_text") or "").strip()]))[:240],
                # Only investigations outside the catalogue are free text now.
                investigations_advised=(request.POST.get("investigations_advised_text") or "").strip(),
                advice=(request.POST.get("advice") or "").strip(),
                stop_notes=(request.POST.get("stop_notes") or "").strip(),
            )
            for test in _requested_tests(request.POST.getlist("investigations_advised")):
                PrescriptionTestRequest.objects.create(prescription=rx, test=test)

            for i in rows:
                PrescriptionItem.objects.create(
                    prescription=rx, drug_id=int(request.POST.get(f"drug_{i}")),
                    brand=_clip(request.POST.get(f"brand_{i}"), f("brand")),
                    # Product strength and the dose per administration are
                    # different facts; blank dose = one unit of the product.
                    strength=_clip(request.POST.get(f"strength_{i}"), f("strength")),
                    dose=_clip(request.POST.get(f"dose_{i}"), f("dose")),
                    dose_unit=_clip(request.POST.get(f"dose_unit_{i}"), f("dose_unit")),
                    route=_clip((request.POST.get(f"route_{i}") or "").strip().upper(), f("route")),
                    frequency=_clip(request.POST.get(f"frequency_{i}"), f("frequency")),
                    timing=_clip(request.POST.get(f"timing_{i}") or "after", f("timing")),
                    duration=_clip(request.POST.get(f"duration_{i}"), f("duration")),
                    instruction_bn=_clip(request.POST.get(f"instruction_{i}"), f("instruction_bn")),
                    taper_notes=(request.POST.get(f"taper_{i}") or "").strip(),
                    sort_order=i,
                )
        n = len(rows)
        messages.success(request, f"Draft prescription created with {n} item(s). "
                         "Review it, then Finalize to freeze it, place the requested "
                         "lab orders and reconcile the medication history.")
        return redirect("prescriptions:preview", pk=rx.pk)

    drugs = list(DrugMaster.objects.filter(is_active=True).order_by("generic_name"))
    # Group the drug picker into Supportive vs Disease-specific therapy so the
    # prescription reads like the treatment plan (protocol §3A/§3B).
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

    # Type-to-filter key for the drug picker. The visible option label is only
    # the generic name, but a prescriber recalls a drug by whatever is on the
    # box or the strip: "Losec", "Seclo", "40mg". The searchable <select>
    # matches against this wider string, so brand and strength hits are found
    # too. It is attached to the in-memory instance (drugs is a list) rather
    # than the model, so nothing is persisted and no migration is needed.
    for d in drugs:
        _brands = [str(b) for b in (d.brand_names or []) if b]
        _strengths = [str(s) for s in (d.available_strengths or []) if s]
        d.search_text = " ".join(
            [d.generic_name or ""] + _brands + _strengths).strip()

    # The visit's selected next appointment, when there is one; otherwise a
    # suggestion (4 weeks), labelled as such.
    if encounter.next_due_date:
        default_next, next_selected = encounter.next_due_date.isoformat(), True
    else:
        default_next, next_selected = suggested_next_visit().isoformat(), False
    from patients import choices
    from prescriptions.services.diagnosis_prefill import diagnosis_prefill

    # Diagnosis: the last finalized prescription's, else the working diagnosis
    # (see the service). A re-shown POST keeps what was typed.
    dx_prefill = diagnosis_prefill(patient, encounter)
    if bound is not None:
        default_diagnosis, dx_source_label = bound["diagnosis"], ""
    else:
        default_diagnosis, dx_source_label = dx_prefill.value, dx_prefill.source_label
    choice_values = {v for v, _l in choices.SPECIFIC_GN_DIAGNOSIS}
    # A legacy, custom or combined diagnosis is offered as itself rather than
    # lost to a dropdown mismatch.
    diagnosis_choices = list(choices.SPECIFIC_GN_DIAGNOSIS)
    extra_dx = [v for v in [default_diagnosis] + [v for _l, v in dx_prefill.also_on_record]
                if v and v not in choice_values]
    for v in dict.fromkeys(extra_dx):
        diagnosis_choices.insert(0, (v, f"{v} (as recorded)"))

    # Carry-forward: pre-fill rows from the patient's most recent prescription so
    # the FULL regimen is preserved; the clinician edits / removes / adds before
    # finalize. (Print the full current regimen each visit — finalize reconciles it.)
    prev = (Prescription.objects.filter(encounter__patient=patient)
            .order_by("-created_at").prefetch_related("items", "test_requests").first())
    prev_items = list(prev.items.order_by("sort_order")) if prev else []
    item_by_drug = {it.drug_id: it for it in prev_items}

    def _dose_fields(it):
        # A separately stated dose only; legacy rows copied the strength.
        if it is None or not it.administered_dose:
            return {"dose": "", "dose_unit": ""}
        return {"dose": it.dose, "dose_unit": it.dose_unit}

    # The patient's CURRENT regimen = ongoing treatment episodes. This includes
    # medications added manually via the Treatment page (prior/external drugs the
    # patient was already on), so they auto-populate the prescription too — not
    # just meds from the last prescription. Enrich each with the last
    # prescription's richer fields (brand/timing/duration) where the drug matches.
    carried, seen = [], set()
    for exp in (patient.exposures.filter(ongoing=True)
                .select_related("drug").order_by("drug__generic_name")):
        it = item_by_drug.get(exp.drug_id)
        carried.append(dict(
            drug_id=exp.drug_id, brand=(it.brand if it else ""),
            strength=(it.strength if it and it.strength else (exp.strength or exp.dose)),
            **_dose_fields(it),
            route=(it.route_value if it else exp.route),
            frequency=exp.frequency or (it.frequency if it else ""),
            timing=(it.timing if it else ""), duration=(it.duration if it else ""),
            instruction=(it.instruction_bn if it else ""),
            taper=(it.taper_notes if it else "")))
        seen.add(exp.drug_id)
    # Include any last-prescription drug not yet an ongoing episode (e.g. a draft
    # not finalized) so nothing from the previous script is silently dropped.
    for it in prev_items:
        if it.drug_id not in seen:
            carried.append(dict(
                drug_id=it.drug_id, brand=it.brand, strength=it.strength,
                **_dose_fields(it), route=it.route_value, frequency=it.frequency,
                timing=it.timing, duration=it.duration, instruction=it.instruction_bn,
                taper=it.taper_notes))
            seen.add(it.drug_id)

    rows_data = []
    for idx in range(1, MAX_PRESCRIPTION_ITEMS + 1):
        row = {"i": idx}
        if idx - 1 < len(carried):
            row.update(carried[idx - 1])
        rows_data.append(row)

    # Formulary map that drives the row dropdowns (brands, routes, per-route
    # strengths, default frequency) — one JSON blob, no per-option attributes.
    _class_labels = dict(DrugClass.choices)
    drug_data = {
        str(d.pk): {
            "brands": d.brand_names or [],
            "routes": d.routes,
            "default_route": d.default_route or "PO",
            "strengths": d.available_strengths or [],
            "strengths_by_route": d.strengths_by_route or {},
            "freq": d.default_frequency or "",
            # For the live duplicate-class warning (OTHER is not research-coded).
            "cls": d.drug_class if d.drug_class != DrugClass.OTHER else "",
            "cls_label": _class_labels.get(d.drug_class, ""),
            # For the live renal-dose warning: eGFR threshold below which this
            # drug needs review / dose adjustment (None -> no threshold).
            "egfr_caution": (int(d.egfr_caution_below)
                             if d.egfr_caution_below is not None else None),
            # For the per-row taper plan: only systemic single-agent steroids
            # get one (topical/ophthalmic combination drops never do).
            "systemic_steroid": is_systemic_steroid(d),
        }
        for d in drugs
    }

    # Investigations: structured requests carried by test id; a legacy
    # prescription's free text is matched to catalogue names where exact.
    lab_tests = list(LabTest.objects.filter(is_active=True, is_derived=False).order_by("name"))
    by_name = {t.name: t.pk for t in lab_tests}
    prefill_invest, prefill_invest_text = set(), ""
    if prev:
        prefill_invest = {r.test_id for r in prev.test_requests.all()}
        leftovers = []
        for s in (prev.investigations_advised or "").split(","):
            s = s.strip()
            if not s:
                continue
            if s in by_name and not prev.test_requests.exists():
                prefill_invest.add(by_name[s])
            else:
                leftovers.append(s)
        prefill_invest_text = ", ".join(leftovers)
    outstanding = list(LabOrderItem.objects.filter(
        order__encounter=encounter,
        order__status__in=["ordered", "collected"]).select_related("test", "order"))
    outstanding = [it for it in outstanding if not it.is_resulted]

    # Declutter: show carried-forward rows + a couple of blanks; the rest are
    # revealed one at a time by the "Add medication" button.
    initial_visible = min(MAX_PRESCRIPTION_ITEMS, max(3, len(carried) + 1))

    # Comorbidities: the patient record's CURRENT conditions (ticked -> printed);
    # plus common prescription-only items (asthma, thyroid ...) which may be
    # carried from the last slip because the record does not own them. A
    # condition the record owns is never carried from an old slip, so a
    # correction on the record cannot be undone by the previous prescription.
    record_items = comorbidity_items(patient, getattr(patient, "baseline", None))
    owned = structured_labels() | {c["label"] for c in record_items}
    comorbidity_options = ["Bronchial asthma", "Hypothyroidism", "Dyslipidaemia",
                           "Ischaemic heart disease", "COPD", "CKD"]
    prefill_comorbid = set()
    extra = []
    if prev and prev.comorbidities:
        for s in (x.strip() for x in prev.comorbidities.split(",")):
            if not s or s in owned or s.startswith("Diabetes mellitus"):
                continue
            if s in comorbidity_options:
                prefill_comorbid.add(s)
            else:
                extra.append(s)
    comorbid_extra = ", ".join(extra)

    return render(request, "clinic/prescription_form.html", {
        "active": "prescriptions", "patient": patient, "encounter": encounter,
        "drugs": drugs, "drug_groups": drug_groups,
        "rows_data": rows_data, "drug_data": drug_data,
        "timings": PrescriptionItem.Timing.choices, "dose_units": DOSE_UNITS,
        "default_diagnosis": default_diagnosis,
        "diagnosis_choices": diagnosis_choices,
        "diagnosis_source_label": dx_source_label,
        "diagnosis_newer_draft": dx_prefill.newer_draft if bound is None else None,
        "diagnosis_also_on_record": dx_prefill.also_on_record,
        "lab_tests": lab_tests,
        "default_next_visit": default_next, "next_visit_is_selected": next_selected,
        "prefill_invest": prefill_invest, "prefill_invest_text": prefill_invest_text,
        "outstanding_orders": outstanding,
        "outstanding_test_ids": {it.test_id for it in outstanding},
        "prefill_advice": (bound["advice"] if bound is not None
                           else (prev.advice if prev else "")),
        "carried_count": len(carried), "initial_visible": initial_visible,
        "patient_egfr": (float(patient.latest_egfr)
                         if patient.latest_egfr is not None else None),
        "advice_templates": list(
            AdviceTemplate.objects.filter(is_active=True)
            .values("title", "body")),
        "taper_presets": list(
            TaperTemplate.objects.filter(is_active=True)
            .values("title", "body")),
        "record_comorbidities": record_items,
        "comorbidity_options": comorbidity_options,
        "prefill_comorbid": prefill_comorbid, "comorbid_extra": comorbid_extra,
    })


@login_required(login_url=LOGIN)
def prescriptions_list(request):
    rx = (Prescription.objects.select_related("encounter", "encounter__patient")
          .order_by("-created_at")[:100])
    return render(request, "clinic/prescriptions_list.html",
                  {"active": "prescriptions", "prescriptions": rx})
