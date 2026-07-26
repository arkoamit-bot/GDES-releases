"""Tests for parsing a Vera Health response into plan-ready recommendations.

The sample below is written in the shape Vera actually answers in -- markdown
headings, bold labels, bullets, numbered lists -- not the clean `Drug:` blocks
the prompt asks for. The previous parser only matched a bare `Drug:` at the
start of a line, so responses like this were stored as one opaque blob.
"""
from clinical_reasoning.services import vera_ingest


VERA_MARKDOWN = """
## Recommended Prescription

### First-Line Therapy

**Drug:** Prednisolone
**Dose:** 1 mg/kg/day (max 80 mg)
**Frequency:** once daily
**Route:** PO
**Duration:** 4 weeks, then taper over 6 months
**Renal adjustment:** None required at eGFR 52 mL/min
**Monitoring:** Fasting glucose, BP, weight every 2 weeks
**Evidence:** KDIGO 2021 Glomerular Diseases, Chapter 3
**Rationale:** Induction of remission in biopsy-proven minimal change disease.

- **Drug:** Ramipril
  - **Dose:** 5 mg
  - **Frequency:** once daily
  - **Route:** PO
  - **Duration:** indefinite
  - **Rationale:** Antiproteinuric effect; target BP <130/80.

### Second-Line Therapy

**Drug:** Tacrolimus
**Dose:** 0.05 mg/kg/day divided BD
**Duration:** 12 months
**Monitoring:** Trough level 5-8 ng/mL, creatinine every 2 weeks

## Pre-treatment checks

1. Hepatitis B, C and HIV serology
2. Chest X-ray to exclude latent TB

## Contraindications to consider

- Active systemic infection
- Uncontrolled diabetes mellitus

## Drug interactions to monitor

- Tacrolimus with azole antifungals (raises trough levels)

## Vaccination requirements

- Pneumococcal and influenza vaccination before immunosuppression

## Patient counselling points

- Do not stop steroids abruptly
- Report fever or dysuria promptly
"""


class TestParsing:
    def setup_method(self):
        self.plan = vera_ingest.parse_vera_response(VERA_MARKDOWN)

    def test_finds_every_medication_despite_markdown(self):
        drugs = [m["drug"] for m in self.plan.medications]
        assert drugs == ["Prednisolone", "Ramipril", "Tacrolimus"]

    def test_extracts_the_prescribing_fields(self):
        pred = self.plan.medications[0]
        assert pred["dose"] == "1 mg/kg/day (max 80 mg)"
        assert pred["frequency"] == "once daily"
        assert pred["route"] == "PO"
        assert pred["duration"].startswith("4 weeks")
        assert "eGFR 52" in pred["renal_adjustment"]
        assert "KDIGO 2021" in pred["evidence"]
        assert "minimal change" in pred["rationale"]

    def test_assigns_line_of_therapy_from_the_heading(self):
        by_drug = {m["drug"]: m["section"] for m in self.plan.medications}
        assert by_drug["Prednisolone"] == "first_line"
        assert by_drug["Ramipril"] == "first_line"
        assert by_drug["Tacrolimus"] == "second_line"

    def test_captures_the_narrative_sections(self):
        assert any("Hepatitis B" in x for x in self.plan.pre_treatment)
        assert any("Active systemic infection" in x for x in self.plan.contraindicated)
        assert any("azole" in x for x in self.plan.interactions)
        assert any("Pneumococcal" in x for x in self.plan.vaccinations)
        assert any("abruptly" in x for x in self.plan.counselling)

    def test_counts_are_reported(self):
        counts = self.plan.counts()
        assert counts["medications"] == 3
        assert counts["contraindicated"] == 2


class TestLegacyAndEdgeCases:
    def test_still_parses_plain_label_blocks(self):
        plan = vera_ingest.parse_vera_response(
            "Drug: Cyclophosphamide\nDose: 2 mg/kg/day\nDuration: 3 months\n")
        assert len(plan.medications) == 1
        assert plan.medications[0]["dose"] == "2 mg/kg/day"

    def test_empty_response(self):
        plan = vera_ingest.parse_vera_response("")
        assert plan.is_empty
        assert plan.medications == []

    def test_prose_only_response_is_kept_not_guessed_at(self):
        text = "This patient should continue supportive care and be reviewed."
        plan = vera_ingest.parse_vera_response(text)
        assert plan.medications == []
        assert plan.unparsed  # preserved verbatim rather than invented

    def test_repeated_label_is_appended_not_lost(self):
        plan = vera_ingest.parse_vera_response(
            "Drug: Prednisolone\nMonitoring: BP weekly\nMonitoring: glucose monthly\n")
        assert plan.medications[0]["monitoring"] == "BP weekly; glucose monthly"

    def test_strip_markdown(self):
        assert vera_ingest.strip_markdown("**Dose:** 5 mg") == "Dose: 5 mg"
        assert vera_ingest.strip_markdown("[KDIGO](https://kdigo.org)") == "KDIGO"


class TestRuleData:
    def test_maps_section_to_plan_line(self):
        med = {"drug": "Tacrolimus", "dose": "0.05 mg/kg", "section": "second_line"}
        data = vera_ingest.medication_to_rule_data(
            med, disease_id="mcd", disease_name="Minimal Change Disease",
            patient_id="BGD-00001", captured_at="2026-07-27T01:53:00")
        assert data["plan_line"] == "second_line"
        assert data["drug"] == "Tacrolimus"
        assert data["disease_id"] == "mcd"

    def test_records_provenance_without_patient_name(self):
        # The knowledge base is disease-level knowledge; it must not accumulate
        # identifiable data. The registry ID is enough to trace the source.
        med = {"drug": "Prednisolone", "section": "first_line"}
        data = vera_ingest.medication_to_rule_data(
            med, disease_id="mcd", disease_name="MCD",
            patient_id="BGD-00001", captured_at="2026-07-27T01:53:00")
        assert data["provenance"]["source"] == "vera_health_ai"
        assert data["provenance"]["patient_id"] == "BGD-00001"
        assert "patient_name" not in data

    def test_unknown_section_defaults_to_first_line(self):
        data = vera_ingest.medication_to_rule_data(
            {"drug": "X", "section": ""}, disease_id="iga", disease_name="IgAN",
            patient_id="BGD-1", captured_at="2026-07-27T01:00:00")
        assert data["plan_line"] == "first_line"
