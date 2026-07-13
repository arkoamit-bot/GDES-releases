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
        Event.objects.create(
            event_type=event_type,
            source_model=source_model,
            source_pk=source_pk,
            payload=payload,
        )
    except Exception:
        logger.exception("Failed to persist event %s", event_type)


def _run_handlers(event_type, source_model, source_pk, payload):
    for handler in _handlers.get(event_type, []):
        try:
            handler(
                event_type=event_type,
                source_model=source_model,
                source_pk=source_pk,
                payload=payload,
            )
        except Exception:
            logger.exception(
                "Handler %s failed for event %s", handler.__name__, event_type
            )


def _celery_available() -> bool:
    return bool(getattr(settings, "CELERY_BROKER_URL", None)) or \
           bool(getattr(settings, "REDIS_URL", None))


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
    """
    payload = payload or {}
    _persist_event(event_type, source_model, source_pk, payload)

    if event_type in _async_event_types and _celery_available():
        try:
            from .celery_tasks import dispatch_event_task
            dispatch_event_task.delay(event_type, source_model, source_pk, payload)
            return
        except Exception:
            logger.warning("Celery dispatch failed, falling back to in-process for %s", event_type)

    _run_handlers(event_type, source_model, source_pk, payload)
