"""
Forms for the guided clinical workflow (register → baseline → follow-up).

These are thin ModelForms over the existing registry models — the validation,
auto-derivation (BMI, eGFR, patient_id) and downstream reconciliation all live
in the models/services, so the UI stays simple.

Labs: the baseline and follow-up forms also expose a small point-of-care lab
panel. These are NOT model fields — on save the view records them as longitudinal
LabResult rows via labs.services.results.record_result (entering creatinine also
auto-derives the CKD-EPI 2021 eGFR and refreshes the patient's cached value).
"""
from decimal import Decimal

from django import forms

from patients import choices
from patients.comorbidity import BASELINE_MIRROR_FIELDS
from patients.models import Patient
from patients.workflow import RelapseType
from baseline.models import BaselineAssessment
from encounters.models import Admission, ClinicalEncounter
from safety.models import AdverseEvent
from treatments.models import DrugMaster
from pathology.models import (Biopsy, FSGSPathology, GNDiagnosis, IgANScore,
                              LupusPathology, MembranousPathology, PathologyReport)
from studies.models import Study
from audit.models import Consent
from treatments.models import TreatmentExposure
from labs.models import LabPanel, LabTest


def _date(**kw):
    return forms.DateInput(attrs={"type": "date", **kw})


# (form field name, LabTest.code, label with unit). Order = display order.
# The quick point-of-care panel shown inline on the baseline / follow-up forms.
# Numeric tests only (qualitative ANA/ANCA live on the dedicated results page).
LAB_MAP = [
    ("lab_creatinine", "creatinine", "Serum creatinine"),
    ("lab_utp_24h",    "utp_24h",    "24-h urine total protein (g/day)"),
    ("lab_upcr",       "upcr",       "Urine protein:creatinine (g/g)"),
    ("lab_uacr",       "uacr",       "Urine albumin:creatinine (mg/g)"),
    ("lab_albumin",    "albumin",    "Serum albumin (g/dL)"),
    ("lab_hemoglobin", "hemoglobin", "Hemoglobin (g/dL)"),
    ("lab_potassium",  "potassium",  "Serum potassium (mmol/L)"),
]

# Serological markers offered on the baseline form with BOTH a quantitative value
# (titre/level) AND a qualitative read. The qualitative option set is marker-
# specific: complement (C3/C4) reads low/normal; antibodies read negative/
# positive. code, label, unit, qual-set ("posneg" | "lownormal").
SEROLOGY_QUAL = {
    "posneg": [("", "—"), ("Negative", "Negative"), ("Positive", "Positive"),
               ("Equivocal", "Equivocal")],
    "lownormal": [("", "—"), ("Low", "Low"), ("Normal", "Normal"), ("High", "High")],
}
BASELINE_SEROLOGY = [
    ("ana",        "ANA",           "titre/index", "posneg"),
    ("anti_dsdna", "Anti-dsDNA",    "IU/mL",       "posneg"),
    ("anca",       "ANCA",          "U/mL",        "posneg"),
    ("anti_pla2r", "Anti-PLA2R",    "RU/mL",       "posneg"),
    ("anti_gbm",   "Anti-GBM",      "U/mL",        "posneg"),
    ("aso",        "ASO titre",     "IU/mL",       "posneg"),
    ("c3",         "Complement C3", "mg/dL",       "lownormal"),
    ("c4",         "Complement C4", "mg/dL",       "lownormal"),
    ("gd_iga1",    "Gd-IgA1",       "U/mL",        "posneg"),
]

# Creatinine may be entered in either unit; stored canonically in mg/dL (which
# is what the CKD-EPI 2021 eGFR derivation expects). 1 mg/dL = 88.4 µmol/L.
CREATININE_UMOL_PER_MGDL = Decimal("88.4")
CREATININE_UNITS = [("mg", "mg/dL"), ("umol", "µmol/L")]


def add_lab_fields(form):
    """Attach the optional point-of-care lab fields to a form instance:
    numeric kidney/urine tests, plus serology with a value AND a qualitative read."""
    for name, _code, label in LAB_MAP:
        form.fields[name] = forms.DecimalField(
            required=False, label=label, min_value=0,
            widget=forms.NumberInput(attrs={"step": "any", "placeholder": "—"}),
        )
    # Unit toggle for creatinine so either mg/dL or µmol/L can be entered.
    form.fields["lab_creatinine_unit"] = forms.ChoiceField(
        required=False, label="Creatinine unit", choices=CREATININE_UNITS,
        initial="mg", widget=forms.Select())
    # Serology: numeric value + qualitative read per marker.
    for code, label, unit, qual in BASELINE_SEROLOGY:
        form.fields[f"slab_{code}"] = forms.DecimalField(
            required=False, label=label, min_value=0,
            widget=forms.NumberInput(attrs={"step": "any", "placeholder": unit}))
        form.fields[f"squal_{code}"] = forms.ChoiceField(
            required=False, choices=SEROLOGY_QUAL[qual], label=f"{label} (read)",
            widget=forms.Select())


def collect_labs(cleaned_data):
    """Return [(code, value_numeric, value_text), …] for filled lab fields.

    Creatinine entered in µmol/L is converted to mg/dL before storage so the
    eGFR derivation and longitudinal trend stay in one canonical unit."""
    out = []
    for name, code, _label in LAB_MAP:
        val = cleaned_data.get(name)
        if val is None:
            continue
        if code == "creatinine" and cleaned_data.get("lab_creatinine_unit") == "umol":
            val = (Decimal(str(val)) / CREATININE_UMOL_PER_MGDL).quantize(Decimal("0.01"))
        out.append((code, val, ""))
    # Serology: record a row if EITHER the value or the qualitative read is set.
    for code, _label, _unit, _qual in BASELINE_SEROLOGY:
        val = cleaned_data.get(f"slab_{code}")
        qual = (cleaned_data.get(f"squal_{code}") or "").strip()
        if val is None and not qual:
            continue
        out.append((code, val, qual))
    return out


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        # patient_id is auto-assigned (BGD-00001…); latest_egfr is set by labs.
        fields = ["name", "hospital_id", "phone", "sex", "dob",
                  "enrollment_date", "cohort", "diabetes_status",
                  "primary_diagnosis",
                  # Level 2: persistent clinical data (single source of truth).
                  # Comorbidities are asked HERE and nowhere else — the baseline
                  # form no longer repeats them.
                  "hypertension", "cvd_history", "autoimmune_disease",
                  "chronic_infection", "malignancy", "previous_kidney_disease",
                  "prior_immunosuppression", "family_history_kidney",
                  "diabetic_retinopathy", "neuropathy", "diabetic_foot_history",
                  "smoking_status", "hepatitis_status", "hiv_status",
                  # Histology — only shown once a biopsy exists (see __init__).
                  "biopsy_diagnosis", "gn_broad_group", "gn_primary_secondary",
                  "oxford_mestc", "isn_rps_class",
                  "ckd_etiology", "transplant_status"]
        widgets = {
            "dob": _date(),
            "enrollment_date": _date(),
        }
        help_texts = {
            "hospital_id": "Hospital/BIRDEM registration number (optional).",
            "primary_diagnosis": "Primary GN diagnosis (auto-set from biopsy if available).",
            "biopsy_diagnosis": "Diagnosis from biopsy report (auto-synced from pathology).",
            "gn_broad_group": "Broad disease category (auto-synced from GNDiagnosis).",
            "gn_primary_secondary": "Primary vs secondary GN (auto-synced from GNDiagnosis).",
            "oxford_mestc": "Oxford MEST-C score (auto-synced from IgAN score).",
            "isn_rps_class": "ISN/RPS class for lupus nephritis (auto-synced from pathology).",
            "ckd_etiology": "CKD aetiology (auto-derived or clinician-entered).",
        }

    # Histological fields. Before a biopsy these have no answer -- and each is
    # projected from pathology anyway (see the help texts), so asking at
    # registration invites a guess that a later biopsy report will overwrite.
    HISTOLOGY_FIELDS = ["biopsy_diagnosis", "gn_broad_group",
                        "gn_primary_secondary", "oxford_mestc", "isn_rps_class"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from patients.comorbidity import LEVEL2_COMORBIDITY_FIELDS
        # Present / absent / not recorded: an unticked box used to mean all
        # three. Existing legacy False values show as "not recorded" until
        # someone states them (Patient.condition_provenance).
        for name in LEVEL2_COMORBIDITY_FIELDS:
            if name in self.fields:
                self.fields[name].widget = TriStateSelect(
                    labels=("Not recorded", "Yes", "No"))
                instance = getattr(self, "instance", None)
                if instance is not None and instance.pk:
                    from patients.comorbidity import condition_state
                    if condition_state(instance, name) == "unknown":
                        self.initial[name] = None
        if not self._has_biopsy():
            for name in self.HISTOLOGY_FIELDS:
                self.fields.pop(name, None)
        elif self.pathology_is_projected():
            # Owned by the pathology projection: shown, not editable here.
            for name in self.HISTOLOGY_FIELDS:
                if name in self.fields:
                    self.fields[name].disabled = True
                    self.fields[name].help_text = (
                        "From the selected biopsy report (read-only). "
                        "Change it on the biopsy report.")

    def pathology_is_projected(self) -> bool:
        patient = getattr(self, "instance", None)
        if patient is None or not patient.pk:
            return False
        try:
            return patient.biopsies.exists() or bool(patient.pathology_source_biopsy_id)
        except Exception:  # pragma: no cover
            return False

    def clean(self):
        cleaned = super().clean()
        # Leaving a legacy condition at "Not recorded" keeps its raw stored
        # value (the old default False) instead of rewriting it to None.
        from patients.comorbidity import LEVEL2_COMORBIDITY_FIELDS, condition_state
        instance = self.instance
        if instance is not None and instance.pk:
            for name in LEVEL2_COMORBIDITY_FIELDS:
                if (name in cleaned and cleaned[name] is None
                        and getattr(instance, name) is False
                        and condition_state(instance, name) == "unknown"):
                    cleaned[name] = False
        return cleaned

    def save(self, commit=True):
        self.instance.provenance_source = "patient_form"
        return super().save(commit=commit)

    def _has_biopsy(self) -> bool:
        """True once this patient has a biopsy on file (or a histology value
        already recorded, so an existing entry is never hidden from editing)."""
        patient = getattr(self, "instance", None)
        if patient is None or not patient.pk:
            return False
        if any(getattr(patient, name, "") for name in self.HISTOLOGY_FIELDS):
            return True
        try:
            return patient.biopsies.exists()
        except Exception:  # pragma: no cover - relation unavailable
            return False

    def histology_visible(self) -> bool:
        """For the template: whether the histology block should be rendered."""
        return any(name in self.fields for name in self.HISTOLOGY_FIELDS)


class BaselineForm(forms.ModelForm):
    # Curated dropdowns (replace the old free-text boxes).
    occupation = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + choices.OCCUPATION)
    division_residence = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + choices.DIVISION,
        label="Division / residence")
    oedema_grade = forms.TypedChoiceField(
        required=False, coerce=int, empty_value=None, label="Oedema grade",
        choices=[("", "— select —")] + choices.OEDEMA_GRADE)
    # C. Presentation — one PRIMARY presenting syndrome plus any additional
    # presentations already recorded or clinically present. (A single select
    # used to load only the first stored value and save a one-element list,
    # silently dropping the rest.) Symptoms remain multi-select.
    presentation_syndromes = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + list(choices.PRESENTATION_SYNDROMES),
        widget=forms.Select, label="Primary presenting syndrome")
    additional_syndromes = forms.MultipleChoiceField(
        required=False, choices=choices.PRESENTATION_SYNDROMES,
        widget=forms.CheckboxSelectMultiple, label="Additional presentations")
    # HbA1c is a laboratory observation: recorded through the lab service and
    # linked to this baseline (the old baseline column is legacy only).
    hba1c = forms.DecimalField(
        required=False, min_value=0, max_value=25, decimal_places=1, label="HbA1c (%)",
        widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "%"}),
        help_text="Recorded as a dated lab result on the assessment date.")
    # One token per rendered form: a resubmission returns the results already
    # recorded instead of recording them again.
    form_token = forms.CharField(required=False, widget=forms.HiddenInput)
    # Set when the user confirms that a value identical to one on file for the
    # same date is a genuine repeat measurement.
    confirm_repeat = forms.BooleanField(
        required=False, label="These are new repeat measurements — record them anyway")
    presenting_symptoms = forms.MultipleChoiceField(
        required=False, choices=choices.PRESENTING_SYMPTOMS,
        widget=forms.CheckboxSelectMultiple, label="Presenting symptoms")
    # D. Examination findings — curated dropdowns.
    fundoscopy = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + choices.FUNDOSCOPY, label="Fundoscopy")
    skin_findings = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + choices.SKIN_FINDINGS, label="Skin findings")
    joint_findings = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + choices.JOINT_FINDINGS, label="Joint findings")

    class Meta:
        model = BaselineAssessment
        # BMI + category are auto-derived on save; patient is set from the URL;
        # presentation_syndrome (legacy single) is synced from the multi-select.
        # Comorbidities are excluded: they are Level 2 data, asked once on the
        # patient record. Re-asking them here is what let the two copies drift.
        # The columns remain (historical data, analytics) and are mirrored from
        # the patient on save.
        # drug_history is excluded for the same reason as the comorbidities:
        # medication belongs in TreatmentExposure episodes, which the
        # prescription -> reconciliation engine maintains and every exposure ->
        # outcome analysis reads. Free text typed here reaches no analysis and
        # can contradict the structured record. The column stays for the legacy
        # text, which the form shows read-only.
        exclude = ["patient", "bmi", "bmi_category", "created_at", "updated_at",
                   "presentation_syndrome", "drug_history"] + BASELINE_MIRROR_FIELDS
        widgets = {
            "assessment_date": _date(),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "drug_history": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "alcohol_use": "Alcohol use",
            "pulse_bpm": "Pulse (bpm)", "temperature_c": "Temperature (°C)",
            "respiratory_rate": "Respiratory rate (/min)",
            "volume_status": "Volume status", "drug_history": "Drug history",
        }

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        add_lab_fields(self)
        self.patient = patient
        import uuid
        if not self.is_bound:
            self.initial["form_token"] = uuid.uuid4().hex
        if "baseline_encounter" in self.fields:
            self.fields["baseline_encounter"].queryset = (
                ClinicalEncounter.objects.filter(patient=patient).order_by("-encounter_date")
                if patient is not None else ClinicalEncounter.objects.none())
            self.fields["baseline_encounter"].label = "Captured at visit"
        # presentation_syndromes is stored as a JSON list: the first element is
        # the primary presentation, the rest are additional. A legacy row with
        # only the scalar is shown through its canonical code.
        if self.instance and self.instance.pk:
            existing = list(self.instance.presentation_syndromes or [])
            if not existing and self.instance.presentation_syndrome:
                canonical = BaselineAssessment._LEGACY_TO_CANONICAL.get(
                    self.instance.presentation_syndrome)
                existing = [canonical] if canonical else []
            if existing:
                self.initial["presentation_syndromes"] = existing[0]
                self.initial["additional_syndromes"] = existing[1:]
            hv = self.baseline_hba1c()
            if hv.source == "linked":
                self.initial["hba1c"] = hv.value

    def baseline_hba1c(self):
        from labs.services.baseline import baseline_hba1c
        return baseline_hba1c(self.instance if self.instance and self.instance.pk else None)

    def recorded_results(self):
        """Results already on file around this baseline, shown with date and
        source so they are not typed in again."""
        from labs.models import LabResult
        from labs.services.baseline import (ENROLLMENT_WINDOW_AFTER,
                                            ENROLLMENT_WINDOW_BEFORE, anchor_date)
        import datetime as _dt
        if self.patient is None:
            return []
        anchor = anchor_date(self.instance if self.instance.pk else None, self.patient)
        if anchor is None:
            return []
        lo = anchor - _dt.timedelta(days=ENROLLMENT_WINDOW_BEFORE)
        hi = anchor + _dt.timedelta(days=ENROLLMENT_WINDOW_AFTER)
        return list(LabResult.objects.filter(
            patient=self.patient, result_date__range=(lo, hi))
            .exclude(source=LabResult.Source.DERIVED)
            .select_related("test").order_by("result_date", "test__name"))

    def clean_additional_syndromes(self):
        return list(self.cleaned_data.get("additional_syndromes") or [])

    def carried_comorbidities(self):
        """Comorbidities from the patient record, shown read-only on this form.

        They are displayed rather than re-asked so the clinician can see what is
        already known without a second copy that can disagree with the first.
        """
        from patients.comorbidity import comorbidity_summary
        return comorbidity_summary(self.patient, self.instance)

    def carried_medications(self):
        """Ongoing medication episodes, shown read-only on this form.

        Recorded once — by prescribing (the reconciliation engine opens the
        episode) or via Add medication for drugs started elsewhere — so the
        exposure -> outcome analyses see them.
        """
        if self.patient is None:
            return []
        return list(self.patient.exposures.filter(ongoing=True)
                    .select_related("drug").order_by("drug_name"))

    def legacy_drug_history(self):
        """Free text from a baseline recorded before medication was structured."""
        return (getattr(self.instance, "drug_history", "") or "").strip()

    def clean(self):
        cleaned = super().clean()
        # Compose the canonical list: primary first, then the additional ones
        # (never the primary twice). Clearing both is an explicit clear, which
        # also clears the legacy scalar rather than leaving it stale.
        primary = cleaned.get("presentation_syndromes")
        if isinstance(primary, list):      # already composed
            return cleaned
        additional = cleaned.get("additional_syndromes") or []
        if self.is_bound and "additional_syndromes_shown" not in self.data:
            # The submitting form never showed the additional presentations
            # (an older page, a script): keep what is stored rather than read
            # their absence as "untick all".
            additional = list((self.instance.presentation_syndromes or [])[1:]) \
                if self.instance and self.instance.pk else additional
        additional = [s for s in additional if s != primary]
        combined = ([primary] if primary else []) + additional
        cleaned["presentation_syndromes"] = combined
        if not combined:
            self.instance.presentation_syndrome = ""
        return cleaned

    def clean_presentation_syndromes(self):
        # Kept as the single primary value here; clean() builds the list.
        return self.cleaned_data.get("presentation_syndromes") or ""

    def serology_fields(self):
        """Paired (value, qualitative) bound fields for the E. serology block."""
        return [{"label": label, "unit": unit,
                 "value": self[f"slab_{code}"], "qual": self[f"squal_{code}"]}
                for code, label, unit, _q in BASELINE_SEROLOGY]

    def comorbidity_fields(self):
        """Kept for templates: the checkbox grid is gone (comorbidities are
        recorded on the patient record), so there is nothing left to bind."""
        return []


class AdverseEventForm(forms.ModelForm):
    """Guided adverse-event report. `patient` is set from the URL; `serious` is
    auto-derived on save (hospitalisation / G4 / G5). The drug and encounter
    dropdowns are scoped to active drugs and this patient's own visits."""

    class Meta:
        model = AdverseEvent
        exclude = ["patient", "serious", "created_at"]
        widgets = {
            "onset_date": _date(),
            "description": forms.TextInput(attrs={"placeholder": "Short clinical description"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "infection_type": "Only when category = Infection.",
            "suspected_drug": "Attributing a drug drives the infection-risk-by-agent analyses.",
        }

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["suspected_drug"].queryset = (
            DrugMaster.objects.filter(is_active=True).order_by("generic_name"))
        self.fields["suspected_drug"].required = False
        if patient is not None:
            self.fields["encounter"].queryset = (
                ClinicalEncounter.objects.filter(patient=patient)
                .order_by("-encounter_date"))
        self.fields["encounter"].required = False


class TriStateSelect(forms.NullBooleanSelect):
    """Not assessed / Present / Absent -- a blank lesion is not a negative."""
    def __init__(self, attrs=None, labels=("Not assessed", "Present", "Absent")):
        super().__init__(attrs)
        self.choices = [("unknown", labels[0]), ("true", labels[1]), ("false", labels[2])]


class BiopsyForm(forms.ModelForm):
    """Core biopsy + light-microscopy summary. `patient` is set from the URL;
    `review_status` defaults to 'pending' (the central-review workflow takes it
    from there). The single-choice IF/EM fields are no longer entered here:
    they are repeatable findings on the report (see PathologyFindingForm)."""

    class Meta:
        model = Biopsy
        exclude = ["patient", "review_status", "created_at", "updated_at",
                   "if_pattern", "em_findings"]
        widgets = {
            "biopsy_date": _date(),
            "notes": forms.Textarea(attrs={"rows": 2}),
            "arteriolar_hyalinosis": TriStateSelect(),
            "dkd_lesion_present": TriStateSelect(),
            "crescents_present": TriStateSelect(),
            "necrosis_present": TriStateSelect(),
        }


class GNDiagnosisForm(forms.ModelForm):
    """The diagnosis — drives the disease-specific remission rules and analytics.
    Required for a final or preliminary report; a draft, pending or inadequate
    report can be recorded without inventing one."""
    # Common secondary causes as a dropdown (stores the readable label).
    secondary_cause = forms.ChoiceField(
        required=False, label="Secondary cause / association",
        choices=[("", "— none / not secondary —")]
                + [(lbl, lbl) for _k, lbl in choices.SECONDARY_CAUSE])

    class Meta:
        model = GNDiagnosis
        exclude = ["biopsy"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["diagnosis"].required = False


class PathologyReportForm(forms.ModelForm):
    """Report provenance, specimen adequacy by modality, modality availability
    and conclusion. The primary diagnosis is the one on GNDiagnosisForm (asked
    once); coexisting diagnoses are added here."""
    additional_diagnoses = forms.MultipleChoiceField(
        required=False, choices=choices.SPECIFIC_GN_DIAGNOSIS,
        widget=forms.SelectMultiple(attrs={"size": 4}),
        label="Additional / coexisting diagnoses",
        help_text="E.g. DKD with a superimposed GN. Hold Ctrl to pick several.")

    class Meta:
        model = PathologyReport
        fields = ["status", "report_identifier", "laboratory", "pathologist",
                  "report_date", "context", "cortex_present", "medulla_present",
                  "cores", "glomeruli_if", "glomeruli_em", "globally_sclerosed",
                  "segmentally_sclerosed", "crescentic_glomeruli",
                  "lm_status", "if_status", "ihc_status", "em_status",
                  "additional_diagnoses", "limitations", "comment",
                  "original_report_text", "panel_override_reason",
                  "signed_by", "signed_at"]
        widgets = {
            "report_date": _date(), "signed_at": _date(),
            "cortex_present": TriStateSelect(labels=("Not stated", "Yes", "No")),
            "medulla_present": TriStateSelect(labels=("Not stated", "Yes", "No")),
            "limitations": forms.Textarea(attrs={"rows": 2}),
            "comment": forms.Textarea(attrs={"rows": 2}),
            "original_report_text": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Paste the original report text (optional)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Omitted status (older clients, scripts) = a final report, the model
        # default; the form shows it preselected.
        self.fields["status"].required = False

    def clean_status(self):
        return self.cleaned_data.get("status") or PathologyReport.Status.FINAL

    def report_data(self):
        data = dict(self.cleaned_data)
        data["additional_diagnoses"] = list(data.get("additional_diagnoses") or [])
        return data


def _finding_code_choices():
    from pathology import findings as vocab
    return [("", "— finding —")] + [
        (label, [(code, lbl) for code, lbl in codes])
        for _key, (label, codes) in vocab.SECTIONS.items()]


class PathologyFindingForm(forms.Form):
    """One repeatable finding row. The section is fixed by the "Add finding"
    button that created the row; the code must belong to that section."""
    section = forms.CharField(widget=forms.HiddenInput)
    code = forms.ChoiceField(required=False, choices=_finding_code_choices)
    other_label = forms.CharField(required=False, max_length=120,
                                  widget=forms.TextInput(attrs={"placeholder": "Describe"}))
    marker = forms.ChoiceField(required=False, choices=[])
    presence = forms.ChoiceField(required=False, choices=[])
    intensity = forms.ChoiceField(required=False, choices=[])
    distribution = forms.ChoiceField(required=False, choices=[])
    site = forms.ChoiceField(required=False, choices=[])
    severity = forms.ChoiceField(required=False, choices=[])
    extent = forms.ChoiceField(required=False, choices=[])
    extent_pct = forms.DecimalField(required=False, min_value=0, max_value=100,
                                    decimal_places=1, label="%",
                                    widget=forms.NumberInput(attrs={"step": "any"}))
    count = forms.IntegerField(required=False, min_value=0)
    denominator = forms.IntegerField(required=False, min_value=0, label="of")
    detail = forms.CharField(required=False, max_length=240,
                             widget=forms.TextInput(attrs={"placeholder": "Details (optional)"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from pathology import findings as vocab
        from pathology.models import PathologyFinding as F
        blank = [("", "—")]
        self.fields["marker"].choices = blank + list(vocab.IF_MARKERS)
        self.fields["presence"].choices = list(F.Presence.choices)
        self.fields["intensity"].choices = blank + list(F.Intensity.choices)
        self.fields["distribution"].choices = blank + list(F.Distribution.choices)
        self.fields["site"].choices = blank + list(F.Site.choices)
        self.fields["severity"].choices = blank + list(F.Severity.choices)
        self.fields["extent"].choices = blank + list(F.Extent.choices)

    def section_value(self):
        return (self["section"].value() or "")

    def clean_section(self):
        from pathology import findings as vocab
        value = self.cleaned_data.get("section") or ""
        if value not in vocab.SECTIONS:
            raise forms.ValidationError("Unknown section.")
        return value


FindingFormSet = forms.formset_factory(PathologyFindingForm, extra=0, can_delete=True)


def findings_from_formset(formset):
    """Cleaned finding dicts (deleted and empty rows dropped), in form order,
    plus the formset index of each so service errors can be attached back."""
    rows, index = [], []
    for i, form in enumerate(formset.forms):
        cd = getattr(form, "cleaned_data", None) or {}
        if not cd or cd.get("DELETE"):
            continue
        row = {k: v for k, v in cd.items() if k != "DELETE"}
        if not (row.get("code") or row.get("marker") or row.get("other_label")
                or row.get("detail")):
            continue
        rows.append(row)
        index.append(i)
    return rows, index


def findings_initial(report):
    """Formset initial data from an existing report revision."""
    from pathology.services.report import FINDING_FIELDS
    return [{k: getattr(f, k) for k in FINDING_FIELDS} for f in report.findings.all()]


class IgANScoreForm(forms.ModelForm):
    """Oxford MEST-C — optional, only when IgA nephropathy."""

    class Meta:
        model = IgANScore
        exclude = ["biopsy"]


class LupusPathologyForm(forms.ModelForm):
    class Meta:
        model = LupusPathology
        exclude = ["biopsy"]
        help_texts = {
            "isn_rps_class": "Leave blank if the diagnosis above already states "
                             "the class — it is carried across automatically.",
        }


class FSGSPathologyForm(forms.ModelForm):
    """Variant only. Primary/secondary is asked once, on the diagnosis; the
    panel's column is written from there (pathology.diagnosis.project_fsgs_panel)."""
    class Meta:
        model = FSGSPathology
        exclude = ["biopsy", "primary_secondary"]


class MembranousPathologyForm(forms.ModelForm):
    class Meta:
        model = MembranousPathology
        exclude = ["biopsy"]


class StudyEnrollmentForm(forms.Form):
    """Screen + enrol a patient into a study. The randomization engine
    (studies.services.randomization.enroll) does the screening, consent gate and
    seeded allocation — this form just chooses the study and the dates."""
    study = forms.ModelChoiceField(
        queryset=Study.objects.exclude(status=Study.Status.CLOSED).order_by("code"),
        empty_label="— choose a study —",
        help_text="Only studies open for enrolment are listed.")
    screened_date = forms.DateField(
        required=False, widget=_date(), help_text="Defaults to today.")
    enrolled_date = forms.DateField(
        required=False, widget=_date(),
        help_text="Set on successful enrolment; defaults to today.")


class TreatmentExposureForm(forms.ModelForm):
    """Record a medication *episode* directly — for prior/external drugs the
    patient was on before registry entry or prescribed elsewhere (the in-clinic
    regimen flows through the prescription → reconciliation engine instead).

    Honours the engine invariant — at most one ongoing episode per drug — so a
    manually-added ongoing episode reconciles cleanly with later prescriptions."""

    COMMON_FREQUENCIES = [
        ("", "— select —"),
        ("1+0+0", "1+0+0 (morning)"),
        ("0+0+1", "0+0+1 (night)"),
        ("1+0+1", "1+0+1 (morning + night)"),
        ("1+1+1", "1+1+1 (TID)"),
        ("0+1+0", "0+1+0 (noon)"),
        ("once daily", "Once daily"),
        ("twice daily", "Twice daily"),
        ("thrice daily", "Thrice daily"),
        ("weekly", "Weekly"),
        ("infusion", "Infusion"),
        ("__other__", "Other — type below"),
    ]

    frequency = forms.ChoiceField(
        choices=COMMON_FREQUENCIES,
        required=False,
        help_text="Select a common frequency, or choose 'Other' to type freely.")
    frequency_other = forms.CharField(
        max_length=40, required=False, label="Frequency (other)",
        widget=forms.TextInput(attrs={"placeholder": "e.g. every 8 hours"}))

    class Meta:
        model = TreatmentExposure
        # drug_name is snapshotted from the drug; encounter links are for the
        # reconciliation engine, not manual entry; patient comes from the URL.
        exclude = ["patient", "drug_name", "opened_by_encounter",
                   "closed_by_encounter", "created_at", "frequency"]
        widgets = {
            "start_date": _date(),
            "stop_date": _date(),
        }

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._patient = patient
        self.fields["drug"].queryset = (
            DrugMaster.objects.filter(is_active=True).order_by("generic_name"))

    def clean(self):
        cleaned = super().clean()
        ongoing = cleaned.get("ongoing")
        stop_date = cleaned.get("stop_date")
        drug = cleaned.get("drug")
        start_date = cleaned.get("start_date")

        # Resolve frequency: if "Other" chosen, use the free-text field
        freq_sel = cleaned.get("frequency", "")
        freq_other = (cleaned.get("frequency_other") or "").strip()
        if freq_sel == "__other__":
            cleaned["frequency"] = freq_other
        elif freq_sel:
            cleaned["frequency"] = freq_sel
        else:
            cleaned["frequency"] = ""

        if ongoing and stop_date:
            self.add_error("stop_date", "An ongoing medication can't have a stop date.")
        if not ongoing and not stop_date:
            self.add_error("stop_date", "Set a stop date, or mark the medication ongoing.")
        if start_date and stop_date and stop_date < start_date:
            self.add_error("stop_date", "Stop date can't be before the start date.")

        # Enforce the one-ongoing-episode-per-drug invariant.
        if ongoing and drug and self._patient is not None:
            exists = TreatmentExposure.objects.filter(
                patient=self._patient, drug=drug, ongoing=True)
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                self.add_error(
                    "drug", "There is already an ongoing episode for this drug. "
                    "Close it first, or record this one with a stop date.")
        return cleaned


class ConsentForm(forms.Form):
    """Record (grant) a versioned consent. Granting supersedes any current
    consent of the same type — handled by audit.services.consent.grant_consent."""
    consent_type = forms.ChoiceField(choices=Consent.Type.choices)
    ICF_VERSIONS = [
        ("BGDDR-ICF-v1.0", "BGDDR-ICF-v1.0"),
        ("BGDDR-ICF-v2.0", "BGDDR-ICF-v2.0"),
        ("BGDDR-ICF-v2.1", "BGDDR-ICF-v2.1"),
        ("BGDDR-ICF-v3.0", "BGDDR-ICF-v3.0"),
        ("BGDDR-Trial-ICF-v1.0", "BGDDR-Trial-ICF-v1.0"),
    ]
    form_version = forms.ChoiceField(
        choices=ICF_VERSIONS,
        label="ICF version",
        help_text="Select the informed consent form version used.")
    consent_date = forms.DateField(
        required=False, widget=_date(), help_text="Defaults to today.")
    scope = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2}),
        help_text="What the patient agreed to (optional).")
    notes = forms.CharField(max_length=240, required=False)


class FollowupForm(forms.ModelForm):
    class Meta:
        model = ClinicalEncounter
        # patient is set from the URL; created_at is automatic.
        fields = ["encounter_date", "encounter_type", "seen_by",
                  "clinic_location", "systolic_bp", "diastolic_bp",
                  "weight_kg", "edema_grade", "symptoms",
                  "clinician_response", "disease_phase", "treatment_adjusted",
                  "advice", "next_due_date"]
        widgets = {
            "encounter_date": _date(),
            "next_due_date": _date(),
            "symptoms": forms.TextInput(
                attrs={"placeholder": "Frothy urine, breathlessness, haematuria…"}),
            "advice": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "next_due_date": "Drives the follow-up worklist on the dashboard.",
            "advice": "Prints on the prescription (Bangla supported).",
            "clinician_response": "Your response assessment at this visit "
                                  "(the lab-based remission is computed separately).",
            "disease_phase": "Leave blank to let the workflow set it from the "
                             "response; choose a value to override.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # No inline lab panel here — follow-up results are entered on the
        # dedicated "Enter results" page (clinic:lab_results).
        self.fields["edema_grade"] = forms.TypedChoiceField(
            required=False, coerce=int, empty_value=None, label="Oedema grade",
            choices=[("", "—")] + [(i, f"{i} — {lbl}") for i, lbl in enumerate(
                ["none", "trace / ankle", "mild (below knee)",
                 "moderate (generalised)", "severe (anasarca)"])])
        self.fields["clinician_response"].required = False
        self.fields["disease_phase"].required = False


class RelapseForm(forms.Form):
    """Document a relapse (workflow step 5E). Handled by
    encounters.services.workflow.record_relapse (creates the episode + a
    ClinicalEvent + flips the phase to Relapse)."""
    relapse_date = forms.DateField(widget=_date(), help_text="Date relapse identified.")
    relapse_type = forms.ChoiceField(choices=RelapseType.choices)
    criteria = forms.CharField(
        max_length=240, required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. UPCR 0.4→3.2 g/g; albumin 2.6"}),
        help_text="Criteria met / how the relapse was defined.")
    action_taken = forms.CharField(
        max_length=240, required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. restart prednisolone 1 mg/kg"}))


class AdmissionForm(forms.ModelForm):
    """Inpatient work-up episode (workflow step 2). The biopsy dropdown is scoped
    to this patient's biopsies."""
    class Meta:
        model = Admission
        exclude = ["patient", "created_at"]
        widgets = {
            "admit_date": _date(),
            "discharge_date": _date(),
            "reason": forms.TextInput(attrs={"placeholder": "Reason for admission / work-up"}),
            "discharge_advice": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        if patient is not None:
            from pathology.models import Biopsy
            self.fields["biopsy"].queryset = (
                Biopsy.objects.filter(patient=patient).order_by("-biopsy_date"))
        self.fields["biopsy"].required = False


class RegisterForm(forms.Form):
    """Register a suspected patient into structured GN follow-up (step 4)."""
    registration_date = forms.DateField(
        required=False, widget=_date(), help_text="Defaults to today.")


# Clinical grouping + display order for the standalone results-entry page.
LAB_RESULT_GROUPS = [
    ("Kidney function & urine",
     ["creatinine", "utp_24h", "upcr", "uacr", "albumin", "potassium", "hemoglobin"]),
    ("Immunology / serology",
     ["ana", "anca", "anti_dsdna", "anti_pla2r", "anti_gbm", "aso", "c3", "c4", "gd_iga1"]),
    ("Infection screen (TB & viral)",
     ["hbsag", "anti_hbc_total", "anti_hcv", "hiv", "igra", "mantoux"]),
    ("Metabolic", ["hba1c"]),
]

# Infection-screen markers are read qualitatively only (Negative/Positive/
# Equivocal) — no numeric value.
INFECTION_MARKERS = {"hbsag", "anti_hbc_total", "anti_hcv", "hiv", "igra", "mantoux"}

# Standard dropdown for qualitative results — covers both pos/neg serology and
# low/normal/high graded reads, per the clinic's request.
QUALITATIVE_CHOICES = [
    ("", "—"),
    ("Positive", "Positive"), ("Negative", "Negative"), ("Equivocal", "Equivocal"),
    ("Low", "Low"), ("Normal", "Normal"), ("High", "High"),
]


class LabResultsForm(forms.Form):
    """Enter result VALUES for a patient on a given date — independent of a
    visit. This is where diagnostic serology (available before biopsy) and any
    results a patient brings to a follow-up get recorded. Numeric tests take a
    number; qualitative tests (ANA/ANCA) take free text (pos/neg/titre).
    Entering creatinine auto-derives the CKD-EPI 2021 eGFR."""
    result_date = forms.DateField(
        widget=_date(), help_text="Date the sample was taken / resulted.")

    # Creatinine may be entered in mg/dL or µmol/L (converted to mg/dL on save).
    creatinine_unit = forms.ChoiceField(
        required=False, choices=CREATININE_UNITS, initial="mg", widget=forms.Select())
    # One token per rendered form: a resubmission (double click, browser
    # retry) returns the results already recorded instead of adding them again.
    form_token = forms.CharField(required=False, widget=forms.HiddenInput)
    confirm_repeat = forms.BooleanField(
        required=False, label="These are new repeat measurements — record them anyway")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        import uuid
        if not self.is_bound:
            self.initial["form_token"] = uuid.uuid4().hex
        from labs.models import LabTest
        tests = {t.code: t for t in
                 LabTest.objects.filter(is_active=True, is_derived=False)}
        # Ordered groups + any catalogue test not explicitly grouped -> "Other".
        grouped_codes = {c for _, codes in LAB_RESULT_GROUPS for c in codes}
        layout = list(LAB_RESULT_GROUPS)
        extra = sorted(c for c in tests if c not in grouped_codes)
        if extra:
            layout.append(("Other", extra))

        # Serology markers take BOTH a value and a qualitative read (like the
        # baseline form): complement C3/C4 read Low/Normal, antibodies Neg/Pos.
        sero = {code: (label, unit, q) for code, label, unit, q in BASELINE_SEROLOGY}

        self._meta_groups = []
        for title, codes in layout:
            fields = []
            for code in codes:
                t = tests.get(code)
                if not t:
                    continue
                name = f"t_{code}"
                if code in sero:
                    _lbl, _unit, qkind = sero[code]
                    self.fields[name] = forms.DecimalField(
                        required=False, label=t.name, min_value=0,
                        widget=forms.NumberInput(
                            attrs={"step": "any", "placeholder": t.default_unit or _unit}))
                    qname = f"q_{code}"
                    self.fields[qname] = forms.ChoiceField(
                        required=False, choices=SEROLOGY_QUAL[qkind], widget=forms.Select())
                    fields.append({"name": name, "code": code, "unit": t.default_unit,
                                   "qualitative": False, "qual_name": qname})
                elif code in INFECTION_MARKERS:
                    # Infection screen: Negative/Positive/Equivocal only.
                    self.fields[name] = forms.ChoiceField(
                        required=False, label=t.name,
                        choices=SEROLOGY_QUAL["posneg"], widget=forms.Select())
                    fields.append({"name": name, "code": code, "unit": t.default_unit,
                                   "qualitative": True, "qual_name": None})
                elif t.value_type == LabTest.ValueType.QUALITATIVE:
                    self.fields[name] = forms.ChoiceField(
                        required=False, label=t.name, choices=QUALITATIVE_CHOICES,
                        widget=forms.Select())
                    fields.append({"name": name, "code": code, "unit": t.default_unit,
                                   "qualitative": True, "qual_name": None})
                else:
                    self.fields[name] = forms.DecimalField(
                        required=False, label=t.name, min_value=0,
                        widget=forms.NumberInput(
                            attrs={"step": "any", "placeholder": t.default_unit or "—"}))
                    fields.append({"name": name, "code": code, "unit": t.default_unit,
                                   "qualitative": False, "qual_name": None})
            if fields:
                self._meta_groups.append({"title": title, "fields": fields})

    def grouped(self):
        """Bound fields grouped for the template. The creatinine row carries a
        unit toggle (mg/dL ↔ µmol/L) beside its value input."""
        return [{"title": g["title"],
                 "fields": [{"bf": self[f["name"]], "unit": f["unit"],
                             "unit_toggle": self["creatinine_unit"] if f["code"] == "creatinine" else None,
                             "qual": self[f["qual_name"]] if f.get("qual_name") else None}
                            for f in g["fields"]]}
                for g in self._meta_groups]

    def collect(self):
        """Return [(code, value_numeric, value_text), …] for the filled fields.
        Serology rows carry a value and/or a qualitative read; creatinine in
        µmol/L is converted to mg/dL (the canonical eGFR unit)."""
        out = []
        for g in self._meta_groups:
            for f in g["fields"]:
                val = self.cleaned_data.get(f["name"])
                if f["qualitative"]:
                    if val not in (None, ""):
                        out.append((f["code"], None, str(val).strip()))
                    continue
                text = ""
                if f.get("qual_name"):
                    text = (self.cleaned_data.get(f["qual_name"]) or "").strip()
                if val in (None, "") and not text:
                    continue
                if (val not in (None, "") and f["code"] == "creatinine"
                        and self.cleaned_data.get("creatinine_unit") == "umol"):
                    val = (Decimal(str(val)) / CREATININE_UMOL_PER_MGDL).quantize(Decimal("0.01"))
                out.append((f["code"], val if val not in (None, "") else None, text))
        return out


class LabOrderForm(forms.Form):
    """Order labs at a visit — choose a panel or custom tests."""
    panel = forms.ModelChoiceField(
        queryset=LabPanel.objects.all(), required=False,
        empty_label="— choose a panel —",
        help_text="Select a panel to order its standard tests, or choose individual tests below.")
    custom_tests = forms.ModelMultipleChoiceField(
        queryset=LabTest.objects.filter(is_active=True, is_derived=False).order_by("name"),
        required=False, widget=forms.CheckboxSelectMultiple,
        help_text="Optional: add individual tests not in the chosen panel.")
    notes = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 2}),
        help_text="e.g. 'urgent — result by phone'")

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._patient = patient

    def clean(self):
        cleaned = super().clean()
        panel = cleaned.get("panel")
        tests = cleaned.get("custom_tests")
        if not panel and not tests:
            self.add_error("panel", "Choose a panel or at least one individual test.")
        return cleaned
