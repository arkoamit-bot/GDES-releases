"""Patient management views: list, search, CRUD, detail, quicksearch.
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    LOGIN,
    Patient,
    PatientForm,
    Prescription,
    Q,
    RegisterForm,
    _PATIENT_CLIN_FIELDS,
    _PATIENT_DEM_FIELDS,
    _PATIENT_LEVEL2_FIELDS,
    _get_patient_override_context,
    _get_prediction_history,
    _get_recommendation_audit_records,
    get_object_or_404,
    logger,
    login_required,
    messages,
    redirect,
    render,
)


@login_required(login_url=LOGIN)
def patients_list(request):
    q = (request.GET.get("q") or "").strip()
    patients = Patient.objects.all().order_by("patient_id")
    if q:
        patients = patients.filter(
            Q(patient_id__icontains=q) | Q(name__icontains=q)
            | Q(hospital_id__icontains=q) | Q(phone__icontains=q)
        )
    total = patients.count()
    patients = patients[:200]
    ctx = {"active": "patients", "patients": patients, "q": q,
           "total": total, "capped": total > 200}
    # Live search: HTMX requests get just the table rows for an in-place swap.
    if request.headers.get("HX-Request"):
        return render(request, "clinic/_patient_rows.html", ctx)
    return render(request, "clinic/patients_list.html", ctx)


@login_required(login_url=LOGIN)
def quicksearch(request):
    """Global topbar quick-jump — returns a small dropdown of matching patients."""
    q = (request.GET.get("q") or "").strip()
    results = []
    if q:
        results = (Patient.objects.filter(
            Q(patient_id__icontains=q) | Q(name__icontains=q)
            | Q(hospital_id__icontains=q) | Q(phone__icontains=q))
            .order_by("patient_id")[:8])
    return render(request, "clinic/_quicksearch_results.html",
                  {"results": results, "q": q})


@login_required(login_url=LOGIN)
def patient_dupcheck(request):
    """Live duplicate check for the registration form: warn if a patient with the
    same phone / hospital id / similar name already exists (prevents the kind of
    duplicate the data validation flagged)."""
    name = (request.GET.get("name") or "").strip()
    phone = (request.GET.get("phone") or "").strip()
    hosp = (request.GET.get("hospital_id") or "").strip()
    exclude = request.GET.get("exclude")

    conds = []
    if len(phone) >= 4:
        conds.append(Q(phone=phone))
    if hosp:
        conds.append(Q(hospital_id__iexact=hosp))
    if len(name) >= 3:
        conds.append(Q(name__icontains=name))

    matches = []
    if conds:
        q = conds[0]
        for c in conds[1:]:
            q |= c
        qs = Patient.objects.filter(q)
        if exclude and str(exclude).isdigit():
            qs = qs.exclude(pk=int(exclude))
        matches = list(qs.order_by("patient_id")[:5])
    return render(request, "clinic/_dupcheck.html", {"matches": matches})


@login_required(login_url=LOGIN)
def patient_create(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save()
        messages.success(request, f"Patient {patient.patient_id} registered.")
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/patient_form.html",
                  {"active": "patients", "form": form, "mode": "create",
                   "dem_fields": _PATIENT_DEM_FIELDS,
                   "clin_fields": _PATIENT_CLIN_FIELDS,
                   "level2_fields": _PATIENT_LEVEL2_FIELDS})


@login_required(login_url=LOGIN)
def patient_delete(request, pk):
    """Permanently delete a patient and ALL their records (superuser only).

    Encounters PROTECT the patient and prescriptions/lab-orders PROTECT the
    encounters, so a plain delete fails — this removes dependents in the correct
    order inside one transaction. Guarded: POST + typed-ID confirmation.
    """
    from django.db import transaction
    patient = get_object_or_404(Patient, pk=pk)
    if not request.user.is_superuser:
        messages.error(request, "Only a superuser can delete a patient record.")
        return redirect("clinic:patient_detail", pk=patient.pk)

    if request.method == "POST":
        if (request.POST.get("confirm_id") or "").strip() != patient.patient_id:
            messages.error(request, "Deletion not confirmed — the typed ID did not match.")
            return redirect("clinic:patient_detail", pk=patient.pk)
        pid = patient.patient_id
        with transaction.atomic():
            # 1) Records that PROTECT encounters.
            Prescription.objects.filter(encounter__patient=patient).delete()
            patient.lab_orders.all().delete()
            # 2) Encounters (they PROTECT the patient).
            patient.encounters.all().delete()
            # 3) The patient — cascades labs, biopsies, exposures, outcomes,
            #    events, enrolments, consents, adverse events, admissions, etc.
            patient.delete()
        messages.success(request, f"Patient {pid} and all associated records were deleted.")
        return redirect("clinic:patients")

    # GET → confirmation page.
    return render(request, "clinic/patient_confirm_delete.html",
                  {"active": "patients", "patient": patient})


@login_required(login_url=LOGIN)
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Patient details updated.")
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/patient_form.html",
                  {"active": "patients", "form": form, "mode": "edit",
                   "patient": patient,
                   "dem_fields": _PATIENT_DEM_FIELDS,
                   "clin_fields": _PATIENT_CLIN_FIELDS,
                   "level2_fields": _PATIENT_LEVEL2_FIELDS})


@login_required(login_url=LOGIN)
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    baseline = getattr(patient, "baseline", None)
    encounters = patient.encounters.all().order_by("-encounter_date")[:10]
    prescriptions = (Prescription.objects.filter(encounter__patient=patient)
                     .order_by("-created_at")[:10])
    outcome = getattr(patient, "outcome", None)
    adverse_events = patient.adverse_events.all().order_by("-onset_date")[:20]
    biopsies = (patient.biopsies.select_related("diagnosis")
                .order_by("-biopsy_date")[:10])
    enrollments = (patient.enrollments.select_related("study", "arm")
                   .order_by("-enrolled_date", "-id")[:10])
    exposures = (patient.exposures.select_related("drug")
                 .order_by("-ongoing", "-start_date")[:30])
    lab_orders = (patient.lab_orders.select_related("encounter")
                  .prefetch_related("items__test")
                  .order_by("-ordered_date")[:20])
    from clinical_reasoning.models import ClinicalProfile
    try:
        profile = ClinicalProfile.objects.get(patient=patient)
    except ClinicalProfile.DoesNotExist:
        profile = None
    from audit.models import Consent, AuditLog
    from audit.services.consent import current_consent
    consents = [{"label": label, "current": current_consent(patient, value)}
                for value, label in Consent.Type.choices]
    # Broad audit trail for the patient across key models.
    patient_models = [
        "patients.Patient", "clinic.Encounter", "prescriptions.Prescription",
        "pathology.Biopsy", "adverse.AdverseEvent", "patients.LabResult",
        "patients.DrugExposure", "patients.Admission", "patients.Relapse",
    ]
    audit_q = AuditLog.objects.filter(
        object_pk=str(patient.pk), model_label__in=patient_models
    ) | AuditLog.objects.filter(object_repr__icontains=patient.patient_id)
    audit_entries = audit_q.order_by("-changed_at")[:50]

    # Lab trends for the charts (eGFR + proteinuria over time).
    def _pts(code):
        return list(
            patient.lab_results.filter(test__code=code, value_numeric__isnull=False)
            .exclude(result_date__isnull=True)
            .order_by("result_date")
            .values_list("result_date", "value_numeric")
        )
    egfr_pts = _pts("egfr")
    prot_pts = _pts("utp_24h")
    prot_label = "24-h urine protein (g/day)"
    if not prot_pts:
        prot_pts = _pts("upcr")
        prot_label = "UPCR (g/g)"
    _dates = sorted({d for d, _ in egfr_pts} | {d for d, _ in prot_pts})
    egfr_map = {d: float(v) for d, v in egfr_pts}
    prot_map = {d: float(v) for d, v in prot_pts}
    chart_dates = [d.isoformat() for d in _dates]
    chart_egfr = [egfr_map.get(d) for d in _dates]
    chart_prot = [prot_map.get(d) for d in _dates]
    has_chart = bool(_dates)

    # Recorded lab RESULTS (the values entered at baseline/follow-up), pivoted
    # date × key test, newest first — so they can be SEEN like the ordered labs.
    KEY_LAB_COLS = [
        ("egfr", "eGFR"), ("creatinine", "Creatinine"),
        ("utp_24h", "24h UTP"), ("upcr", "UPCR"), ("uacr", "UACR"),
        ("albumin", "Albumin"), ("hemoglobin", "Hb"), ("potassium", "K⁺"),
        ("hba1c", "HbA1c"), ("c3", "C3"), ("c4", "C4"),
        ("anti_pla2r", "PLA2R"), ("anti_dsdna", "dsDNA"), ("gd_iga1", "Gd-IgA1"),
        ("ana", "ANA"), ("anca", "ANCA"),
    ]
    by_date, present = {}, set()
    for r in (patient.lab_results
              .exclude(result_date__isnull=True).select_related("test")):
        # Numeric value if present, else the qualitative text (ANA/ANCA).
        val = r.value_numeric if r.value_numeric is not None else (r.value_text or None)
        if val is None:
            continue
        by_date.setdefault(r.result_date, {})[r.test.code] = val
        present.add(r.test.code)
    lab_cols = [(c, lbl) for c, lbl in KEY_LAB_COLS if c in present]

    def _cellfmt(v):
        if v is None or isinstance(v, str):
            return v
        return ("%.2f" % float(v)).rstrip("0").rstrip(".")  # numeric, trim zeros
    recorded_labs = [{"date": d, "cells": [_cellfmt(by_date[d].get(c)) for c, _ in lab_cols]}
                     for d in sorted(by_date, reverse=True)]

    # Enrich each visit with the eGFR + proteinuria recorded that day.
    visits = []
    for e in encounters:
        vals = by_date.get(e.encounter_date, {})
        prot, plabel = vals.get("utp_24h"), "g/d"
        if prot is None:
            prot, plabel = vals.get("upcr"), "g/g"
        visits.append({"e": e, "egfr": vals.get("egfr"),
                       "prot": prot, "prot_label": plabel})

    admissions = patient.admissions.select_related("biopsy").all()[:10]
    relapses = patient.relapses.all()[:10]
    # Auto drug-specific monitoring plan from the patient's active therapy
    # (CBC/LFT for MMF, potassium for finerenone, retinal for HCQ, …).
    try:
        from scheduling.services.monitoring import monitoring_requirements
        monitoring = monitoring_requirements(patient)
    except Exception:
        monitoring = []
    register_form = RegisterForm()
    # Auto-suggest GN-clinic registration once a positive biopsy is on file
    # (workflow step 4: biopsy-positive → register for structured follow-up).
    suggest_register = (
        patient.registration_status == "suspected"
        and patient.biopsies.filter(result_category="positive").exists())

    def _infer_ckd_stage(pat):
        """Infer CKD stage from latest eGFR."""
        egfr = pat.latest_egfr
        if not egfr:
            return None
        if egfr >= 90:
            return 1
        if egfr >= 60:
            return 2
        if egfr >= 45:
            return 3
        if egfr >= 30:
            return 4
        return 5

    # CDS plans: management, monitoring, follow-up schedule
    management_plan = None
    monitoring_plan_data = None
    followup_schedule = None
    cds_errors = []
    if profile and profile.differential:
        disease_id = (profile.differential[0] or {}).get("disease_id", "")
        if disease_id:
            try:
                from clinical_reasoning.services.management_plan import generate_management_plan
                management_plan = generate_management_plan(patient, disease_id)
            except Exception:
                logger.exception("management_plan failed for patient %s", patient.pk)
                management_plan = None
                cds_errors.append("management")
            try:
                from clinical_reasoning.services.monitoring_plan import generate_monitoring_plan
                monitoring_plan_data = generate_monitoring_plan(
                    patient, disease_id,
                    ckd_stage=_infer_ckd_stage(patient),
                )
            except Exception:
                logger.exception("monitoring_plan failed for patient %s", patient.pk)
                monitoring_plan_data = None
                cds_errors.append("monitoring")
            try:
                from clinical_reasoning.services.followup_scheduler import generate_follow_up_schedule
                risk_cat = "moderate"
                if profile.risk_assessment:
                    risk_cat = profile.risk_assessment.get("risk_category", "moderate")
                followup_schedule = generate_follow_up_schedule(
                    patient,
                    risk_category=risk_cat,
                    disease_phase=patient.current_phase or "active",
                    treatment_phase="maintenance",
                    disease_id=disease_id,
                    num_visits=6,
                )
            except Exception:
                logger.exception("followup_schedule failed for patient %s", patient.pk)
                followup_schedule = None
                cds_errors.append("followup")

    # Workflow step states for the progress strip.
    steps = [
        {"key": "register", "label": "Registered",
         "done": patient.registration_status == "registered",
         "icon": "fa-user-check", "url": f"/patients/{patient.pk}/"},
        {"key": "baseline", "label": "Baseline", "done": baseline is not None,
         "icon": "fa-clipboard-list",
         "url": f"/patients/{patient.pk}/baseline/"},
        {"key": "prescription", "label": "Prescription",
         "done": prescriptions.exists() if hasattr(prescriptions, "exists") else bool(prescriptions),
         "icon": "fa-prescription", "url": f"/patients/{patient.pk}/prescription/"},
        {"key": "followup", "label": "Follow-up",
         "done": patient.encounters.exists(), "icon": "fa-notes-medical",
         "url": f"/patients/{patient.pk}/followup/"},
        {"key": "outcome", "label": "Outcomes", "done": outcome is not None,
         "icon": "fa-chart-line", "url": f"/patients/{patient.pk}/outcome/recompute/"},
    ]
    last_visit = encounters[0] if encounters else None

    # The full ranking stays on the profile for audit/export; the page shows
    # only what is clinically in contention (see services/differential.py).
    from clinical_reasoning.services.differential import differential_for_display
    dx_display = differential_for_display(
        patient, getattr(profile, "differential", None) if profile else None)

    # Pathology summary: read-only projection with its source and any newer
    # biopsy still pending review; and the current comorbidities with their
    # source (a legacy-baseline-only item is flagged for confirmation).
    from pathology.services.projection import select_source, working_diagnosis_differs
    from patients.comorbidity import comorbidity_items
    _sel = select_source(patient)
    pathology_ctx = {"pending": _sel.pending_biopsies if _sel.state == "final" else [],
                     "differs": working_diagnosis_differs(patient)}

    return render(request, "clinic/patient_detail.html", {
        "active": "patients", "patient": patient, "baseline": baseline,
        "encounters": encounters, "prescriptions": prescriptions,
        "outcome": outcome, "profile": profile, "steps": steps,
        "dx_display": dx_display,
        "adverse_events": adverse_events,
        "biopsies": biopsies, "enrollments": enrollments, "consents": consents,
        "exposures": exposures, "lab_orders": lab_orders,
        "admissions": admissions, "relapses": relapses, "monitoring": monitoring,
        "register_form": register_form, "suggest_register": suggest_register,
        "visits": visits, "recorded_labs": recorded_labs, "lab_cols": lab_cols,
        "has_chart": has_chart, "chart_dates": chart_dates,
        "chart_egfr": chart_egfr, "chart_prot": chart_prot, "prot_label": prot_label,
        "audit_entries": audit_entries,
        "management_plan": management_plan,
        "monitoring_plan": monitoring_plan_data,
        "followup_schedule": followup_schedule,
        "cds_errors": cds_errors,
        "audit_records": _get_recommendation_audit_records(patient),
        "last_visit": last_visit,
        "patient_override_context": _get_patient_override_context(patient),
        "prediction_history": _get_prediction_history(patient),
        "pathology": pathology_ctx,
        "comorbidity_items": comorbidity_items(patient, baseline),
    })
