"""
Guided clinical-workflow UI for BGDDR.

A patient-centric set of server-rendered pages on top of the existing registry
models and services — the "register → baseline → prescription → follow-up →
outcomes → analyse → export" spine, styled like a modern clinical app.

No new models: every page reads/writes the existing ones and reuses the
prescription, analytics and export endpoints already in the project.
"""
from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

logger = logging.getLogger(__name__)

from patients.models import Patient
from encounters.models import ClinicalEncounter
from prescriptions.models import AdviceTemplate, Prescription, PrescriptionItem
from prescriptions.services.tapers import TAPER_PRESETS, is_systemic_steroid
from treatments.models import DrugMaster

from .forms import (AdmissionForm, AdverseEventForm, BaselineForm, BiopsyForm,
                    FollowupForm, FSGSPathologyForm, GNDiagnosisForm,
                    IgANScoreForm, ConsentForm, LabResultsForm,
                    LupusPathologyForm, MembranousPathologyForm, PatientForm,
                    RegisterForm, RelapseForm, StudyEnrollmentForm,
                    TreatmentExposureForm, LabOrderForm, collect_labs)

LOGIN = "/login/"

# Number of medication rows on the prescription form (form render + POST handler
# must agree — see prescription_create).
MAX_PRESCRIPTION_ITEMS = 12

# PatientForm field partition for the stepped registration wizard
# (clinic/patient_form.html). Any field not listed falls through to neither step,
# so keep these in sync with PatientForm.Meta.fields.
_PATIENT_DEM_FIELDS = ["name", "hospital_id", "phone", "sex", "dob"]
_PATIENT_CLIN_FIELDS = ["enrollment_date", "cohort", "diabetes_status",
                         "primary_diagnosis"]
_PATIENT_LEVEL2_FIELDS = [
    "hypertension", "cvd_history", "autoimmune_disease", "chronic_infection",
    "malignancy", "previous_kidney_disease", "prior_immunosuppression",
    "family_history_kidney", "diabetic_retinopathy", "neuropathy",
    "diabetic_foot_history", "smoking_status", "hepatitis_status", "hiv_status",
    # Histology — PatientForm drops these until a biopsy exists, so a field
    # listed here simply will not be rendered before then.
    "biopsy_diagnosis", "gn_broad_group",
    "gn_primary_secondary", "oxford_mestc", "isn_rps_class",
    "ckd_etiology", "transplant_status"]


def _clip(value, field):
    """Trim a POSTed value to the model field's max_length.

    SQLite silently accepts an over-long CharField; PostgreSQL raises
    DataError, so the same form submission would 500 only after the SQLite ->
    PostgreSQL migration. Clipping from the model's own limit keeps the two
    backends behaving identically and means a hand-crafted POST cannot take the
    prescription endpoint down.
    """
    text = (value or "").strip()
    limit = getattr(field, "max_length", None)
    if limit and len(text) > limit:
        text = text[:limit].rstrip()
    return text


def _save_labs(patient, form, result_date):
    """Record any point-of-care labs entered on the form as LabResult rows.
    Entering creatinine auto-derives eGFR + refreshes the patient's cached value.
    A lab failure must never lose the visit/baseline, so each is best-effort."""
    from labs.services.results import record_result
    saved = 0
    for code, value, text in collect_labs(form.cleaned_data):
        try:
            record_result(patient, code, result_date=result_date,
                          value_numeric=value, value_text=text)
            saved += 1
        except Exception:  # pragma: no cover - defensive
            pass
    return saved


# --- Patients ---------------------------------------------------------------

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


def _get_recommendation_audit_records(patient):
    """Get RecommendationAudit records for a patient, most recent first."""
    try:
        from knowledge.models import RecommendationAudit
        return RecommendationAudit.objects.filter(patient=patient).order_by("-issued_at")[:50]
    except Exception:
        return []


def _get_patient_override_context(patient):
    """Get override feedback context for a patient (Sprint 6)."""
    try:
        from feedback.analytics import patient_override_context
        return patient_override_context(patient)
    except Exception:
        return {"local_total": 0, "local_overrides": 0, "local_override_rate": None}


def _get_prediction_history(patient):
    """Get prediction audit trail for the patient (V10 Sprint 11)."""
    try:
        from analytics.services.prediction import prediction_history
        return prediction_history(patient.patient_id)
    except Exception:
        return []


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
    })


# --- Baseline ---------------------------------------------------------------

@login_required(login_url=LOGIN)
def baseline_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    instance = getattr(patient, "baseline", None)
    form = BaselineForm(request.POST or None, instance=instance, patient=patient)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.patient = patient
        # BaselineAssessment.save() syncs Level 2 comorbidities back to the
        # Patient record itself (_sync_level2_to_patient), so nothing to do here.
        obj.save()
        import datetime as _dt
        n = _save_labs(patient, form, obj.assessment_date or _dt.date.today())
        messages.success(request, "Baseline assessment saved."
                         + (f" {n} baseline lab result(s) recorded." if n else ""))
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/baseline_form.html",
                  {"active": "patients", "form": form, "patient": patient})


# --- Follow-up visit --------------------------------------------------------


def _sync_level2_from_followup(patient, form):
    """Sync Level 2 persistent fields from follow-up form back to Patient.

    Currently the follow-up form displays Level 2 as read-only; when clinicians
    update persistent data via Edit Patient, this sync ensures consistency.
    """
    pass  # Level 2 edits go through patient_edit → Patient form.


@login_required(login_url=LOGIN)
def followup_create(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = FollowupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        enc = form.save(commit=False)
        enc.patient = patient
        enc.save()
        n = _save_labs(patient, form, enc.encounter_date)
        # --- Level 2: sync any clinician changes back to Patient (single source) ---
        _sync_level2_from_followup(patient, form)
        # Advance the disease-phase state machine from this visit's assessment.
        from encounters.services.workflow import apply_visit
        apply_visit(enc)
        phase_note = ""
        if patient.current_phase:
            phase_note = f" Phase: {patient.get_current_phase_display()}."
        messages.success(request, "Follow-up visit recorded."
                         + (f" {n} lab result(s) recorded; eGFR updated." if n else "")
                         + phase_note)
        return redirect("clinic:patient_detail", pk=patient.pk)

    # Continuity: surface the previous visit + latest key labs so the clinician
    # continues from the last record instead of re-entering a blank sheet.
    prev = patient.encounters.order_by("-encounter_date", "-id").first()
    def _last(code):
        r = (patient.lab_results.filter(test__code=code, value_numeric__isnull=False)
             .order_by("-result_date").first())
        return r.value_numeric if r else None
    last_labs = [("eGFR", _last("egfr")), ("Creatinine", _last("creatinine")),
                 ("24h UTP", _last("utp_24h")), ("UPCR", _last("upcr")),
                 ("Albumin", _last("albumin")), ("K⁺", _last("potassium"))]
    last_labs = [(lbl, v) for lbl, v in last_labs if v is not None]

    baseline = getattr(patient, "baseline", None)
    baseline_dx = patient.primary_diagnosis or ""
    biopsy_dx = ""
    try:
        latest_biopsy = patient.biopsies.select_related("diagnosis").order_by("-biopsy_date").first()
        if latest_biopsy and latest_biopsy.diagnosis:
            biopsy_dx = latest_biopsy.diagnosis.diagnosis or ""
    except Exception:
        pass

    # Level 2 persistent clinical data from Patient (single source of truth).
    level2 = {
        "primary_diagnosis": patient.primary_diagnosis or "",
        "biopsy_diagnosis": patient.biopsy_diagnosis or "",
        "gn_broad_group": patient.gn_broad_group or "",
        "gn_primary_secondary": patient.gn_primary_secondary or "",
        "diabetes_status": patient.get_diabetes_status_display() if patient.diabetes_status != "none" else "",
        "hypertension": patient.hypertension,
        "autoimmune_disease": patient.autoimmune_disease,
        "chronic_infection": patient.chronic_infection,
        "smoking_status": patient.get_smoking_status_display() if patient.smoking_status else "",
        "hepatitis_status": patient.get_hepatitis_status_display() if patient.hepatitis_status else "",
        "hiv_status": patient.get_hiv_status_display() if patient.hiv_status else "",
        "oxford_mestc": patient.oxford_mestc or "",
        "isn_rps_class": patient.isn_rps_class or "",
    }

    return render(request, "clinic/followup_form.html",
                  {"active": "patients", "form": form, "patient": patient,
                   "prev": prev, "last_labs": last_labs,
                   "baseline": baseline,
                   "baseline_dx": baseline_dx, "biopsy_dx": biopsy_dx,
                   "level2": level2})


# --- GN registry workflow: registration, relapse, admission ------------------

@login_required(login_url=LOGIN)
def patient_register(request, pk):
    """Register a suspected patient into structured GN follow-up (step 4).
    Sets registration status/date and opens the Active disease phase."""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            from encounters.services.workflow import register_patient
            register_patient(patient, date=form.cleaned_data.get("registration_date"))
            messages.success(
                request, f"{patient.patient_id} registered in the GN clinic "
                f"({patient.registration_date}). Phase: Active disease.")
    return redirect("clinic:patient_detail", pk=patient.pk)


@login_required(login_url=LOGIN)
def relapse_create(request, pk):
    """Document a relapse and re-enter active monitoring (step 5E)."""
    patient = get_object_or_404(Patient, pk=pk)
    form = RelapseForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        from encounters.services.workflow import record_relapse
        enc = patient.encounters.order_by("-encounter_date", "-id").first()
        record_relapse(
            patient, form.cleaned_data["relapse_date"],
            form.cleaned_data["relapse_type"],
            criteria=form.cleaned_data.get("criteria", ""),
            action_taken=form.cleaned_data.get("action_taken", ""),
            encounter=enc, by=request.user)
        messages.success(request, "Relapse documented. Phase set to Relapse — "
                         "patient re-entered active monitoring.")
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/relapse_form.html",
                  {"active": "patients", "form": form, "patient": patient})


@login_required(login_url=LOGIN)
def admission_create(request, pk):
    """Record an inpatient work-up admission (step 2)."""
    patient = get_object_or_404(Patient, pk=pk)
    form = AdmissionForm(request.POST or None, patient=patient)
    if request.method == "POST" and form.is_valid():
        adm = form.save(commit=False)
        adm.patient = patient
        adm.save()
        messages.success(request, "Admission recorded.")
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/admission_form.html",
                  {"active": "patients", "form": form, "patient": patient})


# --- Adverse event (guided report) ------------------------------------------

@login_required(login_url=LOGIN)
def adverse_event_create(request, pk):
    """Guided adverse-event report for a patient. SAE status is auto-derived by
    the model (hospitalisation / G4 / G5). Feeds the cohort Safety page."""
    patient = get_object_or_404(Patient, pk=pk)
    form = AdverseEventForm(request.POST or None, patient=patient)
    if request.method == "POST" and form.is_valid():
        ae = form.save(commit=False)
        ae.patient = patient
        ae.save()
        flag = " (flagged serious)" if ae.serious else ""
        messages.success(request, f"Adverse event recorded{flag}.")
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/adverse_event_form.html",
                  {"active": "patients", "form": form, "patient": patient})


# --- Biopsy (guided entry) --------------------------------------------------

# Diagnosis value (GNDiagnosis.diagnosis) → which disease-specific score block
# to offer/save. Substring match keeps it robust to the exact choice codes.
_SCORE_HINTS = {
    "igan": ("iga",),
    "lupus": ("lupus", "ln"),
    "fsgs": ("fsgs",),
    "mn": ("membranous", "mn"),
}


def _reconcile_lupus_class(dx_form, lupus_form):
    """Keep the ISN/RPS class consistent between the diagnosis and the panel.

    Returns False (and attaches a form error) when the two contradict each
    other — that is the case only the pathologist can resolve. Otherwise the
    class is carried across, whichever of the two states it.
    """
    from pathology import lupus as lupus_rules

    if not dx_form.is_valid():
        return True  # the diagnosis has its own errors; nothing to reconcile

    diagnosis = dx_form.cleaned_data.get("diagnosis") or ""
    if not lupus_rules.is_lupus(diagnosis):
        return True

    panel_class = ""
    if lupus_form.is_valid():
        panel_class = lupus_form.cleaned_data.get("isn_rps_class") or ""

    new_diagnosis, new_class, error = lupus_rules.reconcile(diagnosis, panel_class)
    if error:
        lupus_form.add_error("isn_rps_class", error)
        return False

    # cleaned_data is not enough: the model instance was already populated
    # during validation, and that is what save() writes.
    if new_diagnosis != diagnosis:
        dx_form.cleaned_data["diagnosis"] = new_diagnosis
        dx_form.instance.diagnosis = new_diagnosis
    if new_class != panel_class and lupus_form.is_bound and lupus_form.is_valid():
        lupus_form.cleaned_data["isn_rps_class"] = new_class
        lupus_form.instance.isn_rps_class = new_class
    return True


def _sync_biopsy_to_patient(patient, dxo, active_scores):
    """Sync Level 2 biopsy data to Patient model (single source of truth)."""
    changed = False
    if dxo.diagnosis and not patient.biopsy_diagnosis:
        patient.biopsy_diagnosis = dxo.get_diagnosis_display() or dxo.diagnosis
        changed = True
    if dxo.diagnosis and not patient.primary_diagnosis:
        patient.primary_diagnosis = dxo.diagnosis
        changed = True
    if dxo.broad_group and not patient.gn_broad_group:
        patient.gn_broad_group = dxo.broad_group
        changed = True
    if dxo.primary_secondary and not patient.gn_primary_secondary:
        patient.gn_primary_secondary = dxo.primary_secondary
        changed = True
    # Oxford MEST-C
    igan = active_scores.get("igan")
    if igan and igan.is_valid():
        score = f"M{igan.cleaned_data['M']}E{igan.cleaned_data['E']}S{igan.cleaned_data['S']}T{igan.cleaned_data['T']}C{igan.cleaned_data['C']}"
        if not patient.oxford_mestc:
            patient.oxford_mestc = score
            changed = True
    # ISN/RPS class — from the diagnosis, which is where it is stated; the panel
    # is only a fallback for a diagnosis recorded without a class.
    from pathology import lupus as lupus_rules
    cls = lupus_rules.class_from_diagnosis(dxo.diagnosis)
    if not cls:
        lupus = active_scores.get("lupus")
        if lupus and lupus.is_valid():
            cls = lupus.cleaned_data.get("isn_rps_class", "")
    if cls and not patient.isn_rps_class:
        patient.isn_rps_class = cls
        changed = True
    if changed:
        patient.save(update_fields=[
            "biopsy_diagnosis", "primary_diagnosis", "gn_broad_group",
            "gn_primary_secondary", "oxford_mestc",
            "isn_rps_class", "updated_at"])


@login_required(login_url=LOGIN)
def biopsy_create(request, pk):
    """Guided biopsy entry: the core biopsy + its diagnosis (the driver of the
    disease-specific remission rules) + optional MEST-C / ISN-RPS / FSGS / MN
    score blocks. A score block is only saved when the user actually fills it.
    New biopsies enter the central-review workflow as 'pending'."""
    patient = get_object_or_404(Patient, pk=pk)
    post = request.POST or None
    bx = BiopsyForm(post, prefix="bx")
    dx = GNDiagnosisForm(post, prefix="dx")
    scores = {
        "igan": IgANScoreForm(post, prefix="igan"),
        "lupus": LupusPathologyForm(post, prefix="lupus"),
        "fsgs": FSGSPathologyForm(post, prefix="fsgs"),
        "mn": MembranousPathologyForm(post, prefix="mn"),
    }

    if request.method == "POST":
        # Validate the required pair; validate a score block only if touched.
        ok = bx.is_valid()
        ok = dx.is_valid() and ok
        active = {k: f for k, f in scores.items() if f.has_changed()}
        for f in active.values():
            ok = f.is_valid() and ok
        # The ISN/RPS class is stated once: the diagnosis and the lupus panel
        # must agree, and a contradiction is reported rather than resolved.
        ok = _reconcile_lupus_class(dx, scores["lupus"]) and ok

        if ok:
            biopsy = bx.save(commit=False)
            biopsy.patient = patient
            biopsy.save()
            dxo = dx.save(commit=False)
            dxo.biopsy = biopsy
            dxo.save()
            for f in active.values():
                obj = f.save(commit=False)
                obj.biopsy = biopsy
                obj.save()
            # --- Level 2: sync biopsy diagnosis to Patient (single source) ---
            _sync_biopsy_to_patient(patient, dxo, active)
            extra = f" + {len(active)} score block(s)" if active else ""
            # --- Confirm-GN gate (workflow) --------------------------------
            # A positive biopsy (specific GN) auto-registers the patient into the
            # GN clinic; a negative one (no specific GN) exits the registry.
            from patients.workflow import BiopsyResult, RegistrationStatus
            gate = ""
            if patient.registration_status == RegistrationStatus.SUSPECTED:
                if biopsy.result_category == BiopsyResult.POSITIVE:
                    from encounters.services.workflow import register_patient
                    register_patient(patient, date=biopsy.biopsy_date)
                    gate = (f" Confirmed GN — {patient.patient_id} was auto-registered "
                            "into the GN clinic (phase: Active disease).")
                elif biopsy.result_category == BiopsyResult.NEGATIVE:
                    patient.registration_status = RegistrationStatus.EXCLUDED
                    patient.save(update_fields=["registration_status"])
                    gate = " No specific GN on biopsy — patient marked excluded (registry ends)."
            messages.success(
                request, f"Biopsy recorded ({dxo.get_diagnosis_display()}){extra}. "
                f"It enters central review as 'pending'.{gate}")
            return redirect("clinic:patient_detail", pk=patient.pk)

    return render(request, "clinic/biopsy_form.html", {
        "active": "patients", "patient": patient,
        "bx": bx, "dx": dx, "scores": scores, "score_hints": _SCORE_HINTS,
    })


# --- Study enrolment (guided) -----------------------------------------------

@login_required(login_url=LOGIN)
def study_enroll(request, pk):
    """Screen + enrol a patient into a study. Delegates to the randomization
    engine, which screens, enforces the trial-consent gate and allocates an arm
    via the seeded sequence. Outcomes (enrolled / ineligible / consent-required /
    already-enrolled) are surfaced as messages."""
    from studies.models import StudyEnrollment
    from studies.services.randomization import (AlreadyEnrolled, ConsentRequired,
                                                enroll)
    patient = get_object_or_404(Patient, pk=pk)
    form = StudyEnrollmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        study = form.cleaned_data["study"]
        try:
            enr = enroll(
                study, patient, by=request.user,
                screened_date=form.cleaned_data.get("screened_date") or None,
                enrolled_date=form.cleaned_data.get("enrolled_date") or None,
            )
        except ConsentRequired as exc:
            messages.error(request, f"{exc} Record TRIAL consent for this patient first.")
            return redirect("clinic:study_enroll", pk=patient.pk)
        except AlreadyEnrolled as exc:
            messages.warning(request, str(exc))
            return redirect("clinic:patient_detail", pk=patient.pk)
        except Exception as exc:  # pragma: no cover - defensive
            messages.error(request, f"Could not enrol: {exc}")
            return redirect("clinic:study_enroll", pk=patient.pk)

        if enr.status == StudyEnrollment.Status.INELIGIBLE:
            reasons = ", ".join(enr.ineligibility_reasons) or "no reason recorded"
            messages.warning(request, f"Screened ineligible for {study.code}: {reasons}.")
        elif enr.status == StudyEnrollment.Status.ENROLLED:
            arm = f" → arm “{enr.arm.name}”" if enr.arm else ""
            strat = f" (stratum {enr.stratum})" if enr.stratum and enr.stratum != "all" else ""
            messages.success(request, f"Enrolled in {study.code}{arm}{strat}.")
        else:
            messages.info(request, f"Recorded as {enr.get_status_display()} for {study.code}.")
        return redirect("clinic:patient_detail", pk=patient.pk)

    studies = list(form.fields["study"].queryset)
    return render(request, "clinic/study_enroll_form.html", {
        "active": "patients", "patient": patient, "form": form, "studies": studies,
    })


# --- Consent (guided grant / withdraw) --------------------------------------

@login_required(login_url=LOGIN)
def consent_manage(request, pk):
    """Record or withdraw versioned patient consent. Granting a type supersedes
    its current consent (version chain); withdrawing flips the current one to
    withdrawn. TRIAL consent here unblocks registry-embedded trial enrolment."""
    from audit.models import Consent
    from audit.services.consent import (consent_history, current_consent,
                                        grant_consent, withdraw_consent)
    patient = get_object_or_404(Patient, pk=pk)
    form = ConsentForm(request.POST or None)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "withdraw":
            ctype = request.POST.get("consent_type")
            label = dict(Consent.Type.choices).get(ctype, ctype)
            res = withdraw_consent(patient, ctype)
            if res:
                messages.success(request, f"{label} consent withdrawn.")
            else:
                messages.warning(request, f"No current {label} consent to withdraw.")
            return redirect("clinic:consent", pk=patient.pk)
        if form.is_valid():
            cd = form.cleaned_data
            grant_consent(
                patient, cd["consent_type"], cd["form_version"],
                consent_date=cd.get("consent_date") or None,
                obtained_by=request.user, scope=cd.get("scope", ""),
                notes=cd.get("notes", ""))
            label = dict(Consent.Type.choices).get(cd["consent_type"])
            messages.success(request, f"{label} consent recorded ({cd['form_version']}).")
            return redirect("clinic:patient_detail", pk=patient.pk)

    types = [{"value": value, "label": label,
              "current": current_consent(patient, value)}
             for value, label in Consent.Type.choices]
    history = consent_history(patient)
    return render(request, "clinic/consent_form.html", {
        "active": "patients", "patient": patient, "form": form,
        "types": types, "history": history,
    })


# --- Treatment exposure (guided, for prior/external meds) --------------------

@login_required(login_url=LOGIN)
def treatment_add(request, pk):
    """Record a medication episode directly — for prior/external drugs not
    captured by the in-clinic prescription→reconciliation flow. The form keeps
    the engine invariant (one ongoing episode per drug), so a manually-added
    ongoing episode is later continued/changed by prescriptions cleanly."""
    patient = get_object_or_404(Patient, pk=pk)
    form = TreatmentExposureForm(request.POST or None, patient=patient)
    if request.method == "POST" and form.is_valid():
        exp = form.save(commit=False)
        exp.patient = patient
        exp.drug_name = exp.drug.generic_name
        exp.save()
        span = "ongoing" if exp.ongoing else f"stopped {exp.stop_date}"
        messages.success(request, f"Recorded {exp.drug_name} ({span}).")
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/treatment_form.html",
                  {"active": "patients", "form": form, "patient": patient})


# --- Prescription (guided create) -------------------------------------------

@login_required(login_url=LOGIN)
def prescription_create(request, pk):
    """Guided prescription entry: a draft Prescription on the patient's latest
    visit + its items, then hand off to the existing preview/finalize/PDF flow.
    Print the FULL current regimen each visit — that set is what finalize
    reconciles into TreatmentExposure episodes."""
    from django.db.models import Max
    import datetime as dt
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
        for i in range(1, MAX_PRESCRIPTION_ITEMS + 1):
            drug_id = request.POST.get(f"drug_{i}")
            # Skip empty rows and reject anything that isn't a known drug id.
            if not drug_id or not drug_id.isdigit() or int(drug_id) not in valid_drug_ids:
                continue
            strength_val = _clip(
                request.POST.get(f"strength_{i}"), PrescriptionItem._meta.get_field("strength"))
            PrescriptionItem.objects.create(
                prescription=rx, drug_id=int(drug_id),
                brand=_clip(
                    request.POST.get(f"brand_{i}"), PrescriptionItem._meta.get_field("brand")),
                strength=strength_val,
                # No separate "dose" column — strength is the regimen amount and
                # drives reconciliation's dose-change detection (signature).
                dose=strength_val,
                route=_clip(
                    (request.POST.get(f"route_{i}") or "").strip().upper(),
                    PrescriptionItem._meta.get_field("route")),
                frequency=_clip(
                    request.POST.get(f"frequency_{i}"), PrescriptionItem._meta.get_field("frequency")),
                timing=_clip(
                    request.POST.get(f"timing_{i}") or "after",
                    PrescriptionItem._meta.get_field("timing")),
                duration=_clip(
                    request.POST.get(f"duration_{i}"), PrescriptionItem._meta.get_field("duration")),
                instruction_bn=_clip(
                    request.POST.get(f"instruction_{i}"),
                    PrescriptionItem._meta.get_field("instruction_bn")),
                taper_notes=(request.POST.get(f"taper_{i}") or "").strip(),
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
    # Default next visit = 4 weeks from today (clinic schedule)
    default_next = (dt.date.today() + dt.timedelta(weeks=4)).isoformat()
    from patients import choices
    from labs.models import LabTest

    # Carry-forward: pre-fill rows from the patient's most recent prescription so
    # the FULL regimen is preserved; the clinician edits / removes / adds before
    # finalize. (Print the full current regimen each visit — finalize reconciles it.)
    prev = (Prescription.objects.filter(encounter__patient=patient)
            .order_by("-created_at").prefetch_related("items").first())
    prev_items = list(prev.items.order_by("sort_order")) if prev else []
    item_by_drug = {it.drug_id: it for it in prev_items}

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
            strength=(it.strength if it and it.strength else exp.dose),
            dose=exp.dose, route=(it.route_value if it else exp.route),
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
                dose=it.dose, route=it.route_value, frequency=it.frequency,
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
    prefill_invest = set()
    if prev and prev.investigations_advised:
        prefill_invest = {s.strip() for s in prev.investigations_advised.split(",") if s.strip()}

    # Declutter: show carried-forward rows + a couple of blanks; the rest are
    # revealed one at a time by the "Add medication" button.
    initial_visible = min(MAX_PRESCRIPTION_ITEMS, max(3, len(carried) + 1))

    # Comorbidities: standard tick-list, pre-checked from the baseline record
    # (and the patient's diabetes status), then carried forward from the last Rx.
    comorbidity_options = ["Hypertension", "Diabetes mellitus", "Bronchial asthma",
                           "Hypothyroidism", "Dyslipidaemia", "Ischaemic heart disease",
                           "COPD", "CKD"]
    # Patient Level 2 + baseline, via the shared helper, so everything recorded
    # at registration or baseline is pre-ticked here.
    from patients.comorbidity import comorbidity_summary
    prefill_comorbid = set()
    for label in comorbidity_summary(patient, getattr(patient, "baseline", None)):
        # The tick-list uses the short label; "Diabetes mellitus (Type 2)" and
        # the like must still match their checkbox.
        match = next((o for o in comorbidity_options if label.startswith(o)), None)
        prefill_comorbid.add(match or label)
    if prev and prev.comorbidities:
        prefill_comorbid |= {s.strip() for s in prev.comorbidities.split(",") if s.strip()}
    # Any carried-forward value not in the standard list -> free-text box.
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
        "taper_presets": [{"label": p.label, "text": p.text}
                          for p in TAPER_PRESETS],
        "comorbidity_options": comorbidity_options,
        "prefill_comorbid": prefill_comorbid, "comorbid_extra": comorbid_extra,
    })


# --- Outcomes ---------------------------------------------------------------

@login_required(login_url=LOGIN)
def outcome_recompute(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    try:
        from analytics.services.outcomes import compute_patient_outcome
        compute_patient_outcome(patient)
        messages.success(request, "Outcomes recomputed from current data.")
    except Exception as exc:  # pragma: no cover - defensive
        messages.error(request, f"Could not compute outcomes: {exc}")
    return redirect("clinic:patient_detail", pk=patient.pk)


@login_required(login_url=LOGIN)
def run_clinical_intelligence(request, pk):
    """Trigger the full clinical intelligence pipeline for a patient."""
    patient = get_object_or_404(Patient, pk=pk)
    try:
        from clinical_reasoning.services.clinical_intelligence import (
            ClinicalIntelligenceService,
        )
        service = ClinicalIntelligenceService()
        report = service.analyze_patient(patient.patient_id)
        complexity = report.get("complexity", {}).get("level", "unknown")
        confidence = report.get("confidence", {}).get("level", "unknown")
        messages.success(
            request,
            f"Clinical intelligence updated — complexity: {complexity}, "
            f"confidence: {confidence}.",
        )
    except Exception as exc:
        messages.error(request, f"Clinical intelligence failed: {exc}")
    return redirect("clinic:patient_detail", pk=patient.pk)


@login_required(login_url=LOGIN)
def verify_treatment_with_vera(request, pk):
    """Concise clinical case summary for independent AI review.

    Generates a one-page summary of the patient's essential clinical data
    suitable for copying into Vera Health or any other clinical AI.

    Returns rendered HTML for HTMX inline display. Only accepts POST.
    """
    if request.method != "POST":
        from django.http import HttpResponseNotAllowed
        return HttpResponseNotAllowed(["POST"])

    patient = get_object_or_404(Patient, pk=pk)

    from clinical_reasoning.models import ClinicalProfile
    try:
        profile = ClinicalProfile.objects.get(patient=patient)
    except ClinicalProfile.DoesNotExist:
        profile = None

    if not profile or not profile.differential:
        return render(request, "clinic/vera_verification_results.html", {
            "error": "No clinical profile available. Run clinical intelligence first.",
            "patient": patient,
        })

    disease_name = (profile.differential[0] or {}).get("disease_name", "Unknown")

    features = profile.features_snapshot if profile else {}
    patient_sex_display = patient.get_sex_display() if hasattr(patient, "get_sex_display") else patient.sex

    # Age
    import datetime as dt_module
    patient_age = None
    if patient.dob:
        today = dt_module.date.today()
        patient_age = today.year - patient.dob.year - (
            (today.month, today.day) < (patient.dob.month, patient.dob.day)
        )

    # Baseline / encounter data
    baseline = getattr(patient, "baseline", None)
    latest_encounter = patient.encounters.order_by("-encounter_date").first() if hasattr(patient, "encounters") else None

    # BP and weight
    patient_bp_systolic = patient_bp_diastolic = patient_weight = ""
    patient_height = ""
    if latest_encounter:
        patient_bp_systolic = latest_encounter.systolic_bp or ""
        patient_bp_diastolic = latest_encounter.diastolic_bp or ""
        patient_weight = getattr(latest_encounter, "weight_kg", None) or ""
    elif baseline:
        patient_bp_systolic = getattr(baseline, "systolic_bp", None) or ""
        patient_bp_diastolic = getattr(baseline, "diastolic_bp", None) or ""
        patient_weight = getattr(baseline, "weight_kg", None) or ""
    if baseline:
        patient_height = getattr(baseline, "height_cm", None) or ""

    # Proteinuria from features → labs → baseline
    raw_proteinuria = features.get("proteinuria", "")
    if raw_proteinuria in (None, "none", ""):
        try:
            from labs.models import LabResult
            from datetime import timedelta
            six_months_ago = timezone.now().date() - timedelta(days=180)
            prot_lab = LabResult.objects.filter(
                patient=patient,
                test__code__in=("utp_24h", "upcr", "uacr"),
                result_date__gte=six_months_ago,
            ).order_by("-result_date").first()
            if prot_lab and prot_lab.value_numeric is not None:
                raw_proteinuria = f"{prot_lab.value_numeric} {prot_lab.unit or 'g/day'}"
        except Exception:
            pass
    if raw_proteinuria in (None, "none", ""):
        if baseline:
            syndromes = getattr(baseline, "presentation_syndromes", None) or []
            if any("proteinuria" in s for s in syndromes):
                raw_proteinuria = "Present (not quantified)"
    if isinstance(raw_proteinuria, (int, float)):
        patient_proteinuria = f"{raw_proteinuria} g/day"
    else:
        patient_proteinuria = "" if raw_proteinuria in (None, "none") else raw_proteinuria

    # eGFR and creatinine
    patient_egfr = patient.latest_egfr or features.get("latest_egfr")
    patient_creatinine = ""
    try:
        from labs.models import LabResult
        cr_lab = LabResult.objects.filter(patient=patient, test__code="creatinine").order_by("-result_date").first()
        if cr_lab and cr_lab.value_numeric is not None:
            patient_creatinine = f"{cr_lab.value_numeric} {cr_lab.unit or 'mg/dL'}"
    except Exception:
        pass

    # CKD stage from eGFR
    ckd_stage = ""
    if patient_egfr:
        egfr = float(patient_egfr)
        if egfr >= 90:
            ckd_stage = "G1"
        elif egfr >= 60:
            ckd_stage = "G2"
        elif egfr >= 45:
            ckd_stage = "G3a"
        elif egfr >= 30:
            ckd_stage = "G3b"
        elif egfr >= 15:
            ckd_stage = "G4"
        else:
            ckd_stage = "G5"

    # Comorbidities — one shared list so the AI prompt sees everything recorded,
    # not just HTN/DM/CVD.
    from patients.comorbidity import comorbidity_text
    comorbidities_text = comorbidity_text(patient, baseline)

    # Current medications
    meds = []
    if hasattr(patient, "exposures"):
        for exp in patient.exposures.filter(ongoing=True).select_related("drug")[:5]:
            name = exp.drug_name or getattr(exp.drug, "generic_name", "")
            if name:
                meds.append(name)
    meds_text = ", ".join(meds) if meds else "None"

    # Biopsy
    biopsy_text = ""
    biopsy = patient.biopsies.order_by("-biopsy_date").first() if hasattr(patient, "biopsies") else None
    if biopsy:
        gn = getattr(biopsy, "gn_diagnosis", None)
        dx = gn.diagnosis if gn else ""
        crescents = "Crescents present" if biopsy.crescents_present else "Crescents absent"
        biopsy_text = f"{dx or 'Biopsy done'}; {crescents}"

    # GDES assessment
    gdes_assessment = features.get("disease_phase", "")
    if gdes_assessment:
        gdes_assessment = f"{gdes_assessment.capitalize()} disease"
        if patient_proteinuria and patient_proteinuria not in ("None", "-", ""):
            gdes_assessment += f" with persistent proteinuria"
    else:
        gdes_assessment = "Pending assessment"

    # Build case summary rows for template
    case_rows = [
        ("Diagnosis", disease_name),
        ("Patient", f"{patient_age} years \u2022 {patient_sex_display} \u2022 Weight {patient_weight} kg" if patient_age and patient_weight else f"{patient_age or '-'} years \u2022 {patient_sex_display}"),
        ("Height", f"{patient_height} cm" if patient_height else "-"),
        ("Blood Pressure", f"{patient_bp_systolic}/{patient_bp_diastolic} mmHg" if patient_bp_systolic and patient_bp_diastolic else "-"),
        ("eGFR", f"{patient_egfr} mL/min/1.73m\u00B2" if patient_egfr else "-"),
        ("Serum Creatinine", patient_creatinine or "-"),
        ("Proteinuria", patient_proteinuria or "-"),
        ("CKD Stage", ckd_stage or "-"),
        ("Relevant Comorbidities", comorbidities_text),
        ("Current Medication", meds_text),
        ("Kidney Biopsy", biopsy_text or "Not available"),
        ("Current GDES Assessment", gdes_assessment),
    ]

    # Build plain-text copy format
    copy_lines = [
        "Please review the following patient independently and generate a structured, evidence-based management plan.",
        "",
        "Patient Summary",
        "",
        f"Diagnosis: {disease_name}",
        f"Age: {patient_age} years" if patient_age else "Age: Not recorded",
        f"Sex: {patient_sex_display}",
        f"Weight: {patient_weight} kg" if patient_weight else "Weight: Not recorded",
        f"Height: {patient_height} cm" if patient_height else "Height: Not recorded",
        f"Blood Pressure: {patient_bp_systolic}/{patient_bp_diastolic} mmHg" if patient_bp_systolic and patient_bp_diastolic else "Blood Pressure: Not recorded",
        f"eGFR: {patient_egfr} mL/min/1.73m\u00B2" if patient_egfr else "eGFR: Not recorded",
        f"Serum Creatinine: {patient_creatinine}" if patient_creatinine else "Serum Creatinine: Not recorded",
        f"24-hour Urine Protein: {patient_proteinuria}" if patient_proteinuria else "Proteinuria: Not quantified",
        f"CKD Stage: {ckd_stage}" if ckd_stage else "",
        f"Relevant Comorbidities: {comorbidities_text}",
        f"Current Medication: {meds_text}",
        f"Kidney Biopsy: {biopsy_text}" if biopsy_text else "",
        "",
        "Please provide:",
        "",
        "1. Confirmation or revision of the diagnosis.",
        "",
        "2. Disease severity and risk assessment.",
        "",
        "3. A personalised treatment plan based on:",
        "   - Age",
        "   - Sex",
        "   - Weight",
        "   - Renal function",
        "   - Current clinical findings",
        "",
        "4. Drug recommendations including:",
        "   - Drug name",
        "   - Dose",
        "   - Frequency",
        "   - Duration",
        "   - Renal dose adjustment",
        "   - Monitoring requirements",
        "",
        "5. Monitoring plan and follow-up schedule.",
        "",
        "6. Contraindications and drug interactions.",
        "",
        "7. Supporting guideline recommendations and evidence.",
        "",
        "Please provide your recommendations in a structured clinical format.",
    ]
    copy_text = "\n".join(copy_lines)

    return render(request, "clinic/vera_verification_results.html", {
        "case_rows": case_rows,
        "copy_text": copy_text,
        "patient": patient,
    })


def _build_treatment_verification_prompt(patient, profile, management_plan):
    """Build a prompt for Vera to verify a treatment plan."""
    differential_text = "Not available"
    if profile and profile.differential:
        top = profile.differential[0] if profile.differential else {}
        differential_text = (
            f"Disease: {top.get('disease_name', 'Unknown')} "
            f"(confidence {top.get('confidence', 0)}%)"
        )

    features = []
    if profile and profile.features_snapshot:
        f = profile.features_snapshot
        if f.get("proteinuria") and f["proteinuria"] != "none":
            features.append(f"Proteinuria: {f['proteinuria']}")
        if f.get("latest_egfr"):
            features.append(f"eGFR: {f['latest_egfr']}")
        if f.get("biopsy"):
            features.append(f"Biopsy: {', '.join(f['biopsy'])}")
        if f.get("labs"):
            features.append(f"Labs: {', '.join(f['labs'][:5])}")

    # Build treatment plan text (handle both ManagementPlan dataclass and dict)
    treatment_lines = []
    first_line = management_plan.first_line if hasattr(management_plan, "first_line") else management_plan.get("first_line", [])
    second_line = management_plan.second_line if hasattr(management_plan, "second_line") else management_plan.get("second_line", [])
    rescue = management_plan.rescue_therapy if hasattr(management_plan, "rescue_therapy") else management_plan.get("rescue_therapy", [])

    if first_line:
        treatment_lines.append("First-line therapy:")
        for tx in first_line:
            treatment_lines.append(f"  - {tx.get('drug', 'Unknown')}: {tx.get('dose', '')} for {tx.get('duration', '')}")
            if tx.get("target"):
                treatment_lines.append(f"    Target: {tx['target']}")

    if second_line:
        treatment_lines.append("Second-line therapy:")
        for tx in second_line:
            treatment_lines.append(f"  - {tx.get('drug', 'Unknown')}: {tx.get('dose', '')} for {tx.get('duration', '')}")
            if tx.get("conditions"):
                treatment_lines.append(f"    When: {tx['conditions']}")

    if rescue:
        treatment_lines.append("Rescue therapy:")
        for tx in rescue:
            treatment_lines.append(f"  - {tx.get('drug', 'Unknown')}: {tx.get('dose', '')} for {tx.get('duration', '')}")

    treatment_text = "\n".join(treatment_lines) if treatment_lines else "Not available"

    # Build patient context
    patient_context = []
    if patient.latest_egfr:
        patient_context.append(f"Latest eGFR: {patient.latest_egfr}")
    if patient.sex:
        patient_context.append(f"Sex: {patient.sex}")
    if patient.dob:
        patient_context.append(f"DOB: {patient.dob}")

    prompt = (
        f"Treatment Plan Verification Request\n"
        f"===================================\n\n"
        f"Patient: {patient.name}\n"
        f"{'  '.join(patient_context)}\n\n"
        f"Diagnosis: {differential_text}\n"
        f"Clinical Features:\n"
        + ("\n".join(f"  - {f}" for f in features) if features else "  Not available") +
        f"\n\nCurrent Treatment Plan:\n{treatment_text}\n\n"
        f"Please verify this treatment plan for:\n"
        f"1. Appropriateness for this specific patient\n"
        f"2. Alignment with current guidelines (KDIGO 2021/2024)\n"
        f"3. Safety considerations given patient context\n"
        f"4. Any alternative options that should be considered\n"
        f"5. Potential drug interactions or contraindications\n"
    )

    return prompt


def _build_prescription_prompt(patient, profile, management_plan):
    """Build a structured prompt for Vera to generate a personalised prescription.

    Returns plain-text suitable for clipboard → paste into any clinical AI.
    """
    import datetime as dt_module

    features = profile.features_snapshot if profile else {}
    disease_name = "Unknown"
    disease_id = ""
    if profile and profile.differential:
        top = profile.differential[0] or {}
        disease_name = top.get("disease_name", "Unknown")
        disease_id = top.get("disease_id", "")

    # Demographics
    patient_age = None
    if patient.dob:
        today = dt_module.date.today()
        patient_age = today.year - patient.dob.year - (
            (today.month, today.day) < (patient.dob.month, patient.dob.day)
        )
    sex = patient.get_sex_display() if hasattr(patient, "get_sex_display") else patient.sex

    # Weight
    weight = ""
    baseline = getattr(patient, "baseline", None)
    latest_enc = patient.encounters.order_by("-encounter_date").first() if hasattr(patient, "encounters") else None
    if latest_enc and latest_enc.weight_kg:
        weight = f"{latest_enc.weight_kg}"
    elif baseline and baseline.weight_kg:
        weight = f"{baseline.weight_kg}"

    # Height & BMI
    height = ""
    bmi = ""
    if baseline:
        if baseline.height_cm:
            height = f"{baseline.height_cm}"
        if baseline.bmi:
            bmi = f"{baseline.bmi}"

    # Labs
    def _latest(code):
        from labs.models import LabResult
        r = LabResult.objects.filter(patient=patient, test__code=code).order_by("-result_date").first()
        if r and r.value_numeric is not None:
            return f"{r.value_numeric} {r.unit or ''}".strip()
        return None

    egfr = _latest("egfr") or (f"{features['latest_egfr']}" if features.get("latest_egfr") else None)
    creatinine = _latest("creatinine")
    proteinuria = features.get("proteinuria", "")
    if proteinuria in (None, "none", ""):
        proteinuria = _latest("utp_24h") or _latest("upcr") or _latest("uacr") or ""
    albumin = _latest("albumin")
    potassium = _latest("potassium")
    hba1c = _latest("hba1c")
    c3 = _latest("c3")
    c4 = _latest("c4")
    hb = _latest("hemoglobin")

    # CKD stage
    ckd_stage = ""
    if egfr:
        try:
            e = float(egfr.split()[0])
            if e >= 90: ckd_stage = "G1"
            elif e >= 60: ckd_stage = "G2"
            elif e >= 45: ckd_stage = "G3a"
            elif e >= 30: ckd_stage = "G3b"
            elif e >= 15: ckd_stage = "G4"
            else: ckd_stage = "G5"
        except (ValueError, IndexError):
            pass

    # Current meds
    meds = []
    if hasattr(patient, "exposures"):
        for exp in patient.exposures.filter(ongoing=True).select_related("drug")[:8]:
            name = exp.drug_name or getattr(exp.drug, "generic_name", "")
            if name:
                dose_part = f" {exp.dose}" if exp.dose else ""
                freq_part = f" {exp.frequency}" if exp.frequency else ""
                meds.append(f"{name}{dose_part}{freq_part}")
    meds_text = "; ".join(meds) if meds else "None"

    # Biopsy
    biopsy_text = ""
    biopsy = patient.biopsies.order_by("-biopsy_date").first() if hasattr(patient, "biopsies") else None
    if biopsy:
        gn = getattr(biopsy, "gn_diagnosis", None)
        dx = gn.diagnosis if gn else ""
        biopsy_text = dx or "Biopsy done (details not recorded)"
    else:
        biopsy_text = "Not available"

    # Comorbidities — shared helper (see patients/comorbidity.py).
    from patients.comorbidity import comorbidity_text
    comorbidities_text = comorbidity_text(patient, baseline)

    # Current management plan summary
    plan_lines = []
    if management_plan:
        for label, items in [("First-line", management_plan.first_line),
                             ("Second-line", management_plan.second_line),
                             ("Rescue", management_plan.rescue_therapy)]:
            for tx in items:
                drug = tx.get("drug", "")
                dose = tx.get("dose", "")
                dur = tx.get("duration", "")
                plan_lines.append(f"  {label}: {drug} {dose} for {dur}".strip())
    plan_text = "\n".join(plan_lines) if plan_lines else "  Not yet prescribed"

    lines = [
        "Please generate a structured, personalised prescription for this patient.",
        "Base your recommendations on the clinical data below and current evidence-based guidelines.",
        "",
        "=== PATIENT DATA ===",
        "",
        f"Diagnosis: {disease_name}",
        f"Age: {patient_age} years" if patient_age else "Age: Not recorded",
        f"Sex: {sex}",
        f"Weight: {weight} kg" if weight else "Weight: Not recorded",
        f"Height: {height} cm" if height else "",
        f"BMI: {bmi} kg/m²" if bmi else "",
        "",
        "=== RENAL FUNCTION ===",
        "",
        f"eGFR: {egfr} mL/min/1.73m²" if egfr else "eGFR: Not recorded",
        f"Serum Creatinine: {creatinine}" if creatinine else "Creatinine: Not recorded",
        f"CKD Stage: {ckd_stage}" if ckd_stage else "",
        "",
        "=== LABORATORY VALUES ===",
        "",
    ]
    if proteinuria:
        lines.append(f"Proteinuria: {proteinuria}")
    if albumin:
        lines.append(f"Serum Albumin: {albumin}")
    if potassium:
        lines.append(f"Serum Potassium: {potassium}")
    if hb:
        lines.append(f"Hemoglobin: {hb}")
    if c3:
        lines.append(f"Complement C3: {c3}")
    if c4:
        lines.append(f"Complement C4: {c4}")
    if hba1c:
        lines.append(f"HbA1c: {hba1c}")
    lines += [
        "",
        "=== CLINICAL CONTEXT ===",
        "",
        f"Comorbidities: {comorbidities_text}",
        f"Kidney Biopsy: {biopsy_text}",
        "",
        "=== CURRENT MEDICATIONS ===",
        "",
        f"{meds_text}",
        "",
        "=== EXISTING GDES MANAGEMENT PLAN ===",
        "",
        f"{plan_text}",
        "",
        "=== PRESCRIPTION REQUEST ===",
        "",
        "Please provide a structured prescription in the following format for EACH medication:",
        "",
        "Drug: [generic name]",
        "Dose: [exact dose with units]",
        "Frequency: [e.g. once daily, twice daily]",
        "Route: [PO/IV/SC]",
        "Duration: [e.g. 6 months, indefinite]",
        "Renal adjustment: [dose modification for current eGFR, or 'None required']",
        "Monitoring: [what to monitor and how often]",
        "Evidence: [guideline reference, e.g. KDIGO 2021, KDIGO 2024]",
        "Rationale: [brief clinical reasoning]",
        "",
        "---",
        "",
        "Also provide:",
        "1. Pre-treatment checks required",
        "2. Contraindications to consider",
        "3. Drug interactions to monitor",
        "4. Vaccination requirements before immunosuppression",
        "5. Patient counselling points",
    ]
    return "\n".join(lines)


@login_required(login_url=LOGIN)
def request_vera_prescription(request, pk):
    """Build a prescription-generation prompt for Vera Health.

    POST-only. Returns JSON {prompt} for the frontend to copy to clipboard
    and open Vera.
    """
    from django.http import JsonResponse
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    patient = get_object_or_404(Patient, pk=pk)
    from clinical_reasoning.models import ClinicalProfile
    from clinical_reasoning.services.management_plan import generate_management_plan

    try:
        profile = ClinicalProfile.objects.get(patient=patient)
    except ClinicalProfile.DoesNotExist:
        profile = None

    disease_id = ""
    management_plan = None
    if profile and profile.differential:
        disease_id = (profile.differential[0] or {}).get("disease_id", "")
        if disease_id:
            try:
                management_plan = generate_management_plan(patient, disease_id)
            except Exception:
                pass

    prompt = _build_prescription_prompt(patient, profile, management_plan)

    return JsonResponse({"prompt": prompt})


@login_required(login_url=LOGIN)
def vera_autopaste(request):
    """Send one guarded Ctrl+V to the browser window showing Vera (Windows only).

    Called right after the page copies the prompt and opens Vera. No patient
    data crosses this endpoint -- the case note is already on the clipboard;
    this only delivers a keystroke, and only once the foreground window is
    verifiably a browser showing Vera. See clinical_evidence.services
    .vera_autopaste for the guard rationale.
    """
    from django.http import JsonResponse
    from clinical_evidence.services import vera_autopaste as ap

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    return JsonResponse(ap.autopaste_into_vera())


@login_required(login_url=LOGIN)
def save_vera_response(request, pk):
    """Parse a pasted Vera Health response and save as KnowledgeBaseEntry records.

    POST with field 'vera_response' (the raw text from Vera).
    Creates one KnowledgeBaseEntry per extracted medication recommendation.
    """
    from django.http import JsonResponse
    from django.utils import timezone as tz

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    patient = get_object_or_404(Patient, pk=pk)
    raw = (request.POST.get("vera_response") or "").strip()
    if not raw:
        return JsonResponse({"error": "No response text provided."}, status=400)

    from clinical_reasoning.models import ClinicalProfile
    try:
        profile = ClinicalProfile.objects.get(patient=patient)
    except ClinicalProfile.DoesNotExist:
        profile = None

    disease_id = ""
    disease_name = "Unknown"
    if profile and profile.differential:
        top = profile.differential[0] or {}
        disease_id = top.get("disease_id", "")
        disease_name = top.get("disease_name", "Unknown")

    # --- Parse Vera's markdown into plan-shaped recommendations ---
    from clinical_reasoning.services import vera_ingest

    vera_plan = vera_ingest.parse_vera_response(raw)
    medications = vera_plan.medications

    if not medications:
        # Nothing confidently parseable: keep the response verbatim so the
        # clinician can still review it, rather than guessing at its content.
        medications = [{
            "drug": "Vera recommendation (unstructured)",
            "rationale": raw[:2000],
            "section": "first_line",
        }]

    from knowledge.models import KnowledgeBaseEntry, GuidelineSource

    # Ensure a "Vera Health" guideline source exists
    source, _ = GuidelineSource.objects.get_or_create(
        abbreviation="Vera",
        defaults={
            "title": "Vera Health AI Clinical Recommendations",
            "version_year": tz.now().year,
            "url": "https://verahealth.ai",
            "effective_date": tz.now().date(),
        },
    )

    stamp = tz.now().strftime("%Y%m%d%H%M")
    captured_at = tz.now().isoformat(timespec="seconds")

    entries_created = []
    for med in medications:
        entry_id = f"VERA-{patient.patient_id}-{stamp}-{len(entries_created)+1:02d}"
        rule_data = vera_ingest.medication_to_rule_data(
            med,
            disease_id=disease_id,
            disease_name=disease_name,
            patient_id=patient.patient_id,
            captured_at=captured_at,
        )
        # The narrative sections belong to the whole response, so they are
        # attached once, to the first entry, rather than duplicated per drug.
        if not entries_created:
            rule_data["response_context"] = {
                "contraindicated": vera_plan.contraindicated,
                "pre_treatment": vera_plan.pre_treatment,
                "vaccinations": vera_plan.vaccinations,
                "interactions": vera_plan.interactions,
                "monitoring": vera_plan.monitoring,
                "counselling": vera_plan.counselling,
            }
            rule_data["raw_response"] = raw[:8000]

        entry = KnowledgeBaseEntry.objects.create(
            entry_id=entry_id,
            disease_id=disease_id or "unspecified",
            rule_data=rule_data,
            source=source,
            evidence_grade="OP",  # Expert opinion (AI-generated)
            rule_type="treatment",
            status="draft",
            effective_date=tz.now().date(),
            tags=["vera_health", "ai_generated", patient.patient_id,
                  rule_data.get("plan_line", "first_line")],
            review_notes=(
                f"Auto-imported from Vera Health for {patient.patient_id} "
                f"({disease_name}). Draft: it does NOT affect management plans "
                f"until a clinician activates it in the Knowledge Base."
            ),
            author=request.user if request.user.is_authenticated else None,
        )
        entries_created.append(entry.entry_id)

    counts = vera_plan.counts()
    parsed = bool(vera_plan.medications)
    return JsonResponse({
        "ok": True,
        "entries_created": entries_created,
        "count": len(entries_created),
        "parsed": parsed,
        "counts": counts,
        "message": (
            f"Saved {len(entries_created)} structured recommendation(s) as draft "
            f"knowledge-base entries. Activate them in the Knowledge Base to let "
            f"them inform future management plans for {disease_name}."
            if parsed else
            "Could not identify medication blocks in that response — saved the "
            "full text as a single draft entry for manual review."
        ),
    })


# --- Prescriptions list -----------------------------------------------------

@login_required(login_url=LOGIN)
def prescriptions_list(request):
    rx = (Prescription.objects.select_related("encounter", "encounter__patient")
          .order_by("-created_at")[:100])
    return render(request, "clinic/prescriptions_list.html",
                  {"active": "prescriptions", "prescriptions": rx})


# --- Quality assessment & clinical insight (workflow steps 6-7) -------------

@login_required(login_url=LOGIN)
def quality_page(request):
    """Biopsy yield, predictors of a positive biopsy, phase/response/relapse
    snapshots, and the between-group comparison the clinic uses for insight."""
    from analytics.services import quality
    group_by = request.GET.get("group_by", "diagnosis")
    if group_by not in quality.GROUPERS:
        group_by = "diagnosis"
    ctx = {
        "active": "quality",
        "yield": quality.biopsy_yield(),
        "phases": quality.phase_distribution(),
        "relapse": quality.relapse_rate(),
        "concordance": quality.remission_concordance(),
        "comparison": quality.group_comparison(group_by),
        "group_by": group_by,
        "groupers": [(k, v[0]) for k, v in quality.GROUPERS.items()],
    }
    return render(request, "clinic/quality.html", ctx)


# --- Analytics & Export landing pages --------------------------------------

def _drug_group_options():
    """"drug:<class>" options for the exposure -> outcome comparison.

    Only classes a patient is actually exposed to are offered: an option that
    splits the cohort into "everyone" vs "nobody" produces an empty comparison
    and looks like a broken page.
    """
    try:
        from treatments.models import TreatmentExposure
        classes = (TreatmentExposure.objects
                   .exclude(drug__drug_class="")
                   .values_list("drug__drug_class", flat=True)
                   .distinct())
        return [f"drug:{c}" for c in sorted(set(classes)) if c]
    except Exception:  # pragma: no cover - DB not ready
        return []


@login_required(login_url=LOGIN)
def analytics_page(request):
    """Cohort analytics rendered as tables (not raw JSON). Each computation is
    guarded so sparse data shows a friendly note instead of erroring the page."""
    group_by = request.GET.get("group_by", "diagnosis")
    endpoint = request.GET.get("endpoint", "composite_kidney_event")
    ctx = {
        "active": "analytics", "group_by": group_by, "endpoint": endpoint,
        # Exposure -> outcome: cohort.split_patients has always supported
        # "drug:<class>" (ever-exposed vs never-exposed), but the option was
        # never offered here, so the analysis was unreachable from the app.
        "group_options": ["diabetes", "diagnosis", "cohort"] + _drug_group_options(),
        "endpoint_options": [
            "composite_kidney_event", "eskd", "death",
            "sustained_40_decline", "sustained_50_decline",
            "complete_remission", "partial_remission", "any_remission",
            "igan_proteinuria_response",
        ],
    }
    qs = Patient.objects.all()

    # Per-group baseline/outcome counts — generic table (column-agnostic).
    try:
        from analytics.services.cohort import cohort_summary
        rows = cohort_summary(qs, group_by) or []
        cols = list(rows[0].keys()) if rows else []
        ctx["summary_cols"] = [c.replace("_", " ") for c in cols]
        ctx["summary_rows"] = [[r.get(c) for c in cols] for r in rows]
    except Exception as exc:
        ctx["summary_error"] = str(exc)

    # Kaplan–Meier group summary + log-rank.
    try:
        from analytics.services.cohort import cohort_survival
        cohort = cohort_survival(qs, group_by, endpoint)
        ctx["surv_groups"] = cohort.groups
        ctx["surv_logrank"] = cohort.logrank
    except Exception as exc:
        ctx["surv_error"] = str(exc)

    return render(request, "clinic/analytics.html", ctx)


@login_required(login_url=LOGIN)
def export_page(request):
    from studies.models import Study
    studies = (Study.objects.exclude(status=Study.Status.CLOSED)
               .order_by("code").values_list("code", "title"))
    return render(request, "clinic/export.html",
                  {"active": "export", "studies": list(studies)})


# --- Follow-up worklist (scheduling, as a real page) ------------------------

@login_required(login_url=LOGIN)
def worklist_page(request):
    """Coordinator worklist: overdue + due follow-up visits and today's clinic
    roster — the scheduling engine's output rendered as a page instead of JSON.
    Every query is defensive so a sparse DB never 500s the page."""
    import datetime as _dt
    from scheduling.services.schedule import due_visits, overdue_visits, clinic_roster

    as_of = request.GET.get("as_of")
    try:
        today = _dt.date.fromisoformat(as_of) if as_of else _dt.date.today()
    except ValueError:
        today = _dt.date.today()

    def _safe(fn, default):
        try:
            return fn()
        except Exception:
            return default

    due = _safe(lambda: list(due_visits(today)), [])
    overdue = _safe(lambda: list(overdue_visits(today)), [])
    roster = _safe(lambda: clinic_roster(today), None)
    return render(request, "clinic/worklist.html", {
        "active": "worklist", "today": today,
        "due": due, "overdue": overdue, "roster": roster,
    })


# --- Studies / Safety / Pathology / Biomarkers (engine outputs as pages) -----

def _safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


@login_required(login_url=LOGIN)
def studies_page(request):
    from studies.models import Study
    from studies.services.randomization import study_dashboard
    studies = list(Study.objects.all())
    code = request.GET.get("code") or (studies[0].code if studies else None)
    dash, err = None, None
    if code:
        st = Study.objects.filter(code=code).first()
        if st:
            try:
                dash = study_dashboard(st)
            except Exception as exc:
                err = str(exc)
    return render(request, "clinic/studies.html", {
        "active": "studies", "studies": studies, "code": code,
        "dash": dash, "dash_error": err,
    })


@login_required(login_url=LOGIN)
def drug_intelligence_page(request):
    """Drug Intelligence — browsable disease-independent clinical drug knowledge."""
    from knowledge.models import DrugIntelligence

    q = (request.GET.get("q") or "").strip()
    drugs = DrugIntelligence.objects.filter(is_active=True)
    if q:
        drugs = drugs.filter(Q(name__icontains=q) | Q(drug_class__icontains=q))
    return render(request, "clinic/drug_intelligence.html", {
        "active": "drugs",
        "drugs": drugs.order_by("name"),
        "q": q,
        "total": DrugIntelligence.objects.filter(is_active=True).count(),
    })


@login_required(login_url=LOGIN)
def drug_intelligence_detail(request, drug_id):
    """Full drug monograph."""
    from knowledge.models import DrugIntelligence

    drug = get_object_or_404(DrugIntelligence, pk=drug_id, is_active=True)
    return render(request, "clinic/drug_intelligence_detail.html", {
        "active": "drugs", "drug": drug,
    })


@login_required(login_url=LOGIN)
def recommendation_feedback(request, pk):
    """V8 Layer 10 — capture a nephrologist's Accept/Modify/Reject on a CDS
    recommendation as structured learning data. NEVER auto-applied to the
    production knowledge base (governance: expert review required)."""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        from feedback.models import WorkflowFeedback

        action = request.POST.get("action", "")
        area = request.POST.get("area", "clinical_reasoning")
        valid_areas = dict(WorkflowFeedback.FEEDBACK_TYPES)
        if action in ("accept", "modify", "reject"):
            WorkflowFeedback.objects.create(
                user=request.user if request.user.is_authenticated else None,
                patient=patient,
                feedback_type=area if area in valid_areas else "clinical_reasoning",
                action=action,
                recommendation_ref=(request.POST.get("ref") or "")[:120],
                rating={"accept": 5, "modify": 3, "reject": 1}.get(action, 0),
                comments=(request.POST.get("comments") or "").strip(),
            )
            messages.success(
                request,
                f"Recommendation {action}ed — thank you. Your feedback becomes "
                "structured learning data (applied only after expert review).")
        else:
            messages.error(request, "Please choose Accept, Modify, or Reject.")
    return redirect("clinic:patient_detail", pk=patient.pk)


@login_required(login_url=LOGIN)
def safety_page(request):
    group_by = request.GET.get("group_by", "diabetes")
    ctx = {"active": "safety", "group_by": group_by,
           "group_options": ["diabetes", "diagnosis", "cohort"]}
    qs = Patient.objects.all()
    try:
        from safety.services.summary import safety_summary
        ctx["summary"] = safety_summary(qs)
    except Exception as exc:
        ctx["summary_error"] = str(exc)
    try:
        from safety.services.summary import infection_incidence
        inc = infection_incidence(qs, group_by) or {}
        rows = inc.get("rows", []) if isinstance(inc, dict) else []
        cols = list(rows[0].keys()) if rows else []
        ctx["inc_cols"] = [c.replace("_", " ") for c in cols]
        ctx["inc_rows"] = [[r.get(c) for c in cols] for r in rows]
    except Exception as exc:
        ctx["inc_error"] = str(exc)
    return render(request, "clinic/safety.html", ctx)


@login_required(login_url=LOGIN)
def pathology_page(request):
    ctx = {"active": "pathology"}
    try:
        from pathology.services.agreement import interobserver_agreement
        ctx["agree"] = interobserver_agreement()
    except Exception as exc:
        ctx["agree_error"] = str(exc)
    try:
        from pathology.models import Biopsy
        from pathology.services.review import concordance
        disc = Biopsy.objects.filter(
            review_status=Biopsy.ReviewStatus.DISCORDANT).select_related("patient")
        ctx["discordant"] = [
            {"pk": b.pk, "patient": b.patient.patient_id,
             "fields": (concordance(b) or {}).get("discordant_fields", [])}
            for b in disc]
        from django.db.models import Count
        ctx["status_counts"] = list(
            Biopsy.objects.values("review_status").annotate(n=Count("id")).order_by())
    except Exception as exc:
        ctx["disc_error"] = str(exc)
    return render(request, "clinic/pathology.html", ctx)


@login_required(login_url=LOGIN)
def biomarkers_page(request):
    try:
        within = int(request.GET.get("within_days", 90))
    except ValueError:
        within = 90
    ctx = {"active": "biomarkers", "within_days": within}
    try:
        from biomarkers.services.predictor import pla2r_remission_predictor
        ctx["pred"] = pla2r_remission_predictor(Patient.objects.all(), within_days=within)
    except Exception as exc:
        ctx["pred_error"] = str(exc)
    return render(request, "clinic/biomarkers.html", ctx)


# --- Lab ordering (guided) --------------------------------------------------

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
                # A single bad value must not lose the rest of the panel.
                continue
        if saved:
            messages.success(
                request, f"Recorded {saved} result(s) dated {result_date}."
                + (" eGFR updated." if any(c == "creatinine" for c, *_ in rows) else ""))
            return redirect("clinic:patient_detail", pk=patient.pk)
        messages.error(request, "Enter at least one result value.")
    return render(request, "clinic/lab_results_form.html",
                  {"active": "patients", "form": form, "patient": patient})


# --- Advanced analytics results (HTML wrappers for JSON endpoints) ----------

@login_required(login_url=LOGIN)
def cox_results(request):
    """Multivariable Cox PH rendered as a table instead of raw JSON."""
    endpoint = request.GET.get("endpoint", "composite_kidney_event")
    raw = request.GET.get("covariates", "age,diabetes,baseline_egfr")
    covariates = [c.strip() for c in raw.split(",") if c.strip()]
    ctx = {
        "active": "analytics", "endpoint": endpoint, "covariates": raw,
        "endpoint_options": [
            "composite_kidney_event", "eskd", "death",
            "sustained_40_decline", "sustained_50_decline",
            "complete_remission", "partial_remission", "any_remission",
            "igan_proteinuria_response",
        ],
    }
    try:
        from analytics.services.cohort import cox_regression
        result, meta = cox_regression(Patient.objects.all(), covariates, endpoint)
        # Merge meta into result for easy template access
        ctx["result"] = {**result, **meta}
    except ValueError as exc:
        ctx["error"] = str(exc)
    except Exception as exc:
        ctx["error"] = f"Could not compute: {exc}"
    return render(request, "clinic/cox_results.html", ctx)


@login_required(login_url=LOGIN)
def egfr_slope_results(request):
    """Linear mixed-effects eGFR slope per group, rendered as a table."""
    group_by = request.GET.get("group_by", "diabetes")
    ctx = {"active": "analytics", "group_by": group_by,
           "group_options": ["diabetes", "diagnosis", "cohort"]}
    try:
        from analytics.services.cohort import cohort_egfr_slope
        data = cohort_egfr_slope(Patient.objects.all(), group_by)
        # Reshape flat dict into rows list for the template
        if data and "groups" in data:
            rows = []
            for g in data["groups"]:
                rows.append({
                    "label": g,
                    "slope": data.get(f"slope_{g}"),
                    "n_patients": data.get("n_patients"),
                })
            ctx["data"] = {
                "rows": rows,
                "slope_difference": data.get("slope_difference"),
                "difference_se": data.get("difference_se"),
                "p_value": data.get("p_value"),
                "converged": data.get("converged"),
            }
        elif data and "error" in data:
            ctx["error"] = data["error"]
        else:
            ctx["data"] = data
    except Exception as exc:
        ctx["error"] = str(exc)
    return render(request, "clinic/egfr_slope_results.html", ctx)


@login_required(login_url=LOGIN)
def cif_results(request):
    """Competing-risks CIF at a specified timepoint, rendered as a table."""
    group_by = request.GET.get("group_by", "diabetes")
    try:
        at_days = int(request.GET.get("at_days", 365))
    except ValueError:
        at_days = 365
    ctx = {"active": "analytics", "group_by": group_by, "at_days": at_days,
           "group_options": ["diabetes", "diagnosis", "cohort"]}
    try:
        from analytics.services.cohort import cohort_competing_risks
        data = cohort_competing_risks(Patient.objects.all(), group_by, at_days=at_days)
        # Build rows list with dynamic CIF key
        cif_key = f"cif_at_{at_days}d"
        rows = []
        for g in data.get("groups", []):
            rows.append({
                "label": g.get("label"),
                "n": g.get("n"),
                "n_kidney_events": g.get("n_kidney_events"),
                "n_competing_deaths": g.get("n_competing_deaths"),
                "cif": g.get(cif_key),
                "final_cif": g.get("final_cif"),
            })
        ctx["data"] = {
            "rows": rows,
            "comparison": data.get("comparison"),
        }
    except Exception as exc:
        ctx["error"] = str(exc)
    return render(request, "clinic/cif_results.html", ctx)


# --- Help / documentation ---------------------------------------------------
# Three in-app guides. The user guide is open to any signed-in user; the admin
# guide is gated to staff; the developer guide to the superuser (the maintainer).
@login_required
def help_index(request):
    return render(request, "help/index.html", {"active": "help"})


@login_required
def help_user(request):
    return render(request, "help/user.html", {"active": "help"})


@login_required
def help_admin(request):
    if not request.user.is_staff:
        messages.error(request, "The administrator guide is available to staff accounts only.")
        return redirect("clinic:help")
    return render(request, "help/admin.html", {"active": "help"})


@login_required
def help_developer(request):
    if not request.user.is_superuser:
        messages.error(request, "The developer guide is available to the maintainer (superuser) only.")
        return redirect("clinic:help")
    return render(request, "help/developer.html", {"active": "help"})
