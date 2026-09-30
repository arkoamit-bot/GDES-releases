"""
Import BDDrugBank / MedEx generics and brand names into DrugMaster.

Usage:
    python manage.py import_bddrugbank Imports/medex_brands.csv [--dry-run] [--limit N]

- Existing DrugMaster generics get new Bangladeshi brand names and strengths
  merged in (deduped; brand names and strengths are additive).
- DrugClass is upgraded where the BDDrugBank therapeutic class or generic
  name confirms a known research class (e.g. an "OTHER" row whose BD
  therapeutic class says "Statins").
- New generics not matching any existing row are created with DrugClass.OTHER
  and receive all BD brand names + strengths.
- Mechanism: normalized match on generic name, plus a curated synonym
  dictionary for salt-form variants (e.g. "Metformin Hydrochloride" ->
  "Metformin"). Combination products and different drugs that share a word
  are NOT merged - they get their own DrugMaster row.

MedEx naming conventions this import reconciles
----------------------------------------------
MedEx does not key brands on a bare INN generic. It files them under a
"generic" string that often carries a formulation or indication qualifier:

    Budesonide (Inhaler)          -> Budesonide      route INH
    Cyclosporine (Ophthalmic)     -> Cyclosporine    route TOP
    Acyclovir (Oral)              -> Acyclovir       route PO
    Zoledronic Acid [For osteoporosis] -> Zoledronic acid

Left alone these become near-duplicate rows and the real formulary entry
stops receiving brands, so the qualifier is folded onto the base generic and
- where it names a route unambiguously - recorded in `available_routes` /
`strengths_by_route`. Where it does not (bare "Injection", "MUPS
preparation", a strength in brackets) the suffix is dropped but no route is
asserted, so nothing is mislabelled.

Non-medicines (devices, consumables) are dropped: they can never be
prescribed and only clutter the drug picker. Cosmetics are kept.

The import is a merge, never a replace: curated formulary data (dose,
frequency, routes, safety flags, and the most-used brand names in
`seed_drugs.DRUGS`) is preserved, and scraped brands are appended after it.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from treatments.models import DrugClass, DrugMaster, Route

# Curated, most-used-first brand lists for the research formulary. The
# prescription form auto-selects brand_names[0] and persists it as the drug's
# display name on the printed prescription and in FHIR exports, so scraped
# brands (sorted alphabetically) must not displace these.
try:
    from prescriptions.management.commands.seed_drugs import DRUGS as _SEED_DRUGS
    CURATED_BRANDS = {row[0]: list(row[4]) for row in _SEED_DRUGS}
    # Formulary drugs whose route list the seed states explicitly; there the
    # first entry IS the intended default and the catalogue must not move it.
    CURATED_ROUTES = {row[0]: list(row[7]) for row in _SEED_DRUGS if row[7]}
except Exception:  # pragma: no cover - seed module is optional at runtime
    CURATED_BRANDS = {}
    CURATED_ROUTES = {}

# Model field limits. PrescriptionItem.brand is max_length=120, and
# PrescriptionItem.strength/dose are max_length=120 too (widened from 40 because
# combination products carry multi-ingredient strings like
# "1000 mg+327 mg (Conventional calcium)+500 mg+400 IU").
MAX_GENERIC = 120
MAX_BRAND = 120
MAX_STRENGTH = 120

# MedEx dosage-form / generic-suffix qualifiers that name a route
# unambiguously, mapped to the app's Route vocabulary. Anything NOT listed
# here is still folded off the generic name but never assigned a route:
# a bare "Injection" could be IV, IM or SC, "Nasal Spray" is intranasal
# rather than inhaled, and "Vaginal Pessary" is not rectal.
FORM_ROUTES = {
    "oral": Route.PO,
    "tablet": Route.PO,
    "capsule": Route.PO,
    "ophthalmic": Route.TOP,
    "eye drop": Route.TOP,
    "ear drop": Route.TOP,
    "topical": Route.TOP,
    "cream": Route.TOP,
    "lotion": Route.TOP,
    "ointment": Route.TOP,
    "jelly": Route.TOP,
    "gel": Route.TOP,
    "shampoo": Route.TOP,
    "nail lacquer": Route.TOP,
    "vaginal cream": Route.TOP,
    "vaginal gel": Route.TOP,
    "inhaler": Route.INH,
    "inhalation capsule": Route.INH,
    "nebuliser solution": Route.INH,
    "nebuliser suspension": Route.INH,
    "rectal": Route.PR,
    "suppository": Route.PR,
    "sublingual": Route.SL,
    "intramuscular": Route.IM,
    "im injection": Route.IM,
    "subcutaneous": Route.SC,
    "sc injection": Route.SC,
    "intravenous": Route.IV,
    "iv injection": Route.IV,
    "iv infusion": Route.IV,
}

# How a product is given is stated in the catalogue's `dosage_form` column
# ("IV Injection or Infusion", "IM/IV Injection", "Eye Drops"); the generic
# name carries a route qualifier only occasionally. Ignoring the column left
# every injection-only drug on DrugMaster's default route, so the prescription
# form offered PO for meropenem and printed "PO" on the slip.
#
# Claiming a route the product does not have is a clinical risk, so a form
# contributes a route only when it names one outright: a bare "Injection"
# (IV? IM? SC?), a bare "Infusion", "Solution" or "Drops", a nasal spray and a
# mouthwash all stay unassigned. Local forms are checked before the oral words
# they contain, so "Vaginal Tablet" is not oral and "Eye Capsule" is not either.
_F_INHALED = re.compile(r" (inhaler|inhalation|inhalations|mdi|dpi|nebuliser|"
                        r"nebulizer|respirator|respirator solution) ")
_F_ORAL_EXPLICIT = re.compile(r" (oral|mouth dissolving|orodispersible) ")
_F_EYE_EAR = re.compile(r" (eye|ophthalmic|ear|otic|e e) ")
_F_NOWHERE = re.compile(r" (nasal|vaginal|mouthwash|gargle|dialysis|irrigation|"
                        r"bladder|implant|pessary) ")
_F_RECTAL = re.compile(r" (rectal|suppository|enema) ")
_F_SUBLINGUAL = re.compile(r" (sublingual|buccal) ")
_F_TOPICAL = re.compile(r" (topical|cream|ointment|lotion|shampoo|scalp|"
                        r"hand rub|medicated bar|paint|liniment|patch|"
                        r"transdermal|nail lacquer|soap) ")
_F_ORAL_WORDS = re.compile(r" (tablet|capsule|syrup|suspension|chewable|"
                           r"dispersible|effervescent|sachet|granule|granules|"
                           r"lozenge|pediatric drops|paediatric drops|"
                           r"powder for suspension|oral) ")


# Route order for a drug the catalogue described: the first entry becomes the
# form's default when the drug has no curated route. Alphabetical order would
# default ceftriaxone (IM + IV) to IM; the usual hospital route is IV.
ROUTE_PREFERENCE = [Route.PO, Route.IV, Route.IM, Route.SC, Route.INH,
                    Route.SL, Route.PR, Route.TOP]


def route_sort_key(route):
    value = getattr(route, "value", route)
    order = [r.value for r in ROUTE_PREFERENCE]
    return (order.index(value) if value in order else len(order), value)


def routes_from_dosage_form(form: str) -> frozenset:
    """Routes a catalogue `dosage_form` states outright; empty when ambiguous.

    >>> sorted(routes_from_dosage_form("IV Injection or Infusion"))
    ['IV']
    >>> sorted(routes_from_dosage_form("IM/IV Injection"))
    ['IM', 'IV']
    >>> sorted(routes_from_dosage_form("Injection"))      # IV? IM? SC?
    []
    >>> sorted(routes_from_dosage_form("Vaginal Tablet"))  # not oral
    []
    """
    f = " " + re.sub(r"[^a-z0-9]+", " ", (form or "").lower()).strip() + " "
    if not f.strip():
        return frozenset()

    routes = set()
    # Parenteral routes are additive: "IM/IV Injection" is genuinely both.
    if re.search(r" (iv|intravenous) ", f):
        routes.add(Route.IV)
    if re.search(r" (im|intramuscular) ", f):
        routes.add(Route.IM)
    if re.search(r" (sc|subcutaneous) ", f):
        routes.add(Route.SC)

    # Exactly one non-parenteral route, first match wins.
    if _F_INHALED.search(f):
        routes.add(Route.INH)
    elif _F_ORAL_EXPLICIT.search(f):
        routes.add(Route.PO)
    elif _F_EYE_EAR.search(f):
        routes.add(Route.TOP)
    elif _F_NOWHERE.search(f):
        pass
    elif _F_RECTAL.search(f):
        routes.add(Route.PR)
    elif _F_SUBLINGUAL.search(f):
        routes.add(Route.SL)
    elif _F_TOPICAL.search(f):
        routes.add(Route.TOP)
    elif _F_ORAL_WORDS.search(f):
        routes.add(Route.PO)
    return frozenset(routes)


# Device / consumable "generics": never prescribable.
DEVICE_RE = re.compile(
    r"(?i)\b(device|surgical|cannula|syringe|needle set|adhesive bandage|"
    r"dressing|graft|condom)\b"
)

# A trailing qualifier: "(Inhaler)" or "[For osteoporosis]".
QUALIFIER_RE = re.compile(r"\s*(?:\(([^()]*)\)|\[([^\[\]]*)\])\s*$")



class _NullContext:
    """Stand-in for transaction.atomic() during --dry-run."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False



# Curated synonyms: BDDrugBank generic name -> canonical DrugMaster generic.
# Only salt-form and minor spelling variants belong here. Combination products
# and genuinely different drugs must NOT be listed (they get their own row).
SYNONYMS = {
    # ACE inhibitors
    "Ramipril hydrochloride": "Ramipril",
    "Enalapril Maleate": "Enalapril",
    "Enalapril maleate": "Enalapril",
    # ARBs
    "Losartan Potassium": "Losartan",
    "Losartan potassium": "Losartan",
    # Statins
    "Atorvastatin Calcium": "Atorvastatin",
    "Atorvastatin calcium": "Atorvastatin",
    "Rosuvastatin Calcium": "Rosuvastatin",
    "Rosuvastatin calcium": "Rosuvastatin",
    # SGLT2i
    "Dapagliflozin Propanediol": "Dapagliflozin",
    "Dapagliflozin propanediol": "Dapagliflozin",
    # PPIs
    "Pantoprazole Sodium": "Pantoprazole",
    "Pantoprazole sodium": "Pantoprazole",
    "Omeprazole": "Omeprazole",
    "Esomeprazole": "Esomeprazole",
    "Esomeprazole Magnesium": "Esomeprazole",
    "Esomeprazole magnesium": "Esomeprazole",
    # Diabetes
    "Metformin Hydrochloride": "Metformin",
    "Metformin hydrochloride": "Metformin",
    "Sitagliptin Phosphate": "Sitagliptin",
    "Sitagliptin phosphate": "Sitagliptin",
    "Linagliptin": "Linagliptin",
    "Vildagliptin": "Vildagliptin",
    "Gliclazide": "Gliclazide",
    "Glimepiride": "Glimepiride",
    "Glipizide": "Glipizide",
    "Pioglitazone": "Pioglitazone",
    "Liraglutide": "Liraglutide",
    "Semaglutide": "Semaglutide",
    "Dulaglutide": "Dulaglutide",
    "Exenatide": "Exenatide",
    "Insulin human": "Insulin (soluble/regular)",
    "Insulin (soluble)": "Insulin (soluble/regular)",
    "Insulin Isophane": "Insulin isophane (NPH)",
    "Insulin (isophane)": "Insulin isophane (NPH)",
    "Insulin Glargine": "Insulin glargine",
    "Insulin Aspart": "Insulin aspart",
    "Insulin Aspart [Protamine Crystallised]": "Insulin aspart",
    "Insulin Lyspro": "Insulin aspart",
    "Biphasic Insulin Aspart": "Premixed insulin 70/30",
    "Insulin Aspart + Insulin Aspart Protamine": "Premixed insulin 70/30",
    "Insulin Degludec + Insulin Aspart Premixed": "Premixed insulin 70/30",
    "Biphasic Insulin": "Premixed insulin 70/30",
    "Insulin Biphasic": "Premixed insulin 70/30",
    # Immunosuppressants
    "Mycophenolate Mofetil": "Mycophenolate mofetil",
    "Mycophenolate mofetil": "Mycophenolate mofetil",
    "Mycophenolate Sodium": "Mycophenolate mofetil",
    "Mycophenolate sodium": "Mycophenolate mofetil",
    "Cyclosporine": "Cyclosporine",
    "Cyclosporine A": "Cyclosporine",
    "Tacrolimus Monohydrate": "Tacrolimus",
    "Tacrolimus monohydrate": "Tacrolimus",
    "Azathioprine": "Azathioprine",
    "Cyclophosphamide Monohydrate": "Cyclophosphamide",
    "Cyclophosphamide monohydrate": "Cyclophosphamide",
    "Rituximab": "Rituximab",
    "Hydroxychloroquine Sulphate": "Hydroxychloroquine",
    "Hydroxychloroquine sulphate": "Hydroxychloroquine",
    "Hydroxychloroquine Sulfate": "Hydroxychloroquine",
    # Steroids
    "Prednisolone": "Prednisolone",
    "Prednisolone Sodium Phosphate": "Prednisolone",
    "Prednisolone sodium phosphate": "Prednisolone",
    "Prednisolone Acetate": "Prednisolone",
    "Prednisolone acetate": "Prednisolone",
    "Methylprednisolone": "Methylprednisolone",
    "Methylprednisolone Sodium Succinate": "Methylprednisolone",
    "Methylprednisolone sodium succinate": "Methylprednisolone",
    "Methylprednisolone Acetate": "Methylprednisolone",
    "Methylprednisolone acetate": "Methylprednisolone",
    "Dexamethasone": "Dexamethasone",
    "Betamethasone": "Betamethasone",
    "Budesonide": "Budesonide",
    # Diuretics
    "Furosemide": "Furosemide",
    "Spironolactone": "Spironolactone",
    "Eplerenone": "Eplerenone",
    "Torsemide": "Torsemide",
    "Hydrochlorothiazide": "Hydrochlorothiazide",
    "Chlorthalidone": "Chlorthalidone",
    "Indapamide": "Indapamide",
    # CKD-MBD
    "Calcium Carbonate": "Calcium carbonate",
    "Calcium carbonate": "Calcium carbonate",
    "Sevelamer Hydrochloride": "Sevelamer",
    "Sevelamer hydrochloride": "Sevelamer",
    "Sevelamer Carbonate": "Sevelamer",
    "Sevelamer carbonate": "Sevelamer",
    "Cholecalciferol": "Cholecalciferol",
    "Cholecalciferol [Vitamin D3]": "Cholecalciferol",
    "Paricalcitol": "Paricalcitol",
    "Alendronate Sodium": "Alendronate",
    "Alendronate sodium": "Alendronate",
    "Risedronate Sodium": "Risedronate",
    "Risedronate sodium": "Risedronate",
    "Zoledronic Acid": "Zoledronic acid",
    "Zoledronic acid": "Zoledronic acid",
    "Ibandronic Acid": "Ibandronic acid",
    "Denosumab": "Denosumab",
    # Anaemia
    "Epoetin Alfa": "Epoetin alfa",
    "Epoetin alfa": "Epoetin alfa",
    "Darbepoetin Alfa": "Darbepoetin alfa",
    "Iron Sucrose": "Iron sucrose",
    "Iron sucrose": "Iron sucrose",
    "Ferrous Sulfate": "Ferrous sulfate",
    "Ferrous sulfate": "Ferrous sulfate",
    # Electrolytes
    "Sodium Bicarbonate": "Sodium bicarbonate",
    "Sodium bicarbonate": "Sodium bicarbonate",
    "Potassium Chloride": "Potassium chloride",
    # Anticoagulants
    "Heparin Sodium": "Heparin",
    "Heparin sodium": "Heparin",
    "Warfarin Sodium": "Warfarin",
    "Warfarin sodium": "Warfarin",
    "Rivaroxaban": "Rivaroxaban",
    "Apixaban": "Apixaban",
    "Edoxaban": "Edoxaban",
    "Dabigatran": "Dabigatran",
    # Anti-infectives (common generics)
    "Amoxicillin + Clavulanic Acid": "Amoxicillin + Clavulanic Acid",
    "Amoxicillin Clavulanate": "Amoxicillin + Clavulanic Acid",
    "Amoxicillin": "Amoxicillin",
    "Ceftriaxone": "Ceftriaxone",
    "Cefixime": "Cefixime",
    "Ciprofloxacin": "Ciprofloxacin",
    "Azithromycin": "Azithromycin",
    "Azithromycin Dihydrate": "Azithromycin",
    "Azithromycin dihydrate": "Azithromycin",
    "Metronidazole": "Metronidazole",
    "Doxycycline": "Doxycycline",
    "Clindamycin": "Clindamycin",
    "Vancomycin": "Vancomycin",
    "Gentamicin": "Gentamicin",
    "Amikacin": "Amikacin",
    "Acyclovir": "Acyclovir",
    "Valacyclovir": "Valacyclovir",
    "Oseltamivir": "Oseltamivir",
    "Fluconazole": "Fluconazole",
    "Ketoconazole": "Ketoconazole",
    "Itraconazole": "Itraconazole",
    "Voriconazole": "Voriconazole",
    " Amphotericin B": "Amphotericin B".strip(),
    # NSAIDs / analgesics
    "Diclofenac Sodium": "Diclofenac",
    "Diclofenac sodium": "Diclofenac",
    "Diclofenac Potassium": "Diclofenac",
    "Diclofenac potassium": "Diclofenac",
    "Ibuprofen": "Ibuprofen",
    "Naproxen": "Naproxen",
    "Aceclofenac": "Aceclofenac",
    "Paracetamol": "Paracetamol",
    "Acetaminophen": "Paracetamol",
    "Ketorolac": "Ketorolac",
    "Aspirin": "Aspirin",
    "Tramadol": "Tramadol",
    "Celecoxib": "Celecoxib",
    "Meloxicam": "Meloxicam",
    # Antihypertensives
    "Amlodipine": "Amlodipine",
    "Amlodipine Besilate": "Amlodipine",
    "Amlodipine besilate": "Amlodipine",
    "Atenolol": "Atenolol",
    "Bisoprolol": "Bisoprolol",
    "Bisoprolol Fumarate": "Bisoprolol",
    "Bisoprolol fumarate": "Bisoprolol",
    "Metoprolol": "Metoprolol",
    "Carvedilol": "Carvedilol",
    "Nebivolol": "Nebivolol",
    "Propranolol": "Propranolol",
    "Labetalol": "Labetalol",
    "Hydralazine": "Hydralazine",
    "Minoxidil": "Minoxidil",
    # CCBs + combos (combinations get their own rows)
    "Amlodipine + Atenolol": "Amlodipine + Atenolol",
    "Amlodipine + Atorvastatin": "Amlodipine + Atorvastatin",
    "Amlodipine + Telmisartan": "Amlodipine + Telmisartan",
    "Amlodipine + Valsartan": "Amlodipine + Valsartan",
    "Amlodipine + Benazepril": "Amlodipine + Benazepril",
    "Amlodipine + Olmesartan": "Amlodipine + Olmesartan",
    "Amlodipine + Losartan": "Amlodipine + Losartan",
    "Losartan + Hydrochlorothiazide": "Losartan + HCTZ",
    "Telmisartan + Hydrochlorothiazide": "Telmisartan + HCTZ",
    "Valsartan + Hydrochlorothiazide": "Valsartan + HCTZ",
    "Ramipril + Hydrochlorothiazide": "Ramipril + HCTZ",
    "Sacubitril + Valsartan": "Sacubitril + Valsartan",
    "Bisoprolol + Amlodipine": "Bisoprolol + Amlodipine",
    "Bisoprolol + Hydrochlorothiazide": "Bisoprolol + HCTZ",
    "Atenolol + Chlorthalidone": "Atenolol + Chlorthalidone",
    # Vitamins / minerals
    "Vitamin B1, B6 & B12": "Vitamin B1 B6 B12",
    "Vitamin B complex": "Vitamin B complex",
    "Vitamin C": "Vitamin C",
    "Vitamin D3": "Vitamin D3",
    "Vitamin E": "Vitamin E",
    "Zinc Sulfate": "Zinc sulfate",
    "Zinc sulfate": "Zinc sulfate",
    "Zinc Sulfate Monohydrate": "Zinc sulfate",
    "Zinc sulfate monohydrate": "Zinc sulfate",
    "Magnesium Sulfate": "Magnesium sulfate",
    "Calcium Lactate Gluconate": "Calcium lactate gluconate",
    # Thyroid
    "Levothyroxine": "Levothyroxine",
    "Carbimazole": "Carbimazole",
    "Propylthiouracil": "Propylthiouracil",
    # GI / antiemetic / motility
    "Pantoprazole": "Pantoprazole",
    "Rabeprazole": "Rabeprazole",
    "Lansoprazole": "Lansoprazole",
    "Domperidone": "Domperidone",
    "Domperidone Maleate": "Domperidone",
    "Domperidone maleate": "Domperidone",
    "Ondansetron": "Ondansetron",
    "Ranitidine": "Ranitidine",
    "Famotidine": "Famotidine",
    "Sucralfate": "Sucralfate",
    "Mesalazine": "Mesalazine",
    "Sulfasalazine": "Sulfasalazine",
    "Ursodeoxycholic Acid": "Ursodeoxycholic acid",
    "Ursodeoxycholic acid": "Ursodeoxycholic acid",
    # Respiratory
    "Montelukast": "Montelukast",
    "Montelukast Sodium": "Montelukast",
    "Montelukast sodium": "Montelukast",
    "Salbutamol": "Salbutamol",
    "Salbutamol Sulfate": "Salbutamol",
    "Salbutamol sulfate": "Salbutamol",
    "Terbutaline": "Terbutaline",
    "Budesonide + Formoterol": "Budesonide + Formoterol",
    "Beclomethasone": "Beclomethasone",
    "Fluticasone": "Fluticasone",
    "Fluticasone Propionate": "Fluticasone",
    "Fluticasone propionate": "Fluticasone",
    "Salmeterol": "Salmeterol",
    "Formoterol": "Formoterol",
    "Formoterol Fumarate": "Formoterol",
    "Formoterol fumarate": "Formoterol",
    "Tiotropium": "Tiotropium",
    "Ipratropium": "Ipratropium",
    # Allergy
    "Cetirizine": "Cetirizine",
    "Cetirizine Hydrochloride": "Cetirizine",
    "Cetirizine hydrochloride": "Cetirizine",
    "Fexofenadine": "Fexofenadine",
    "Fexofenadine Hydrochloride": "Fexofenadine",
    "Fexofenadine hydrochloride": "Fexofenadine",
    "Loratadine": "Loratadine",
    "Levocetirizine": "Levocetirizine",
    "Bilastine": "Bilastine",
    "Desloratadine": "Desloratadine",
    "Chlorpheniramine": "Chlorpheniramine",
    "Pheniramine": "Pheniramine",
    "Ketotifen": "Ketotifen",
    # Psychiatry / neurology
    "Fluoxetine": "Fluoxetine",
    "Sertraline": "Sertraline",
    "Citalopram": "Citalopram",
    "Escitalopram": "Escitalopram",
    "Paroxetine": "Paroxetine",
    "Venlafaxine": "Venlafaxine",
    "Duloxetine": "Duloxetine",
    "Mirtazapine": "Mirtazapine",
    "Bupropion": "Bupropion",
    "Trazodone": "Trazodone",
    "Amitriptyline": "Amitriptyline",
    "Nortriptyline": "Nortriptyline",
    "Pregabalin": "Pregabalin",
    "Gabapentin": "Gabapentin",
    "Levetiracetam": "Levetiracetam",
    "Carbamazepine": "Carbamazepine",
    "Phenytoin": "Phenytoin",
    "Valproic Acid": "Valproic acid",
    "Valproic acid": "Valproic acid",
    "Sodium Valproate": "Valproic acid",
    "Sodium valproate": "Valproic acid",
    "Clonazepam": "Clonazepam",
    "Lorazepam": "Lorazepam",
    "Alprazolam": "Alprazolam",
    "Diazepam": "Diazepam",
    "Donepezil": "Donepezil",
    "Memantine": "Memantine",
    "Pirenzepine": "Pirenzepine",
    # Muscarinic / urology
    "Tamsulosin": "Tamsulosin",
    "Oxybutynin": "Oxybutynin",
    "Solifenacin": "Solifenacin",
    "Tolterodine": "Tolterodine",
    "Fesoterodine": "Fesoterodine",
    "Mirabegron": "Mirabegron",
    # Vitamins / minerals
    "Folic Acid": "Folic acid",
    "Folic acid": "Folic acid",
    "Methylcobalamin": "Methylcobalamin",
    "Cyanocobalamin": "Cyanocobalamin",
    "Alpha Lipoic Acid": "Alpha lipoic acid",
    "Alpha lipoic acid": "Alpha lipoic acid",
    "Thiamine": "Thiamine",
    "Riboflavin": "Riboflavin",
    "Niacin": "Niacin",
    "Pyridoxine": "Pyridoxine",
    "Biotin": "Biotin",
    "Ascorbic Acid": "Vitamin C",
    "Ascorbic acid": "Vitamin C",
    # Minerals
    "Potassium Citrate": "Potassium citrate",
    "Potassium citrate": "Potassium citrate",
    "Magnesium Oxide": "Magnesium oxide",
    "Chromium": "Chromium",
    "Selenium": "Selenium",
    "Copper": "Copper",
    "Manganese": "Manganese",
    # Cardio / lipids
    "Clopidogrel": "Clopidogrel",
    "Ticagrelor": "Ticagrelor",
    "Prasugrel": "Prasugrel",
    "Ezetimibe": "Ezetimibe",
    "Atorvastatin + Ezetimibe": "Atorvastatin + Ezetimibe",
    "Rosuvastatin + Ezetimibe": "Rosuvastatin + Ezetimibe",
    "Fenofibrate": "Fenofibrate",
    "Omega-3": "Omega-3 fatty acids",
    "Omega 3": "Omega-3 fatty acids",
    "Fish Oil": "Fish oil",
    # Diuretics
    "Amiloride": "Amiloride",
    "Triamterene": "Triamterene",
    "Mannitol": "Mannitol",
    "Acetazolamide": "Acetazolamide",
    "Furosemide + Spironolactone": "Furosemide + Spironolactone",
    # Oncology
    "Imatinib": "Imatinib",
    "Nilotinib": "Nilotinib",
    "Dasatinib": "Dasatinib",
    "Ruxolitinib": "Ruxolitinib",
    "Sorafenib": "Sorafenib",
    "Sunitinib": "Sunitinib",
    "Axitinib": "Axitinib",
    "Vemurafenib": "Vemurafenib",
    "Dabrafenib": "Dabrafenib",
    "Trastuzumab": "Trastuzumab",
    "Bevacizumab": "Bevacizumab",
    "Cetuximab": "Cetuximab",
    "Panitumumab": "Panitumumab",
    "Pertuzumab": "Pertuzumab",
    "Bicalutamide": "Bicalutamide",
    "Leuprolide": "Leuprolide",
    "Goserelin": "Goserelin",
    "Pembrolizumab": "Pembrolizumab",
    "Nivolumab": "Nivolumab",
    "Atezolizumab": "Atezolizumab",
    "Avelumab": "Avelumab",
    "Durvalumab": "Durvalumab",
    "Adalimumab": "Adalimumab",
    "Infliximab": "Infliximab",
    "Etanercept": "Etanercept",
    "Ustekinumab": "Ustekinumab",
    "Secukinumab": "Secukinumab",
    "Tocilizumab": "Tocilizumab",
    "Abatacept": "Abatacept",
    "Anakinra": "Anakinra",
    "Canakinumab": "Canakinumab",
    "Belimumab": "Belimumab",
    "Apremilast": "Apremilast",
    "Tofacitinib": "Tofacitinib",
    "Baricitinib": "Baricitinib",
    "Upadacitinib": "Upadacitinib",
    "Filgotinib": "Filgotinib",
    "Leflunomide": "Leflunomide",
    "Methotrexate": "Methotrexate",
    "Hydroxyurea": "Hydroxyurea",
    "Busulfan": "Busulfan",
    "Mercaptopurine": "Mercaptopurine",
    "Capecitabine": "Capecitabine",
    "Gemcitabine": "Gemcitabine",
    "Paclitaxel": "Paclitaxel",
    "Docetaxel": "Docetaxel",
    "Vinblastine": "Vinblastine",
    "Vincristine": "Vincristine",
    "Etoposide": "Etoposide",
    "Teniposide": "Teniposide",
    "Ifosfamide": "Ifosfamide",
    "Carmustine": "Carmustine",
    "Lomustine": "Lomustine",
    "Procarbazine": "Procarbazine",
    "Dactinomycin": "Dactinomycin",
    "Bleomycin": "Bleomycin",
    "Doxorubicin": "Doxorubicin",
    "Daunorubicin": "Daunorubicin",
    "Epirubicin": "Epirubicin",
    "Idarubicin": "Idarubicin",
    "Mitoxantrone": "Mitoxantrone",
    "Mitomycin": "Mitomycin",
    "Plicamycin": "Plicamycin",
    "Cisplatin": "Cisplatin",
    "Carboplatin": "Carboplatin",
    "Oxaliplatin": "Oxaliplatin",
    "Nedaplatin": "Nedaplatin",
    "Lobaplatin": "Lobaplatin",
    "Heptaplatin": "Heptaplatin",
    "Satraplatin": "Satraplatin",
    "Spirogermanium": "Spirogermanium",
    "Topotecan": "Topotecan",
    "Irinotecan": "Irinotecan",
    "Camptothecin": "Camptothecin",
    "Raltitrexed": "Raltitrexed",
    "Trimetrexate": "Trimetrexate",
    "Pemetrexed": "Pemetrexed",
    "Flutamide": "Flutamide",
    "Nilutamide": "Nilutamide",
    "Enzalutamide": "Enzalutamide",
    "Abiraterone": "Abiraterone",
    "Degarelix": "Degarelix",
    "Histrelin": "Histrelin",
    "Triptorelin": "Triptorelin",
    "Buserelin": "Buserelin",
    "Nafarelin": "Nafarelin",
    "Cetrorelix": "Cetrorelix",
    "Ganirelix": "Ganirelix",
    "Fulvestrant": "Fulvestrant",
    "Tamoxifen": "Tamoxifen",
    "Toremifene": "Toremifene",
    "Raloxifene": "Raloxifene",
    "Clomiphene": "Clomiphene",
    "Diethylstilbestrol": "Diethylstilbestrol",
    "Estradiol": "Estradiol",
    "Estriol": "Estriol",
    "Conjugated Estrogens": "Conjugated estrogens",
    "Progesterone": "Progesterone",
    "Hydroxyprogesterone": "Hydroxyprogesterone",
    "Megestrol": "Megestrol",
    "Medroxyprogesterone": "Medroxyprogesterone",
    "Norethisterone": "Norethisterone",
    "Norgestrel": "Norgestrel",
    "Levonorgestrel": "Levonorgestrel",
    "Desogestrel": "Desogestrel",
    "Gestodene": "Gestodene",
    "Norgestimate": "Norgestimate",
    "Drospirenone": "Drospirenone",
    "Cyproterone": "Cyproterone",
    "Chlormadinone": "Chlormadinone",
    "Mep-trade": "Mep-trade",
}


def norm(s: str) -> str:
    """Fold a drug name to a match key: lowercase, alphanumerics only.

    This is what makes "Losartan potassium", "losartan potassium" and
    "LOSARTAN POTASSIUM" resolve to the same DrugMaster row. `generic_name`
    is unique only case-sensitively, so an exact match alone would let
    MedEx's inconsistent capitalisation create duplicate drugs - which then
    breaks `seed_drug_knowledge`'s `generic_name__iexact` lookup with
    MultipleObjectsReturned.
    """
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


# Same lookup keyed by norm() so consolidation finds a curated drug whose
# stored casing differs from the folded base ("Zoledronic acid" vs
# "Zoledronic Acid"). _consolidate only needs membership, not the list.
CURATED_BRANDS_NORM = {norm(k): v for k, v in CURATED_BRANDS.items()}
CURATED_ROUTES_NORM = {norm(k) for k in CURATED_ROUTES}


# SYNONYMS also indexed case/punctuation-insensitively, so MedEx's
# inconsistent capitalisation ("Insulin Human" vs the curated "Insulin
# human") resolves to the same canonical drug instead of creating a second
# row for a drug the clinic already prescribes.
SYNONYMS_BY_NORM = {}
for _key, _val in SYNONYMS.items():
    _folded = norm(_key)
    if SYNONYMS_BY_NORM.get(_folded, _val) != _val:
        # Two spellings of one key pointing at different drugs: refuse to
        # guess, and fall back to the exact-match path.
        SYNONYMS_BY_NORM[_folded] = None
    else:
        SYNONYMS_BY_NORM.setdefault(_folded, _val)


def canonical_generic(generic: str) -> str:
    """Resolve a scraped generic name to its canonical DrugMaster name."""
    if generic in SYNONYMS:
        return SYNONYMS[generic]
    return SYNONYMS_BY_NORM.get(norm(generic)) or generic


def is_device(generic: str) -> bool:
    """True for MedEx device / consumable pseudo-generics."""
    return bool(DEVICE_RE.search(generic or ""))


def split_generic(generic: str) -> tuple[str, str | None]:
    """Fold a MedEx generic onto its base name plus a route, if unambiguous.

    >>> split_generic("Budesonide (Inhaler)")
    ('Budesonide', 'INH')
    >>> split_generic("Acyclovir (Oral)")
    ('Acyclovir', 'PO')
    >>> split_generic("Acyclovir (Injection)")   # ambiguous -> no route
    ('Acyclovir', None)
    >>> split_generic("Zoledronic Acid [For osteoporosis]")
    ('Zoledronic acid', None)                    # indication, not a route
    >>> split_generic("17 β Estradiol")
    ('17 β Estradiol', None)
    """
    base, route = (generic or "").strip(), None
    # Peel trailing qualifiers repeatedly: "Insulin (Human) (Injection)".
    while True:
        match = QUALIFIER_RE.search(base)
        if not match:
            break
        qualifier = (match.group(1) or match.group(2) or "").strip().lower()
        candidate = FORM_ROUTES.get(qualifier)
        if candidate and route is None:
            route = candidate
        stripped = base[:match.start()].strip()
        if not stripped:
            break  # the whole name was a qualifier - keep it as-is
        base = stripped
    return base, route


# A name tagged as a local product ("Betamethasone 0.05% Topical", "Tobramycin
# Eye prep") or built from several ingredients is not the systemic exposure the
# steroid / calcineurin-inhibitor research classes analyse.
LOCAL_FORM_RE = re.compile(
    r"\b(topical|eye|ear|nasal|ophthalmic|otic|prep|cream|ointment|lotion|"
    r"gel|drops?|spray|inhal\w*|vag\w*|rectal|mouth\W?wash|gargle|"
    r"respirator\w*)\b|\d\s*%",
    re.I,
)


def is_local_or_combination(generic_name: str) -> bool:
    name = generic_name or ""
    if LOCAL_FORM_RE.search(name):
        return True
    parts = [p.split()[0].lower() for p in name.split("+") if p.strip()]
    # "Betamethasone Sodium Phosphate + Betamethasone Acetate" is one molecule
    # in two salts (the systemic injectable), not a combination product.
    return len(set(parts)) > 1


def classify_drug(generic_name: str, therapeutic_classes: list[str]) -> DrugClass:
    """Map a BDDrugBank generic to a BGDDR DrugClass."""
    g = (generic_name or "").lower()
    tc = " ".join(t.lower() for t in therapeutic_classes)
    local = is_local_or_combination(generic_name)

    # SGLT2 inhibitors
    if (any(k in g for k in ("dapagliflozin", "empagliflozin", "canagliflozin",
                              "ertugliflozin", "sglt2", "beatus"))
            or any(k in tc for k in ("sglt2", "sodium-glucose"))):
        return DrugClass.SGLT2I
    if "finerenone" in g:
        return DrugClass.FINERENONE
    if "hydroxychloroquine" in g:
        return DrugClass.HCQ

    # RAAS inhibitors — catch ACEi and ARB separately
    acei_kw = ["ramipril", "enalapril", "lisinopril", "perindopril",
               "captopril", "trandolapril", "quinapril", "benazepril",
               "fosinopril", "moexipril", "ace inhibit"]
    arb_kw = ["losartan", "telmisartan", "valsartan", "irbesartan",
              "candesartan", "olmesartan", "azilsartan", "eprosartan",
              "angiotensin receptor"]
    if any(k in g for k in acei_kw) or any(k in tc for k in acei_kw):
        return DrugClass.RAASI
    if any(k in g for k in arb_kw) or any(k in tc for k in arb_kw):
        return DrugClass.RAASI

    steroids = ["prednisolone", "prednisone", "methylprednisolone",
                "dexamethasone", "betamethasone", "budesonide",
                "deflazacort", "hydrocortisone", "cortisone",
                "triamcinolone", "beclomethasone", "fluticasone",
                "corticosteroid", "glucocorticoid"]
    if any(k in g for k in steroids) and not local:
        return DrugClass.STEROID
    if "mycophenolate" in g:
        return DrugClass.MMF
    if "azathioprine" in g:
        return DrugClass.AZATHIOPRINE
    if "cyclophosphamide" in g:
        return DrugClass.CYCLOPHOSPHAMIDE
    cni = ["cyclosporine", "ciclosporin", "tacrolimus",
           "rapamycin", "everolimus", "sirolimus"]
    if any(k in g for k in cni) and not local:
        return DrugClass.CNI
    if "rituximab" in g:
        return DrugClass.RITUXIMAB

    diuretics = ["furosemide", "spironolactone", "eplerenone",
                 "torsemide", "bumetanide", "hydrochlorothiazide",
                 "chlorthalidone", "indapamide", "amiloride",
                 "triamterene", "diuretic", "loop diuretic",
                 "potassium-sparing", "thiazide"]
    if any(k in g for k in diuretics) or any(k in tc for k in diuretics):
        return DrugClass.DIURETIC
    # HMG-CoA reductase inhibitors all end in "-vastatin". A bare "statin"
    # substring also hits nystatin (antifungal), somatostatin (hormone) and
    # cilastatin (dehydropeptidase inhibitor).
    if "vastatin" in g or re.search(r"\bstatins?\b", tc):
        return DrugClass.STATIN
    if "metformin" in g or "biguanide" in g:
        return DrugClass.METFORMIN
    su_kw = ["gliclazide", "glimepiride", "glipizide", "glyburide",
             "sulfonylurea", "sulfonylurea"]
    if any(k in g for k in su_kw):
        return DrugClass.SULFONYLUREA
    dpp4_kw = ["sitagliptin", "linagliptin", "vildagliptin",
               "saxagliptin", "alogliptin", "gliptin", "dpp-4"]
    if any(k in g for k in dpp4_kw):
        return DrugClass.DPP4I
    glp1_kw = ["liraglutide", "semaglutide", "dulaglutide",
               "exenatide", "lixisenatide", "glp-1"]
    if any(k in g for k in glp1_kw):
        return DrugClass.GLP1
    if "insulin" in g:
        return DrugClass.INSULIN

    return DrugClass.OTHER


class Command(BaseCommand):
    """Import BDDrugBank generics and brand names into DrugMaster.

    Skips system checks so the command runs even when gdes_core is not
    installed (the analytics/labs import chain would otherwise fail the
    check before the command body runs).
    """
    requires_system_checks = []
    help = ("Import BDDrugBank (Bangladesh medicine corpus) generics and "
            "brand names into DrugMaster.")

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path", type=str,
            help="Path to the scraped MedEx/BDDrugBank brand CSV",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would change without saving to the database",
        )
        parser.add_argument(
            "--limit", type=int, default=0,
            help="Stop after this many generics (0 = process all; for testing)",
        )
        parser.add_argument(
            "--consolidate", action="store_true",
            help="Repair pre-existing rows first: merge DrugMaster rows whose "
                 "names differ only by a MedEx qualifier "
                 "('Chlorhexidine Gluconate [4%%]' -> 'Chlorhexidine "
                 "Gluconate'), repointing prescriptions/exposures/adverse "
                 "events at the survivor, and delete pre-existing device "
                 "rows. Destructive - always dry-run first.",
        )

    def handle(self, *args, csv_path=None, dry_run=False, limit=0, **options):
        path = Path(csv_path)
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {csv_path}"))
            return

        self.stdout.write(f"Reading {path} ...")
        generics = self._accumulate(path)
        total_unique = len(generics)

        if limit:
            limited = dict(list(generics.items())[:limit])
            generics = limited
            self.stdout.write(f"Limited to {limit} of {total_unique} generics\n")

        if options.get("consolidate"):
            self._consolidate(dry_run)

        # Index the existing table by normalized name. `generic_name` is
        # unique only case-sensitively, so matching on `norm()` is what
        # stops MedEx's inconsistent capitalisation ("Losartan potassium"
        # vs "losartan potassium") from creating a second row for a drug the
        # clinicians already prescribe - a duplicate would also break
        # seed_drug_knowledge's `generic_name__iexact` lookup.
        existing = {}
        exact = {}
        collisions = defaultdict(list)
        for obj in DrugMaster.objects.all():
            exact[obj.generic_name] = obj
            existing.setdefault(norm(obj.generic_name), obj)
            collisions[norm(obj.generic_name)].append(obj.generic_name)
        dupes = {k: v for k, v in collisions.items() if len(v) > 1}
        if dupes:
            self.stdout.write(self.style.WARNING(
                f"  WARNING: {len(dupes)} pre-existing duplicate generic(s) "
                f"in DrugMaster, e.g. {list(dupes.values())[:3]}. "
                f"Resolve these before re-running."))

        created = updated = brands_added = strengths_added = 0
        class_upgrades = routes_added = 0
        too_long = 0

        def apply(obj, canonical, data, is_new):
            """Merge scraped data onto `obj`. Returns per-field change counts."""
            counts = {"brands": 0, "strengths": 0, "routes": 0}

            # --- brands: curated formulary order first, then alphabetical ---
            existing_brands = list(obj.brand_names or [])
            merged_brands = set(existing_brands) | data["brands"]
            ordered = self._order_brands(canonical, merged_brands)
            counts["brands"] = len(merged_brands) - len(existing_brands)
            if ordered != existing_brands:
                obj.brand_names = ordered

            # --- strengths (additive) ---
            existing_strengths = set(obj.available_strengths or [])
            merged_strengths = existing_strengths | data["strengths"]
            counts["strengths"] = len(merged_strengths - existing_strengths)
            if merged_strengths != existing_strengths:
                obj.available_strengths = sorted(merged_strengths)

            # --- routes: additive, never removing curated ones ---
            if data["routes"]:
                routes = list(obj.available_routes or [])
                for route in sorted(data["routes"], key=route_sort_key):
                    if route not in routes:
                        routes.append(route)
                        counts["routes"] += 1
                if routes:
                    if norm(canonical) in CURATED_ROUTES_NORM:
                        # Seeded route list: keep its order and its default.
                        obj.available_routes = routes
                        if obj.default_route not in routes:
                            obj.default_route = routes[0]
                    else:
                        # Derived from the catalogue, so recompute it rather
                        # than keeping whatever an earlier import happened to
                        # store first: paracetamol had been left defaulting to
                        # IV because an "(IV Infusion)" name reached it before
                        # any oral form did.
                        routes = sorted(routes, key=route_sort_key)
                        obj.available_routes = routes
                        obj.default_route = routes[0]
                # Per-route strengths only for rows this import created, so
                # curated strengths_by_route on formulary drugs is untouched.
                if is_new and data["strengths_by_route"]:
                    obj.strengths_by_route = {
                        r: sorted(v) for r, v in data["strengths_by_route"].items()
                    }
            return counts

        context = transaction.atomic() if not dry_run else _NullContext()
        with context:
            for idx, (generic, data) in enumerate(sorted(generics.items()), 1):
                # Resolve canonical generic via synonym map, then normalized
                # match against an existing row.
                canonical = canonical_generic(generic)
                if len(canonical) > MAX_GENERIC:
                    too_long += 1
                    self.stderr.write(self.style.WARNING(
                        f"  skipping over-long generic_name ({len(canonical)} "
                        f"chars): {canonical[:60]}..."))
                    continue
                drug_class = classify_drug(canonical,
                                           data["therapeutic_classes"])

                obj = exact.get(canonical) or existing.get(norm(canonical))
                if obj is not None:
                    counts = apply(obj, canonical, data, is_new=False)
                    brands_added += counts["brands"]
                    strengths_added += counts["strengths"]
                    routes_added += counts["routes"]
                    # Upgrade DrugClass if it was OTHER and we now have a match
                    if obj.drug_class == DrugClass.OTHER and \
                       drug_class != DrugClass.OTHER:
                        obj.drug_class = drug_class
                        class_upgrades += 1
                    # `apply` mutates the instance, so the save must be
                    # skipped in --dry-run too, not just the create path.
                    if not dry_run:
                        obj.save()
                    updated += 1
                else:
                    created += 1
                    if dry_run:
                        continue
                    obj = DrugMaster.objects.create(
                        generic_name=canonical,
                        drug_class=drug_class,
                    )
                    # Later spellings that fold to the same canonical name
                    # ("Losartan potassium" / "Losartan Potassium") must find
                    # this row, not try to create it again.
                    exact[canonical] = obj
                    existing.setdefault(norm(canonical), obj)
                    counts = apply(obj, canonical, data, is_new=True)
                    brands_added += counts["brands"]
                    strengths_added += counts["strengths"]
                    routes_added += counts["routes"]
                    obj.save()

                if idx % 2000 == 0:
                    self.stdout.write(
                        f"  ... {idx}/{len(generics)} generics processed "
                        f"(created={created}, updated={updated}, "
                        f"brands={brands_added}) ...")

                if limit and idx >= limit:
                    break

        if too_long:
            self.stdout.write(self.style.WARNING(
                f"  Skipped {too_long} generic(s) exceeding "
                f"generic_name max_length={MAX_GENERIC}."))

        if dry_run:
            self.stdout.write(self.style.WARNING("--- DRY RUN ---"))

        total_db = DrugMaster.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\n{'DRY RUN' if dry_run else 'IMPORT COMPLETE'}:\n"
            f"  New generics created : {created}\n"
            f"  Existing updated     : {updated}\n"
            f"  New brand names added: {brands_added}\n"
            f"  New strengths added  : {strengths_added}\n"
            f"  Routes added         : {routes_added}\n"
            f"  DrugClass upgrades   : {class_upgrades}\n"
            f"  Total generics in DB : {total_db}"
        ))

    @staticmethod
    def _order_brands(canonical, brands):
        """Curated formulary brands first, then the rest alphabetically.

        `templates/clinic/prescription_form.html` preselects `brands[0]`
        and POSTs it as the item's brand, which becomes the drug's name on
        the printed prescription and in the FHIR MedicationRequest. Sorting
        everything alphabetically would silently swap a familiar brand
        (Cardace, Tritace) for an obscure one (Acecard) on every new
        prescription.
        """
        curated = CURATED_BRANDS.get(canonical) or []
        if not curated:
            return sorted(brands)
        head = [b for b in curated if b in brands]
        # Curated list first (in curated order), then the remainder sorted.
        return head + sorted(brands - set(head))

    def _consolidate(self, dry_run: bool):
        """Repair DrugMaster rows left over from an un-normalised import.

        An earlier import stored MedEx's qualified names verbatim, so the
        table accumulated rows that differ only by a qualifier:
        'Chlorhexidine Gluconate [0.2%]', '[1%]', '[4%]', '[7.1%]'. Folding
        the incoming catalogue would then create a *second*
        'Chlorhexidine Gluconate' beside them, and a duplicate generic splits
        a patient's treatment episode across two drug records.

        For each folded base this picks a survivor, repoints every foreign
        key at it, merges the variant rows' brands/strengths/routes into it,
        and deletes the variants. Device rows are deleted outright: they can
        never be prescribed.

        Destructive, hence opt-in via --consolidate.
        """
        from prescriptions.models import PrescriptionItem
        from safety.models import AdverseEvent
        from treatments.models import TreatmentExposure

        self.stdout.write("\n--- consolidation ---")
        rows = list(DrugMaster.objects.all())

        devices = [o for o in rows if is_device(o.generic_name)]
        device_pks = {o.pk for o in devices}
        variants = defaultdict(list)
        for obj in rows:
            # Devices are deleted outright, never merged into a survivor.
            if obj.pk in device_pks:
                continue
            # A seeded formulary name is authoritative - never fold or rename
            # it. `Insulin (soluble/regular)` and `Insulin isophane (NPH)`
            # look foldable but are the exact keys seed_drug_knowledge looks
            # up and that CURATED_BRANDS is keyed by; folding them to
            # `Insulin` would orphan the formulary entry.
            if norm(obj.generic_name) in CURATED_BRANDS_NORM:
                continue
            base, _route = split_generic(obj.generic_name)
            if base != obj.generic_name:
                variants[base].append(obj)

        if not devices and not variants:
            self.stdout.write("  nothing to consolidate.")
            return

        merged_rows = deleted_rows = repointed = 0
        plan = []

        for base, group in sorted(variants.items()):
            # Prefer a row that already carries the clean base name. Match
            # case-insensitively: `Zoledronic acid` (the seeded formulary row,
            # holding the curated brands and the correct IV route) must win
            # over the `Zoledronic Acid` variants, otherwise folding renames a
            # variant into a second `Zoledronic Acid` and `seed_drug_knowledge`
            #'s `generic_name__iexact` lookup starts raising
            # MultipleObjectsReturned.
            target = norm(base)
            survivor = next((o for o in rows
                             if o.pk not in device_pks
                             and o.generic_name == base), None)
            if survivor is None:
                survivor = next((o for o in rows
                                 if o.pk not in device_pks
                                 and norm(o.generic_name) == target), None)
            if survivor is None:
                # No clean row yet: rename the richest variant in place rather
                # than creating a duplicate. These rows carry no curated
                # clinical data, so this is safe.
                survivor = max(
                    group, key=lambda o: (len(o.brand_names or []),
                                          len(o.available_strengths or []),
                                          -len(o.generic_name)))
            losers = [o for o in group if o.pk != survivor.pk]
            rename_only = (norm(survivor.generic_name) != norm(base)
                           and not losers)
            if not losers and not rename_only:
                # Already stored under the clean base name; nothing to fold.
                continue

            brands = set(survivor.brand_names or [])
            strengths = set(survivor.available_strengths or [])
            routes = set(survivor.available_routes or [])
            for obj in losers:
                brands |= set(obj.brand_names or [])
                strengths |= set(obj.available_strengths or [])
                routes |= set(obj.available_routes or [])

            plan.append((survivor.generic_name, base,
                         [o.generic_name for o in losers],
                         len(brands), len(strengths)))

            if dry_run:
                merged_rows += 1
                deleted_rows += len(losers)
                continue

            # Each group is its own transaction. A crash midway through a
            # scheduled (unattended) consolidation must not leave a
            # TreatmentExposure pointing at a half-deleted row, so the
            # repoint and the delete have to commit or roll back together.
            with transaction.atomic():
                if norm(survivor.generic_name) != norm(base):
                    survivor.generic_name = base
                survivor.brand_names = self._order_brands(
                    base, brands) if norm(base) in CURATED_BRANDS_NORM else \
                    sorted(brands)
                survivor.available_strengths = sorted(strengths)
                if routes:
                    # Only widen the route set; a curated IV-only drug such
                    # as zoledronic acid must not gain PO because a scraped
                    # variant defaulted to it.
                    survivor.available_routes = sorted(
                        routes | set(survivor.available_routes or []))
                    if survivor.default_route not in survivor.available_routes:
                        survivor.default_route = survivor.available_routes[0]
                # A variant that carried a real class keeps it over OTHER.
                if survivor.drug_class == DrugClass.OTHER:
                    for obj in losers:
                        if obj.drug_class != DrugClass.OTHER:
                            survivor.drug_class = obj.drug_class
                            break
                survivor.save()

                for obj in losers:
                    for model, field in ((TreatmentExposure, "drug"),
                                         (PrescriptionItem, "drug"),
                                         (AdverseEvent, "suspected_drug")):
                        repointed += model.objects.filter(
                            **{field: obj}).update(**{field: survivor})
                    obj.delete()
                    deleted_rows += 1
            merged_rows += 1

        if devices:
            for obj in devices:
                # `drug` is non-nullable on exposures and prescription items,
                # so never force a null: report and leave the row alone for a
                # human to resolve.
                in_use = (TreatmentExposure.objects.filter(drug=obj).count()
                          + PrescriptionItem.objects.filter(drug=obj).count())
                if in_use:
                    self.stdout.write(self.style.WARNING(
                        f"  keeping device row {obj.generic_name!r}: "
                        f"{in_use} clinical record(s) reference it"))
                    continue
                if dry_run:
                    deleted_rows += 1
                    continue
                AdverseEvent.objects.filter(suspected_drug=obj).update(
                    suspected_drug=None)
                obj.delete()
                deleted_rows += 1

        for name, base, losers, nb, ns in plan[:20]:
            self.stdout.write(
                f"  {name}  +  {', '.join(losers[:3])}"
                f"{' ...' if len(losers) > 3 else ''}"
                f"  ->  {base!r}  ({nb} brands, {ns} strengths)")
        if len(plan) > 20:
            self.stdout.write(f"  ... and {len(plan) - 20} more groups")
        if devices:
            self.stdout.write(
                f"  delete {len(devices)} device row(s): "
                f"{', '.join(o.generic_name for o in devices[:5])}"
                f"{' ...' if len(devices) > 5 else ''}")
        self.stdout.write(self.style.WARNING(
            f"  {'DRY RUN: would ' if dry_run else ''}merge {merged_rows} "
            f"group(s), delete {deleted_rows} row(s), repoint {repointed} "
            f"FK reference(s)"))


    def _accumulate(self, csv_path: Path) -> dict:
        """Stream the CSV and accumulate per-generic data.

        MedEx qualifiers are folded off the generic name here (see
        `split_generic`) so a base generic accumulates the brands and
        strengths of every form it is sold in, plus the routes those forms
        imply.
        """
        generics = defaultdict(lambda: {
            "brands": set(),
            "strengths": set(),
            "therapeutic_classes": set(),
            "routes": set(),
            "strengths_by_route": defaultdict(set),
        })

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            skipped_devices = skipped_long = folded = 0
            for row in reader:
                count += 1
                if count % 5000 == 0:
                    self.stdout.write(f"  ... {count} rows read ...")

                generic = (row.get("generic_name") or "").strip()
                if not generic:
                    continue
                if is_device(generic):
                    skipped_devices += 1
                    continue
                base, route = split_generic(generic)
                if base != generic:
                    folded += 1
                brand = (row.get("name") or "").strip()
                strength = (row.get("strength") or "").strip()
                tclass = (row.get("therapeutic_class") or "").strip()
                form_routes = routes_from_dosage_form(row.get("dosage_form"))

                data = generics[base]
                # Brand name: include if it differs from the generic name.
                # Over-long brands would overflow PrescriptionItem.brand.
                if brand and brand.lower() != base.lower():
                    if len(brand) > MAX_BRAND:
                        skipped_long += 1
                    else:
                        data["brands"].add(brand)
                if strength:
                    # An over-long strength would be offered in the prescription
                    # form's strength picker and then overflow
                    # PrescriptionItem.strength/dose on PostgreSQL.
                    if len(strength) > MAX_STRENGTH:
                        skipped_long += 1
                    else:
                        data["strengths"].add(strength)
                        for r in ({route} if route else set()) | form_routes:
                            data["routes"].add(r)
                            data["strengths_by_route"][r].add(strength)
                # A product with no strength still tells us its route.
                data["routes"].update(form_routes)
                if tclass:
                    data["therapeutic_classes"].add(tclass)

        if skipped_devices or skipped_long or folded:
            self.stdout.write(
                f"  Folding: {folded} qualified generics, "
                f"skipped {skipped_devices} device rows, "
                f"skipped {skipped_long} over-long brand names.")
        self.stdout.write(f"  Done. {count} rows, {len(generics)} unique generics.")
        return generics
