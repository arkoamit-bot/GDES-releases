"""Conditions, laboratory results, visit measurements and presentations:
one owner each, linked everywhere else.

Corrected-behaviour regressions for the 2026-09-27 entry-linkage review.
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.management import call_command
from django.urls import reverse

pytestmark = pytest.mark.django_db
DAY = date(2026, 9, 1)


@pytest.fixture(autouse=True)
def quiet_events(monkeypatch):
    monkeypatch.setattr("events.signal_handlers.dispatch", lambda *a, **k: None)
    monkeypatch.setattr("events.dispatcher.dispatch", lambda *a, **k: None)


@pytest.fixture
def labs():
    call_command("seed_labs", verbosity=0)


@pytest.fixture
def patient():
    from patients.models import Patient
    return Patient.objects.create(patient_id="LINK-1", name="Link Synthetic", sex="M",
                                  dob=date(1966, 1, 1), enrollment_date=DAY)


@pytest.fixture
def signed_in(client, django_user_model):
    client.force_login(django_user_model.objects.create_user("link_user"))
    return client


# --- Comorbidities: current state vs enrollment snapshot -----------------------

class TestConditions:
    def test_correction_does_not_return_from_baseline(self, patient):
        from baseline.models import BaselineAssessment
        from patients.comorbidity import comorbidity_summary
        patient.hypertension = True
        patient.save()
        baseline = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY)
        patient.hypertension = False
        patient.provenance_reason = "Misread BP; not hypertensive"
        patient.save()
        baseline.save()
        baseline.refresh_from_db()
        assert baseline.hypertension is True          # enrollment snapshot kept
        assert "Hypertension" not in comorbidity_summary(patient, baseline)
        prov = patient.condition_provenance["hypertension"]
        assert prov["value"] is False and prov["previous"] is True
        assert prov["reason"] == "Misread BP; not hypertensive"

    def test_new_current_condition_does_not_rewrite_enrollment(self, patient):
        from baseline.models import BaselineAssessment
        baseline = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY)
        patient.malignancy = True
        patient.save()
        baseline.notes = "Unrelated correction"
        baseline.save()
        baseline.refresh_from_db()
        assert baseline.malignancy is False
        assert baseline.comorbidity_snapshot_source == "enrollment"

    def test_snapshot_correction_is_separate_and_audited(self, patient, django_user_model):
        from audit.models import AuditLog
        from baseline.models import BaselineAssessment
        from patients.comorbidity import correct_baseline_snapshot
        baseline = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY)
        with pytest.raises(ValueError):
            correct_baseline_snapshot(baseline, {"malignancy": True}, reason="")
        user = django_user_model.objects.create_user("corrector")
        correct_baseline_snapshot(baseline, {"malignancy": True},
                                  reason="Enrollment note documents prior lymphoma", user=user)
        baseline.refresh_from_db()
        assert baseline.malignancy is True and baseline.comorbidity_snapshot_source == "correction"
        row = AuditLog.objects.get(model_label="baseline.BaselineAssessment",
                                   field_name="malignancy")
        assert row.changed_by == user and "lymphoma" in row.change_reason

    def test_legacy_false_is_not_a_verified_negative(self, patient):
        from patients.comorbidity import condition_state
        from patients.models import Patient
        Patient.objects.filter(pk=patient.pk).update(hypertension=False,
                                                     condition_provenance={})
        patient.refresh_from_db()
        assert condition_state(patient, "hypertension") == "unknown"
        patient.hypertension = False
        patient.provenance_source = "patient_form"
        patient.save()
        patient.refresh_from_db()
        assert condition_state(patient, "hypertension") == "unknown"   # unchanged value, no stamp
        patient.hypertension = True
        patient.save()
        patient.hypertension = False
        patient.save()
        assert condition_state(patient, "hypertension") == "absent"

    def test_legacy_baseline_only_condition_is_flagged(self, patient):
        from baseline.models import BaselineAssessment
        from patients.comorbidity import comorbidity_items
        b = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY)
        BaselineAssessment.objects.filter(pk=b.pk).update(
            hypertension=True, comorbidity_snapshot_source="legacy_mirror")
        b.refresh_from_db()
        items = comorbidity_items(patient, b)
        assert items == [{"label": "Hypertension", "source": "legacy_baseline",
                          "field": "hypertension"}]
        patient.hypertension = False
        patient.save()      # reconciled on the patient record: fallback stops
        assert comorbidity_items(patient, b) == []

    def test_patient_form_tristate_keeps_legacy_raw_value(self, patient):
        from clinic.forms import PatientForm
        from patients.models import Patient
        Patient.objects.filter(pk=patient.pk).update(malignancy=False, condition_provenance={})
        patient.refresh_from_db()
        data = {"name": patient.name, "sex": "M", "diabetes_status": "none",
                "malignancy": "unknown", "hypertension": "true"}
        form = PatientForm(data, instance=patient)
        assert form.is_valid(), form.errors
        form.save()
        patient.refresh_from_db()
        assert patient.malignancy is False                 # raw legacy value kept
        assert "malignancy" not in patient.condition_provenance
        assert patient.condition_provenance["hypertension"]["source"] == "patient_form"

    def test_dm_duration_does_not_invent_type_2(self, patient):
        from baseline.models import BaselineAssessment
        BaselineAssessment.objects.create(patient=patient, dm_duration_years=Decimal("5"))
        patient.refresh_from_db()
        assert patient.diabetes_status == "unknown"


# --- Laboratory results ---------------------------------------------------------

class TestLabs:
    def test_api_creatinine_derives_egfr_and_refreshes_cache(self, patient, labs):
        from api.serializers import LabResultSerializer
        from labs.models import LabTest
        creat = LabTest.objects.get(code="creatinine")
        ser = LabResultSerializer(data={"patient": patient.pk, "test": creat.pk,
                                        "result_date": DAY, "value_numeric": "1.2",
                                        "unit": "mg/dL"})
        assert ser.is_valid(), ser.errors
        result = ser.save()
        patient.refresh_from_db()
        egfr = patient.lab_results.get(test__code="egfr")
        assert egfr.derived_from_id == result.pk
        assert egfr.formula_version == "CKD-EPI-2021-creatinine"
        assert patient.latest_egfr == egfr.value_numeric
        assert result.entry_path == "api"

    def test_api_umol_creatinine_is_normalised(self, patient, labs):
        from api.serializers import LabResultSerializer
        from labs.models import LabTest
        ser = LabResultSerializer(data={"patient": patient.pk,
                                        "test": LabTest.objects.get(code="creatinine").pk,
                                        "result_date": DAY, "value_numeric": "106.08",
                                        "unit": "µmol/L"})
        assert ser.is_valid(), ser.errors
        r = ser.save()
        assert r.value_numeric == Decimal("1.20") and r.unit == "mg/dL"

    def test_api_update_supersedes_with_lineage(self, patient, labs):
        from api.serializers import LabResultSerializer
        from labs.models import LabResult
        from labs.services.results import lineage, record_result
        original = record_result(patient, "creatinine", result_date=DAY, value_numeric="1.2")
        bad = LabResultSerializer(original, data={"value_numeric": "2.4"}, partial=True)
        assert bad.is_valid() and pytest.raises(Exception, bad.save)
        ser = LabResultSerializer(original, data={"value_numeric": "2.4",
                                                  "correction_reason": "Transcription error"},
                                  partial=True)
        assert ser.is_valid(), ser.errors
        corrected = ser.save()
        assert corrected.pk != original.pk and corrected.supersedes_id == original.pk
        assert [r.pk for r in lineage(corrected)] == [original.pk, corrected.pk]
        original.refresh_from_db()
        assert original.is_current is False and original.value_numeric == Decimal("1.2")
        old_egfr = LabResult.all_objects.get(derived_from=original)
        assert old_egfr.is_current is False
        current = patient.lab_results.filter(test__code="egfr")
        assert current.count() == 1 and current.get().derived_from_id == corrected.pk
        patient.refresh_from_db()
        assert patient.latest_egfr == current.get().value_numeric

    def test_api_cannot_delete_a_result(self, patient, labs, client, django_user_model):
        from labs.services.results import record_result
        r = record_result(patient, "albumin", result_date=DAY, value_numeric="3.2")
        client.force_login(django_user_model.objects.create_superuser("labadmin", password="x"))
        assert client.delete(f"/api/v1/lab-results/{r.pk}/").status_code == 405

    def test_admin_add_derives_egfr(self, patient, labs, client, django_user_model):
        from labs.models import LabTest
        client.force_login(django_user_model.objects.create_superuser("labadmin2", password="x"))
        resp = client.post("/admin/labs/labresult/add/", {
            "patient": patient.pk, "test": LabTest.objects.get(code="creatinine").pk,
            "value_numeric": "1.4", "unit": "mg/dL", "result_date": DAY.isoformat(),
            "source": "lab", "value_text": "", "correction_reason": ""})
        assert resp.status_code == 302, resp.content[:500]
        assert patient.lab_results.filter(test__code="egfr").count() == 1

    def test_fhir_import_uses_catalogue_and_is_idempotent(self, patient, labs):
        from fhir.import_fhir import import_lab_from_fhir
        obs = {"resourceType": "Observation", "id": "obs-77",
               "subject": {"reference": f"Patient/{patient.pk}"},
               "code": {"coding": [{"system": "http://loinc.org", "code": "2160-0",
                                    "display": "Creatinine"}]},
               "valueQuantity": {"value": 1.1, "unit": "mg/dL"},
               "effectiveDateTime": "2026-09-01", "issued": "2026-09-02"}
        first = import_lab_from_fhir(obs)
        second = import_lab_from_fhir(obs)
        assert first["id"] == second["id"]
        assert patient.lab_results.filter(test__code="creatinine").count() == 1
        assert patient.lab_results.filter(test__code="egfr").count() == 1

    def test_retry_is_idempotent_but_genuine_repeat_is_recorded(self, patient, labs, signed_in):
        url = reverse("clinic:lab_results", args=[patient.pk])
        payload = {"result_date": DAY.isoformat(), "t_albumin": "3.2", "form_token": "tok-1"}
        assert signed_in.post(url, payload).status_code == 302
        assert signed_in.post(url, payload).status_code == 302     # retried submission
        assert patient.lab_results.filter(test__code="albumin").count() == 1
        # A fresh form with the same value: not silently duplicated...
        again = dict(payload, form_token="tok-2")
        resp = signed_in.post(url, again)
        assert resp.status_code == 200
        assert "not</b> recorded" in resp.content.decode()
        assert patient.lab_results.filter(test__code="albumin").count() == 1
        # ...until the user confirms a genuine same-day repeat measurement.
        assert signed_in.post(url, dict(again, confirm_repeat="on")).status_code == 302
        assert patient.lab_results.filter(test__code="albumin", result_date=DAY).count() == 2

    def test_partial_failure_is_reported_per_field(self, patient, labs, monkeypatch):
        from labs.services import results as svc
        real = svc.record_result

        def flaky(p, code, **kw):
            if code == "potassium":
                raise svc.ValidationError("instrument flag")
            return real(p, code, **kw)
        monkeypatch.setattr(svc, "record_result", flaky)
        out = svc.record_panel(patient, [("albumin", "3.1", ""), ("potassium", "4.1", "")],
                               result_date=DAY)
        assert [r.test.code for r in out.saved] == ["albumin"]
        assert "potassium" in out.failed and out.partial

    def test_result_links_to_unambiguous_outstanding_order(self, patient, labs):
        from encounters.models import ClinicalEncounter
        from labs.services.ordering import order_tests
        from labs.services.results import record_panel
        enc = ClinicalEncounter.objects.create(patient=patient, encounter_date=DAY)
        order = order_tests(enc, ["albumin"])
        out = record_panel(patient, [("albumin", "3.0", "")], result_date=DAY + timedelta(days=3))
        assert out.saved[0].order_item.order_id == order.pk
        order.refresh_from_db()
        assert order.status == "resulted"


class TestBaselineHbA1c:
    def test_baseline_hba1c_is_a_lab_result_and_export_reads_it(self, patient, labs, signed_in):
        from baseline.models import BaselineAssessment
        from exports.services.dataset import build_row
        from labs.services.results import record_result
        resp = signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
            "assessment_date": DAY.isoformat(), "hba1c": "8.2", "form_token": "b-1"})
        assert resp.status_code == 302
        hb = patient.lab_results.get(test__code="hba1c")
        assert hb.value_numeric == Decimal("8.2") and hb.entry_path == "baseline"
        baseline = BaselineAssessment.objects.get(patient=patient)
        assert baseline.hba1c_result_id == hb.pk and baseline.hba1c is None
        # A second, different same-date report stays distinguishable.
        other = record_result(patient, "hba1c", result_date=DAY, value_numeric="7.1",
                              source_report_id="LAB-2")
        assert patient.lab_results.filter(test__code="hba1c", result_date=DAY).count() == 2
        row = build_row(patient)
        assert row["hba1c"] == Decimal("8.2")
        assert row["hba1c_date"] == DAY and row["hba1c_source"] == "linked"
        assert other.pk != hb.pk

    def test_window_selection_and_legacy_fallback(self, patient, labs):
        from baseline.models import BaselineAssessment
        from labs.services.baseline import baseline_hba1c
        from labs.services.results import record_result
        b = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY)
        BaselineAssessment.objects.filter(pk=b.pk).update(hba1c=Decimal("9.0"))
        b.refresh_from_db()
        assert baseline_hba1c(b).source == "legacy_field"
        # Outside the window: never used as the enrollment value.
        record_result(patient, "hba1c", result_date=DAY + timedelta(days=200), value_numeric="6.0")
        assert baseline_hba1c(b).source == "legacy_field"
        record_result(patient, "hba1c", result_date=DAY - timedelta(days=20), value_numeric="8.8")
        hv = baseline_hba1c(b)
        assert hv.source == "window" and hv.value == Decimal("8.8")


class TestBaselineLabsNotDuplicated:
    def test_resaving_baseline_does_not_record_labs_twice(self, patient, labs, signed_in):
        url = reverse("clinic:baseline", args=[patient.pk])
        data = {"assessment_date": DAY.isoformat(), "lab_albumin": "3.3", "form_token": "x-1"}
        assert signed_in.post(url, data).status_code == 302
        # The edit form is re-opened and saved with the old value still typed.
        assert signed_in.post(url, dict(data, form_token="x-2", notes="edit")).status_code == 302
        assert patient.lab_results.filter(test__code="albumin").count() == 1
        page = signed_in.get(url).content.decode()
        assert "Already on file around enrollment" in page


# --- Presenting syndromes -----------------------------------------------------

class TestSyndromes:
    def test_unrelated_edit_keeps_additional_presentations(self, patient, signed_in):
        from baseline.models import BaselineAssessment
        from clinic.forms import BaselineForm
        b = BaselineAssessment.objects.create(patient=patient,
                                              presentation_syndromes=["nephrotic", "aki"])
        form = BaselineForm(instance=b, patient=patient)
        assert form.initial["presentation_syndromes"] == "nephrotic"
        assert form.initial["additional_syndromes"] == ["aki"]
        # Rendered form posts both (checkboxes ticked) ...
        resp = signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
            "presentation_syndromes": "nephrotic", "additional_syndromes": ["aki"],
            "additional_syndromes_shown": "1", "notes": "Unrelated correction"})
        assert resp.status_code == 302
        b.refresh_from_db()
        assert b.presentation_syndromes == ["nephrotic", "aki"]
        # ... and an older page that never showed them does not drop them.
        signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
            "presentation_syndromes": "nephrotic", "notes": "Another edit"})
        b.refresh_from_db()
        assert b.presentation_syndromes == ["nephrotic", "aki"]

    def test_new_primary_keeps_the_rest(self, patient, signed_in):
        from baseline.models import BaselineAssessment
        b = BaselineAssessment.objects.create(patient=patient,
                                              presentation_syndromes=["nephrotic", "aki"])
        signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
            "presentation_syndromes": "rpgn", "additional_syndromes": ["aki", "nephrotic"],
            "additional_syndromes_shown": "1"})
        b.refresh_from_db()
        assert b.presentation_syndromes == ["rpgn", "aki", "nephrotic"]
        assert b.presentation_syndrome == "rpgn"

    def test_explicit_clear_clears_legacy_scalar(self, patient, signed_in):
        from baseline.models import BaselineAssessment
        b = BaselineAssessment.objects.create(patient=patient, presentation_syndromes=["nephrotic"])
        assert b.presentation_syndrome == "nephrotic"
        signed_in.post(reverse("clinic:baseline", args=[patient.pk]), {
            "presentation_syndromes": "", "additional_syndromes_shown": "1"})
        b.refresh_from_db()
        assert b.presentation_syndromes == [] and b.presentation_syndrome == ""

    def test_legacy_scalar_only_row_is_lifted_not_lost(self, patient):
        from baseline.models import BaselineAssessment
        b = BaselineAssessment.objects.create(patient=patient)
        BaselineAssessment.objects.filter(pk=b.pk).update(presentation_syndrome="hematuria")
        b.refresh_from_db()
        b.notes = "touch"
        b.save()
        b.refresh_from_db()
        assert b.presentation_syndromes == ["isolated_hematuria"]
        assert b.presentation_syndrome == "hematuria"


# --- Visit measurements ---------------------------------------------------------

class TestVitals:
    def test_vitalsign_is_the_visit_measurement(self, patient):
        from clinical.models import VitalSign
        from encounters.models import ClinicalEncounter
        from knowledge.services import extract_patient_features
        enc = ClinicalEncounter.objects.create(patient=patient, encounter_date=DAY)
        first = VitalSign.objects.create(encounter=enc, bp_systolic=180, bp_diastolic=100)
        enc.refresh_from_db()
        assert enc.selected_vital_id == first.pk and enc.systolic_bp == 180
        assert "hypertension" in extract_patient_features(patient)["features"]
        # A second reading is kept but does not silently replace the selected one.
        second = VitalSign.objects.create(encounter=enc, bp_systolic=150, bp_diastolic=90)
        enc.refresh_from_db()
        assert enc.systolic_bp == 180 and enc.vitals.count() == 2
        from encounters.services.vitals import select
        select(enc, second, reason="Repeat reading after rest")
        enc.refresh_from_db()
        assert enc.systolic_bp == 150

    def test_followup_form_records_a_reading(self, patient, signed_in):
        resp = signed_in.post(reverse("clinic:followup", args=[patient.pk]), {
            "encounter_date": DAY.isoformat(), "encounter_type": "followup",
            "systolic_bp": "142", "diastolic_bp": "88", "weight_kg": "70.5"})
        assert resp.status_code == 302, resp.content[:500]
        enc = patient.encounters.get()
        assert enc.vitals.count() == 1
        assert enc.selected_vital.bp_systolic == 142 and enc.systolic_bp == 142

    def test_followup_reading_does_not_rewrite_enrollment_measurement(self, patient, signed_in):
        from baseline.models import BaselineAssessment
        b = BaselineAssessment.objects.create(patient=patient, assessment_date=DAY,
                                              systolic_bp=130, diastolic_bp=80)
        signed_in.post(reverse("clinic:followup", args=[patient.pk]), {
            "encounter_date": (DAY + timedelta(days=30)).isoformat(),
            "encounter_type": "followup", "systolic_bp": "160", "diastolic_bp": "95"})
        b.refresh_from_db()
        assert b.systolic_bp == 130

    def test_api_encounter_bp_becomes_a_reading(self, patient, client, django_user_model):
        client.force_login(django_user_model.objects.create_superuser("encapi", password="x"))
        resp = client.post("/api/v1/encounters/", {
            "patient": patient.pk, "encounter_date": DAY.isoformat(),
            "systolic_bp": 170, "diastolic_bp": 100}, content_type="application/json")
        assert resp.status_code == 201, resp.content[:400]
        enc = patient.encounters.get()
        assert enc.vitals.count() == 1 and enc.selected_vital.bp_systolic == 170
