"""Evidence retrieval engine — builds queries and fetches from providers.

Phase 3: Free API providers are the backbone.
  PubMed, Europe PMC, Semantic Scholar, OpenAlex, CrossRef.

Phase 5: Search dedup prevents redundant queries for the same disease.
"""

import hashlib
import logging
import time
from typing import Any

from django.utils import timezone

from clinical_evidence.models import (
    EvidenceQuery,
    EvidenceResult,
    ProviderConfiguration,
)
from clinical_evidence.providers.base import EvidenceItem
from clinical_evidence.services.cache import (
    get_cache,
    search_cache_key,
    set_cache,
)
from clinical_evidence.services.monitoring import is_rate_limited, record_request
from clinical_evidence.services.orchestrator import get_provider_instance

logger = logging.getLogger("bgddr.evidence.retrieval")

# Free, reliable public APIs — the evidence backbone (Phase 3)
FREE_API_PROVIDERS = frozenset({
    "pubmed",
    "europe_pmc",
    "semantic_scholar",
    "openalex",
    "crossref",
})

# AI-backed providers — used for review, not primary search
AI_PROVIDERS = frozenset({
    "openai",
    "perplexity",
    "vera",
    "vera_web",
})


def build_clinical_query(
    disease_id: str = "",
    keywords: list[str] | None = None,
    question: str = "",
) -> str:
    """Build an optimised clinical search query string."""
    parts = []
    if disease_id:
        disease_name = disease_id.replace("_", " ").replace("-", " ").title()
        parts.append(f"({disease_name})")
    if keywords:
        parts.extend(keywords)
    if question:
        parts.append(question)
    return " AND ".join(parts) if parts else ""


def retrieve_evidence(
    query_text: str,
    disease_id: str = "",
    max_results: int = 20,
    force_refresh: bool = False,
    free_only: bool = True,
    **filters: Any,
) -> EvidenceQuery:
    """Execute a multi-provider evidence search and store results.

    When *free_only* is True (default), only free public APIs are queried.
    AI-backed providers are skipped for primary search — they are used
    for review/summary instead.

    Returns the EvidenceQuery with results populated.
    """
    cache_key = search_cache_key(query_text, disease_id=disease_id, **filters)
    if not force_refresh:
        cached = get_cache(cache_key)
        if cached:
            return _from_cache(cached, query_text, disease_id)

    query = EvidenceQuery.objects.create(
        query_text=query_text,
        disease_id=disease_id,
        filters=filters,
        max_results=max_results,
    )

    all_items: list[EvidenceItem] = []
    providers = ProviderConfiguration.objects.filter(
        is_enabled=True,
    ).order_by("priority")

    for config in providers:
        # Phase 3: filter to free API providers for primary search
        if free_only and config.provider_type not in FREE_API_PROVIDERS:
            logger.debug(
                "Skipping %s (not a free API provider, free_only=%s)",
                config.provider_type, free_only,
            )
            continue

        if is_rate_limited(config.provider_type):
            logger.warning("Rate limited: %s", config.provider_type)
            continue

        try:
            instance = get_provider_instance(config)
            t0 = time.time()
            items = instance.search(query_text, max_results=max_results)
            latency = (time.time() - t0) * 1000
            record_request(config.provider_type)

            for item in items:
                item.relevance_score = getattr(item, "relevance_score", None) or 0.0
                all_items.append(item)
                _save_result(item, query, config)

            query.provider_count += 1
            logger.debug(
                "Provider %s returned %d items in %.0fms",
                config.provider_type, len(items), latency,
            )
        except Exception as exc:
            logger.error("Provider %s failed: %s", config.provider_type, exc)
            continue

    query.completed_at = timezone.now()
    query.result_count = len(all_items)
    query.save()

    set_cache(cache_key, _serialize_query(query), cache_type="search")
    return query


def _save_result(
    item: EvidenceItem,
    query: EvidenceQuery,
    config: ProviderConfiguration,
) -> EvidenceResult:
    return EvidenceResult.objects.create(
        query=query,
        provider=config if config.pk else None,
        source_type=item.source_type,
        title=item.title,
        authors=item.authors,
        journal=item.journal,
        publication_date=item.publication_date,
        pmid=item.pmid,
        pmcid=item.pmcid,
        doi=item.doi,
        abstract=item.abstract,
        url=item.url,
        evidence_level=item.evidence_level,
        study_design=item.study_design,
        citation_count=item.citation_count,
        journal_impact=item.journal_impact,
        sample_size=item.sample_size,
        keywords=item.keywords,
        mesh_terms=item.mesh_terms,
        raw_data=item.raw_data,
        relevance_score=item.relevance_score,
    )


def retrieve_single(identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
    """Retrieve a single evidence item from the first available provider."""
    providers = ProviderConfiguration.objects.filter(is_enabled=True).order_by("priority")
    for config in providers:
        try:
            instance = get_provider_instance(config)
            item = instance.retrieve(identifier, id_type=id_type)
            if item:
                return item
        except Exception:
            continue
    return None


def _from_cache(cached: dict, query_text: str, disease_id: str) -> EvidenceQuery:
    qid = cached.get("query_id", "")
    try:
        query = EvidenceQuery.objects.get(query_id=qid)
        if query.result_count == 0:
            query.result_count = query.results.count()
            query.save()
        return query
    except EvidenceQuery.DoesNotExist:
        return EvidenceQuery.objects.create(
            query_text=query_text,
            disease_id=disease_id,
            is_cached=True,
        )


def _serialize_query(query: EvidenceQuery) -> dict:
    return {
        "query_id": query.query_id,
        "query_text": query.query_text,
        "disease_id": query.disease_id,
        "result_count": query.result_count,
        "provider_count": query.provider_count,
        "completed_at": str(query.completed_at),
    }
