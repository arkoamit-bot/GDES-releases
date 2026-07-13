"""FHIR API views for export and import."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .export import export_patient_bundle, export_all_patients, export_patient
from .import_fhir import import_bundle


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fhir_capabilities(request):
    """FHIR capability statement."""
    return Response({
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": "2026-07-09",
        "publisher": "BIRDEM General Hospital — Dept. of Nephrology",
        "kind": "instance",
        "software": {"name": "BGDDR FHIR Module", "version": "1.0.0"},
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [{
            "mode": "server",
            "resource": [
                {"type": "Patient", "interaction": ["read", "search-type", "create"]},
                {"type": "Observation", "interaction": ["read", "search-type"]},
                {"type": "Condition", "interaction": ["read"]},
                {"type": "MedicationRequest", "interaction": ["read"]},
                {"type": "DiagnosticReport", "interaction": ["read"]},
            ],
        }],
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fhir_export_patient(request, patient_id=None):
    """Export a single patient as FHIR R4 Bundle (include_related=true for full)."""
    from patients.models import Patient

    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"},
                        status=status.HTTP_404_NOT_FOUND)

    include_related = request.GET.get("include_related", "false").lower() == "true"
    bundle = export_patient_bundle(patient, include_related=include_related)
    return Response(bundle)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fhir_export_all(request):
    """Export all patients as a FHIR R4 Bundle."""
    bundle = export_all_patients()
    return Response(bundle)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def fhir_import(request):
    """Import resources from a FHIR R4 Bundle."""
    bundle = request.data
    if bundle.get("resourceType") != "Bundle":
        return Response({"error": "Expected a FHIR Bundle resource"},
                        status=status.HTTP_400_BAD_REQUEST)

    results = import_bundle(bundle)
    return Response({
        "status": "completed",
        "total": len(results),
        "results": results,
    })
