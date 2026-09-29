"""Cross-field consistency rules for one biopsy, shared by every write path.

The biopsy form, the report amendment, the API and the admin all store the
same related facts: crescents present/absent, the crescent percentage, the
crescentic-glomeruli count, Oxford C, and the diagnostic-yield category. Each
rule here states a contradiction by definition only -- no score threshold is
guessed and nothing is derived:

*   Crescents: a positive percentage or count means crescents were seen, so
    it cannot be saved as "absent" or "not assessed"; "present" cannot carry
    0 % or a count of 0. An unknown percentage stays unknown (None), never 0.
*   Oxford C: C0 means no crescents; C1/C2 mean crescents were seen. The
    C1/C2 boundary is not checked here.
*   Result category (patients.workflow.BiopsyResult): positive = a specific
    GN diagnosis, negative = no specific GN, inconclusive = inadequate. Only
    labels that say so explicitly are checked; a diagnosis whose GN status is
    not stated by its label is left to the clinician.

Each function returns [(target, field, message)], where target names the form
the field belongs to: "bx" (Biopsy), "rp" (PathologyReport), "igan"
(IgANScore) or "dx" (GNDiagnosis).
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from . import diagnosis as dxrules


def _num(value):
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _fmt(value) -> str:
    return f"{value:g}" if isinstance(value, Decimal) else str(value)


def crescent_errors(present, pct, *, count=None, oxford_c=None):
    """present: True / False / None (not assessed). pct, count, oxford_c may
    be None (not stated)."""
    out = []
    pct, count = _num(pct), _num(count)
    if pct is not None and pct > 0 and present is not True:
        state = "absent" if present is False else "not assessed"
        out.append(("bx", "crescents_present",
                    f"Crescents are recorded in {_fmt(pct)}% of glomeruli but marked "
                    f"{state}. Set Crescents to Present, or correct the percentage."))
    if count is not None and count > 0 and present is False:
        out.append(("bx", "crescents_present",
                    f"The report counts {_fmt(count)} crescentic glomeruli but crescents "
                    "are marked absent. Set Crescents to Present, or correct the count."))
    if present is True and pct is not None and pct == 0:
        out.append(("bx", "crescent_pct",
                    "Crescents are marked present but the percentage is 0. Enter the "
                    "reported percentage, or leave it blank if it was not reported."))
    if present is True and count is not None and count == 0:
        out.append(("rp", "crescentic_glomeruli",
                    "Crescents are marked present but 0 crescentic glomeruli are counted. "
                    "Enter the count, or leave it blank if it was not reported."))
    if oxford_c is not None:
        seen = (present is True or (pct is not None and pct > 0)
                or (count is not None and count > 0))
        if oxford_c == 0 and seen:
            out.append(("igan", "C",
                        "Oxford C0 means no crescents, but crescents are recorded above. "
                        "Correct the C score or the crescent entries."))
        if oxford_c in (1, 2) and present is False:
            out.append(("igan", "C",
                        f"Oxford C{oxford_c} means crescents were seen, but crescents are "
                        "marked absent above. Correct the C score or the crescent entries."))
    return out


# Diagnoses whose label states that there is no GN.
NO_GN_DIAGNOSES = frozenset({
    "Diabetic kidney disease only - no GN",
    "Hypertensive nephrosclerosis only - no GN",
})
# Families whose diagnoses are, by label, a specific glomerular disease.
GN_FAMILIES = frozenset({dxrules.IGAN, dxrules.LUPUS, dxrules.FSGS, dxrules.MN,
                         dxrules.MCD, dxrules.ANCA, dxrules.ANTI_GBM, dxrules.C3G})


def result_category_errors(result, diagnosis, adequacy, *, report_status=""):
    """The diagnostic-yield category must agree with the diagnosis, the
    adequacy and the report status it is based on. It is never inferred."""
    from patients.workflow import BiopsyResult
    from .models import Biopsy, PathologyReport

    out = []
    if not result:
        return out
    diagnosis = dxrules.canonical(diagnosis or "")
    fam = dxrules.family(diagnosis)
    unfinished = report_status in (PathologyReport.Status.DRAFT, PathologyReport.Status.PENDING,
                                   PathologyReport.Status.INADEQUATE)
    if result == BiopsyResult.POSITIVE:
        if not diagnosis:
            out.append(("bx", "result_category",
                        "Positive means a specific GN diagnosis. Record the diagnosis, or "
                        "leave the result blank until it is known."))
        elif diagnosis in NO_GN_DIAGNOSES:
            out.append(("bx", "result_category",
                        f"'{diagnosis}' states there is no GN, so the result cannot be positive."))
    elif result == BiopsyResult.NEGATIVE:
        if fam in GN_FAMILIES and diagnosis not in NO_GN_DIAGNOSES:
            out.append(("bx", "result_category",
                        f"'{diagnosis}' is a specific GN diagnosis, so the result cannot be "
                        "negative."))
        if adequacy == Biopsy.Adequacy.INADEQUATE:
            out.append(("bx", "result_category",
                        "An inadequate specimen cannot show that there is no GN. Record the "
                        "result as inconclusive."))
    if result in (BiopsyResult.POSITIVE, BiopsyResult.NEGATIVE) and unfinished:
        out.append(("bx", "result_category",
                    f"The report is {report_status}; a positive or negative result needs a "
                    "final or preliminary report. Leave the result blank for now."))
    return out
