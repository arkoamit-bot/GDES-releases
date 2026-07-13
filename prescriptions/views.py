"""
Thin views to drive and inspect the workflow end-to-end:

    /prescriptions/<id>/preview/             -> rendered HTML prescription
    /prescriptions/<id>/reconcile/preview/   -> JSON diff (writes nothing)
    /prescriptions/<id>/finalize/            -> POST: freeze + reconcile
    /prescriptions/<id>/pdf/                 -> PDF download (WeasyPrint)
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST


def _wants_json(request):
    """True for API / HTMX / fetch callers; False for a plain browser form POST."""
    return bool(
        request.headers.get("HX-Request")
        or request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("Accept", ""))

from .models import Prescription
from .pdf import PDFEngineUnavailable, render_prescription_html, render_prescription_html_download, render_prescription_pdf, save_prescription_pdf
from .services.finalize import FinalizeBlocked, finalize_prescription
from .services.reconciliation import plan_reconciliation
from .services.safety import check_prescription


@login_required
def preview(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    # Render the full preview page with action buttons (not just raw print HTML)
    return render(request, "prescriptions/preview_wrapper.html", {
        "rx": rx, "patient": rx.patient,
        "prescription_html": render_prescription_html(rx),
    })


@login_required
def html_download(request, pk):
    """Serve the prescription as an HTML file the user can open and print.
    Works on any system — no PDF engine needed."""
    rx = get_object_or_404(Prescription, pk=pk)
    html = render_prescription_html_download(rx)
    resp = HttpResponse(html, content_type="text/html; charset=utf-8")
    resp["Content-Disposition"] = (
        f'attachment; filename="rx_{rx.patient.patient_id}_v{rx.version}.html"')
    return resp


@login_required
def reconcile_preview(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    plan = plan_reconciliation(rx)
    return JsonResponse({
        "prescription": rx.id,
        "as_of": str(plan.as_of),
        "summary": plan.summary(),
        "actions": [vars(a) for a in plan.actions],
        "needs_stop_reason": plan.drugs_being_stopped,
        "safety": [vars(w) for w in check_prescription(rx)],
    }, json_dumps_params={"indent": 2})


@login_required
@require_POST
def finalize(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    try:
        warnings = finalize_prescription(
            rx, user=request.user if request.user.is_authenticated else None,
            override_blocks=request.POST.get("override") == "1")
    except FinalizeBlocked as exc:
        if _wants_json(request):
            return JsonResponse(
                {"status": "blocked", "warnings": [vars(w) for w in exc.warnings]},
                status=409)
        messages.error(request, "Cannot finalize — safety check blocked it: "
                       + "; ".join(w.message for w in exc.warnings))
        return redirect("prescriptions:preview", pk=rx.pk)

    if _wants_json(request):
        return JsonResponse({
            "status": "finalized", "version": rx.version,
            "content_hash": rx.content_hash,
            "reconciled_at": str(rx.reconciled_at),
            "warnings": [vars(w) for w in warnings],
        })
    # Browser form post → land back on the (now finalized) preview page.
    if warnings:
        messages.warning(request, "Finalized with safety notes: "
                         + "; ".join(w.message for w in warnings))
    else:
        messages.success(request, f"Prescription finalized (v{rx.version}). "
                         "The PDF is ready to print.")
    return redirect("prescriptions:preview", pk=rx.pk)


@login_required
def pdf(request, pk):
    rx = get_object_or_404(Prescription, pk=pk)
    try:
        data = render_prescription_pdf(rx)
    except PDFEngineUnavailable as exc:
        # If no PDF engine, offer the HTML download as a fallback
        html = render_prescription_html_download(rx)
        resp = HttpResponse(html, content_type="text/html; charset=utf-8")
        resp["Content-Disposition"] = (
            f'attachment; filename="rx_{rx.patient.patient_id}_v{rx.version}.html"')
        return resp

    # Save to disk if production media storage is configured
    try:
        save_prescription_pdf(rx, data)
    except Exception:
        pass  # non-fatal; the PDF is still returned

    resp = HttpResponse(data, content_type="application/pdf")
    resp["Content-Disposition"] = (
        f'inline; filename="rx_{rx.patient.patient_id}_v{rx.version}.pdf"')
    return resp
