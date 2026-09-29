"""Provider orchestrator — discovers, loads, and manages provider instances."""

import logging

from clinical_evidence.exceptions import ConfigurationError
from clinical_evidence.models import ProviderConfiguration
from clinical_evidence.providers.base import (
    AIReviewResult,
    BaseEvidenceProvider,
    EvidenceItem,
)
from clinical_evidence.providers.crossref import CrossrefProvider
from clinical_evidence.providers.europe_pmc import EuropePMCProvider
from clinical_evidence.providers.openai import OpenAIProvider
from clinical_evidence.providers.openalex import OpenAlexProvider
from clinical_evidence.providers.perplexity import PerplexityProvider
from clinical_evidence.providers.pubmed import PubMedProvider
from clinical_evidence.providers.semantic_scholar import SemanticScholarProvider
from clinical_evidence.providers.vera import VeraProvider
from clinical_evidence.providers.vera_web import VeraWebSessionProvider

logger = logging.getLogger("bgddr.evidence.orchestrator")

_PROVIDER_REGISTRY: dict[str, type[BaseEvidenceProvider]] = {
    "pubmed": PubMedProvider,
    "europe_pmc": EuropePMCProvider,
    "semantic_scholar": SemanticScholarProvider,
    "openalex": OpenAlexProvider,
    "crossref": CrossrefProvider,
    "vera": VeraProvider,
    "vera_web": VeraWebSessionProvider,
    "openai": OpenAIProvider,
    "perplexity": PerplexityProvider,
}


def get_provider_class(provider_type: str) -> type[BaseEvidenceProvider]:
    """Get a provider class by type string."""
    cls = _PROVIDER_REGISTRY.get(provider_type)
    if not cls:
        raise ConfigurationError(f"Unknown provider type: {provider_type}")
    return cls


def get_provider_instance(config: ProviderConfiguration) -> BaseEvidenceProvider:
    """Get a configured provider instance from a ProviderConfiguration."""
    cls = get_provider_class(config.provider_type)
    instance_config = {
        "api_key": config.api_key_encrypted or "",
        "api_base_url": config.api_base_url or "",
        "max_retries": config.max_retries,
        "timeout_seconds": config.timeout_seconds,
        **config.extra_config,
    }
    return cls(config=instance_config)


def get_ai_reviewer() -> OpenAIProvider | VeraProvider | VeraWebSessionProvider | None:
    """Get the best available AI reviewer — GPT-5 first, Vera fallback.

    GPT-5 (OpenAI) is the PRIMARY AI reviewer: independent, explainable,
    and available with just an API key. Vera Health is consulted only when
    explicitly requested via get_vera_reviewer() — it is an optional
    senior consultant, NOT a pipeline dependency.

    The fallback chain is: openai → vera → vera_web
    """
    for ptype in ("openai", "vera", "vera_web"):
        try:
            config = ProviderConfiguration.objects.get(
                provider_type=ptype, is_enabled=True,
            )
            instance = get_provider_instance(config)
            if instance.authenticate():
                return instance
        except Exception:
            continue
    return None


def get_vera_reviewer() -> VeraProvider | VeraWebSessionProvider | None:
    """Get a configured and authenticated Vera Health provider instance.

    Tries the enterprise API (vera) first, then falls back to the
    web-session provider (vera_web) if the user has configured credentials.
    """
    for ptype in ("vera", "vera_web"):
        try:
            config = ProviderConfiguration.objects.get(
                provider_type=ptype, is_enabled=True,
            )
            instance = get_provider_instance(config)
            if instance.authenticate():
                return instance
        except Exception:
            continue
    return None


def get_all_available_providers() -> list[BaseEvidenceProvider]:
    """Get instances of all enabled and authenticated providers."""
    instances = []
    for config in ProviderConfiguration.objects.filter(
        is_enabled=True,
    ).order_by("priority"):
        try:
            instance = get_provider_instance(config)
            instance.authenticate()
            instances.append(instance)
        except Exception as exc:
            logger.debug("Skipping unauthenticated provider %s: %s", config.provider_type, exc)
    return instances


def register_provider(provider_type: str, provider_class: type[BaseEvidenceProvider]) -> None:
    """Register a custom provider class at runtime."""
    _PROVIDER_REGISTRY[provider_type] = provider_class
