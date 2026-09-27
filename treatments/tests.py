"""
Drug-disease contraindication tests.

`CONTRANDICATION_DB` is partly keyed on drug *class* ("aminoglycoside",
"corticosteroid", "iodinated_contrast", "anti_tnf"). The matcher only knew three
alias groups, so a caller supplying a generic name — which is what the
prescription safety check does — never reached those rules. Gentamicin in CKD 4/5
produced no warning at all.
"""
from django.test import TestCase

from .contraindications import check_contraindications


class ClassKeyedRuleTests(TestCase):
    def test_aminoglycoside_member_matches_its_class_rule(self):
        for drug in ("Gentamicin", "Amikacin", "Tobramycin", "Streptomycin"):
            with self.subTest(drug=drug):
                results = check_contraindications(drug, ["CKD stage 4-5"])
                self.assertTrue(
                    any("nephrotoxic" in r.reason for r in results),
                    f"{drug} in CKD 4/5 must raise the aminoglycoside rule")

    def test_aminoglycoside_rule_is_absolute(self):
        results = check_contraindications("Gentamicin", ["CKD"])
        self.assertTrue(any(r.severity == "absolute" for r in results))

    def test_corticosteroid_member_matches_its_class_rules(self):
        cases = [
            ("Prednisolone", "Uncontrolled diabetes"),
            ("Dexamethasone", "Active peptic ulcer"),
            ("Hydrocortisone", "Glaucoma"),
            ("Methylprednisolone", "Osteoporosis"),
        ]
        for drug, disease in cases:
            with self.subTest(drug=drug, disease=disease):
                self.assertTrue(check_contraindications(drug, [disease]))

    def test_iodinated_contrast_member_matches_its_class_rule(self):
        self.assertTrue(check_contraindications("Iohexol", ["CKD stage 3"]))
        self.assertTrue(check_contraindications("Iopamidol", ["CKD stage 4-5"]))

    def test_anti_tnf_member_matches_its_class_rule(self):
        self.assertTrue(check_contraindications("Infliximab", ["Active infection"]))
        self.assertTrue(check_contraindications("Adalimumab", ["Demyelinating disease"]))

    def test_registry_class_code_alone_is_enough(self):
        # The prescription safety check also passes drug_class; a class code with
        # an unrecognised generic name must still reach the class rules.
        results = check_contraindications("Unknown brand", ["Osteoporosis"],
                                          drug_class="steroid")
        self.assertTrue(results)

    def test_no_match_without_the_relevant_disease(self):
        self.assertEqual(check_contraindications("Gentamicin", ["Diabetes"]), [])


class PreviouslyWorkingRuleTests(TestCase):
    def test_nsaid_alias_group_still_works(self):
        for drug in ("Ibuprofen", "Naproxen", "Diclofenac", "Ketorolac"):
            with self.subTest(drug=drug):
                self.assertTrue(check_contraindications(drug, ["CKD stage 4-5"]))

    def test_calcineurin_alias_group_still_works(self):
        self.assertTrue(
            check_contraindications("Tacrolimus", ["Uncontrolled hypertension"]))
        self.assertTrue(
            check_contraindications("Ciclosporin", ["Thrombotic microangiopathy"]))

    def test_sglt2_alias_group_still_works(self):
        self.assertTrue(check_contraindications("Empagliflozin", ["Recurrent UTI"]))
        self.assertTrue(
            check_contraindications("Dapagliflozin", ["Ketoacidosis risk"]))

    def test_single_drug_rules_still_works(self):
        self.assertTrue(check_contraindications("Metformin", ["CKD stage 4-5"]))
        self.assertTrue(check_contraindications("Rituximab", ["Active TB"]))
        self.assertTrue(check_contraindications("Warfarin", ["Dialysis"]))
        self.assertTrue(
            check_contraindications("Azathioprine", ["TPMT deficiency"]))


class CkdStageSpecificityTests(TestCase):
    """`normalize_disease_id` collapses "CKD stage 5" into `ckd_stage_4_5`, so
    the finer-grained `ckd_stage_5` database rules were unreachable."""

    def test_ckd_4_5_patient_triggers_the_stage_5_rule(self):
        results = check_contraindications("Empagliflozin", ["CKD stage 4-5"])
        self.assertTrue(any(r.disease == "ckd_stage_5" for r in results))

    def test_ckd_3_5_patient_triggers_the_contrast_rule(self):
        results = check_contraindications("Iohexol", ["CKD stage 3-5"])
        self.assertTrue(any(r.disease == "ckd_stage_3_5" for r in results))

    def test_dialysis_patient_triggers_the_dialysis_rule(self):
        results = check_contraindications("Warfarin", ["CKD stage 5 dialysis"])
        self.assertTrue(any(r.disease == "ckd_stage_5_dialysis" for r in results))

    def test_ckd_4_5_alone_does_not_imply_dialysis(self):
        # CKD 4/5 expands to the stage-5 and stage-3/5 rules, but a patient who
        # is not on dialysis must not pick up the dialysis-only warfarin rule.
        results = check_contraindications("Warfarin", ["CKD stage 4-5"])
        self.assertFalse(any(r.disease == "ckd_stage_5_dialysis" for r in results))
        # It does still pick up the nsaid/aminoglycoside 4-5 rules.
        self.assertTrue(check_contraindications("Ibuprofen", ["CKD stage 4-5"]))

    def test_normal_kidney_function_does_not_trigger(self):
        self.assertEqual(check_contraindications("Empagliflozin", ["Diabetes"]), [])
