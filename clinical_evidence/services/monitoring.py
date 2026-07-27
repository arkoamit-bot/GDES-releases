"""Provider health monitor — tracks availability, latency, error rates."""

import threading
import time

from django.db import models

from clinical_evidence.constants import ProviderStatus
from clinical_evidence.models import (
    EvidenceAnalytics,
    ProviderConfiguration,
    ProviderHealth,
    ProviderRateLimit,
)

_monitor_thread = None
_stop_event = threading.Event()


def check_provider(config: ProviderConfiguration) -> ProviderHealth:
    """Run a health check against a single provider."""
    from clinical_evidence.services.orchestrator import get_provider_instance

    t0 = time.time()
    instance = get_provider_instance(config)
    try:
        result = instance.health_check()
        latency = result.get("latency_ms", (time.time() - t0) * 1000)
        available = result.get("available", False)
        error = result.get("error")

        defaults = {
            "status": ProviderStatus.ACTIVE if available else ProviderStatus.ERROR,
            "is_available": available,
            "latency_ms": latency,
            "error_rate": 0.0 if available else 1.0,
        }
        if available:
            defaults["last_success_at"] = _now()
            defaults["consecutive_failures"] = 0
        else:
            defaults["last_error_at"] = _now()
            defaults["last_error_message"] = error or "Unknown error"
            defaults["consecutive_failures"] = _get_consecutive_failures(config) + 1

        health, _ = ProviderHealth.objects.update_or_create(
            provider=config,
            defaults=defaults,
        )
        return health
    except Exception as exc:
        health, _ = ProviderHealth.objects.update_or_create(
            provider=config,
            defaults={
                "status": ProviderStatus.ERROR,
                "is_available": False,
                "latency_ms": (time.time() - t0) * 1000,
                "last_error_at": _now(),
                "last_error_message": str(exc),
                "consecutive_failures": _get_consecutive_failures(config) + 1,
            },
        )
        return health


def _get_consecutive_failures(config: ProviderConfiguration) -> int:
    last = (
        ProviderHealth.objects.filter(provider=config)
        .order_by("-checked_at")
        .first()
    )
    return last.consecutive_failures if last else 0


def run_all_checks() -> dict[str, ProviderHealth]:
    results = {}
    for config in ProviderConfiguration.objects.filter(is_enabled=True):
        results[config.provider_type] = check_provider(config)
    return results


def record_request(provider_type: str) -> None:
    """Increment the request counter for the current hour window."""
    from django.utils import timezone as tz

    config = ProviderConfiguration.objects.filter(provider_type=provider_type).first()
    if not config:
        return
    now = tz.now()
    window_start = now.replace(minute=0, second=0, microsecond=0)
    obj, _ = ProviderRateLimit.objects.get_or_create(
        provider=config,
        window_start=window_start,
        defaults={"request_count": 0},
    )
    ProviderRateLimit.objects.filter(pk=obj.pk).update(
        request_count=models.F("request_count") + 1,
    )


def is_rate_limited(provider_type: str) -> bool:
    from django.utils import timezone as tz
    now = tz.now()
    window_start = now.replace(minute=0, second=0, microsecond=0)
    config = ProviderConfiguration.objects.filter(
        provider_type=provider_type,
    ).first()
    if not config:
        return True
    try:
        entry = ProviderRateLimit.objects.get(
            provider=config, window_start=window_start,
        )
        return entry.request_count >= config.rate_limit_per_minute
    except ProviderRateLimit.DoesNotExist:
        return False


def start_health_monitor(interval_seconds: int = 300) -> None:
    global _monitor_thread
    if _monitor_thread and _monitor_thread.is_alive():
        return
    _stop_event.clear()

    def _loop():
        while not _stop_event.is_set():
            try:
                run_all_checks()
            except Exception:
                pass
            _stop_event.wait(interval_seconds)

    _monitor_thread = threading.Thread(target=_loop, daemon=True)
    _monitor_thread.start()


def stop_health_monitor() -> None:
    _stop_event.set()


def _now():
    from django.utils import timezone
    return timezone.now()


# django.db.models already imported at top of file
