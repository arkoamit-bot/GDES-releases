"""System diagnostics — collects non-PHI environment information for error reports."""
from __future__ import annotations

import json
import logging
import os
import platform
import sys

from django.conf import settings

from bgddr.version import __version__ as app_version

logger = logging.getLogger(__name__)


def collect_system_info() -> dict:
    """Collect sanitized system information. No PHI is included."""
    info = {
        "app_version": app_version,
        "python_version": platform.python_version(),
        "os_version": platform.platform(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "machine_type": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "hostname_hash": _hash(platform.node()),
        "django_version": _get_django_version(),
        "db_engine": _get_db_engine(),
        "frozen": getattr(sys, "frozen", False),
        "encoding": sys.getdefaultencoding(),
        "filesystem_encoding": sys.getfilesystemencoding(),
    }

    # Memory (best-effort, non-critical)
    try:
        import psutil
        vm = psutil.virtual_memory()
        info["total_memory_mb"] = round(vm.total / (1024 * 1024))
        info["available_memory_mb"] = round(vm.available / (1024 * 1024))
    except ImportError:
        pass

    return info


def collect_request_context(request=None) -> dict:
    """Collect sanitized request context. Strips all PHI."""
    if request is None:
        return {}

    ctx = {
        "method": getattr(request, "method", ""),
        "path": getattr(request, "path", ""),
        "url": getattr(request, "build_absolute_uri", lambda: "")(),
        "user_agent": str(request.META.get("HTTP_USER_AGENT", ""))[:200],
    }

    if hasattr(request, "resolver_match") and request.resolver_match:
        ctx["view_name"] = request.resolver_match.view_name or ""
        ctx["url_name"] = request.resolver_match.url_name or ""

    if hasattr(request, "session"):
        ctx["workflow"] = request.session.get("current_workflow", "")

    if request.user and request.user.is_authenticated:
        ctx["user_role"] = getattr(request.user, "role", "unknown")

    # Strip PHI from the context
    from feedback.services.sanitizer import sanitize
    return sanitize(ctx)


def _get_django_version() -> str:
    try:
        import django
        return django.VERSION[:3]
    except Exception:
        return "unknown"


def _get_db_engine() -> str:
    try:
        return settings.DATABASES.get("default", {}).get("ENGINE", "unknown")
    except Exception:
        return "unknown"


def _hash(value: str) -> str:
    import hashlib
    return hashlib.sha256(value.encode()).hexdigest()[:16]
