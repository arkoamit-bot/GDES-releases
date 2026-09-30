"""import_dkdr_drugs: additive brand merge from a DKDR checkout."""
import csv
import io
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase

from treatments.models import DrugMaster

from .management.commands.import_dkdr_drugs import clean_strength

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
