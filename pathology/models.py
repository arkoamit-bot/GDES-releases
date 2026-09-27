"""
Histopathology (Excel sheet 4) — the research-grade biopsy dataset.

    Biopsy              core biopsy + lesion descriptors
    GNDiagnosis         the diagnosis (specific + broad + pathogenesis groups)
    IgANScore           Oxford MEST-C (discrete fields, per the portfolio)
    LupusPathology      ISN/RPS class + NIH activity/chronicity indices
    FSGSPathology       primary/secondary + histologic variant
    MembranousPathology PLA2R/THSD7A tissue staining + MN stage
    BiopsyImage         digital-pathology slide images (imaging-consent gated)

Capturing the scores as discrete ordinal fields (not buried in narrative) is the
single change that makes the biopsy archive research-grade.
"""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from patients import choices
from patients.models import Patient
from patients.workflow import BiopsyIndication, BiopsyResult

from . import findings as vocab

# A reported percentage (sclerosis, IFTA, crescents, effacement) is 0-100.
_PCT = [MinValueValidator(0), MaxValueValidator(100)]


class Biopsy(models.Model):
    class Adequacy(models.TextChoices):
        ADEQUATE = "adequate", "Adequate"
        BORDERLINE = "borderline", "Borderline"
        INADEQUATE = "inadequate", "Inadequate"

    class Grade(models.TextChoices):
        NONE = "none", "None"
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending review"
        AWAITING_CENTRAL = "awaiting_central", "Local done, awaiting central"
        CONCORDANT = "concordant", "Concordant (local = central)"
        DISCORDANT = "discordant", "Discordant — needs adjudication"
        ADJUDICATED = "adjudicated", "Adjudicated (consensus)"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="biopsies")
    biopsy_date = models.DateField()
    adequacy = models.CharField(max_length=12, choices=Adequacy.choices, blank=True)
    # Why the biopsy was done + its diagnostic yield (workflow steps 4 & 7).
    indication = models.CharField(
        max_length=20, choices=BiopsyIndication.choices, blank=True,
        help_text="Clinical indication — drives the biopsy-yield analysis.")
    result_category = models.CharField(
        max_length=14, choices=BiopsyResult.choices, blank=True, db_index=True,
        help_text="Diagnostic yield: positive / negative / inconclusive.")
    # Central-review workflow state (§7.3); maintained by services/review.py.
    review_status = models.CharField(
        max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)

    # Light-microscopy summary of the local read. The lesion flags are
    # three-state: None = not assessed / not reported, which is not the same as
    # examined and absent. Rows saved before 2026-09-27 hold the old default
    # False, whose meaning cannot be recovered -- see reconcile_linked_facts.
    total_glomeruli = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Glomeruli (light microscopy)")
    global_sclerosis_pct = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, validators=_PCT)
    ifta_pct = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, validators=_PCT)
    arteriosclerosis = models.CharField(max_length=8, choices=Grade.choices, blank=True)
    arteriolar_hyalinosis = models.BooleanField(null=True, blank=True, default=None)
    dkd_lesion_present = models.BooleanField(null=True, blank=True, default=None)
    crescents_present = models.BooleanField(null=True, blank=True, default=None)
    crescent_pct = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, validators=_PCT)
    necrosis_present = models.BooleanField(null=True, blank=True, default=None)

    # Legacy single-choice IF/EM fields. New reports record repeatable
    # PathologyFinding rows instead; these keep their original values and are
    # converted (tagged as legacy) by reconcile_linked_facts, never guessed.
    if_pattern = models.CharField(
        max_length=120, blank=True,
        choices=[
            ("", "—"),
            ("mesangial_iga", "Mesangial IgA"),
            ("full_house", "Full-house (IgG/IgA/IgM/C3/C1q)"),
            ("granular_capillary_subendothelial", "Granular capillary wall — subendothelial"),
            ("granular_capillary_subepithelial", "Granular capillary wall — subepithelial"),
            ("linear_igg", "Linear IgG (anti-GBM pattern)"),
            ("pauci_immune", "Pauci-immune / no immune deposits"),
            ("mesangial_c3", "Mesangial C3"),
            ("mesangial_igg", "Mesangial IgG"),
            ("c3_dominant", "C3 dominant (starry sky)"),
            ("granular_mesangial_capillary", "Granular mesangial + capillary wall"),
            ("other", "Other (specify in notes)"),
        ],
        help_text="Immunofluorescence pattern on biopsy")
    em_findings = models.TextField(
        blank=True,
        choices=[
            ("", "—"),
            ("normal", "Normal ultrastructure"),
            ("mesangial_expansion", "Mesangial matrix expansion"),
            ("subendothelial_deposits", "Subendothelial electron-dense deposits"),
            ("subepithelial_deposits", "Subepithelial electron-dense deposits"),
            ("mesangial_deposits", "Mesangial electron-dense deposits"),
            ("intramembranous_deposits", "Intramembranous deposits"),
            ("foot_process_effacement", "Foot process effacement"),
            ("basement_membrane_thinning", "GBM thinning"),
            ("basement_membrane_irregularity", "GBM irregularity/double contours"),
            ("electron_dense_cryoglobulin", "Electron-dense cryoglobulin-like deposits"),
            ("fibrillary_deposits", "Fibrillary/tubulointerstitial deposits"),
            ("other", "Other (specify in notes)"),
        ],
        help_text="Electron microscopy findings")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["patient", "-biopsy_date"]
        verbose_name_plural = "biopsies"

    def __str__(self):
        return f"Biopsy {self.patient.patient_id} @ {self.biopsy_date}"


class GNDiagnosis(models.Model):
    class PrimarySecondary(models.TextChoices):
        PRIMARY = "primary", "Primary"
        SECONDARY = "secondary", "Secondary"
        UNKNOWN = "unknown", "Unknown"

    biopsy = models.OneToOneField(Biopsy, on_delete=models.CASCADE, related_name="diagnosis")
    diagnosis = models.CharField(max_length=120, choices=choices.SPECIFIC_GN_DIAGNOSIS)
    broad_group = models.CharField(max_length=80, blank=True, choices=choices.GN_BROAD_GROUP)
    pathogenesis_group = models.CharField(
        max_length=80, blank=True, choices=choices.GN_PATHOGENESIS_GROUP)
    primary_secondary = models.CharField(
        max_length=10, choices=PrimarySecondary.choices, blank=True)
    secondary_cause = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return f"{self.biopsy.patient.patient_id}: {self.diagnosis}"


def _ordinal(maxv):
    return dict(null=True, blank=True,
               validators=[MinValueValidator(0), MaxValueValidator(maxv)])


class IgANScore(models.Model):
    """Oxford MEST-C. M0/1 E0/1 S0/1 T0-2 C0-2."""
    biopsy = models.OneToOneField(Biopsy, on_delete=models.CASCADE, related_name="igan_score")
    M = models.PositiveSmallIntegerField(**_ordinal(1))   # mesangial hypercellularity
    E = models.PositiveSmallIntegerField(**_ordinal(1))   # endocapillary hypercellularity
    S = models.PositiveSmallIntegerField(**_ordinal(1))   # segmental sclerosis
    T = models.PositiveSmallIntegerField(**_ordinal(2))   # tubular atrophy/IF
    C = models.PositiveSmallIntegerField(**_ordinal(2))   # crescents

    def __str__(self):
        return (f"{self.biopsy.patient.patient_id} MEST-C "
                f"M{self.M}E{self.E}S{self.S}T{self.T}C{self.C}")


class LupusPathology(models.Model):
    class ISNClass(models.TextChoices):
        I = "I", "Class I"
        II = "II", "Class II"
        III = "III", "Class III"
        IV = "IV", "Class IV"
        V = "V", "Class V"
        VI = "VI", "Class VI"
        # Mixed lesions. The diagnosis list has always offered these; without
        # them here the class could not be carried across from the diagnosis.
        III_V = "III+V", "Class III+V"
        IV_V = "IV+V", "Class IV+V"

    biopsy = models.OneToOneField(Biopsy, on_delete=models.CASCADE, related_name="lupus")
    isn_rps_class = models.CharField(max_length=6, choices=ISNClass.choices, blank=True)
    activity_index = models.PositiveSmallIntegerField(**_ordinal(24))
    chronicity_index = models.PositiveSmallIntegerField(**_ordinal(12))

    def __str__(self):
        return f"{self.biopsy.patient.patient_id} LN {self.isn_rps_class}"


class FSGSPathology(models.Model):
    class Variant(models.TextChoices):
        NOS = "nos", "NOS"
        PERIHILAR = "perihilar", "Perihilar"
        CELLULAR = "cellular", "Cellular"
        TIP = "tip", "Tip"
        COLLAPSING = "collapsing", "Collapsing"

    biopsy = models.OneToOneField(Biopsy, on_delete=models.CASCADE, related_name="fsgs")
    primary_secondary = models.CharField(
        max_length=10, choices=GNDiagnosis.PrimarySecondary.choices, blank=True)
    variant = models.CharField(max_length=10, choices=Variant.choices, blank=True)

    def __str__(self):
        return f"{self.biopsy.patient.patient_id} FSGS {self.variant}"


class MembranousPathology(models.Model):
    class Stain(models.TextChoices):
        POSITIVE = "pos", "Positive"
        NEGATIVE = "neg", "Negative"
        NOT_DONE = "nd", "Not done"

    biopsy = models.OneToOneField(Biopsy, on_delete=models.CASCADE, related_name="membranous")
    pla2r_tissue = models.CharField(max_length=4, choices=Stain.choices, blank=True)
    thsd7a_tissue = models.CharField(max_length=4, choices=Stain.choices, blank=True)
    mn_stage = models.PositiveSmallIntegerField(**_ordinal(4))   # Ehrenreich-Churg I-IV

    def __str__(self):
        return f"{self.biopsy.patient.patient_id} MN stage {self.mn_stage}"


class BiopsyImage(models.Model):
    """Digital-pathology slide image. Requires imaging consent (enforced in
    clean() so admin/forms validate; biobank/pathology services do too)."""
    class Stain(models.TextChoices):
        HE = "he", "H&E"
        PAS = "pas", "PAS"
        SILVER = "silver", "Silver"
        TRICHROME = "trichrome", "Masson trichrome"
        IF = "if", "Immunofluorescence"
        EM = "em", "Electron microscopy"

    biopsy = models.ForeignKey(Biopsy, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="biopsy_images/%Y/%m/")
    stain = models.CharField(max_length=10, choices=Stain.choices, blank=True)
    description = models.CharField(max_length=240, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.biopsy.patient.patient_id} ({self.stain})"

    def clean(self):
        from audit.models import Consent
        from audit.services.consent import has_consent
        if not has_consent(self.biopsy.patient, Consent.Type.IMAGING):
            raise ValidationError(
                "Imaging consent is not on file for this patient — "
                "cannot store digital-pathology images.")


class PathologyReview(models.Model):
    """One pathologist's independent read of a biopsy. The protocol mandates a
    LOCAL read and a CENTRAL expert read for every index biopsy; discordance is
    resolved by an ADJUDICATION (consensus) read (§7.3)."""
    class Role(models.TextChoices):
        LOCAL = "local", "Local pathologist"
        CENTRAL = "central", "Central expert review"
        ADJUDICATION = "adjudication", "Consensus adjudication"

    # The classification fields compared for concordance and inter-observer kappa.
    KEY_FIELDS = ["diagnosis", "broad_group", "mest_m", "mest_e", "mest_s",
                  "mest_t", "mest_c", "isn_rps_class", "fsgs_variant"]

    biopsy = models.ForeignKey(Biopsy, on_delete=models.CASCADE, related_name="reviews")
    role = models.CharField(max_length=12, choices=Role.choices)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pathology_reviews")
    review_date = models.DateField(null=True, blank=True)

    diagnosis = models.CharField(max_length=120, choices=choices.SPECIFIC_GN_DIAGNOSIS)
    broad_group = models.CharField(max_length=80, blank=True, choices=choices.GN_BROAD_GROUP)
    # Oxford MEST-C (IgAN).
    mest_m = models.PositiveSmallIntegerField(null=True, blank=True)
    mest_e = models.PositiveSmallIntegerField(null=True, blank=True)
    mest_s = models.PositiveSmallIntegerField(null=True, blank=True)
    mest_t = models.PositiveSmallIntegerField(null=True, blank=True)
    mest_c = models.PositiveSmallIntegerField(null=True, blank=True)
    isn_rps_class = models.CharField(   # LN
        max_length=6, blank=True, choices=LupusPathology.ISNClass.choices)
    fsgs_variant = models.CharField(    # FSGS
        max_length=10, blank=True, choices=FSGSPathology.Variant.choices)

    is_final = models.BooleanField(default=False)
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["biopsy", "role"]
        constraints = [
            models.UniqueConstraint(fields=["biopsy", "role"], name="uniq_biopsy_review_role"),
        ]

    def __str__(self):
        return f"{self.biopsy.patient.patient_id} {self.get_role_display()}: {self.diagnosis}"


class ModalityStatus(models.TextChoices):
    """Whether a modality was examined. Blank = not stated in the report."""
    PERFORMED = "performed", "Performed"
    PENDING = "pending", "Pending"
    NOT_DONE = "not_done", "Not done"
    UNAVAILABLE = "unavailable", "Unavailable"
    INADEQUATE = "inadequate", "Inadequate sample"


class PathologyReport(models.Model):
    """One revision of one pathologist's report on a biopsy.

    The Biopsy is the procedure/specimen anchor; each read (local, central,
    adjudication) is a report, and an amendment or addendum is a new revision
    that supersedes the previous one without erasing it. Repeatable findings
    hang off a particular revision, so a correction never rewrites what an
    earlier revision said. A repeat biopsy is a new Biopsy, not a revision.
    """
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending further studies"
        PRELIMINARY = "preliminary", "Preliminary"
        FINAL = "final", "Final"
        INADEQUATE = "inadequate", "Inadequate / non-diagnostic"

    class Origin(models.TextChoices):
        GUIDED = "guided", "Guided entry"
        AMENDMENT = "amendment", "Amendment"
        ADDENDUM = "addendum", "Addendum"
        API = "api", "API"
        ADMIN = "admin", "Admin"
        LEGACY = "legacy", "Converted from legacy biopsy fields"

    class Context(models.TextChoices):
        NATIVE = "native", "Native kidney"
        TRANSPLANT = "transplant", "Transplant kidney"

    biopsy = models.ForeignKey(Biopsy, on_delete=models.CASCADE, related_name="reports")
    role = models.CharField(max_length=12, choices=PathologyReview.Role.choices,
                            default=PathologyReview.Role.LOCAL)
    revision = models.PositiveSmallIntegerField(default=1)
    supersedes = models.OneToOneField(
        "self", on_delete=models.PROTECT, null=True, blank=True,
        related_name="superseded_by")
    is_current = models.BooleanField(default=True, db_index=True)
    origin = models.CharField(max_length=10, choices=Origin.choices, default=Origin.GUIDED)
    revision_reason = models.CharField(
        max_length=240, blank=True,
        help_text="Required for an amendment or addendum.")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.FINAL)

    # Provenance.
    report_identifier = models.CharField(max_length=60, blank=True)
    laboratory = models.CharField(max_length=120, blank=True)
    pathologist = models.CharField(max_length=120, blank=True)
    specimen_date = models.DateField(null=True, blank=True)
    report_date = models.DateField(null=True, blank=True)
    context = models.CharField(max_length=10, choices=Context.choices, blank=True)
    signed_by = models.CharField(max_length=120, blank=True)
    signed_at = models.DateField(null=True, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pathology_reports")

    # Specimen and adequacy. Counts are per modality and are never summed
    # across modalities (they are not the same glomeruli). The light-microscopy
    # glomerular total is Biopsy.total_glomeruli.
    cortex_present = models.BooleanField(null=True, blank=True)
    medulla_present = models.BooleanField(null=True, blank=True)
    cores = models.PositiveSmallIntegerField(null=True, blank=True)
    glomeruli_if = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Glomeruli (IF)")
    glomeruli_em = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Glomeruli (EM)")
    globally_sclerosed = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Globally sclerosed glomeruli (LM)")
    segmentally_sclerosed = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Segmentally sclerosed glomeruli (LM)")
    crescentic_glomeruli = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Glomeruli with crescents (LM)")
    limitations = models.TextField(blank=True)

    # Modality availability.
    lm_status = models.CharField(max_length=12, choices=ModalityStatus.choices, blank=True,
                                 verbose_name="Light microscopy")
    if_status = models.CharField(max_length=12, choices=ModalityStatus.choices, blank=True,
                                 verbose_name="Immunofluorescence")
    ihc_status = models.CharField(max_length=12, choices=ModalityStatus.choices, blank=True,
                                  verbose_name="Special stains / IHC")
    em_status = models.CharField(max_length=12, choices=ModalityStatus.choices, blank=True,
                                 verbose_name="Electron microscopy")

    # Conclusion. A draft / pending / inadequate report need not state a
    # diagnosis; the biopsy's GNDiagnosis is the adopted interpretation.
    primary_diagnosis = models.CharField(
        max_length=120, blank=True, choices=choices.SPECIFIC_GN_DIAGNOSIS)
    additional_diagnoses = models.JSONField(
        default=list, blank=True,
        help_text="Coexisting diagnoses (e.g. DKD + GN), as diagnosis labels.")
    comment = models.TextField(blank=True)
    original_report_text = models.TextField(blank=True)
    # Disease-score values as stated in THIS revision. The biopsy-level score
    # models hold the current (finalized) values; older values stay here.
    scores = models.JSONField(default=dict, blank=True)
    panel_override_reason = models.CharField(
        max_length=240, blank=True,
        help_text="Why a score panel outside the diagnosis family applies "
                  "(mixed / coexisting lesion).")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["biopsy", "role", "-revision"]
        constraints = [
            models.UniqueConstraint(fields=["biopsy", "role", "revision"],
                                    name="uniq_report_revision"),
        ]

    def __str__(self):
        return (f"{self.biopsy.patient.patient_id} {self.get_role_display()} "
                f"report r{self.revision} ({self.get_status_display()})")

    def findings_by_section(self):
        grouped: dict[str, list] = {}
        for f in self.findings.all():
            grouped.setdefault(f.section, []).append(f)
        return [(key, vocab.section_label(key), grouped[key])
                for key in vocab.SECTIONS if key in grouped]

    def modality_rows(self):
        return [(f.verbose_name, getattr(self, f"get_{f.name}_display")())
                for f in (self._meta.get_field(n) for n in
                          ("lm_status", "if_status", "ihc_status", "em_status"))]


class PathologyFinding(models.Model):
    """One repeatable, optionally graded finding on a report revision."""
    class Presence(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        INDETERMINATE = "indeterminate", "Indeterminate"

    class Severity(models.TextChoices):
        MINIMAL = "minimal", "Minimal"
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"

    class Extent(models.TextChoices):
        FOCAL = "focal", "Focal"
        DIFFUSE = "diffuse", "Diffuse"
        SEGMENTAL = "segmental", "Segmental"
        GLOBAL = "global", "Global"

    class Site(models.TextChoices):
        MESANGIAL = "mesangial", "Mesangial"
        CAPILLARY_WALL = "capillary_wall", "Capillary wall"
        SUBENDOTHELIAL = "subendothelial", "Subendothelial"
        SUBEPITHELIAL = "subepithelial", "Subepithelial"
        INTRAMEMBRANOUS = "intramembranous", "Intramembranous"
        TUBULAR_BM = "tubular_bm", "Tubular basement membrane"
        INTERSTITIUM = "interstitium", "Interstitium"
        VESSELS = "vessels", "Vessels"
        BOWMAN = "bowman", "Bowman capsule"

    class Intensity(models.TextChoices):
        NEGATIVE = "0", "Negative"
        TRACE = "trace", "Trace"
        ONE = "1+", "1+"
        TWO = "2+", "2+"
        THREE = "3+", "3+"

    class Distribution(models.TextChoices):
        GRANULAR = "granular", "Granular"
        LINEAR = "linear", "Linear"
        PSEUDOLINEAR = "pseudolinear", "Pseudolinear"
        SMUDGY = "smudgy", "Smudgy"

    class Origin(models.TextChoices):
        ENTERED = "entered", "Entered"
        LEGACY = "legacy", "Converted from a legacy biopsy field"

    report = models.ForeignKey(PathologyReport, on_delete=models.CASCADE,
                               related_name="findings")
    section = models.CharField(max_length=20, choices=vocab.SECTION_CHOICES)
    code = models.CharField(max_length=40, choices=vocab.CODE_CHOICES)
    other_label = models.CharField(
        max_length=120, blank=True, help_text="What the finding is, when 'Other'.")
    presence = models.CharField(max_length=14, choices=Presence.choices,
                                default=Presence.PRESENT)
    severity = models.CharField(max_length=10, choices=Severity.choices, blank=True)
    extent = models.CharField(max_length=10, choices=Extent.choices, blank=True)
    extent_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True,
                                     blank=True, validators=_PCT,
                                     verbose_name="Extent (%)")
    count = models.PositiveSmallIntegerField(null=True, blank=True)
    denominator = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Out of how many (e.g. glomeruli examined).")
    site = models.CharField(max_length=16, choices=Site.choices, blank=True)
    marker = models.CharField(max_length=16, choices=vocab.IF_MARKERS, blank=True)
    intensity = models.CharField(max_length=6, choices=Intensity.choices, blank=True)
    distribution = models.CharField(max_length=14, choices=Distribution.choices, blank=True)
    detail = models.CharField(max_length=240, blank=True)
    origin = models.CharField(max_length=8, choices=Origin.choices, default=Origin.ENTERED)
    legacy_value = models.CharField(max_length=120, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["report", "section", "sort_order", "id"]

    def __str__(self):
        return f"{self.get_section_display()}: {self.display_label}"

    @property
    def display_label(self):
        if self.section == "if_marker":
            name = self.other_label if self.marker == vocab.OTHER else self.get_marker_display()
            return name or "Marker"
        if self.code == vocab.OTHER:
            return self.other_label or "Other"
        return vocab.label_for(self.section, self.code)

    @property
    def grading(self):
        parts = []
        if self.section == "if_marker":
            parts += [self.get_intensity_display() if self.intensity else "",
                      self.get_distribution_display() if self.distribution else ""]
        parts += [self.get_severity_display() if self.severity else "",
                  self.get_extent_display() if self.extent else "",
                  f"{self.extent_pct}%" if self.extent_pct is not None else "",
                  (f"{self.count}/{self.denominator}" if self.denominator
                   else (str(self.count) if self.count is not None else "")),
                  self.get_site_display() if self.site else ""]
        return ", ".join(p for p in parts if p)
