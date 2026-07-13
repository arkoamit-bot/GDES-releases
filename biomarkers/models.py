"""
Biomarker kinetics (protocol §9.3, portfolio Study 6).

Computed per-patient from the longitudinal LabResult series — like PatientOutcome,
not hand-entered. Headline is anti-PLA2R in membranous nephropathy:

  * >=50% decline (early decline = strong predictor of later remission)
  * seroconversion to negative = IMMUNOLOGICAL REMISSION (precedes proteinuria
    remission), with first-achieved dates so it is a time-to-event endpoint

Plus complement recovery (C3/C4 normalisation in LN/C3G) and anti-dsDNA
normalisation (LN).
"""
from django.db import models

from patients.models import Patient


class BiomarkerKinetics(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="biomarker_kinetics")

    # Anti-PLA2R (membranous nephropathy).
    pla2r_baseline = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    pla2r_latest = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    pla2r_nadir = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    pla2r_baseline_date = models.DateField(null=True, blank=True)
    pla2r_pct_decline = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    pla2r_50pct_decline = models.BooleanField(default=False)
    pla2r_50pct_date = models.DateField(null=True, blank=True)
    pla2r_50pct_days = models.IntegerField(
        null=True, blank=True, help_text="Days from baseline to >=50% decline.")
    # Seroconversion to negative = immunological remission.
    pla2r_immunological_remission = models.BooleanField(default=False)
    pla2r_remission_date = models.DateField(null=True, blank=True)

    # Complement recovery (lupus nephritis / C3 glomerulopathy).
    c3_recovered = models.BooleanField(default=False)
    c3_recovered_date = models.DateField(null=True, blank=True)
    c4_recovered = models.BooleanField(default=False)
    c4_recovered_date = models.DateField(null=True, blank=True)

    # Anti-dsDNA (lupus nephritis).
    dsdna_baseline = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    dsdna_latest = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    dsdna_normalized = models.BooleanField(default=False)
    dsdna_normalized_date = models.DateField(null=True, blank=True)

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["patient"]
        verbose_name_plural = "biomarker kinetics"

    def __str__(self):
        return f"Biomarkers {self.patient.patient_id}"

    def early_pla2r_responder(self, *, within_days=90):
        """True if a >=50% anti-PLA2R decline was reached within ``within_days``
        of baseline — the Study 6 early-response predictor."""
        return (self.pla2r_50pct_days is not None
                and self.pla2r_50pct_days <= within_days)
