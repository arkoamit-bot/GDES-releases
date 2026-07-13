"""FHIR R4 resource exporters.

Converts BGDDR domain models to FHIR R4 resource dicts for interoperability
with hospital information systems and registries.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any


def _full_url(resource_type: str, local_id: int) -> str:
    return f"urn:uuid:{resource_type.lower()}-{local_id}"


def _reference(resource_type: str, local_id: int) -> dict:
    return {"reference": _full_url(resource_type, local_id)}


def _identifier(system: str, value: str) -> list[dict]:
    return [{"system": system, "value": value}]


def export_patient(patient) -> dict:
    """Convert a BGDDR Patient to a FHIR R4 Patient resource."""
    resource: dict[str, Any] = {
        "resourceType": "Patient",
        "id": _full_url("Patient", patient.id),
        "identifier": _identifier(
            "https://bgddr.birdem.org/patient-id", patient.patient_id
        ),
        "name": [{"use": "official", "text": patient.name}],
        "gender": {"M": "male", "F": "female", "O": "other"}.get(
            patient.sex, "unknown"
        ),
        "birthDate": str(patient.dob) if patient.dob else None,
    }

    if patient.hospital_id:
        resource["identifier"].append(
            {"system": "https://bgddr.birdem.org/hospital-id",
             "value": patient.hospital_id}
        )

    if patient.phone:
        resource["telecom"] = [{"system": "phone", "value": patient.phone}]

    if patient.site:
        resource["managingOrganization"] = {
            "reference": _full_url("Organization", patient.site.id),
            "display": patient.site.name,
        }

    return resource


def export_condition(patient, diagnosis: str, encounter=None) -> dict:
    """Convert a diagnosis to a FHIR R4 Condition resource."""
    fhir_condition = {
        "resourceType": "Condition",
        "id": _full_url("Condition", f"{patient.id}-{diagnosis[:20]}"),
        "subject": _reference("Patient", patient.id),
        "code": {
            "coding": [
                {"system": "http://snomed.info/sct",
                 "code": "90708001",
                 "display": diagnosis}
            ],
            "text": diagnosis,
        },
        "clinicalStatus": {
            "coding": [
                {"system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                 "code": "active"}
            ]
        },
        "onsetDateTime": str(patient.enrollment_date) if patient.enrollment_date else None,
    }
    if encounter:
        fhir_condition["encounter"] = _reference("Encounter", encounter.id)
    return fhir_condition


def export_lab_result(lab_result) -> dict:
    """Convert a LabResult to a FHIR R4 Observation resource."""
    obs: dict[str, Any] = {
        "resourceType": "Observation",
        "id": _full_url("Observation", lab_result.id),
        "status": "final",
        "subject": _reference("Patient", lab_result.patient_id),
        "code": {
            "coding": [
                {"system": "http://loinc.org",
                 "code": lab_result.test.code if lab_result.test else "",
                 "display": lab_result.test.name if lab_result.test else ""}
            ],
            "text": lab_result.test.name if lab_result.test else "",
        },
        "effectiveDateTime": str(lab_result.sample_date or lab_result.result_date or ""),
        "issued": str(lab_result.result_date or ""),
    }

    if lab_result.value_numeric is not None:
        obs["valueQuantity"] = {
            "value": float(lab_result.value_numeric),
            "unit": lab_result.unit or "",
            "system": "http://unitsofmeasure.org",
            "code": lab_result.unit or "",
        }
    elif lab_result.value_text:
        obs["valueString"] = lab_result.value_text

    if lab_result.flag:
        obs["interpretation"] = [
            {"coding": [
                {"system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                 "code": lab_result.flag.upper()}
            ]}
        ]

    return obs


def export_biopsy_report(biopsy) -> dict:
    """Convert a Biopsy to a FHIR R4 DiagnosticReport resource."""
    report: dict[str, Any] = {
        "resourceType": "DiagnosticReport",
        "id": _full_url("DiagnosticReport", biopsy.id),
        "status": "final",
        "subject": _reference("Patient", biopsy.patient_id),
        "code": {
            "coding": [
                {"system": "http://loinc.org",
                 "code": "45038-0",
                 "display": "Kidney biopsy report"}
            ],
            "text": "Kidney biopsy report",
        },
        "effectiveDateTime": str(biopsy.biopsy_date or ""),
        "conclusion": "",
    }

    if hasattr(biopsy, "gn_diagnosis") and biopsy.gn_diagnosis:
        report["conclusion"] = biopsy.gn_diagnosis.diagnosis
        report["conclusionCode"] = [
            {"coding": [{"system": "http://snomed.info/sct",
                         "display": biopsy.gn_diagnosis.diagnosis}]}
        ]

    if hasattr(biopsy, "light_microscopy") and biopsy.light_microscopy:
        report["result"] = [
            {
                "resourceType": "Observation",
                "code": {"text": "Light microscopy"},
                "valueString": biopsy.light_microscopy,
            }
        ]

    return report


def export_medication_request(prescription_item) -> dict:
    """Convert a PrescriptionItem to a FHIR R4 MedicationRequest resource."""
    timing_str = prescription_item.frequency or ""
    mr: dict[str, Any] = {
        "resourceType": "MedicationRequest",
        "id": _full_url("MedicationRequest", prescription_item.id),
        "status": "active",
        "intent": "order",
        "medicationCodeableConcept": {
            "coding": [
                {"system": "http://drugbank.ca",
                 "display": prescription_item.drug.generic_name
                 if prescription_item.drug_id else ""}
            ],
            "text": prescription_item.brand or prescription_item.drug.generic_name
            if prescription_item.drug_id else "",
        },
        "subject": _reference("Patient",
                              prescription_item.prescription.encounter.patient_id),
        "authoredOn": str(
            prescription_item.prescription.printed_at
            or prescription_item.prescription.created_at
        ),
        "dosageInstruction": [
            {
                "text": f"{prescription_item.dose} {prescription_item.frequency}"
                        f" {prescription_item.timing}".strip(),
                "timing": {
                    "code": {
                        "coding": [
                            {"display": timing_str}
                        ]
                    }
                } if timing_str else None,
                "doseAndRate": [
                    {
                        "type": {"coding": [{"display": "ordered"}]},
                        "doseQuantity": {
                            "value": float(prescription_item.dose.split()[0])
                            if prescription_item.dose and prescription_item.dose.split()[0].replace(".", "").isdigit()
                            else None,
                            "unit": prescription_item.dose_unit or "",
                        },
                    }
                ] if prescription_item.dose else None,
            }
        ],
    }
    return mr


def export_patient_bundle(patient, include_related: bool = False) -> dict:
    """Export a patient and optionally all related data as a FHIR R4 Bundle."""
    entries = [
        {"fullUrl": _full_url("Patient", patient.id),
         "resource": export_patient(patient),
         "request": {"method": "PUT", "url": f"Patient/{_full_url('Patient', patient.id)}"}},
    ]

    if include_related:
        # Conditions from primary diagnosis
        if patient.primary_diagnosis:
            entries.append({
                "fullUrl": _full_url("Condition", f"{patient.id}-dx"),
                "resource": export_condition(patient, patient.primary_diagnosis),
                "request": {"method": "PUT", "url": "Condition/..."},
            })

        # Lab results
        try:
            for lab in patient.lab_results.all()[:100]:
                entries.append({
                    "fullUrl": _full_url("Observation", lab.id),
                    "resource": export_lab_result(lab),
                    "request": {"method": "PUT", "url": "Observation/..."},
                })
        except Exception:
            pass

        # Prescriptions
        try:
            for encounter in patient.encounters.all():
                for rx in encounter.prescriptions.filter(status="final"):
                    for item in rx.items.all():
                        entries.append({
                            "fullUrl": _full_url("MedicationRequest", item.id),
                            "resource": export_medication_request(item),
                            "request": {"method": "PUT", "url": "MedicationRequest/..."},
                        })
        except Exception:
            pass

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": entries,
    }


def export_all_patients() -> dict:
    """Export all patients as a single FHIR R4 Bundle."""
    from patients.models import Patient
    patients = Patient.objects.all()
    entries = []
    for p in patients:
        entries.append({
            "fullUrl": _full_url("Patient", p.id),
            "resource": export_patient(p),
        })
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "total": len(entries),
        "entry": entries,
    }
