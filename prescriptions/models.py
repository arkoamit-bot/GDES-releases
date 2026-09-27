"""
Prescription   — the printable clinical artifact, one per encounter, versioned
                 and immutable once finalized (medico-legal + audit).
PrescriptionItem — a single "what to take now" line. Because we print the FULL
                 current medication list each visit, the set of items at finalize
                 time IS the patient's standing regimen — which is exactly what
                 the reconciliation engine diffs against open exposures.
"""
import hashlib
import json

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
    # What the clinician chose to PRINT: a selection from the patient's
    # current conditions plus prescription-only notes. Omitting a condition
    # here is not a clinical deletion; the patient record is not changed.
    comorbidities = models.CharField(
        max_length=240, blank=True,
        help_text="Comorbidities printed on the slip — chosen from the "
                  "patient record, plus prescription-only notes."
    )
    # Catalogue tests are structured PrescriptionTestRequest rows (linked to
    # real LabOrders at finalization). This text holds only investigations
    # that are not in the catalogue, plus legacy prescriptions' free text.
    investigations_advised = models.TextField(
        blank=True, help_text="Investigations not in the lab catalogue (free text)."
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
    # 1 = the original hash (compute_hash; kept for prescriptions finalized
    # before issued snapshots). 2 = hash of the issued snapshot's clinical
    # content. A style-only template change alters neither.
    content_hash_version = models.PositiveSmallIntegerField(default=1)

    # Everything the printout shows, frozen at finalization (patient identity,
    # visit, vitals, eGFR with its source, diagnosis, printed comorbidities,
    # items, investigations, advice, next visit). Rendering a finalized
    # prescription reads this, so later edits to the patient, labs or
    # appointments never change a prescription already issued. Empty for
    # prescriptions finalized before 2026-09-27: their context was not kept and
    # is not reconstructed.
    issued_snapshot = models.JSONField(default=dict, blank=True, editable=False)
    snapshot_version = models.PositiveSmallIntegerField(default=0, editable=False)

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

    def compute_snapshot_hash(self):
        """Hash v2: the issued snapshot's clinical content (not its styling)."""
        content = {k: v for k, v in (self.issued_snapshot or {}).items()
                   if k not in ("clinic", "rendered_at")}
        blob = json.dumps(content, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def compute_hash(self):
        """Hash v1 -- unchanged, so prescriptions hashed with it still verify."""
        parts = [str(self.encounter_id), str(self.version), self.diagnosis_text]
        for it in self.items.all().order_by("id"):
            parts.append(
                f"{it.drug_id}|{it.brand}|{it.strength}|{it.dose}|{it.route}|"
                f"{it.frequency}|{it.timing}|{it.duration}|{it.taper_notes}"
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
    # 120, not 40: combination products legitimately carry multi-ingredient
    # strength strings, e.g. "1000 mg+327 mg (Conventional calcium)+500 mg+400 IU"
    # (51 chars) in the BD DrugBank formulary. At 40 these overflowed
    # PrescriptionItem.strength on PostgreSQL while SQLite accepted them.
    strength = models.CharField(max_length=120, blank=True)

    # Dose per administration, distinct from the product strength: a 5 mg
    # tablet taken as 2 tablets is strength "5 mg", dose "2" + unit "tab".
    # Blank = the clinic convention of one unit of the product per frequency
    # slot (1+0+1). Before 2026-09-27 the form copied the strength here, so a
    # dose equal to the strength means "not separately stated" (see
    # administered_dose); historical rows are never re-interpreted.
    dose = models.CharField(max_length=120, blank=True, help_text='e.g. "2" or "10 mg"')
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

    # Taper plan for a finite drug course (steroids above all). Clinician-authored
    # free text so the prescriber stays in control of the schedule; it prints
    # under the drug line and is part of the immutable hash. Blank -> no taper
    # (e.g. a short course that can stop abruptly, or a maintenance drug).
    taper_notes = models.TextField(
        blank=True,
        help_text="How to step this drug down before stopping — e.g. "
                  "'40 mg 1 wk → 20 mg 1 wk → 10 mg 1 wk → stop'. Prints under "
                  "the drug line. Required for a systemic steroid course.",
    )

    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.drug.generic_name} {self.dose} {self.frequency}".strip()

    # Units that count product units (so the regimen needs the strength too).
    COUNT_UNITS = {"tab", "cap", "ml", "drop", "puff", "sachet", "unit", "vial",
                   "amp", "patch", "application", "spoon"}

    @property
    def administered_dose(self):
        """Dose per administration as written, or "" when not separately stated."""
        dose = (self.dose or "").strip()
        if not dose or dose == (self.strength or "").strip():
            return ""
        return f"{dose} {self.dose_unit or ''}".strip()

    @property
    def regimen_dose(self):
        """The amount per administration used for reconciliation.

        Not stated -> the strength (identical to what legacy rows stored, so
        existing exposure episodes continue without a spurious split). A count
        of units -> count x strength ("2 tab x 5 mg"); an amount -> the amount.
        """
        administered = self.administered_dose
        strength = (self.strength or "").strip()
        if not administered:
            return strength or (self.dose or "").strip()
        if (self.dose_unit or "").strip().lower() in self.COUNT_UNITS and strength:
            return f"{administered} x {strength}"
        return administered

    @property
    def signature(self):
        """Regimen identity used by reconciliation to detect dose changes."""
        return (self.regimen_dose.strip().lower(), self.frequency.strip().lower(),
                self.route_value)

    @property
    def route_value(self):
        """The effective route: the line's own route, else the drug default.
        Feeds the reconciliation signature, so a PO→IV switch correctly splits
        the exposure episode."""
        return (self.route or self.drug.default_route or "PO").strip().upper()


class PrescriptionTestRequest(models.Model):
    """A catalogue investigation requested on a prescription.

    Saving a draft records the request only. Finalization (the clinician's
    acceptance) commits it as a LabOrderItem on the prescription's visit --
    linking to an outstanding order for the same test at that visit instead of
    creating a duplicate -- and stores the link here, so a retried finalize
    never orders twice and the printout lists exactly what was ordered.
    """
    prescription = models.ForeignKey(
        Prescription, on_delete=models.CASCADE, related_name="test_requests")
    test = models.ForeignKey("labs.LabTest", on_delete=models.PROTECT, related_name="+")
    order_item = models.ForeignKey(
        "labs.LabOrderItem", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="prescription_requests")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["prescription", "test__name"]
        constraints = [
            models.UniqueConstraint(fields=["prescription", "test"],
                                    name="uniq_rx_test_request"),
        ]

    def __str__(self):
        return f"{self.prescription_id}: {self.test.name}"


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
