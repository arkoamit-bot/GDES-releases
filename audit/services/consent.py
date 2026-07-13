"""
Consent lifecycle — grant (with versioning), withdraw, and query.

Granting a new consent of a type supersedes the previous current one (forming a
version chain) so you always know which ICF version a patient is under, and can
reconstruct the history. ``has_consent`` is the gate to call before any action
that needs it (e.g. biobank sampling, genetic testing).
"""
from __future__ import annotations

import datetime as dt

from django.db import transaction

from audit.models import Consent


def current_consent(patient, consent_type):
    return Consent.objects.filter(
        patient=patient, consent_type=consent_type, is_current=True).first()


def has_consent(patient, consent_type) -> bool:
    c = current_consent(patient, consent_type)
    return bool(c and c.is_active)


@transaction.atomic
def grant_consent(patient, consent_type, form_version, *, consent_date=None,
                  obtained_by=None, scope="", document=None, notes=""):
    consent_date = consent_date or dt.date.today()
    prev = current_consent(patient, consent_type)
    if prev:
        prev.is_current = False
        prev.save(update_fields=["is_current", "updated_at"])
    new = Consent.objects.create(
        patient=patient, consent_type=consent_type, form_version=form_version,
        status=Consent.Status.GRANTED, consent_date=consent_date,
        obtained_by=obtained_by, scope=scope, notes=notes,
        supersedes=prev, is_current=True)
    if document:
        new.document = document
        new.save(update_fields=["document"])
    return new


@transaction.atomic
def withdraw_consent(patient, consent_type, *, withdrawn_date=None, notes=""):
    cur = current_consent(patient, consent_type)
    if cur is None:
        return None
    cur.status = Consent.Status.WITHDRAWN
    cur.withdrawn_date = withdrawn_date or dt.date.today()
    if notes:
        cur.notes = notes
    cur.save(update_fields=["status", "withdrawn_date", "notes", "updated_at"])
    return cur


def consent_history(patient, consent_type=None):
    qs = Consent.objects.filter(patient=patient)
    if consent_type:
        qs = qs.filter(consent_type=consent_type)
    return qs.order_by("consent_type", "-consent_date")
