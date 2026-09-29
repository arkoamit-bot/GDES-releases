"""
Recording lab results, the longitudinal way -- the ONE command every entry
path uses (results page, baseline form, API, admin, FHIR import,
reconciliation), plus the automatic effects the registry needs:

  1. Entering a creatinine auto-derives an eGFR result (CKD-EPI 2021, versioned).
  2. The patient's cached `latest_egfr` is refreshed from the newest current
     eGFR, which is exactly what the prescription renal-safety check reads.

Two further guarantees:

* Retries are idempotent. A caller passes an ``idempotency_key`` (the guided
  forms send a per-form token); recording again with the same key returns the
  row already created, with no second derivation. This is NOT a uniqueness
  rule on patient+test+date: a genuine same-day repeat measurement is recorded
  as a second row.
* Corrections supersede, never overwrite. ``correct_result`` writes a new row
  linked to the one it replaces; the original and its derived eGFR stay in the
  table (not current) so the history and the lineage remain readable.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from labs.models import LabResult, LabTest
from .egfr import ckd_epi_2021

CREATININE_CODE = "creatinine"
EGFR_CODE = "egfr"
CREATININE_UMOL_PER_MGDL = Decimal("88.4")
_UMOL_UNITS = {"umol/l", "µmol/l", "μmol/l", "umol"}


def _compute_flag(test: LabTest, value: Decimal) -> str:
    if value is None:
        return ""
    if test.ref_low is not None and value < test.ref_low:
        return LabResult.Flag.LOW
    if test.ref_high is not None and value > test.ref_high:
        return LabResult.Flag.HIGH
    return LabResult.Flag.NORMAL


def _patient_age(patient, on_date: dt.date) -> float | None:
    if not patient.dob:
        return None
    d = on_date
    return (d.year - patient.dob.year
            - ((d.month, d.day) < (patient.dob.month, patient.dob.day)))


def _to_decimal(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError({"value_numeric": f"'{value}' is not a number."})


def normalize(test: LabTest, value: Decimal | None, unit: str):
    """Canonical unit per test. Creatinine is stored in mg/dL (what the eGFR
    equation expects); a value sent in umol/L is converted, not rejected."""
    unit = (unit or "").strip()
    if (test.code == CREATININE_CODE and value is not None
            and unit.lower() in _UMOL_UNITS):
        return (value / CREATININE_UMOL_PER_MGDL).quantize(Decimal("0.01")), "mg/dL"
    return value, unit or test.default_unit


def validate(test: LabTest, value: Decimal | None, value_text: str,
             result_date, sample_date=None):
    if value is None and not (value_text or "").strip():
        raise ValidationError("Enter a value or a qualitative result.")
    # A derived test (eGFR) may still arrive as a reported value from another
    # laboratory or an import; the guided forms do not offer it, and the API
    # refuses results that claim to be computed (source="derived").
    if value is not None and value < 0:
        raise ValidationError({"value_numeric": "Cannot be negative."})
    if result_date is None:
        raise ValidationError({"result_date": "A result date is required."})
    if sample_date and result_date and sample_date > result_date:
        raise ValidationError({"sample_date": "Sample date cannot be after result date."})


def refresh_latest_egfr(patient):
    """Set patient.latest_egfr to the most recent CURRENT eGFR result."""
    latest = (LabResult.objects
              .filter(patient=patient, test__code=EGFR_CODE,
                      value_numeric__isnull=False)
              .order_by("-result_date", "-created_at")
              .first())
    value = latest.value_numeric if latest else None
    if patient.latest_egfr != value:
        patient.latest_egfr = value
        patient.save(update_fields=["latest_egfr", "updated_at"])
    return latest


@transaction.atomic
def record_result(patient, test_code, *, result_date, value_numeric=None,
                  value_text="", unit="", sample_date=None, order_item=None,
                  source=LabResult.Source.LAB, age_years=None,
                  idempotency_key="", entry_path="", entered_by=None,
                  source_report_id="", specimen_id=""):
    """Record one result. If it's a creatinine, also derive & store eGFR and
    refresh the patient's cached eGFR. Idempotent per ``idempotency_key``."""
    test = test_code if isinstance(test_code, LabTest) else LabTest.objects.get(code=test_code)
    key = (idempotency_key or "")[:80]
    if key:
        existing = LabResult.all_objects.filter(patient=patient, idempotency_key=key).first()
        if existing is not None:
            return existing

    value = _to_decimal(value_numeric)
    value, unit = normalize(test, value, unit)
    validate(test, value, value_text, result_date, sample_date)

    try:
        with transaction.atomic():
            result = LabResult.objects.create(
                patient=patient, test=test, order_item=order_item,
                value_numeric=value, value_text=(value_text or "").strip(),
                unit=unit, sample_date=sample_date,
                result_date=result_date, source=source,
                flag=_compute_flag(test, value) if value is not None else "",
                idempotency_key=key, entry_path=entry_path or "",
                entered_by=entered_by if getattr(entered_by, "pk", None) else None,
                source_report_id=source_report_id or "", specimen_id=specimen_id or "",
            )
    except IntegrityError:
        # A concurrent retry with the same key won the race.
        if key:
            return LabResult.all_objects.get(patient=patient, idempotency_key=key)
        raise

    if order_item is not None:
        order_item.order.refresh_status()

    if test.code == CREATININE_CODE and value is not None:
        _derive_egfr(patient, result, age_years=age_years)

    return result


@transaction.atomic
def correct_result(result, *, reason, value_numeric=None, value_text=None, unit=None,
                   result_date=None, sample_date=None, entered_by=None, entry_path=""):
    """Supersede ``result`` with a corrected observation.

    The original row -- and every eGFR derived from it -- is kept but no longer
    current; the new row links back to it (``supersedes``) and carries the
    reason. A corrected creatinine re-derives eGFR and refreshes the cache.
    """
    reason = (reason or "").strip()
    if not reason:
        raise ValidationError({"correction_reason": "State why the result is corrected."})
    result = LabResult.all_objects.select_for_update().get(pk=result.pk)
    if not result.is_current:
        raise ValidationError("Only the current version of a result can be corrected.")
    if result.source == LabResult.Source.DERIVED:
        raise ValidationError("Derived results are corrected by correcting their source.")

    test = result.test
    value = _to_decimal(value_numeric) if value_numeric is not None else result.value_numeric
    text = value_text if value_text is not None else result.value_text
    value, unit_ = normalize(test, value, unit if unit is not None else result.unit)
    rdate = result_date or result.result_date
    sdate = sample_date if sample_date is not None else result.sample_date
    validate(test, value, text, rdate, sdate)

    LabResult.all_objects.filter(pk=result.pk).update(is_current=False)
    LabResult.all_objects.filter(derived_from=result).update(is_current=False)
    new = LabResult.objects.create(
        patient=result.patient, test=test, order_item=result.order_item,
        value_numeric=value, value_text=(text or "").strip(), unit=unit_,
        sample_date=sdate, result_date=rdate, source=result.source,
        flag=_compute_flag(test, value) if value is not None else "",
        supersedes=result, correction_reason=reason[:240],
        entry_path=entry_path or result.entry_path,
        entered_by=entered_by if getattr(entered_by, "pk", None) else None,
        source_report_id=result.source_report_id, specimen_id=result.specimen_id,
    )
    if test.code == CREATININE_CODE and value is not None:
        _derive_egfr(result.patient, new)
    else:
        refresh_latest_egfr(result.patient)
    return new


def lineage(result):
    """Oldest-to-newest chain of versions that ``result`` belongs to."""
    chain = [result]
    node = result
    while node.supersedes_id:
        node = LabResult.all_objects.get(pk=node.supersedes_id)
        chain.insert(0, node)
    node = result
    while True:
        nxt = LabResult.all_objects.filter(supersedes=node).first()
        if nxt is None:
            break
        chain.append(nxt)
        node = nxt
    return chain


def _derive_egfr(patient, creatinine_result, *, age_years=None):
    age = age_years if age_years is not None else _patient_age(
        patient, creatinine_result.result_date)
    if age is None:
        refresh_latest_egfr(patient)
        return None  # cannot compute without age; creatinine still recorded

    scr = float(creatinine_result.value_numeric)
    if scr <= 0:
        return None
    egfr_value, version = ckd_epi_2021(scr, age, patient.sex)
    egfr_test = LabTest.objects.get(code=EGFR_CODE)

    egfr_result = LabResult.objects.create(
        patient=patient, test=egfr_test,
        value_numeric=Decimal(str(egfr_value)),
        unit=egfr_test.default_unit, result_date=creatinine_result.result_date,
        sample_date=creatinine_result.sample_date,
        source=LabResult.Source.DERIVED, entry_path=LabResult.EntryPath.DERIVED,
        derived_from=creatinine_result, formula_version=version,
        flag=_compute_flag(egfr_test, Decimal(str(egfr_value))),
    )
    refresh_latest_egfr(patient)
    return egfr_result


# --- Guided entry helpers ----------------------------------------------------

@dataclass
class PanelOutcome:
    """Truthful result of recording a panel: what was saved, what was already
    on file (not duplicated), and which fields failed and why."""
    saved: list = field(default_factory=list)
    existing: list = field(default_factory=list)
    failed: dict = field(default_factory=dict)      # code -> message

    @property
    def partial(self):
        return bool(self.failed) and bool(self.saved)


def same_value_on_file(patient, code, result_date, value_numeric, value_text):
    """Current results that already hold this exact value for the date."""
    value = _to_decimal(value_numeric)
    qs = LabResult.objects.filter(patient=patient, test__code=code, result_date=result_date)
    out = []
    for r in qs:
        if (value is not None and r.value_numeric is not None
                and Decimal(r.value_numeric) == value):
            out.append(r)
        elif value is None and (value_text or "").strip().lower() == (r.value_text or "").strip().lower():
            out.append(r)
    return out


def outstanding_order_item(patient, code, result_date):
    """The order item a returned result fulfils, when that is unambiguous:
    exactly one unresulted item for this test, ordered on or before the
    result date. Otherwise None (the result is recorded unlinked)."""
    from labs.models import LabOrder, LabOrderItem
    candidates = [it for it in LabOrderItem.objects.filter(
        order__patient=patient, test__code=code,
        order__status__in=[LabOrder.Status.ORDERED, LabOrder.Status.COLLECTED],
        order__ordered_date__lte=result_date).select_related("order")
        if not it.is_resulted]
    return candidates[0] if len(candidates) == 1 else None


def record_panel(patient, rows, *, result_date, token="", entry_path="guided",
                 entered_by=None, source=LabResult.Source.MANUAL,
                 allow_repeat=False, source_report_id=""):
    """Record several results entered together, each independently.

    * ``token`` (one per rendered form) makes a re-submission return the rows
      already created instead of inserting them again.
    * Without ``allow_repeat`` a value identical to one already on file for the
      same date is not inserted; it is reported in ``existing`` so the user
      can confirm it is a genuine repeat measurement.
    * A failure in one row never loses the others; it is reported per field.
    """
    outcome = PanelOutcome()
    for code, value_numeric, value_text in rows:
        key = f"{token}:{code}" if token else ""
        try:
            if key and LabResult.all_objects.filter(patient=patient,
                                                    idempotency_key=key).exists():
                outcome.saved.append(LabResult.all_objects.get(patient=patient,
                                                               idempotency_key=key))
                continue
            if not allow_repeat:
                dup = same_value_on_file(patient, code, result_date, value_numeric, value_text)
                if dup:
                    outcome.existing.extend(dup)
                    continue
            outcome.saved.append(record_result(
                patient, code, result_date=result_date, value_numeric=value_numeric,
                value_text=value_text, source=source, idempotency_key=key,
                entry_path=entry_path, entered_by=entered_by,
                source_report_id=source_report_id,
                order_item=outstanding_order_item(patient, code, result_date)))
        except ValidationError as exc:
            outcome.failed[code] = "; ".join(exc.messages)
        except LabTest.DoesNotExist:
            outcome.failed[code] = "Test is not in the laboratory catalogue."
        except Exception as exc:  # pragma: no cover - defensive, reported truthfully
            outcome.failed[code] = f"Not saved: {exc}"
    return outcome


def egfr_slope(patient, *, min_points=2):
    """Annualized eGFR slope (mL/min/1.73m^2 per year) via least-squares over the
    eGFR series. Returns None if too few points. A first cut at the auto-computed
    outcome the portfolio specifies — refine (e.g. mixed models) in analytics."""
    points = [(r.result_date, float(r.value_numeric))
              for r in LabResult.series(patient, EGFR_CODE)
              if r.value_numeric is not None]
    if len(points) < min_points:
        return None

    t0 = points[0][0]
    xs = [(d - t0).days / 365.25 for d, _ in points]
    ys = [v for _, v in points]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    return round(slope, 2)
