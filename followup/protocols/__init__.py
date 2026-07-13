"""Protocol registry: maps disease identifiers to protocol classes."""

from .base import FollowUpProtocol


_registry = {}


def register(protocol_class):
    _registry[protocol_class.disease_id] = protocol_class
    return protocol_class


def get_protocol(disease_id):
    return _registry.get(disease_id)


def get_all_protocols():
    return list(_registry.values())


def get_protocol_for_patient(patient):
    from patients.models import Patient
    if hasattr(patient, "clinical_profile") and patient.clinical_profile:
        differential = patient.clinical_profile.differential or []
        if differential:
            top = differential[0]
            disease_id = top.get("disease_id") or top.get("disease_name", "").lower().replace(" ", "_")
            proto = get_protocol(disease_id)
            if proto:
                return proto
    biopsies = patient.biopsies.filter(
        diagnosis__isnull=False).order_by("-biopsy_date")
    for bx in biopsies:
        try:
            gndiag = bx.diagnosis
            disease_key = gndiag.diagnosis.lower().replace(" ", "_").replace("/", "_")
            proto = get_protocol(disease_key)
            if proto:
                return proto
        except GNDiagnosis.DoesNotExist:
            continue
    return get_protocol("general")


from . import igan
from . import mcd
from . import fsgs
from . import mn
from . import ln
from . import anca
from . import anti_gbm
from . import c3g
from . import mpgn
from . import ddd
from . import general
