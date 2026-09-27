"""Celery tasks for async event dispatch."""
from __future__ import annotations

import logging

from bgddr.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def dispatch_event_task(self, event_type, source_model, source_pk, payload):
    """Async task that runs registered handlers for an event.

    ``_run_handlers`` reports failures rather than raising, so the retry has to
    be driven from its return value — otherwise a failed recompute was logged
    and then silently dropped with the event left unprocessed forever.
    """
    from .dispatcher import _run_handlers, mark_event_processed
    failures = _run_handlers(event_type, source_model, source_pk, payload)
    if failures:
        names = ", ".join(name for name, _ in failures)
        logger.error(
            "Async dispatch failed for event %s (%d handler(s) failed: %s)",
            event_type, len(failures), names)
        mark_event_processed(event_type, source_model, source_pk, processed=False)
        raise self.retry(exc=RuntimeError(f"handler(s) failed: {names}"))
    mark_event_processed(event_type, source_model, source_pk, processed=True)
