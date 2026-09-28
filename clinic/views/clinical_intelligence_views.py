"""Clinical intelligence and Vera Health views: run the reasoning engine,
verify a treatment plan or request a prescription from Vera, auto-paste the
case note, and save Vera's structured response.
"""
from __future__ import annotations

from ._common import (  # noqa: F401
    LOGIN,
    Patient,
    get_object_or_404,
    login_required,
    messages,
    redirect,
    render,
)


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
            from django.utils import timezone
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
    # The biopsy the patient's pathology summary is projected from (final
    # review preferred), not simply the newest row.
    from pathology.services.projection import select_source
    _sel = select_source(patient)
    biopsy = _sel.biopsy or (patient.biopsies.order_by("-biopsy_date").first()
                             if hasattr(patient, "biopsies") else None)
    if biopsy:
        try:
            dx = biopsy.diagnosis.diagnosis
        except Exception:
            dx = ""
        crescents = {True: "Crescents present", False: "Crescents absent"}.get(
            biopsy.crescents_present, "Crescents not assessed")
        state = {"final": "", "provisional": " (provisional, review pending)"}.get(_sel.state, "")
        biopsy_text = f"{dx or 'Biopsy done'}{state}; {crescents}"

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
