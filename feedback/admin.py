from django.contrib import admin
from .models import (
    ErrorLog, CrashReport, ClinicalConflict, KnowledgeConflict,
    AIFailureLog, RuleFailureLog, UserFeedback, WorkflowFeedback,
    PerformanceLog, KnowledgeImprovementSuggestion, FeedbackExport,
    FeedbackConfig, TelemetrySettings, ErrorOccurrence, UploadBatch,
)


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "severity", "error_type", "module", "recovered_automatically")
    list_filter = ("severity", "recovered_automatically")
    search_fields = ("error_type", "module", "stack_trace")
    date_hierarchy = "timestamp"


@admin.register(CrashReport)
class CrashReportAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "exception_type", "module", "app_version")
    list_filter = ("exception_type",)
    search_fields = ("exception_type", "module", "stack_trace")
    date_hierarchy = "timestamp"


@admin.register(ClinicalConflict)
class ClinicalConflictAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "disease", "ai_confidence", "resolved")
    list_filter = ("disease", "resolved")
    search_fields = ("disease", "ai_recommendation", "clinician_decision")
    date_hierarchy = "timestamp"


@admin.register(KnowledgeConflict)
class KnowledgeConflictAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "conflict_type", "disease", "severity", "resolved")
    list_filter = ("conflict_type", "severity", "resolved")
    search_fields = ("description",)
    date_hierarchy = "timestamp"


@admin.register(AIFailureLog)
class AIFailureLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "failure_type", "disease", "confidence")
    list_filter = ("failure_type",)
    search_fields = ("disease",)
    date_hierarchy = "timestamp"


@admin.register(RuleFailureLog)
class RuleFailureLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "rule_id", "disease", "missing_feature")
    list_filter = ("disease",)
    search_fields = ("rule_id", "exception_message")
    date_hierarchy = "timestamp"


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "feedback_type", "title", "user", "resolved")
    list_filter = ("feedback_type", "resolved")
    search_fields = ("title", "description")
    date_hierarchy = "created_at"


@admin.register(WorkflowFeedback)
class WorkflowFeedbackAdmin(admin.ModelAdmin):
    list_display = ("created_at", "feedback_type", "rating", "user")
    list_filter = ("feedback_type", "rating")
    search_fields = ("comments",)
    date_hierarchy = "created_at"


@admin.register(PerformanceLog)
class PerformanceLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "metric_name", "duration_ms", "module", "page")
    list_filter = ("metric_name",)
    search_fields = ("module", "page")
    date_hierarchy = "timestamp"


@admin.register(KnowledgeImprovementSuggestion)
class KnowledgeImprovementSuggestionAdmin(admin.ModelAdmin):
    list_display = ("created_at", "rule_id", "disease", "override_count", "status")
    list_filter = ("status", "disease")
    search_fields = ("rule_id",)
    date_hierarchy = "created_at"


@admin.register(FeedbackExport)
class FeedbackExportAdmin(admin.ModelAdmin):
    list_display = ("filename", "exported_at", "exported_by", "size_bytes", "date_from", "date_to")
    readonly_fields = ("exported_at", "exported_by", "export_hash")
    date_hierarchy = "exported_at"


@admin.register(FeedbackConfig)
class FeedbackConfigAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key",)


@admin.register(TelemetrySettings)
class TelemetrySettingsAdmin(admin.ModelAdmin):
    list_display = ("enabled", "sync_interval", "github_repo", "last_upload", "pending_count")

    def has_add_permission(self, request):
        return not TelemetrySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ErrorOccurrence)
class ErrorOccurrenceAdmin(admin.ModelAdmin):
    list_display = ("fingerprint", "severity", "exception_type", "module",
                    "occurrence_count", "queue_state", "github_issue_number", "last_seen")
    list_filter = ("severity", "queue_state")
    search_fields = ("exception_type", "module", "stack_trace")
    date_hierarchy = "last_seen"
    readonly_fields = ("fingerprint", "first_seen", "occurrence_count",
                       "github_issue_number", "github_issue_url")


@admin.register(UploadBatch)
class UploadBatchAdmin(admin.ModelAdmin):
    list_display = ("started_at", "state", "errors_uploaded", "errors_failed",
                    "trigger")
    list_filter = ("state", "trigger")
    date_hierarchy = "started_at"
    readonly_fields = ("started_at", "finished_at", "log_output")
