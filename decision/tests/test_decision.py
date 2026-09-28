"""
Clinical calculator tests for the decision-support API.

The eGFR check is a parity test against `labs.services.egfr` — the
implementation whose output is stored on every derived `LabResult` and consumed
by every analytic. A calculator that disagrees with the stored value can move a
patient across a CKD stage boundary, so the two must never diverge.
"""
from django.test import TestCase

from labs.services.egfr import ckd_epi_2021

from ..services import (
    egfr_ckd_epi_2021,
    kdigo_heatmap_point,
    renal_dose_adjustment,
)


class EgfrCalculatorTests(TestCase):
    def test_matches_the_stored_ckd_epi_2021_value(self):
        # Male, Scr 0.5, age 45: 123.7 under the 2021 equation.
        cases = [
            (0.5, 45, "M"), (0.6, 50, "M"), (0.9, 60, "M"), (3.0, 70, "M"),
            (0.4, 30, "F"), (0.8, 50, "F"), (1.01, 70, "F"), (2.0, 65, "F"),
        ]
        for scr, age, sex in cases:
            with self.subTest(scr=scr, age=age, sex=sex):
                expected = round(ckd_epi_2021(scr, age, sex)[0], 1)
                self.assertAlmostEqual(
                    egfr_ckd_epi_2021(scr, age, sex), expected, places=1)

    def test_does_not_use_the_2009_coefficients(self):
        # Replaced 2026-09-27 (entry-linkage review): the 2021 equation uses
        # alpha -0.302 for males (NIDDK). The previous assertion (123.7)
        # pinned the defective shared -0.241 alpha and wrongly attributed
        # -0.302 to the 2009 equation (which used -0.411 and gives ~131 here).
        self.assertEqual(egfr_ckd_epi_2021(0.5, 45, "M"), 128.2)
        # Female, Scr 1.01, age 70: 59.9 (G3a). The 2009 constants gave 60.2 (G2).
        self.assertEqual(egfr_ckd_epi_2021(1.01, 70, "F"), 59.9)

    def test_registry_sex_codes_and_words_agree(self):
        self.assertEqual(egfr_ckd_epi_2021(0.8, 50, "F"),
                         egfr_ckd_epi_2021(0.8, 50, "female"))
        self.assertEqual(egfr_ckd_epi_2021(0.8, 50, "M"),
                         egfr_ckd_epi_2021(0.8, 50, "male"))

    def test_non_positive_creatinine_returns_zero(self):
        self.assertEqual(egfr_ckd_epi_2021(0, 50, "M"), 0.0)
        self.assertEqual(egfr_ckd_epi_2021(-1, 50, "M"), 0.0)


class RenalDoseTests(TestCase):
    """The table is keyed on drug identity; callers pass the registry
    `drug_class` code, so a name-keyed lookup missed every code row and returned
    full dose where the table advises a reduction."""

    def test_registry_class_code_reaches_the_dosing_row(self):
        r = renal_dose_adjustment("mmf", 25)
        self.assertEqual(r["dose_pct"], 25)
        self.assertIn("25%", r["adjustment"])

    def test_calcineurin_class_code_reaches_the_dosing_row(self):
        for drug in ("cni", "tacrolimus", "ciclosporin", "cyclosporin"):
            with self.subTest(drug=drug):
                self.assertEqual(renal_dose_adjustment(drug, 25)["dose_pct"], 25)

    def test_no_reduction_needed_above_the_threshold(self):
        self.assertEqual(renal_dose_adjustment("mmf", 70)["dose_pct"], 100)
        self.assertEqual(renal_dose_adjustment("doxycycline", 40)["dose_pct"], 100)

    def test_cni_table_has_no_no_adjustment_row(self):
        # Documented as-is: the CNI rows start at 50%, so a tacrolimus patient
        # at eGFR 45 is advised a 50% dose. Flagged for clinical review rather
        # than changed here — the table is the clinical source of truth.
        self.assertEqual(renal_dose_adjustment("cni", 45)["dose_pct"], 50)

    def test_unknown_drug_returns_the_requested_dose_with_advice(self):
        r = renal_dose_adjustment("unknown_thing", 25)
        self.assertEqual(r["dose_pct"], 100)
        self.assertIn("consult pharmacist", r["adjustment"])

    def test_class_code_without_guidance_is_not_silently_dosed(self):
        r = renal_dose_adjustment("sglt2i", 25)
        self.assertIn("consult pharmacist", r["adjustment"])


class KdigoHeatmapTests(TestCase):
    """KDIGO 2024 heat map. The old grid mapped G3a and G3b to the same bucket
    and used 0.15/3.5 albuminuria boundaries, mis-tiering several cells."""

    def test_green_only_for_g1_g2_with_a1(self):
        self.assertEqual(kdigo_heatmap_point(95, 0.2)["color"], "green")
        self.assertEqual(kdigo_heatmap_point(65, 0.1)["color"], "green")

    def test_yellow_cells(self):
        for egfr, upcr in [(95, 1.0), (65, 0.5), (50, 0.2)]:
            with self.subTest(egfr=egfr, upcr=upcr):
                self.assertEqual(kdigo_heatmap_point(egfr, upcr)["color"], "yellow")

    def test_orange_cells(self):
        for egfr, upcr in [(95, 3.2), (50, 1.0), (35, 0.2)]:
            with self.subTest(egfr=egfr, upcr=upcr):
                self.assertEqual(kdigo_heatmap_point(egfr, upcr)["color"], "orange")

    def test_red_cells(self):
        for egfr, upcr in [(50, 3.5), (35, 1.0), (22, 0.2), (20, 3.0), (10, 0.1)]:
            with self.subTest(egfr=egfr, upcr=upcr):
                self.assertEqual(kdigo_heatmap_point(egfr, upcr)["color"], "red")

    def test_g3a_and_g3b_are_distinct_zones(self):
        self.assertEqual(kdigo_heatmap_point(50, 0.2)["egfr_zone"], "G3a")
        self.assertEqual(kdigo_heatmap_point(35, 0.2)["egfr_zone"], "G3b")
        # Same albuminuria, different risk.
        self.assertNotEqual(kdigo_heatmap_point(50, 0.2)["color"],
                            kdigo_heatmap_point(35, 0.2)["color"])

    def test_albuminuria_zones_use_kdigo_boundaries(self):
        self.assertEqual(kdigo_heatmap_point(95, 0.29)["proteinuria_zone"], "A1")
        self.assertEqual(kdigo_heatmap_point(95, 0.3)["proteinuria_zone"], "A2")
        self.assertEqual(kdigo_heatmap_point(95, 3.0)["proteinuria_zone"], "A2")
        self.assertEqual(kdigo_heatmap_point(95, 3.1)["proteinuria_zone"], "A3")
