"""Upload service — processes the error queue and pushes to GitHub."""
from __future__ import annotations

import logging
import platform
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from bgddr.version import __version__ as app_version

logger = logging.getLogger(__name__)

# Max upload attempts before marking as failed permanently
MAX_UPLOAD_ATTEMPTS = 5


def _is_internet_available() -> bool:
    """Quick connectivity check."""
    import urllib.request
    try:
        urllib.request.urlopen("https://api.github.com", timeout=5)
        return True
    except Exception:
        return False


def _get_pending_occurrences():
    """Get errors ready for upload — pending with limited retry count."""
    from feedback.models import ErrorOccurrence
    return ErrorOccurrence.objects.filter(
        queue_state="pending",
        upload_fail_count__lt=MAX_UPLOAD_ATTEMPTS,
    ).order_by("-severity", "-occurrence_count")[:50]


def _get_critical_occurrences():
    """Get critical errors that need immediate upload."""
    from feedback.models import ErrorOccurrence
    return ErrorOccurrence.objects.filter(
        queue_state="pending",
        severity="critical",
        upload_fail_count__lt=MAX_UPLOAD_ATTEMPTS,
    ).order_by("-last_seen")


def run_upload(trigger: str = "scheduled") -> dict:
    """Process the error queue and upload to GitHub.

    Returns a summary dict with counts.
    """
    from feedback.models import UploadBatch, TelemetrySettings
    from feedback.services.github import create_or_update_issue

    settings_obj = TelemetrySettings.load()
    summary = {
        "uploaded": 0, "failed": 0, "skipped": 0,
        "trigger": trigger, "started_at": timezone.now(),
    }

    if not settings_obj.enabled:
        summary["skipped_reason"] = "telemetry_disabled"
        return summary

    batch = UploadBatch.objects.create(trigger=trigger)
    log_lines = []

    try:
        if not settings_obj.github_token:
            msg = "No GitHub token configured — skipping upload."
            log_lines.append(msg)
            logger.warning(msg)
            batch.log_output = "\n".join(log_lines)
            batch.state = "failed"
            batch.finished_at = timezone.now()
            batch.save()
            return summary

        if not _is_internet_available():
            msg = "No internet connectivity — will retry later."
            log_lines.append(msg)
            logger.info(msg)
            batch.log_output = "\n".join(log_lines)
            batch.state = "failed"
            batch.finished_at = timezone.now()
            batch.save()
            summary["skipped_reason"] = "offline"
            return summary

        repo = settings_obj.github_repo
        token = settings_obj.github_token

        # Process critical errors first, then regular pending
        all_occurrences = list(_get_critical_occurrences()) + list(_get_pending_occurrences())
        # Deduplicate the combined list (critical may overlap with pending)
        seen_fps = set()
        unique = []
        for occ in all_occurrences:
            if occ.fingerprint not in seen_fps:
                seen_fps.add(occ.fingerprint)
                unique.append(occ)

        for occ in unique:
            try:
                result = create_or_update_issue(occ, repo, token)
                if result:
                    occ.queue_state = "uploaded"
                    occ.save(update_fields=["queue_state"])
                    summary["uploaded"] += 1
                    log_lines.append(f"OK: {occ.fingerprint[:12]} → issue #{occ.github_issue_number}")
                else:
                    occ.queue_state = "failed"
                    occ.save(update_fields=["queue_state"])
                    summary["failed"] += 1
                    log_lines.append(f"FAIL: {occ.fingerprint[:12]} (no response)")
            except Exception as exc:
                summary["failed"] += 1
                log_lines.append(f"ERROR: {occ.fingerprint[:12]} — {exc}")
                logger.exception("Upload failed for %s", occ.fingerprint[:12])

        # Mark permanently failed ones
        permanently_failed = _get_pending_occurrences().filter(
            upload_fail_count__gte=MAX_UPLOAD_ATTEMPTS,
        )
        count = permanently_failed.update(queue_state="failed")
        if count:
            summary["skipped"] = count
            log_lines.append(f"Permanently failed: {count} occurrences")

        # Update settings
        settings_obj.last_upload = timezone.now()
        settings_obj.pending_count = _get_pending_occurrences().count()
        settings_obj.save(update_fields=["last_upload", "pending_count"])

        batch.state = "success" if summary["failed"] == 0 else "partial"
    except Exception as exc:
        batch.state = "failed"
        log_lines.append(f"FATAL: {exc}")
        logger.exception("Upload batch failed")
    finally:
        batch.finished_at = timezone.now()
        batch.errors_uploaded = summary["uploaded"]
        batch.errors_failed = summary["failed"]
        batch.errors_skipped = summary["skipped"]
        batch.log_output = "\n".join(log_lines)
        batch.save()

    summary["finished_at"] = timezone.now()
    return summary


def should_sync_now() -> bool:
    """Check if it's time to sync based on the configured interval."""
    from feedback.models import TelemetrySettings

    settings_obj = TelemetrySettings.load()
    if not settings_obj.enabled:
        return False
    if settings_obj.sync_interval == "manual":
        return False

    last = settings_obj.last_upload
    if not last:
        return True

    interval_map = {
        "hourly": timedelta(hours=1),
        "6h": timedelta(hours=6),
        "daily": timedelta(hours=24),
        "weekly": timedelta(hours=168),
    }
    delta = interval_map.get(settings_obj.sync_interval, timedelta(hours=24))
    return timezone.now() - last >= delta


def upload_critical_now(exc_type: str, message: str, stack: str,
                        context: dict | None = None) -> None:
    """Immediately record and upload a critical error (bypasses schedule)."""
    from feedback.services.deduplicator import record_error
    from feedback.models import ErrorOccurrence

    record_error(exc_type, message, stack, severity="critical", context=context)

    # Find the just-recorded occurrence and force-upload
    fingerprint = None
    from feedback.services.deduplicator import _compute_fingerprint, _extract_module_line
    module, func, line = _extract_module_line(stack)
    fingerprint = _compute_fingerprint(exc_type, module, line, stack)

    try:
        occ = ErrorOccurrence.objects.get(fingerprint=fingerprint)
        occ.queue_state = "pending"
        occ.severity = "critical"
        occ.save(update_fields=["queue_state", "severity"])
    except ErrorOccurrence.DoesNotExist:
        return

    run_upload(trigger="critical")
