"""reconcile_linked_facts: dry run changes nothing; --apply is idempotent and
only performs provenance-tagged, non-destructive actions."""
import json
from datetime import date
from decimal import Decimal
from io import StringIO

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db
DAY = date(2026, 3, 1)


@pytest.fixture(autouse=True)
def quiet_events(monkeypatch):
    monkeypatch.setattr("events.signal_handlers.dispatch", lambda *a, **k: None)
    monkeypatch.setattr("events.dispatcher.dispatch", lambda *a, **k: None)


@pytest.fixture
def legacy_world():
    """Synthetic pre-2026-09-27 data written the way the old code wrote it."""
    from baseline.models import BaselineAssessment
    from encounters.models import ClinicalEncounter
    from labs.models import LabResult, LabTest
    from pathology.models import Biopsy, GNDiagnosis
    from patients.models import Patient
    call_command("seed_labs", verbosity=0)
    p = Patient.objects.create(patient_id="LEG-1", name="Legacy", sex="M",
                               dob=date(1960, 1, 1), enrollment_date=DAY)
    b = BaselineAssessment.objects.create(patient=p, assessment_date=DAY)
    BaselineAssessment.objects.filter(pk=b.pk).update(
        hypertension=True, hba1c=Decimal("8.1"), comorbidity_snapshot_source="legacy_mirror",
        presentation_syndromes=["nephrotic", "aki"])
    bx = Biopsy.objects.create(patient=p, biopsy_date=DAY, if_pattern="mesangial_iga",
                               em_findings="foot_process_effacement")
    Biopsy.objects.filter(pk=bx.pk).update(crescents_present=False)
    GNDiagnosis.objects.create(biopsy=bx, diagnosis="Minimal change disease")
    # Legacy state as the old code left it (written after the signals ran).
    Patient.objects.filter(pk=p.pk).update(
        hypertension=False, malignancy=False, condition_provenance={},
        biopsy_diagnosis="IgA nephropathy", primary_diagnosis="IgA nephropathy",
        pathology_source_biopsy=None, pathology_projection_state="")
    enc = ClinicalEncounter.objects.create(patient=p, encounter_date=DAY)
    ClinicalEncounter.objects.filter(pk=enc.pk).update(systolic_bp=150, diastolic_bp=90)
    egfr = LabTest.objects.get(code="egfr")
    LabResult.objects.create(patient=p, test=egfr, value_numeric=Decimal("107.8117"),
                             result_date=DAY, source="derived",
                             formula_version="CKD-EPI 2021 (local fallback)")
    alb = LabTest.objects.get(code="albumin")
    for _ in range(2):
        LabResult.objects.create(patient=p, test=alb, value_numeric=Decimal("3.1"),
                                 result_date=DAY)
    return p


def _run(*args):
    out = StringIO()
    call_command("reconcile_linked_facts", *args, stdout=out)
    return out.getvalue()


def _state(p):
    from baseline.models import BaselineAssessment
    from labs.models import LabResult
    from pathology.models import PathologyReport
    p.refresh_from_db()
    b = BaselineAssessment.objects.get(patient=p)
    return {
        "labs": LabResult.all_objects.filter(patient=p).count(),
        "reports": PathologyReport.objects.filter(biopsy__patient=p).count(),
        "biopsy_dx": p.biopsy_diagnosis, "working_dx": p.primary_diagnosis,
        "hba1c_link": b.hba1c_result_id, "legacy_hba1c": b.hba1c,
        "vitals": p.encounters.get().vitals.count(),
        "baseline_htn": b.hypertension, "patient_htn": p.hypertension,
    }


def test_dry_run_reports_and_changes_nothing(legacy_world, tmp_path):
    before = _state(legacy_world)
    out = _run("--json", str(tmp_path / "r.json"))
    assert _state(legacy_world) == before
    report = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert report["mode"] == "dry-run"
    assert report["comorbidity_disagreements"][0]["field"] == "hypertension"
    assert report["pathology_projection"][0]["differences"]["biopsy_diagnosis"]["projected"] \
        == "Minimal change disease"
    assert report["pathology_projection"][0]["working_diagnosis_differs"] is True
    assert report["baseline_hba1c"][0]["status"].startswith("record as legacy")
    assert len(report["lab_possible_duplicates"][0]["rows"]) == 2
    assert report["egfr_defective_fallback"][0]["sex"] == "M"
    assert "crescents_present" in out


def test_apply_is_idempotent_and_non_destructive(legacy_world):
    from baseline.models import BaselineAssessment
    from labs.models import LabResult
    from pathology.models import PathologyFinding
    _run("--apply")
    first = _state(legacy_world)
    _run("--apply")                                   # re-run after "interruption"
    assert _state(legacy_world) == first
    p = legacy_world
    assert first["biopsy_dx"] == "Minimal change disease"
    assert first["working_dx"] == "IgA nephropathy"          # left for the clinician
    assert first["reports"] == 1 and first["vitals"] == 1
    assert first["legacy_hba1c"] == Decimal("8.1")           # original kept
    link = LabResult.objects.get(pk=first["hba1c_link"])
    assert link.source == "legacy" and link.result_date == DAY
    assert set(PathologyFinding.objects.values_list("origin", flat=True)) == {"legacy"}
    # Nothing deleted: both possible-duplicate albumin rows still exist.
    assert LabResult.objects.filter(patient=p, test__code="albumin").count() == 2
    # The legacy comorbidity disagreement is reported, never auto-resolved.
    assert first["baseline_htn"] is True and first["patient_htn"] is False
    b = BaselineAssessment.objects.get(patient=p)
    assert b.presentation_syndromes == ["nephrotic", "aki"]
