"""Analytics service for evidence module metrics."""

from datetime import date, datetime

from django.db.models import Avg, Count, Q
from django.utils import timezone

from clinical_evidence.constants import ValidationOutcome
from clinical_evidence.models import (
    EvidenceAnalytics,
    EvidenceCache,
    EvidenceConflict,
    EvidenceQuery,
    ProviderConfiguration,
    ProviderHealth,
    RecommendationValidation,
)


def compute_daily_analytics() -> EvidenceAnalytics:
    """Compute and store a daily analytics snapshot."""
    today = timezone.now().date()
    start = timezone.make_aware(
        datetime.combine(today, datetime.min.time())
    )
    end = timezone.make_aware(
        datetime.combine(today, datetime.max.time())
    )

    total_queries = EvidenceQuery.objects.filter(
        created_at__gte=start, created_at__lte=end,
    ).count()

    total_results = sum(
        q.result_count for q in EvidenceQuery.objects.filter(
            created_at__gte=start, created_at__lte=end,
        )
    )

    cache_total = EvidenceCache.objects.count()
    cache_expired = EvidenceCache.objects.filter(
        expires_at__lte=timezone.now(),
    ).count()
    cache_hit_rate = (
        ((cache_total - cache_expired) / max(cache_total, 1)) * 100
    )

    latency = ProviderHealth.objects.filter(
        checked_at__gte=start,
    ).aggregate(avg=Avg("latency_ms"))
    avg_latency = latency["avg"] or 0.0

    provider_uptime = {}
    for config in ProviderConfiguration.objects.all():
        latest = ProviderHealth.objects.filter(
            provider=config,
        ).order_by("-checked_at").first()
        provider_uptime[config.provider_type] = (
            latest.is_available if latest else False
        )

    validations_run = RecommendationValidation.objects.filter(
        created_at__gte=start,
    ).count()

    conflicts_detected = EvidenceConflict.objects.filter(
        created_at__gte=start,
    ).count()

    alerts_generated = EvidenceAlert.objects.filter(
        created_at__gte=start,
    ).count()

    analytics = EvidenceAnalytics.objects.create(
        total_queries=total_queries,
        total_results=total_results,
        cache_hit_rate=round(cache_hit_rate, 2),
        avg_latency_ms=round(avg_latency, 2),
        provider_uptime=provider_uptime,
        validations_run=validations_run,
        conflicts_detected=conflicts_detected,
        alerts_generated=alerts_generated,
    )
    return analytics


def get_summary_stats(days: int = 30) -> dict:
    """Get summary statistics for the dashboard."""
    since = timezone.now() - timezone.timedelta(days=days)
    total_queries = EvidenceQuery.objects.filter(
        created_at__gte=since,
    ).count()
    validations = RecommendationValidation.objects.filter(
        created_at__gte=since,
    )
    verified_count = validations.filter(outcome=ValidationOutcome.VERIFIED).count()
    conflict_count = EvidenceConflict.objects.filter(
        created_at__gte=since,
    ).count()
    active_conflicts = EvidenceConflict.objects.filter(
        is_resolved=False,
    ).count()
    providers = ProviderConfiguration.objects.filter(is_enabled=True).count()
    available = ProviderHealth.objects.filter(
        is_available=True,
    ).values("provider").distinct().count()

    return {
        "total_queries": total_queries,
        "validations_run": validations.count(),
        "verified_count": verified_count,
        "conflicts_detected": conflict_count,
        "active_conflicts": active_conflicts,
        "providers_enabled": providers,
        "providers_available": available,
    }
