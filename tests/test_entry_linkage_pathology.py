"""Pathology: one projection, coherent review finalization, multiple findings.

Corrected-behaviour regressions for the 2026-09-27 entry-linkage review
(docs/CLAUDE_OPUS_ENTRY_LINKAGE_HISTOPATHOLOGY_PRINT_REVIEW_2026-09-27.md).
The review's probes asserted the defects; these assert the fixes.
"""
from datetime import date

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db
DAY = date(2026, 9, 1)


@pytest.fixture(autouse=True)
def quiet_events(monkeypatch):
    # Persistence under test; event consumers are covered separately below.
    monkeypatch.setattr("events.signal_handlers.dispatch", lambda *a, **k: None)
    monkeypatch.setattr("events.dispatcher.dispatch", lambda *a, **k: None)


@pytest.fixture
def patient():
    from patients.models import Patient
    return Patient.objects.create(patient_id="PATH-1", name="Path Synthetic", sex="F",
                                  dob=date(1980, 1, 1), enrollment_date=DAY)


@pytest.fixture
def signed_in(client, django_user_model):
    client.force_login(django_user_model.objects.create_user("path_user"))
    return client


def _biopsy(client, patient, **data):
    payload = {"bx-biopsy_date": DAY.isoformat()}
    payload.update(data)
    return client.post(reverse("clinic:biopsy", args=[patient.pk]), payload)


def _findings(rows):
    data = {"f-TOTAL_FORMS": str(len(rows)), "f-INITIAL_FORMS": "0",
            "f-MIN_NUM_FORMS": "0", "f-MAX_NUM_FORMS": "1000"}
    for i, row in enumerate(rows):
        for k, v in row.items():
            data[f"f-{i}-{k}"] = v
    return data


# --- Projection -------------------------------------------------------------

class TestProjection:
    def test_repeat_biopsy_updates_pathology_summary_but_not_working_dx(self, patient, signed_in):
        assert _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"}).status_code == 302
        assert _biopsy(signed_in, patient, **{"bx-biopsy_date": "2026-09-20",
                                              "dx-diagnosis": "Minimal change disease"}).status_code == 302
        patient.refresh_from_db()
        newest = patient.biopsies.order_by("-biopsy_date").first()
        assert patient.biopsy_diagnosis == "Minimal change disease"
        assert patient.pathology_source_biopsy_id == newest.pk
        assert patient.pathology_projection_state == "provisional"
        # The working (clinical) diagnosis is the clinician's: prefilled once,
        # never silently replaced by a later biopsy.
        assert patient.primary_diagnosis == "IgA nephropathy"

    def test_explicit_adoption_updates_working_dx_with_audit(self, patient, signed_in):
        from audit.models import AuditLog
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"})
        _biopsy(signed_in, patient, **{"bx-biopsy_date": "2026-09-20",
                                       "dx-diagnosis": "Minimal change disease"})
        resp = signed_in.post(reverse("clinic:adopt_pathology_dx", args=[patient.pk]))
        assert resp.status_code == 302
        patient.refresh_from_db()
        assert patient.primary_diagnosis == "Minimal change disease"
        row = AuditLog.objects.filter(model_label="patients.Patient",
                                      field_name="primary_diagnosis").latest("changed_at")
        assert "Adopted pathology diagnosis" in row.change_reason

    def test_newer_pending_biopsy_does_not_displace_final_interpretation(self, patient, signed_in):
        from pathology.services.projection import select_source
        from pathology.services.review import submit_review
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"})
        first = patient.biopsies.get()
        submit_review(first, "local", diagnosis="IgA nephropathy")
        submit_review(first, "central", diagnosis="IgA nephropathy")   # concordant -> final
        _biopsy(signed_in, patient, **{"bx-biopsy_date": "2026-09-20",
                                       "dx-diagnosis": "Minimal change disease"})
        patient.refresh_from_db()
        sel = select_source(patient)
        assert sel.state == "final" and sel.biopsy.pk == first.pk
        assert [b.biopsy_date for b in sel.pending_biopsies] == [date(2026, 9, 20)]
        assert patient.biopsy_diagnosis == "IgA nephropathy"
        page = signed_in.get(reverse("clinic:patient_detail", args=[patient.pk])).content.decode()
        assert "pending review" in page

    def test_disease_change_clears_obsolete_scores(self, patient, signed_in):
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy",
                                       "igan-M": "1", "igan-E": "0", "igan-S": "1",
                                       "igan-T": "0", "igan-C": "0"})
        patient.refresh_from_db()
        assert patient.oxford_mestc == "M1E0S1T0C0"
        _biopsy(signed_in, patient, **{"bx-biopsy_date": "2026-09-20",
                                       "dx-diagnosis": "Minimal change disease"})
        patient.refresh_from_db()
        assert patient.oxford_mestc == ""

    def test_patient_form_shows_pathology_fields_read_only(self, patient, signed_in):
        from clinic.forms import PatientForm
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"})
        patient.refresh_from_db()
        form = PatientForm(instance=patient)
        assert form.fields["biopsy_diagnosis"].disabled
        data = {"name": patient.name, "sex": patient.sex, "diabetes_status": "none"}
        data["biopsy_diagnosis"] = "Something typed over it"
        bound = PatientForm(data, instance=patient)
        assert bound.is_valid(), bound.errors
        assert bound.cleaned_data["biopsy_diagnosis"] == "IgA nephropathy"

    def test_admin_or_api_diagnosis_edit_reprojects(self, patient, signed_in):
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"})
        dx = patient.biopsies.get().diagnosis
        dx.diagnosis = "Minimal change disease"
        dx.save()   # e.g. via the admin inline -- signal-driven projection
        patient.refresh_from_db()
        assert patient.biopsy_diagnosis == "Minimal change disease"


# --- Review finalization ------------------------------------------------------

class TestReviewFinalization:
    def test_adjudicated_lupus_class_reaches_panel_patient_and_export(self, patient, signed_in):
        from exports.services.dataset import build_row
        from pathology.models import PathologyReview
        from pathology.services.review import adjudicate
        assert _biopsy(signed_in, patient, **{"dx-diagnosis": "Lupus nephritis class III",
                                              "lupus-isn_rps_class": "III"}).status_code == 302
        biopsy = patient.biopsies.get()
        adjudicate(biopsy, diagnosis="Lupus nephritis class IV", isn_rps_class="IV")
        biopsy.refresh_from_db()
        patient.refresh_from_db()
        assert biopsy.reviews.get(role=PathologyReview.Role.ADJUDICATION).is_final
        assert biopsy.diagnosis.diagnosis == "Lupus nephritis class IV"
        assert biopsy.lupus.isn_rps_class == "IV"
        assert patient.isn_rps_class == "IV"
        assert patient.pathology_projection_state == "final"
        row = build_row(patient)
        assert row["pathology_diagnosis"] == "Lupus nephritis class IV"
        assert row["isn_rps_class"] == "IV"
        # The local report revision keeps what it originally stated.
        local = biopsy.reports.get(role="local", is_current=True)
        assert local.scores["lupus"]["isn_rps_class"] == "III"

    def test_local_and_central_disagreement_stays_visible(self, patient, signed_in):
        from pathology.services.review import submit_review
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"})
        b = patient.biopsies.get()
        submit_review(b, "local", diagnosis="IgA nephropathy")
        submit_review(b, "central", diagnosis="Minimal change disease")
        b.refresh_from_db()
        assert b.review_status == "discordant"
        assert b.reviews.count() == 2
        page = signed_in.get(reverse("clinic:biopsy_detail", args=[patient.pk, b.pk])).content.decode()
        assert "disagree" in page


# --- Diagnosis qualifier consistency ------------------------------------------

class TestQualifiers:
    def test_fsgs_contradiction_is_rejected(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"dx-diagnosis": "FSGS - primary",
                                              "dx-primary_secondary": "primary",
                                              "fsgs-primary_secondary": "secondary"})
        assert resp.status_code == 200
        assert not patient.biopsies.exists()
        assert "states primary" in resp.content.decode()

    def test_fsgs_variant_contradiction_is_rejected(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"dx-diagnosis": "FSGS - collapsing variant",
                                              "fsgs-variant": "tip"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_diagnosis_prefills_qualifiers(self, patient, signed_in):
        assert _biopsy(signed_in, patient, **{"dx-diagnosis": "FSGS - collapsing variant",
                                              "fsgs-primary_secondary": "primary"}).status_code == 302
        b = patient.biopsies.get()
        assert b.fsgs.variant == "collapsing"
        assert b.diagnosis.primary_secondary == "primary"

    def test_unrelated_score_panel_is_not_attached(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy",
                                              "lupus-isn_rps_class": "IV"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_panel_allowed_with_coexisting_diagnosis_or_reason(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{
            "dx-diagnosis": "IgA nephropathy", "lupus-isn_rps_class": "IV",
            "rp-additional_diagnoses": "Lupus nephritis class IV"})
        assert resp.status_code == 302

    def test_mixed_lupus_classes_still_supported(self, patient, signed_in):
        assert _biopsy(signed_in, patient, **{"dx-diagnosis": "Lupus nephritis class IV+V"}).status_code == 302
        patient.refresh_from_db()
        assert patient.isn_rps_class == "IV+V"

    def test_no_substring_guessing(self):
        from pathology import diagnosis as dxrules
        assert dxrules.family("C1q nephropathy") == ""          # not IgA
        assert dxrules.family("Membranous nephropathy - PLA2R positive") == dxrules.MN
        assert dxrules.family("iga") == dxrules.IGAN              # explicit legacy alias

    def test_legacy_free_text_maps_by_whole_phrase_only(self):
        from pathology import diagnosis as dxrules
        # The column held free text before it had choices.
        assert dxrules.canonical("IgA nephropathy (IgAN)") == "IgA nephropathy"
        assert dxrules.qualifiers("FSGS") == {"family": dxrules.FSGS}   # no variant invented
        assert dxrules.family("Membranous nephropathy") == dxrules.MN
        assert dxrules.family("ANCA vasculitis") == dxrules.ANCA
        # Unlisted phrasing stays unmapped rather than guessed from a substring.
        assert dxrules.family("IgA-dominant infection-related GN (query)") == ""
        assert dxrules.family("Not lupus nephritis") == ""


# --- Histopathology report with multiple findings -----------------------------

EM_TWO = [
    {"section": "em", "code": "deposits_subepithelial", "presence": "present"},
    {"section": "em", "code": "foot_process_effacement", "presence": "present",
     "extent_pct": "70"},
]
IF_ROWS = [
    {"section": "if_marker", "marker": "IgG", "intensity": "3+", "distribution": "granular",
     "site": "capillary_wall", "presence": "present"},
    {"section": "if_marker", "marker": "C3", "intensity": "1+", "distribution": "granular",
     "site": "capillary_wall", "presence": "present"},
    {"section": "if_marker", "marker": "IgA", "intensity": "0", "presence": "absent"},
]
OTHER_ROW = [{"section": "lm_glomerular", "code": "other",
              "other_label": "Mesangiolysis", "presence": "present"},
             {"section": "lm_glomerular", "code": "segmental_sclerosis",
              "presence": "present", "count": "2", "denominator": "18",
              "extent": "segmental"}]


class TestFindings:
    def _post_full(self, client, patient, extra=None):
        data = {"dx-diagnosis": "Membranous nephropathy - PLA2R positive",
                "bx-total_glomeruli": "18", "rp-status": "final",
                "rp-lm_status": "performed", "rp-if_status": "performed",
                "rp-em_status": "performed", "rp-ihc_status": "not_done",
                "rp-glomeruli_if": "6", "rp-glomeruli_em": "2",
                "rp-globally_sclerosed": "3"}
        data.update(_findings(EM_TWO + IF_ROWS + OTHER_ROW))
        data.update(extra or {})
        return _biopsy(client, patient, **data)

    def test_report_keeps_every_finding_and_state(self, patient, signed_in):
        resp = self._post_full(signed_in, patient)
        assert resp.status_code == 302, resp.content[:600]
        b = patient.biopsies.get()
        report = b.reports.get()
        codes = sorted((f.section, f.code, f.marker) for f in report.findings.all())
        assert ("em", "deposits_subepithelial", "") in codes
        assert ("em", "foot_process_effacement", "") in codes
        assert sum(1 for s, c, m in codes if s == "if_marker") == 3
        other = report.findings.get(code="other")
        assert other.other_label == "Mesangiolysis"
        assert report.ihc_status == "not_done"
        assert report.findings.get(marker="IgA").presence == "absent"
        page = signed_in.get(reverse("clinic:biopsy_detail", args=[patient.pk, b.pk])).content.decode()
        for text in ("Mesangiolysis", "Foot-process effacement", "IgG", "Not done"):
            assert text in page

    def test_findings_reach_export_api_and_reasoning(self, patient, signed_in, client, django_user_model):
        from exports.services.dataset import build_findings_table, build_row
        from knowledge.services import extract_patient_features
        from patients.models import Patient
        self._post_full(signed_in, patient)
        cols, rows = build_findings_table(Patient.objects.filter(pk=patient.pk))
        assert len(rows) == 7
        assert {r["patient_id"] for r in rows} == {"PATH-1"}
        # The patient-level dataset still has exactly one row per patient.
        assert build_row(patient)["patient_id"] == "PATH-1"
        feats = extract_patient_features(patient)
        assert "podocyteEffacement" in feats["biopsy"]
        assert "subepithelial" in feats["biopsy"]
        user = django_user_model.objects.create_superuser("api_admin", password="pw")
        client.force_login(user)
        body = client.get("/api/v1/pathology-reports/", {"biopsy": patient.biopsies.get().pk}).json()
        results = body["results"] if isinstance(body, dict) and "results" in body else body
        assert len(results[0]["findings"]) == 7

    def test_modality_not_done_rejects_its_findings(self, patient, signed_in):
        resp = self._post_full(signed_in, patient, {"rp-em_status": "not_done"})
        assert resp.status_code == 200 and not patient.biopsies.exists()
        assert "cannot be recorded" in resp.content.decode()

    def test_count_cannot_exceed_total(self, patient, signed_in):
        resp = self._post_full(signed_in, patient, {"rp-globally_sclerosed": "30"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_percentage_over_100_rejected(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy",
                                              "bx-ifta_pct": "140"})
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_reported_percentage_disagreeing_with_counts_is_kept_and_warned(self, patient, signed_in):
        resp = self._post_full(signed_in, patient, {"bx-global_sclerosis_pct": "40"})
        assert resp.status_code == 302
        b = patient.biopsies.get()
        assert str(b.global_sclerosis_pct) == "40.0"   # kept as reported
        follow = signed_in.get(resp["Location"]).content.decode()
        assert "The reported value is kept" in follow

    def test_blank_lesion_is_not_a_negative(self, patient, signed_in):
        _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy"})
        b = patient.biopsies.get()
        assert b.crescents_present is None and b.necrosis_present is None

    def test_absent_summary_contradicting_present_finding_is_rejected(self, patient, signed_in):
        data = {"dx-diagnosis": "IgA nephropathy", "bx-crescents_present": "false"}
        data.update(_findings([{"section": "lm_glomerular", "code": "crescent_cellular",
                                "presence": "present"}]))
        resp = _biopsy(signed_in, patient, **data)
        assert resp.status_code == 200 and not patient.biopsies.exists()

    def test_pending_report_without_diagnosis_is_recordable(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"rp-status": "pending", "rp-em_status": "pending"})
        assert resp.status_code == 302
        b = patient.biopsies.get()
        assert not hasattr(b, "diagnosis")      # no diagnosis invented
        assert b.reports.get().status == "pending"

    def test_final_report_requires_diagnosis(self, patient, signed_in):
        resp = _biopsy(signed_in, patient, **{"rp-status": "final"})
        assert resp.status_code == 200 and not patient.biopsies.exists()


class TestAmendment:
    def test_amendment_is_a_new_revision_and_keeps_the_old(self, patient, signed_in):
        from audit.models import AuditLog
        TestFindings()._post_full(signed_in, patient)
        b = patient.biopsies.get()
        url = reverse("clinic:biopsy_amend", args=[patient.pk, b.pk])
        assert signed_in.get(url).status_code == 200
        data = {"kind": "amendment", "revision_reason": "EM re-read: no subepithelial deposits",
                "bx-biopsy_date": DAY.isoformat(), "bx-total_glomeruli": "18",
                "rp-status": "final", "rp-em_status": "performed", "rp-if_status": "performed",
                "rp-lm_status": "performed"}
        data.update(_findings([{"section": "em", "code": "foot_process_effacement",
                                "presence": "present", "extent_pct": "90"}]))
        resp = signed_in.post(url, data)
        assert resp.status_code == 302, resp.content[:800]
        revisions = list(b.reports.order_by("revision"))
        assert [r.revision for r in revisions] == [1, 2]
        assert not revisions[0].is_current and revisions[1].is_current
        assert revisions[0].findings.count() == 7            # untouched
        assert revisions[1].findings.count() == 1
        assert revisions[1].supersedes_id == revisions[0].pk
        assert AuditLog.objects.filter(model_label="pathology.PathologyReport",
                                       change_reason__icontains="EM re-read").exists()

    def test_addendum_keeps_previous_findings(self, patient, signed_in):
        TestFindings()._post_full(signed_in, patient)
        b = patient.biopsies.get()
        data = {"kind": "addendum", "revision_reason": "Congo red result",
                "bx-biopsy_date": DAY.isoformat(), "bx-total_glomeruli": "18",
                "rp-ihc_status": "performed"}
        data.update(_findings([{"section": "special_stain", "code": "congo_red",
                                "presence": "absent"}]))
        resp = signed_in.post(reverse("clinic:biopsy_amend", args=[patient.pk, b.pk]), data)
        assert resp.status_code == 302, resp.content[:800]
        current = b.reports.get(is_current=True)
        assert current.findings.count() == 8

    def test_amendment_requires_reason(self, patient, signed_in):
        TestFindings()._post_full(signed_in, patient)
        b = patient.biopsies.get()
        data = {"kind": "amendment", "bx-biopsy_date": DAY.isoformat(), "rp-status": "final"}
        data.update(_findings([]))
        resp = signed_in.post(reverse("clinic:biopsy_amend", args=[patient.pk, b.pk]), data)
        assert resp.status_code == 200
        assert b.reports.count() == 1


class TestLegacyConversion:
    def test_scalar_if_em_become_tagged_legacy_findings(self, patient):
        from pathology.models import Biopsy
        from pathology.services.report import legacy_report_from_biopsy
        b = Biopsy.objects.create(patient=patient, biopsy_date=DAY,
                                  if_pattern="full_house", em_findings="foot_process_effacement")
        report = legacy_report_from_biopsy(b)
        assert report.origin == "legacy" and report.report_date is None
        assert report.role == "local" and not report.signed_by
        values = {(f.section, f.code, f.origin, f.legacy_value) for f in report.findings.all()}
        assert ("if_interpretation", "full_house", "legacy", "full_house") in values
        assert ("em", "foot_process_effacement", "legacy", "foot_process_effacement") in values
        # Original scalars are preserved; conversion is idempotent.
        b.refresh_from_db()
        assert b.if_pattern == "full_house"
        assert legacy_report_from_biopsy(b) is None


class TestAggregateEvent:
    def test_one_event_after_commit_for_the_whole_biopsy(self, patient, signed_in, monkeypatch,
                                                         django_capture_on_commit_callbacks):
        sent = []
        monkeypatch.setattr("events.dispatcher.dispatch",
                            lambda event_type, **kw: sent.append((event_type, kw.get("payload"))))
        with django_capture_on_commit_callbacks(execute=True):
            _biopsy(signed_in, patient, **{"dx-diagnosis": "IgA nephropathy",
                                           "igan-M": "1", "igan-E": "0", "igan-S": "0",
                                           "igan-T": "0", "igan-C": "0"})
        changed = [p for t, p in sent if t == "pathology.report_changed"]
        assert len(changed) == 1
        assert changed[0]["biopsy_id"] == patient.biopsies.get().pk
