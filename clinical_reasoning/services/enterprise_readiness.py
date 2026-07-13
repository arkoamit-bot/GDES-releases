"""Enterprise Readiness — audit trail, tenant isolation support, and rate limiting."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    actor: str
    action: str
    resource_type: str
    resource_id: str
    details: dict | None = None
    timestamp: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "actor": self.actor,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details or {},
            "timestamp": (self.timestamp or datetime.now()).isoformat(),
        }


def log_audit_event(actor: str, action: str, resource_type: str, resource_id: str, details: dict | None = None) -> None:
    """Log an audit event to the database."""
    from audit.models import AuditLog

    try:
        AuditLog.objects.create(
            model_label=resource_type,
            object_pk=str(resource_id),
            object_repr=f"{resource_type}/{resource_id}",
            action=action,
            field_name="",
            old_value="",
            new_value=str(details or {}),
            change_reason="clinical_reasoning_engine",
        )
    except Exception:
        logger.exception("Failed to log audit event")


def get_audit_trail(resource_type: str, resource_id: str, limit: int = 50) -> list[dict]:
    """Retrieve audit trail for a specific resource."""
    from audit.models import AuditLog

    entries = AuditLog.objects.filter(
        model_label=resource_type,
        object_pk=str(resource_id),
    ).order_by("-changed_at")[:limit]

    return [
        {
            "actor": e.change_reason,
            "action": e.action,
            "resource_type": e.model_label,
            "resource_id": e.object_pk,
            "details": e.new_value,
            "timestamp": e.changed_at.isoformat(),
        }
        for e in entries
    ]


class RateLimiter:
    """Redis-backed rate limiter for API operations.

    Falls back to in-memory if Redis is unavailable.
    """

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, list[float]] = {}
        self._redis = None

    def _get_redis(self):
        if self._redis is None:
            try:
                from django.conf import settings
                from redis import Redis
                if hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
                    self._redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
                elif hasattr(settings, "CELERY_BROKER_URL") and settings.CELERY_BROKER_URL:
                    self._redis = Redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)
            except Exception:
                pass
        return self._redis

    def check(self, key: str) -> bool:
        """Check if a request for `key` is within rate limits."""
        redis = self._get_redis()
        if redis:
            try:
                import time
                now = int(time.time())
                window_start = now - self.window_seconds
                pipeline = redis.pipeline()
                pipeline.zremrangebyscore(f"ratelimit:{key}", 0, window_start)
                pipeline.zcard(f"ratelimit:{key}")
                pipeline.zadd(f"ratelimit:{key}", {str(now): now})
                pipeline.expire(f"ratelimit:{key}", self.window_seconds * 2)
                _, count, *_ = pipeline.execute()
                return int(count) < self.max_requests
            except Exception:
                pass
        return self._check_in_memory(key)

    def remaining(self, key: str) -> int:
        """Get remaining requests for a key."""
        redis = self._get_redis()
        if redis:
            try:
                import time
                now = int(time.time())
                window_start = now - self.window_seconds
                pipeline = redis.pipeline()
                pipeline.zremrangebyscore(f"ratelimit:{key}", 0, window_start)
                pipeline.zcard(f"ratelimit:{key}")
                result = pipeline.execute()
                return max(0, self.max_requests - int(result[1]))
            except Exception:
                pass
        return self._remaining_in_memory(key)

    def _check_in_memory(self, key: str) -> bool:
        import time
        now = time.time()
        window_start = now - self.window_seconds
        if key not in self._buckets:
            self._buckets[key] = []
        self._buckets[key] = [t for t in self._buckets[key] if t > window_start]
        if len(self._buckets[key]) >= self.max_requests:
            return False
        self._buckets[key].append(now)
        return True

    def _remaining_in_memory(self, key: str) -> int:
        import time
        now = time.time()
        window_start = now - self.window_seconds
        if key not in self._buckets:
            return self.max_requests
        self._buckets[key] = [t for t in self._buckets[key] if t > window_start]
        return max(0, self.max_requests - len(self._buckets[key]))


def get_data_quality_report() -> dict:
    """Generate a data quality report across the registry."""
    from patients.models import Patient
    from clinical_reasoning.models import ClinicalProfile

    total = Patient.objects.count()
    profiles = ClinicalProfile.objects.count()

    complete = Patient.objects.filter(
        latest_egfr__isnull=False,
    ).exclude(
        registration_status="inactive",
    ).count()

    return {
        "total_patients": total,
        "profiles_generated": profiles,
        "profile_coverage_pct": round(profiles / max(total, 1) * 100, 1),
        "patients_with_egfr": complete,
        "incomplete_patients": total - complete,
        "last_profile_update": _last_profile_update(),
    }


def _last_profile_update() -> str | None:
    from clinical_reasoning.models import ClinicalProfile
    latest = ClinicalProfile.objects.order_by("-last_updated").first()
    if latest and latest.last_updated:
        return latest.last_updated.isoformat()
    return None
