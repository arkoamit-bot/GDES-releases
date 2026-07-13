"""
Inter-observer agreement (protocol §11.3) — Cohen's kappa between the local and
central pathology reads across all dual-reviewed biopsies, for the key diagnoses
and scores. Pure-Python, dependency-free, consistent with the analytics layer.
"""
from __future__ import annotations

from collections import Counter

from pathology.models import Biopsy, PathologyReview

Role = PathologyReview.Role


def cohens_kappa(pairs):
    """Unweighted Cohen's kappa for a list of (rater1, rater2) categorical pairs.
    Returns None if there are no usable pairs."""
    pairs = [(a, b) for a, b in pairs if a not in (None, "") and b not in (None, "")]
    n = len(pairs)
    if n == 0:
        return None
    labels = sorted(set(a for a, _ in pairs) | set(b for _, b in pairs), key=str)
    po = sum(1 for a, b in pairs if a == b) / n
    c1 = Counter(a for a, _ in pairs)
    c2 = Counter(b for _, b in pairs)
    pe = sum((c1[l] / n) * (c2[l] / n) for l in labels)
    if pe >= 1.0:                      # only one label used -> perfect by definition
        return 1.0
    return round((po - pe) / (1 - pe), 4)


def _pairs(reviews, field):
    out = []
    for local, central in reviews:
        out.append((getattr(local, field), getattr(central, field)))
    return out


def interobserver_agreement(biopsies=None):
    """Kappa for each key field across biopsies that have both a local and a
    central read. Returns per-field kappa, n, and overall diagnosis agreement."""
    biopsies = biopsies if biopsies is not None else Biopsy.objects.all()
    reviews = []
    for b in biopsies.prefetch_related("reviews"):
        local = next((r for r in b.reviews.all() if r.role == Role.LOCAL), None)
        central = next((r for r in b.reviews.all() if r.role == Role.CENTRAL), None)
        if local and central:
            reviews.append((local, central))

    n = len(reviews)
    fields = {}
    for f in PathologyReview.KEY_FIELDS:
        pairs = _pairs(reviews, f)
        usable = [(a, b) for a, b in pairs if a not in (None, "") or b not in (None, "")]
        if usable:
            fields[f] = {"kappa": cohens_kappa(pairs), "n_pairs": len(usable)}

    diag_pairs = _pairs(reviews, "diagnosis")
    diag_agree = (sum(1 for a, b in diag_pairs if a == b) / n) if n else None
    return {
        "n_dual_reviewed": n,
        "diagnosis_agreement_pct": round(diag_agree * 100, 1) if diag_agree is not None else None,
        "kappa_by_field": fields,
    }
