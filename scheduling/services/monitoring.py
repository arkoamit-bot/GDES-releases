"""
Laboratory-monitoring schedule for active immunosuppression (protocol §7.7).

Given a patient's currently-active immunosuppressive agents, return the
agent-specific monitoring requirements (which labs, how often). This is reference
logic the clinic uses to know what to order alongside each visit — it does not
itself place orders (the labs app does that).
"""
from __future__ import annotations

import datetime as dt

from treatments.models import DrugClass, TreatmentExposure

# Drug classes that count as active immunosuppression for monitoring purposes.
IMMUNOSUPPRESSION = {
    DrugClass.STEROID, DrugClass.CYCLOPHOSPHAMIDE, DrugClass.RITUXIMAB,
    DrugClass.CNI, DrugClass.MMF, DrugClass.AZATHIOPRINE,
}

# Agent-specific monitoring (labs + cadence) from §7.7.
REQUIREMENTS = {
    DrugClass.STEROID: [
        ("CBC, creatinine, random glucose, urine glucose/protein", "monthly months 1-6"),
    ],
    DrugClass.CYCLOPHOSPHAMIDE: [
        ("CBC with differential, creatinine, LFT", "weeks 1 and 2"),
        ("Urinalysis (haemorrhagic cystitis surveillance)", "each monthly visit"),
        ("CBC nadir", "day 10-14 of each pulse cycle"),
    ],
    DrugClass.RITUXIMAB: [
        ("CBC", "monthly"),
        ("Serum immunoglobulins", "3 and 6 months post-infusion"),
    ],
    DrugClass.CNI: [
        ("Trough drug level", "weeks 2, 4, then monthly"),
        ("Creatinine", "monthly"),
    ],
    DrugClass.MMF: [
        ("CBC with differential, LFT", "weeks 1 and 2, then monthly months 1-6"),
    ],
    DrugClass.AZATHIOPRINE: [
        ("CBC, LFT", "monthly"),
    ],
    DrugClass.HCQ: [
        ("Baseline + annual retinal screening (visual fields / OCT)", "baseline, then yearly"),
    ],
    DrugClass.FINERENONE: [
        ("Serum potassium + creatinine", "4 weeks after start / dose change, then periodically"),
    ],
    DrugClass.SGLT2I: [
        ("Volume status, foot care; hold during acute illness (DKA/AKI risk)", "each visit"),
    ],
}

# Any drug class with a monitoring schedule (immunosuppression + finerenone/HCQ/SGLT2i).
MONITORED_CLASSES = set(REQUIREMENTS)


def active_immunosuppression(patient, as_of=None):
    """Ongoing immunosuppressive exposures as of a date."""
    as_of = as_of or dt.date.today()
    qs = (TreatmentExposure.objects
          .filter(patient=patient, ongoing=True, drug__drug_class__in=IMMUNOSUPPRESSION,
                  start_date__lte=as_of)
          .select_related("drug"))
    return list(qs)


def is_on_active_immunosuppression(patient, as_of=None):
    return bool(active_immunosuppression(patient, as_of))


def active_monitored(patient, as_of=None):
    """Ongoing exposures to any drug class that carries a monitoring schedule
    (immunosuppression plus finerenone / HCQ / SGLT2i)."""
    as_of = as_of or dt.date.today()
    qs = (TreatmentExposure.objects
          .filter(patient=patient, ongoing=True, drug__drug_class__in=MONITORED_CLASSES,
                  start_date__lte=as_of)
          .select_related("drug"))
    return list(qs)


def monitoring_requirements(patient, as_of=None):
    """Per-agent monitoring requirements auto-generated from a patient's active
    drugs — CBC/LFT for MMF, potassium for finerenone, retinal for HCQ, etc."""
    out = []
    seen = set()
    for exp in active_monitored(patient, as_of):
        cls = exp.drug.drug_class
        if cls in seen:
            continue
        seen.add(cls)
        for labs, cadence in REQUIREMENTS.get(cls, []):
            out.append({"agent": exp.drug.get_drug_class_display(),
                        "drug": exp.drug_name, "labs": labs, "cadence": cadence})
    return out
