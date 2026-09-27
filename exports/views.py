"""
Research-dataset export.

  GET /exports/research-dataset/?fmt=csv|xlsx|sav&identified=0
  GET /exports/research-dataset/?table=findings&fmt=csv|xlsx   (biopsy findings)

De-identified by default (Study ID only). identified=1 requires data-manager
role (or superuser), per §13.5. Token or session auth via DRF.
"""
from django.http import HttpResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from patients.models import Patient

from .services.dataset import build_dataset
from .services.dictionary import DICTIONARY_COLUMNS, column_defs, data_dictionary
from .services.writers import (ExcelUnavailable, SavUnavailable, to_csv, to_sav,
                               to_xlsx)


def _can_export_identified(user):
    return user.is_superuser or user.groups.filter(name="data_manager").exists()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def research_dataset(request):
    fmt = request.GET.get("fmt", "csv").lower()
    identified = request.GET.get("identified") in ("1", "true", "yes")
    if identified and not _can_export_identified(request.user):
        return Response(
            {"detail": "Identified export requires the data_manager role."},
            status=403)

    study = (request.GET.get("study") or "").strip() or None
    table = (request.GET.get("table") or "patients").strip().lower()
    dictionary_rows, dictionary_cols = data_dictionary(identified), DICTIONARY_COLUMNS
    if table == "findings":
        # Repeated biopsy findings: a child table keyed by patient / biopsy /
        # report revision / finding (never widens the patient-level rows).
        from .services.dataset import build_findings_table
        from .services.dictionary import findings_dictionary
        cols, rows = build_findings_table(Patient.objects.all())
        dictionary_rows = findings_dictionary()
        tag = "biopsy_findings"
        if fmt == "sav":
            fmt = "csv"
    else:
        cols, rows = build_dataset(Patient.objects.all().order_by("patient_id"),
                                   identified=identified, study=study)
        tag = "identified" if identified else "deidentified"
        if study:
            tag = f"{study}_{tag}"

    if fmt == "xlsx":
        try:
            data = to_xlsx(cols, rows, dictionary=dictionary_rows,
                           dictionary_columns=dictionary_cols)
        except ExcelUnavailable as exc:
            return Response({"detail": str(exc)}, status=503)
        resp = HttpResponse(
            data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        resp["Content-Disposition"] = f'attachment; filename="bgddr_research_{tag}.xlsx"'
        return resp

    if fmt == "sav":
        try:
            data = to_sav(cols, rows, defs=column_defs(identified, study=bool(study)))
        except SavUnavailable as exc:
            return Response({"detail": str(exc)}, status=503)
        resp = HttpResponse(data, content_type="application/x-spss-sav")
        resp["Content-Disposition"] = f'attachment; filename="bgddr_research_{tag}.sav"'
        return resp

    resp = HttpResponse(to_csv(cols, rows), content_type="text/csv")
    resp["Content-Disposition"] = f'attachment; filename="bgddr_research_{tag}.csv"'
    return resp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dictionary(request):
    """The research dataset's data dictionary / codebook (Appendix C)."""
    identified = request.GET.get("identified") in ("1", "true", "yes")
    if identified and not _can_export_identified(request.user):
        identified = False
    return Response({"columns": DICTIONARY_COLUMNS,
                     "entries": data_dictionary(identified)})
