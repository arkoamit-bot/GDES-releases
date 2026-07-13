"""
Production safety checks — run at startup via Django system check framework.

Each check returns warnings/errors for conditions that should never exist in
a clinical production environment.
"""
from django.core.checks import Warning, Error, register
from django.db import OperationalError, ProgrammingError


def _db_ready():
    """Return True if the database has the required tables."""
    try:
        from knowledge.models import KnowledgeBaseEntry
        KnowledgeBaseEntry.objects.exists()
        return True
    except (OperationalError, ProgrammingError):
        return False


@register("default", "deploy")
def check_no_test_rules_active(app_configs, **kwargs):
    if not _db_ready():
        return []
    from knowledge.models import KnowledgeBaseEntry
    test_active = KnowledgeBaseEntry.objects.filter(
        entry_id__startswith="TEST-", status="active"
    )
    if test_active.exists():
        ids = list(test_active.values_list("entry_id", flat=True))
        return [Error(
            f"{len(ids)} TEST-* knowledge rules are ACTIVE: {ids}",
            hint="Run manage.py to deactivate TEST-* rules before clinical use.",
            obj="knowledge.KnowledgeBaseEntry",
            id="clinical_reasoning.E001",
        )]
    return []


@register()
def check_knowledge_governance(app_configs, **kwargs):
    if not _db_ready():
        return []
    from knowledge.models import KnowledgeBaseEntry
    active = KnowledgeBaseEntry.objects.filter(status="active")
    if not active.exists():
        return []

    warnings = []
    missing_author = active.filter(author__isnull=True).count()
    missing_validation = active.filter(date_validated__isnull=True).count()
    missing_next_review = active.filter(next_review_date__isnull=True).count()
    missing_guideline = active.filter(guideline_chapter="").count()
    missing_version = active.filter(knowledge_version="").count()

    if missing_author:
        warnings.append(Warning(
            f"{missing_author} active knowledge rules have no author/reviewer.",
            hint="Assign an author to each active rule for governance traceability.",
            obj="knowledge.KnowledgeBaseEntry",
            id="clinical_reasoning.W001",
        ))
    if missing_validation:
        warnings.append(Warning(
            f"{missing_validation} active knowledge rules lack a validation date.",
            hint="Record the date each rule was clinically validated.",
            obj="knowledge.KnowledgeBaseEntry",
            id="clinical_reasoning.W002",
        ))
    if missing_next_review:
        warnings.append(Warning(
            f"{missing_next_review} active knowledge rules lack a next review date.",
            hint="Set a next review date so rules don't expire without notice.",
            obj="knowledge.KnowledgeBaseEntry",
            id="clinical_reasoning.W003",
        ))
    if missing_version:
        warnings.append(Warning(
            f"{missing_version} active knowledge rules lack a knowledge version.",
            hint="Assign a version string to each rule for traceability.",
            obj="knowledge.KnowledgeBaseEntry",
            id="clinical_reasoning.W004",
        ))
    if missing_guideline:
        warnings.append(Warning(
            f"{missing_guideline} active knowledge rules lack a guideline chapter reference.",
            hint="Link each rule to the relevant guideline chapter for transparency.",
            obj="knowledge.KnowledgeBaseEntry",
            id="clinical_reasoning.W005",
        ))
    return warnings


@register()
def check_recommendation_governance(app_configs, **kwargs):
    if not _db_ready():
        return []
    from knowledge.models import RecommendationAudit
    recs = RecommendationAudit.objects.all()
    if not recs.exists():
        return []  # No recommendations generated yet — not a warning

    warnings = []
    missing_grade = recs.filter(evidence_grade="").count()
    missing_guideline = recs.filter(guideline="").count()
    missing_reviewer = recs.filter(expert_reviewer__isnull=True).count()
    missing_validation = recs.filter(validation_date__isnull=True).count()
    missing_next = recs.filter(next_review_date__isnull=True).count()
    missing_explanation = recs.filter(explanation="").count()

    if missing_grade:
        warnings.append(Warning(
            f"{missing_grade} recommendations lack an evidence grade.",
            id="clinical_reasoning.W011",
        ))
    if missing_guideline:
        warnings.append(Warning(
            f"{missing_guideline} recommendations lack a guideline reference.",
            id="clinical_reasoning.W012",
        ))
    if missing_reviewer:
        warnings.append(Warning(
            f"{missing_reviewer} recommendations lack a reviewer assignment.",
            id="clinical_reasoning.W013",
        ))
    if missing_next:
        warnings.append(Warning(
            f"{missing_next} recommendations lack a next review date.",
            id="clinical_reasoning.W014",
        ))
    if missing_explanation:
        warnings.append(Warning(
            f"{missing_explanation} recommendations lack a clinical explanation.",
            id="clinical_reasoning.W015",
        ))
    return warnings
