"""Error deduplication — fingerprints exceptions so identical errors
are merged into a single ErrorOccurrence with an incremented count."""
from __future__ import annotations

import hashlib
import logging
import platform
import traceback

from django.db import transaction
from django.utils import timezone

from bgddr.version import __version__ as app_version

logger = logging.getLogger(__name__)


def _de_parameterize_stack(stack: str) -> str:
    """Normalize a stack trace so different parameter values for the same
    code path produce the same hash (e.g. patient IDs in URLs)."""
    import re
    # Replace numeric IDs in function args and URLs
    normalized = re.sub(r"\b\d{3,}\b", "N", stack)
    # Replace UUIDs
    normalized = re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                        "UUID", normalized, flags=re.IGNORECASE)
    # Replace hex strings (hashes)
    normalized = re.sub(r"\b[0-9a-f]{16,}\b", "HASH", normalized, flags=re.IGNORECASE)
    return normalized


def _compute_fingerprint(exc_type: str, module: str, line_number: int | None,
                         stack: str) -> str:
    """Unique fingerprint: SHA-256 of (exception_type + module + line + stack_hash)."""
    deparam = _de_parameterize_stack(stack)
    stack_hash = hashlib.sha256(deparam.encode("utf-8")).hexdigest()[:32]
    raw = f"{exc_type}|{module}|{line_number or 0}|{stack_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def _compute_stack_hash(stack: str) -> str:
    deparam = _de_parameterize_stack(stack)
    return hashlib.sha256(deparam.encode("utf-8")).hexdigest()[:32]


def _extract_module_line(stack: str) -> tuple[str, str, int | None]:
    """Parse the stack trace to find the originating module, function, and line."""
    for line in stack.strip().splitlines():
        line = line.strip()
        if line.startswith("File ") and line.endswith(", line"):
            continue
        if line.startswith('File "'):
            import re
            m = re.search(r'File "(.+?)", line (\d+), in (.+)', line)
            if m:
                filepath = m.group(1)
                lineno = int(m.group(2))
                func = m.group(3)
                # Extract module name from filepath
                parts = filepath.replace("\\", "/").split("/")
                # Skip standard library and site-packages
                module = parts[-1] if parts else filepath
                # Find the "in <module>" or last meaningful function
                return module, func, lineno
    return "", "", None


def record_error(exc_type: str, exc_message: str, stack_trace: str,
                 severity: str = "error", context: dict | None = None) -> None:
    """Record an error, deduplicating against existing occurrences.

    This is the primary entry point — called by the middleware, exception hook,
    and management command. Thread-safe via transaction.atomic + get_or_create.
    """
    from feedback.models import ErrorOccurrence, TelemetrySettings

    settings_obj = TelemetrySettings.load()
    if not settings_obj.enabled:
        return

    module, function_name, line_number = _extract_module_line(stack_trace)
    fingerprint = _compute_fingerprint(exc_type, module, line_number, stack_trace)
    stack_hash = _compute_stack_hash(stack_trace)

    try:
        with transaction.atomic():
            occ, created = ErrorOccurrence.objects.select_for_update().get_or_create(
                fingerprint=fingerprint,
                defaults={
                    "exception_type": exc_type,
                    "exception_message": exc_message[:2000],
                    "module": module,
                    "function_name": function_name,
                    "line_number": line_number,
                    "stack_trace": stack_trace[:10000],
                    "stack_hash": stack_hash,
                    "severity": severity,
                    "occurrence_count": 1,
                    "first_seen": timezone.now(),
                    "last_seen": timezone.now(),
                    "queue_state": "pending",
                    "app_version": app_version,
                    "os_version": platform.platform(),
                    "python_version": platform.python_version(),
                    "sample_context": context,
                },
            )
            if not created:
                occ.occurrence_count += 1
                occ.last_seen = timezone.now()
                if context:
                    occ.sample_context = context
                occ.save(update_fields=[
                    "occurrence_count", "last_seen", "sample_context",
                ])
    except Exception as exc:
        logger.warning("Failed to record error occurrence: %s", exc)
