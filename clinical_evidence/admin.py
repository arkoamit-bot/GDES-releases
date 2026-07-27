from django.contrib import admin

from .models import (
    EvidenceAlert,
    EvidenceAnalytics,
    EvidenceAuditLog,
    EvidenceCache,
    EvidenceCitation,
    EvidenceConflict,
    EvidencePackage,
    EvidenceQuery,
    EvidenceResult,
    EvidenceSummary,
    EvidenceUpdate,
    GuidelineRecommendation,
    KnowledgeGap,
    ProviderConfiguration,
    ProviderHealth,
    ProviderRateLimit,
    RecommendationValidation,
)


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProviderConfiguration)
class ProviderConfigurationAdmin(admin.ModelAdmin):
    list_display = ("provider_type", "is_enabled", "priority", "rate_limit_per_minute", "created_at")
    list_filter = ("is_enabled", "provider_type")
    search_fields = ("provider_type",)
    readonly_fields = ("api_key_encrypted",)


@admin.register(ProviderHealth)
class ProviderHealthAdmin(admin.ModelAdmin):
    list_display = ("provider", "status", "is_available", "latency_ms", "checked_at")
    list_filter = ("status", "is_available")
    date_hierarchy = "checked_at"


@admin.register(ProviderRateLimit)
class ProviderRateLimitAdmin(admin.ModelAdmin):
    list_display = ("provider", "request_count", "window_start")
    date_hierarchy = "window_start"


@admin.register(EvidenceQuery)
class EvidenceQueryAdmin(admin.ModelAdmin):
    list_display = ("query_id", "query_text", "disease_id", "result_count", "query_type", "created_at")
    list_filter = ("query_type",)
    search_fields = ("query_text", "disease_id")
    date_hierarchy = "created_at"


@admin.register(EvidenceResult)
class EvidenceResultAdmin(admin.ModelAdmin):
    list_display = ("title", "source_type", "pmid", "publication_date", "relevance_score", "evidence_level")
    list_filter = ("source_type", "evidence_level")
    search_fields = ("title", "pmid", "doi", "authors")
    date_hierarchy = "publication_date"


@admin.register(EvidenceCitation)
class EvidenceCitationAdmin(admin.ModelAdmin):
    list_display = ("result", "created_at")
    search_fields = ("result__title", "result__pmid")


@admin.register(EvidencePackage)
class EvidencePackageAdmin(admin.ModelAdmin):
    list_display = ("package_id", "query", "overall_confidence", "ai_confidence", "guideline_match")
    list_filter = ("overall_confidence",)
    search_fields = ("package_id", "query__query_text")


@admin.register(GuidelineRecommendation)
class GuidelineRecommendationAdmin(admin.ModelAdmin):
    list_display = ("recommendation_id", "guideline_source", "evidence_grade", "recommendation_strength", "publication_date", "is_active")
    list_filter = ("guideline_source", "evidence_grade", "recommendation_strength", "is_active")
    search_fields = ("recommendation_text", "recommendation_id")


@admin.register(RecommendationValidation)
class RecommendationValidationAdmin(admin.ModelAdmin):
    list_display = ("gdes_recommendation", "outcome", "confidence_score", "package", "validated_by", "created_at")
    list_filter = ("outcome", "validated_by")
    date_hierarchy = "created_at"


@admin.register(EvidenceConflict)
class EvidenceConflictAdmin(admin.ModelAdmin):
    list_display = ("title", "severity", "conflict_type", "is_resolved", "created_at")
    list_filter = ("severity", "conflict_type", "is_resolved")
    search_fields = ("title",)
    date_hierarchy = "created_at"


@admin.register(EvidenceCache)
class EvidenceCacheAdmin(admin.ModelAdmin):
    list_display = ("cache_key", "cache_type", "created_at", "expires_at")
    list_filter = ("cache_type",)
    search_fields = ("cache_key",)
    date_hierarchy = "created_at"


@admin.register(EvidenceAuditLog)
class EvidenceAuditLogAdmin(ReadOnlyAdmin):
    list_display = ("action", "actor", "resource_type", "resource_id", "timestamp")
    list_filter = ("action", "resource_type")
    date_hierarchy = "timestamp"
    search_fields = ("actor", "resource_id")


@admin.register(EvidenceAlert)
class EvidenceAlertAdmin(admin.ModelAdmin):
    list_display = ("alert_id", "alert_type", "severity", "title", "is_read", "created_at")
    list_filter = ("alert_type", "severity", "is_read")
    date_hierarchy = "created_at"


@admin.register(EvidenceUpdate)
class EvidenceUpdateAdmin(admin.ModelAdmin):
    list_display = ("update_type", "provider", "new_results", "updated_results", "duration_seconds", "created_at")
    list_filter = ("update_type",)


@admin.register(EvidenceAnalytics)
class EvidenceAnalyticsAdmin(ReadOnlyAdmin):
    list_display = ("date", "total_queries", "total_results", "cache_hit_rate", "avg_latency_ms")
    date_hierarchy = "date"


@admin.register(EvidenceSummary)
class EvidenceSummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "query", "confidence", "ai_provider", "citation_count", "created_at")
    date_hierarchy = "created_at"


@admin.register(KnowledgeGap)
class KnowledgeGapAdmin(admin.ModelAdmin):
    list_display = ("title", "gap_type", "priority", "disease_id", "is_addressed")
    list_filter = ("gap_type", "priority", "is_addressed")
    search_fields = ("title",)
