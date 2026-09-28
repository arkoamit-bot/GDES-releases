"""Clinical workflow views: adverse events, biopsy entry, study enrollment,
consent management, treatment exposure.
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    AdverseEventForm,
    BiopsyForm,
    ConsentForm,
    FSGSPathologyForm,
    GNDiagnosisForm,
    IgANScoreForm,
    LOGIN,
    LupusPathologyForm,
    MembranousPathologyForm,
    Patient,
    StudyEnrollmentForm,
    TreatmentExposureForm,
    get_object_or_404,
    login_required,
    messages,
    redirect,
    render,
)


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


def _reconcile_fsgs(dx_form, fsgs_form, fsgs_active):
    """Primary/secondary and variant are stated by some FSGS diagnoses and
    asked again on the diagnosis and the FSGS panel. Prefill blanks from the
    diagnosis; report contradictions instead of saving them."""
    from pathology import diagnosis as dxrules

    if not dx_form.is_valid():
        return True
    diagnosis = dx_form.cleaned_data.get("diagnosis") or ""
    if dxrules.family(diagnosis) != dxrules.FSGS and not fsgs_active:
        return True
    dx_ps = dx_form.cleaned_data.get("primary_secondary") or ""
    panel_ps = panel_variant = ""
    if fsgs_active and fsgs_form.is_valid():
        panel_ps = fsgs_form.cleaned_data.get("primary_secondary") or ""
        panel_variant = fsgs_form.cleaned_data.get("variant") or ""
    ps, variant, errors = dxrules.reconcile_fsgs(diagnosis, dx_ps, panel_ps, panel_variant)
    for (form_key, field), msg in errors.items():
        (dx_form if form_key == "dx" else fsgs_form).add_error(field, msg)
    if errors:
        return False
    if ps and not dx_ps:
        dx_form.cleaned_data["primary_secondary"] = ps
        dx_form.instance.primary_secondary = ps
    if fsgs_active and fsgs_form.is_valid():
        if ps and not panel_ps:
            fsgs_form.instance.primary_secondary = ps
        if variant and not panel_variant:
            fsgs_form.instance.variant = variant
    return True


def _attach_report_errors(errors, report_form, formset, index, fallback_form):
    """Map pathology.services.report errors back onto the forms."""
    for key, messages_ in errors.items():
        for msg in messages_:
            if key.startswith("finding-"):
                pos = int(key.split("-", 1)[1])
                target = formset.forms[index[pos]] if pos < len(index) else None
                (target or report_form).add_error(None, msg)
            elif key in report_form.fields:
                report_form.add_error(key, msg)
            elif key in getattr(fallback_form, "fields", {}):
                fallback_form.add_error(key, msg)
            else:
                report_form.add_error(None, msg)


def _biopsy_summary_flags(bx_form):
    from pathology import findings as vocab
    return {f: bx_form.cleaned_data.get(f) for f in vocab.SUMMARY_LINKS}


@login_required(login_url=LOGIN)
def biopsy_create(request, pk):
    """Guided biopsy entry: the core biopsy + its diagnosis (the driver of the
    disease-specific remission rules) + optional MEST-C / ISN-RPS / FSGS / MN
    score blocks + the local pathology report with any number of structured
    findings. A score block is only saved when the user actually fills it.
    New biopsies enter the central-review workflow as 'pending'."""
    from django.db import transaction

    from pathology import diagnosis as dxrules
    from pathology.models import PathologyReport
    from pathology.services.projection import deferred_projection
    from pathology.services.report import save_report, validate_report

    from ..forms import FindingFormSet, PathologyReportForm, findings_from_formset

    patient = get_object_or_404(Patient, pk=pk)
    post = request.POST or None
    bx = BiopsyForm(post, prefix="bx")
    dx = GNDiagnosisForm(post, prefix="dx")
    rp = PathologyReportForm(post, prefix="rp")
    # A submission without the findings block (older page, script) simply
    # has no findings -- not a broken management form.
    fs = FindingFormSet(post if post and "f-TOTAL_FORMS" in post else None, prefix="f")
    scores = {
        "igan": IgANScoreForm(post, prefix="igan"),
        "lupus": LupusPathologyForm(post, prefix="lupus"),
        "fsgs": FSGSPathologyForm(post, prefix="fsgs"),
        "mn": MembranousPathologyForm(post, prefix="mn"),
    }
    warnings = []

    if request.method == "POST":
        # Validate the required pair; validate a score block only if touched.
        ok = bx.is_valid()
        ok = dx.is_valid() and ok
        ok = rp.is_valid() and ok
        ok = (fs.is_valid() if fs.is_bound else True) and ok
        active = {k: f for k, f in scores.items() if f.has_changed()}
        for f in active.values():
            ok = f.is_valid() and ok

        diagnosis = dx.cleaned_data.get("diagnosis", "") if dx.is_valid() else ""
        status = rp.cleaned_data.get("status") if rp.is_valid() else ""
        if (dx.is_valid() and not diagnosis and status in (
                PathologyReport.Status.FINAL, PathologyReport.Status.PRELIMINARY)):
            dx.add_error("diagnosis", "A final or preliminary report needs a diagnosis. "
                         "Record it as draft, pending or inadequate if there is none yet.")
            ok = False

        # The ISN/RPS class is stated once: the diagnosis and the lupus panel
        # must agree, and a contradiction is reported rather than resolved.
        ok = _reconcile_lupus_class(dx, scores["lupus"]) and ok
        ok = _reconcile_fsgs(dx, scores["fsgs"], "fsgs" in active) and ok
        if dx.is_valid():
            diagnosis = dx.cleaned_data.get("diagnosis") or ""

        # A score panel outside the diagnosis family is not silently attached.
        if rp.is_valid():
            panel_errors = dxrules.check_panels(
                diagnosis, active.keys(),
                additional=rp.cleaned_data.get("additional_diagnoses") or [],
                override_reason=rp.cleaned_data.get("panel_override_reason", ""))
            for key, msg in panel_errors.items():
                active[key].add_error(None, msg)
                ok = False

        findings, index = (findings_from_formset(fs) if fs.is_bound and fs.is_valid()
                           else ([], []))
        derived = {}
        if ok:
            data = rp.report_data()
            data["primary_diagnosis"] = diagnosis
            errors, warnings, derived = validate_report(
                data, findings, total_glomeruli=bx.cleaned_data.get("total_glomeruli"),
                summary=_biopsy_summary_flags(bx),
                reported_pct={"global_sclerosis_pct": bx.cleaned_data.get("global_sclerosis_pct"),
                              "crescent_pct": bx.cleaned_data.get("crescent_pct")})
            if errors:
                _attach_report_errors(errors, rp, fs, index, bx)
                ok = False

        if ok:
            with transaction.atomic(), deferred_projection():
                biopsy = bx.save(commit=False)
                biopsy.patient = patient
                for flag, value in derived.items():
                    setattr(biopsy, flag, value)
                biopsy.save()
                dxo = None
                if diagnosis:
                    dxo = dx.save(commit=False)
                    dxo.biopsy = biopsy
                    dxo.save()
                for f in active.values():
                    obj = f.save(commit=False)
                    obj.biopsy = biopsy
                    obj.save()
                save_report(biopsy, data=data, findings=findings,
                            user=request.user if request.user.is_authenticated else None)
            patient.refresh_from_db()
            extra = f" + {len(active)} score block(s)" if active else ""
            if findings:
                extra += f" + {len(findings)} finding(s)"
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
            label = dxo.get_diagnosis_display() if dxo else rp.cleaned_data["status"]
            messages.success(
                request, f"Biopsy recorded ({label}){extra}. "
                f"It enters central review as 'pending'.{gate}")
            for w in warnings:
                messages.warning(request, w)
            return redirect("clinic:biopsy_detail", pk=patient.pk, bid=biopsy.pk)

    return render(request, "clinic/biopsy_form.html", {
        "active": "patients", "patient": patient,
        "bx": bx, "dx": dx, "rp": rp, "fs": fs, "scores": scores,
        "score_hints": _SCORE_HINTS, "sections": _finding_sections(),
        "mode": "create",
    })


def _finding_sections():
    from pathology import findings as vocab
    return [{"key": key, "label": label,
             "codes": [c for c, _ in codes]}
            for key, (label, codes) in vocab.SECTIONS.items()]


@login_required(login_url=LOGIN)
def biopsy_detail(request, pk, bid):
    """The full clinical report view for one biopsy: every report revision
    with its findings, the current score panels, the independent review
    reads and their disagreements, and whether this biopsy is the source of
    the patient's pathology summary."""
    from pathology.models import Biopsy
    from pathology.services.projection import select_source
    from pathology.services.review import concordance

    patient = get_object_or_404(Patient, pk=pk)
    biopsy = get_object_or_404(
        Biopsy.objects.select_related("diagnosis"), pk=bid, patient=patient)
    reports = list(biopsy.reports.prefetch_related("findings")
                   .order_by("role", "-revision"))
    current = [r for r in reports if r.is_current]
    history = [r for r in reports if not r.is_current]
    sel = select_source(patient)

    def rel(name):
        try:
            return getattr(biopsy, name)
        except Exception:
            return None

    return render(request, "clinic/biopsy_detail.html", {
        "active": "patients", "patient": patient, "biopsy": biopsy,
        "current_reports": current, "history": history,
        "igan": rel("igan_score"), "lupus": rel("lupus"), "fsgs": rel("fsgs"),
        "mn": rel("membranous"),
        "reviews": list(biopsy.reviews.select_related("reviewer").all()),
        "concordance": concordance(biopsy),
        "images": list(biopsy.images.all()),
        "is_source": sel.biopsy is not None and sel.biopsy.pk == biopsy.pk,
        "source_state": sel.state,
        "is_pending_newer": any(b.pk == biopsy.pk for b in sel.pending_biopsies),
        "source_biopsy": sel.biopsy,
        "legacy_if": biopsy.get_if_pattern_display() if biopsy.if_pattern else "",
        "legacy_em": biopsy.get_em_findings_display() if biopsy.em_findings else "",
    })


@login_required(login_url=LOGIN)
def biopsy_amend(request, pk, bid):
    """Amend (replace) or add an addendum to the current local report. The
    previous revision is kept, unchanged; the new one records who, when and
    why. A repeat biopsy is a new biopsy, not an amendment."""
    from django.db import transaction

    from pathology.models import Biopsy, GNDiagnosis
    from pathology.services.projection import FINAL_STATUSES, deferred_projection
    from pathology.services.report import (ReportInvalid, amend_report,
                                           current_report, legacy_report_from_biopsy,
                                           save_report)

    from ..forms import (FindingFormSet, PathologyReportForm, findings_from_formset,
                        findings_initial)

    patient = get_object_or_404(Patient, pk=pk)
    biopsy = get_object_or_404(Biopsy, pk=bid, patient=patient)
    kind = request.POST.get("kind") or request.GET.get("kind") or "amendment"
    if kind not in ("amendment", "addendum"):
        kind = "amendment"
    report = current_report(biopsy) or legacy_report_from_biopsy(biopsy)

    initial_dx = biopsy.diagnosis.diagnosis if hasattr(biopsy, "diagnosis") else ""
    post = request.POST or None
    bx = BiopsyForm(post, prefix="bx", instance=biopsy)
    rp = PathologyReportForm(post, prefix="rp", instance=None,
                             initial=({} if kind == "addendum" or report is None else
                                      {f: getattr(report, f) for f in PathologyReportForm.Meta.fields}))
    fs = FindingFormSet(post, prefix="f",
                        initial=([] if kind == "addendum" or report is None
                                 else findings_initial(report)))
    from django import forms as djforms
    from patients import choices as pchoices
    conclusion = djforms.ChoiceField(
        required=False, choices=[("", "— unchanged / none —")] + list(pchoices.SPECIFIC_GN_DIAGNOSIS),
        initial=(report.primary_diagnosis if report else initial_dx))
    reason = (request.POST.get("revision_reason") or "").strip()

    if request.method == "POST":
        ok = bx.is_valid() and rp.is_valid() and fs.is_valid()
        new_dx = (request.POST.get("primary_diagnosis") or "").strip()
        if not reason:
            messages.error(request, "State why the report is being amended.")
            ok = False
        if ok:
            findings, index = findings_from_formset(fs)
            data = rp.report_data()
            data["primary_diagnosis"] = new_dx or (report.primary_diagnosis if report else "")
            user = request.user if request.user.is_authenticated else None
            try:
                with transaction.atomic(), deferred_projection():
                    from audit.local import acting_as
                    with acting_as(user, reason=f"Pathology report {kind}: {reason}"[:240]):
                        bx.save()
                    if report is None:
                        new, warnings = save_report(biopsy, data=data, findings=findings,
                                                    user=user)
                    else:
                        new, warnings = amend_report(report, data=data, findings=findings,
                                                     reason=reason, user=user, kind=kind)
                    # The amended conclusion becomes the biopsy's adopted
                    # diagnosis only while no reviewed read is final.
                    if new_dx and biopsy.review_status not in FINAL_STATUSES:
                        with acting_as(user, reason=f"Pathology report {kind}: {reason}"[:240]):
                            GNDiagnosis.objects.update_or_create(
                                biopsy=biopsy, defaults={"diagnosis": new_dx})
                    elif new_dx and new_dx != initial_dx:
                        warnings.append(
                            "This biopsy has a finalized review, so the adopted diagnosis "
                            "is unchanged. The amended conclusion is on the report; submit "
                            "a review read to change the adopted diagnosis.")
            except ReportInvalid as exc:
                _attach_report_errors(exc.errors, rp, fs, index, bx)
            else:
                messages.success(request, f"Report {kind} recorded (revision {new.revision}).")
                for w in warnings:
                    messages.warning(request, w)
                return redirect("clinic:biopsy_detail", pk=patient.pk, bid=biopsy.pk)

    return render(request, "clinic/biopsy_form.html", {
        "active": "patients", "patient": patient, "biopsy": biopsy,
        "bx": bx, "rp": rp, "fs": fs, "scores": {}, "dx": None,
        "score_hints": _SCORE_HINTS, "sections": _finding_sections(),
        "mode": kind, "report": report, "reason": reason,
        "conclusion_choices": conclusion.choices,
        "conclusion_value": request.POST.get("primary_diagnosis",
                                             report.primary_diagnosis if report else initial_dx),
    })


@login_required(login_url=LOGIN)
def adopt_pathology_diagnosis(request, pk):
    """Explicitly adopt the selected biopsy's diagnosis as the working
    diagnosis (POST only, audited)."""
    from pathology.services.projection import adopt_pathology_diagnosis as adopt
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        try:
            new = adopt(patient, user=request.user,
                        reason=(request.POST.get("reason") or "").strip())
            messages.success(request, f"Working diagnosis set to {new}.")
        except ValueError as exc:
            messages.error(request, str(exc))
    return redirect("clinic:patient_detail", pk=patient.pk)


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
