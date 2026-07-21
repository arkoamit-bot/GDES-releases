"""Clinical workflow views: adverse events, biopsy entry, study enrollment,
consent management, treatment exposure.
"""
from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ._common import LOGIN, Patient, login_required
from .forms import (AdverseEventForm, BiopsyForm, ConsentForm, FSGSPathologyForm,
                    GNDiagnosisForm, IgANScoreForm, LupusPathologyForm,
                    MembranousPathologyForm, StudyEnrollmentForm,
                    TreatmentExposureForm)


# --- Adverse event (guided report) ------------------------------------------

@login_required(login_url=LOGIN)
def adverse_event_create(request, pk):
    """Guided adverse-event report for a patient."""
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

_SCORE_HINTS = {
    "igan": ("iga",),
    "lupus": ("lupus", "ln"),
    "fsgs": ("fsgs",),
    "mn": ("membranous", "mn"),
}


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
    # ISN/RPS class
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
    """Guided biopsy entry: core biopsy + diagnosis + optional score blocks."""
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
        ok = bx.is_valid()
        ok = dx.is_valid() and ok
        active = {k: f for k, f in scores.items() if f.has_changed()}
        for f in active.values():
            ok = f.is_valid() and ok
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
            _sync_biopsy_to_patient(patient, dxo, active)
            extra = f" + {len(active)} score block(s)" if active else ""
            # --- Confirm-GN gate
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
    """Screen + enrol a patient into a study."""
    from studies.models import StudyEnrollment
    from studies.services.randomization import (AlreadyEnrolled, ConsentRequired, enroll)
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
        except Exception as exc:
            messages.error(request, f"Could not enrol: {exc}")
            return redirect("clinic:study_enroll", pk=patient.pk)

        if enr.status == StudyEnrollment.Status.INELIGIBLE:
            reasons = ", ".join(enr.ineligibility_reasons) or "no reason recorded"
            messages.warning(request, f"Screened ineligible for {study.code}: {reasons}.")
        elif enr.status == StudyEnrollment.Status.ENROLLED:
            arm = f' \u2192 arm "{enr.arm.name}"' if enr.arm else ""
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
    """Record or withdraw versioned patient consent."""
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


# --- Treatment exposure (for prior/external meds) ---------------------------

@login_required(login_url=LOGIN)
def treatment_add(request, pk):
    """Record a medication episode directly."""
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
