"""
Thread-local "who is acting" context, so the audit recorder can attribute every
change to a user without threading the request through every call site.

Set automatically per web request by AuditMiddleware; set manually in scripts /
management commands via the ``acting_as`` context manager.
"""
from __future__ import annotations

import contextlib
import threading

_state = threading.local()


def set_actor(user=None, reason: str = ""):
    _state.user = user
    _state.reason = reason


def clear_actor():
    _state.user = None
    _state.reason = ""


def current_actor():
    return getattr(_state, "user", None)


def current_reason():
    return getattr(_state, "reason", "")


@contextlib.contextmanager
def acting_as(user=None, reason: str = ""):
    """Use in shells / management commands / data migrations:

        with acting_as(some_user, reason="bulk correction"):
            patient.save()
    """
    prev_user = current_actor()
    prev_reason = current_reason()
    set_actor(user, reason)
    try:
        yield
    finally:
        set_actor(prev_user, prev_reason)
