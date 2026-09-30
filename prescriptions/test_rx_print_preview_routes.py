"""Printing, the preview frame, and the route a drug is offered by.

Named test_*.py on purpose: pytest.ini sets `python_files = test_*.py`, so a
file called tests.py is never collected by the project's own pytest run.
"""
import datetime as dt
import io

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from encounters.models import ClinicalEncounter
from patients.models import Patient
from treatments.models import DrugClass, DrugMaster

from .models import Prescription, PrescriptionItem

# Column order `import_bddrugbank`'s DictReader expects.
CSV_HEADER = ["name", "generic_name", "strength", "therapeutic_class",
              "company", "dosage_form", "medex_url"]

User = get_user_model()

class PrintPageTests(TestCase):
    """Print must not go through the preview page: printing the slip inside an
    iframe under the app layout gave blank pages on real printers."""

    def setUp(self):
        self.user = User.objects.create_user("printer", password="pw")
        self.client.force_login(self.user)
        p = Patient.objects.create(patient_id="BGD-0950", name="Print User", sex="F")
        enc = ClinicalEncounter.objects.create(
            patient=p, encounter_date=dt.date(2026, 9, 1),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)
        self.rx = Prescription.objects.create(encounter=enc)
        PrescriptionItem.objects.create(
            prescription=self.rx, sort_order=1,
            drug=DrugMaster.objects.create(generic_name="Ramipril",
                                           drug_class=DrugClass.RAASI))

    def test_print_page_is_the_slip_alone_and_opens_print(self):
        resp = self.client.get(reverse("prescriptions:print", args=[self.rx.pk]))
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        self.assertIn("Ramipril", html)
        self.assertIn("window.print()", html)
        self.assertNotIn("<iframe", html)
        self.assertNotIn("sidebar", html.lower())

    def test_print_page_needs_login(self):
        self.client.logout()
        resp = self.client.get(reverse("prescriptions:print", args=[self.rx.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_preview_print_button_opens_the_print_page_not_the_frame(self):
        resp = self.client.get(reverse("prescriptions:preview", args=[self.rx.pk]))
        html = resp.content.decode()
        self.assertIn(reverse("prescriptions:print", args=[self.rx.pk]), html)
        self.assertNotIn("contentWindow.print", html)

class DosageFormRouteTests(TestCase):
    """The catalogue's dosage_form is the only place most products say how
    they are given. Reading it wrong prints a wrong route on a prescription,
    so an ambiguous form must claim nothing."""

    def _r(self, form):
        from .management.commands.import_bddrugbank import routes_from_dosage_form
        return sorted(str(x) for x in routes_from_dosage_form(form))

    def test_parenteral_forms_that_name_their_route(self):
        self.assertEqual(self._r("IV Injection"), ["IV"])
        self.assertEqual(self._r("IV Injection or Infusion"), ["IV"])
        self.assertEqual(self._r("IM/IV Injection"), ["IM", "IV"])
        self.assertEqual(self._r("IV/SC Injection"), ["IV", "SC"])
        self.assertEqual(self._r("SC Injection"), ["SC"])

    def test_ambiguous_forms_claim_nothing(self):
        for form in ("Injection", "Infusion", "Solution", "Drops",
                     "Nasal Spray", "Mouthwash", "Dialysis Solution", ""):
            self.assertEqual(self._r(form), [], form)

    def test_local_forms_win_over_the_oral_word_they_contain(self):
        self.assertEqual(self._r("Vaginal Tablet"), [])
        self.assertEqual(self._r("Eye Capsule"), ["TOP"])
        self.assertEqual(self._r("Inhalation Capsule"), ["INH"])
        self.assertEqual(self._r("Ophthalmic Suspension"), ["TOP"])
        self.assertEqual(self._r("Nebuliser Suspension"), ["INH"])
        self.assertEqual(self._r("Suppository"), ["PR"])

    def test_oral_forms(self):
        for form in ("Tablet", "Capsule (Enteric Coated)", "Syrup",
                     "Powder for Suspension", "Oral Solution",
                     "Chewable Tablet", "Paediatric Drops"):
            self.assertEqual(self._r(form), ["PO"], form)

class ImportRouteFromDosageFormTests(TestCase):
    """An injection-only drug must not be offered, or printed, as oral."""

    def _import(self, rows):
        import csv as _csv
        import os
        import tempfile
        from django.core.management import call_command
        fd, path = tempfile.mkstemp(suffix=".csv")
        os.close(fd)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = _csv.writer(fh)
            w.writerow(CSV_HEADER)
            w.writerows(rows)
        import io
        call_command("import_bddrugbank", path, stdout=io.StringIO(),
                     stderr=io.StringIO())
        os.unlink(path)

    def test_injection_only_drug_gets_its_route_not_po(self):
        self._import([
            ["Carbanem", "Meropenem", "1 gm/vial", "", "X", "IV Injection", ""],
            ["Meronem", "Meropenem", "500 mg/vial", "", "Y",
             "IV Injection or Infusion", ""],
        ])
        d = DrugMaster.objects.get(generic_name="Meropenem")
        self.assertEqual(d.available_routes, ["IV"])
        self.assertEqual(d.default_route, "IV")
        self.assertEqual(d.routes, ["IV"])

    def test_a_drug_sold_orally_and_iv_keeps_po_as_default(self):
        self._import([
            ["Napa", "Paracetamol", "500 mg", "", "X", "Tablet", ""],
            ["Napa IV", "Paracetamol", "1 gm/100 ml", "", "X", "IV Infusion", ""],
        ])
        d = DrugMaster.objects.get(generic_name="Paracetamol")
        self.assertEqual(sorted(d.available_routes), ["IV", "PO"])
        self.assertEqual(d.default_route, "PO")

    def test_a_curated_route_is_never_replaced(self):
        DrugMaster.objects.create(generic_name="Insulin Human",
                                  default_route="SC", available_routes=["SC"])
        self._import([["Humulin", "Insulin Human", "100 IU/ml", "", "X",
                       "Injection", ""]])
        d = DrugMaster.objects.get(generic_name="Insulin Human")
        self.assertEqual(d.default_route, "SC")

    def test_an_ambiguous_form_leaves_the_route_unasserted(self):
        self._import([["Rocephin", "Ceftriaxone", "1 gm/vial", "", "X",
                       "Injection", ""]])
        d = DrugMaster.objects.get(generic_name="Ceftriaxone")
        self.assertEqual(d.available_routes, [])

    def test_a_catalogue_derived_default_is_recomputed_not_inherited(self):
        """Paracetamol sat at default IV because an "(IV Infusion)" name
        reached it before any oral form; merging must recompute the default,
        not keep whatever an earlier import stored first."""
        DrugMaster.objects.create(generic_name="Paracetamol",
                                  default_route="IV", available_routes=["IV"])
        self._import([
            ["Napa", "Paracetamol", "500 mg", "", "X", "Tablet", ""],
            ["Napa IV", "Paracetamol", "1 gm/100 ml", "", "X", "IV Infusion", ""],
        ])
        d = DrugMaster.objects.get(generic_name="Paracetamol")
        self.assertEqual(d.default_route, "PO")
        self.assertEqual(d.available_routes, ["PO", "IV"])

    def test_a_seeded_route_list_keeps_its_own_order_and_default(self):
        from .management.commands.import_bddrugbank import CURATED_ROUTES
        self.assertIn("Cyclophosphamide", CURATED_ROUTES)
        DrugMaster.objects.create(generic_name="Cyclophosphamide",
                                  default_route="PO",
                                  available_routes=["PO", "IV"])
        self._import([["Endoxan", "Cyclophosphamide", "500 mg/vial", "", "X",
                       "IV Injection", ""]])
        d = DrugMaster.objects.get(generic_name="Cyclophosphamide")
        self.assertEqual(d.available_routes, ["PO", "IV"])
        self.assertEqual(d.default_route, "PO")

    def test_iv_leads_im_when_the_drug_is_parenteral_only(self):
        self._import([["Rocephin", "Ceftriaxone", "1 gm/vial", "", "X",
                       "IM/IV Injection", ""]])
        d = DrugMaster.objects.get(generic_name="Ceftriaxone")
        self.assertEqual(d.available_routes, ["IV", "IM"])
        self.assertEqual(d.default_route, "IV")

class PreviewIframeTests(TestCase):
    """The preview embeds the slip in an iframe via srcdoc. render_to_string
    returns a SafeString, so the slip went in unescaped and its first
    `lang="en"` closed the attribute: an empty frame, and blank printed pages.
    """

    def setUp(self):
        self.user = User.objects.create_user("previewer", password="pw")
        self.client.force_login(self.user)
        p = Patient.objects.create(patient_id="BGD-0960", name="Frame User",
                                   sex="M")
        enc = ClinicalEncounter.objects.create(
            patient=p, encounter_date=dt.date(2026, 9, 1),
            encounter_type=ClinicalEncounter.Type.FOLLOWUP)
        self.rx = Prescription.objects.create(encounter=enc)
        PrescriptionItem.objects.create(
            prescription=self.rx, sort_order=1,
            drug=DrugMaster.objects.create(generic_name="Meropenem",
                                           default_route="IV"))

    def _srcdoc(self):
        html = self.client.get(
            reverse("prescriptions:preview", args=[self.rx.pk])).content.decode()
        i = html.index('srcdoc="') + len('srcdoc="')
        return html[i:html.index('"', i)]

    def test_srcdoc_holds_the_whole_slip_escaped(self):
        doc = self._srcdoc()
        self.assertIn("&lt;!DOCTYPE html&gt;", doc)
        self.assertIn("Meropenem", doc)
        self.assertIn("rx-table", doc)
        # The truncation bug left 27 characters.
        self.assertGreater(len(doc), 3000)

    def test_srcdoc_contains_no_bare_quote_to_close_the_attribute(self):
        self.assertNotIn('"', self._srcdoc())
