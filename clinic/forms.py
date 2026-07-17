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
from patients.models import Patient
from patients.workflow import RelapseType
from baseline.models import BaselineAssessment
from encounters.models import Admission, ClinicalEncounter
from safety.models import AdverseEvent
from treatments.models import DrugMaster
from pathology.models import (Biopsy, FSGSPathology, GNDiagnosis, IgANScore,
                              LupusPathology, MembranousPathology)
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
                  "hypertension", "autoimmune_disease", "chronic_infection",
                  "smoking_status", "hepatitis_status", "hiv_status",
"biopsy_diagnosis", "gn_broad_group", "gn_primary_secondary", "oxford_mestc", "isn_rps_class",
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
    # C. Presentation — the syndrome is a SINGLE choice (one predominant
    # syndrome); symptoms remain multi-select.
    presentation_syndromes = forms.ChoiceField(
        required=False, choices=[("", "— select —")] + list(choices.PRESENTATION_SYNDROMES),
        widget=forms.Select, label="Presenting syndrome")
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
        exclude = ["patient", "bmi", "bmi_category", "created_at", "updated_at",
                   "presentation_syndrome"]
        widgets = {
            "assessment_date": _date(),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "drug_history": forms.Textarea(attrs={"rows": 2}),
        }
        labels = {
            "family_history_kidney": "Family history of kidney disease",
            "previous_kidney_disease": "Previous kidney disease",
            "autoimmune_disease": "Autoimmune disease",
            "chronic_infection": "Chronic infection (HBV/HCV/HIV/TB)",
            "prior_immunosuppression": "Previous immunosuppressive therapy",
            "alcohol_use": "Alcohol use",
            "pulse_bpm": "Pulse (bpm)", "temperature_c": "Temperature (°C)",
            "respiratory_rate": "Respiratory rate (/min)",
            "volume_status": "Volume status", "drug_history": "Drug history",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_lab_fields(self)
        # presentation_syndromes is stored as a JSON list; the form edits a single
        # value, so seed the initial from the first stored element.
        if self.instance and self.instance.pk:
            existing = self.instance.presentation_syndromes or []
            if existing:
                self.initial["presentation_syndromes"] = existing[0]

    def clean_presentation_syndromes(self):
        # Store the single choice back as a 1-element list (model field is JSON).
        v = self.cleaned_data.get("presentation_syndromes")
        return [v] if v else []

    def serology_fields(self):
        """Paired (value, qualitative) bound fields for the E. serology block."""
        return [{"label": label, "unit": unit,
                 "value": self[f"slab_{code}"], "qual": self[f"squal_{code}"]}
                for code, label, unit, _q in BASELINE_SEROLOGY]

    def comorbidity_fields(self):
        """Bound boolean fields for the B. Medical-history checkbox grid."""
        names = ["hypertension", "cvd_history", "previous_kidney_disease",
                 "autoimmune_disease", "chronic_infection", "malignancy",
                 "prior_immunosuppression", "family_history_kidney",
                 "diabetic_retinopathy", "neuropathy", "diabetic_foot_history"]
        return [self[n] for n in names]


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


class BiopsyForm(forms.ModelForm):
    """Core biopsy + lesion descriptors. `patient` is set from the URL;
    `review_status` defaults to 'pending' (the central-review workflow takes it
    from there)."""

    class Meta:
        model = Biopsy
        exclude = ["patient", "review_status", "created_at", "updated_at"]
        widgets = {
            "biopsy_date": _date(),
            "em_findings": forms.Select(),
            "notes": forms.Textarea(attrs={"rows": 2}),
            "if_pattern": forms.Select(),
        }


class GNDiagnosisForm(forms.ModelForm):
    """The diagnosis — drives the disease-specific remission rules and analytics.
    Required for every biopsy."""
    # Common secondary causes as a dropdown (stores the readable label).
    secondary_cause = forms.ChoiceField(
        required=False, label="Secondary cause / association",
        choices=[("", "— none / not secondary —")]
                + [(lbl, lbl) for _k, lbl in choices.SECONDARY_CAUSE])

    class Meta:
        model = GNDiagnosis
        exclude = ["biopsy"]


class IgANScoreForm(forms.ModelForm):
    """Oxford MEST-C — optional, only when IgA nephropathy."""

    class Meta:
        model = IgANScore
        exclude = ["biopsy"]


class LupusPathologyForm(forms.ModelForm):
    class Meta:
        model = LupusPathology
        exclude = ["biopsy"]


class FSGSPathologyForm(forms.ModelForm):
    class Meta:
        model = FSGSPathology
        exclude = ["biopsy"]


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
