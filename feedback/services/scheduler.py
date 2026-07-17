"""Background scheduler — periodically checks for pending errors and uploads."""
from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)

_scheduler_thread: threading.Thread | None = None
_stop_event = threading.Event()


def _scheduler_loop():
    """Background loop that runs the upload on the configured schedule."""
    from feedback.services.uploader import should_sync_now, run_upload

    while not _stop_event.is_set():
        try:
            if should_sync_now():
                logger.info("Scheduled error upload starting ...")
                result = run_upload(trigger="scheduled")
                logger.info("Scheduled upload complete: %s", result)
        except Exception as exc:
            logger.exception("Scheduler error: %s", exc)

        # Sleep in small increments so stop_event is responsive
        for _ in range(60):  # 60 seconds between checks
            if _stop_event.is_set():
                return
            time.sleep(1)


def start_scheduler() -> None:
    """Start the background upload scheduler. Safe to call multiple times."""
    global _scheduler_thread
    if _scheduler_thread is not None and _scheduler_thread.is_alive():
        return
    _stop_event.clear()
    _scheduler_thread = threading.Thread(
        target=_scheduler_loop, daemon=True, name="gdes-error-scheduler",
    )
    _scheduler_thread.start()
    logger.info("Error reporting scheduler started")


def stop_scheduler() -> None:
    """Signal the scheduler to stop."""
    _stop_event.set()
    logger.info("Error reporting scheduler stopped")
