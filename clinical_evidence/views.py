"""Clinical Evidence Intelligence views."""

import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .models import (
    EvidenceAlert,
    EvidenceConflict,
    EvidencePackage,
    EvidenceQuery,
    EvidenceResult,
    EvidenceSummary,
    GuidelineRecommendation,
    KnowledgeGap,
    ProviderConfiguration,
    RecommendationValidation,
)
from .services.analytics import compute_daily_analytics, get_summary_stats
from .services.orchestrator import get_ai_reviewer, get_all_available_providers
from .services.retrieval import retrieve_evidence


@login_required
@require_GET
def search_evidence(request):
    """Search for evidence across all configured providers."""
    query_text = request.GET.get("q", "")
    disease_id = request.GET.get("disease_id", "")
    max_results = int(request.GET.get("max_results", 20))
    providers = request.GET.getlist("providers")

    if not query_text and not disease_id:
        return JsonResponse({"error": "Provide q (query text) or disease_id."}, status=400)

    try:
        query = retrieve_evidence(
            query_text=query_text,
            disease_id=disease_id,
            max_results=max_results,
        )
        results = query.results.all()
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

    return JsonResponse({
        "query": query_text or disease_id,
        "count": len(results),
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "authors": r.authors,
                "journal": r.journal,
                "year": r.publication_date.year if r.publication_date else None,
                "pmid": r.pmid,
                "doi": r.doi,
                "provider": r.source_type,
                "relevance_score": r.relevance_score,
                "evidence_level": r.evidence_level,
                "url": r.url,
            }
            for r in results
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def query_detail(request, query_id):
    query = get_object_or_404(EvidenceQuery, query_id=query_id)
    results = EvidenceResult.objects.filter(query=query)
    packages = EvidencePackage.objects.filter(query=query)
    return JsonResponse({
        "query": {
            "query_id": query.query_id,
            "query_text": query.query_text,
            "disease_id": query.disease_id,
            "result_count": query.result_count,
            "created_at": query.created_at,
        },
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "provider": r.source_type,
                "relevance_score": r.relevance_score,
                "evidence_level": r.evidence_level,
                "year": r.publication_date.year if r.publication_date else None,
            }
            for r in results
        ],
        "packages": [
            {
                "package_id": p.package_id,
                "ai_confidence": p.ai_confidence,
                "supporting": p.supporting_results.count(),
                "contradictory": p.contradictory_results.count(),
            }
            for p in packages
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def package_detail(request, package_id):
    package = get_object_or_404(EvidencePackage, package_id=package_id)
    return JsonResponse({
        "package_id": package.package_id,
        "query_id": package.query_id,
        "ai_confidence": package.ai_confidence,
        "summary": package.ai_summary,
        "supporting": [
            {"id": r.id, "title": r.title, "pmid": r.pmid}
            for r in package.supporting_results.all()
        ],
        "contradictory": [
            {"id": r.id, "title": r.title, "pmid": r.pmid}
            for r in package.contradictory_results.all()
        ],
        "validations": list(
            package.validations.values("id", "outcome", "confidence_score", "summary")
        ),
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def validation_list(request):
    outcome = request.GET.get("outcome")
    validations = RecommendationValidation.objects.all()
    if outcome:
        validations = validations.filter(outcome=outcome)
    validations = validations.select_related("package", "matched_guideline")[:100]
    return JsonResponse({
        "count": validations.count(),
        "results": [
            {
                "id": v.id,
                "outcome": v.outcome,
                "confidence_score": v.confidence_score,
                "summary": v.summary,
                "recommendation_id": v.gdes_recommendation_id,
                "matched_guideline": str(v.matched_guideline) if v.matched_guideline else None,
                "encountered_at": v.encountered_at,
                "validated_by": v.validated_by,
            }
            for v in validations
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def conflicts_list(request):
    resolved = request.GET.get("resolved")
    conflicts = EvidenceConflict.objects.all()
    if resolved == "0":
        conflicts = conflicts.filter(is_resolved=False)
    elif resolved == "1":
        conflicts = conflicts.filter(is_resolved=True)
    conflicts = conflicts.select_related("affected_guideline")[:100]
    return JsonResponse({
        "count": conflicts.count(),
        "results": [
            {
                "id": c.id,
                "severity": c.severity,
                "conflict_type": c.conflict_type,
                "title": c.title,
                "description": c.description,
                "is_resolved": c.is_resolved,
                "resolution": c.resolution_notes,
                "affected_disease": c.affected_disease,
                "affected_guideline": str(c.affected_guideline) if c.affected_guideline else None,
                "created_at": c.created_at,
            }
            for c in conflicts
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def alerts_list(request):
    alerts = EvidenceAlert.objects.filter(is_read=False).order_by("-created_at")[:50]
    return JsonResponse({
        "count": alerts.count(),
        "results": [
            {
                "alert_id": a.alert_id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "title": a.title,
                "description": a.description,
                "created_at": a.created_at,
            }
            for a in alerts
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def analytics_dashboard(request):
    days = int(request.GET.get("days", 30))
    return JsonResponse(get_summary_stats(days=days), json_dumps_params={"indent": 2})


@login_required
@require_POST
def compute_analytics(request):
    snapshot = compute_daily_analytics()
    return JsonResponse({
        "id": snapshot.id,
        "date": str(snapshot.date),
        "total_queries": snapshot.total_queries,
        "total_results": snapshot.total_results,
        "cache_hit_rate": snapshot.cache_hit_rate,
        "avg_latency_ms": snapshot.avg_latency_ms,
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def provider_status(request):
    providers = ProviderConfiguration.objects.filter(is_enabled=True)
    return JsonResponse({
        "providers": [
            {
                "type": p.provider_type,
                "enabled": p.is_enabled,
                "priority": p.priority,
                "health": [
                    {
                        "is_available": h.is_available,
                        "latency_ms": h.latency_ms,
                        "error_message": h.last_error_message,
                        "checked_at": h.checked_at,
                    }
                    for h in p.health_logs.order_by("-checked_at")[:5]
                ],
            }
            for p in providers
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def summaries_list(request):
    disease_id = request.GET.get("disease_id")
    summaries = EvidenceSummary.objects.all()
    if disease_id:
        summaries = summaries.filter(query__disease_id=disease_id)
    summaries = summaries.order_by("-created_at")[:20]
    return JsonResponse({
        "count": summaries.count(),
        "results": [
            {
                "summary_id": s.id,
                "disease_id": s.query.disease_id if s.query else "",
                "title": s.summary_text[:100],
                "summary_type": s.ai_provider,
                "created_at": s.created_at,
            }
            for s in summaries
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def knowledge_gaps(request):
    disease_id = request.GET.get("disease_id")
    gaps = KnowledgeGap.objects.all()
    if disease_id:
        gaps = gaps.filter(disease_id=disease_id)
    gaps = gaps.order_by("-priority", "-created_at")[:50]
    return JsonResponse({
        "count": gaps.count(),
        "results": [
            {
                "id": g.id,
                "gap_type": g.gap_type,
                "title": g.title,
                "description": g.description,
                "priority": g.priority,
                "disease_id": g.disease_id,
                "is_addressed": g.is_addressed,
            }
            for g in gaps
        ],
    }, json_dumps_params={"indent": 2})


@login_required
@require_GET
def guidelines_list(request):
    guidelines = GuidelineRecommendation.objects.filter(is_active=True)[:100]
    return JsonResponse({
        "count": guidelines.count(),
        "results": [
            {
                "recommendation_id": g.recommendation_id,
                "guideline_source": g.guideline_source,
                "recommendation_text": g.recommendation_text[:200],
                "evidence_level": g.evidence_grade,
                "strength": g.recommendation_strength,
                "disease_id": g.disease_id,
                "year": g.publication_date.year if g.publication_date else None,
                "url": g.url,
            }
            for g in guidelines
        ],
    }, json_dumps_params={"indent": 2})
