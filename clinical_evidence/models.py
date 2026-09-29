import hashlib
import json
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from clinical_evidence.constants import (
    AlertType,
    CacheTTL,
    CitationFormat,
    ConfidenceScore,
    ConflictSeverity,
    EvidenceLevel,
    ProviderStatus,
    ProviderType,
    StudyDesign,
    ValidationOutcome,
    VALIDATION_SOURCES,
)


def _default_query_id():
    return f"Q{uuid.uuid4().hex[:12].upper()}"


def _default_package_id():
    return f"EP{uuid.uuid4().hex[:12].upper()}"


def _default_alert_id():
    return f"EA{uuid.uuid4().hex[:12].upper()}"


def _compute_hash(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# --------------------------------------------------------------------------- #
# Provider configuration & health
# --------------------------------------------------------------------------- #
class ProviderConfiguration(models.Model):
    """Per-provider configuration, stored securely."""

    provider_type = models.CharField(
        max_length=30, choices=ProviderType.choices, unique=True,
    )
    is_enabled = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(
        default=10, help_text="Lower = queried first",
    )
    api_key_encrypted = models.TextField(blank=True, default="")
    api_base_url = models.URLField(blank=True, default="")
    extra_config = models.JSONField(default=dict, blank=True)
    max_retries = models.PositiveSmallIntegerField(default=3)
    timeout_seconds = models.PositiveSmallIntegerField(default=30)
    rate_limit_per_minute = models.PositiveSmallIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provider configuration"
        ordering = ["priority", "provider_type"]

    def __str__(self):
        return f"{self.get_provider_type_display()}"


class ProviderHealth(models.Model):
    """Health metrics for a provider over time."""

    provider = models.ForeignKey(
        ProviderConfiguration, on_delete=models.CASCADE, related_name="health_logs",
    )
    status = models.CharField(
        max_length=20, choices=ProviderStatus.choices, default=ProviderStatus.ACTIVE,
    )
    is_available = models.BooleanField(default=True)
    latency_ms = models.FloatField(null=True, blank=True)
    error_rate = models.FloatField(default=0.0)
    quota_remaining = models.IntegerField(null=True, blank=True)
    last_success_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    last_error_message = models.TextField(blank=True, default="")
    consecutive_failures = models.PositiveIntegerField(default=0)
    checked_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Provider health"
        verbose_name_plural = "Provider health metrics"
        indexes = [
            models.Index(fields=["provider", "-checked_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.provider} – {self.status}"


class ProviderRateLimit(models.Model):
    """Track rate limit consumption per provider."""

    provider = models.ForeignKey(
        ProviderConfiguration, on_delete=models.CASCADE, related_name="rate_limits",
    )
    window_start = models.DateTimeField()
    request_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Provider rate limit"
        unique_together = [("provider", "window_start")]
        indexes = [models.Index(fields=["provider", "window_start"])]


# --------------------------------------------------------------------------- #
# Queries & results
# --------------------------------------------------------------------------- #
class EvidenceQuery(models.Model):
    """A clinical evidence search query."""

    query_id = models.CharField(
        max_length=30, primary_key=True, default=_default_query_id,
    )
    disease_id = models.CharField(
        max_length=50, blank=True, default="",
        help_text="GDES disease identifier if context-specific",
    )
    query_text = models.TextField()
    query_type = models.CharField(
        max_length=30, default="clinical",
        help_text="clinical, guideline, drug, safety",
    )
    filters = models.JSONField(default=dict, blank=True)
    max_results = models.PositiveSmallIntegerField(default=20)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    provider_count = models.PositiveSmallIntegerField(default=0)
    result_count = models.PositiveSmallIntegerField(default=0)
    is_cached = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Evidence query"
        verbose_name_plural = "Evidence queries"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["disease_id"]),
            models.Index(fields=["query_type"]),
        ]

    def __str__(self):
        return f"{self.query_id} – {self.query_text[:80]}"


class EvidenceResult(models.Model):
    """A single evidence item returned by a provider."""

    query = models.ForeignKey(
        EvidenceQuery, on_delete=models.CASCADE, related_name="results",
    )
    provider = models.ForeignKey(
        ProviderConfiguration, on_delete=models.SET_NULL, null=True,
    )
    source_type = models.CharField(
        max_length=30, choices=ProviderType.choices,
    )
    title = models.TextField()
    authors = models.TextField(blank=True, default="")
    journal = models.CharField(max_length=300, blank=True, default="")
    publication_date = models.DateField(null=True, blank=True)
    pmid = models.CharField(max_length=30, blank=True, default="")
    pmcid = models.CharField(max_length=30, blank=True, default="")
    doi = models.CharField(max_length=200, blank=True, default="")
    abstract = models.TextField(blank=True, default="")
    url = models.URLField(max_length=500, blank=True, default="")
    evidence_level = models.CharField(
        max_length=10, choices=EvidenceLevel.choices, blank=True, default="",
    )
    study_design = models.CharField(
        max_length=30, choices=StudyDesign.choices, blank=True, default="",
    )
    citation_count = models.IntegerField(null=True, blank=True)
    journal_impact = models.FloatField(null=True, blank=True)
    sample_size = models.IntegerField(null=True, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    mesh_terms = models.JSONField(default=list, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)
    relevance_score = models.FloatField(
        null=True, blank=True, help_text="Provider-assigned relevance 0-1",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence result"
        indexes = [
            models.Index(fields=["query", "source_type"]),
            models.Index(fields=["pmid"]),
            models.Index(fields=["doi"]),
            models.Index(fields=["source_type"]),
        ]

    def __str__(self):
        return f"{self.title[:80]} [{self.source_type}]"


class EvidenceCitation(models.Model):
    """Citation metadata for an evidence result."""

    result = models.OneToOneField(
        EvidenceResult, on_delete=models.CASCADE, related_name="citation",
    )
    apa = models.TextField(blank=True, default="")
    vancouver = models.TextField(blank=True, default="")
    bibtex = models.TextField(blank=True, default="")
    ris = models.TextField(blank=True, default="")
    mla = models.TextField(blank=True, default="")
    chicago = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence citation"


# --------------------------------------------------------------------------- #
# Fused evidence & validation
# --------------------------------------------------------------------------- #
class EvidencePackage(models.Model):
    """A fused, deduplicated evidence package from multiple providers."""

    package_id = models.CharField(
        max_length=30, primary_key=True, default=_default_package_id,
    )
    query = models.ForeignKey(
        EvidenceQuery, on_delete=models.CASCADE, related_name="packages",
    )
    supporting_results = models.ManyToManyField(
        EvidenceResult, related_name="supporting_packages",
    )
    contradictory_results = models.ManyToManyField(
        EvidenceResult, related_name="contradictory_packages",
    )
    neutral_results = models.ManyToManyField(
        EvidenceResult, related_name="neutral_packages",
    )
    ai_summary = models.TextField(blank=True, default="")
    ai_confidence = models.FloatField(null=True, blank=True)
    ai_response_raw = models.JSONField(default=dict, blank=True)
    ai_provider = models.CharField(
        max_length=30, blank=True, default="",
    )
    overall_confidence = models.PositiveSmallIntegerField(
        choices=ConfidenceScore.choices, null=True, blank=True,
    )
    guideline_match = models.CharField(
        max_length=30, blank=True, default="",
        help_text="Matched guideline identifier",
    )
    governance_hash = models.CharField(
        max_length=64, blank=True, default="",
    )
    knowledge_version = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence package"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["overall_confidence"]),
        ]

    def __str__(self):
        return f"{self.package_id} – {self.query.query_text[:60]}"

    def save(self, *args, **kwargs):
        if not self.governance_hash:
            payload = {
                "package_id": self.package_id,
                "query_id": self.query_id,
                "ai_confidence": self.ai_confidence,
                "overall_confidence": self.overall_confidence,
                "created_at": str(self.created_at or timezone.now()),
            }
            self.governance_hash = _compute_hash(payload)
        super().save(*args, **kwargs)


class GuidelineRecommendation(models.Model):
    """Stored guideline reference for validation matching."""

    guideline_source = models.CharField(max_length=30, choices=VALIDATION_SOURCES)
    recommendation_id = models.CharField(max_length=100, primary_key=True)
    disease_id = models.CharField(max_length=50, blank=True, default="")
    title = models.TextField()
    recommendation_text = models.TextField()
    evidence_grade = models.CharField(max_length=20, blank=True, default="")
    recommendation_strength = models.CharField(
        max_length=50, blank=True, default="",
    )
    guideline_version = models.CharField(max_length=30, blank=True, default="")
    publication_date = models.DateField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    url = models.URLField(max_length=500, blank=True, default="")
    keywords = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Guideline recommendation"
        indexes = [
            models.Index(fields=["guideline_source", "disease_id"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"[{self.guideline_source}] {self.recommendation_id}"


class RecommendationValidation(models.Model):
    """Result of validating a GDES recommendation against evidence."""

    gdes_recommendation = models.ForeignKey(
        "knowledge.RecommendationAudit", on_delete=models.CASCADE,
        related_name="evidence_validations",
    )
    package = models.ForeignKey(
        EvidencePackage, on_delete=models.SET_NULL, null=True, related_name="validations",
    )
    outcome = models.CharField(
        max_length=20, choices=ValidationOutcome.choices,
        default=ValidationOutcome.PENDING,
    )
    confidence_score = models.PositiveSmallIntegerField(
        choices=ConfidenceScore.choices, null=True, blank=True,
    )
    matched_guideline = models.ForeignKey(
        GuidelineRecommendation, on_delete=models.SET_NULL, null=True, blank=True,
    )
    summary = models.TextField(blank=True, default="")
    details = models.JSONField(default=dict, blank=True)
    governance_hash = models.CharField(max_length=64, blank=True, default="")
    validated_by = models.CharField(
        max_length=30, default="system",
        help_text="system, ai, or clinician username",
    )
    encountered_at = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recommendation validation"
        indexes = [
            models.Index(fields=["outcome"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Validation {self.outcome} – {self.gdes_recommendation_id}"

    def save(self, *args, **kwargs):
        if not self.governance_hash:
            payload = {
                "validation_id": self.pk,
                "recommendation": str(self.gdes_recommendation_id),
                "outcome": self.outcome,
                "confidence": self.confidence_score,
                "timestamp": str(self.created_at or timezone.now()),
            }
            self.governance_hash = _compute_hash(payload)
        super().save(*args, **kwargs)


class EvidenceConflict(models.Model):
    """A detected contradiction between evidence and recommendations."""

    package = models.ForeignKey(
        EvidencePackage, on_delete=models.CASCADE, related_name="conflicts",
    )
    severity = models.CharField(
        max_length=20, choices=ConflictSeverity.choices,
        default=ConflictSeverity.MEDIUM,
    )
    conflict_type = models.CharField(max_length=50, blank=True, default="")
    title = models.CharField(max_length=300)
    description = models.TextField()
    supporting_results = models.ManyToManyField(
        EvidenceResult, related_name="conflict_supporting",
    )
    contradictory_results = models.ManyToManyField(
        EvidenceResult, related_name="conflict_contradictory",
    )
    affected_disease = models.CharField(max_length=50, blank=True, default="")
    affected_guideline = models.ForeignKey(
        GuidelineRecommendation, on_delete=models.SET_NULL, null=True, blank=True,
    )
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, default="")
    governance_hash = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence conflict"
        indexes = [
            models.Index(fields=["severity"]),
            models.Index(fields=["is_resolved", "-created_at"]),
            models.Index(fields=["conflict_type"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title[:80]}"


# --------------------------------------------------------------------------- #
# Caching
# --------------------------------------------------------------------------- #
class EvidenceCache(models.Model):
    """Cache for evidence searches and AI responses."""

    cache_key = models.CharField(max_length=128, unique=True)
    cache_type = models.CharField(
        max_length=30,
        choices=[
            ("search", "Search results"),
            ("summary", "Evidence summary"),
            ("ai", "AI provider response"),
            ("guideline", "Guideline match"),
        ],
    )
    data = models.JSONField()
    ttl_seconds = models.PositiveIntegerField(default=CacheTTL.SEARCH)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Evidence cache"
        indexes = [
            models.Index(fields=["cache_type", "expires_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.cache_type}:{self.cache_key[:60]}"

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at


# --------------------------------------------------------------------------- #
# Governance & audit
# --------------------------------------------------------------------------- #
class EvidenceAuditLog(models.Model):
    """Immutable audit record for all CEI operations."""

    action = models.CharField(max_length=50)
    actor = models.CharField(max_length=100, blank=True, default="")
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
    audit_hash = models.CharField(max_length=64, unique=True)
    knowledge_version = models.CharField(max_length=20, blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence audit log"
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["action", "resource_type"]),
        ]

    def __str__(self):
        return f"{self.action} – {self.resource_type}:{self.resource_id}"

    def save(self, *args, **kwargs):
        if not self.audit_hash:
            super().save(*args, **kwargs)
            # auto_now_add has now set self.timestamp from the DB.
            payload = {
                "action": self.action,
                "actor": self.actor,
                "resource": f"{self.resource_type}:{self.resource_id}",
                "data": self.payload,
                "ts": str(self.timestamp),
            }
            self.audit_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, default=str).encode()
            ).hexdigest()
            self.__class__.objects.filter(pk=self.pk).update(audit_hash=self.audit_hash)
            return
        super().save(*args, **kwargs)


# --------------------------------------------------------------------------- #
# Alerts & updates
# --------------------------------------------------------------------------- #
class EvidenceAlert(models.Model):
    """Alert generated when important evidence is found."""

    alert_id = models.CharField(
        max_length=30, primary_key=True, default=_default_alert_id,
    )
    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    severity = models.CharField(
        max_length=20, choices=ConflictSeverity.choices,
        default=ConflictSeverity.INFO,
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    disease_id = models.CharField(max_length=50, blank=True, default="")
    related_results = models.ManyToManyField(
        EvidenceResult, blank=True,
    )
    related_guideline = models.ForeignKey(
        GuidelineRecommendation, on_delete=models.SET_NULL, null=True, blank=True,
    )
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence alert"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["alert_type", "is_dismissed"]),
            models.Index(fields=["severity"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title[:80]}"


class EvidenceUpdate(models.Model):
    """Tracks what evidence was updated and when."""

    update_type = models.CharField(
        max_length=30,
        choices=[
            ("daily_refresh", "Daily literature refresh"),
            ("guideline_scan", "Weekly guideline scan"),
            ("provider_sync", "Provider data sync"),
            ("manual", "Manual import"),
        ],
    )
    provider = models.ForeignKey(
        ProviderConfiguration, on_delete=models.SET_NULL, null=True, blank=True,
    )
    summary = models.TextField(blank=True, default="")
    new_results = models.PositiveIntegerField(default=0)
    updated_results = models.PositiveIntegerField(default=0)
    errors = models.JSONField(default=list, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence update"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_update_type_display()} – {self.created_at.date()}"


# --------------------------------------------------------------------------- #
# Analytics & knowledge gaps
# --------------------------------------------------------------------------- #
class EvidenceAnalytics(models.Model):
    """Aggregated analytics snapshot."""

    date = models.DateField(auto_now_add=True)
    total_queries = models.PositiveIntegerField(default=0)
    total_results = models.PositiveIntegerField(default=0)
    cache_hit_rate = models.FloatField(default=0.0)
    avg_latency_ms = models.FloatField(default=0.0)
    provider_uptime = models.JSONField(default=dict)
    validations_run = models.PositiveIntegerField(default=0)
    conflicts_detected = models.PositiveIntegerField(default=0)
    alerts_generated = models.PositiveIntegerField(default=0)
    knowledge_gaps_identified = models.PositiveIntegerField(default=0)
    summary = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Evidence analytics"
        verbose_name_plural = "Evidence analytics"
        indexes = [models.Index(fields=["-date"])]

    def __str__(self):
        return f"Analytics – {self.date}"


class EvidenceSummary(models.Model):
    """AI-generated summary of evidence for a specific context."""

    query = models.ForeignKey(
        EvidenceQuery, on_delete=models.CASCADE, related_name="summaries",
    )
    summary_text = models.TextField()
    key_findings = models.JSONField(default=list, blank=True)
    limitations = models.JSONField(default=list, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    ai_provider = models.CharField(max_length=30, blank=True, default="")
    citation_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evidence summary"
        indexes = [models.Index(fields=["-created_at"])]


class KnowledgeGap(models.Model):
    """Identified gaps in GDES knowledge base vs current evidence."""

    disease_id = models.CharField(max_length=50)
    gap_type = models.CharField(
        max_length=30,
        choices=[
            ("missing_rule", "Missing clinical rule"),
            ("outdated_evidence", "Outdated evidence reference"),
            ("new_treatment", "New treatment not in KB"),
            ("safety_update", "Safety information update"),
            ("guideline_change", "Guideline recommendation changed"),
            ("contradiction", "KB contradicts current evidence"),
        ],
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    evidence_results = models.ManyToManyField(
        EvidenceResult, blank=True,
    )
    recommended_action = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=10,
        choices=[("critical", "Critical"), ("high", "High"), ("medium", "Medium"), ("low", "Low")],
        default="medium",
    )
    is_addressed = models.BooleanField(default=False)
    addressed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    addressed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Knowledge gap"
        indexes = [
            models.Index(fields=["disease_id", "gap_type"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["is_addressed"]),
        ]

    def __str__(self):
        return f"[{self.priority}] {self.disease_id} – {self.title[:80]}"
