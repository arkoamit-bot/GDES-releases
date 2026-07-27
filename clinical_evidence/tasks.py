"""Celery tasks for async evidence processing."""

from __future__ import annotations

import logging

try:
    from bgddr.celery import app
except ImportError:
    app = None  # Celery not available; tasks will be no-ops

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_evidence_search(
    self,
    query_text: str,
    disease_id: str = "",
    max_results: int = 20,
    provider_types: list[str] | None = None,
) -> dict:
    """Execute an evidence search in the background."""
    from clinical_evidence.services.retrieval import retrieve_evidence
    try:
        query = retrieve_evidence(
            query_text=query_text,
            disease_id=disease_id,
            max_results=max_results,
        )
        results = query.results.all()
        return {
            "query": query_text or disease_id,
            "count": len(results),
            "query_id": query.query_id,
            "result_ids": [r.id for r in results],
        }
    except Exception as exc:
        logger.exception("Evidence search failed for query=%s", query_text)
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_validate_recommendation(
    self,
    recommendation_id: int,
    package_id: str | None = None,
) -> dict:
    """Validate a recommendation against evidence in the background.

    Runs AI review via the best available provider (Vera first), then
    passes the result to the validation service so it can use the
    AI-generated confidence, evidence alignment, and key findings.
    """
    from clinical_evidence.models import EvidencePackage, GuidelineRecommendation
    from clinical_evidence.services.orchestrator import get_ai_reviewer
    from clinical_evidence.services.validation import validate_recommendation
    try:
        recommendation = GuidelineRecommendation.objects.get(pk=recommendation_id)
        package = EvidencePackage.objects.filter(package_id=package_id).first() if package_id else None

        ai_review = None
        reviewer = get_ai_reviewer()
        if reviewer is not None:
            try:
                ai_review = reviewer.review_clinical_question(
                    recommendation.recommendation_text,
                    context={"disease_id": recommendation.disease_id or ""},
                )
            except Exception as exc:
                logger.warning("AI review failed for recommendation %s: %s", recommendation_id, exc)

        validation = validate_recommendation(
            recommendation_text=recommendation.recommendation_text,
            gdes_recommendation=recommendation,
            package=package,
            ai_review=ai_review,
        )
        return {"validation_id": validation.id, "outcome": validation.outcome}
    except Exception as exc:
        logger.exception("Validation failed for recommendation %s", recommendation_id)
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_detect_contradictions(
    self,
    package_id: str,
) -> dict:
    """Detect contradictions within an evidence package."""
    from clinical_evidence.models import EvidencePackage
    from clinical_evidence.services.contradiction import detect_contradictions
    try:
        package = EvidencePackage.objects.get(package_id=package_id)
        all_results = list(package.supporting_results.all()) + list(package.contradictory_results.all())
        conflicts = detect_contradictions(all_results, package.query.disease_id)
        return {"package_id": package_id, "conflicts": len(conflicts)}
    except Exception as exc:
        logger.exception("Contradiction detection failed for package %s", package_id)
        raise self.retry(exc=exc)


@app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def async_compute_analytics(self) -> dict:
    """Compute and store daily analytics snapshot."""
    from clinical_evidence.services.analytics import compute_daily_analytics
    try:
        snapshot = compute_daily_analytics()
        return {"analytics_id": snapshot.id, "date": str(snapshot.date)}
    except Exception as exc:
        logger.exception("Daily analytics computation failed")
        raise self.retry(exc=exc)


@app.task
def periodic_cache_cleanup() -> int:
    """Remove expired cache entries."""
    from django.utils import timezone
    from clinical_evidence.models import EvidenceCache
    deleted, _ = EvidenceCache.objects.filter(expires_at__lte=timezone.now()).delete()
    if deleted:
        logger.info("Cleaned %d expired evidence cache entries", deleted)
    return deleted
