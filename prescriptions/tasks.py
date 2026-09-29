"""Celery tasks for the drug catalogue."""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger("bgddr.drug_sync")


@shared_task(name="prescriptions.tasks.sync_medex_drugs")
def sync_medex_drugs():
    """Refresh DrugMaster from medex.com.bd/brands (celery beat, weekly).

    Returns the summary dict so the result backend keeps an audit trail; a
    failure is re-raised after the DrugSyncRun row has recorded it, so beat
    shows a non-zero status instead of silently reporting success.
    """
    from .services.medex_sync import run_sync

    try:
        return run_sync(trigger="scheduled")
    except Exception as exc:
        logger.error("MedEx drug sync failed: %s", exc)
        raise
