"""Abstract base class for all evidence providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass
class ProviderCapabilities:
    """Declares what a provider can do."""

    supports_search: bool = True
    supports_retrieve: bool = True
    supports_structured_output: bool = False
    supports_ai_summary: bool = False
    supports_citations: bool = True
    max_query_length: int = 500
    rate_limit_per_minute: int = 30
    requires_authentication: bool = False

    def __post_init__(self):
        if self.requires_authentication and not self.supports_search:
            raise ValueError(
                "A provider requiring authentication must support search."
            )


@dataclass
class EvidenceItem:
    """Normalised evidence item returned by any provider."""

    source_type: str
    title: str
    authors: str = ""
    journal: str = ""
    publication_date: date | None = None
    pmid: str = ""
    pmcid: str = ""
    doi: str = ""
    abstract: str = ""
    url: str = ""
    evidence_level: str = ""
    study_design: str = ""
    citation_count: int | None = None
    journal_impact: float | None = None
    sample_size: int | None = None
    keywords: list[str] = field(default_factory=list)
    mesh_terms: list[str] = field(default_factory=list)
    relevance_score: float | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIReviewResult:
    """Structured output from an AI clinical reviewer provider."""

    summary: str
    key_findings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradictory_evidence: list[str] = field(default_factory=list)
    confidence_score: float | None = None
    recommendation_alignment: str = ""
    structured_data: dict[str, Any] = field(default_factory=dict)
    raw_response: str = ""
    provider_type: str = ""


class BaseEvidenceProvider(ABC):
    """Every evidence provider must inherit from this."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._capabilities: ProviderCapabilities | None = None

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Machine-readable provider identifier matching ProviderType choices."""

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the provider. Return True on success."""

    @abstractmethod
    def health_check(self) -> dict:
        """Return {'available': bool, 'latency_ms': float, 'error': str|None}."""

    @abstractmethod
    def search(self, query: str, **kwargs) -> list[EvidenceItem]:
        """Search for evidence matching the clinical query."""

    @abstractmethod
    def retrieve(self, identifier: str, id_type: str = "pmid") -> EvidenceItem | None:
        """Retrieve a single evidence item by PMID, DOI, etc."""

    def normalize(self, raw: dict) -> EvidenceItem:
        """Convert provider-specific raw data into a normalised EvidenceItem."""
        raise NotImplementedError

    def version(self) -> str:
        """Return the provider API version in use."""
        return "1.0"

    def capabilities(self) -> ProviderCapabilities:
        """Return the provider's declared capabilities."""
        if self._capabilities is None:
            self._capabilities = ProviderCapabilities()
        return self._capabilities
