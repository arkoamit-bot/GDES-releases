"""
Longitudinal laboratory model.

Real-world flow: a lab is ORDERED at one visit and RESULTED at a later date.
So results cannot live as flat baseline columns — they are time-series rows, one
per (patient, test, date). This is what feeds the trajectories the research
portfolio depends on: eGFR slope, anti-PLA2R kinetics, proteinuria trends.

    LabTest      — the test catalog (LOINC-ready), reference ranges, units
    LabPanel     — a named bundle of tests for one-click ordering
    LabOrder     — placed at a ClinicalEncounter (the "record the lab" step)
    LabOrderItem — one ordered test; gets fulfilled by a LabResult
    LabResult    — the longitudinal value; eGFR is auto-derived from creatinine
"""
from django.core.exceptions import ValidationError
from django.db import models

from encounters.models import ClinicalEncounter
from patients.models import Patient


class LabTest(models.Model):
    class ValueType(models.TextChoices):
        NUMERIC = "numeric", "Numeric"
        QUALITATIVE = "qualitative", "Qualitative (pos/neg/text)"

    code = models.SlugField(max_length=40, unique=True)   # e.g. "creatinine"
    name = models.CharField(max_length=120)
    loinc = models.CharField(max_length=20, blank=True)
    default_unit = models.CharField(max_length=20, blank=True)
    value_type = models.CharField(
        max_length=12, choices=ValueType.choices, default=ValueType.NUMERIC)

    # Reference range for the abnormal flag (numeric tests only).
    ref_low = models.DecimalField(max_digits=10, decimal_places=3,
                                  null=True, blank=True)
    ref_high = models.DecimalField(max_digits=10, decimal_places=3,
                                   null=True, blank=True)

    # Derived tests (eGFR) are computed, not entered directly.
    is_derived = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class LabPanel(models.Model):
    code = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=120)
    tests = models.ManyToManyField(LabTest, related_name="panels")

    def __str__(self):
        return self.name


class LabOrder(models.Model):
    class Status(models.TextChoices):
        ORDERED = "ordered", "Ordered"
        COLLECTED = "collected", "Sample collected"
        RESULTED = "resulted", "Resulted"
        CANCELLED = "cancelled", "Cancelled"

    encounter = models.ForeignKey(
        ClinicalEncounter, on_delete=models.PROTECT, related_name="lab_orders")
    # Denormalized for easy per-patient querying without joining through encounter.
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="lab_orders")
    ordered_date = models.DateField()
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.ORDERED)
    notes = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ordered_date"]
        indexes = [models.Index(fields=["patient", "ordered_date"])]

    def __str__(self):
        return f"Order {self.patient.patient_id} · {self.ordered_date} ({self.status})"

    def refresh_status(self):
        items = list(self.items.all())
        if items and all(i.is_resulted for i in items):
            self.status = self.Status.RESULTED
            self.save(update_fields=["status"])


class LabOrderItem(models.Model):
    order = models.ForeignKey(
        LabOrder, on_delete=models.CASCADE, related_name="items")
    test = models.ForeignKey(LabTest, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["order", "test"],
                                    name="uniq_order_test")
        ]

    def __str__(self):
        return f"{self.order_id}:{self.test.code}"

    @property
    def is_resulted(self):
        return self.results.exists()


class CurrentResultManager(models.Manager):
    """Default manager: only current observations.

    A corrected result is superseded, not overwritten. Superseded rows (and
    the derivations made from them) stay in the table for lineage and are
    reachable through ``LabResult.all_objects`` and ``result.supersedes``;
    every ordinary query -- trends, latest value, exports, reasoning -- sees
    the current observation only.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_current=True)


class LabResult(models.Model):
    class Source(models.TextChoices):
        LAB = "lab", "Laboratory"
        MANUAL = "manual", "Manual entry"
        DERIVED = "derived", "Derived (computed)"
        LEGACY = "legacy", "Legacy value (reconciled from an older form)"

    class EntryPath(models.TextChoices):
        GUIDED = "guided", "Results page"
        BASELINE = "baseline", "Baseline form"
        API = "api", "API"
        ADMIN = "admin", "Admin"
        IMPORT = "import", "Import"
        FHIR = "fhir", "FHIR"
        DERIVED = "derived", "Derived"
        RECONCILE = "reconcile", "Reconciliation"
        OTHER = "other", "Other"

    class Flag(models.TextChoices):
        NORMAL = "", "Normal"
        LOW = "L", "Low"
        HIGH = "H", "High"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="lab_results")
    test = models.ForeignKey(
        LabTest, on_delete=models.PROTECT, related_name="results")
    # Optional link back to what was ordered (results can also arrive unsolicited).
    order_item = models.ForeignKey(
        LabOrderItem, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="results")

    value_numeric = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True)
    value_text = models.CharField(max_length=120, blank=True)
    unit = models.CharField(max_length=20, blank=True)

    sample_date = models.DateField(null=True, blank=True)
    result_date = models.DateField()
    flag = models.CharField(max_length=1, choices=Flag.choices, blank=True)
    source = models.CharField(
        max_length=8, choices=Source.choices, default=Source.LAB)

    # Provenance for derived values (eGFR ← creatinine) + the formula version,
    # so multi-year slopes stay reproducible even if the equation is updated.
    derived_from = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="derivations")
    formula_version = models.CharField(max_length=40, blank=True)

    # Correction lineage: a correction is a new row that supersedes this one.
    supersedes = models.OneToOneField(
        "self", on_delete=models.PROTECT, null=True, blank=True,
        related_name="superseded_by")
    is_current = models.BooleanField(default=True, db_index=True)
    correction_reason = models.CharField(max_length=240, blank=True)

    # Entry provenance and duplicate protection. idempotency_key makes a
    # retried submission return the row it already created; it is NOT a
    # uniqueness rule on patient+test+date (a genuine same-day repeat
    # measurement is a second row). source_report_id / specimen_id identify the
    # laboratory report when it is known.
    idempotency_key = models.CharField(max_length=80, blank=True, db_index=True)
    source_report_id = models.CharField(max_length=60, blank=True)
    specimen_id = models.CharField(max_length=60, blank=True)
    entry_path = models.CharField(max_length=10, choices=EntryPath.choices, blank=True)
    entered_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+")

    objects = CurrentResultManager()
    all_objects = models.Manager()

    def clean(self):
        if self.value_numeric is None and not self.value_text:
            raise ValidationError("At least one of value_numeric or value_text must be provided.")
        if self.sample_date and self.result_date and self.sample_date > self.result_date:
            raise ValidationError({"sample_date": "Sample date cannot be after result date."})

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["patient", "test__code", "result_date"]
        indexes = [
            models.Index(fields=["patient", "test", "result_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="uniq_labresult_idempotency_key"),
        ]
        base_manager_name = "all_objects"

    def __str__(self):
        v = self.value_numeric if self.value_numeric is not None else self.value_text
        return f"{self.patient.patient_id} {self.test.code}={v} {self.unit} @{self.result_date}"

    @classmethod
    def series(cls, patient, test_code):
        """Time-ordered values for one patient+test — the trajectory primitive."""
        return (cls.objects
                .filter(patient=patient, test__code=test_code)
                .order_by("result_date"))
