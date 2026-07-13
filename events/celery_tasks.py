"""Celery tasks for async event dispatch."""
from __future__ import annotations

import logging

from bgddr.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def dispatch_event_task(self, event_type, source_model, source_pk, payload):
    """Async task that runs registered handlers for an event."""
    from .dispatcher import _run_handlers
    try:
        _run_handlers(event_type, source_model, source_pk, payload)
    except Exception as exc:
        logger.exception("Async dispatch failed for event %s", event_type)
        raise self.retry(exc=exc)
