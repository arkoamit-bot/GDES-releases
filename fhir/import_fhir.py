"""FHIR R4 resource importers.

Parses FHIR R4 resource bundles and creates/updates BGDDR domain objects.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from django.db import transaction


@transaction.atomic
def import_patient_from_fhir(fhir_patient: dict) -> dict:
    """Import or update a Patient from a FHIR R4 Patient resource.

    Returns dict with status, patient_id, and any errors.
    """
    from patients.models import Patient

    identifier = _get_identifier(fhir_patient, "https://bgddr.birdem.org/patient-id")
    hospital_id = _get_identifier(fhir_patient, "https://bgddr.birdem.org/hospital-id")

    name = _get_name(fhir_patient)
    gender = fhir_patient.get("gender", "")
    sex_map = {"male": "M", "female": "F", "other": "O", "unknown": "O"}
    sex = sex_map.get(gender, "O")
    birth_date = _parse_date(fhir_patient.get("birthDate"))
    phone = _get_telecom(fhir_patient, "phone")

    if identifier:
        patient, created = Patient.objects.get_or_create(
            patient_id=identifier,
            defaults={
                "name": name or "Imported Patient",
                "sex": sex,
                "dob": birth_date,
                "phone": phone or "",
                "hospital_id": hospital_id or "",
            },
        )
        if not created:
            has_updates = False
            if name and name != patient.name:
                patient.name = name
                has_updates = True
            if hospital_id and hospital_id != patient.hospital_id:
                patient.hospital_id = hospital_id
                has_updates = True
            if phone and phone != patient.phone:
                patient.phone = phone
                has_updates = True
            if has_updates:
                patient.save()
    else:
        created = True
        patient = Patient.objects.create(
            name=name or "FHIR Import",
            sex=sex,
            dob=birth_date,
            phone=phone or "",
            hospital_id=hospital_id or "",
        )

    return {
        "status": "created" if created else "updated",
        "patient_id": patient.patient_id,
        "id": patient.id,
    }


def import_lab_from_fhir(fhir_obs: dict) -> dict:
    """Import an Observation (lab result) from FHIR R4."""
    from patients.models import Patient
    from labs.models import LabResult, LabTest

    subject = fhir_obs.get("subject", {})
    ref = subject.get("reference", "")
    patient_id = _parse_reference(ref, "Patient")

    if not patient_id:
        return {"status": "error", "error": "No patient reference"}

    try:
        patient = Patient.objects.get(id=patient_id)
    except (Patient.DoesNotExist, ValueError):
        return {"status": "error", "error": f"Patient {patient_id} not found"}

    coding = fhir_obs.get("code", {}).get("coding", [])
    loinc_code = coding[0].get("code", "") if coding else ""
    display = coding[0].get("display", "") if coding else ""

    if loinc_code:
        # Map to the catalogue test carrying this LOINC first, so an imported
        # creatinine is the registry's creatinine (and derives eGFR); only an
        # unknown code creates a new catalogue entry.
        test = (LabTest.objects.filter(loinc=loinc_code).first()
                or LabTest.objects.filter(code=loinc_code).first())
        if test is None:
            test = LabTest.objects.create(code=loinc_code, loinc=loinc_code,
                                          name=display or loinc_code)
    else:
        return {"status": "error", "error": "No LOINC code"}

    value_qty = fhir_obs.get("valueQuantity", {})
    value_str = fhir_obs.get("valueString")

    effective = _parse_date(fhir_obs.get("effectiveDateTime"))
    issued = _parse_date(fhir_obs.get("issued"))

    # Through the one recording service: unit normalisation, eGFR derivation,
    # cache refresh; the Observation id makes a re-import idempotent.
    from labs.services.results import record_result
    obs_id = str(fhir_obs.get("id") or "")
    lab_result = record_result(
        patient, test,
        value_numeric=value_qty.get("value") if value_qty else None,
        value_text=value_str or "",
        unit=value_qty.get("unit", "") if value_qty else "",
        sample_date=effective or issued or date.today(),
        result_date=issued or effective or date.today(),
        entry_path=LabResult.EntryPath.FHIR,
        idempotency_key=f"fhir:{obs_id}" if obs_id else "",
        source_report_id=obs_id[:60],
    )

    return {"status": "created", "id": lab_result.id}


def import_bundle(fhir_bundle: dict) -> list[dict]:
    """Import all resources from a FHIR R4 Bundle.

    Returns list of import results (one per resource).
    """
    results = []
    entries = fhir_bundle.get("entry", [])

    for entry in entries:
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType", "")

        try:
            if resource_type == "Patient":
                results.append(import_patient_from_fhir(resource))
            elif resource_type == "Observation":
                results.append(import_lab_from_fhir(resource))
            else:
                results.append({"status": "skipped", "resourceType": resource_type})
        except Exception as e:
            results.append({"status": "error", "resourceType": resource_type, "error": str(e)})

    return results


# --- Helper functions ---

def _get_identifier(resource: dict, system: str) -> str | None:
    for ident in resource.get("identifier", []):
        if ident.get("system") == system:
            return ident.get("value")
    return None


def _get_name(resource: dict) -> str:
    for name in resource.get("name", []):
        if name.get("use") in ("official", "usual", None):
            parts = []
            if name.get("given"):
                parts.extend(name["given"])
            if name.get("family"):
                parts.append(name["family"])
            if name.get("text"):
                return name["text"]
            return " ".join(parts) if parts else ""
    return ""


def _get_telecom(resource: dict, system: str) -> str | None:
    for t in resource.get("telecom", []):
        if t.get("system") == system:
            return t.get("value")
    return None


def _parse_date(d: str | None) -> date | None:
    if not d:
        return None
    try:
        return date.fromisoformat(d[:10])
    except (ValueError, TypeError):
        return None


def _parse_reference(ref: str, expected_type: str) -> str | None:
    if not ref:
        return None
    parts = ref.split("/")
    if len(parts) == 2 and parts[0] == expected_type:
        return parts[1]
    if ref.startswith("urn:uuid:"):
        parts = ref.split("-")
        return parts[-1] if len(parts) > 1 else None
    return ref
