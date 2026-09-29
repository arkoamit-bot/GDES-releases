"""Exposure -> outcome output, and the duplicate exposure that would skew it.

cohort.split_patients has always supported "drug:<class>" (ever-exposed vs
never-exposed, with survival/log-rank/Cox), but the analytics page never offered
the option, so the analysis was unreachable from the app.

The same module's input could also be double-counted: "one ongoing episode per
drug" was an invariant the reconciliation engine assumes and one form checked,
but nothing in the database enforced it.
"""
import pytest
from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _patient(pid, **extra):
    from patients.models import Patient
    fields = dict(
        patient_id=pid, name="Exp", hospital_id=f"H-{pid}", phone="+1234567890",
        sex="F", cohort="GN", diabetes_status="none", primary_diagnosis="iga",
        current_phase="active", registration_status="active",
        registration_date=date.today(), enrollment_date=date.today(),
        created_at=timezone.now(), updated_at=timezone.now(),
    )
    fields.update(extra)
    return Patient.objects.create(**fields)


def _drug(name="Dapagliflozin", drug_class="sglt2i"):
    from treatments.models import DrugMaster
    drug, _ = DrugMaster.objects.get_or_create(
        generic_name=name, defaults={"drug_class": drug_class, "is_active": True})
    return drug


def _expose(patient, drug, *, ongoing=True, start=None, stop=None):
    from treatments.models import TreatmentExposure
    return TreatmentExposure.objects.create(
        patient=patient, drug=drug, drug_name=drug.generic_name,
        start_date=start or date.today() - timedelta(days=180),
        stop_date=stop, ongoing=ongoing)


class TestExposureToOutcomeIsReachable:
    def test_drug_classes_with_exposures_are_offered(self):
        from clinic.views import _drug_group_options
        p = _patient("BGD-EXP-1")
        _expose(p, _drug())
        assert "drug:sglt2i" in _drug_group_options()

    def test_classes_nobody_is_exposed_to_are_not_offered(self):
        # An option that splits the cohort into everyone vs nobody renders an
        # empty comparison and reads as a broken page.
        from clinic.views import _drug_group_options
        _drug("Finerenone", "mra")          # exists, but no exposure
        assert "drug:mra" not in _drug_group_options()

    def test_the_analytics_page_lists_the_exposure_option(self, client, django_user_model):
        u = django_user_model.objects.create_user("an", password="x123456789")
        client.force_login(u)
        p = _patient("BGD-EXP-2")
        _expose(p, _drug())
        html = client.get("/clinic/analytics/").content.decode()
        assert "drug:sglt2i" in html
        assert "ever vs never" in html

    def test_cohort_splits_exposed_from_unexposed(self):
        from analytics.services.cohort import split_patients
        from patients.models import Patient
        exposed = _patient("BGD-EXP-3")
        _patient("BGD-EXP-4")               # never exposed
        _expose(exposed, _drug())
        groups = split_patients(Patient.objects.all(), "drug:sglt2i")
        labels = {k: [p.patient_id for p in v] for k, v in groups.items()}
        assert any("BGD-EXP-3" in ids for ids in labels.values())
        assert len(groups) == 2, f"expected exposed vs unexposed, got {list(groups)}"

    def test_page_still_works_with_no_exposures_at_all(self, client, django_user_model):
        u = django_user_model.objects.create_user("an2", password="x123456789")
        client.force_login(u)
        assert client.get("/clinic/analytics/").status_code == 200


class TestNoDuplicateExposure:
    """The input side: one drug must not be counted twice."""

    def test_second_ongoing_episode_for_the_same_drug_is_rejected(self):
        p = _patient("BGD-EXP-10")
        d = _drug()
        _expose(p, d)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                _expose(p, d)

    def test_a_new_episode_is_allowed_once_the_previous_one_is_closed(self):
        # Stop/restart is a real clinical sequence and must stay possible.
        p = _patient("BGD-EXP-11")
        d = _drug()
        first = _expose(p, d)
        first.ongoing = False
        first.stop_date = date.today() - timedelta(days=30)
        first.save()
        _expose(p, d, start=date.today() - timedelta(days=29))
        from treatments.models import TreatmentExposure
        assert TreatmentExposure.objects.filter(patient=p, drug=d).count() == 2
        assert TreatmentExposure.objects.filter(patient=p, drug=d, ongoing=True).count() == 1

    def test_two_patients_on_the_same_drug_are_unaffected(self):
        d = _drug()
        _expose(_patient("BGD-EXP-12"), d)
        _expose(_patient("BGD-EXP-13"), d)   # must not collide

    def test_one_patient_on_two_drugs_is_unaffected(self):
        p = _patient("BGD-EXP-14")
        _expose(p, _drug())
        _expose(p, _drug("Ramipril", "acei"))

    def test_reconciliation_sees_the_open_episode(self):
        # The engine keys its diff by drug; this is what the constraint protects.
        from prescriptions.services.reconciliation import _open_exposures_by_drug
        p = _patient("BGD-EXP-15")
        d = _drug()
        exp = _expose(p, d)
        assert _open_exposures_by_drug(p) == {d.id: exp}

    def test_closed_episodes_are_not_treated_as_open(self):
        from prescriptions.services.reconciliation import _open_exposures_by_drug
        p = _patient("BGD-EXP-16")
        d = _drug()
        _expose(p, d, ongoing=False, stop=date.today())
        assert _open_exposures_by_drug(p) == {}


class TestIntegrityCheck:
    def test_duplicate_ongoing_check_is_registered(self):
        # Rows predating the constraint still need surfacing.
        import inspect
        from patients.management.commands import check_data_integrity
        src = inspect.getsource(check_data_integrity)
        assert "tx.duplicate_ongoing" in src

    def test_clean_data_passes(self):
        from django.core.management import call_command
        p = _patient("BGD-EXP-20")
        _expose(p, _drug())
        call_command("check_data_integrity")   # must not raise
