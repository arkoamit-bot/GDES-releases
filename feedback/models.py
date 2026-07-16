import hashlib
import logging
from django.conf import settings
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


def hash_id(value: str | int | None) -> str | None:
    if value is None:
        return None
    return hashlib.sha256(str(value).encode()).hexdigest()[:16]


class FeedbackConfig(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)

    class Meta:
        verbose_name = "Feedback Configuration"
        verbose_name_plural = "Feedback Configurations"

    def __str__(self):
        return f"{self.key} = {self.value[:60]}"


class ErrorLog(models.Model):
    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    ]

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    app_version = models.CharField(max_length=50, blank=True)
    knowledge_version = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=200, blank=True)
    db_version = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    module = models.CharField(max_length=100, blank=True, db_index=True)
    page = models.CharField(max_length=500, blank=True)
    action = models.CharField(max_length=200, blank=True)
    stack_trace = models.TextField(blank=True)
    error_type = models.CharField(max_length=200, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="error")
    recovered_automatically = models.BooleanField(default=False)
    request_data = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Error Log"
        verbose_name_plural = "Error Logs"
        indexes = [
            models.Index(fields=["severity", "timestamp"]),
            models.Index(fields=["module", "error_type"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.error_type} @ {self.timestamp:%Y-%m-%d %H:%M}"


class CrashReport(models.Model):
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    exception_type = models.CharField(max_length=200)
    exception_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    module = models.CharField(max_length=100, blank=True)
    patient_id_hash = models.CharField(max_length=64, blank=True)
    encounter_id_hash = models.CharField(max_length=64, blank=True)
    url = models.CharField(max_length=1000, blank=True)
    workflow = models.CharField(max_length=200, blank=True)
    memory_usage_mb = models.FloatField(null=True, blank=True)
    recent_actions = models.JSONField(null=True, blank=True)
    app_version = models.CharField(max_length=50, blank=True)
    knowledge_version = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = "Crash Report"
        verbose_name_plural = "Crash Reports"
        indexes = [
            models.Index(fields=["exception_type", "timestamp"]),
            models.Index(fields=["module"]),
        ]

    def __str__(self):
        return f"Crash: {self.exception_type} @ {self.timestamp:%Y-%m-%d %H:%M}"


class ClinicalConflict(models.Model):
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    patient_id_hash = models.CharField(max_length=64, blank=True, db_index=True)
    disease = models.CharField(max_length=100, blank=True, db_index=True)
    ai_recommendation = models.TextField(blank=True)
    clinician_decision = models.TextField(blank=True)
    difference = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    guideline_ref = models.CharField(max_length=200, blank=True)
    knowledge_rule_id = models.CharField(max_length=50, blank=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Clinical Conflict"
        verbose_name_plural = "Clinical Conflicts"
        indexes = [
            models.Index(fields=["disease", "resolved"]),
            models.Index(fields=["knowledge_rule_id"]),
        ]

    def __str__(self):
        return f"Conflict: {self.disease} @ {self.timestamp:%Y-%m-%d}"


class KnowledgeConflict(models.Model):
    CONFLICT_TYPES = [
        ("recommendation_vs_guideline", "Recommendation vs Guideline"),
        ("treatment_vs_contraindication", "Treatment vs Contraindication"),
        ("biopsy_vs_diagnosis", "Biopsy vs Diagnosis"),
        ("diagnosis_vs_pathology", "Diagnosis vs Pathology"),
        ("ckd_vs_egfr", "CKD Stage vs eGFR"),
        ("drug_contraindication", "Drug Contraindication"),
        ("duplicate_diagnosis", "Duplicate Diagnosis"),
        ("missing_followup", "Missing Follow-up"),
        ("missing_investigation", "Missing Investigation"),
    ]
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    conflict_type = models.CharField(max_length=50, choices=CONFLICT_TYPES, db_index=True)
    patient_id_hash = models.CharField(max_length=64, blank=True)
    disease = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    rule_id_a = models.CharField(max_length=50, blank=True)
    rule_id_b = models.CharField(max_length=50, blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="medium")
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Knowledge Conflict"
        verbose_name_plural = "Knowledge Conflicts"
        indexes = [
            models.Index(fields=["conflict_type", "severity"]),
            models.Index(fields=["disease"]),
        ]

    def __str__(self):
        return f"{self.get_conflict_type_display()} ({self.severity})"


class AIFailureLog(models.Model):
    FAILURE_TYPES = [
        ("diagnosis", "Diagnosis"),
        ("treatment", "Treatment"),
        ("monitoring", "Monitoring"),
        ("investigation", "Investigation"),
    ]

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    failure_type = models.CharField(max_length=20, choices=FAILURE_TYPES, db_index=True)
    patient_id_hash = models.CharField(max_length=64, blank=True)
    disease = models.CharField(max_length=100, blank=True)
    missing_data = models.JSONField(null=True, blank=True)
    reasoning_chain = models.JSONField(null=True, blank=True)
    rules_evaluated = models.JSONField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    knowledge_version = models.CharField(max_length=50, blank=True)
    evidence_retrieved = models.JSONField(null=True, blank=True)
    ai_output = models.TextField(blank=True)

    class Meta:
        verbose_name = "AI Failure Log"
        verbose_name_plural = "AI Failure Logs"
        indexes = [
            models.Index(fields=["failure_type", "confidence"]),
            models.Index(fields=["disease"]),
        ]

    def __str__(self):
        return f"AI Failure: {self.get_failure_type_display()} (conf={self.confidence})"


class RuleFailureLog(models.Model):
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    rule_id = models.CharField(max_length=50, db_index=True)
    disease = models.CharField(max_length=100, blank=True)
    condition = models.JSONField(null=True, blank=True)
    missing_feature = models.CharField(max_length=200, blank=True)
    exception_message = models.TextField(blank=True)
    knowledge_version = models.CharField(max_length=50, blank=True)
    patient_feature_summary = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Rule Failure Log"
        verbose_name_plural = "Rule Failure Logs"
        indexes = [
            models.Index(fields=["rule_id", "timestamp"]),
            models.Index(fields=["disease"]),
        ]

    def __str__(self):
        return f"Rule Failure: {self.rule_id}"


class UserFeedback(models.Model):
    FEEDBACK_TYPES = [
        ("software_bug", "Software Bug"),
        ("incorrect_recommendation", "Incorrect Recommendation"),
        ("missing_guideline", "Missing Guideline"),
        ("workflow_issue", "Workflow Issue"),
        ("ui_issue", "UI Issue"),
        ("suggestion", "Suggestion"),
        ("feature_request", "Feature Request"),
        ("clinical_concern", "Clinical Concern"),
    ]

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES, db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    screenshot = models.ImageField(upload_to="feedback_screenshots/", null=True, blank=True)
    page_url = models.CharField(max_length=1000, blank=True)
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "User Feedback"
        verbose_name_plural = "User Feedback"
        indexes = [
            models.Index(fields=["feedback_type", "resolved"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"[{self.get_feedback_type_display()}] {self.title[:60]}"


class WorkflowFeedback(models.Model):
    FEEDBACK_TYPES = [
        ("diagnosis", "Diagnosis Suggestions"),
        ("treatment_plan", "Treatment Plans"),
        ("followup_plan", "Follow-up Plans"),
        ("investigation_plan", "Investigation Plans"),
        ("clinical_reasoning", "Clinical Reasoning"),
    ]

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.SET_NULL, null=True, blank=True,
    )
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES, db_index=True)
    rating = models.PositiveSmallIntegerField(default=0)
    # V8 Layer 10: explicit nephrologist decision on a recommendation. Structured
    # learning data — NEVER auto-applied to the production knowledge base.
    ACTION_CHOICES = [
        ("accept", "Accepted"),
        ("modify", "Modified"),
        ("reject", "Rejected"),
    ]
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, blank=True, db_index=True)
    recommendation_ref = models.CharField(
        max_length=120, blank=True,
        help_text="What the feedback is about (e.g. differential:iga, management_plan:membranous).")
    comments = models.TextField(blank=True)
    recommendation_audit = models.ForeignKey(
        "knowledge.RecommendationAudit", on_delete=models.SET_NULL,
        null=True, blank=True,
    )

    class Meta:
        verbose_name = "Workflow Feedback"
        verbose_name_plural = "Workflow Feedback"
        indexes = [
            models.Index(fields=["feedback_type", "rating"]),
            models.Index(fields=["action", "feedback_type"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self):
        return f"{self.get_feedback_type_display()}: {self.rating} stars"


class PerformanceLog(models.Model):
    METRIC_CHOICES = [
        ("startup_time", "Application Startup Time"),
        ("knowledge_loading", "Knowledge Loading Time"),
        ("reasoning_time", "Clinical Reasoning Time"),
        ("patient_loading", "Patient Loading Time"),
        ("db_query", "Database Query Duration"),
        ("slow_page", "Slow Page Load"),
        ("memory_usage", "Memory Usage"),
        ("cpu_usage", "CPU Usage"),
    ]

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    metric_name = models.CharField(max_length=30, choices=METRIC_CHOICES, db_index=True)
    duration_ms = models.FloatField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True, help_text="Numeric value for non-duration metrics (MB, %, etc.)")
    module = models.CharField(max_length=100, blank=True)
    page = models.CharField(max_length=500, blank=True)
    url = models.CharField(max_length=1000, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    metadata = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Performance Log"
        verbose_name_plural = "Performance Logs"
        indexes = [
            models.Index(fields=["metric_name", "timestamp"]),
            models.Index(fields=["module"]),
        ]

    def __str__(self):
        if self.duration_ms is not None:
            return f"{self.get_metric_name_display()}: {self.duration_ms:.0f}ms"
        return f"{self.get_metric_name_display()} @ {self.timestamp:%H:%M}"


class KnowledgeImprovementSuggestion(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    rule_id = models.CharField(max_length=50, db_index=True)
    disease = models.CharField(max_length=100, blank=True, db_index=True)
    override_count = models.PositiveIntegerField(default=0)
    common_override_reason = models.TextField(blank=True)
    current_recommendation = models.TextField(blank=True)
    suggested_change = models.TextField(blank=True)
    supporting_evidence = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reviewed_suggestions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Knowledge Improvement Suggestion"
        verbose_name_plural = "Knowledge Improvement Suggestions"
        indexes = [
            models.Index(fields=["status", "override_count"]),
            models.Index(fields=["disease", "rule_id"]),
        ]

    def __str__(self):
        return f"Suggestion: {self.rule_id} (x{self.override_count})"


class FeedbackExport(models.Model):
    exported_at = models.DateTimeField(default=timezone.now)
    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
    )
    filename = models.CharField(max_length=500)
    size_bytes = models.IntegerField(null=True, blank=True)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    included_sections = models.JSONField(default=list)
    export_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "Feedback Export"
        verbose_name_plural = "Feedback Exports"
        ordering = ["-exported_at"]

    def __str__(self):
        return self.filename


# --------------------------------------------------------------------------- #
# Automated GitHub Error Reporting System
# --------------------------------------------------------------------------- #

class TelemetrySettings(models.Model):
    SYNC_CHOICES = [
        ("hourly", "Hourly"),
        ("6h", "Every 6 Hours"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("manual", "Manual Only"),
    ]

    enabled = models.BooleanField(default=True, help_text="Enable automatic error reporting")
    sync_interval = models.CharField(max_length=10, choices=SYNC_CHOICES, default="daily")
    auto_crash_reporting = models.BooleanField(default=True)
    auto_performance_reporting = models.BooleanField(default=False)
    github_repo = models.CharField(
        max_length=200, default="arkoamit-bot/GDES",
        help_text="GitHub repo for issue reporting (owner/repo)",
    )
    github_token = models.CharField(
        max_length=200, blank=True,
        help_text="GitHub Personal Access Token (stored locally)",
    )
    last_upload = models.DateTimeField(null=True, blank=True)
    pending_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Telemetry Settings"
        verbose_name_plural = "Telemetry Settings"

    def __str__(self):
        return f"Telemetry: {'ON' if self.enabled else 'OFF'} ({self.sync_interval})"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ErrorOccurrence(models.Model):
    """Deduplicated error fingerprint — one row per unique error signature."""
    SEVERITY_CHOICES = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    ]
    QUEUE_STATE_CHOICES = [
        ("pending", "Pending"),
        ("uploaded", "Uploaded"),
        ("failed", "Failed"),
        ("ignored", "Ignored"),
    ]

    fingerprint = models.CharField(max_length=64, unique=True, db_index=True,
        help_text="SHA-256 of (exception_type + module + line + stack_hash)")
    exception_type = models.CharField(max_length=200, db_index=True)
    exception_message = models.TextField(blank=True)
    module = models.CharField(max_length=200, blank=True, db_index=True)
    function_name = models.CharField(max_length=200, blank=True)
    line_number = models.PositiveIntegerField(null=True, blank=True)
    stack_trace = models.TextField(blank=True)
    stack_hash = models.CharField(max_length=64, blank=True,
        help_text="Hash of the de-parameterized stack trace")

    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default="error")
    occurrence_count = models.PositiveIntegerField(default=1)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)

    queue_state = models.CharField(max_length=10, choices=QUEUE_STATE_CHOICES,
        default="pending", db_index=True)
    github_issue_number = models.PositiveIntegerField(null=True, blank=True)
    github_issue_url = models.CharField(max_length=500, blank=True)
    last_upload_attempt = models.DateTimeField(null=True, blank=True)
    upload_fail_count = models.PositiveIntegerField(default=0)

    app_version = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=200, blank=True)
    python_version = models.CharField(max_length=50, blank=True)
    django_version = models.CharField(max_length=50, blank=True)

    sample_context = models.JSONField(null=True, blank=True,
        help_text="Sanitized request context from the most recent occurrence")

    class Meta:
        verbose_name = "Error Occurrence"
        verbose_name_plural = "Error Occurrences"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["queue_state", "severity"]),
            models.Index(fields=["exception_type", "module"]),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.exception_type} x{self.occurrence_count}"


class UploadBatch(models.Model):
    """Record of each synchronization attempt."""
    STATE_CHOICES = [
        ("running", "Running"),
        ("success", "Success"),
        ("partial", "Partial"),
        ("failed", "Failed"),
    ]

    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default="running")
    errors_uploaded = models.PositiveIntegerField(default=0)
    errors_failed = models.PositiveIntegerField(default=0)
    errors_skipped = models.PositiveIntegerField(default=0)
    trigger = models.CharField(max_length=50, default="scheduled",
        help_text="scheduled | manual | startup | critical")
    log_output = models.TextField(blank=True)

    class Meta:
        verbose_name = "Upload Batch"
        verbose_name_plural = "Upload Batches"
        ordering = ["-started_at"]

    def __str__(self):
        return f"Upload {self.started_at:%Y-%m-%d %H:%M} ({self.state})"
