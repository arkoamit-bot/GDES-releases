"""
Patient-level operations that need to respect the FK graph.

`delete_patient_cascade` removes a patient and ALL their clinical data in a
foreign-key-safe order. The registry deliberately PROTECTs encounters (and
prescriptions / lab orders PROTECT their encounter) so nothing is deleted by
accident — which also means a plain Patient.delete() is refused while any visit
exists. This helper deletes the protected children first, then the patient
(whose remaining children cascade).
"""
from django.db import transaction


@transaction.atomic
def delete_patient_cascade(patient):
    """Delete a patient and everything hanging off them. Returns the patient_id."""
    pid = patient.patient_id
    from prescriptions.models import Prescription
    from labs.models import LabOrder

    # 1. Free the encounters: prescriptions and lab orders PROTECT them.
    Prescription.objects.filter(encounter__patient=patient).delete()  # cascades items
    LabOrder.objects.filter(patient=patient).delete()                 # cascades items/results

    # 2. Encounters (PROTECT patient) can now go.
    patient.encounters.all().delete()

    # 3. The rest (baseline, biopsies, exposures, events, outcome, consents,
    #    enrolments, adverse events, admissions, relapses, scheduled visits,
    #    lab results) cascade with the patient.
    # NB: Patient.delete() raises PermissionDenied by design; bypass via
    # super() so the cascade through CASCADE FKs completes.
    from django.db.models.base import Model
    Model.delete(patient)
    return pid
