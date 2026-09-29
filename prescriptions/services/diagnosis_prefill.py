"""Which diagnosis a new prescription starts from, and where it came from.

Order (docs/CLAUDE_OPUS_BIOPSY_LINKAGE_DIAGNOSIS_CARRY_FORWARD_2026-09-29.md, B):

1.  The most recent FINALIZED prescription of the same patient with a
    diagnosis, ordered by visit date, then version, then id, and never from a
    visit later than the one being prescribed for.
2.  Otherwise the patient's working diagnosis.
3.  Otherwise blank, shown as blank.

The prefill is a convenience, not a new confirmation: the form says where it
came from. A newer saved draft is offered, not substituted. Facts that differ
from the carried text -- the working diagnosis, the selected biopsy's
diagnosis -- are shown beside it, never swapped in. Medication carry-forward
is separate and unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DiagnosisPrefill:
    value: str = ""
    source: str = "none"           # prescription | working | none
    source_label: str = ""
    source_prescription: object = None
    newer_draft: object = None     # a draft newer than the source, to resume
    also_on_record: list = field(default_factory=list)   # [(label, value)]


def _applicable(patient, encounter):
    from prescriptions.models import Prescription
    qs = Prescription.objects.filter(encounter__patient=patient)
    if encounter is not None:
        qs = qs.filter(encounter__encounter_date__lte=encounter.encounter_date)
    return qs.select_related("encounter").order_by(
        "-encounter__encounter_date", "-version", "-id")


def diagnosis_prefill(patient, encounter) -> DiagnosisPrefill:
    from prescriptions.models import Prescription

    out = DiagnosisPrefill()
    qs = _applicable(patient, encounter)
    source = (qs.filter(status=Prescription.Status.FINAL)
              .exclude(diagnosis_text="").first())
    if source is not None:
        out.value = source.diagnosis_text
        out.source = "prescription"
        out.source_prescription = source
        out.source_label = (f"Carried from the prescription of "
                            f"{source.encounter.encounter_date:%d %b %Y} (v{source.version})")
    elif (patient.primary_diagnosis or "").strip():
        out.value = patient.primary_diagnosis.strip()
        out.source = "working"
        out.source_label = "From the patient's working diagnosis"

    # A saved draft newer than the source is offered for resumption.
    drafts = qs.filter(status=Prescription.Status.DRAFT)
    if source is not None:
        from django.db.models import Q
        d = source.encounter.encounter_date
        drafts = drafts.filter(
            Q(encounter__encounter_date__gt=d)
            | Q(encounter__encounter_date=d, version__gt=source.version)
            | Q(encounter__encounter_date=d, version=source.version, id__gt=source.id))
    out.newer_draft = drafts.first()

    if out.source == "prescription":
        working = (patient.primary_diagnosis or "").strip()
        if working and working != out.value:
            out.also_on_record.append(("Working diagnosis on the patient record", working))
    pathology = (getattr(patient, "biopsy_diagnosis", "") or "").strip()
    if pathology and pathology != out.value and all(v != pathology for _l, v in out.also_on_record):
        out.also_on_record.append(("Diagnosis of the selected biopsy", pathology))
    return out
