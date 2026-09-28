"""KDIGO guideline compliance validation for management plans."""

import pytest
from clinical_reasoning.services.management_plan.registry import ProfileRegistry


class TestKdigoCompliance:
    """Verify all disease profiles contain valid KDIGO references."""

    DISEASES_WITH_PLANS = [
        "iga", "membranous", "lupus", "anca", "diabeticNephropathy",
        "fsgs", "mcd", "c3",
    ]

    def test_all_profiles_have_first_line(self):
        for key in self.DISEASES_WITH_PLANS:
            profile = ProfileRegistry.get(key)
            assert profile is not None, f"No profile registered for {key}"
            assert "first_line" in profile, (
                f"{key} profile missing first_line"
            )
            assert len(profile["first_line"]) > 0, (
                f"{key} profile has empty first_line"
            )

    def test_all_profiles_have_guideline_refs(self):
        for key in self.DISEASES_WITH_PLANS:
            profile = ProfileRegistry.get(key)
            assert profile is not None
            refs = profile.get("guideline_refs", [])
            if not refs:
                continue
            for ref in refs:
                assert "KDIGO" in ref or "ERA" in ref or "CKD" in ref, (
                    f"{key} has unrecognised guideline ref: {ref}"
                )

    def _drugs(self, key):
        profile = ProfileRegistry.get(key)
        return [item["drug"] if isinstance(item, dict) else item
                for item in profile["first_line"]]

    def test_iga_first_line_contains_raas_blockade(self):
        drugs = self._drugs("iga")
        drug_text = " ".join(drugs).lower()
        assert any(kw in drug_text for kw in ("raas", "ace", "arb", "acei")), (
            f"IgA first-line should recommend RAAS blockade, got drugs: {drugs}"
        )

    def test_membranous_first_line_contains_immunosuppression(self):
        drugs = self._drugs("membranous")
        drug_text = " ".join(drugs).lower()
        assert any(kw in drug_text for kw in (
            "rituximab", "mycophenolate", "cyclophosphamide",
            "calcineurin", "cni",
        )), f"Membranous first-line missing immunosuppression, got drugs: {drugs}"

    def test_lupus_first_line_contains_induction(self):
        drugs = self._drugs("lupus")
        drug_text = " ".join(drugs).lower()
        assert any(kw in drug_text for kw in (
            "mycophenolate", "cyclophosphamide", "steroid", "prednisone",
        )), f"Lupus first-line missing induction therapy, got drugs: {drugs}"
