"""Placeholder views for the exports module.

Full export UI lives in the clinic-guided workflow; these endpoints handle
direct CSV/Excel/SPSS downloads via URL.
"""
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest


@login_required
def export_index(request):
    """Landing page listing available export formats."""
    return HttpResponse(
        "<h1>Dataset Exports</h1>"
        "<p>Available formats: CSV, Excel (.xlsx), SPSS (.sav)</p>"
        "<p>Use the research dashboard to generate exports.</p>"
    )


@login_required
def export_dataset_csv(request):
    """Placeholder — CSV export triggered via the export_dataset management command."""
    return HttpResponse("CSV export endpoint — use the CLI or dashboard.", content_type="text/plain")


@login_required
def export_dataset_xlsx(request):
    """Placeholder — Excel export endpoint."""
    return HttpResponse("Excel export endpoint — use the CLI or dashboard.", content_type="text/plain")


@login_required
def export_dataset_sav(request):
    """Placeholder — SPSS .sav export endpoint."""
    return HttpResponse("SPSS export endpoint — use the CLI or dashboard.", content_type="text/plain")
