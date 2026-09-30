"""import_dkdr_drugs: additive brand merge from a DKDR checkout."""
import csv
import io
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from treatments.models import DrugClass, DrugMaster

from .management.commands.import_dkdr_drugs import (build_salt_index, clean_strength,
                                                    fold_salt_variant)

BD_MED_HEADER = ["brand id", "brand name", "type", "slug", "dosage form",
                 "generic", "strength", "manufacturer", "package container",
                 "Package Size"]
REGISTRY_HEADER = ["FORM_DESC", "FORM", "GENERIC_NAME", "TRADE_NAME",
                   "STRENGTH", "DRUG_ITEM_ID"]


def _med(brand, generic, strength, type_="allopathic"):
    return {"brand id": "1", "brand name": brand, "type": type_, "slug": "",
            "dosage form": "Tablet", "generic": generic, "strength": strength,
            "manufacturer": "X", "package container": "", "Package Size": ""}


def _reg(brand, generic, strength):
    return {"FORM_DESC": "Tablet", "FORM": "Tab.", "GENERIC_NAME": generic,
            "TRADE_NAME": brand, "STRENGTH": strength, "DRUG_ITEM_ID": "01-1"}


def _write(path, header, rows, delimiter=","):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, delimiter=delimiter)
        w.writeheader()
        w.writerows(rows)


class CleanStrengthTests(TestCase):
    def test_spacing_and_combinations_match_medex_style(self):
        self.assertEqual(clean_strength("30mg"), "30 mg")
        self.assertEqual(clean_strength("125mg/5ml"), "125 mg/5 ml")
        self.assertEqual(clean_strength("325mg + 37.5mg"), "325 mg+37.5 mg")
        self.assertEqual(clean_strength("500 mg+400 IU"), "500 mg+400 IU")

    def test_pack_descriptions_are_dropped(self):
        self.assertEqual(clean_strength("5's pack"), "")
        self.assertEqual(clean_strength(""), "")


class ImportDkdrDrugsTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        data = Path(self._tmp.name) / "data"
        (data / "bd_med").mkdir(parents=True)
        (data / "brand_registry").mkdir(parents=True)
        _write(data / "bd_med" / "medicine.csv", BD_MED_HEADER, [
            _med("Cardace", "Ramipril", "5 mg"),
            _med("Newpril", "Ramipril", "10 mg"),
            _med("Herbo", "Ramipril", "5 mg", type_="herbal"),
            _med("Elsewhere", "Unknownium", "5 mg"),
        ])
        _write(data / "brand_registry" / "drugs.xls", REGISTRY_HEADER, [
            _reg("Regpril", "Ramipril", "2.5mg"),
            _reg("Packpril", "Ramipril", "5's pack"),
        ], delimiter="\t")
        self.dkdr = self._tmp.name
        self.ramipril = DrugMaster.objects.create(
            generic_name="Ramipril", brand_names=["Cardace", "Tritace"],
            available_strengths=["5 mg"])

    def _run(self, *args):
        out = io.StringIO()
        call_command("import_dkdr_drugs", "--dkdr-dir", self.dkdr, *args,
                     stdout=out, stderr=io.StringIO())
        return out.getvalue()

    def test_dry_run_writes_nothing(self):
        self._run("--dry-run")
        self.ramipril.refresh_from_db()
        self.assertEqual(self.ramipril.brand_names, ["Cardace", "Tritace"])

    def test_merges_brands_and_strengths_additively(self):
        self._run()
        self.ramipril.refresh_from_db()
        self.assertEqual(self.ramipril.brand_names[:2], ["Cardace", "Tritace"])
        self.assertIn("Newpril", self.ramipril.brand_names)
        self.assertIn("Regpril", self.ramipril.brand_names)
        self.assertEqual(sorted(self.ramipril.available_strengths),
                         ["10 mg", "2.5 mg", "5 mg"])

    def test_herbal_and_pack_rows_are_not_imported(self):
        self._run()
        self.ramipril.refresh_from_db()
        self.assertNotIn("Herbo", self.ramipril.brand_names)
        self.assertNotIn("5's pack", self.ramipril.available_strengths)

    def test_unmatched_generics_are_reported_not_created(self):
        report = Path(self._tmp.name) / "unmatched.csv"
        self._run("--report", str(report))
        self.assertFalse(DrugMaster.objects.filter(
            generic_name="Unknownium").exists())
        self.assertIn("Unknownium", report.read_text(encoding="utf-8"))

    def test_create_generics_opts_in(self):
        self._run("--create-generics")
        self.assertTrue(DrugMaster.objects.filter(
            generic_name="Unknownium").exists())

    def test_is_idempotent(self):
        self._run()
        self.ramipril.refresh_from_db()
        first = list(self.ramipril.brand_names)
        self._run()
        self.ramipril.refresh_from_db()
        self.assertEqual(self.ramipril.brand_names, first)


class BddrugbankZipTests(ImportDkdrDrugsTests):
    def test_zip_brands_and_therapeutic_class_are_imported(self):
        import zipfile
        z = Path(self.dkdr) / "data" / "bddrugbank"
        z.mkdir()
        buf = io.StringIO(newline="")
        w = csv.DictWriter(buf, fieldnames=["name", "generic_name", "strength",
                                            "therapeutic_class", "manufacturer",
                                            "dosage_form"])
        w.writeheader()
        w.writerow({"name": "Zipril", "generic_name": "Ramipril",
                    "strength": "1.25 mg", "therapeutic_class": "ACE inhibitors",
                    "manufacturer": "X", "dosage_form": "Tablet"})
        w.writerow({"name": "Znew", "generic_name": "Statinomab",
                    "strength": "5 mg", "therapeutic_class": "",
                    "manufacturer": "X", "dosage_form": "Tablet"})
        with zipfile.ZipFile(z / "BDDrugBank_test.zip", "w") as zf:
            zf.writestr("medex_merged.csv", buf.getvalue())
        self._run("--create-generics")
        self.ramipril.refresh_from_db()
        self.assertIn("Zipril", self.ramipril.brand_names)
        self.assertIn("1.25 mg", self.ramipril.available_strengths)
        self.assertTrue(DrugMaster.objects.filter(generic_name="Statinomab").exists())


class SaltFoldTests(TestCase):
    def _index(self, *names):
        return build_salt_index(names)

    def test_salt_only_difference_folds_either_way(self):
        idx = self._index("Cefixime Trihydrate", "Pantoprazole")
        self.assertEqual(fold_salt_variant("Cefixime", idx), "Cefixime Trihydrate")
        self.assertEqual(
            fold_salt_variant("Pantoprazole Sodium Sesquihydrate", idx),
            "Pantoprazole")

    def test_combinations_never_fold_or_count_as_targets(self):
        idx = self._index("Amoxicillin + Clavulanic Acid")
        self.assertIsNone(fold_salt_variant("Amoxicillin", idx))
        self.assertIsNone(fold_salt_variant(
            "Amlodipine + Atenolol",
            self._index("Amlodipine Besilate + Atenolol")))

    def test_a_different_molecule_is_not_a_salt(self):
        idx = self._index("Metformin Hydrochloride")
        self.assertIsNone(fold_salt_variant("Metformin Glibenclamide", idx))
        self.assertIsNone(fold_salt_variant("Meta", idx))

    def test_form_tags_and_more_salts(self):
        idx = self._index("Clobetasol Propionate", "Escitalopram Oxalate",
                          "Tobramycin")
        self.assertEqual(fold_salt_variant("Clobetasol Propionate 0.05% topical",
                                           idx), "Clobetasol Propionate")
        self.assertEqual(fold_salt_variant("Escitalopram", idx),
                         "Escitalopram Oxalate")
        self.assertEqual(fold_salt_variant("Tobramycin Eye prep", idx),
                         "Tobramycin")

    def test_a_bare_ion_is_not_a_salt_variant(self):
        idx = self._index("Calcium Carbonate", "Sodium Chloride")
        self.assertIsNone(fold_salt_variant("Calcium", idx))
        self.assertIsNone(fold_salt_variant("Sodium", idx))

    def test_ambiguity_is_left_alone(self):
        idx = self._index("Cefuroxime Axetil", "Cefuroxime Sodium")
        self.assertIsNone(fold_salt_variant("Cefuroxime", idx))


class FoldSaltsCommandTests(ImportDkdrDrugsTests):
    def test_new_insulin_generics_are_created_as_insulin(self):
        data = Path(self.dkdr) / "data"
        _write(data / "bd_med" / "medicine.csv", BD_MED_HEADER,
               [_med("Insu", "Insulin Degludec", "100 IU/ml")])
        self._run("--create-generics", "--fold-salts")
        row = DrugMaster.objects.get(generic_name="Insulin Degludec")
        self.assertEqual(row.drug_class, DrugClass.INSULIN)

    def test_fold_salts_avoids_a_twin_row(self):
        DrugMaster.objects.create(generic_name="Cefixime Trihydrate",
                                  brand_names=["Old"])
        data = Path(self.dkdr) / "data"
        _write(data / "bd_med" / "medicine.csv", BD_MED_HEADER,
               [_med("Fixo", "Cefixime", "200 mg")])
        self._run("--create-generics", "--fold-salts")
        self.assertFalse(DrugMaster.objects.filter(
            generic_name="Cefixime").exists())
        self.assertIn("Fixo", DrugMaster.objects.get(
            generic_name="Cefixime Trihydrate").brand_names)


class ClassifyDrugFalsePositiveTests(TestCase):
    def _cls(self, name, tc=()):
        from .management.commands.import_bddrugbank import classify_drug
        return classify_drug(name, list(tc))

    def test_statin_suffix_is_not_a_bare_substring(self):
        for name in ("Nystatin", "Somatostatin", "Imipenem + Cilastatin"):
            self.assertNotEqual(self._cls(name), DrugClass.STATIN, name)
        self.assertEqual(self._cls("Atorvastatin Calcium"), DrugClass.STATIN)
        self.assertEqual(self._cls("Pitavastatin"), DrugClass.STATIN)
        self.assertEqual(self._cls("Ezetimibe", ["HMG-CoA (Statins)"]),
                         DrugClass.STATIN)

    def test_local_and_combination_steroids_and_cnis_are_other(self):
        for name in ("Betamethasone valerate 0.01% Topical",
                     "Acyclovir + Hydrocortisone",
                     "Tobramycin + Dexamethasone Eye prep",
                     "Tacrolimus 0.1%, 0.03% Topical"):
            self.assertEqual(self._cls(name), DrugClass.OTHER, name)

    def test_two_salts_of_one_steroid_stay_systemic(self):
        self.assertEqual(
            self._cls("Betamethasone Sodium Phosphate + Betamethasone Acetate"),
            DrugClass.STEROID)

    def test_systemic_single_ingredient_classes_are_unchanged(self):
        self.assertEqual(self._cls("Prednisolone"), DrugClass.STEROID)
        self.assertEqual(self._cls("Tacrolimus"), DrugClass.CNI)
        self.assertEqual(self._cls("Amlodipine + Telmisartan"), DrugClass.RAASI)


class ReclassifyCommandTests(TestCase):
    def setUp(self):
        self.bad = DrugMaster.objects.create(
            generic_name="Nystatin", drug_class=DrugClass.STATIN)
        self.topical = DrugMaster.objects.create(
            generic_name="Betamethasone 0.1% + Neomycin Topical",
            drug_class=DrugClass.STEROID)
        self.good = DrugMaster.objects.create(
            generic_name="Rosuvastatin", drug_class=DrugClass.STATIN)
        # Class came from the therapeutic class, not the name: not ours to move.
        self.by_tc = DrugMaster.objects.create(
            generic_name="Ezetimibe", drug_class=DrugClass.STATIN)

    def _run(self, *args):
        out = io.StringIO()
        call_command("reclassify_drug_classes", *args, stdout=out)
        return out.getvalue()

    def test_report_only_by_default(self):
        self.assertIn("Would change 2", self._run())
        self.bad.refresh_from_db()
        self.assertEqual(self.bad.drug_class, DrugClass.STATIN)

    def test_apply_moves_only_false_positives(self):
        self._run("--apply")
        for row, expected in ((self.bad, DrugClass.OTHER),
                              (self.topical, DrugClass.OTHER),
                              (self.good, DrugClass.STATIN),
                              (self.by_tc, DrugClass.STATIN)):
            row.refresh_from_db()
            self.assertEqual(row.drug_class, expected, row.generic_name)
        self.assertIn("Would change 0", self._run())


class SpellingVariantCreationTests(TestCase):
    def test_two_spellings_of_a_new_generic_make_one_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            (data / "bd_med").mkdir(parents=True)
            (data / "brand_registry").mkdir(parents=True)
            _write(data / "bd_med" / "medicine.csv", BD_MED_HEADER, [
                _med("Aa", "Losartan potassium", "50 mg"),
                _med("Bb", "Losartan Potassium", "100 mg"),
            ])
            _write(data / "brand_registry" / "drugs.xls", REGISTRY_HEADER, [],
                   delimiter="\t")
            call_command("import_dkdr_drugs", "--dkdr-dir", tmp,
                         "--create-generics", stdout=io.StringIO(),
                         stderr=io.StringIO())
        rows = DrugMaster.objects.filter(generic_name__icontains="losartan")
        self.assertEqual(rows.count(), 1)
        self.assertEqual(sorted(rows[0].brand_names), ["Aa", "Bb"])


class BundleTests(ImportDkdrDrugsTests):
    def test_bundle_round_trip_matches_a_checkout_import(self):
        bundle = Path(self.dkdr) / "b.csv.gz"
        self._run("--write-bundle", str(bundle))
        self.ramipril.refresh_from_db()
        self.assertEqual(self.ramipril.brand_names, ["Cardace", "Tritace"])

        self._run("--bundle", str(bundle), "--create-generics")
        via_bundle = DrugMaster.objects.get(pk=self.ramipril.pk)
        self.assertIn("Regpril", via_bundle.brand_names)
        self.assertIn("Newpril", via_bundle.brand_names)
        self.assertNotIn("Herbo", via_bundle.brand_names)
        self.assertTrue(DrugMaster.objects.filter(
            generic_name="Unknownium").exists())

    def test_shipped_bundle_exists_and_reads(self):
        from .management.commands.import_dkdr_drugs import (BUNDLE_PATH,
                                                            _read_bundle)
        self.assertTrue(BUNDLE_PATH.exists(), BUNDLE_PATH)
        first = next(iter(_read_bundle(BUNDLE_PATH)))
        self.assertTrue(first["generic_name"] and first["name"])


class DrugBundleGateTests(TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        from django.test import override_settings
        ctx = override_settings(BGDDR_DATA_DIR=Path(self._tmp.name))
        ctx.enable()
        self.addCleanup(ctx.disable)

    def test_applies_once_then_is_stamped(self):
        from unittest import mock

        from prescriptions import drug_bundle
        with mock.patch("django.core.management.call_command") as cc:
            self.assertTrue(drug_bundle.apply_if_newer(log=lambda *_: None))
            self.assertEqual(cc.call_count, 2)
            self.assertEqual(drug_bundle.installed_version(),
                             drug_bundle.BUNDLE_VERSION)
            self.assertFalse(drug_bundle.apply_if_newer(log=lambda *_: None))
            self.assertEqual(cc.call_count, 2)

    def test_a_failed_import_is_retried_next_launch(self):
        from unittest import mock

        from prescriptions import drug_bundle
        with mock.patch("django.core.management.call_command",
                        side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                drug_bundle.apply_if_newer(log=lambda *_: None)
        self.assertIsNone(drug_bundle.installed_version())
        self.assertTrue(drug_bundle.should_apply())


class CommandParsersTests(TestCase):
    def test_every_management_command_builds_its_parser(self):
        """Python 3.14 rejects a lone "%" in argparse help when the option is
        added, so a bad help string breaks the command outright in the packaged
        app - including the weekly MedEx sync, which calls import_bddrugbank."""
        from django.core.management import get_commands, load_command_class
        for name, app in get_commands().items():
            with self.subTest(command=name):
                load_command_class(app, name).create_parser("manage.py", name)
