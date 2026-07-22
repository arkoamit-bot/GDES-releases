# clinic/forms.py Coupling Analysis

## Current State

`clinic/forms.py` (671 LOC, 18 forms) imports from 8 different apps:

| App | Imports | Forms Using |
|-----|---------|-------------|
| **patients** | choices, models.Patient, workflow.RelapseType | PatientForm, RegisterForm |
| **baseline** | models.BaselineAssessment | BaselineForm |
| **encounters** | models.Admission, models.ClinicalEncounter | AdmissionForm |
| **safety** | models.AdverseEvent | AdverseEventForm |
| **treatments** | models.DrugMaster, models.TreatmentExposure | TreatmentExposureForm |
| **pathology** | models.Biopsy, FSGSPathology, GNDiagnosis, IgANScore, etc. | BiopsyForm, GNDiagnosisForm, IgANScoreForm, etc. |
| **studies** | models.Study | StudyEnrollmentForm |
| **audit** | models.Consent | ConsentForm |
| **labs** | models.LabPanel, models.LabTest | LabResultsForm, LabOrderForm |

## Analysis

### Is this coupling justified?
**YES — mostly.** This is a clinical forms module that serves as the **unified data entry interface** for the entire clinical workflow. Each form wraps specific domain models because:

1. **Clinical workflow requires it:** A patient encounter involves baseline data, labs, pathology, treatment, and safety monitoring — all in one session
2. **Django ModelForm pattern:** Forms are tightly coupled to their models by design
3. **No abstraction layer needed:** The forms ARE the interface between users and domain models

### When would this be a problem?
- If forms started containing business logic (they don't — they're pure data entry)
- If the same form was imported by many apps (it's only used by clinic views)
- If the forms grew beyond what a single module can manage (671 LOC is manageable)

## Recommendation

**No refactoring needed.** The current coupling is **appropriate for a clinical forms module** that serves as the unified data entry interface.

### Optional improvements (low priority):
1. Split into domain-specific form modules:
   - `clinic/forms/patient.py`
   - `clinic/forms/encounter.py`
   - `clinic/forms/pathology.py`
   - `clinic/forms/labs.py`
   - `clinic/forms/treatment.py`
2. Keep `clinic/forms/__init__.py` re-exporting all forms for backward compatibility

### Risk Assessment
- **Risk Level:** LOW (current state is acceptable)
- **Impact:** Minimal — forms work correctly
- **Recommendation:** Defer unless forms grow beyond 1,000 LOC
