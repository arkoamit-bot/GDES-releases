import logging
from django.conf import settings
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class GuidelineSource(models.Model):
    title = models.CharField(max_length=500)
    abbreviation = models.CharField(max_length=50)
    version_year = models.PositiveSmallIntegerField()
    url = models.URLField(max_length=500, blank=True)
    effective_date = models.DateField()
    retired_date = models.DateField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["abbreviation", "version_year"])]

    def __str__(self):
        return f"{self.abbreviation} {self.version_year}"


class KnowledgeBaseEntry(models.Model):
    class RuleType(models.TextChoices):
        DIAGNOSTIC = "diagnostic", "Diagnostic"
        TREATMENT = "treatment", "Treatment recommendation"
        MONITORING = "monitoring", "Monitoring"
        REFERRAL = "referral", "Referral criterion"
        PROGNOSTIC = "prognostic", "Prognostic"
        EXCLUSION = "exclusion", "Exclusion criterion"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        UNDER_REVIEW = "under_review", "Under review"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        SUPERSEDED = "superseded", "Superseded"
        ARCHIVED = "archived", "Archived"
        RETIRED = "retired", "Retired"

    class EvidenceGrade(models.TextChoices):
        LEVEL_1 = "1", "Level 1 (Strong recommendation)"
        LEVEL_2 = "2", "Level 2 (Weak recommendation)"
        NOT_GRADED = "NG", "Not graded"
        OPINION = "OP", "Expert opinion"

    entry_id = models.CharField(max_length=50, unique=True, help_text="Stable KB entry ID (e.g. KB-IGA-001)")
    disease_id = models.CharField(max_length=50, db_index=True, help_text="Disease code from prototype (e.g. iga, membranous)")
    rule_data = models.JSONField(help_text="Full rule definition (conditions, weights, explanations)")
    source = models.ForeignKey(GuidelineSource, on_delete=models.PROTECT, related_name="entries")
    evidence_grade = models.CharField(max_length=2, choices=EvidenceGrade.choices, default=EvidenceGrade.NOT_GRADED)
    rule_type = models.CharField(max_length=20, choices=RuleType.choices, default=RuleType.DIAGNOSTIC)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    effective_date = models.DateField()
    retired_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True, help_text="Flexible tags for categorisation")
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Guideline linkage (Phase 3.1)
    guideline_chapter = models.CharField(max_length=200, blank=True, help_text="e.g. 'KDIGO 2021 IgAN Chapter 3.1'")
    guideline_paragraph = models.CharField(max_length=100, blank=True, help_text="e.g. 'Section 3.1.2'")
    guideline_quote = models.TextField(blank=True, help_text="Direct quote from the guideline supporting this rule")
    evidence_url = models.URLField(max_length=500, blank=True, help_text="Link to supporting evidence or DOI")

    # Clinical Governance (V6.5)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="authored_rules", help_text="Original rule author",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="approved_rules", help_text="Clinical reviewer who approved",
    )
    approved_at = models.DateTimeField(null=True, blank=True, help_text="Approval timestamp")
    next_review_date = models.DateField(null=True, blank=True, help_text="Scheduled re-review date")
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence score (0-100)")
    explanation = models.TextField(blank=True, help_text="Human-readable reasoning for this rule")
    override_allowed = models.BooleanField(default=True, help_text="Whether clinicians can override this recommendation")
    recommendation_id = models.CharField(max_length=100, blank=True, help_text="Guideline recommendation ID (e.g. KDIGO-2021-IGAN-4.1.3)")
    knowledge_version = models.CharField(max_length=50, blank=True, help_text="Knowledge base version when rule was created")
    date_validated = models.DateField(null=True, blank=True, help_text="Last validation date")

    class Meta:
        verbose_name_plural = "knowledge base entries"
        indexes = [
            models.Index(fields=["disease_id", "status"]),
            models.Index(fields=["rule_type"]),
        ]

    # Valid lifecycle transitions: {current_status: [allowed_next_statuses]}
    VALID_TRANSITIONS: dict[str, list[str]] = {
        "draft": ["under_review", "archived"],
        "under_review": ["approved", "draft", "archived"],
        "approved": ["active", "draft", "archived"],
        "active": ["superseded", "retired", "draft", "archived"],
        "superseded": ["archived", "retired"],
        "archived": ["draft"],
        "retired": ["archived"],
    }

    def transition_to(self, new_status: str, user=None) -> "KnowledgeBaseEntry":
        """Transition this entry to a new lifecycle status with audit logging.

        Raises ValueError if the transition is not allowed.
        Returns self for chaining.
        """
        old_status = self.status
        allowed = self.VALID_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition {self.entry_id} from '{old_status}' to '{new_status}'. "
                f"Allowed transitions from '{old_status}': {allowed}"
            )
        self.status = new_status
        if new_status == "active":
            self.effective_date = timezone.now().date()
        if new_status in ("retired", "superseded", "archived"):
            self.retired_date = timezone.now().date()
        self.save(update_fields=["status", "effective_date", "retired_date", "updated_at"])
        logger.info(
            "KB entry %s transitioned: %s -> %s (by %s)",
            self.entry_id, old_status, new_status, user or "system",
        )
        return self

    def __str__(self):
        return f"{self.entry_id} ({self.disease_id}) - {self.get_status_display()}"


class KnowledgeBaseVersion(models.Model):
    """Version history for KnowledgeBaseEntry changes."""
    entry = models.ForeignKey(KnowledgeBaseEntry, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveSmallIntegerField()
    rule_data = models.JSONField()
    rule_data_diff = models.JSONField(default=dict, blank=True, help_text="Diff from previous version")
    evidence_grade = models.CharField(max_length=2, blank=True)
    guideline_chapter = models.CharField(max_length=200, blank=True)
    guideline_paragraph = models.CharField(max_length=100, blank=True)
    guideline_quote = models.TextField(blank=True)
    change_summary = models.TextField(blank=True, help_text="What changed in this version")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        unique_together = [("entry", "version_number")]
        verbose_name_plural = "knowledge base versions"

    def __str__(self):
        return f"{self.entry.entry_id} v{self.version_number}"


class RuleTemplate(models.Model):
    """Reusable condition template/schema for building rules consistently."""
    class Category(models.TextChoices):
        DIAGNOSTIC = "diagnostic", "Diagnostic"
        TREATMENT = "treatment", "Treatment"
        MONITORING = "monitoring", "Monitoring"
        REFERRAL = "referral", "Referral"

    template_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.DIAGNOSTIC)
    condition_schema = models.JSONField(
        default=dict, blank=True,
        help_text="JSON Schema describing valid conditions for this template",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "template_id"]

    def __str__(self):
        return f"{self.template_id} — {self.name}"


class RuleReview(models.Model):
    """Review workflow: tracks the approval chain for rule activation."""
    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending review"
        APPROVED = "approved", "Approved"
        CHANGES_REQUESTED = "changes_requested", "Changes requested"
        REJECTED = "rejected", "Rejected"

    entry = models.ForeignKey(KnowledgeBaseEntry, on_delete=models.CASCADE, related_name="reviews")
    version = models.ForeignKey(KnowledgeBaseVersion, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review {self.entry.entry_id} — {self.get_status_display()}"


class RuleTestResult(models.Model):
    """Outcome of testing a rule against a known patient case."""
    entry = models.ForeignKey(KnowledgeBaseEntry, on_delete=models.CASCADE, related_name="test_results")
    patient = models.ForeignKey("patients.Patient", on_delete=models.SET_NULL, null=True, blank=True)
    test_name = models.CharField(max_length=200, blank=True)
    expected_score = models.FloatField(null=True, blank=True)
    actual_score = models.FloatField()
    matched = models.BooleanField()
    test_input = models.JSONField(help_text="Features used for the test")
    test_output = models.JSONField(help_text="Full evaluation output")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["entry", "matched"])]

    def __str__(self):
        return f"{self.entry.entry_id} — {'✓' if self.matched else '✗'} ({self.actual_score})"


class GuidelineDocument(models.Model):
    """Imported guideline document containing parseable rule candidates."""
    class DocType(models.TextChoices):
        MARKDOWN = "markdown", "Markdown"
        HTML = "html", "HTML"
        TEXT = "text", "Plain text"
        JSON = "json", "Structured JSON"
        YAML = "yaml", "YAML"

    class ImportStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PARSING = "parsing", "Parsing"
        COMPLETE = "complete", "Complete"
        ERROR = "error", "Error"

    title = models.CharField(max_length=500)
    source = models.ForeignKey(GuidelineSource, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DocType.choices, default=DocType.MARKDOWN)
    content = models.TextField(blank=True)
    import_status = models.CharField(max_length=20, choices=ImportStatus.choices, default=ImportStatus.PENDING)
    parsed_rules = models.JSONField(default=list, blank=True, help_text="Rule candidates extracted from the document")
    import_log = models.TextField(blank=True, help_text="Parsing log messages")
    imported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-imported_at"]

    def __str__(self):
        return f"{self.title} ({self.get_import_status_display()})"


class EvidenceEntry(models.Model):
    """Evidence / literature reference supporting a KnowledgeBaseEntry."""
    class EvidenceLevel(models.TextChoices):
        META_ANALYSIS = "meta", "Meta-analysis / Systematic review"
        RCT = "rct", "Randomised controlled trial"
        COHORT = "cohort", "Cohort study"
        CASE_CONTROL = "case_control", "Case-control study"
        CASE_SERIES = "case_series", "Case series"
        EXPERT_OPINION = "expert", "Expert opinion"
        OTHER = "other", "Other"

    entry = models.ForeignKey(KnowledgeBaseEntry, on_delete=models.CASCADE, related_name="evidence_entries")
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    journal = models.CharField(max_length=200, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    pmid = models.CharField(max_length=20, blank=True)
    evidence_level = models.CharField(max_length=20, choices=EvidenceLevel.choices, default=EvidenceLevel.OTHER)
    summary = models.TextField(blank=True, help_text="How this evidence supports the rule")
    url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "title"]
        verbose_name_plural = "evidence entries"

    def __str__(self):
        return f"{self.title[:80]} ({self.get_evidence_level_display()})"


class DiseaseCategory(models.TextChoices):
    PRIMARY = "primary", "Primary glomerular disease"
    SECONDARY = "secondary", "Secondary glomerular disease"
    TRANSPLANT = "transplant", "Transplant glomerular disease"
    TUBULOINTERSTITIAL = "tubulointerstitial", "Tubulointerstitial disease"
    VASCULAR = "vascular", "Renal vascular disease"
    HEREDITARY = "hereditary", "Hereditary/congenital disease"
    OTHER = "other", "Other renal condition"


class Disease(models.Model):
    """Complete medical knowledge object for a single disease.

    Every disease is a comprehensive knowledge entity with definition,
    epidemiology, etiology, pathophysiology, presentation, diagnostic
    criteria, differentials, treatment, monitoring, and prognosis.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Disease code (e.g. iga, membranous)")
    name = models.CharField(max_length=300, help_text="Full disease name")
    category = models.CharField(max_length=30, choices=DiseaseCategory.choices, default=DiseaseCategory.PRIMARY)
    parent_disease = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="subtypes",
        help_text="Parent disease for subtypes (e.g. FSGS subtypes under FSGS)",
    )

    # Core knowledge fields
    definition = models.TextField(blank=True, help_text="Concise definition of the disease")
    epidemiology = models.TextField(blank=True, help_text="Incidence, prevalence, demographics")
    etiology = models.TextField(blank=True, help_text="Causes and risk factors")
    pathophysiology = models.TextField(blank=True, help_text="Disease mechanisms and pathways")
    clinical_presentation = models.TextField(blank=True, help_text=" Signs, symptoms, typical presentation patterns")

    # Diagnostic framework
    diagnostic_criteria = models.JSONField(default=list, blank=True, help_text="List of diagnostic criteria with evidence levels")
    differential_diagnosis = models.JSONField(default=list, blank=True, help_text="List of disease_id values to consider in differential")
    lab_findings = models.JSONField(default=list, blank=True, help_text="Typical laboratory findings")
    biopsy_findings = models.JSONField(default=list, blank=True, help_text="Typical histopathology findings")

    # Classification and stratification
    classification_systems = models.JSONField(default=list, blank=True, help_text="Classification systems (e.g. Oxford MEST-C, ISN/RPS)")
    risk_stratification = models.JSONField(default=list, blank=True, help_text="Risk factors and stratification schemes")

    # Management
    treatment_overview = models.TextField(blank=True, help_text="General treatment approach")
    treatment_algorithms = models.JSONField(default=list, blank=True, help_text="Structured treatment decision nodes")
    monitoring_protocol = models.TextField(blank=True, help_text="Standard monitoring schedule and parameters")

    # Outcomes
    complications = models.JSONField(default=list, blank=True, help_text="Potential complications")
    relapse_information = models.TextField(blank=True, help_text="Relapse rates, patterns, and management")
    long_term_prognosis = models.TextField(blank=True, help_text="Long-term outcomes and kidney survival data")

    # Governance
    evidence_summary = models.TextField(blank=True, help_text="Overall evidence base summary")
    guideline_recommendations = models.JSONField(default=list, blank=True, help_text="Key guideline recommendations with sources")
    key_references = models.JSONField(default=list, blank=True, help_text="Key literature references with DOIs")
    notes = models.TextField(blank=True, help_text="Clinical knowledge engineering notes")

    # Lifecycle
    is_active = models.BooleanField(default=True, help_text="Whether this disease is actively supported")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]
        verbose_name_plural = "diseases"

    def __str__(self):
        return f"{self.name} ({self.id})"


class ClinicalCase(models.Model):
    """Representative patient case for clinical validation.

    Each case forms a gold standard for testing the reasoning engine.
    Contains full clinical data plus expected reasoning outputs.
    """
    class PresentationType(models.TextChoices):
        TYPICAL = "typical", "Typical presentation"
        ATYPICAL = "atypical", "Atypical presentation"
        EARLY = "early", "Early disease"
        ADVANCED = "advanced", "Advanced disease"
        RAPID = "rapid", "Rapid progression"
        REMISSION = "remission", "Remission"
        RELAPSE = "relapse", "Relapse"
        RESISTANT = "resistant", "Treatment-resistant disease"
        COMPLICATIONS = "complications", "Complications"
        SPECIAL = "special", "Special population"

    class ReviewStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        INTERNAL_REVIEW = "internal_review", "Internal Review"
        CLINICAL_REVIEW = "clinical_review", "Clinical Review"
        APPROVED = "approved", "Approved"
        PUBLISHED = "published", "Published"

    case_id = models.CharField(max_length=50, unique=True, help_text="Stable case identifier (e.g. CASE-IGA-001)")
    title = models.CharField(max_length=300, help_text="Case title")
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="clinical_cases")
    presentation_type = models.CharField(max_length=20, choices=PresentationType.choices, default=PresentationType.TYPICAL)

    # Clinical data
    history = models.TextField(blank=True, help_text="Patient history and background")
    examination = models.TextField(blank=True, help_text="Physical examination findings")
    lab_data = models.JSONField(default=dict, blank=True, help_text="Laboratory data key-value pairs")
    biopsy_data = models.JSONField(default=dict, blank=True, help_text="Biopsy findings")
    diagnosis = models.TextField(blank=True, help_text="Final clinical diagnosis")

    # Expected reasoning outputs (gold standard for validation)
    expected_differential = models.JSONField(default=list, blank=True, help_text="Expected differential diagnosis with scores")
    expected_reasoning = models.JSONField(default=list, blank=True, help_text="Expected reasoning chain steps")
    expected_recommendations = models.JSONField(default=list, blank=True, help_text="Expected clinical recommendations")
    expected_monitoring = models.JSONField(default=list, blank=True, help_text="Expected monitoring plan")
    expected_followup = models.JSONField(default=list, blank=True, help_text="Expected follow-up schedule")

    # Clinical course
    treatment = models.TextField(blank=True, help_text="Treatment administered and response")
    outcome = models.TextField(blank=True, help_text="Clinical outcome")

    # Governance
    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.DRAFT)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="authored_cases")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_cases")
    review_notes = models.TextField(blank=True)
    source = models.CharField(max_length=200, blank=True, help_text="Source of the case (clinic, literature, synthetic)")
    is_gold_standard = models.BooleanField(default=False, help_text="Whether this case is a validated gold standard")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["disease", "presentation_type", "title"]
        verbose_name_plural = "clinical cases"

    def __str__(self):
        return f"{self.case_id}: {self.title}"


class ClinicalPathway(models.Model):
    """Standardized clinical pathway for a disease.

    Each pathway defines the expected sequence of care from presentation
    through assessment, diagnosis, treatment, monitoring, and follow-up.
    """
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name="pathways")
    stage_id = models.CharField(max_length=50, help_text="Stage identifier (e.g. IGA-PATH-01)")
    stage_name = models.CharField(max_length=200, help_text="Human-readable stage name")
    stage_order = models.PositiveIntegerField(help_text="Order in the pathway sequence")
    description = models.TextField(blank=True, help_text="What happens at this stage")
    required_actions = models.JSONField(default=list, blank=True, help_text="Actions that must be completed at this stage")
    expected_duration_days = models.PositiveIntegerField(null=True, blank=True, help_text="Typical duration in days")
    next_stages = models.JSONField(default=list, blank=True, help_text="List of stage_ids that can follow")
    criteria_to_proceed = models.TextField(blank=True, help_text="Criteria that must be met to move to next stage")
    warnings = models.JSONField(default=list, blank=True, help_text="Red flags or cautionary notes")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["disease", "stage_order"]
        verbose_name_plural = "clinical pathways"

    def __str__(self):
        return f"{self.disease.name}: {self.stage_name} ({self.stage_id})"


# ─── V4.2 Reusable Knowledge Objects ─────────────────────────────────────


class Syndrome(models.Model):
    """Clinical syndrome knowledge object (e.g. Nephrotic Syndrome, RPGN).

    Every clinical reasoning process begins from the patient's presentation.
    Syndromes bridge clinical features to differential diagnoses.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Syndrome code (e.g. nephrotic_syndrome)")
    name = models.CharField(max_length=300, help_text="Full syndrome name")
    definition = models.TextField(blank=True, help_text="Concise definition of the syndrome")
    diagnostic_criteria = models.JSONField(default=list, blank=True, help_text="Diagnostic criteria for the syndrome")
    common_causes = models.JSONField(default=list, blank=True, help_text="Common disease causes")
    rare_causes = models.JSONField(default=list, blank=True, help_text="Rare disease causes")
    clinical_clues = models.JSONField(default=list, blank=True, help_text="Key clinical examination findings")
    lab_clues = models.JSONField(default=list, blank=True, help_text="Key laboratory findings")
    biopsy_clues = models.JSONField(default=list, blank=True, help_text="Key biopsy findings")
    recommended_investigations = models.JSONField(default=list, blank=True, help_text="Recommended diagnostic workup")
    associated_diseases = models.ManyToManyField(
        Disease, blank=True, related_name="syndromes",
        help_text="Diseases that can present with this syndrome",
    )
    immediate_management = models.TextField(blank=True, help_text="Urgent management considerations")
    long_term_evaluation = models.TextField(blank=True, help_text="Long-term follow-up evaluation")
    expected_outcomes = models.TextField(blank=True, help_text="Expected clinical outcomes")
    is_active = models.BooleanField(default=True, help_text="Whether this syndrome is actively maintained")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "syndromes"

    def __str__(self):
        return f"{self.name} ({self.id})"


class PathologyEntity(models.Model):
    """Reusable pathology finding that occurs across multiple diseases.

    Instead of duplicating pathology explanations per disease, create a single
    authoritative knowledge object for each pathological finding.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Pathology entity code (e.g. mesangial_proliferation)")
    name = models.CharField(max_length=300, help_text="Full entity name")
    definition = models.TextField(blank=True, help_text="Histopathological definition")
    histological_appearance = models.TextField(blank=True, help_text="Light microscopy, IF, and EM description")
    clinical_significance = models.TextField(blank=True, help_text="What this finding means clinically")
    associated_diseases = models.ManyToManyField(
        Disease, blank=True, related_name="pathology_entities",
        help_text="Diseases where this finding is observed",
    )
    prognostic_value = models.TextField(blank=True, help_text="Prognostic implications")
    treatment_implications = models.TextField(blank=True, help_text="How this finding influences treatment")
    guideline_references = models.JSONField(default=list, blank=True, help_text="Guideline references for this entity")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "pathology entities"

    def __str__(self):
        return f"{self.name} ({self.id})"


class LabEntity(models.Model):
    """Reusable laboratory interpretation module.

    Each lab entity defines reference ranges, interpretation guidelines, and
    disease associations to support consistent lab data interpretation.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Lab entity code (e.g. proteinuria, egfr)")
    name = models.CharField(max_length=300, help_text="Full lab test name")
    reference_ranges = models.JSONField(default=dict, blank=True, help_text="Reference ranges by age/sex: {adult: {male: .., female: ..}}")
    interpretation = models.TextField(blank=True, help_text="How to interpret results")
    clinical_implications = models.TextField(blank=True, help_text="Clinical meaning of abnormal results")
    associated_diseases = models.ManyToManyField(
        Disease, blank=True, related_name="lab_entities",
        help_text="Diseases associated with abnormal results",
    )
    false_positives = models.TextField(blank=True, help_text="Causes of false positive results")
    false_negatives = models.TextField(blank=True, help_text="Causes of false negative results")
    repeat_testing = models.TextField(blank=True, help_text="Repeat testing recommendations")
    monitoring_recommendations = models.TextField(blank=True, help_text="Monitoring schedule recommendations")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "lab entities"

    def __str__(self):
        return f"{self.name} ({self.id})"


class DrugIntelligence(models.Model):
    """Unified drug intelligence platform — disease-independent drug knowledge.

    Complements the formulary-focused DrugMaster in treatments app with
    clinical knowledge: indications, contraindications, interactions,
    pregnancy/lactation advice, and evidence references.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Drug code (e.g. rituximab, cyclophosphamide)")
    name = models.CharField(max_length=300, help_text="Generic drug name")
    drug_class = models.CharField(max_length=200, blank=True, help_text="Pharmacological class (e.g. monoclonal antibody, alkylating agent)")
    mechanism_of_action = models.TextField(blank=True, help_text="Pharmacological mechanism")
    indications = models.ManyToManyField(
        Disease, blank=True, related_name="drug_intelligence",
        help_text="Diseases for which this drug is indicated",
    )
    contraindications = models.TextField(blank=True, help_text="Absolute and relative contraindications")
    renal_dosing = models.TextField(blank=True, help_text="Dose adjustment in CKD/ESRD")
    dialysis_dosing = models.TextField(blank=True, help_text="Dosing considerations during dialysis")
    transplant_considerations = models.TextField(blank=True, help_text="Special considerations in transplant")
    pregnancy = models.TextField(blank=True, help_text="Safety in pregnancy (FDA category)")
    lactation = models.TextField(blank=True, help_text="Safety during lactation")
    drug_interactions = models.JSONField(default=list, blank=True, help_text="Clinically significant drug interactions")
    laboratory_monitoring = models.TextField(blank=True, help_text="Required laboratory monitoring")
    vaccination_advice = models.TextField(blank=True, help_text="Vaccination recommendations before/during therapy")
    common_side_effects = models.JSONField(default=list, blank=True, help_text="Common adverse effects")
    serious_side_effects = models.JSONField(default=list, blank=True, help_text="Serious adverse effects requiring attention")
    stopping_criteria = models.TextField(blank=True, help_text="Criteria for stopping or holding")
    evidence_level = models.CharField(
        max_length=2, blank=True,
        choices=[("1", "Level 1 (Strong recommendation)"), ("2", "Level 2 (Weak recommendation)"),
                 ("NG", "Not graded"), ("OP", "Expert opinion")],
        help_text="GRADE evidence level for GN indications",
    )
    guideline_references = models.JSONField(default=list, blank=True, help_text="Guideline references")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "drug intelligence"

    def __str__(self):
        return f"{self.name} ({self.id})"


class MonitoringProtocol(models.Model):
    """Reusable monitoring pathway for drugs and disease states.

    Defines baseline investigations, monitoring schedules, safety checks,
    response assessment, and long-term surveillance protocols.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Protocol code (e.g. rituximab_monitoring)")
    name = models.CharField(max_length=300, help_text="Protocol name")
    drug = models.ForeignKey(
        DrugIntelligence, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="monitoring_protocols",
        help_text="Drug this protocol is primarily for",
    )
    associated_diseases = models.ManyToManyField(
        Disease, blank=True, related_name="monitoring_protocols",
        help_text="Diseases using this monitoring protocol",
    )
    baseline_investigations = models.JSONField(default=list, blank=True, help_text="Investigations to perform before starting")
    monitoring_schedule = models.JSONField(default=list, blank=True, help_text="Monitoring frequency and parameters")
    safety_monitoring = models.TextField(blank=True, help_text="Safety monitoring requirements")
    response_assessment = models.TextField(blank=True, help_text="How to assess treatment response")
    dose_adjustment = models.TextField(blank=True, help_text="Dose adjustment guidance based on results")
    treatment_discontinuation = models.TextField(blank=True, help_text="Criteria for stopping treatment")
    long_term_surveillance = models.TextField(blank=True, help_text="Long-term follow-up after treatment")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "monitoring protocols"

    def __str__(self):
        return f"{self.name} ({self.id})"


class Complication(models.Model):
    """Complication knowledge object reusable across diseases and drugs.

    Complications frequently overlap across diseases; this model provides
    a single authoritative knowledge source for each complication type.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="Complication code (e.g. infection, thrombosis)")
    name = models.CharField(max_length=300, help_text="Complication name")
    risk_factors = models.JSONField(default=list, blank=True, help_text="Risk factors for this complication")
    clinical_features = models.TextField(blank=True, help_text="Signs and symptoms")
    prevention = models.TextField(blank=True, help_text="Prevention strategies")
    early_detection = models.TextField(blank=True, help_text="Screening and early detection methods")
    treatment = models.TextField(blank=True, help_text="Treatment approach")
    monitoring = models.TextField(blank=True, help_text="Monitoring recommendations")
    long_term_consequences = models.TextField(blank=True, help_text="Long-term outcomes")
    associated_diseases = models.ManyToManyField(
        Disease, blank=True, related_name="complication_objects",
        help_text="Diseases associated with this complication",
    )
    associated_drugs = models.ManyToManyField(
        DrugIntelligence, blank=True, related_name="complications",
        help_text="Drugs that increase risk of this complication",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "complications"

    def __str__(self):
        return f"{self.name} ({self.id})"


# ─── V4.2 Cross-Disease Knowledge Graph ──────────────────────────────────


class KnowledgeGraphNode(models.Model):
    """Typed node in the cross-disease knowledge graph.

    Every syndrome, disease, pathology finding, lab test, drug, monitoring
    protocol, and complication becomes a node in a unified, traversable graph.
    """
    class NodeType(models.TextChoices):
        SYNDROME = "syndrome", "Clinical Syndrome"
        DISEASE = "disease", "Disease"
        PATHOLOGY = "pathology", "Pathology Entity"
        LAB = "lab", "Lab Entity"
        DRUG = "drug", "Drug Intelligence"
        MONITORING = "monitoring_protocol", "Monitoring Protocol"
        COMPLICATION = "complication", "Complication"
        CLINICAL_FEATURE = "clinical_feature", "Clinical Feature"
        GUIDELINE = "guideline", "Guideline"
        EVIDENCE = "evidence", "Evidence Entry"

    node_id = models.CharField(max_length=50, unique=True, help_text="Stable node identifier (e.g. sn:iga, e:mesangial_proliferation)")
    node_type = models.CharField(max_length=30, choices=NodeType.choices, db_index=True)
    label = models.CharField(max_length=300, help_text="Human-readable node label")
    description = models.TextField(blank=True, help_text="Node description")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional node metadata (provenance, references)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["node_type", "label"]
        verbose_name_plural = "knowledge graph nodes"
        indexes = [
            models.Index(fields=["node_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.get_node_type_display()}: {self.label} ({self.node_id})"


class KnowledgeGraphEdge(models.Model):
    """Typed, directed edge between two knowledge graph nodes.

    Edges define clinical relationships: presents_with, causes, diagnosed_by,
    treated_by, monitored_by, complicated_by, etc.
    """
    class EdgeType(models.TextChoices):
        PRESENTS_WITH = "presents_with", "Presents with"
        CAUSES = "causes", "Causes"
        DIAGNOSED_BY = "diagnosed_by", "Diagnosed by"
        TREATED_BY = "treated_by", "Treated by"
        INDICATED_FOR = "indicated_for", "Indicated for"
        MONITORED_BY = "monitored_by", "Monitored by"
        COMPLICATED_BY = "complicated_by", "Complicated by"
        RISK_FACTOR_FOR = "risk_factor_for", "Risk factor for"
        EVIDENCE_FOR = "evidence_for", "Evidence for"
        GUIDELINE_FOR = "guideline_for", "Guideline for"
        SUBTYPE_OF = "subtype_of", "Subtype of"
        FOUND_IN = "found_in", "Found in disease"
        ASSOCIATED_WITH = "associated_with", "Associated with"

    source = models.ForeignKey(
        KnowledgeGraphNode, on_delete=models.CASCADE,
        related_name="outgoing_edges",
        help_text="Source node of the edge",
    )
    target = models.ForeignKey(
        KnowledgeGraphNode, on_delete=models.CASCADE,
        related_name="incoming_edges",
        help_text="Target node of the edge",
    )
    edge_type = models.CharField(max_length=30, choices=EdgeType.choices, db_index=True)
    weight = models.FloatField(default=1.0, help_text="Edge weight for scoring/traversal (0.0 to 1.0)")
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional edge metadata (evidence, references)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["edge_type", "source__label"]
        verbose_name_plural = "knowledge graph edges"
        indexes = [
            models.Index(fields=["source", "edge_type"]),
            models.Index(fields=["target", "edge_type"]),
            models.Index(fields=["edge_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.source.label} --[{self.get_edge_type_display()}]--> {self.target.label}"


class RecommendationAudit(models.Model):
    """Audit trail for every AI recommendation issued by the clinical decision support system.

    Every patient-facing recommendation MUST have a corresponding record here.
    """

    class RecommendationType(models.TextChoices):
        INVESTIGATION = "investigation", "Investigation recommendation"
        DRUG_TOXICITY = "drug_toxicity", "Drug toxicity alert"
        TREATMENT_FAILURE = "treatment_failure", "Treatment failure alert"
        MANAGEMENT_PLAN = "management_plan", "Management plan"
        MONITORING_PLAN = "monitoring_plan", "Monitoring plan"
        FOLLOWUP = "followup", "Follow-up scheduling"
        DISEASE_VALIDATION = "disease_validation", "Disease validation"
        CLINICAL_REASONING = "clinical_reasoning", "Clinical reasoning output"

    # Recommendation identity
    recommendation_id = models.CharField(max_length=100, unique=True, help_text="Unique recommendation ID")
    recommendation_type = models.CharField(max_length=30, choices=RecommendationType.choices, db_index=True)
    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="recommendation_audits")
    clinician = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="issued_recommendations",
    )

    # Clinical content
    disease_id = models.CharField(max_length=50, db_index=True)
    recommendation_text = models.TextField(help_text="Human-readable recommendation")
    clinical_rationale = models.TextField(help_text="Why this recommendation was made")

    # Guideline linkage
    guideline = models.CharField(max_length=200, help_text="e.g. 'KDIGO 2021'")
    guideline_version = models.CharField(max_length=50, help_text="e.g. '2021'")
    guideline_section = models.CharField(max_length=200, blank=True, help_text="e.g. 'Section 4.1'")
    guideline_recommendation_id = models.CharField(max_length=100, blank=True, help_text="e.g. 'KDIGO-2021-IGAN-4.1.3'")

    # Evidence
    evidence_grade = models.CharField(
        max_length=2,
        choices=KnowledgeBaseEntry.EvidenceGrade.choices,
        default=KnowledgeBaseEntry.EvidenceGrade.NOT_GRADED,
        help_text="Evidence grade: 1=Strong, 2=Weak, NG=Not Graded, OP=Expert Opinion",
    )
    evidence_source = models.URLField(max_length=500, blank=True, help_text="Evidence URL or DOI")

    # AI scoring
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence (0-100)")
    kb_rule_id = models.CharField(max_length=50, blank=True, help_text="Knowledge base rule ID (e.g. KB-IGA-001)")
    kb_version = models.CharField(max_length=50, blank=True, help_text="KB version when rule was applied")

    # Governance
    validation_date = models.DateField(help_text="When this recommendation was validated")
    next_review_date = models.DateField(null=True, blank=True, help_text="Scheduled re-review")
    expert_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_recommendations",
    )
    approval_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected"), ("overridden", "Overridden")],
        default="pending",
    )
    override_allowed = models.BooleanField(default=True, help_text="Can clinician override?")
    override_reason = models.TextField(blank=True, help_text="If overridden, why")

    # Explanation
    explanation = models.TextField(help_text="Full reasoning chain for this recommendation")

    # Timestamps
    issued_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["patient", "recommendation_type"]),
            models.Index(fields=["disease_id", "approval_status"]),
            models.Index(fields=["kb_rule_id"]),
            models.Index(fields=["issued_at"]),
        ]

    def __str__(self):
        return f"{self.recommendation_id} — {self.recommendation_type} for {self.patient_id}"
