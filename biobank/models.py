"""
Biobank — serial sample storage (serum, plasma, urine, DNA, tissue) for the
future biomarker work (Gd-IgA1, complement, genetics) the portfolio describes.

Every sample requires biobank consent. The gate is enforced in clean() so admin
forms validate, and in store_sample() for programmatic use.
"""
from django.core.exceptions import ValidationError
from django.db import models

from patients.models import Patient


class Sample(models.Model):
    class Type(models.TextChoices):
        SERUM = "serum", "Serum"
        PLASMA = "plasma", "Plasma"
        URINE = "urine", "Urine"
        DNA = "dna", "DNA"
        TISSUE = "tissue", "Tissue"

    class Status(models.TextChoices):
        STORED = "stored", "Stored"
        DEPLETED = "depleted", "Depleted"
        SHIPPED = "shipped", "Shipped"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="samples")
    sample_type = models.CharField(max_length=8, choices=Type.choices)
    collection_date = models.DateField()
    volume_ml = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    aliquots = models.PositiveSmallIntegerField(default=1)
    storage_location = models.CharField(max_length=80, blank=True)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.STORED)
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "-collection_date"]

    def __str__(self):
        return f"{self.patient.patient_id} {self.get_sample_type_display()} @ {self.collection_date}"

    def clean(self):
        from audit.models import Consent
        from audit.services.consent import has_consent
        if not has_consent(self.patient, Consent.Type.BIOBANK):
            raise ValidationError(
                "Biobank consent is not on file for this patient — "
                "cannot store samples.")
