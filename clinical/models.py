from django.db import models
from patients.models import Patient


class ClinicalAssessment(models.Model):
    encounter = models.OneToOneField("encounters.ClinicalEncounter", on_delete=models.CASCADE, related_name="clinical_assessment")
    chief_complaint = models.TextField(blank=True)
    time_course = models.CharField(max_length=20, choices=[
        ("acute", "Acute days to weeks"),
        ("subacute", "Subacute weeks to months"),
        ("chronic", "Chronic or incidental"),
        ("relapsing", "Relapsing"),
    ], default="subacute")
    features = models.JSONField(default=list, blank=True, help_text="Clinical feature codes: edema, hypertension, grossHematuria, purpura, arthritis, sinopulmonary, hemoptysis, sle, diabetes")
    syndrome_classification = models.CharField(max_length=100, blank=True, help_text="e.g. Nephrotic syndrome, Rapidly progressive nephritic syndrome")
    syndrome_classified_at = models.DateTimeField(null=True, blank=True)
    severity_flags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["encounter"])]

    def __str__(self):
        return f"ClinicalAssessment for encounter {self.encounter_id}"


class VitalSign(models.Model):
    encounter = models.ForeignKey("encounters.ClinicalEncounter", on_delete=models.CASCADE, related_name="vitals")
    bp_systolic = models.PositiveSmallIntegerField(null=True, blank=True)
    bp_diastolic = models.PositiveSmallIntegerField(null=True, blank=True)
    heart_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
