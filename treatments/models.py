"""
DrugMaster      — the clinic formulary AND the research-coding bridge.
TreatmentExposure — one row per *episode* of a drug at a dose. This is the
research-grade table the portfolio depends on (new-user cohorts, target-trial
emulation). It is written automatically by the reconciliation engine from the
prescription — clinicians never edit it directly.
"""
from django.core.exceptions import ValidationError
from django.db import models

from patients.models import Patient


class DrugClass(models.TextChoices):
    """Maps a prescribed drug to the exposure variable analytics cares about.

    These are the classes the BGDDR research portfolio analyses by name
    (HCQ, MMF, finerenone, SGLT2i, steroids, rituximab ...). Adding the right
    class here is what lets the analytics layer classify exposure with zero
    manual coding.
    """
    RAASI = "raasi", "RAAS inhibitor (ACEi/ARB)"
    SGLT2I = "sglt2i", "SGLT2 inhibitor"
    FINERENONE = "finerenone", "Finerenone (ns-MRA)"
    HCQ = "hcq", "Hydroxychloroquine"
    STEROID = "steroid", "Corticosteroid"
    MMF = "mmf", "Mycophenolate"
    AZATHIOPRINE = "azathioprine", "Azathioprine"
    CYCLOPHOSPHAMIDE = "cyclophosphamide", "Cyclophosphamide"
    CNI = "cni", "Calcineurin inhibitor"
    RITUXIMAB = "rituximab", "Rituximab"
    DIURETIC = "diuretic", "Diuretic"
    STATIN = "statin", "Statin"
    # Antidiabetic classes (distinct so common combinations are NOT flagged as
    # duplicate therapy, and so analytics can classify glucose-lowering exposure).
    INSULIN = "insulin", "Insulin"
    METFORMIN = "metformin", "Metformin (biguanide)"
    SULFONYLUREA = "sulfonylurea", "Sulfonylurea"
    DPP4I = "dpp4i", "DPP-4 inhibitor"
    GLP1 = "glp1", "GLP-1 receptor agonist"
    OTHER = "other", "Other / not research-coded"


class Route(models.TextChoices):
    """Routes of administration a prescription line can carry (mirrors FHIR
    dosageInstruction.route, trimmed to what the clinic actually uses)."""
    PO = "PO", "Oral (PO)"
    IV = "IV", "Intravenous (IV)"
    IM = "IM", "Intramuscular (IM)"
    SC = "SC", "Subcutaneous (SC)"
    SL = "SL", "Sublingual (SL)"
    TOP = "TOP", "Topical"
    INH = "INH", "Inhaled"
    PR = "PR", "Rectal (PR)"


class DrugMaster(models.Model):
    generic_name = models.CharField(max_length=120, unique=True)
    brand_names = models.JSONField(
        default=list, blank=True,
        help_text="Common Bangladeshi brand names, most-used first."
    )
    drug_class = models.CharField(
        max_length=20, choices=DrugClass.choices, default=DrugClass.OTHER
    )
    available_strengths = models.JSONField(
        default=list, blank=True, help_text='e.g. ["5 mg", "10 mg", "20 mg"]'
    )
    default_frequency = models.CharField(
        max_length=40, blank=True, help_text='e.g. "1+0+1" or "once daily"'
    )
    default_route = models.CharField(max_length=20, blank=True, default="PO")
    # Routes this drug can be given by, e.g. ["PO", "IV"] for cyclophosphamide.
    # Empty list -> [default_route].
    available_routes = models.JSONField(
        default=list, blank=True,
        help_text='Routes of administration, e.g. ["PO", "IV"].'
    )
    # Optional per-route strengths, e.g. {"PO": ["50 mg"], "IV": ["500 mg vial"]}.
    # A route without an entry falls back to available_strengths.
    strengths_by_route = models.JSONField(
        default=dict, blank=True,
        help_text='Strengths per route, e.g. {"IV": ["500 mg vial", "1 g vial"]}.'
    )

    # --- Safety flags used by the prescription checks -----------------------
    renal_dose_adjust = models.BooleanField(default=False)
    # Below this eGFR the drug needs review / is often contraindicated.
    egfr_caution_below = models.DecimalField(
        max_digits=4, decimal_places=0, null=True, blank=True
    )

    # --- V3.5 Drug Intelligence certification fields ------------------------
    nephrotoxic = models.BooleanField(default=False, help_text="Known nephrotoxic agent")
    hepatic_dose_adjust = models.BooleanField(default=False, help_text="Requires dose adjustment in hepatic impairment")
    dialysis_dose_adjust = models.BooleanField(default=False, help_text="Requires dose adjustment/administration timing with dialysis")
    pregnancy_category = models.CharField(
        max_length=3, blank=True,
        help_text="FDA pregnancy category (A, B, C, D, X, N)"
    )
    lactation_safety = models.CharField(
        max_length=20, blank=True,
        help_text="Lactation safety: safe, caution, contraindicated, unknown"
    )
    indications = models.JSONField(
        default=list, blank=True,
        help_text="Approved indications: list of disease/condition identifiers",
    )

    # --- V4.0 Drug Knowledge Platform fields -------------------------------
    mechanism_of_action = models.TextField(blank=True, help_text="Pharmacological mechanism of action")
    common_side_effects = models.JSONField(default=list, blank=True, help_text="Common adverse effects (frequency >= 1%)")
    serious_side_effects = models.JSONField(default=list, blank=True, help_text="Serious adverse effects requiring attention")
    monitoring_parameters = models.TextField(blank=True, help_text="Required monitoring: labs, vitals, levels")
    stopping_criteria = models.TextField(blank=True, help_text="Criteria for stopping or holding the drug")
    evidence_level = models.CharField(
        max_length=2, blank=True,
        choices=[("1", "Level 1 (Strong recommendation)"), ("2", "Level 2 (Weak recommendation)"),
                 ("NG", "Not graded"), ("OP", "Expert opinion")],
        help_text="GRADE evidence level for GN indications",
    )
    guideline_recommendations = models.JSONField(
        default=list, blank=True,
        help_text="Guideline recommendations referencing this drug: [{source, chapter, recommendation}]",
    )
    typical_dosage = models.CharField(max_length=200, blank=True, help_text="Typical starting and maintenance dosage")
    maximum_dose = models.CharField(max_length=100, blank=True, help_text="Maximum recommended daily dose")
    transplant_considerations = models.TextField(blank=True, help_text="Special considerations in transplant patients")

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["generic_name"]

    def __str__(self):
        return f"{self.generic_name} ({self.get_drug_class_display()})"

    @property
    def routes(self):
        """Effective route list (never empty)."""
        return self.available_routes or [self.default_route or "PO"]

    def strengths_for_route(self, route):
        """Strengths offered for a route, falling back to the flat list."""
        return (self.strengths_by_route or {}).get(route) or self.available_strengths


class DrugSyncRun(models.Model):
    """Audit trail for the automated MedEx drug-catalogue refresh.

    One row per attempt. Exists for three reasons:

    1. `should_sync_now()` needs to know when the catalogue last imported
       cleanly, and `content_hash` lets a run detect "nothing changed" and
       skip the (destructive) import entirely rather than rewriting 1.5k
       rows for no reason.
    2. An unattended job that deletes DrugMaster rows must leave a reviewable
       record of exactly what it merged, added and deleted.
    3. Clinicians need to answer "which brands are actually available?" -
       a stale catalogue is a clinical-safety issue, so `state` and
       `finished_at` are surfaced in the admin.
    """

    class State(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Succeeded"
        UNCHANGED = "unchanged", "Succeeded (catalogue unchanged)"
        SKIPPED = "skipped", "Skipped"
        FAILED = "failed", "Failed"

    class Trigger(models.TextChoices):
        MANUAL = "manual", "Manual"
        SCHEDULED = "scheduled", "Scheduled"

    state = models.CharField(
        max_length=12, choices=State.choices, default=State.RUNNING,
        db_index=True,
    )
    trigger = models.CharField(
        max_length=12, choices=Trigger.choices, default=Trigger.SCHEDULED,
    )
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    # Scrape
    pages_fetched = models.PositiveIntegerField(default=0)
    total_pages = models.PositiveIntegerField(default=0)
    rows_scraped = models.PositiveIntegerField(default=0)
    content_hash = models.CharField(max_length=64, blank=True, db_index=True)

    # Import outcome
    generics_created = models.PositiveIntegerField(default=0)
    generics_updated = models.PositiveIntegerField(default=0)
    brands_added = models.PositiveIntegerField(default=0)
    strengths_added = models.PositiveIntegerField(default=0)
    routes_added = models.PositiveIntegerField(default=0)
    rows_merged = models.PositiveIntegerField(default=0)
    rows_deleted = models.PositiveIntegerField(default=0)
    fks_repointed = models.PositiveIntegerField(default=0)

    error = models.TextField(blank=True)
    detail = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "drug sync run"

    def __str__(self):
        return f"MedEx sync {self.started_at:%Y-%m-%d %H:%M} ({self.state})"

    @property
    def duration_seconds(self):
        if not self.finished_at:
            return None
        return (self.finished_at - self.started_at).total_seconds()


class StopReason(models.TextChoices):
    REMISSION = "remission", "Remission / goal achieved"
    NON_RESPONSE = "non_response", "Non-response"
    INTOLERANCE = "intolerance", "Intolerance / side-effect"
    ADVERSE_EVENT = "adverse_event", "Adverse event"
    COST = "cost", "Cost / access"
    DOSE_CHANGE = "dose_change", "Dose/regimen changed (episode split)"
    SWITCH = "switch", "Switched to another agent"
    COMPLETED = "completed", "Planned course completed"
    OTHER = "other", "Other / unspecified"


class TreatmentExposure(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="exposures"
    )
    drug = models.ForeignKey(
        DrugMaster, on_delete=models.PROTECT, related_name="exposures"
    )
    # Denormalized snapshot of what was actually prescribed at the time.
    drug_name = models.CharField(max_length=120)
    # The regimen amount per administration (PrescriptionItem.regimen_dose):
    # compared by the reconciliation signature, so a change in the number of
    # tablets at an unchanged product strength splits the episode. 120 to hold
    # combination-product strengths without truncation on PostgreSQL.
    dose = models.CharField(max_length=120, blank=True)
    # Product strength as prescribed (e.g. "5 mg"); display only.
    strength = models.CharField(max_length=120, blank=True)
    dose_unit = models.CharField(max_length=20, blank=True)
    frequency = models.CharField(max_length=40, blank=True)
    route = models.CharField(max_length=20, blank=True, default="PO")

    start_date = models.DateField()
    stop_date = models.DateField(null=True, blank=True)
    ongoing = models.BooleanField(default=True)
    stop_reason = models.CharField(
        max_length=20, choices=StopReason.choices, blank=True
    )

    # Provenance: which encounters opened and closed this episode. Makes the
    # reconciliation idempotent and gives a full audit trail.
    opened_by_encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="opened_exposures",
    )
    closed_by_encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="closed_exposures",
    )

    def clean(self):
        if self.ongoing and self.stop_date:
            raise ValidationError({"stop_date": "Ongoing exposure cannot have a stop date."})
        if not self.ongoing and not self.stop_date:
            raise ValidationError({"stop_date": "Completed exposure must have a stop date."})
        if self.start_date and self.stop_date and self.stop_date < self.start_date:
            raise ValidationError({"stop_date": "Stop date cannot be before start date."})

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "drug__generic_name", "start_date"]
        indexes = [
            models.Index(fields=["patient", "ongoing"]),
            models.Index(fields=["drug", "ongoing"]),
        ]
        constraints = [
            # One ongoing episode per drug. The reconciliation engine assumes
            # this ("Engine invariant" in _open_exposures_by_drug) and the
            # manual form checked it, but nothing enforced it in the database —
            # so the API, an import or a race could open a second episode for a
            # drug already running. The engine keys its diff by drug, so the
            # extra episode is invisible to it: never continued, never closed,
            # left ongoing forever, and counted again by every exposure query
            # downstream.
            models.UniqueConstraint(
                fields=["patient", "drug"],
                condition=models.Q(ongoing=True),
                name="one_ongoing_exposure_per_drug",
            ),
        ]

    def __str__(self):
        span = f"{self.start_date} → {self.stop_date or 'ongoing'}"
        return f"{self.patient.patient_id}: {self.drug_name} {self.dose} ({span})"

    @property
    def signature(self):
        """Regimen identity, compared against a prescription item to detect a
        dose/regimen change (which splits the episode)."""
        return (self.dose.strip().lower(), self.frequency.strip().lower(),
                (self.route or "PO").strip().upper())
