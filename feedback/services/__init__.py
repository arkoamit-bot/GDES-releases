"""feedback.services package — re-exports the original export/summary functions
plus the new automated error reporting submodules."""
from __future__ import annotations

import json
import os
import sys
import zipfile
import io
import hashlib
import platform
from datetime import datetime

from django.db import models as django_models
from django.utils import timezone
from django.conf import settings

from bgddr.version import __version__ as app_version
from knowledge.kb_version import PACKAGED_KB_VERSION


SERIALIZER_REGISTRY = {}


def register_serializer(model_class):
    def wrapper(func):
        SERIALIZER_REGISTRY[model_class] = func
        return func
    return wrapper


def patient_fields_to_remove():
    return [
        "patient_name", "name", "full_name", "first_name", "last_name",
        "hospital_id", "mrn", "phone", "mobile", "telephone",
        "address", "street", "city", "postcode", "zip",
        "national_id", "nid", "ssn", "email", "date_of_birth", "dob",
    ]


def strip_pii(obj):
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            kl = k.lower()
            if any(p in kl for p in ["patient", "name", "phone", "address", "email", "nid", "ssn", "mrn", "hospital_id"]):
                continue
            if kl in patient_fields_to_remove() or any(p == kl for p in ["dob", "date_of_birth"]):
                continue
            cleaned[k] = strip_pii(v)
        return cleaned
    if isinstance(obj, list):
        return [strip_pii(item) for item in obj]
    return obj


def model_to_safe_dict(instance, seen=None):
    if seen is None:
        seen = set()
    obj_id = id(instance)
    if obj_id in seen:
        return {"_ref": str(instance)}
    seen.add(obj_id)
    data = {}
    for field in instance._meta.get_fields():
        if field.is_relation:
            continue
        val = getattr(instance, field.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        data[field.name] = val
    return data


def export_feedback_package(date_from=None, date_to=None):
    from .models import (
        ErrorLog, ClinicalConflict, PerformanceLog, AIFailureLog,
        KnowledgeConflict, UserFeedback, WorkflowFeedback, RuleFailureLog,
        KnowledgeImprovementSuggestion,
    )

    filters = {}
    if date_from:
        filters["timestamp__gte"] = date_from
    if date_to:
        filters["timestamp__lte"] = date_to

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        sections = []

        datasets = {
            "errors.json": ErrorLog.objects.filter(**filters).order_by("timestamp"),
            "conflicts.json": ClinicalConflict.objects.filter(**filters).order_by("timestamp"),
            "performance.json": PerformanceLog.objects.filter(**filters).order_by("timestamp"),
            "ai_failures.json": AIFailureLog.objects.filter(**filters).order_by("timestamp"),
            "knowledge_conflicts.json": KnowledgeConflict.objects.filter(**filters).order_by("timestamp"),
            "user_feedback.json": UserFeedback.objects.order_by("created_at"),
            "workflow_feedback.json": WorkflowFeedback.objects.order_by("created_at"),
            "rule_failures.json": RuleFailureLog.objects.filter(**filters).order_by("timestamp"),
            "improvement_suggestions.json": KnowledgeImprovementSuggestion.objects.order_by("created_at"),
        }

        for filename, qs in datasets.items():
            records = []
            for obj in qs:
                d = model_to_safe_dict(obj)
                records.append(strip_pii(d))
            zf.writestr(f"logs/{filename}", json.dumps(records, indent=2, default=str))
            sections.append(filename.replace(".json", ""))

        env_info = {
            "app_version": app_version,
            "knowledge_version": PACKAGED_KB_VERSION,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "system": platform.system(),
            "django_settings": settings.SETTINGS_MODULE,
            "timezone": settings.TIME_ZONE,
            "exported_at": timezone.now().isoformat(),
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
        }
        zf.writestr("environment.json", json.dumps(env_info, indent=2))

        sys_info = {
            "modules": sorted([m for m in sys.modules.keys() if not m.startswith("_")]),
        }
        zf.writestr("system_information.json", json.dumps(sys_info))

        manifest = {
            "exported_at": timezone.now().isoformat(),
            "app_version": app_version,
            "knowledge_version": PACKAGED_KB_VERSION,
            "build_number": app_version,
            "guideline_version": "KDIGO 2021/2024/2025",
            "sections": sections,
            "record_counts": {s: len(datasets[f"{s}.json"]) for s in sections},
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return buf, manifest


def generate_improvement_suggestions():
    from django.db.models import Count, Q
    from .models import ClinicalConflict, KnowledgeImprovementSuggestion

    suggestions = []
    conflicts = (
        ClinicalConflict.objects
        .filter(resolved=False)
        .values("knowledge_rule_id", "disease")
        .annotate(count=Count("id"))
        .filter(count__gte=3)
    )

    for c in conflicts:
        rule_id = c["knowledge_rule_id"]
        if not rule_id:
            continue
        disease = c["disease"]
        override_count = c["count"]

        sample = ClinicalConflict.objects.filter(
            knowledge_rule_id=rule_id, disease=disease
        ).exclude(reason="").values("reason").annotate(cnt=Count("id")).order_by("-cnt").first()

        suggestion, created = KnowledgeImprovementSuggestion.objects.get_or_create(
            rule_id=rule_id,
            disease=disease,
            defaults={
                "override_count": override_count,
                "common_override_reason": sample["reason"] if sample else "",
                "status": "pending",
            },
        )
        if not created and suggestion.status == "pending":
            suggestion.override_count = override_count
            if sample:
                suggestion.common_override_reason = sample["reason"]
            suggestion.save(update_fields=["override_count", "common_override_reason"])

        suggestions.append(suggestion)

    return suggestions


def generate_summary_report():
    from .models import (
        ErrorLog, CrashReport, ClinicalConflict, KnowledgeConflict,
        AIFailureLog, RuleFailureLog, UserFeedback, PerformanceLog,
        KnowledgeImprovementSuggestion, WorkflowFeedback,
    )
    from django.db.models import Count

    now = timezone.now()

    report = {
        "generated_at": now.isoformat(),
        "app_version": app_version,
        "knowledge_version": PACKAGED_KB_VERSION,
        "critical_bugs": list(
            CrashReport.objects.values("exception_type")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "ai_disagreements": list(
            ClinicalConflict.objects.values("disease")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "most_overridden": list(
            ClinicalConflict.objects.values("knowledge_rule_id", "disease")
            .annotate(count=Count("id"))
            .filter(count__gte=2)
            .order_by("-count")[:10]
        ),
        "knowledge_conflicts": list(
            KnowledgeConflict.objects.values("conflict_type", "severity")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "ai_failures_by_type": list(
            AIFailureLog.objects.values("failure_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
        "top_failing_rules": list(
            RuleFailureLog.objects.values("rule_id", "disease")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "user_feedback_by_type": list(
            UserFeedback.objects.values("feedback_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        ),
        "workflow_ratings": {
            str(ft): list(
                WorkflowFeedback.objects.filter(feedback_type=ft)
                .values("rating")
                .annotate(count=Count("id"))
                .order_by("rating")
            )
            for ft, _ in WorkflowFeedback.FEEDBACK_TYPES
        },
        "slow_pages": list(
            PerformanceLog.objects.filter(metric_name="slow_page")
            .values("page")
            .annotate(
                avg_ms=django_models.Avg("duration_ms"),
                count=Count("id"),
            )
            .order_by("-avg_ms")[:10]
        ),
        "improvement_suggestions": {
            "pending": KnowledgeImprovementSuggestion.objects.filter(status="pending").count(),
            "under_review": KnowledgeImprovementSuggestion.objects.filter(status="under_review").count(),
            "approved": KnowledgeImprovementSuggestion.objects.filter(status="approved").count(),
            "rejected": KnowledgeImprovementSuggestion.objects.filter(status="rejected").count(),
        },
        "knowledge_gaps": list(
            AIFailureLog.objects.values("disease")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
    }
    return report
