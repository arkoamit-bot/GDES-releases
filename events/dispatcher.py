"""Event dispatcher — lightweight in-process pub/sub for domain events.

Usage:
    from events.dispatcher import dispatch, subscribe, mark_async

    subscribe("patient.registered", my_handler)
    dispatch("patient.registered", source_model="Patient", source_pk="42", payload={"name": "..."})

    mark_async("lab.result.created")  # Routes via Celery when broker is available

Handlers receive (event_type, source_model, source_pk, payload).
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from django.conf import settings

logger = logging.getLogger(__name__)

# In-process handler registry: event_type -> list of handler functions
_handlers: dict[str, list[Callable]] = {}

# Event types that should be dispatched asynchronously via Celery
_async_event_types: set[str] = set()


def subscribe(event_type: str, handler: Callable) -> None:
    """Register a callable handler for a domain event type."""
    _handlers.setdefault(event_type, []).append(handler)


def unsubscribe(event_type: str, handler: Callable) -> None:
    """Remove a previously registered handler."""
    handlers = _handlers.get(event_type, [])
    if handler in handlers:
        handlers.remove(handler)


def mark_async(event_type: str) -> None:
    """Mark an event type for asynchronous dispatch via Celery."""
    _async_event_types.add(event_type)


def _persist_event(event_type, source_model, source_pk, payload):
    try:
        from .models import Event
        return Event.objects.create(
            event_type=event_type,
            source_model=source_model,
            source_pk=source_pk,
            payload=payload,
        )
    except Exception:
        logger.exception("Failed to persist event %s", event_type)
        return None


def _run_handlers(event_type, source_model, source_pk, payload):
    """Run every handler for ``event_type``.

    Returns the list of ``(handler_name, exception)`` failures instead of
    swallowing them: callers need to know that a recompute was lost so the event
    stays unprocessed and can be retried.
    """
    failures = []
    for handler in _handlers.get(event_type, []):
        try:
            handler(
                event_type=event_type,
                source_model=source_model,
                source_pk=source_pk,
                payload=payload,
            )
        except Exception as exc:
            failures.append((getattr(handler, "__name__", repr(handler)), exc))
            logger.exception(
                "Handler %s failed for event %s", handler.__name__, event_type
            )
    return failures


def mark_event_processed(event_type, source_model="", source_pk="", processed=True):
    """Set ``Event.processed`` on the newest matching event row.

    Separate from ``dispatch`` because an async event is persisted by the
    publishing process but only marked by the Celery worker that runs it.
    """
    try:
        from .models import Event
        qs = Event.objects.filter(event_type=event_type)
        if source_model:
            qs = qs.filter(source_model=source_model)
        if source_pk:
            qs = qs.filter(source_pk=str(source_pk))
        event = qs.order_by("-occurred_at", "-id").first()
        if event is not None and event.processed != processed:
            event.processed = processed
            event.save(update_fields=["processed"])
    except Exception:
        logger.exception("Failed to mark event %s processed=%s", event_type, processed)


def _celery_available() -> bool:
    return bool(getattr(settings, "CELERY_BROKER_URL", None)) or \
           bool(getattr(settings, "REDIS_URL", None))


def dispatch_on_commit(event_type: str, *, key: str, source_model: str = "",
                       source_pk: str = "", payload: dict[str, Any] | None = None) -> None:
    """Dispatch once, after the surrounding transaction commits.

    For aggregates saved in several steps (a biopsy, its diagnosis, its score
    panels and report): each step asks for the event, one is sent, and only
    once the whole aggregate is visible to handlers. Outside a transaction it
    runs immediately. ``key`` identifies the aggregate: a second request for
    the same event and key within the same transaction is dropped. A rollback
    discards the pending callback with the transaction.
    """
    from django.db import transaction

    token = (event_type, key)
    conn = transaction.get_connection()
    if conn.in_atomic_block and any(
            getattr(entry[1], "_event_token", None) == token
            for entry in conn.run_on_commit):
        return

    def _send():
        dispatch(event_type, source_model=source_model, source_pk=source_pk,
                 payload=payload)

    _send._event_token = token
    transaction.on_commit(_send)


def dispatch(
    event_type: str,
    *,
    source_model: str = "",
    source_pk: str = "",
    payload: dict[str, Any] | None = None,
) -> None:
    """Dispatch a domain event to all registered handlers.

    If the event type is marked async and Celery is configured, the dispatch
    happens in a background worker. Otherwise it runs in-process.

    Either way the persisted :class:`~events.models.Event` row is marked
    ``processed`` only when every handler succeeded, so a transient failure
    leaves a visible unprocessed event instead of a silently stale profile.
    """
    payload = payload or {}
    event = _persist_event(event_type, source_model, source_pk, payload)

    if event_type in _async_event_types and _celery_available():
        try:
            from .celery_tasks import dispatch_event_task
            dispatch_event_task.delay(event_type, source_model, source_pk, payload)
            return
        except Exception:
            logger.warning("Celery dispatch failed, falling back to in-process for %s", event_type)

    failures = _run_handlers(event_type, source_model, source_pk, payload)
    if event is not None:
        try:
            event.processed = not failures
            event.save(update_fields=["processed"])
        except Exception:
            logger.exception("Failed to mark event %s processed", event_type)
