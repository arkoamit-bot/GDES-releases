"""
Minimal Patient model — just enough of the core registry for the prescription
module to hang off. The full registry (baseline, labs, pathology, outcomes)
plugs in around this without changing the prescription workflow.
"""
from datetime import date

from django.db import IntegrityError, models, transaction

from . import choices
from .workflow import DiseasePhase, RegistrationStatus


def next_patient_id():
    """Next sequential study ID, e.g. BGD-00001. Computed by NUMERIC maximum (not
    lexicographic order) so it stays correct past BGD-99999; ignores non-sequence
    IDs (demo/imported)."""
    ids = (Patient.objects.filter(patient_id__regex=r"^BGD-\d+$")
           .values_list("patient_id", flat=True))
    n = max((int(pid.split("-")[1]) for pid in ids), default=0) + 1
    return f"BGD-{n:05d}"


class Site(models.Model):
    """Multi-center site — each hospital/center in the federated registry."""
    code = models.CharField(max_length=20, unique=True,
                            help_text="Short site code, e.g. BIRDEM, DMCH, SQUARE")
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    config = models.JSONField(
        default=dict, blank=True,
        help_text="Site-specific configuration (lab panels, local drugs, etc.)",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Site (multi-center)"
        verbose_name_plural = "Sites (multi-center)"

    def __str__(self):
        return f"{self.code} — {self.name}"


class Patient(models.Model):
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class DiabetesStatus(models.TextChoices):
        NONE = "none", "No diabetes"
        T1 = "t1", "Type 1"
        T2 = "t2", "Type 2"
        OTHER = "other", "Other / secondary"

    # Auto-generated on first save (BGD-00001…); leave blank in the form.
    patient_id = models.CharField(max_length=32, unique=True, blank=True)
    # Indexed: used for exact-match duplicate detection (validate_patients).
    hospital_id = models.CharField(max_length=64, blank=True, db_index=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=32, blank=True, db_index=True)
    sex = models.CharField(max_length=1, choices=Sex.choices)
    dob = models.DateField(null=True, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)

    # Multi-center site (Phase 3.3). Nullable for backward compatibility.
    site = models.ForeignKey(
        Site, on_delete=models.PROTECT, null=True, blank=True,
        related_name="patients",
        help_text="Enrolling/primary site for this patient",
    )

    cohort = models.CharField(max_length=32, blank=True, choices=choices.PATIENT_CATEGORY)
    diabetes_status = models.CharField(
        max_length=8, choices=DiabetesStatus.choices, default=DiabetesStatus.NONE
    )
    # Primary GN diagnosis — chosen from the curated specific-diagnosis list.
    primary_diagnosis = models.CharField(
        max_length=120, blank=True, choices=choices.SPECIFIC_GN_DIAGNOSIS)

    # --- Level 2: Persistent clinical data (single source of truth) ---------
    # Entered once at baseline; auto-carried-forward to all encounters.
    # Clinicians update only when a true clinical change occurs.
    hypertension = models.BooleanField(default=False)
    autoimmune_disease = models.BooleanField(default=False)
    chronic_infection = models.BooleanField(
        default=False, help_text="HBV / HCV / HIV / TB")
    smoking_status = models.CharField(
        max_length=20, blank=True, choices=choices.SMOKING)
    hepatitis_status = models.CharField(
        max_length=20, blank=True,
        choices=[("", "—"), ("negative", "Negative"), ("hbv", "HBV"),
                 ("hcv", "HCV"), ("both", "HBV + HCV")])
    hiv_status = models.CharField(
        max_length=10, blank=True,
        choices=[("", "—"), ("negative", "Negative"), ("positive", "Positive")])
    biopsy_diagnosis = models.CharField(
        max_length=120, blank=True,
        help_text="GN diagnosis from biopsy (auto-synced from GNDiagnosis)")
    oxford_mestc = models.CharField(
        max_length=20, blank=True,
        help_text="Oxford MEST-C summary (auto-synced from IgANScore)")
    isn_rps_class = models.CharField(
        max_length=10, blank=True,
        help_text="ISN/RPS class for lupus nephritis (auto-synced)")
    ckd_etiology = models.CharField(
        max_length=120, blank=True,
        help_text="CKD aetiology (auto-derived or clinician-entered)")
    transplant_status = models.CharField(
        max_length=20, blank=True,
        choices=[("", "—"), ("none", "No transplant"),
                 ("preemptive", "Pre-emptive transplant"),
                 ("living", "Living donor transplant"),
                 ("deceased", "Deceased donor transplant")])

    # Latest known renal function, refreshed by the labs app.
    latest_egfr = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )

    # --- GN management workflow -------------------------------------------
    registration_status = models.CharField(
        max_length=16, choices=RegistrationStatus.choices,
        default=RegistrationStatus.SUSPECTED, db_index=True)
    registration_date = models.DateField(null=True, blank=True)
    current_phase = models.CharField(
        max_length=16, choices=DiseasePhase.choices, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["patient_id"]

    def __str__(self):
        return f"{self.patient_id} — {self.name}"

    def clean(self):
        if self.dob and self.dob > date.today():
            raise ValidationError({"dob": "Date of birth cannot be in the future."})
        if self.enrollment_date and self.dob and self.enrollment_date < self.dob:
            raise ValidationError({"enrollment_date": "Enrollment date cannot be before date of birth."})
        if self.name and not self.name.strip():
            raise ValidationError({"name": "Name cannot be blank or whitespace only."})

    def delete(self, *args, **kwargs):
        """Override delete to prevent cascade — clinical data must be archived, not deleted."""
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Patient deletion is not permitted. Use registration_status='inactive' to mark patients as inactive.")

    def save(self, *args, **kwargs):
        if not self.patient_id:
            for _ in range(5):
                self.patient_id = next_patient_id()
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    self.patient_id = ""
                    continue
        return super().save(*args, **kwargs)


class UserSiteRole(models.Model):
    """Maps a user to a site with a specific role for multi-center RBAC."""
    class Role(models.TextChoices):
        SITE_COORDINATOR = "site_coordinator", "Site Coordinator"
        SITE_INVESTIGATOR = "site_investigator", "Site Investigator"
        SITE_DATA_MANAGER = "site_data_manager", "Site Data Manager"
        SITE_READONLY = "site_readonly", "Site Read-Only"

    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="site_roles"
    )
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name="user_roles"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SITE_READONLY)
    is_primary = models.BooleanField(default=False,
                                      help_text="Primary site assignment for this user")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "site")]
        verbose_name = "User-Site Role"
        verbose_name_plural = "User-Site Roles"

    def __str__(self):
        return f"{self.user.username} @ {self.site.code} ({self.get_role_display()})"
