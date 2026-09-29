"""The ISN/RPS class is stated once.

The biopsy form asked for it twice — the diagnosis dropdown carries the class
("Lupus nephritis class III") and the lupus panel has its own ISN/RPS select —
so a mis-click produced a record saying class III in one place and class IV in
another, with no way to tell which the pathologist meant.
"""
import pytest
from datetime import date

from django.utils import timezone

from pathology import lupus

pytestmark = pytest.mark.django_db


def _patient(pid="BGD-LN-1"):
    from patients.models import Patient
    return Patient.objects.create(
        patient_id=pid, name="LN", hospital_id=f"H-{pid}", phone="+1234567890",
        sex="F", cohort="GN", diabetes_status="none",
        current_phase="active", registration_status="active",
        registration_date=date.today(), enrollment_date=date.today(),
        created_at=timezone.now(), updated_at=timezone.now())


class TestParsing:
    @pytest.mark.parametrize("diagnosis,expected", [
        ("Lupus nephritis class III", "III"),
        ("Lupus nephritis class IV", "IV"),
        ("Lupus nephritis class III+V", "III+V"),
        ("Lupus nephritis class IV+V", "IV+V"),
        ("Lupus nephritis class I", "I"),
        ("Lupus nephritis", ""),          # unqualified — the panel states it
        ("IgA nephropathy", ""),          # not lupus at all
        ("", ""),
    ])
    def test_class_from_diagnosis(self, diagnosis, expected):
        assert lupus.class_from_diagnosis(diagnosis) == expected

    def test_mixed_class_is_not_truncated_to_its_first_half(self):
        # "III+V" must not parse as "III" — they are different lesions.
        assert lupus.class_from_diagnosis("Lupus nephritis class III+V") == "III+V"

    def test_diagnosis_for_class(self):
        assert lupus.diagnosis_for_class("IV+V") == "Lupus nephritis class IV+V"
        assert lupus.diagnosis_for_class("nonsense") == ""

    def test_is_lupus(self):
        assert lupus.is_lupus("Lupus nephritis class V")
        assert not lupus.is_lupus("Membranous nephropathy")

    def test_every_class_round_trips(self):
        for cls in lupus.CLASSES:
            assert lupus.class_from_diagnosis(lupus.diagnosis_for_class(cls)) == cls

    def test_all_classes_are_valid_model_choices(self):
        # Otherwise carrying the class across would write an invalid value.
        from pathology.models import LupusPathology
        valid = {c for c, _ in LupusPathology.ISNClass.choices}
        assert set(lupus.CLASSES) <= valid


class TestReconcile:
    def test_class_is_carried_from_the_diagnosis(self):
        dx, cls, err = lupus.reconcile("Lupus nephritis class III", "")
        assert (dx, cls, err) == ("Lupus nephritis class III", "III", "")

    def test_diagnosis_is_upgraded_when_only_the_panel_states_the_class(self):
        dx, cls, err = lupus.reconcile("Lupus nephritis", "IV")
        assert dx == "Lupus nephritis class IV"
        assert cls == "IV"
        assert err == ""

    def test_agreement_is_left_alone(self):
        dx, cls, err = lupus.reconcile("Lupus nephritis class V", "V")
        assert (dx, cls, err) == ("Lupus nephritis class V", "V", "")

    def test_contradiction_is_reported_not_resolved(self):
        # Only the pathologist knows which reading is right; picking one
        # silently would bury the error in the record.
        dx, cls, err = lupus.reconcile("Lupus nephritis class III", "IV")
        assert "class III" in err and "class IV" in err
        assert dx == "Lupus nephritis class III"  # nothing changed

    def test_non_lupus_diagnosis_is_untouched(self):
        assert lupus.reconcile("IgA nephropathy", "") == ("IgA nephropathy", "", "")

    def test_neither_states_a_class(self):
        assert lupus.reconcile("Lupus nephritis", "") == ("Lupus nephritis", "", "")


class TestBiopsyForm:
    """End-to-end through the view, which is where the two forms meet."""

    def _post(self, client, patient, diagnosis, panel_class, **extra):
        data = {
            "bx-biopsy_date": date.today().isoformat(),
            "bx-adequacy": "adequate",
            "dx-diagnosis": diagnosis,
            "lupus-isn_rps_class": panel_class,
        }
        data.update(extra)
        return client.post(f"/patients/{patient.pk}/biopsy/", data)

    @pytest.fixture
    def client_in(self, client, django_user_model):
        u = django_user_model.objects.create_user("path", password="x123456789")
        client.force_login(u)
        return client

    def test_contradiction_is_rejected_with_an_explanation(self, client_in):
        p = _patient("BGD-LN-10")
        response = self._post(client_in, p, "Lupus nephritis class III", "IV")
        assert response.status_code == 200  # re-rendered, not saved
        assert "must be stated once" in response.content.decode()
        assert not p.biopsies.exists()

    def test_class_is_carried_across_when_the_panel_is_left_blank(self, client_in):
        p = _patient("BGD-LN-11")
        response = self._post(client_in, p, "Lupus nephritis class IV+V", "",
                              **{"lupus-activity_index": 8})
        assert response.status_code == 302, response.content[:400]
        biopsy = p.biopsies.get()
        assert biopsy.lupus.isn_rps_class == "IV+V"
        assert biopsy.lupus.activity_index == 8

    def test_patient_level2_takes_the_class_from_the_diagnosis(self, client_in):
        # Even when the lupus panel was never opened.
        p = _patient("BGD-LN-12")
        assert self._post(client_in, p, "Lupus nephritis class III", "").status_code == 302
        p.refresh_from_db()
        assert p.isn_rps_class == "III"

    def test_agreeing_values_save(self, client_in):
        p = _patient("BGD-LN-13")
        assert self._post(client_in, p, "Lupus nephritis class V", "V").status_code == 302
        assert p.biopsies.get().lupus.isn_rps_class == "V"

    def test_non_lupus_biopsy_is_unaffected(self, client_in):
        p = _patient("BGD-LN-14")
        assert self._post(client_in, p, "IgA nephropathy", "").status_code == 302
        assert p.biopsies.exists()
