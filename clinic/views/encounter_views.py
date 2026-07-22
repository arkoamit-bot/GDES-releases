"""Encounter-related views: baseline, follow-up, registration, relapse, admission."""
from __future__ import annotations

import datetime as _dt

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ._common import (LOGIN, Patient, _save_labs, login_required)
from ..forms import (AdmissionForm, BaselineForm, FollowupForm, RelapseForm,
                    RegisterForm)


# --- Baseline ---------------------------------------------------------------

@login_required(login_url=LOGIN)
def baseline_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    instance = getattr(patient, "baseline", None)
    form = BaselineForm(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.patient = patient
        obj.save()
        n = _save_labs(patient, form, obj.assessment_date or _dt.date.today())
        messages.success(request, "Baseline assessment saved."
                         + (f" {n} baseline lab result(s) recorded." if n else ""))
        return redirect("clinic:patient_detail", pk=patient.pk)
    return render(request, "clinic/baseline_form.html",
                  {"active": "patients", "form": form, "patient": patient})


# --- Follow-up visit --------------------------------------------------------

def _sync_level2_from_followup(patient, form):
    """Sync Level 2 persistent fields from follow-up form back to Patient."""
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

    # Continuity: surface the previous visit + latest key labs
    prev = patient.encounters.order_by("-encounter_date", "-id").first()
    def _last(code):
        r = (patient.lab_results.filter(test__code=code, value_numeric__isnull=False)
             .order_by("-result_date").first())
        return r.value_numeric if r else None
    last_labs = [("eGFR", _last("egfr")), ("Creatinine", _last("creatinine")),
                 ("24h UTP", _last("utp_24h")), ("UPCR", _last("upcr")),
                 ("Albumin", _last("albumin")), ("K\u207a", _last("potassium"))]
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

    # Level 2 persistent clinical data from Patient
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
    """Register a suspected patient into structured GN follow-up (step 4)."""
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
