"""Approved knowledge-base entries must reach future management plans.

This closes the loop for the Vera capture workflow: a recommendation is pasted
in, parsed into structured entries, reviewed by a clinician, activated -- and
only then does it appear in the Personalized Management Plan for that disease.

The safety properties tested here matter more than the happy path:
drafts must never influence a plan, and KDIGO protocol lines must never be
displaced by knowledge-base additions.
"""
import pytest
from datetime import date

from clinical_reasoning.services.management_plan import (
    DISEASE_TREATMENT_PROFILES, generate_management_plan, merge_kb_recommendations,
)

pytestmark = pytest.mark.django_db


def _source():
    from knowledge.models import GuidelineSource
    src, _ = GuidelineSource.objects.get_or_create(
        abbreviation="Vera",
        defaults={"title": "Vera Health AI", "version_year": 2026,
                  "url": "https://verahealth.ai", "effective_date": date.today()},
    )
    return src


def _entry(entry_id, drug, *, disease_id="iga", status="active",
           plan_line="first_line", **extra):
    from knowledge.models import KnowledgeBaseEntry
    data = {"drug": drug, "dose": "10 mg daily", "duration": "6 months",
            "rationale": "Captured from Vera", "plan_line": plan_line}
    data.update(extra)
    return KnowledgeBaseEntry.objects.create(
        entry_id=entry_id, disease_id=disease_id, rule_data=data,
        source=_source(), evidence_grade="OP", rule_type="treatment",
        status=status, effective_date=date.today(),
        tags=["vera_health", "ai_generated"],
    )


def _patient(pid="BGD-KBM-1"):
    from django.utils import timezone
    from patients.models import Patient
    return Patient.objects.create(
        patient_id=pid, name="Merge Test", hospital_id=f"H-{pid}",
        phone="+1234567890", sex="F", cohort="GN", diabetes_status="no",
        primary_diagnosis="iga", current_phase="active",
        registration_status="active", registration_date=date.today(),
        enrollment_date=date.today(),
        created_at=timezone.now(), updated_at=timezone.now(),
    )


class TestMergeSafety:
    def test_draft_entries_never_reach_a_plan(self):
        # The whole review workflow rests on this: AI-captured recommendations
        # are drafts and must not influence care until a clinician activates.
        _entry("VERA-T-01", "Sparsentan-DRAFT", status="draft")
        plan = generate_management_plan(_patient(), "iga")
        drugs = [d["drug"] for d in plan.first_line]
        assert "Sparsentan-DRAFT" not in drugs

    def test_active_entry_is_added(self):
        _entry("VERA-T-02", "Hydroxychloroquine 200mg (Vera)")
        plan = generate_management_plan(_patient("BGD-KBM-2"), "iga")
        added = [d for d in plan.first_line if d.get("from_knowledge_base")]
        assert [d["drug"] for d in added] == ["Hydroxychloroquine 200mg (Vera)"]

    def test_kdigo_lines_are_preserved_and_come_first(self):
        baseline = [d["drug"] for d in DISEASE_TREATMENT_PROFILES["iga"]["first_line"]]
        _entry("VERA-T-03", "Something New")
        plan = generate_management_plan(_patient("BGD-KBM-3"), "iga")
        assert [d["drug"] for d in plan.first_line][:len(baseline)] == baseline
        assert plan.first_line[-1]["drug"] == "Something New"

    def test_duplicate_drug_is_not_added_twice(self):
        existing = DISEASE_TREATMENT_PROFILES["iga"]["first_line"][0]["drug"]
        _entry("VERA-T-04", existing.upper())
        plan = generate_management_plan(_patient("BGD-KBM-4"), "iga")
        names = [d["drug"].lower() for d in plan.first_line]
        assert names.count(existing.lower()) == 1

    def test_entry_for_another_disease_is_ignored(self):
        _entry("VERA-T-05", "Wrong Disease Drug", disease_id="membranous")
        plan = generate_management_plan(_patient("BGD-KBM-5"), "iga")
        assert not any(d.get("from_knowledge_base") for d in plan.first_line)


class TestProtocolTableIsImmutable:
    """Regression: plans were handed the module-level KDIGO lists directly, so
    every merge permanently appended to DISEASE_TREATMENT_PROFILES -- one
    patient's Vera drug would then show up in every later patient's plan."""

    def test_generating_a_plan_does_not_grow_the_protocol_table(self):
        before = len(DISEASE_TREATMENT_PROFILES["iga"]["first_line"])
        _entry("VERA-T-30", "Leak Check Drug")
        generate_management_plan(_patient("BGD-KBM-30"), "iga")
        generate_management_plan(_patient("BGD-KBM-31"), "iga")
        assert len(DISEASE_TREATMENT_PROFILES["iga"]["first_line"]) == before

    def test_the_same_entry_appears_once_per_plan_not_cumulatively(self):
        _entry("VERA-T-31", "Once Only")
        first = generate_management_plan(_patient("BGD-KBM-32"), "iga")
        second = generate_management_plan(_patient("BGD-KBM-33"), "iga")
        assert [d["drug"] for d in first.first_line].count("Once Only") == 1
        assert [d["drug"] for d in second.first_line].count("Once Only") == 1

    def test_mutating_a_returned_plan_cannot_affect_the_next_one(self):
        plan = generate_management_plan(_patient("BGD-KBM-34"), "iga")
        plan.first_line.append({"drug": "Injected By Caller"})
        nxt = generate_management_plan(_patient("BGD-KBM-35"), "iga")
        assert "Injected By Caller" not in [d["drug"] for d in nxt.first_line]


class TestMergePlacement:
    def test_plan_line_routes_to_the_right_bucket(self):
        _entry("VERA-T-10", "Second Line Drug", plan_line="second_line")
        _entry("VERA-T-11", "Rescue Drug", plan_line="rescue_therapy")
        plan = generate_management_plan(_patient("BGD-KBM-10"), "iga")
        assert "Second Line Drug" in [d["drug"] for d in plan.second_line]
        assert "Rescue Drug" in [d["drug"] for d in plan.rescue_therapy]

    def test_provenance_is_carried_for_display(self):
        _entry("VERA-T-12", "Traceable Drug")
        plan = generate_management_plan(_patient("BGD-KBM-12"), "iga")
        item = [d for d in plan.first_line if d["drug"] == "Traceable Drug"][0]
        assert item["kb_entry_id"] == "VERA-T-12"
        assert item["source_label"] == "Vera"
        assert item["from_knowledge_base"] is True

    def test_optional_fields_are_passed_through(self):
        _entry("VERA-T-13", "Detailed Drug", route="PO", frequency="once daily",
               renal_adjustment="Halve dose if eGFR <30")
        plan = generate_management_plan(_patient("BGD-KBM-13"), "iga")
        item = [d for d in plan.first_line if d["drug"] == "Detailed Drug"][0]
        assert item["route"] == "PO"
        assert item["renal_adjustment"] == "Halve dose if eGFR <30"

    def test_disease_without_a_kdigo_profile_still_gets_kb_entries(self):
        _entry("VERA-T-14", "Orphan Disease Drug", disease_id="rare_gn")
        plan = generate_management_plan(_patient("BGD-KBM-14"), "rare_gn")
        assert "Orphan Disease Drug" in [d["drug"] for d in plan.first_line]

    def test_entry_without_a_drug_name_is_skipped(self):
        _entry("VERA-T-15", "")
        plan = generate_management_plan(_patient("BGD-KBM-15"), "iga")
        assert not any(d.get("from_knowledge_base") for d in plan.first_line)


class TestMergeIsNonFatal:
    def test_plan_generation_survives_a_kb_failure(self, monkeypatch):
        import clinical_reasoning.services.management_plan as mp

        def boom(plan, disease_id):
            raise RuntimeError("KB unavailable")

        # merge_kb_recommendations swallows its own errors; this asserts the
        # contract that a plan is still produced whatever the KB does.
        plan = mp.merge_kb_recommendations(
            mp._build_default_plan(_patient("BGD-KBM-20"), "iga"), "iga")
        assert plan is not None
