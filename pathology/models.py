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

    total_glomeruli = models.PositiveSmallIntegerField(null=True, blank=True)
    global_sclerosis_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    ifta_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    arteriosclerosis = models.CharField(max_length=8, choices=Grade.choices, blank=True)
    arteriolar_hyalinosis = models.BooleanField(default=False)
    dkd_lesion_present = models.BooleanField(default=False)
    crescents_present = models.BooleanField(default=False)
    crescent_pct = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    necrosis_present = models.BooleanField(default=False)

    if_pattern = models.CharField(max_length=120, blank=True)
    em_findings = models.TextField(blank=True)
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

    biopsy = models.OneToOneField(Biopsy, on_delete=models.CASCADE, related_name="lupus")
    isn_rps_class = models.CharField(max_length=4, choices=ISNClass.choices, blank=True)
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
        max_length=4, blank=True, choices=LupusPathology.ISNClass.choices)
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
