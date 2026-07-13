"""
Adverse-event / safety capture (protocol §9.4).

The registry's safety co-primary: serious adverse events, infections (a major
burden in Bangladesh and under immunosuppression), steroid toxicity, and the
counts the DSMB reviews. Coded so the portfolio's infection studies (Study 20:
infection risk by agent and diabetes status; Study 23: diabetic IRGN) are
answerable, and so per-study SAE rates can be tabulated by arm.

This is distinct from encounters.ClinicalEvent (efficacy endpoints like ESKD /
death / remission) — AdverseEvent is the harms side.
"""
from django.db import models

from patients.models import Patient
from treatments.models import DrugMaster


class AdverseEvent(models.Model):
    class Category(models.TextChoices):
        INFECTION = "infection", "Infection"
        STEROID_TOXICITY = "steroid_toxicity", "Steroid toxicity"
        HEMATOLOGIC = "hematologic", "Haematologic"
        HEPATIC = "hepatic", "Hepatotoxicity"
        NEPHROTOXICITY = "nephrotoxicity", "Nephrotoxicity"
        CARDIOVASCULAR = "cardiovascular", "Cardiovascular"
        MALIGNANCY = "malignancy", "Malignancy"
        INFUSION_REACTION = "infusion_reaction", "Infusion reaction"
        OTHER = "other", "Other"

    class InfectionType(models.TextChoices):
        TB = "tb", "Tuberculosis"
        PJP = "pjp", "Pneumocystis (PJP)"
        CMV = "cmv", "CMV"
        ZOSTER = "zoster", "Herpes zoster"
        PNEUMONIA = "pneumonia", "Pneumonia"
        CELLULITIS = "cellulitis", "Cellulitis"
        SEPSIS = "sepsis", "Sepsis"
        UTI = "uti", "Urinary tract infection"
        FUNGAL = "fungal", "Invasive fungal"
        HEPATITIS_FLARE = "hepatitis_flare", "Hepatitis B/C reactivation"
        OTHER = "other", "Other infection"

    class Severity(models.TextChoices):
        MILD = "mild", "Mild (G1)"
        MODERATE = "moderate", "Moderate (G2)"
        SEVERE = "severe", "Severe (G3)"
        LIFE_THREATENING = "life_threatening", "Life-threatening (G4)"
        FATAL = "fatal", "Fatal (G5)"

    class Outcome(models.TextChoices):
        RECOVERED = "recovered", "Recovered/resolved"
        RECOVERING = "recovering", "Recovering"
        SEQUELAE = "sequelae", "Recovered with sequelae"
        ONGOING = "ongoing", "Ongoing"
        FATAL = "fatal", "Fatal"

    class Relatedness(models.TextChoices):
        UNRELATED = "unrelated", "Unrelated"
        UNLIKELY = "unlikely", "Unlikely"
        POSSIBLE = "possible", "Possible"
        PROBABLE = "probable", "Probable"
        DEFINITE = "definite", "Definite"
        NOT_ASSESSED = "not_assessed", "Not assessed"

    SERIOUS_SEVERITIES = {Severity.LIFE_THREATENING, Severity.FATAL}

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="adverse_events")
    onset_date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)
    infection_type = models.CharField(
        max_length=16, choices=InfectionType.choices, blank=True,
        help_text="Only when category = infection.")
    description = models.CharField(max_length=240, blank=True)

    severity = models.CharField(max_length=18, choices=Severity.choices)
    serious = models.BooleanField(
        default=False, help_text="SAE: death, life-threatening, hospitalisation, "
        "disability, or other medically important event.")
    hospitalization = models.BooleanField(default=False)
    outcome = models.CharField(max_length=12, choices=Outcome.choices, blank=True)

    # Drug attribution — drives 'infection risk by agent' analyses.
    suspected_drug = models.ForeignKey(
        DrugMaster, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="adverse_events")
    relatedness = models.CharField(
        max_length=14, choices=Relatedness.choices, default=Relatedness.NOT_ASSESSED)

    encounter = models.ForeignKey(
        "encounters.ClinicalEncounter", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="adverse_events")
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "-onset_date"]
        indexes = [
            models.Index(fields=["patient", "onset_date"]),
            models.Index(fields=["category", "onset_date"]),
        ]

    def __str__(self):
        return f"{self.patient.patient_id}: {self.get_category_display()} ({self.onset_date})"

    def save(self, *args, **kwargs):
        # An SAE if explicitly flagged, hospitalised, or G4/G5 by severity.
        if self.hospitalization or self.severity in self.SERIOUS_SEVERITIES:
            self.serious = True
        super().save(*args, **kwargs)
