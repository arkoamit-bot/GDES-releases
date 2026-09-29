"""Caching service for evidence searches and AI responses."""

import hashlib
import json
from datetime import timedelta

from django.utils import timezone

from clinical_evidence.constants import CacheTTL
from clinical_evidence.models import EvidenceCache


def _make_key(prefix: str, *parts: str) -> str:
    raw = ":".join(str(p) for p in parts)
    return f"{prefix}:{hashlib.sha256(raw.encode()).hexdigest()[:32]}"


def get_cache(cache_key: str) -> dict | None:
    try:
        entry = EvidenceCache.objects.get(cache_key=cache_key)
        if entry.is_expired():
            entry.delete()
            return None
        return entry.data
    except EvidenceCache.DoesNotExist:
        return None


def set_cache(
    cache_key: str,
    data: dict,
    cache_type: str = "search",
    ttl: int | None = None,
) -> EvidenceCache:
    ttl = ttl or getattr(CacheTTL, cache_type.upper(), CacheTTL.SEARCH)
    expires_at = timezone.now() + timedelta(seconds=ttl)
    obj, _ = EvidenceCache.objects.update_or_create(
        cache_key=cache_key,
        defaults={
            "cache_type": cache_type,
            "data": data,
            "ttl_seconds": ttl,
            "expires_at": expires_at,
        },
    )
    return obj


def invalidate(cache_key: str) -> None:
    EvidenceCache.objects.filter(cache_key=cache_key).delete()


def invalidate_by_type(cache_type: str) -> int:
    deleted, _ = EvidenceCache.objects.filter(cache_type=cache_type).delete()
    return deleted


def clear_expired() -> int:
    deleted, _ = EvidenceCache.objects.filter(
        expires_at__lte=timezone.now(),
    ).delete()
    return deleted


def search_cache_key(query_text: str, **filters) -> str:
    parts = [query_text] + [f"{k}={v}" for k, v in sorted(filters.items())]
    return _make_key("search", *parts)


def ai_cache_key(query_text: str, provider: str, **context) -> str:
    parts = [query_text, provider] + [f"{k}={v}" for k, v in sorted(context.items())]
    return _make_key("ai", *parts)
