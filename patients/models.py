"""
Minimal Patient model — just enough of the core registry for the prescription
module to hang off. The full registry (baseline, labs, pathology, outcomes)
plugs in around this without changing the prescription workflow.
"""
from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from . import choices
from .comorbidity import LEVEL2_COMORBIDITY_FIELDS as CONDITION_FIELDS
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
        # Diabetes is known (e.g. a duration was recorded) but its type was
        # never stated. Needs clinician confirmation; never assumed to be T2.
        UNKNOWN = "unknown", "Diabetes, type not recorded"

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
    # CURRENT state of each condition, owned here. Three-state: True present,
    # False absent, None not recorded. Every change is stamped in
    # condition_provenance (see save()); a False with no stamp is a legacy
    # default from before 2026-09-27 and reads as "not recorded", never as a
    # verified negative. The baseline keeps its own dated enrollment snapshot.
    hypertension = models.BooleanField(null=True, blank=True, default=None)
    autoimmune_disease = models.BooleanField(null=True, blank=True, default=None)
    chronic_infection = models.BooleanField(
        null=True, blank=True, default=None, help_text="HBV / HCV / HIV / TB")
    smoking_status = models.CharField(
        max_length=20, blank=True, choices=choices.SMOKING)
    hepatitis_status = models.CharField(
        max_length=20, blank=True,
        choices=[("", "—"), ("negative", "Negative"), ("hbv", "HBV"),
                 ("hcv", "HCV"), ("both", "HBV + HCV")])
    hiv_status = models.CharField(
        max_length=10, blank=True,
        choices=[("", "—"), ("negative", "Negative"), ("positive", "Positive")])
    # Persistent comorbidities. These used to be asked only on the baseline
    # assessment, which meant they could not be recorded at registration and
    # never reached the prescription pre-fill or the AI prompts. They belong
    # here with the rest of Level 2 — recorded once, carried forward.
    cvd_history = models.BooleanField(
        null=True, blank=True, default=None, verbose_name="Cardiovascular disease")
    malignancy = models.BooleanField(null=True, blank=True, default=None)
    previous_kidney_disease = models.BooleanField(null=True, blank=True, default=None)
    prior_immunosuppression = models.BooleanField(
        null=True, blank=True, default=None, verbose_name="Previous immunosuppressive therapy")
    family_history_kidney = models.BooleanField(
        null=True, blank=True, default=None, verbose_name="Family history of kidney disease")
    diabetic_retinopathy = models.BooleanField(null=True, blank=True, default=None)
    neuropathy = models.BooleanField(null=True, blank=True, default=None)
    diabetic_foot_history = models.BooleanField(
        null=True, blank=True, default=None, verbose_name="Diabetic foot disease")
    # Per-condition provenance of the current state:
    #   {"hypertension": {"value": true, "at": ISO, "by": user_id|null,
    #                     "source": "patient_form"|"api"|"correction"|..., "reason": ""}}
    condition_provenance = models.JSONField(default=dict, blank=True, editable=False)

    # Pathology summary: a read-only PROJECTION of the selected biopsy's
    # interpretation, written only by pathology.services.projection. It is
    # distinct from primary_diagnosis, the clinician's working diagnosis.
    pathology_source_biopsy = models.ForeignKey(
        "pathology.Biopsy", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", editable=False,
        help_text="Biopsy the pathology summary below is projected from.")
    pathology_projection_state = models.CharField(
        max_length=12, blank=True, editable=False,
        choices=[("", "—"), ("final", "Final (reviewed)"),
                 ("provisional", "Provisional (local read, review pending)")])
    pathology_projected_at = models.DateTimeField(null=True, blank=True, editable=False)
    biopsy_diagnosis = models.CharField(
        max_length=120, blank=True,
        help_text="GN diagnosis from biopsy (projected from the selected biopsy)")
    gn_broad_group = models.CharField(
        max_length=80, blank=True, choices=choices.GN_BROAD_GROUP,
        help_text="Broad disease category (auto-synced from GNDiagnosis)")
    gn_primary_secondary = models.CharField(
        max_length=10, blank=True,
        choices=[("", "—"), ("primary", "Primary"), ("secondary", "Secondary"),
                 ("unknown", "Unknown")],
        help_text="Primary vs secondary GN (auto-synced from GNDiagnosis)")
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

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_conditions = {
            f: getattr(instance, f, None) for f in CONDITION_FIELDS
            if f in instance.__dict__}
        return instance

    def refresh_from_db(self, *args, **kwargs):
        super().refresh_from_db(*args, **kwargs)
        # The reloaded values are the new "unchanged" state for provenance.
        loaded = dict(getattr(self, "_loaded_conditions", None) or {})
        for f in CONDITION_FIELDS:
            if f in self.__dict__:
                loaded[f] = getattr(self, f)
        self._loaded_conditions = loaded

    def _stamp_condition_provenance(self):
        """Record who/when/how for every condition whose state changed.

        Callers attach context with ``patient.provenance_source`` /
        ``provenance_reason`` / ``provenance_by`` before saving; the audit
        actor is used otherwise. Untouched conditions keep their stamp.
        """
        from django.utils import timezone
        loaded = getattr(self, "_loaded_conditions", None)
        if loaded is None:            # new instance: stamp what was set
            loaded = {f: None for f in CONDITION_FIELDS}
        changed = [f for f in CONDITION_FIELDS
                   if f in loaded and getattr(self, f) != loaded[f]]
        if not changed:
            return []
        by = getattr(self, "provenance_by", None)
        if by is None:
            try:
                from audit.local import current_actor
                by = current_actor()
            except Exception:  # pragma: no cover - audit app unavailable
                by = None
        stamp = {
            "at": timezone.now().isoformat(timespec="seconds"),
            "by": getattr(by, "pk", None),
            "source": getattr(self, "provenance_source", "") or "update",
            "reason": getattr(self, "provenance_reason", "") or "",
        }
        prov = dict(self.condition_provenance or {})
        for f in changed:
            prov[f] = {"value": getattr(self, f), "previous": loaded.get(f), **stamp}
        self.condition_provenance = prov
        return changed

    def save(self, *args, **kwargs):
        changed = self._stamp_condition_provenance()
        update_fields = kwargs.get("update_fields")
        if changed and update_fields is not None:
            kwargs["update_fields"] = list(set(update_fields) | {"condition_provenance"})
        self._loaded_conditions = {f: getattr(self, f) for f in CONDITION_FIELDS}
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
