"""
Prescription   — the printable clinical artifact, one per encounter, versioned
                 and immutable once finalized (medico-legal + audit).
PrescriptionItem — a single "what to take now" line. Because we print the FULL
                 current medication list each visit, the set of items at finalize
                 time IS the patient's standing regimen — which is exactly what
                 the reconciliation engine diffs against open exposures.
"""
import hashlib

from django.conf import settings
from django.db import models

from encounters.models import ClinicalEncounter
from treatments.models import DrugMaster


class Prescription(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft (editable)"
        FINAL = "final", "Finalized (printed, immutable)"

    encounter = models.ForeignKey(
        ClinicalEncounter, on_delete=models.PROTECT, related_name="prescriptions"
    )
    version = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=8, choices=Status.choices, default=Status.DRAFT
    )

    diagnosis_text = models.CharField(max_length=240, blank=True)
    comorbidities = models.CharField(
        max_length=240, blank=True,
        help_text="Relevant comorbidities (e.g. Hypertension, Diabetes) — "
                  "prints on the slip; pre-filled from baseline."
    )
    investigations_advised = models.TextField(
        blank=True, help_text="Labs/tests ordered at this visit (free text)."
    )
    advice = models.TextField(
        blank=True,
        help_text="General advice / OTC or temporary drug advice "
                  "(e.g. paracetamol for fever) — prints on the slip."
    )
    stop_notes = models.TextField(
        blank=True,
        help_text="Justifications for drugs removed at this visit "
                  "(drug — reason), captured when a medication is stopped."
    )

    # Snapshot / provenance once printed.
    printed_at = models.DateTimeField(null=True, blank=True)
    printed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        null=True, blank=True, related_name="printed_prescriptions",
    )
    pdf_file = models.FileField(upload_to="prescriptions/%Y/%m/", blank=True)
    content_hash = models.CharField(max_length=64, blank=True)

    # Set when the reconciliation engine has projected this Rx onto the
    # TreatmentExposure table. Guarantees we never reconcile twice.
    reconciled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["encounter", "version"], name="uniq_encounter_version"
            )
        ]

    def __str__(self):
        return f"Rx {self.encounter.patient.patient_id} v{self.version} ({self.status})"

    @property
    def patient(self):
        return self.encounter.patient

    @property
    def is_final(self):
        return self.status == self.Status.FINAL

    def compute_hash(self):
        """Stable hash of the clinical content, for the immutable snapshot."""
        parts = [str(self.encounter_id), str(self.version), self.diagnosis_text]
        for it in self.items.all().order_by("id"):
            parts.append(
                f"{it.drug_id}|{it.brand}|{it.strength}|{it.dose}|{it.route}|"
                f"{it.frequency}|{it.timing}|{it.duration}"
            )
        return hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()


class PrescriptionItem(models.Model):
    class Timing(models.TextChoices):
        BEFORE_MEAL = "before", "Before meal"
        AFTER_MEAL = "after", "After meal"
        EMPTY = "empty", "Empty stomach"
        ANY = "any", "Any time"

    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="items"
    )
    drug = models.ForeignKey(DrugMaster, on_delete=models.PROTECT)
    brand = models.CharField(max_length=120, blank=True)
    strength = models.CharField(max_length=40, blank=True)

    # Dosing as the clinician writes it.
    dose = models.CharField(max_length=40, blank=True, help_text='e.g. "10 mg"')
    dose_unit = models.CharField(max_length=20, blank=True)
    # Route of administration for THIS line — a drug like cyclophosphamide can
    # be PO on one prescription and IV on another. Blank -> drug default route.
    route = models.CharField(max_length=20, blank=True)
    frequency = models.CharField(max_length=40, blank=True, help_text='e.g. "1+0+1"')
    timing = models.CharField(
        max_length=8, choices=Timing.choices, default=Timing.AFTER_MEAL
    )
    duration = models.CharField(max_length=40, blank=True, help_text='e.g. "continue"')

    # Bilingual patient instruction (Bangla shown on the printout).
    instruction_bn = models.CharField(max_length=240, blank=True)

    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.drug.generic_name} {self.dose} {self.frequency}".strip()

    @property
    def signature(self):
        """Regimen identity used by reconciliation to detect dose changes."""
        return (self.dose.strip().lower(), self.frequency.strip().lower(),
                self.route_value)

    @property
    def route_value(self):
        """The effective route: the line's own route, else the drug default.
        Feeds the reconciliation signature, so a PO→IV switch correctly splits
        the exposure episode."""
        return (self.route or self.drug.default_route or "PO").strip().upper()


class AdviceTemplate(models.Model):
    """Reusable, pre-written advice snippet the clinician can paste into a
    prescription's advice field from a dropdown — build several in advance
    (e.g. "Nephrotic diet", "Steroid counselling", "Sick-day rules")."""
    title = models.CharField(max_length=100, unique=True,
                             help_text="Heading shown in the dropdown.")
    body = models.TextField(help_text="The advice text pasted into the field.")
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title
