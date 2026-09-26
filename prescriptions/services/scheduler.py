"""Background scheduler - periodically refreshes the drug catalogue.

Mirrors `feedback.services.scheduler`: a daemon thread that calls
`should_sync_now()` and sleeps in short increments so shutdown stays
responsive. Started from `desktop/launcher.py` for the single-user Windows
build, where no celery worker or redis broker is running.
"""
from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger("bgddr.drug_sync")

_scheduler_thread: threading.Thread | None = None
_stop_event = threading.Event()

# The scrape takes ~6 minutes; sleep in 60s slices so _stop_event is
# honoured promptly when the launcher shuts down.
_TICK_SECONDS = 60


def _scheduler_loop():
    from .services.medex_sync import run_sync, should_sync_now

    while not _stop_event.is_set():
        try:
            if should_sync_now():
                logger.info("Scheduled MedEx drug sync starting ...")
                summary = run_sync(trigger="scheduled")
                logger.info("Scheduled MedEx drug sync complete: %s",
                            summary.get("state"))
        except Exception:
            # A failed sync must never kill the thread; the DrugSyncRun row
            # already carries the error and the next tick retries.
            logger.exception("MedEx drug sync scheduler error")

        for _ in range(_TICK_SECONDS):
            if _stop_event.is_set():
                return
            time.sleep(1)


def start_scheduler() -> None:
    """Start the drug-sync scheduler. Safe to call multiple times."""
    global _scheduler_thread
    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        return
    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop, daemon=True, name="bgddr-drug-sync",
    )
    _scheduler_thread.start()
    logger.info("Drug sync scheduler started")


def stop_scheduler() -> None:
    """Signal the scheduler thread to exit (used on shutdown/tests)."""
    _stop_event.set()
