"""Global exception hook — captures unhandled exceptions that occur
outside of Django's request/response cycle (e.g. during launcher startup,
background threads, management commands)."""
from __future__ import annotations

import logging
import sys
import threading
import traceback

logger = logging.getLogger(__name__)

_original_excepthook = sys.excepthook
_installed = False


def _gdes_excepthook(exc_type, exc_value, exc_tb):
    """Custom excepthook that records errors to the feedback system."""
    if exc_type is KeyboardInterrupt or exc_type is SystemExit:
        return _original_excepthook(exc_type, exc_value, exc_tb)

    try:
        stack = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        from feedback.services.deduplicator import record_error
        from feedback.services.sanitizer import sanitize_stack_trace

        record_error(
            exc_type=exc_type.__name__ if exc_type else "Unknown",
            exc_message=str(exc_value)[:2000],
            stack_trace=sanitize_stack_trace(stack),
            severity="critical",
        )
    except Exception:
        pass  # Never let error reporting crash the app

    return _original_excepthook(exc_type, exc_value, exc_tb)


def _thread_excepthook(args):
    """Handler for threading.excepthook (Python 3.8+)."""
    try:
        stack = "".join(traceback.format_exception(
            args.exc_type, args.exc_value, args.exc_traceback,
        ))
        from feedback.services.deduplicator import record_error
        from feedback.services.sanitizer import sanitize_stack_trace

        record_error(
            exc_type=args.exc_type.__name__ if args.exc_type else "Unknown",
            exc_message=str(args.exc_value)[:2000],
            stack_trace=sanitize_stack_trace(stack),
            severity="critical",
        )
    except Exception:
        pass


def install_hook() -> None:
    """Install the global exception hook. Safe to call multiple times."""
    global _installed
    if _installed:
        return
    sys.excepthook = _gdes_excepthook
    threading.excepthook = _thread_excepthook
    _installed = True
    logger.info("Global exception hook installed")
