from django.db import models


class ProviderType(models.TextChoices):
    PUBMED = "pubmed", "PubMed (NCBI E-utilities)"
    EUROPE_PMC = "europe_pmc", "Europe PMC"
    SEMANTIC_SCHOLAR = "semantic_scholar", "Semantic Scholar"
    OPENALEX = "openalex", "OpenAlex"
    CROSSREF = "crossref", "Crossref"
    VERA = "vera", "Vera"
    VERA_WEB = "vera_web", "Vera Health (web session)"
    OPENAI = "openai", "OpenAI GPT"
    PERPLEXITY = "perplexity", "Perplexity Sonar"


class ProviderStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    DEGRADED = "degraded", "Degraded"
    DISABLED = "disabled", "Disabled"
    ERROR = "error", "Error"


class EvidenceLevel(models.TextChoices):
    META_ANALYSIS = "1a", "1a — Meta-analysis of RCTs"
    RCT = "1b", "1b — Individual RCT"
    SYSTEMATIC_REVIEW = "2a", "2a — Systematic review of cohort studies"
    COHORT = "2b", "2b — Individual cohort study"
    CASE_CONTROL = "3a", "3a — Systematic review of case-control"
    CASE_CONTROL_INDIV = "3b", "3b — Individual case-control study"
    CASE_SERIES = "4", "4 — Case series"
    EXPERT_OPINION = "5", "5 — Expert opinion"
    GUIDELINE = "gl", "Clinical guideline"
    FDA_ALERT = "fda", "FDA / EMA safety alert"


class StudyDesign(models.TextChoices):
    META_ANALYSIS = "meta_analysis", "Meta-analysis"
    SYSTEMATIC_REVIEW = "systematic_review", "Systematic review"
    RCT = "rct", "Randomised controlled trial"
    COHORT_PROSPECTIVE = "cohort_prospective", "Prospective cohort"
    COHORT_RETROSPECTIVE = "cohort_retrospective", "Retrospective cohort"
    CASE_CONTROL = "case_control", "Case-control"
    CROSS_SECTIONAL = "cross_sectional", "Cross-sectional"
    CASE_SERIES = "case_series", "Case series"
    CASE_REPORT = "case_report", "Case report"
    NARRATIVE_REVIEW = "narrative_review", "Narrative review"
    GUIDELINE = "guideline", "Clinical practice guideline"
    FDA_ALERT = "fda_alert", "FDA / EMA safety communication"
    EDITORIAL = "editorial", "Editorial / commentary"
    LETTER = "letter", "Letter to editor"
    OTHER = "other", "Other"


class ValidationOutcome(models.TextChoices):
    VERIFIED = "verified", "Verified — Recommendation matches evidence"
    MINOR_DIFFERENCE = "minor", "Minor difference — Recommendation aligns broadly"
    MAJOR_DIFFERENCE = "major", "Major difference — Recommendation diverges from evidence"
    CONFLICTING = "conflicting", "Conflicting evidence — Contradictory studies found"
    UNVERIFIABLE = "unverifiable", "Unable to verify — Insufficient evidence"
    PENDING = "pending", "Validation pending"


class ConflictSeverity(models.TextChoices):
    CRITICAL = "critical", "Critical — Safety alert or drug withdrawal"
    HIGH = "high", "High — New RCT contradicts guideline"
    MEDIUM = "medium", "Medium — New systematic review differs"
    LOW = "low", "Low — Minor discrepancy"
    INFO = "info", "Informational — New evidence available"


class ConfidenceScore(models.IntegerChoices):
    VERY_HIGH = 95, "Very High (95-100%)"
    HIGH = 80, "High (80-94%)"
    MODERATE = 60, "Moderate (60-79%)"
    LOW = 40, "Low (40-59%)"
    VERY_LOW = 20, "Very Low (20-39%)"
    INSUFFICIENT = 5, "Insufficient (<20%)"


class CacheTTL(models.IntegerChoices):
    SEARCH = 3600, "1 hour"
    SUMMARY = 86400, "24 hours"
    AI_RESPONSE = 43200, "12 hours"
    PROVIDER_CHECK = 300, "5 minutes"
    GUIDELINE = 604800, "7 days"


class AlertType(models.TextChoices):
    NEW_RCT = "new_rct", "New RCT published"
    NEW_GUIDELINE = "new_guideline", "New guideline released"
    SAFETY_ALERT = "safety_alert", "FDA/EMA safety alert"
    DRUG_WITHDRAWAL = "drug_withdrawal", "Drug withdrawal"
    CONTRADICTION = "contradiction", "Evidence contradiction detected"
    GUIDELINE_UPDATE = "guideline_update", "Guideline update available"
    KNOWLEDGE_GAP = "knowledge_gap", "Knowledge gap identified"


class CitationFormat(models.TextChoices):
    APA = "apa", "APA 7th edition"
    VANCOUVER = "vancouver", "Vancouver style"
    BIBTEX = "bibtex", "BibTeX"
    RIS = "ris", "RIS format"
    MLA = "mla", "MLA 9th edition"
    CHICAGO = "chicago", "Chicago author-date"


VALIDATION_SOURCES = [
    ("KDIGO", "KDIGO — Kidney Disease: Improving Global Outcomes"),
    ("ERA", "ERA — European Renal Association"),
    ("ASN", "ASN — American Society of Nephrology"),
    ("ISN", "ISN — International Society of Nephrology"),
    ("NKF", "NKF/KDOQI — National Kidney Foundation"),
    ("other", "Other guideline body"),
]
