"""Routes for products the catalogue files only as "Injection".

`dosage_form` usually names the route ("IV Injection", "SC Injection"). For
154 generics it says just "Injection" or "Infusion", which does not say
whether the product is IV, IM or SC. Those fell back to DrugMaster's default
of PO, so the prescription form offered an injection as oral and printed
"PO" on the slip.

A guess would be worse than the bug: IV lidocaine-with-adrenaline, IM
heparin and IV premixed insulin are all harmful. So this module answers only
where a published label or a national immunisation reference states the
route, and everything else is recorded as `Route.INJ` — "Injection (route
not specified)". That prints "INJ" rather than a claim the catalogue never
made, and the prescriber picks the route on the form.

Rules are tried in order and the first match wins, so a specific rule is
placed above the family rule it would otherwise fall into (yellow fever
above vaccines, IVIG above the immunoglobulins given IM).

Sources, per group:

* Vaccines and toxoids IM; yellow fever SC; MMR, PPSV23 and varicella IM or
  Subcut; MenACWY, PCV, HepA, HepB, HPV, influenza, Td/Tdap IM --
  Immunize.org "Administering Vaccines to Adults: Dose, Route, Site, and
  Needle Size" (p3084), and Typhim Vi (typhoid Vi polysaccharide) IM by the
  manufacturer's leaflet.
* Vincristine IV only -- FDA label: "INDICATED FOR INTRAVENOUS USE ONLY --
  FATAL IF GIVEN BY OTHER ROUTES"; intrathecal use is usually fatal.
* Heparin IV or deep SC, never IM (haematoma) -- FDA heparin sodium label.
* Premixed insulin 70/30 SC only, not IV or IM -- Humulin 70/30 label.
* Epoetin alfa and methoxy polyethylene glycol-epoetin beta (Mircera) IV or
  SC -- FDA/EMA product information.
* Procaine penicillin IM only, never IV (IV use causes convulsions, cardiac
  and respiratory arrest); streptomycin IM only, never IV -- FDA labels.
* Iron dextran (INFeD) IM or IV -- FDA label.
"""
from __future__ import annotations

import re

from treatments.models import Route

# (pattern matched against the lower-cased generic name, routes, note)
INJECTION_ROUTE_RULES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    # --- Vaccines, toxoids, immunoglobulins, antisera ---------------------
    (r"yellow fever", (Route.SC,), "YF-Vax is subcutaneous"),
    (r"\bvaccine|toxoid", (Route.IM,), "vaccines and toxoids are IM"),
    (r"antiserum|antivenom|anti-?venin", (Route.IV,), "antivenom is infused"),
    (r"immune serum globulin|intravenous immunoglobulin|\bivig\b",
     (Route.IV,), "IVIG"),
    (r"immunoglobulin|immune globulin|immuneglobulin|antitoxin",
     (Route.IM, Route.IV), "hyperimmune globulins"),
    # Combination vaccines the catalogue names by their diseases alone
    # ("Tetanus + Diphtheria", "Diphtheria + Pertussis + Tetanus").
    (r"diphtheria|pertussis|tetanus|measles|rubella|mumps|poliomyelitis",
     (Route.IM,), "vaccine named by its diseases"),

    # --- Insulins ---------------------------------------------------------
    (r"insulin", (Route.SC,), "premixed and analogue insulins are SC"),

    # --- Anticoagulants, antiplatelets, thrombolytics ---------------------
    (r"^heparin", (Route.IV, Route.SC), "never IM"),
    (r"fondaparinux", (Route.SC,), ""),
    (r"streptokinase|urokinase|alteplase|tenecteplase|tirofiban",
     (Route.IV,), ""),

    # --- Kidney-clinic injectables ---------------------------------------
    (r"epoetin|darbepoetin|epoetin beta", (Route.IV, Route.SC), ""),
    (r"iron sucrose|ferric carboxymaltose", (Route.IV,), ""),
    (r"iron.*dextran|dextran.*iron", (Route.IV, Route.IM), ""),
    (r"zoledronic|ibandronic|pamidronate", (Route.IV,), ""),
    (r"terlipressin", (Route.IV,), ""),
    (r"octreotide", (Route.SC, Route.IV), ""),
    (r"deferoxamine|desferrioxamine", (Route.IV, Route.IM, Route.SC), ""),

    # --- Antimicrobials ---------------------------------------------------
    (r"procaine penicillin|penicillin.*procaine|benzathine",
     (Route.IM,), "IV use is fatal"),
    (r"streptomycin", (Route.IM,), "IM only"),
    (r"benzyl ?penicillin", (Route.IV, Route.IM), ""),
    (r"cefazolin|ceftriaxone|ceftazidime|cefotaxime|cefuroxime sodium",
     (Route.IV, Route.IM), ""),
    (r"polymyxin b", (Route.IV, Route.IM), ""),
    (r"artemether", (Route.IM,), ""),
    (r"quinine dihydrochloride", (Route.IV,), ""),

    # --- Cytotoxics and biologics ----------------------------------------
    (r"vincristine", (Route.IV,), "IV only; intrathecal use is fatal"),
    (r"vinblastine|vinorelbine", (Route.IV,), ""),
    (r"bleomycin|topotecan|mitomycin|cabazitaxel|carfilzomib|paclitaxel|"
     r"doxorubicin|fluorouracil|trilaciclib|obinutuzumab|rituximab|"
     r"infliximab|casirivimab|imdevimab", (Route.IV,), ""),
    (r"peginterferon|secukinumab|adalimumab|etanercept|denosumab|"
     r"filgrastim|lenograstim|lenograstrim", (Route.SC,), ""),
    (r"liraglutide|semaglutide|dulaglutide|exenatide|tirzepatide",
     (Route.SC,), ""),
    (r"follitropin|urofollitropin|follicle stimulating hormone|"
     r"choriogonadotropin|cetrorelix|degarelix|leuprolide|triptorelin|"
     r"goserelin", (Route.SC,), ""),
    (r"antihemophilic|factor viii|eptacog|von willebrand", (Route.IV,), ""),

    # --- Fluids, nutrition, blood products, contrast ---------------------
    (r"^dextrose|^glucose|dextran|starch|polygeline|albumin human|"
     r"vamin|intralipid|soyabean oil|amino acid|emulsion for infusion",
     (Route.IV,), ""),
    (r"ringer|hartmann|sodium lactate|"
     r"calcium chloride.*potassium chloride.*sodium chloride",
     (Route.IV,), "electrolyte infusion"),
    (r"iopamidol|iodixanol|iohexol|ioversol|gadoteric|gadobutrol|"
     r"gadodiamide|verteporfin", (Route.IV,), "contrast / photosensitiser"),

    # --- Anaesthesia, resuscitation, peri-operative ----------------------
    (r"atracurium|cisatracurium|pancuronium|pipecuronium|rocuronium|"
     r"vecuronium|suxamethonium|etomidate|remifentanil|propofol|thiopental",
     (Route.IV,), ""),
    (r"^adrenaline$|^epinephrine$|^adrenaline \(epinephrine\)$",
     (Route.IM, Route.IV, Route.SC), "single-ingredient only"),
    (r"^atropine", (Route.IV, Route.IM, Route.SC), ""),
    (r"neostigmine|glycopyrron|glycopyrrolate", (Route.IV, Route.IM), ""),
    (r"levosimendan|nikethamide", (Route.IV,), ""),
    (r"carboprost", (Route.IM,), ""),
    (r"botulinum", (Route.IM,), ""),

    # --- Other parenterals seen in the catalogue -------------------------
    (r"pethidine|pentazocine|morphine|nalbuphine",
     (Route.IM, Route.IV, Route.SC), ""),
    (r"phenobarb", (Route.IM, Route.IV), ""),
    (r"prochlorperazine", (Route.IM,), ""),
    (r"aminocaproic", (Route.IV,), ""),
    (r"magnesium sulphate|magnesium sulfate", (Route.IV, Route.IM), ""),
    (r"nandrolone|testosterone", (Route.IM,), "oily depot injection"),
    (r"metamizol|dipyrone", (Route.IV, Route.IM), ""),
    (r"^cimetidine|^ranitidine", (Route.IV, Route.IM), ""),
    (r"vitamin b|calcium pantothenate|multivitamin|vitamin a",
     (Route.IM, Route.IV), ""),
    (r"amisulpride", (Route.IV, Route.IM), ""),
)

_COMPILED = tuple((re.compile(p), routes) for p, routes, _n in
                  INJECTION_ROUTE_RULES)


def routes_for_injection(generic_name: str) -> tuple[str, ...]:
    """Routes for an injection whose dosage form does not name one.

    Returns ``(Route.INJ,)`` when no rule matches: the product is an
    injection, but which injection is not something the catalogue says and
    not something to guess. A combination product only matches a rule whose
    pattern allows it, so "Lidocaine + Adrenaline" (infiltration) never
    picks up adrenaline's systemic routes.
    """
    name = (generic_name or "").strip().lower()
    if not name:
        return (Route.INJ,)
    for pattern, routes in _COMPILED:
        if pattern.search(name):
            return tuple(routes)
    return (Route.INJ,)
