"""Knowledge / intelligence views: drug intelligence, studies dashboard,
recommendation feedback, safety, pathology, biomarkers.
"""
from __future__ import annotations

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ._common import LOGIN, Patient, _safe_call, login_required


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
    """V8 Layer 10 — capture a nephrologist's Accept/Modify/Reject."""
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
