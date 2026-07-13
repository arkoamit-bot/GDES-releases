"""
PatientOutcome — the computed "Outcome Engine" row, one per patient.

Per the registry's guiding principle, outcomes are NOT entered by hand: this row
is derived from the longitudinal labs, the treatment exposures, and the dated
clinical events, with the operational endpoint definitions fixed in code
(analytics/services/outcomes.py). Re-runnable any time via `compute_outcomes`.

It is also the denormalized, ML-ready "one row per patient" table the portfolio
asks for, and the source of the (duration, event) pairs the survival analysis
consumes.
"""
from django.db import models

from patients.models import Patient


class PatientOutcome(models.Model):
    class Remission(models.TextChoices):
        NONE = "none", "No remission"
        PARTIAL = "partial", "Partial remission"
        COMPLETE = "complete", "Complete remission"

    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="outcome")

    # Index / baseline.
    index_date = models.DateField(null=True, blank=True)
    baseline_egfr = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    baseline_creatinine = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    baseline_upcr = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)

    # Follow-up span.
    last_contact_date = models.DateField(null=True, blank=True)
    followup_days = models.IntegerField(null=True, blank=True)
    n_egfr = models.IntegerField(default=0)
    latest_egfr = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    egfr_slope = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    # Kidney-function endpoints (flag + date the endpoint was met).
    sustained_40_decline = models.BooleanField(default=False)
    sustained_40_date = models.DateField(null=True, blank=True)
    sustained_50_decline = models.BooleanField(default=False)
    sustained_50_date = models.DateField(null=True, blank=True)
    doubling_creatinine = models.BooleanField(default=False)
    doubling_date = models.DateField(null=True, blank=True)

    # Hard endpoints (from ClinicalEvent).
    eskd = models.BooleanField(default=False)
    eskd_date = models.DateField(null=True, blank=True)
    death = models.BooleanField(default=False)
    death_date = models.DateField(null=True, blank=True)

    # Composite kidney endpoint = earliest of {ESKD, sustained >=40% decline, death}.
    composite_kidney_event = models.BooleanField(default=False)
    composite_date = models.DateField(null=True, blank=True)
    composite_cause = models.CharField(max_length=40, blank=True)

    # --- Proteinuria regression (the primary disease-activity outcome) -------
    # Values are g/day (24-h UTP preferred; spot UPCR g/g used as a ~g/day
    # fallback). Remission rules are disease-specific (see services/remission.py).
    remission_definition = models.CharField(max_length=10, blank=True)   # igan/mn/lupus/...
    proteinuria_source = models.CharField(max_length=8, blank=True)      # utp/upcr/mixed
    latest_upcr = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    nadir_upcr = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    best_proteinuria_reduction_pct = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True)
    # IgAN proteinuria response: >=30% relative reduction OR < 0.3 g/day (§9.1).
    igan_proteinuria_response = models.BooleanField(default=False)
    igan_proteinuria_response_date = models.DateField(null=True, blank=True)
    # Sustained remission, with the date FIRST achieved (so it is time-to-event).
    complete_remission = models.BooleanField(default=False)
    complete_remission_date = models.DateField(null=True, blank=True)
    partial_remission = models.BooleanField(default=False)
    partial_remission_date = models.DateField(null=True, blank=True)
    any_remission_date = models.DateField(null=True, blank=True)   # earliest of the two
    # Loss of remission detected from the proteinuria trajectory.
    proteinuria_relapse = models.BooleanField(default=False)
    proteinuria_relapse_date = models.DateField(null=True, blank=True)

    # Best sustained remission achieved (complete > partial > none).
    remission_status = models.CharField(
        max_length=10, choices=Remission.choices, default=Remission.NONE)
    any_relapse = models.BooleanField(default=False)   # trajectory or event-based

    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["patient"]

    def __str__(self):
        return f"Outcome {self.patient.patient_id}"

    @property
    def any_remission(self):
        """True once the patient has reached complete OR partial remission."""
        return bool(self.any_remission_date)

    def duration_event(self, endpoint: str):
        """Return (duration_days, event_bool) for a survival endpoint, or None
        if the patient has no usable follow-up window.

        Kidney-failure endpoints (event = bad):
            "composite_kidney_event" | "eskd" | "death" |
            "sustained_40_decline" | "sustained_50_decline"
        Proteinuria-regression endpoints (event = good; 1 - KM = cumulative
        incidence of remission):
            "complete_remission" | "partial_remission" | "any_remission"
        """
        if not self.index_date or not self.last_contact_date:
            return None
        flag = getattr(self, endpoint)
        date_field = {
            "composite_kidney_event": "composite_date",
            "eskd": "eskd_date",
            "death": "death_date",
            "sustained_40_decline": "sustained_40_date",
            "sustained_50_decline": "sustained_50_date",
            "complete_remission": "complete_remission_date",
            "partial_remission": "partial_remission_date",
            "any_remission": "any_remission_date",
            "igan_proteinuria_response": "igan_proteinuria_response_date",
        }[endpoint]
        event_date = getattr(self, date_field)
        if flag and event_date:
            return ((event_date - self.index_date).days, True)
        return ((self.last_contact_date - self.index_date).days, False)
