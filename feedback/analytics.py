"""Override analytics and continuous improvement metrics.

Computes override rates, feedback trends, and suggestion lifecycle
stats from WorkflowFeedback + RecommendationAudit records.
"""
from datetime import timedelta

from django.db.models import (
    Count, Q, Case, When, Value, IntegerField, F, Avg,
)
from django.utils import timezone


# ---------------------------------------------------------------------------
# Override rate analytics
# ---------------------------------------------------------------------------

def override_rate_by_disease(days=90):
    """Return override rates per disease for the last *days* days."""
    from .models import WorkflowFeedback

    cutoff = timezone.now() - timedelta(days=days)
    qs = WorkflowFeedback.objects.filter(
        action__in=("accept", "modify", "reject"),
        created_at__gte=cutoff,
    )
    rows = (
        qs.values("feedback_type")
        .annotate(
            total=Count("id"),
            accepted=Count("id", filter=Q(action="accept")),
            modified=Count("id", filter=Q(action="modify")),
            rejected=Count("id", filter=Q(action="reject")),
        )
        .order_by("feedback_type")
    )
    result = []
    for r in rows:
        total = r["total"]
        overrides = r["modified"] + r["rejected"]
        result.append({
            "feedback_type": r["feedback_type"],
            "total": total,
            "accepted": r["accepted"],
            "modified": r["modified"],
            "rejected": r["rejected"],
            "override_rate": round(overrides / total * 100, 1) if total else 0,
        })
    return result


def override_rate_by_rule(days=90):
    """Return override rates per recommendation_ref for the last *days* days."""
    from .models import WorkflowFeedback

    cutoff = timezone.now() - timedelta(days=days)
    qs = WorkflowFeedback.objects.filter(
        action__in=("accept", "modify", "reject"),
        recommendation_ref__gt="",
        created_at__gte=cutoff,
    )
    rows = (
        qs.values("recommendation_ref")
        .annotate(
            total=Count("id"),
            accepted=Count("id", filter=Q(action="accept")),
            modified=Count("id", filter=Q(action="modify")),
            rejected=Count("id", filter=Q(action="reject")),
        )
        .filter(total__gte=2)
        .order_by("-total")[:20]
    )
    result = []
    for r in rows:
        total = r["total"]
        overrides = r["modified"] + r["rejected"]
        result.append({
            "recommendation_ref": r["recommendation_ref"],
            "total": total,
            "accepted": r["accepted"],
            "modified": r["modified"],
            "rejected": r["rejected"],
            "override_rate": round(overrides / total * 100, 1) if total else 0,
        })
    return result


def override_rate_by_clinician(days=90):
    """Return override rates per clinician for the last *days* days."""
    from .models import WorkflowFeedback

    cutoff = timezone.now() - timedelta(days=days)
    qs = WorkflowFeedback.objects.filter(
        action__in=("accept", "modify", "reject"),
        created_at__gte=cutoff,
    ).exclude(user__isnull=True)
    rows = (
        qs.values("user__username")
        .annotate(
            total=Count("id"),
            accepted=Count("id", filter=Q(action="accept")),
            modified=Count("id", filter=Q(action="modify")),
            rejected=Count("id", filter=Q(action="reject")),
        )
        .order_by("-total")[:15]
    )
    result = []
    for r in rows:
        total = r["total"]
        overrides = r["modified"] + r["rejected"]
        result.append({
            "clinician": r["user__username"] or "Unknown",
            "total": total,
            "accepted": r["accepted"],
            "modified": r["modified"],
            "rejected": r["rejected"],
            "override_rate": round(overrides / total * 100, 1) if total else 0,
        })
    return result


def temporal_override_trend(days=180, bucket="week"):
    """Return weekly (or daily) override trend for the last *days* days."""
    from .models import WorkflowFeedback
    from django.db.models.functions import TruncWeek, TruncDay

    cutoff = timezone.now() - timedelta(days=days)
    trunc = TruncWeek if bucket == "week" else TruncDay
    qs = WorkflowFeedback.objects.filter(
        action__in=("accept", "modify", "reject"),
        created_at__gte=cutoff,
    )
    rows = (
        qs.annotate(period=trunc("created_at"))
        .values("period")
        .annotate(
            total=Count("id"),
            accepted=Count("id", filter=Q(action="accept")),
            modified=Count("id", filter=Q(action="modify")),
            rejected=Count("id", filter=Q(action="reject")),
        )
        .order_by("period")
    )
    result = []
    for r in rows:
        total = r["total"]
        overrides = r["modified"] + r["rejected"]
        result.append({
            "period": r["period"].strftime("%Y-%m-%d"),
            "total": total,
            "accepted": r["accepted"],
            "modified": r["modified"],
            "rejected": r["rejected"],
            "override_rate": round(overrides / total * 100, 1) if total else 0,
        })
    return result


def overall_override_rate(days=90):
    """Return (total_feedback, override_count, override_rate%) for the period."""
    from .models import WorkflowFeedback

    cutoff = timezone.now() - timedelta(days=days)
    qs = WorkflowFeedback.objects.filter(
        action__in=("accept", "modify", "reject"),
        created_at__gte=cutoff,
    )
    totals = qs.aggregate(
        total=Count("id"),
        overrides=Count("id", filter=Q(action__in=("modify", "reject"))),
        avg_rating=Avg("rating"),
    )
    total = totals["total"] or 0
    overrides = totals["overrides"] or 0
    return {
        "total": total,
        "overrides": overrides,
        "accepts": total - overrides,
        "override_rate": round(overrides / total * 100, 1) if total else 0,
        "avg_rating": round(totals["avg_rating"] or 0, 2),
    }


# ---------------------------------------------------------------------------
# Suggestion lifecycle stats
# ---------------------------------------------------------------------------

def suggestion_lifecycle_stats():
    """Return counts of improvement suggestions in each lifecycle stage."""
    from .models import KnowledgeImprovementSuggestion

    rows = (
        KnowledgeImprovementSuggestion.objects
        .values("status")
        .annotate(count=Count("id"))
        .order_by("status")
    )
    stats = {r["status"]: r["count"] for r in rows}
    stats["total"] = sum(stats.values())
    return stats


def pending_suggestions_for_review(limit=10):
    """Return top *limit* pending improvement suggestions ordered by override count."""
    from .models import KnowledgeImprovementSuggestion

    return list(
        KnowledgeImprovementSuggestion.objects
        .filter(status="pending")
        .order_by("-override_count")[:limit]
    )


# ---------------------------------------------------------------------------
# Per-patient feedback context (for Clinical Reasoning tab)
# ---------------------------------------------------------------------------

def patient_override_context(patient):
    """Return override stats relevant to a specific patient's disease area.

    Looks at WorkflowFeedback linked to the patient (if any), plus global
    feedback for the same feedback_type categories the patient's profile uses.
    """
    from .models import WorkflowFeedback

    local_qs = WorkflowFeedback.objects.filter(patient=patient)
    local_total = local_qs.count()
    local_overrides = local_qs.filter(action__in=("modify", "reject")).count()

    return {
        "local_total": local_total,
        "local_overrides": local_overrides,
        "local_override_rate": (
            round(local_overrides / local_total * 100, 1) if local_total else None
        ),
    }
