"""
Central pathology review workflow (protocol §7.3).

Every index biopsy gets a LOCAL read and a mandatory CENTRAL expert read. The two
are compared field-by-field; if they disagree the biopsy is flagged DISCORDANT
and resolved by an ADJUDICATION (consensus) read. The authoritative (final) read
then writes the biopsy's GNDiagnosis / IgANScore.
"""
from __future__ import annotations

import datetime as dt

from django.db import transaction

from pathology.models import (Biopsy, GNDiagnosis, IgANScore, PathologyReview)

Role = PathologyReview.Role
Status = Biopsy.ReviewStatus


def _get(biopsy, role):
    return biopsy.reviews.filter(role=role).first()


@transaction.atomic
def submit_review(biopsy, role, *, diagnosis, broad_group="", reviewer=None,
                  review_date=None, mest=None, isn_rps_class="", fsgs_variant="",
                  notes=""):
    """Record (or update) one read. ``mest`` is an optional dict M/E/S/T/C."""
    mest = mest or {}
    PathologyReview.objects.update_or_create(
        biopsy=biopsy, role=role,
        defaults=dict(
            diagnosis=diagnosis, broad_group=broad_group, reviewer=reviewer,
            review_date=review_date or dt.date.today(),
            mest_m=mest.get("M"), mest_e=mest.get("E"), mest_s=mest.get("S"),
            mest_t=mest.get("T"), mest_c=mest.get("C"),
            isn_rps_class=isn_rps_class, fsgs_variant=fsgs_variant, notes=notes))
    return _recompute_status(biopsy)


def concordance(biopsy):
    """Compare the LOCAL and CENTRAL reads. Returns None if both not present."""
    local, central = _get(biopsy, Role.LOCAL), _get(biopsy, Role.CENTRAL)
    if not (local and central):
        return None
    diffs = []
    for f in PathologyReview.KEY_FIELDS:
        lv, cv = getattr(local, f), getattr(central, f)
        # Skip fields neither reviewer recorded.
        if (lv in (None, "")) and (cv in (None, "")):
            continue
        if lv != cv:
            diffs.append({"field": f, "local": lv, "central": cv})
    return {"concordant": not diffs, "discordant_fields": diffs}


@transaction.atomic
def _recompute_status(biopsy):
    local, central, adj = (_get(biopsy, Role.LOCAL), _get(biopsy, Role.CENTRAL),
                           _get(biopsy, Role.ADJUDICATION))
    if adj:
        status = Status.ADJUDICATED
    elif local and central:
        status = Status.CONCORDANT if concordance(biopsy)["concordant"] else Status.DISCORDANT
    elif local:
        status = Status.AWAITING_CENTRAL
    else:
        status = Status.PENDING
    biopsy.review_status = status
    biopsy.save(update_fields=["review_status"])
    if status in (Status.CONCORDANT, Status.ADJUDICATED):
        _finalize(biopsy)
    return status


def adjudicate(biopsy, *, diagnosis, broad_group="", reviewer=None, mest=None,
               isn_rps_class="", fsgs_variant="", notes=""):
    """Consensus resolution of a discordant biopsy."""
    return submit_review(biopsy, Role.ADJUDICATION, diagnosis=diagnosis,
                         broad_group=broad_group, reviewer=reviewer, mest=mest,
                         isn_rps_class=isn_rps_class, fsgs_variant=fsgs_variant,
                         notes=notes)


@transaction.atomic
def _finalize(biopsy):
    """Mark the authoritative read final and write the biopsy's GNDiagnosis /
    IgANScore from it. Priority: adjudication > central > local."""
    read = (_get(biopsy, Role.ADJUDICATION) or _get(biopsy, Role.CENTRAL)
            or _get(biopsy, Role.LOCAL))
    if not read:
        return
    biopsy.reviews.update(is_final=False)
    PathologyReview.objects.filter(pk=read.pk).update(is_final=True)

    GNDiagnosis.objects.update_or_create(
        biopsy=biopsy,
        defaults=dict(diagnosis=read.diagnosis, broad_group=read.broad_group))
    if any(getattr(read, f) is not None for f in ("mest_m", "mest_e", "mest_s", "mest_t", "mest_c")):
        IgANScore.objects.update_or_create(
            biopsy=biopsy,
            defaults=dict(M=read.mest_m, E=read.mest_e, S=read.mest_s,
                          T=read.mest_t, C=read.mest_c))
