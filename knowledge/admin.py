"""Admin configuration for the Knowledge Platform."""
from datetime import date

from django.contrib import admin, messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from .models import (
    GuidelineSource, KnowledgeBaseEntry, KnowledgeBaseVersion,
    RuleTemplate, RuleReview, RuleTestResult, GuidelineDocument, EvidenceEntry,
    Disease, ClinicalCase, ClinicalPathway,
    Syndrome, PathologyEntity, LabEntity, DrugIntelligence,
    MonitoringProtocol, Complication,
    KnowledgeGraphNode, KnowledgeGraphEdge,
    RecommendationAudit,
)


@admin.register(GuidelineSource)
class GuidelineSourceAdmin(admin.ModelAdmin):
    list_display = ["abbreviation", "version_year", "title", "effective_date"]
    list_filter = ["abbreviation"]


@admin.register(KnowledgeBaseEntry)
class KnowledgeBaseEntryAdmin(admin.ModelAdmin):
    list_display = ["entry_id", "disease_id", "source", "rule_type", "evidence_grade", "status", "effective_date"]
    list_filter = ["status", "disease_id", "evidence_grade", "rule_type"]
    search_fields = ["entry_id", "disease_id"]
    actions = ["transition_to_under_review", "transition_to_active", "transition_to_retired"]
    change_list_template = "admin/knowledge/knowledgebaseentry/change_list.html"

    # --- Update from downloaded guideline file --------------------------------
    def get_urls(self):
        custom = [
            path(
                "update-from-file/",
                self.admin_site.admin_view(self.update_from_file_view),
                name="knowledge_knowledgebaseentry_update_from_file",
            ),
            path(
                "import-guideline-reference/",
                self.admin_site.admin_view(self.import_guideline_reference_view),
                name="knowledge_knowledgebaseentry_import_guideline_reference",
            ),
        ]
        return custom + super().get_urls()

    def import_guideline_reference_view(self, request):
        """Store a guideline PDF/text as a citable reference (no rules created)."""
        from .guideline_reference import (
            import_guideline_reference,
            import_guideline_reference_from_url,
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Import guideline (reference)",
            "opts": self.model._meta,
        }
        if request.method == "POST":
            upload = request.FILES.get("file")
            url = (request.POST.get("url") or "").strip()
            abbreviation = (request.POST.get("abbreviation") or "").strip()
            year = (request.POST.get("version_year") or "").strip()
            doc_title = (request.POST.get("doc_title") or "").strip()
            try:
                year_int = int(year) if year else 0
                if upload:
                    summary = import_guideline_reference(
                        raw=upload.read(), abbreviation=abbreviation,
                        version_year=year_int, title=doc_title,
                        filename=upload.name, content_type=upload.content_type or "",
                    )
                elif url:
                    summary = import_guideline_reference_from_url(
                        url, abbreviation=abbreviation, version_year=year_int,
                        title=doc_title,
                    )
                else:
                    self.message_user(request, "Choose a file or paste a link.",
                                      level=messages.ERROR)
                    return TemplateResponse(
                        request, "admin/knowledge/kb_guideline_reference_form.html", context)
            except Exception as exc:  # noqa: BLE001
                self.message_user(request, f"Import failed: {exc}", level=messages.ERROR)
            else:
                self.message_user(
                    request,
                    f"Stored guideline reference “{summary['document_title']}” "
                    f"({summary['pages']} page(s), {summary['chars']:,} characters) "
                    f"under source {summary['source']}. No rules were created — "
                    f"cite it from a rule via its evidence fields.",
                    level=messages.SUCCESS,
                )
                return redirect("admin:knowledge_guidelinedocument_changelist")
        return TemplateResponse(
            request, "admin/knowledge/kb_guideline_reference_form.html", context)

    def update_from_file_view(self, request):
        """Import a guideline export (JSON) from an upload OR a web link; as DRAFT."""
        from .kb_update import import_kb_text, import_kb_url

        context = {
            **self.admin_site.each_context(request),
            "title": "Update knowledge base from file or link",
            "opts": self.model._meta,
        }
        if request.method == "POST":
            upload = request.FILES.get("file")
            url = (request.POST.get("url") or "").strip()
            try:
                if upload:
                    source_label = upload.name
                    summary = import_kb_text(upload.read().decode("utf-8"))
                elif url:
                    source_label = url
                    summary = import_kb_url(url)
                else:
                    self.message_user(request, "Choose a file or paste a web link to import.",
                                      level=messages.ERROR)
                    return TemplateResponse(request, "admin/knowledge/kb_update_form.html", context)
            except Exception as exc:  # noqa: BLE001
                self.message_user(request, f"Import failed: {exc}", level=messages.ERROR)
            else:
                self.message_user(
                    request,
                    f"Imported from '{source_label}': {summary['created']} new and "
                    f"{summary['updated']} changed rule(s) saved as DRAFT for review; "
                    f"{summary['unchanged']} unchanged, {summary['errors']} error(s). "
                    f"Review the DRAFT entries, then use “Move to ACTIVE” to publish.",
                    level=messages.WARNING if summary["errors"] else messages.SUCCESS,
                )
                for err in summary["error_details"]:
                    self.message_user(request, f"• {err}", level=messages.WARNING)
                return redirect("admin:knowledge_knowledgebaseentry_changelist")
        return TemplateResponse(request, "admin/knowledge/kb_update_form.html", context)

    @admin.action(description="Move selected entries to UNDER_REVIEW")
    def transition_to_under_review(self, request, queryset):
        count = 0
        for entry in queryset:
            try:
                entry.transition_to("under_review", user=request.user)
                count += 1
            except ValueError:
                pass
        self.message_user(request, f"Moved {count} entries to UNDER_REVIEW.")

    @admin.action(description="Move selected entries to ACTIVE (via proper lifecycle)")
    def transition_to_active(self, request, queryset):
        count = 0
        for entry in queryset:
            try:
                entry.transition_to("active", user=request.user)
                count += 1
            except ValueError:
                pass
        self.message_user(request, f"Activated {count} entries.")

    @admin.action(description="Move selected entries to RETIRED")
    def transition_to_retired(self, request, queryset):
        count = 0
        for entry in queryset:
            try:
                entry.transition_to("retired", user=request.user)
                count += 1
            except ValueError:
                pass
        self.message_user(request, f"Retired {count} entries.")


@admin.register(KnowledgeBaseVersion)
class KnowledgeBaseVersionAdmin(admin.ModelAdmin):
    list_display = ["entry", "version_number", "change_summary", "changed_by", "created_at"]
    list_filter = ["created_at"]


@admin.register(RuleTemplate)
class RuleTemplateAdmin(admin.ModelAdmin):
    list_display = ["template_id", "name", "category"]
    list_filter = ["category"]
    search_fields = ["template_id", "name"]


@admin.register(RuleReview)
class RuleReviewAdmin(admin.ModelAdmin):
    list_display = ["entry", "status", "reviewer", "created_at"]
    list_filter = ["status"]
    search_fields = ["entry__entry_id"]


@admin.register(RuleTestResult)
class RuleTestResultAdmin(admin.ModelAdmin):
    list_display = ["entry", "test_name", "actual_score", "matched", "created_at"]
    list_filter = ["matched", "created_at"]
    search_fields = ["entry__entry_id", "test_name"]


@admin.register(GuidelineDocument)
class GuidelineDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "source", "document_type", "import_status", "imported_at"]
    list_filter = ["import_status", "document_type"]


@admin.register(EvidenceEntry)
class EvidenceEntryAdmin(admin.ModelAdmin):
    list_display = ["title", "entry", "evidence_level", "year", "journal"]
    list_filter = ["evidence_level", "year"]
    search_fields = ["title", "authors", "doi"]


# KnowledgeBaseEntryAdmin is registered via @admin.register decorator above


# ─── V4.0 Disease Knowledge Admin ─────────────────────────────────────


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category", "is_active", "updated_at"]
    list_filter = ["category", "is_active"]
    search_fields = ["id", "name", "definition"]
    fieldsets = [
        ("Identity", {"fields": ["id", "name", "category", "parent_disease", "is_active"]}),
        ("Core Knowledge", {"fields": ["definition", "epidemiology", "etiology", "pathophysiology", "clinical_presentation"]}),
        ("Diagnostic Framework", {"fields": ["diagnostic_criteria", "differential_diagnosis", "lab_findings", "biopsy_findings"]}),
        ("Classification", {"fields": ["classification_systems", "risk_stratification"]}),
        ("Management", {"fields": ["treatment_overview", "treatment_algorithms", "monitoring_protocol"]}),
        ("Outcomes", {"fields": ["complications", "relapse_information", "long_term_prognosis"]}),
        ("Governance", {"fields": ["evidence_summary", "guideline_recommendations", "key_references", "notes"]}),
    ]


@admin.register(ClinicalCase)
class ClinicalCaseAdmin(admin.ModelAdmin):
    list_display = ["case_id", "title", "disease", "presentation_type", "status", "is_gold_standard"]
    list_filter = ["disease", "presentation_type", "status", "is_gold_standard"]
    search_fields = ["case_id", "title", "diagnosis"]


@admin.register(ClinicalPathway)
class ClinicalPathwayAdmin(admin.ModelAdmin):
    list_display = ["stage_id", "disease", "stage_name", "stage_order", "is_active"]
    list_filter = ["disease", "is_active"]
    search_fields = ["stage_id", "stage_name", "disease__name"]


# ─── V4.0 Knowledge Quality Dashboard ─────────────────────────────────


class KnowledgeQualityDashboard(admin.AdminSite):
    """Admin site extension for knowledge quality metrics."""
    site_header = "Knowledge Quality Dashboard"
    site_title = "GDES Knowledge Quality"


def knowledge_dashboard_view(request):
    """Admin view showing knowledge quality metrics."""
    from datetime import timedelta

    total_diseases = Disease.objects.filter(is_active=True).count()
    total_rules = KnowledgeBaseEntry.objects.count()
    active_rules = KnowledgeBaseEntry.objects.filter(status=KnowledgeBaseEntry.Status.ACTIVE).count()
    draft_rules = KnowledgeBaseEntry.objects.filter(status=KnowledgeBaseEntry.Status.DRAFT).count()
    total_cases = ClinicalCase.objects.count()
    gold_cases = ClinicalCase.objects.filter(is_gold_standard=True).count()
    total_sources = GuidelineSource.objects.count()
    total_evidence = EvidenceEntry.objects.count()
    total_pathways = ClinicalPathway.objects.filter(is_active=True).count()
    rules_with_evidence = KnowledgeBaseEntry.objects.filter(evidence_entries__isnull=False).distinct().count()
    rules_with_guidelines = KnowledgeBaseEntry.objects.exclude(guideline_chapter="").count()
    reviewed_rules = KnowledgeBaseEntry.objects.exclude(review_notes="").count()

    disease_coverage = list(
        Disease.objects.filter(is_active=True).values("category")
        .annotate(count=Count("id"))
        .order_by("category")
    )
    rules_per_disease = list(
        KnowledgeBaseEntry.objects.values("disease_id")
        .annotate(count=Count("id"))
        .order_by("-count")
    )

    health_score = 0
    if total_diseases > 0:
        disease_score = min(100, total_diseases * 4)
        if total_rules > 0:
            active_pct = active_rules / total_rules * 100
        else:
            active_pct = 0
        evidence_score = min(100, rules_with_evidence / max(total_rules, 1) * 100 * 2)
        coverage_score = min(100, disease_score * 0.4 + active_pct * 0.3 + evidence_score * 0.3)
        health_score = round(coverage_score, 1)

    context = {
        "title": "Knowledge Quality Dashboard",
        "total_diseases": total_diseases,
        "total_rules": total_rules,
        "active_rules": active_rules,
        "draft_rules": draft_rules,
        "active_pct": round(active_rules / max(total_rules, 1) * 100, 1),
        "total_cases": total_cases,
        "gold_cases": gold_cases,
        "total_sources": total_sources,
        "total_evidence": total_evidence,
        "total_pathways": total_pathways,
        "rules_with_evidence": rules_with_evidence,
        "rules_with_evidence_pct": round(rules_with_evidence / max(total_rules, 1) * 100, 1),
        "rules_with_guidelines": rules_with_guidelines,
        "reviewed_rules": reviewed_rules,
        "disease_coverage": disease_coverage,
        "rules_per_disease": rules_per_disease,
        "health_score": health_score,
    }
    return TemplateResponse(request, "admin/knowledge_dashboard.html", context)


# Patch dashboard URL onto the existing KnowledgeBaseEntryAdmin
admin.site.register_view = lambda: path(
    "knowledge-dashboard/", knowledge_dashboard_view, name="knowledge_dashboard"
)


# ─── V4.2 Reusable Knowledge Objects Admin ────────────────────────────────


@admin.register(Syndrome)
class SyndromeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["id", "name", "definition"]
    filter_horizontal = ["associated_diseases"]


@admin.register(PathologyEntity)
class PathologyEntityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["id", "name", "definition"]
    filter_horizontal = ["associated_diseases"]


@admin.register(LabEntity)
class LabEntityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["id", "name", "interpretation"]
    filter_horizontal = ["associated_diseases"]


@admin.register(DrugIntelligence)
class DrugIntelligenceAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "drug_class", "is_active", "updated_at"]
    list_filter = ["drug_class", "is_active"]
    search_fields = ["id", "name"]
    filter_horizontal = ["indications"]


@admin.register(MonitoringProtocol)
class MonitoringProtocolAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "drug", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["id", "name"]
    filter_horizontal = ["associated_diseases"]


@admin.register(Complication)
class ComplicationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "is_active", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["id", "name"]
    filter_horizontal = ["associated_diseases", "associated_drugs"]


@admin.register(KnowledgeGraphNode)
class KnowledgeGraphNodeAdmin(admin.ModelAdmin):
    list_display = ["node_id", "label", "node_type", "is_active"]
    list_filter = ["node_type", "is_active"]
    search_fields = ["node_id", "label"]
    actions = ["activate", "deactivate"]

    @admin.action(description="Activate selected nodes")
    def activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} nodes.")

    @admin.action(description="Deactivate selected nodes")
    def deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} nodes.")


@admin.register(KnowledgeGraphEdge)
class KnowledgeGraphEdgeAdmin(admin.ModelAdmin):
    list_display = ["source_label", "edge_type", "target_label", "weight", "is_active"]
    list_filter = ["edge_type", "is_active"]
    search_fields = ["source__label", "target__label"]

    def source_label(self, obj):
        return obj.source.label
    source_label.short_description = "Source"
    source_label.admin_order_field = "source__label"

    def target_label(self, obj):
        return obj.target.label
    target_label.short_description = "Target"
    target_label.admin_order_field = "target__label"


@admin.register(RecommendationAudit)
class RecommendationAuditAdmin(admin.ModelAdmin):
    list_display = [
        "recommendation_id", "recommendation_type", "disease_id",
        "confidence_score", "approval_status", "override_allowed", "issued_at",
    ]
    list_filter = ["recommendation_type", "disease_id", "approval_status", "override_allowed"]
    search_fields = ["recommendation_id", "disease_id", "recommendation_text"]
    readonly_fields = [
        "recommendation_id", "patient", "clinician", "recommendation_type",
        "disease_id", "recommendation_text", "clinical_rationale",
        "guideline", "guideline_version", "guideline_section", "guideline_recommendation_id",
        "evidence_grade", "evidence_source", "confidence_score", "kb_rule_id", "kb_version",
        "validation_date", "next_review_date", "expert_reviewer", "approval_status",
        "override_allowed", "override_reason", "explanation", "issued_at", "reviewed_at",
    ]
    actions = ["approve", "reject", "mark_overridden"]

    @admin.action(description="Approve selected recommendations")
    def approve(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(approval_status="pending").update(
            approval_status="approved", expert_reviewer=request.user, reviewed_at=timezone.now()
        )
        self.message_user(request, f"Approved {updated} recommendations.")

    @admin.action(description="Reject selected recommendations")
    def reject(self, request, queryset):
        updated = queryset.filter(approval_status="pending").update(approval_status="rejected")
        self.message_user(request, f"Rejected {updated} recommendations.")

    @admin.action(description="Mark selected recommendations as overridden")
    def mark_overridden(self, request, queryset):
        updated = queryset.update(approval_status="overridden")
        self.message_user(request, f"Marked {updated} recommendations as overridden.")
