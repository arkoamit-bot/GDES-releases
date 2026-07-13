"""
Seed DrugMaster with the BGDDR nephrology formulary.

Sourced from the BIRDEM GN projects' drug database (common Bangladeshi brand
names, most-used first), mapped to the research drug_class each analysis needs,
with per-route strengths where a drug is given by more than one route
(e.g. cyclophosphamide PO tablets vs IV vials — Endoxan 200 mg/500 mg/1 g,
per medex.com.bd).

    python manage.py seed_drugs

Idempotent: update_or_create keyed on generic_name.
"""
from django.core.management.base import BaseCommand

from treatments.models import DrugClass, DrugMaster

# (generic, class, strengths, default_freq, brands, renal_adjust,
#  egfr_caution_below, routes, strengths_by_route)
# routes: first entry is the default route. None -> ["PO"].
# strengths_by_route: only needed when strengths differ per route.
DRUGS = [
    # --- RAAS blockade ------------------------------------------------------
    ("Ramipril", DrugClass.RAASI, ["1.25 mg", "2.5 mg", "5 mg", "10 mg"],
     "1+0+0", ["Cardace", "Tritace", "Ramace"], True, None, None, None),
    ("Enalapril", DrugClass.RAASI, ["5 mg", "10 mg"], "1+0+1",
     ["Renitec", "Enam", "Enapril"], True, None, None, None),
    ("Lisinopril", DrugClass.RAASI, ["5 mg", "10 mg"], "1+0+0",
     ["Zestril", "Lisinor", "Listril"], True, None, None, None),
    ("Losartan", DrugClass.RAASI, ["25 mg", "50 mg", "100 mg"], "1+0+0",
     ["Cozaar", "Losacar", "Repace", "Losar"], True, None, None, None),
    ("Telmisartan", DrugClass.RAASI, ["40 mg", "80 mg"], "1+0+0",
     ["Micardis", "Telma", "Telsan", "Provas"], True, None, None, None),
    ("Valsartan", DrugClass.RAASI, ["80 mg", "160 mg"], "1+0+0",
     ["Diovan", "Valzaar", "Valsar", "Disys"], True, None, None, None),

    # --- SGLT2i / ns-MRA ----------------------------------------------------
    ("Dapagliflozin", DrugClass.SGLT2I, ["5 mg", "10 mg"], "1+0+0",
     ["Forxiga", "Dapavel", "Oxra", "Dapacose"], True, 25, None, None),
    ("Empagliflozin", DrugClass.SGLT2I, ["10 mg", "25 mg"], "1+0+0",
     ["Jardiance", "Empavel", "Gibtulio"], True, 20, None, None),
    ("Finerenone", DrugClass.FINERENONE, ["10 mg", "20 mg"], "1+0+0",
     ["Kerendia"], True, 25, None, None),

    # --- Immunomodulators / immunosuppression -------------------------------
    ("Hydroxychloroquine", DrugClass.HCQ, ["200 mg"], "1+0+1",
     ["Plaquenil", "Hydroquin", "HCQS"], False, None, None, None),
    ("Prednisolone", DrugClass.STEROID, ["5 mg", "10 mg", "20 mg"], "1+0+0",
     ["Deltasone", "Wysolone", "Prednin", "Cortisol"], False, None, None, None),
    ("Methylprednisolone", DrugClass.STEROID, ["4 mg", "16 mg"], "1+0+0",
     ["Medrol", "Solu-Medrol", "Methylpred"], False, None, ["PO", "IV"],
     {"PO": ["4 mg", "16 mg"], "IV": ["500 mg vial", "1 g vial"]}),
    ("Budesonide", DrugClass.STEROID, ["3 mg", "4 mg (TRF)", "9 mg"], "1+0+0",
     ["Nefecon", "Tarpeyo", "Budenofalk", "Entocort"], False, None, None, None),
    ("Mycophenolate mofetil", DrugClass.MMF, ["250 mg", "500 mg"], "1+0+1",
     ["CellCept", "Mofilet", "Renodapt", "Mycept"], True, None, None, None),
    ("Azathioprine", DrugClass.AZATHIOPRINE, ["50 mg"], "1+0+0",
     ["Imuran", "Azoran", "Thiopress"], True, None, None, None),
    ("Cyclophosphamide", DrugClass.CYCLOPHOSPHAMIDE, ["50 mg"], "1+0+0",
     ["Endoxan", "Cycloxan", "Cytoxan"], True, 30, ["PO", "IV"],
     {"PO": ["50 mg"], "IV": ["200 mg vial", "500 mg vial", "1 g vial"]}),
    ("Cyclosporine", DrugClass.CNI, ["25 mg", "50 mg", "100 mg"], "1+0+1",
     ["Sandimmun", "Cyclophil", "Arpimune", "Imusporin"], True, None, None, None),
    ("Tacrolimus", DrugClass.CNI, ["0.5 mg", "1 mg"], "1+0+1",
     ["Prograf", "Pangraf", "Tacrograf", "Tacromus"], True, None, None, None),
    ("Rituximab", DrugClass.RITUXIMAB, ["100 mg/10 mL", "500 mg/50 mL"],
     "infusion", ["MabThera", "Reditux", "Ikgdar"], False, None, ["IV"], None),
    ("Chlorambucil", DrugClass.OTHER, ["2 mg", "5 mg"], "1+0+0",
     ["Leukeran", "Clokeran"], True, 30, None, None),

    # --- Diuretics / statins ------------------------------------------------
    ("Furosemide", DrugClass.DIURETIC, ["40 mg"], "1+0+0",
     ["Lasix", "Frusenex", "Fusid"], False, None, ["PO", "IV"],
     {"PO": ["40 mg"], "IV": ["20 mg/2 mL amp"]}),
    ("Spironolactone", DrugClass.DIURETIC, ["25 mg", "50 mg"], "1+0+0",
     ["Aldactone", "Spiractin"], False, 30, None, None),
    ("Atorvastatin", DrugClass.STATIN, ["10 mg", "20 mg", "40 mg"], "0+0+1",
     ["Lipitor", "Atorva", "Tonact", "Storvas"], False, None, None, None),
    ("Rosuvastatin", DrugClass.STATIN, ["5 mg", "10 mg", "20 mg"], "0+0+1",
     ["Crestor", "Rosuvas", "Rozucor", "Roseday"], False, 30, None, None),

    # --- CKD-MBD / anaemia / supportive --------------------------------------
    ("Calcium carbonate", DrugClass.OTHER, ["500 mg"], "1+1+1",
     ["Calcirol", "Shelcal", "Calcimax"], False, None, None, None),
    ("Sevelamer", DrugClass.OTHER, ["400 mg", "800 mg"], "1+1+1",
     ["Renvela", "Sevcar", "Phoscut"], False, None, None, None),
    ("Epoetin alfa", DrugClass.OTHER, ["2000 IU", "4000 IU", "10000 IU"],
     "weekly", ["Eprex", "Wepox", "Epotin"], False, None, ["SC", "IV"], None),
    ("Iron sucrose", DrugClass.OTHER, ["100 mg/5 mL"], "infusion",
     ["Venofer", "Fersigard", "Fersoft"], False, None, ["IV"], None),
    ("Cholecalciferol", DrugClass.OTHER, ["20000 IU", "40000 IU"], "weekly",
     ["D-Rise", "Uprise", "Devita"], False, None, None, None),
    ("Paricalcitol", DrugClass.OTHER, ["1 mcg", "2 mcg"], "1+0+0",
     ["Zemplar", "Paricel"], False, None, None, None),
    ("Sodium bicarbonate", DrugClass.OTHER, ["500 mg"], "1+1+1",
     ["Soda bicarb", "Alkasol"], False, None, None, None),
    ("Allopurinol", DrugClass.OTHER, ["100 mg", "300 mg"], "1+0+0",
     ["Zyloric", "Alloril", "Uricon"], True, 30, None, None),
    ("Colchicine", DrugClass.OTHER, ["0.6 mg"], "0+0+1",
     ["Colcrys", "Goutnil", "Zycolchin"], True, 10, None, None),

    # --- Anticoagulation ----------------------------------------------------
    ("Heparin", DrugClass.OTHER, ["5000 IU/mL"], "1+0+1",
     ["HepLock", "Neparin"], False, None, ["SC", "IV"], None),
    ("Warfarin", DrugClass.OTHER, ["1 mg", "2 mg", "5 mg"], "0+0+1",
     ["Coumadin", "Warf", "Uniwarfin"], False, None, None, None),
    ("Rivaroxaban", DrugClass.OTHER, ["10 mg", "15 mg", "20 mg"], "1+0+0",
     ["Xarelto", "Rivaxa", "Rivaro"], True, 15, None, None),
    ("Apixaban", DrugClass.OTHER, ["2.5 mg", "5 mg"], "1+0+1",
     ["Eliquis", "Apigat", "Apixia"], True, 15, None, None),

    # --- Prophylaxis / infection / GI / bone --------------------------------
    ("Cotrimoxazole", DrugClass.OTHER, ["480 mg", "960 mg"], "1+0+0",
     ["Bactrim", "Septran", "Cotrim"], True, 30, None, None),
    ("Isoniazid", DrugClass.OTHER, ["300 mg"], "1+0+0",
     ["INH", "Isokin"], False, None, None, None),
    ("Rifampicin", DrugClass.OTHER, ["450 mg", "600 mg"], "1+0+0",
     ["Rifadin", "Rcin"], False, None, None, None),
    ("Valacyclovir", DrugClass.OTHER, ["500 mg"], "1+0+0",
     ["Valtrex", "Valcivir"], True, 30, None, None),
    ("Pantoprazole", DrugClass.OTHER, ["20 mg", "40 mg"], "1+0+0",
     ["Protonix", "Pantodac", "Pantop"], False, None, None, None),
    ("Calcium + Vitamin D", DrugClass.OTHER, ["500 mg + 400 IU"], "1+0+1",
     ["Shelcal", "Calcirol D"], False, None, None, None),
    ("Alendronate", DrugClass.OTHER, ["70 mg"], "weekly",
     ["Fosamax", "Osteofos", "Restofos"], False, 35, None, None),
    ("Risedronate", DrugClass.OTHER, ["35 mg"], "weekly",
     ["Actonel", "Risedron"], False, 30, None, None),
    ("Zoledronic acid", DrugClass.OTHER, ["4 mg vial", "5 mg vial"], "yearly",
     ["Aclasta", "Zometa", "Zoledron"], True, 35, ["IV"], None),
    # Strongyloidiasis prophylaxis (loading) before/with immunosuppression, esp.
    # steroids — pre-empts hyperinfection in an endemic setting.
    ("Ivermectin", DrugClass.OTHER, ["3 mg", "6 mg", "12 mg"], "stat (loading)",
     ["Ivera", "Scabo", "Ivexterm"], False, None, None, None),

    # --- Antidiabetics (glycaemic control incl. steroid-induced) ------------
    ("Metformin", DrugClass.METFORMIN, ["500 mg", "850 mg", "1000 mg"], "1+0+1",
     ["Comet", "Metfo", "Glucophage", "Diabex"], True, 30, None, None),
    ("Gliclazide", DrugClass.SULFONYLUREA, ["30 mg MR", "60 mg MR", "80 mg"], "1+0+0",
     ["Comprid", "Diamicron", "Gliclide"], True, 30, None, None),
    ("Glimepiride", DrugClass.SULFONYLUREA, ["1 mg", "2 mg", "3 mg", "4 mg"], "1+0+0",
     ["Amaryl", "Secrin", "Glime"], True, 30, None, None),
    ("Sitagliptin", DrugClass.DPP4I, ["25 mg", "50 mg", "100 mg"], "1+0+0",
     ["Januvia", "Sita", "Dpp"], True, None, None, None),
    ("Linagliptin", DrugClass.DPP4I, ["5 mg"], "1+0+0",
     ["Trajenta", "Lina", "Ondero"], False, None, None, None),
    ("Vildagliptin", DrugClass.DPP4I, ["50 mg"], "1+0+1",
     ["Galvus", "Vilda", "Jalra"], True, None, None, None),
    ("Liraglutide", DrugClass.GLP1, ["6 mg/mL pen"], "1+0+0",
     ["Victoza"], False, None, ["SC"], None),
    ("Semaglutide", DrugClass.GLP1, ["0.25 mg pen", "0.5 mg pen", "1 mg pen"], "once weekly",
     ["Ozempic", "Rybelsus"], False, None, ["SC"], None),
    ("Insulin (soluble/regular)", DrugClass.INSULIN, ["100 IU/mL"], "1+1+1",
     ["Actrapid", "Humulin R", "Maxsulin R"], False, None, ["SC", "IV"], None),
    ("Insulin isophane (NPH)", DrugClass.INSULIN, ["100 IU/mL"], "1+0+1",
     ["Insulatard", "Humulin N", "Maxsulin N"], False, None, ["SC"], None),
    ("Premixed insulin 70/30", DrugClass.INSULIN, ["100 IU/mL"], "1+0+1",
     ["Mixtard 30", "Humulin 70/30", "Novomix 30"], False, None, ["SC"], None),
    ("Insulin glargine", DrugClass.INSULIN, ["100 IU/mL"], "0+0+1",
     ["Lantus", "Basalog", "Glaritus"], False, None, ["SC"], None),
    ("Insulin aspart", DrugClass.INSULIN, ["100 IU/mL"], "1+1+1",
     ["Novorapid", "Fiasp"], False, None, ["SC"], None),
]


class Command(BaseCommand):
    help = "Seed the nephrology DrugMaster formulary (Bangladeshi brands)."

    def handle(self, *args, **options):
        created = updated = 0
        for (generic, cls, strengths, freq, brands, renal, egfr,
             routes, sbr) in DRUGS:
            routes = routes or ["PO"]
            obj, was_created = DrugMaster.objects.update_or_create(
                generic_name=generic,
                defaults=dict(
                    drug_class=cls, available_strengths=strengths,
                    default_frequency=freq, brand_names=brands,
                    renal_dose_adjust=renal, egfr_caution_below=egfr,
                    default_route=routes[0], available_routes=routes,
                    strengths_by_route=sbr or {},
                ),
            )
            created += was_created
            updated += not was_created
        self.stdout.write(self.style.SUCCESS(
            f"DrugMaster seeded: {created} created, {updated} updated."))
