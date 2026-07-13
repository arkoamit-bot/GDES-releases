"""Automatic study-eligibility screening (Objective 4)."""
import pytest
from decimal import Decimal

pytestmark = pytest.mark.django_db


@pytest.fixture
def hcq_study():
    from studies.models import Study
    return Study.objects.create(
        code="HCQ-IGAN-ADVANCED", title="HCQ in advanced IgAN",
        study_type=Study.Type.OBSERVATIONAL, status=Study.Status.RECRUITING,
    )


def _patient(**kw):
    from patients.models import Patient
    defaults = dict(
        patient_id=kw.pop("pid", "SCR-1"), name="Screen Test",
        hospital_id="H-SCR-1", sex="M", cohort="GN",
        diabetes_status="no", registration_status="active",
    )
    defaults.update(kw)
    return Patient.objects.create(**defaults)


def test_eligible_patient_flagged(hcq_study):
    from studies.services.auto_screen import auto_screen_patient
    from studies.models import StudyEnrollment
    p = _patient(primary_diagnosis="IgA nephropathy", latest_egfr=Decimal("22.0"))
    auto_screen_patient(p)
    e = StudyEnrollment.objects.get(study=hcq_study, patient=p)
    assert e.eligible is True
    assert e.status == StudyEnrollment.Status.SCREENED


def test_ineligible_patient_not_persisted_when_never_screened(hcq_study):
    from studies.services.auto_screen import auto_screen_patient
    from studies.models import StudyEnrollment
    p = _patient(pid="SCR-2", hospital_id="H-SCR-2",
                 primary_diagnosis="Membranous", latest_egfr=Decimal("80.0"))
    auto_screen_patient(p)
    # No clutter row created for a patient who was never eligible.
    assert not StudyEnrollment.objects.filter(study=hcq_study, patient=p).exists()


def test_existing_screening_flips_to_ineligible(hcq_study):
    from studies.services.auto_screen import auto_screen_patient
    from studies.models import StudyEnrollment
    p = _patient(pid="SCR-3", hospital_id="H-SCR-3",
                 primary_diagnosis="IgA nephropathy", latest_egfr=Decimal("22.0"))
    auto_screen_patient(p)
    assert StudyEnrollment.objects.get(study=hcq_study, patient=p).eligible is True
    # eGFR recovers out of range → re-screen flips it to ineligible with reasons.
    p.latest_egfr = Decimal("55.0")
    p.save()
    auto_screen_patient(p)
    e = StudyEnrollment.objects.get(study=hcq_study, patient=p)
    assert e.eligible is False
    assert e.status == StudyEnrollment.Status.INELIGIBLE
    assert e.ineligibility_reasons


def test_clinician_enrolled_record_not_overwritten(hcq_study):
    from studies.services.auto_screen import auto_screen_patient
    from studies.models import StudyEnrollment
    p = _patient(pid="SCR-4", hospital_id="H-SCR-4",
                 primary_diagnosis="Membranous", latest_egfr=Decimal("80.0"))
    enr = StudyEnrollment.objects.create(
        study=hcq_study, patient=p, status=StudyEnrollment.Status.ENROLLED, eligible=True,
    )
    auto_screen_patient(p)  # patient is ineligible now, but is enrolled
    enr.refresh_from_db()
    assert enr.status == StudyEnrollment.Status.ENROLLED  # clinician decision preserved
