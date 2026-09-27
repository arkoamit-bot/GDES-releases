"""Prescriptions: linked investigations, next visit, comorbidities, dosing
facts and the issued snapshot; plus clinical-reasoning semantics.

Corrected-behaviour regressions for the 2026-09-27 entry-linkage review.
"""
from datetime import date, timedelta

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
    return Patient.objects.create(patient_id="RX-1", name="Rx Synthetic", sex="F",
                                  dob=date(1975, 5, 5), enrollment_date=DAY)


@pytest.fixture
def encounter(patient):
    from encounters.models import ClinicalEncounter
    return ClinicalEncounter.objects.create(patient=patient, encounter_date=DAY,
                                            next_due_date=date(2026, 9, 8))


@pytest.fixture
def drug():
    from treatments.models import DrugMaster
    return DrugMaster.objects.create(generic_name="Prednisolone", drug_class="steroid",
                                     default_route="PO")


@pytest.fixture
def signed_in(client, django_user_model):
    user = django_user_model.objects.create_user("rx_user")
    client.force_login(user)
    client.user = user
    return client


def _post_rx(client, patient, **extra):
    data = {"drug_1": "", "strength_1": "5 mg", "frequency_1": "1+0+0"}
    data.update(extra)
    return client.post(reverse("clinic:prescription", args=[patient.pk]), data)


class TestNextVisit:
    def test_existing_next_visit_is_shown_and_kept(self, patient, encounter, drug, signed_in):
        resp = signed_in.get(reverse("clinic:prescription", args=[patient.pk]))
        assert resp.context["default_next_visit"] == "2026-09-08"
        assert resp.context["next_visit_is_selected"] is True
        _post_rx(signed_in, patient, drug_1=drug.pk, next_due_date="2026-09-08")
        encounter.refresh_from_db()
        assert encounter.next_due_date == date(2026, 9, 8)

    def test_explicit_change_is_one_audited_action(self, patient, encounter, drug, signed_in):
        from audit.models import AuditLog
        _post_rx(signed_in, patient, drug_1=drug.pk, next_due_date="2026-09-29",
                 next_due_reason="Patient travelling")
        encounter.refresh_from_db()
        assert encounter.next_due_date == date(2026, 9, 29)
        row = AuditLog.objects.get(model_label="encounters.ClinicalEncounter",
                                   field_name="next_due_date")
        assert row.changed_by == signed_in.user and row.change_reason == "Patient travelling"

    def test_protocol_visits_are_not_touched(self, patient, encounter, drug, signed_in):
        from scheduling.models import ScheduledVisit
        sv = ScheduledVisit.objects.create(patient=patient, label="Month 3",
                                           target_date=date(2026, 12, 1),
                                           window_start=date(2026, 11, 24),
                                           window_end=date(2026, 12, 8))
        _post_rx(signed_in, patient, drug_1=drug.pk, next_due_date="2026-09-29")
        sv.refresh_from_db()
        assert sv.target_date == date(2026, 12, 1) and sv.clinic_date is None

    def test_no_selected_date_shows_a_labelled_suggestion(self, patient, drug, signed_in):
        from encounters.models import ClinicalEncounter
        ClinicalEncounter.objects.create(patient=patient, encounter_date=DAY)
        resp = signed_in.get(reverse("clinic:prescription", args=[patient.pk]))
        assert resp.context["next_visit_is_selected"] is False
        assert "Suggestion" in resp.content.decode()


class TestInvestigations:
    def test_draft_requests_tests_without_ordering(self, patient, encounter, drug, labs, signed_in):
        from labs.models import LabOrder, LabTest
        creat = LabTest.objects.get(code="creatinine")
        _post_rx(signed_in, patient, drug_1=drug.pk,
                 investigations_advised=[str(creat.pk)],
                 investigations_advised_text="Renal ultrasound")
        rx = encounter.prescriptions.get()
        assert [r.test.code for r in rx.test_requests.all()] == ["creatinine"]
        assert rx.investigations_advised == "Renal ultrasound"
        assert not LabOrder.objects.filter(encounter=encounter).exists()

    def test_finalize_places_orders_once_and_links_outstanding(self, patient, encounter, drug,
                                                               labs, signed_in):
        from labs.models import LabOrderItem, LabTest
        from labs.services.ordering import order_tests
        from prescriptions.services.finalize import finalize_prescription
        from prescriptions.services.issue import commit_test_requests
        existing = order_tests(encounter, ["albumin"])        # already outstanding
        ids = [str(LabTest.objects.get(code=c).pk) for c in ("creatinine", "albumin")]
        _post_rx(signed_in, patient, drug_1=drug.pk, investigations_advised=ids)
        rx = encounter.prescriptions.get()
        finalize_prescription(rx)
        commit_test_requests(rx)                              # retry: no-op
        items = LabOrderItem.objects.filter(order__encounter=encounter)
        assert sorted(i.test.code for i in items) == ["albumin", "creatinine"]
        alb = rx.test_requests.get(test__code="albumin")
        assert alb.order_item.order_id == existing.pk          # linked, not re-ordered
        printed = [i["test"] for i in rx.issued_snapshot["investigations"]]
        assert sorted(printed) == ["Serum albumin", "Serum creatinine"]

    def test_legacy_name_posts_still_map_to_catalogue(self, patient, encounter, drug, labs, signed_in):
        _post_rx(signed_in, patient, drug_1=drug.pk, investigations_advised=["Serum creatinine"])
        assert encounter.prescriptions.get().test_requests.get().test.code == "creatinine"


class TestComorbidities:
    def test_corrected_condition_is_not_carried_from_old_rx(self, patient, encounter, drug, signed_in):
        from prescriptions.models import Prescription
        patient.hypertension = False
        patient.save()
        Prescription.objects.create(encounter=encounter, version=1,
                                    comorbidities="Hypertension, Bronchial asthma, Gout")
        resp = signed_in.get(reverse("clinic:prescription", args=[patient.pk]))
        labels = [c["label"] for c in resp.context["record_comorbidities"]]
        assert "Hypertension" not in labels
        assert "Bronchial asthma" in resp.context["prefill_comorbid"]
        assert resp.context["comorbid_extra"] == "Gout"

    def test_current_record_items_are_offered_for_print(self, patient, encounter, drug, signed_in):
        patient.hypertension = True
        patient.save()
        resp = signed_in.get(reverse("clinic:prescription", args=[patient.pk]))
        assert [c["label"] for c in resp.context["record_comorbidities"]] == ["Hypertension"]
        # Leaving it off the slip does not change the patient record.
        _post_rx(signed_in, patient, drug_1=drug.pk)
        patient.refresh_from_db()
        assert patient.hypertension is True


class TestDosing:
    def test_strength_and_dose_are_distinct_and_survive(self, patient, encounter, drug, signed_in):
        from prescriptions.services.finalize import finalize_prescription
        from treatments.models import TreatmentExposure
        _post_rx(signed_in, patient, drug_1=drug.pk, strength_1="5 mg", dose_1="2",
                 dose_unit_1="tab")
        rx = encounter.prescriptions.get()
        item = rx.items.get()
        assert item.strength == "5 mg" and item.dose == "2" and item.dose_unit == "tab"
        assert item.administered_dose == "2 tab"
        assert item.regimen_dose == "2 tab x 5 mg"
        finalize_prescription(rx)
        exp = TreatmentExposure.objects.get(patient=patient, ongoing=True)
        assert exp.dose == "2 tab x 5 mg" and exp.strength == "5 mg"
        snap = rx.issued_snapshot["items"][0]
        assert snap["strength"] == "5 mg" and snap["dose"] == "2 tab"
        html = signed_in.get(reverse("prescriptions:preview", args=[rx.pk])).content.decode()
        assert "2 tab" in html

    def test_dose_change_at_same_strength_splits_the_episode(self, patient, encounter, drug):
        from prescriptions.models import Prescription, PrescriptionItem
        from prescriptions.services.finalize import finalize_prescription
        from treatments.models import TreatmentExposure
        rx1 = Prescription.objects.create(encounter=encounter, version=1)
        PrescriptionItem.objects.create(prescription=rx1, drug=drug, strength="5 mg",
                                        dose="1", dose_unit="tab", frequency="1+0+0")
        finalize_prescription(rx1)
        from encounters.models import ClinicalEncounter
        enc2 = ClinicalEncounter.objects.create(patient=patient,
                                                encounter_date=DAY + timedelta(days=14))
        rx2 = Prescription.objects.create(encounter=enc2, version=1)
        PrescriptionItem.objects.create(prescription=rx2, drug=drug, strength="5 mg",
                                        dose="2", dose_unit="tab", frequency="1+0+0")
        finalize_prescription(rx2)
        episodes = TreatmentExposure.objects.filter(patient=patient).order_by("start_date")
        assert [e.dose for e in episodes] == ["1 tab x 5 mg", "2 tab x 5 mg"]
        assert episodes[0].stop_reason == "dose_change"

    def test_legacy_items_continue_without_spurious_split(self, patient, encounter, drug):
        from prescriptions.models import Prescription, PrescriptionItem
        from prescriptions.services.finalize import finalize_prescription
        from treatments.models import TreatmentExposure
        # An open episode created by the old path (dose copied from strength).
        TreatmentExposure.objects.create(patient=patient, drug=drug, drug_name=drug.generic_name,
                                         dose="5 mg", frequency="1+0+0", route="PO",
                                         start_date=DAY - timedelta(days=30), ongoing=True)
        rx = Prescription.objects.create(encounter=encounter, version=1)
        PrescriptionItem.objects.create(prescription=rx, drug=drug, strength="5 mg",
                                        frequency="1+0+0")
        finalize_prescription(rx)
        assert TreatmentExposure.objects.filter(patient=patient).count() == 1

    def test_no_dose_equals_strength_in_the_save_path(self, patient, encounter, drug, signed_in):
        _post_rx(signed_in, patient, drug_1=drug.pk, strength_1="10 mg")
        item = encounter.prescriptions.get().items.get()
        assert item.dose == "" and item.strength == "10 mg"


class TestIssuedSnapshot:
    def _final_rx(self, patient, encounter, drug):
        from prescriptions.models import Prescription, PrescriptionItem
        from prescriptions.services.finalize import finalize_prescription
        rx = Prescription.objects.create(encounter=encounter, version=1,
                                         diagnosis_text="IgA nephropathy", advice="Low salt")
        PrescriptionItem.objects.create(prescription=rx, drug=drug, strength="5 mg",
                                        frequency="1+0+0")
        finalize_prescription(rx)
        rx.refresh_from_db()
        return rx

    def test_later_edits_do_not_change_an_issued_prescription(self, patient, encounter, drug, labs):
        from labs.services.results import record_result
        from prescriptions.pdf import render_prescription_html
        record_result(patient, "creatinine", result_date=DAY, value_numeric="1.0")
        rx = self._final_rx(patient, encounter, drug)
        before = render_prescription_html(rx)
        hash_before = rx.content_hash
        patient.name = "Renamed Later"
        patient.save()
        encounter.next_due_date = date(2026, 12, 24)
        encounter.save()
        record_result(patient, "creatinine", result_date=DAY + timedelta(days=5), value_numeric="3.0")
        rx.refresh_from_db()
        after = render_prescription_html(rx)
        assert before == after
        assert "Rx Synthetic" in after and "Renamed Later" not in after
        assert rx.content_hash == hash_before == rx.compute_snapshot_hash()
        assert rx.content_hash_version == 2

    def test_legacy_final_is_flagged_not_backfilled(self, patient, encounter, drug):
        from prescriptions.models import Prescription, PrescriptionItem
        from prescriptions.pdf import render_prescription_html
        rx = Prescription.objects.create(encounter=encounter, version=1, status="final")
        PrescriptionItem.objects.create(prescription=rx, drug=drug, strength="5 mg")
        html = render_prescription_html(rx)
        assert "Issued before issued-content snapshots" in html
        rx.refresh_from_db()
        assert rx.issued_snapshot == {} and rx.snapshot_version == 0

    def test_v1_hash_is_unchanged_for_old_prescriptions(self, patient, encounter, drug):
        from prescriptions.models import Prescription, PrescriptionItem
        rx = Prescription.objects.create(encounter=encounter, version=1)
        PrescriptionItem.objects.create(prescription=rx, drug=drug, strength="5 mg",
                                        dose="5 mg", frequency="1+0+0")
        import hashlib
        # v1 joins with a \x01 separator; pinned so a template or snapshot
        # change can never silently alter hashes already issued.
        expected = hashlib.sha256("\x01".join([
            str(rx.encounter_id), "1", "",
            f"{drug.pk}||5 mg|5 mg||1+0+0|after||"]).encode()).hexdigest()
        assert rx.compute_hash() == expected

    def test_archived_pdf_is_not_overwritten(self, patient, encounter, drug, tmp_path, settings):
        from prescriptions.pdf import save_prescription_pdf
        settings.PRESCRIPTION_PDF_DIR = tmp_path
        rx = self._final_rx(patient, encounter, drug)
        path = save_prescription_pdf(rx, b"original")
        save_prescription_pdf(rx, b"re-rendered later")
        assert path.read_bytes() == b"original"


# --- Clinical reasoning semantics ---------------------------------------------

class TestReasoning:
    def test_negative_anca_is_not_evidence_and_dsdna_is_recognised(self, patient, labs):
        from knowledge.services import extract_patient_features
        from labs.services.results import record_result
        record_result(patient, "anca", result_date=DAY, value_text="Negative")
        record_result(patient, "anti_dsdna", result_date=DAY, value_text="Positive")
        feats = extract_patient_features(patient)
        assert "anca" not in feats["labs"]
        assert "anaDsDna" in feats["labs"]
        assert feats["lab_interpretations"]["anca"] == "negative"

    def test_numeric_antibody_above_range_is_positive(self, patient, labs):
        from knowledge.services import extract_patient_features
        from labs.services.results import record_result
        record_result(patient, "anti_pla2r", result_date=DAY, value_numeric="150")
        assert "pla2r" in extract_patient_features(patient)["labs"]
        record_result(patient, "anti_pla2r", result_date=DAY + timedelta(days=90),
                      value_numeric="5")
        assert "pla2r" not in extract_patient_features(patient)["labs"]   # newest result wins

    def test_uacr_is_not_read_as_protein(self, patient, labs):
        from knowledge.services import extract_patient_features
        from labs.services.results import record_result
        record_result(patient, "uacr", result_date=DAY, value_numeric="25")   # mg/g, normal
        feats = extract_patient_features(patient)
        assert feats["proteinuria"] == "none" and feats["uacr"] == 25.0

    def test_legacy_em_option_reaches_features(self, patient):
        from knowledge.services import extract_patient_features
        from pathology.models import Biopsy
        Biopsy.objects.create(patient=patient, biopsy_date=DAY,
                              em_findings="foot_process_effacement")
        assert "podocyteEffacement" in extract_patient_features(patient)["biopsy"]

    def test_diagnosis_expectations_are_inferences_not_findings(self, patient):
        from types import SimpleNamespace
        from knowledge.services import evaluate_entry, extract_patient_features
        from pathology.models import Biopsy, GNDiagnosis
        b = Biopsy.objects.create(patient=patient, biopsy_date=DAY)
        GNDiagnosis.objects.create(biopsy=b, diagnosis="Lupus nephritis class IV")
        feats = extract_patient_features(patient)
        assert "fullHouse" not in feats["biopsy"]
        assert "fullHouse" in feats["biopsy_inferred"]
        entry = SimpleNamespace(disease_id="lupusNephritis", source=None, evidence_grade="", rule_data={
            "conditions": [{"field": "biopsy", "operator": "contains", "value": "fullHouse"}],
            "weight": 6, "explanation": "Full-house immune deposits"})
        score = evaluate_entry(entry, feats)
        assert score.matched_rules and score.matched_rules[0]["inferred"] is True
        assert "not an observed finding" in score.matched_rules[0]["explanation"]
