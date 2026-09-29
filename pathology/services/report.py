"""Pathology reports and their repeatable findings -- the shared command layer.

Guided entry, amendment, the API and the admin all validate and save through
here, so a report is checked the same way whichever door it comes in by:

* counts are per modality and never exceed the applicable total;
* percentages are 0-100 (model validators) and a reported percentage that
  disagrees with the counts is kept as reported and surfaced as a warning;
* a finding cannot be recorded for a modality the report says was not done,
  unavailable or still pending;
* a biopsy summary flag stated "absent" cannot coexist with a present finding
  of the same lesion; a blank flag is filled from the finding;
* "Other" needs a description; an IF/IHC row needs its marker.

Arithmetic contradictions are errors. Interpretive tension that arithmetic
cannot settle is a warning. Nothing here computes a disease score.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Max

from patients import choices
from pathology import findings as vocab
from pathology.models import ModalityStatus, PathologyFinding, PathologyReport

REPORT_FIELDS = [
    "status", "report_identifier", "laboratory", "pathologist", "specimen_date",
    "report_date", "context", "signed_by", "signed_at", "cortex_present",
    "medulla_present", "cores", "glomeruli_if", "glomeruli_em",
    "globally_sclerosed", "segmentally_sclerosed", "crescentic_glomeruli",
    "limitations", "lm_status", "if_status", "ihc_status", "em_status",
    "primary_diagnosis", "additional_diagnoses", "comment",
    "original_report_text", "panel_override_reason",
]
FINDING_FIELDS = [
    "section", "code", "other_label", "presence", "severity", "extent",
    "extent_pct", "count", "denominator", "site", "marker", "intensity",
    "distribution", "detail",
]
BLOCKING_MODALITY = {ModalityStatus.NOT_DONE, ModalityStatus.UNAVAILABLE,
                     ModalityStatus.PENDING}
_DX_VALUES = {v for v, _ in choices.SPECIFIC_GN_DIAGNOSIS}


class ReportInvalid(Exception):
    def __init__(self, errors, warnings=()):
        self.errors = errors
        self.warnings = list(warnings)
        super().__init__("; ".join(f"{k}: {' '.join(v)}" for k, v in errors.items()))


def _num(value):
    if value in (None, ""):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _is_blank_finding(f: dict) -> bool:
    return not (f.get("code") or f.get("marker") or f.get("other_label") or f.get("detail"))


def validate_report(data: dict, findings: list[dict], *, total_glomeruli=None,
                    summary: dict | None = None, reported_pct: dict | None = None):
    """Return (errors, warnings, derived_summary).

    errors: {"field" | "finding-<n>" | "__all__": [messages]}
    derived_summary: blank Biopsy summary flags a present finding fills.
    """
    errors: dict[str, list[str]] = {}
    warnings: list[str] = []
    summary = summary or {}
    reported_pct = reported_pct or {}

    def err(key, msg):
        errors.setdefault(key, []).append(msg)

    total = _num(total_glomeruli)
    counts = {k: _num(data.get(k)) for k in
              ("globally_sclerosed", "segmentally_sclerosed", "crescentic_glomeruli",
               "cores", "glomeruli_if", "glomeruli_em")}
    for key, value in counts.items():
        if value is not None and value < 0:
            err(key, "Cannot be negative.")
    if total is not None:
        for key in ("globally_sclerosed", "segmentally_sclerosed", "crescentic_glomeruli"):
            if counts[key] is not None and counts[key] > total:
                err(key, f"Exceeds the {total:g} glomeruli examined by light microscopy.")
        both = [counts[k] for k in ("globally_sclerosed", "segmentally_sclerosed")
                if counts[k] is not None]
        if len(both) == 2 and sum(both) > total:
            err("segmentally_sclerosed",
                "Globally + segmentally sclerosed exceeds the light-microscopy total.")
        # A reported percentage is kept as reported; a disagreement with the
        # counts is surfaced, never silently replaced.
        for pct_key, count_key in (("global_sclerosis_pct", "globally_sclerosed"),
                                   ("crescent_pct", "crescentic_glomeruli")):
            pct, count = _num(reported_pct.get(pct_key)), counts[count_key]
            if pct is not None and count is not None and total > 0:
                calc = (count / total * 100).quantize(Decimal("0.1"))
                if abs(calc - pct) > 1:
                    warnings.append(
                        f"Reported {pct_key.replace('_', ' ')} is {pct}% but "
                        f"{count:g}/{total:g} glomeruli is {calc}%. The reported "
                        f"value is kept; check the report.")
    elif any(counts[k] is not None for k in
             ("globally_sclerosed", "segmentally_sclerosed", "crescentic_glomeruli")):
        warnings.append("Sclerosis/crescent counts were entered without the number "
                        "of glomeruli examined; proportions cannot be checked.")

    for dx in data.get("additional_diagnoses") or []:
        if dx not in _DX_VALUES:
            err("additional_diagnoses", f"Unknown diagnosis: {dx}")
    primary = data.get("primary_diagnosis") or ""
    if primary and primary in (data.get("additional_diagnoses") or []):
        err("additional_diagnoses", "The primary diagnosis is repeated as additional.")

    present_codes: set[str] = set()
    n = 0
    for i, f in enumerate(findings):
        if _is_blank_finding(f):
            continue
        n += 1
        key = f"finding-{i}"
        section = f.get("section") or ""
        code = f.get("code") or ""
        if section not in vocab.SECTIONS:
            err(key, "Unknown section.")
            continue
        if section == "if_marker":
            if not f.get("marker"):
                err(key, "Choose the marker for this IF/IHC row.")
            if f.get("marker") == vocab.OTHER and not (f.get("other_label") or "").strip():
                err(key, "Name the marker.")
        elif code not in vocab.codes_for(section):
            err(key, f"'{code}' is not a {vocab.section_label(section)} finding.")
        if code == vocab.OTHER and not ((f.get("other_label") or "").strip()
                                        or (f.get("detail") or "").strip()):
            err(key, "Describe the 'Other' finding.")
        count, denom = _num(f.get("count")), _num(f.get("denominator"))
        if count is not None and denom is not None and count > denom:
            err(key, "The count exceeds its denominator.")
        pct = _num(f.get("extent_pct"))
        if pct is not None and not (0 <= pct <= 100):
            err(key, "Extent must be 0-100%.")
        modality = data.get(vocab.SECTION_MODALITY.get(section, "")) or ""
        if modality in BLOCKING_MODALITY:
            label = dict(ModalityStatus.choices)[modality].lower()
            err(key, f"{vocab.section_label(section)}: the report says this modality "
                     f"is {label}, so a finding cannot be recorded for it.")
        elif modality == ModalityStatus.INADEQUATE:
            warnings.append(f"{vocab.section_label(section)} finding recorded on a "
                            f"sample the report calls inadequate.")
        if (f.get("presence") or "present") == "present":
            present_codes.add(code)

    derived = {}
    for flag, codes in vocab.SUMMARY_LINKS.items():
        if present_codes & codes:
            stated = summary.get(flag)
            if stated is False:
                err("__all__",
                    f"'{flag.replace('_', ' ')}' is recorded as absent but a matching "
                    f"finding is recorded as present. Correct one of them.")
            elif stated is None:
                derived[flag] = True

    status = data.get("status") or PathologyReport.Status.FINAL
    if status == PathologyReport.Status.FINAL and n == 0 and not primary:
        warnings.append("A final report with no findings and no diagnosis.")
    return errors, warnings, derived


def score_snapshot(biopsy) -> dict:
    """The disease-score values currently on the biopsy, as plain data."""
    out = {}

    def rel(name):
        try:
            return getattr(biopsy, name)
        except Exception:
            return None

    ig = rel("igan_score")
    if ig:
        out["mest"] = {k: getattr(ig, k) for k in ("M", "E", "S", "T", "C")}
    ln = rel("lupus")
    if ln:
        out["lupus"] = {"isn_rps_class": ln.isn_rps_class,
                        "activity_index": ln.activity_index,
                        "chronicity_index": ln.chronicity_index}
    fs = rel("fsgs")
    if fs:
        out["fsgs"] = {"primary_secondary": fs.primary_secondary, "variant": fs.variant}
    mn = rel("membranous")
    if mn:
        out["mn"] = {"pla2r_tissue": mn.pla2r_tissue,
                     "thsd7a_tissue": mn.thsd7a_tissue, "mn_stage": mn.mn_stage}
    return out


def _clean_findings(findings):
    rows = []
    for i, f in enumerate(findings):
        if _is_blank_finding(f):
            continue
        row = {k: f.get(k) for k in FINDING_FIELDS}
        for k in ("other_label", "severity", "extent", "site", "marker",
                  "intensity", "distribution", "detail"):
            row[k] = (row.get(k) or "").strip()
        row["presence"] = row.get("presence") or PathologyFinding.Presence.PRESENT
        if row["section"] == "if_marker":
            row["code"] = "marker"
        row["sort_order"] = i
        rows.append(row)
    return rows


def _check(biopsy, data, findings, summary=None):
    errors, warnings, derived = validate_report(
        data, findings, total_glomeruli=biopsy.total_glomeruli,
        summary=summary if summary is not None else {
            f: getattr(biopsy, f) for f in vocab.SUMMARY_LINKS},
        reported_pct={"global_sclerosis_pct": biopsy.global_sclerosis_pct,
                      "crescent_pct": biopsy.crescent_pct})
    if errors:
        raise ReportInvalid(errors, warnings)
    return warnings, derived


def _apply_derived(biopsy, derived):
    changed = [f for f, v in derived.items() if getattr(biopsy, f) is None]
    for f in changed:
        setattr(biopsy, f, derived[f])
    if changed:
        biopsy.save(update_fields=changed + ["updated_at"])


def _create(biopsy, *, role, revision, data, findings, user, origin,
            supersedes=None, reason=""):
    fields = {k: data.get(k) for k in REPORT_FIELDS if k in data}
    for k in ("report_identifier", "laboratory", "pathologist", "signed_by",
              "limitations", "comment", "original_report_text",
              "panel_override_reason", "primary_diagnosis", "context",
              "lm_status", "if_status", "ihc_status", "em_status"):
        if k in fields and fields[k] is None:
            fields[k] = ""
    fields["additional_diagnoses"] = list(fields.get("additional_diagnoses") or [])
    fields.setdefault("status", PathologyReport.Status.FINAL)
    if not fields.get("specimen_date"):
        fields["specimen_date"] = biopsy.biopsy_date
    report = PathologyReport.objects.create(
        biopsy=biopsy, role=role, revision=revision, origin=origin,
        supersedes=supersedes, revision_reason=reason, entered_by=user,
        scores=score_snapshot(biopsy), **fields)
    PathologyFinding.objects.bulk_create(
        [PathologyFinding(report=report, **row) for row in _clean_findings(findings)])
    return report


@transaction.atomic
def save_report(biopsy, *, data, findings, role="local", user=None,
                origin=PathologyReport.Origin.GUIDED):
    """Record a new report for a read that has none yet (revision 1)."""
    if biopsy.reports.filter(role=role).exists():
        raise ReportInvalid({"__all__": [
            "This read already has a report; amend it or add an addendum."]})
    warnings, derived = _check(biopsy, data, findings)
    report = _create(biopsy, role=role, revision=1, data=data, findings=findings,
                     user=user, origin=origin)
    _apply_derived(biopsy, derived)
    emit_report_changed(biopsy, report)
    return report, warnings


@transaction.atomic
def amend_report(report, *, data, findings, reason, user=None, kind="amendment"):
    """New revision superseding ``report``; the old revision is kept intact.

    kind "amendment" replaces the content; "addendum" keeps the previous
    findings and adds the new ones.
    """
    from audit.local import acting_as

    reason = (reason or "").strip()
    if not reason:
        raise ReportInvalid({"revision_reason": ["State why the report is amended."]})
    if not report.is_current:
        raise ReportInvalid({"__all__": ["Only the current revision can be amended."]})
    biopsy = report.biopsy
    if kind == "addendum":
        base = [{k: getattr(f, k) for k in FINDING_FIELDS} for f in report.findings.all()]
        findings = base + list(findings)
        merged = {k: getattr(report, k) for k in REPORT_FIELDS}
        merged.update({k: v for k, v in data.items() if v not in (None, "", [])})
        data = merged
    warnings, derived = _check(biopsy, data, findings)
    next_rev = (biopsy.reports.filter(role=report.role)
                .aggregate(m=Max("revision"))["m"] or 0) + 1
    with acting_as(user, reason=f"Pathology report {kind}: {reason}"[:240]):
        PathologyReport.objects.filter(pk=report.pk).update(is_current=False)
        new = _create(biopsy, role=report.role, revision=next_rev, data=data,
                      findings=findings, user=user,
                      origin=(PathologyReport.Origin.ADDENDUM if kind == "addendum"
                              else PathologyReport.Origin.AMENDMENT),
                      supersedes=report, reason=reason)
        _apply_derived(biopsy, derived)
    emit_report_changed(biopsy, new)
    return new, warnings


def current_report(biopsy, role="local"):
    return biopsy.reports.filter(role=role, is_current=True).first()


@transaction.atomic
def legacy_report_from_biopsy(biopsy):
    """Convert a pre-2026-09-27 biopsy's scalar IF/EM values into structured
    findings on a LOCAL report tagged as legacy. Idempotent: skipped when the
    biopsy already has any report. Nothing is invented -- no report date,
    signature or central read; unrecognized values stay narrative text."""
    if biopsy.reports.exists():
        return None
    rows, narrative = [], []
    if biopsy.if_pattern:
        code = vocab.LEGACY_IF_MAP.get(biopsy.if_pattern)
        if code:
            rows.append({"section": "if_interpretation", "code": code,
                         "other_label": "See biopsy notes" if code == vocab.OTHER else ""})
        else:
            narrative.append(f"IF (legacy): {biopsy.if_pattern}")
    if biopsy.em_findings:
        code = vocab.LEGACY_EM_MAP.get(biopsy.em_findings)
        if code:
            rows.append({"section": "em", "code": code,
                         "other_label": "See biopsy notes" if code == vocab.OTHER else ""})
        else:
            narrative.append(f"EM (legacy): {biopsy.em_findings}")
    if not rows and not narrative:
        return None
    dx = getattr(biopsy, "diagnosis", None) if hasattr(biopsy, "diagnosis") else None
    report = PathologyReport.objects.create(
        biopsy=biopsy, role="local", revision=1,
        origin=PathologyReport.Origin.LEGACY,
        status=PathologyReport.Status.FINAL, specimen_date=biopsy.biopsy_date,
        primary_diagnosis=(dx.diagnosis if dx else ""),
        comment="\n".join(narrative), scores=score_snapshot(biopsy),
        revision_reason="Converted from legacy single-choice IF/EM fields")
    for i, row in enumerate(rows):
        legacy_value = biopsy.if_pattern if row["section"] == "if_interpretation" else biopsy.em_findings
        PathologyFinding.objects.create(
            report=report, origin=PathologyFinding.Origin.LEGACY,
            legacy_value=legacy_value, sort_order=i, **row)
    return report


def emit_report_changed(biopsy, report=None):
    """One event for the complete aggregate, after the transaction commits
    (the Biopsy post_save fires before its diagnosis and scores exist)."""
    from events import event_types as et
    from events.dispatcher import dispatch_on_commit
    dispatch_on_commit(
        et.PATHOLOGY_REPORT_CHANGED, key=f"biopsy:{biopsy.pk}",
        source_model="pathology.Biopsy", source_pk=str(biopsy.pk),
        payload={"patient_id": str(biopsy.patient_id), "biopsy_id": biopsy.pk,
                 "report_id": getattr(report, "pk", None)})
