"""Biopsy field linkage and prescription diagnosis carry-forward.

Corrected-behaviour regressions for
docs/CLAUDE_OPUS_BIOPSY_LINKAGE_DIAGNOSIS_CARRY_FORWARD_2026-09-29.md. The
review's probes (docs/reviews/2026-09-29-biopsy-prescription/probes.py)
asserted the required behaviour; these keep it.
"""
from datetime import date

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db
DAY = date(2026, 9, 1)


@pytest.fixture(autouse=True)
def quiet_events(monkeypatch):
    monkeypatch.setattr("events.signal_handlers.dispatch", lambda *a, **k: None)
    monkeypatch.setattr("events.dispatcher.dispatch", lambda *a, **k: None)


@pytest.fixture
def patient():
    from patients.models import Patient
    return Patient.objects.create(patient_id="LINK-29", name="Link Synthetic", sex="F",
                                  dob=date(1980, 1, 1), enrollment_date=DAY)


@pytest.fixture
def signed_in(client, django_user_model):
    client.force_login(django_user_model.objects.create_user("link29"))
    return client


def _biopsy(client, patient, **data):
    payload = {"bx-biopsy_date": DAY.isoformat(), "dx-diagnosis": "IgA nephropathy"}
    payload.update(data)
    return client.post(reverse("clinic:biopsy", args=[patient.pk]), payload)


def _saved(resp, patient):
    return resp.status_code == 302 and patient.biopsies.exists()


# --- A. Crescents: one coherent state ---------------------------------------

class TestCrescents:
    @pytest.mark.parametrize("state", ["", "unknown", "false"])
    def test_positive_percentage_needs_present(self, patient, signed_in, state):
        data = {"bx-crescent_pct": "25"}
        if state:
            data["bx-crescents_present"] = state
        resp = _biopsy(signed_in, patient, **data)
        assert resp.status_code == 200 and not patient.biopsies.exists()
        assert "Set Crescents to Present" in resp.content.decode()

    def test_present_with_zero_percent_is_rejected(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"bx-crescents_present": "true",
                                              "bx-crescent_pct": "0"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_absent_with_crescentic_count_is_rejected(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"bx-crescents_present": "false",
                                              "rp-crescentic_glomeruli": "3",
                                              "bx-total_glomeruli": "20"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_agreeing_values_save_and_unknown_stays_unknown(self, patient, signed_in):
        assert _saved(_biopsy(signed_in, patient, **{"bx-crescents_present": "true",
                                                     "bx-crescent_pct": "25"}), patient)
        b = patient.biopsies.get()
        assert (b.crescents_present, float(b.crescent_pct)) == (True, 25.0)
        assert _saved(_biopsy(signed_in, patient, **{"bx-biopsy_date": "2026-09-10",
                                                     "bx-crescents_present": "true"}), patient)
        assert patient.biopsies.get(biopsy_date="2026-09-10").crescent_pct is None

    def test_percentages_outside_0_100_are_rejected(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"bx-global_sclerosis_pct": "150",
                                              "bx-ifta_pct": "120"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_oxford_c_must_match_the_crescent_record(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"bx-crescents_present": "true",
                                              "bx-crescent_pct": "10", "igan-C": "0"})
        assert resp.status_code == 200 and "Oxford C0" in resp.content.decode()
        resp = _biopsy(signed_in, patient, **{"bx-crescents_present": "false", "igan-C": "1"})
        assert resp.status_code == 200 and not patient.biopsies.exists()
        # Not assessed on the summary + a C score: nothing to contradict.
        assert _saved(_biopsy(signed_in, patient, **{"igan-C": "1"}), patient)


# --- A. Primary/secondary and variant: one owner ------------------------------

class TestQualifierOwner:
    def test_fsgs_panel_no_longer_asks_primary_secondary(self):
        from clinic.forms import FSGSPathologyForm
        assert "primary_secondary" not in FSGSPathologyForm().fields
        assert "variant" in FSGSPathologyForm().fields

    def test_legacy_panel_value_agreeing_is_kept_on_the_owner(self, patient, signed_in):
        assert _saved(_biopsy(signed_in, patient, **{
            "dx-diagnosis": "FSGS - NOS", "fsgs-primary_secondary": "secondary",
            "fsgs-variant": "nos"}), patient)
        b = patient.biopsies.get()
        assert b.diagnosis.primary_secondary == "secondary"
        assert b.fsgs.primary_secondary == "secondary"

    def test_genetic_fsgs_is_not_forced_into_primary_or_secondary(self, patient, signed_in):
        assert _saved(_biopsy(signed_in, patient, **{
            "dx-diagnosis": "FSGS - genetic/suspected genetic"}), patient)
        assert patient.biopsies.get().diagnosis.primary_secondary == ""

    def test_membranous_secondary_label_must_agree(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{
            "dx-diagnosis": "Membranous nephropathy - secondary/associated",
            "dx-primary_secondary": "primary"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_variant_alone_does_not_imply_primary_or_secondary(self, patient, signed_in):
        assert _saved(_biopsy(signed_in, patient, **{
            "dx-diagnosis": "FSGS - collapsing variant", "fsgs-variant": "collapsing"}), patient)
        assert patient.biopsies.get().diagnosis.primary_secondary == ""

    def test_amended_diagnosis_sets_stated_qualifier_and_panel(self, patient, signed_in):
        assert _saved(_biopsy(signed_in, patient, **{
            "dx-diagnosis": "FSGS - NOS", "dx-primary_secondary": "primary",
            "fsgs-variant": "nos"}), patient)
        b = patient.biopsies.get()
        resp = signed_in.post(reverse("clinic:biopsy_amend", args=[patient.pk, b.pk]), {
            "bx-biopsy_date": DAY.isoformat(), "kind": "amendment",
            "revision_reason": "Central report", "primary_diagnosis": "FSGS - secondary/adaptive",
            "f-TOTAL_FORMS": "0", "f-INITIAL_FORMS": "0",
            "f-MIN_NUM_FORMS": "0", "f-MAX_NUM_FORMS": "1000"})
        assert resp.status_code == 302
        b.refresh_from_db()
        assert b.diagnosis.primary_secondary == "secondary"
        assert b.fsgs.primary_secondary == "secondary"

    def test_review_finalization_keeps_one_owner(self, patient, signed_in):
        from pathology.services.review import submit_review
        assert _saved(_biopsy(signed_in, patient, **{
            "dx-diagnosis": "FSGS - primary", "fsgs-variant": "nos"}), patient)
        b = patient.biopsies.get()
        submit_review(b, "local", diagnosis="FSGS - primary")
        submit_review(b, "central", diagnosis="FSGS - secondary/adaptive")
        submit_review(b, "adjudication", diagnosis="FSGS - secondary/adaptive")
        b.refresh_from_db()
        assert b.diagnosis.diagnosis == "FSGS - secondary/adaptive"
        assert b.diagnosis.primary_secondary == "secondary"
        assert b.fsgs.primary_secondary == "secondary"

    def test_form_table_is_explicit_not_substring(self):
        from pathology.diagnosis import qualifier_table
        t = qualifier_table()
        assert "panel" not in t["C1q nephropathy"]
        assert t["Membranous nephropathy - PLA2R positive"]["panel"] == "mn"
        assert t["Lupus nephritis class IV+V"]["isn_rps_class"] == "IV+V"
        assert t["FSGS - tip lesion variant"]["variant"] == "tip"
        assert "primary_secondary" not in t["FSGS - tip lesion variant"]


# --- A. Result category and the registration gate ---------------------------

class TestResultCategory:
    def test_positive_needs_a_diagnosis(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"dx-diagnosis": "", "rp-status": "draft",
                                              "bx-result_category": "positive"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_negative_contradicts_a_specific_gn(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"bx-result_category": "negative"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_inadequate_specimen_cannot_be_negative(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{
            "dx-diagnosis": "Diabetic kidney disease only - no GN",
            "bx-adequacy": "inadequate", "bx-result_category": "negative"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_no_gn_label_cannot_be_positive(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{
            "dx-diagnosis": "Hypertensive nephrosclerosis only - no GN",
            "bx-result_category": "positive"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_pending_report_does_not_change_registry(self, patient, signed_in):
        patient.registration_status = "suspected"
        patient.save()
        resp = _biopsy(signed_in, patient, **{"rp-status": "pending",
                                              "bx-result_category": "positive"})
        assert resp.status_code == 200 and not patient.biopsies.exists()
        patient.refresh_from_db()
        assert patient.registration_status == "suspected"

    def test_blank_result_is_not_inferred(self, patient, signed_in):
        assert _saved(_biopsy(signed_in, patient), patient)
        assert patient.biopsies.get().result_category == ""


# --- A. One transaction ---------------------------------------------------------

def test_failed_score_save_rolls_back_the_whole_biopsy(patient, signed_in, monkeypatch):
    from pathology.models import IgANScore

    def boom(self, *a, **k):
        raise RuntimeError("score save failed")
    monkeypatch.setattr(IgANScore, "save", boom)
    with pytest.raises(RuntimeError):
        _biopsy(signed_in, patient, **{"igan-M": "1"})
    assert not patient.biopsies.exists()


# --- A. Other write paths ---------------------------------------------------------

def test_api_rejects_the_same_crescent_contradiction(patient, django_user_model):
    from rest_framework.test import APIClient
    from pathology.models import Biopsy
    b = Biopsy.objects.create(patient=patient, biopsy_date=DAY)
    api = APIClient()
    api.force_authenticate(django_user_model.objects.create_superuser("api29", "a@x.test", "x"))
    resp = api.patch(f"/api/v1/biopsies/{b.pk}/",
                     {"crescents_present": False, "crescent_pct": "20"}, format="json")
    assert resp.status_code == 400, resp.content
    b.refresh_from_db()
    assert b.crescent_pct is None


def test_model_clean_covers_admin(patient):
    from django.core.exceptions import ValidationError
    from pathology.models import Biopsy
    with pytest.raises(ValidationError):
        Biopsy(patient=patient, biopsy_date=DAY, crescents_present=False,
               crescent_pct=30).full_clean()


def test_inventory_lists_legacy_conflicts_without_changing_them(patient):
    import io
    import json
    from django.core.management import call_command
    from pathology.models import Biopsy, FSGSPathology, GNDiagnosis
    b = Biopsy.objects.create(patient=patient, biopsy_date=DAY)
    Biopsy.objects.filter(pk=b.pk).update(crescents_present=False, crescent_pct=40,
                                          ifta_pct=120)
    GNDiagnosis.objects.create(biopsy=b, diagnosis="FSGS - primary",
                               primary_secondary="secondary")
    FSGSPathology.objects.create(biopsy=b, primary_secondary="primary")
    out = io.StringIO()
    call_command("reconcile_linked_facts", stdout=out)
    text = out.getvalue()
    assert "biopsy_conflicting_values: 1" in text
    row = next(json.loads(line.strip()) for line in text.splitlines()
               if '"biopsy_pk"' in line and '"problems"' in line)
    joined = " ".join(row["problems"])
    assert "ifta_pct=120" in joined and "crescents_present" in joined
    assert "states primary" in joined and "FSGS panel" in joined
    b.refresh_from_db()
    assert (b.crescents_present, int(b.crescent_pct), int(b.ifta_pct)) == (False, 40, 120)


# --- B. Prescription diagnosis carry-forward ------------------------------------

def _encounter(patient, day=DAY):
    from encounters.models import ClinicalEncounter
    return ClinicalEncounter.objects.create(patient=patient, encounter_date=day)


def _rx(encounter, dx, status="final", version=1):
    from prescriptions.models import Prescription
    return Prescription.objects.create(encounter=encounter, diagnosis_text=dx,
                                       status=status, version=version)


def _form(client, patient):
    resp = client.get(reverse("clinic:prescription", args=[patient.pk]))
    assert resp.status_code == 200
    return resp


class TestDiagnosisCarryForward:
    def test_previous_prescription_wins_over_older_working_diagnosis(self, patient, signed_in):
        patient.primary_diagnosis = "IgA nephropathy"
        patient.save()
        _rx(_encounter(patient), "FSGS - primary")
        resp = _form(signed_in, patient)
        assert resp.context["default_diagnosis"] == "FSGS - primary"
        assert "Carried from the prescription" in resp.context["diagnosis_source_label"]
        # The newer working diagnosis is shown beside it, not swapped in.
        assert ("Working diagnosis on the patient record", "IgA nephropathy") in \
            resp.context["diagnosis_also_on_record"]

    def test_first_prescription_falls_back_then_blank(self, patient, signed_in):
        _encounter(patient)
        assert _form(signed_in, patient).context["default_diagnosis"] == ""
        patient.primary_diagnosis = "Minimal change disease"
        patient.save()
        resp = _form(signed_in, patient)
        assert resp.context["default_diagnosis"] == "Minimal change disease"
        assert resp.context["diagnosis_source_label"] == "From the patient's working diagnosis"

    def test_blank_previous_diagnosis_is_skipped(self, patient, signed_in):
        e1 = _encounter(patient)
        _rx(e1, "Lupus nephritis class IV")
        _rx(_encounter(patient, date(2026, 9, 15)), "")
        assert _form(signed_in, patient).context["default_diagnosis"] == "Lupus nephritis class IV"

    def test_custom_diagnosis_is_kept_as_an_option(self, patient, signed_in):
        _rx(_encounter(patient), "IgAN with TMA features (per central review)")
        resp = _form(signed_in, patient)
        value = "IgAN with TMA features (per central review)"
        assert resp.context["default_diagnosis"] == value
        assert any(v == value for v, _l in resp.context["diagnosis_choices"])
        assert f'value="{value}" selected' in resp.content.decode()

    def test_newer_draft_is_offered_not_substituted(self, patient, signed_in):
        e = _encounter(patient)
        _rx(e, "FSGS - primary", version=1)
        draft = _rx(e, "Minimal change disease", status="draft", version=2)
        resp = _form(signed_in, patient)
        assert resp.context["default_diagnosis"] == "FSGS - primary"
        assert resp.context["diagnosis_newer_draft"].pk == draft.pk
        assert "Resume that draft" in resp.content.decode()

    def test_other_patients_and_later_visits_are_ignored(self, patient):
        from patients.models import Patient
        from prescriptions.services.diagnosis_prefill import diagnosis_prefill
        other = Patient.objects.create(patient_id="LINK-29-B", name="Other", sex="M",
                                       dob=date(1970, 1, 1))
        _rx(_encounter(other), "Anti-GBM disease")
        early = _encounter(patient, date(2026, 8, 1))
        _rx(_encounter(patient, date(2026, 9, 20)), "FSGS - primary")   # later visit
        pre = diagnosis_prefill(patient, early)
        assert pre.value == "" and pre.source == "none"

    def test_cleared_diagnosis_survives_a_failed_save(self, patient, signed_in):
        _rx(_encounter(patient), "FSGS - primary")
        resp = signed_in.post(reverse("clinic:prescription", args=[patient.pk]),
                              {"diagnosis_text": "", "advice": "Low salt"})
        assert resp.status_code == 200
        assert resp.context["default_diagnosis"] == ""
        assert resp.context["prefill_advice"] == "Low salt"
        resp = signed_in.post(reverse("clinic:prescription", args=[patient.pk]),
                              {"diagnosis_text": "Minimal change disease"})
        assert resp.context["default_diagnosis"] == "Minimal change disease"

    def test_new_prescription_prints_accepted_diagnosis_old_one_unchanged(self, patient, signed_in):
        from prescriptions.models import Prescription, PrescriptionItem
        from prescriptions.pdf import render_prescription_html
        from prescriptions.services.finalize import finalize_prescription
        from treatments.models import DrugMaster
        drug = DrugMaster.objects.create(generic_name="Ramipril", drug_class="raasi",
                                         default_route="PO")
        e = _encounter(patient)
        old = _rx(e, "FSGS - primary", status="draft")
        PrescriptionItem.objects.create(prescription=old, drug=drug, strength="5 mg",
                                        frequency="1+0+0")
        finalize_prescription(old, override_blocks=True)
        old.refresh_from_db()
        old_hash, old_html = old.content_hash, render_prescription_html(old)
        assert _form(signed_in, patient).context["default_diagnosis"] == "FSGS - primary"
        resp = signed_in.post(reverse("clinic:prescription", args=[patient.pk]), {
            "diagnosis_text": "FSGS - secondary/adaptive", "drug_1": str(drug.pk),
            "strength_1": "5 mg", "frequency_1": "1+0+0"})
        assert resp.status_code == 302
        new = Prescription.objects.exclude(pk=old.pk).get()
        finalize_prescription(new, override_blocks=True)
        new.refresh_from_db()
        assert "FSGS - secondary/adaptive" in render_prescription_html(new)
        old.refresh_from_db()
        assert old.diagnosis_text == "FSGS - primary" and old.content_hash == old_hash
        assert render_prescription_html(old) == old_html
        patient.refresh_from_db()
        assert patient.primary_diagnosis != "FSGS - secondary/adaptive"


# --- Projection wiring --------------------------------------------------------

def test_projection_receivers_cannot_be_garbage_collected():
    """The receiver was a closure inside ready(), held only weakly: on the
    clinic server it was collected and no biopsy ever updated the patient's
    pathology summary. It must be a module-level, strongly held receiver."""
    import gc
    from django.db.models.signals import post_delete, post_save
    from pathology.apps import on_pathology_change
    from pathology.models import Biopsy, GNDiagnosis, IgANScore, LupusPathology
    gc.collect()
    for signal in (post_save, post_delete):
        for model in (Biopsy, GNDiagnosis, IgANScore, LupusPathology):
            live = signal._live_receivers(model)
            live = live[0] if isinstance(live, tuple) else live
            assert on_pathology_change in live, (signal, model)
            assert not any("<locals>" in getattr(r, "__qualname__", "") for r in live)
