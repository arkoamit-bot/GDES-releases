class ClinicalEvidenceError(Exception):
    """Base exception for the CEI module."""


class ProviderError(ClinicalEvidenceError):
    """Raised when an evidence provider fails."""


class ProviderAuthError(ProviderError):
    """Raised when provider authentication fails."""


class ProviderQuotaError(ProviderError):
    """Raised when provider API quota is exceeded."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider request times out."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is unavailable."""


class ValidationError(ClinicalEvidenceError):
    """Raised when recommendation validation fails."""


class ContradictionError(ClinicalEvidenceError):
    """Raised when contradiction detection encounters an error."""


class CacheError(ClinicalEvidenceError):
    """Raised when caching operations fail."""


class GovernanceError(ClinicalEvidenceError):
    """Raised when governance recording fails."""


class CitationError(ClinicalEvidenceError):
    """Raised when citation generation fails."""


class OrchestrationError(ClinicalEvidenceError):
    """Raised when provider orchestration fails."""


class ConfigurationError(ClinicalEvidenceError):
    """Raised when module configuration is invalid."""
