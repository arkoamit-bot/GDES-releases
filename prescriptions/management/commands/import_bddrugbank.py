"""
Import BDDrugBank generics and brand names into DrugMaster.

Usage:
    python manage.py import_bddrugbank /path/to/medex_merged.csv [--dry-run] [--limit N]

- Existing DrugMaster generics get new Bangladeshi brand names and strengths
  merged in (deduped; brand names and strengths are additive).
- DrugClass is upgraded where the BDDrugBank therapeutic class or generic
  name confirms a known research class (e.g. an "OTHER" row whose BD
  therapeutic class says "Statins").
- New generics not matching any existing row are created with DrugClass.OTHER
  and receive all BD brand names + strengths.
- Mechanism: exact normalized match on generic name, plus a curated synonym
  dictionary for salt-form variants (e.g. "Metformin Hydrochloride" ->
  "Metformin"). Combination products and different drugs that share a word
  are NOT merged — they get their own DrugMaster row.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

from django.core.management.base import BaseCommand

from treatments.models import DrugClass, DrugMaster


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
    "Ciprofloxacin": "Ciprofloxacin",
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
    "Omeprazole": "Omeprazole",
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
    "Atorvastatin Calcium": "Atorvastatin",
    "Atorvastatin calcium": "Atorvastatin",
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
    "Zoledronic Acid": "Zoledronic acid",
    "Pembrolizumab": "Pembrolizumab",
    "Nivolumab": "Nivolumab",
    "Atezolizumab": "Atezolizumab",
    "Avelumab": "Avelumab",
    "Durvalumab": "Durvalumab",
    "Rituximab": "Rituximab",
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
    "Bicalutamide": "Bicalutamide",
    "Nilutamide": "Nilutamide",
    "Enzalutamide": "Enzalutamide",
    "Abiraterone": "Abiraterone",
    "Degarelix": "Degarelix",
    "Histrelin": "Histrelin",
    "Goserelin": "Goserelin",
    "Leuprolide": "Leuprolide",
    "Triptorelin": "Triptorelin",
    "Buserelin": "Buserelin",
    "Nafarelin": "Nafarelin",
    "Cetrorelix": "Cetrorelix",
    "Ganirelix": "Ganirelix",
    "Cetrorelix": "Cetrorelix",
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
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def classify_drug(generic_name: str, therapeutic_classes: list[str]) -> DrugClass:
    """Map a BDDrugBank generic to a BGDDR DrugClass."""
    g = (generic_name or "").lower()
    tc = " ".join(t.lower() for t in therapeutic_classes)

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
    if any(k in g for k in steroids):
        return DrugClass.STEROID
    if "mycophenolate" in g:
        return DrugClass.MMF
    if "azathioprine" in g:
        return DrugClass.AZATHIOPRINE
    if "cyclophosphamide" in g:
        return DrugClass.CYCLOPHOSPHAMIDE
    cni = ["cyclosporine", "ciclosporin", "tacrolimus",
           "rapamycin", "everolimus", "sirolimus"]
    if any(k in g for k in cni):
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
    statins_kw = ["atorvastatin", "rosuvastatin", "simvastatin",
                  "pravastatin", "fluvastatin", "pitavastatin",
                  "lovastatin", "statin"]
    if any(k in g for k in statins_kw) or any(k in tc for k in statins_kw):
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
            help="Path to BDDrugBank medex_merged.csv",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would change without saving to the database",
        )
        parser.add_argument(
            "--limit", type=int, default=0,
            help="Stop after this many generics (0 = process all; for testing)",
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

        created = updated = brands_added = strengths_added = 0
        class_upgrades = 0

        for idx, (generic, data) in enumerate(sorted(generics.items()), 1):
            # Resolve canonical generic via synonym map, then exact match
            canonical = SYNONYMS.get(generic, generic)
            drug_class = classify_drug(canonical, data["therapeutic_classes"])
            brands = sorted(data["brands"])
            strengths = sorted(data["strengths"])

            try:
                obj = DrugMaster.objects.get(generic_name=canonical)
                # Merge brand names (deduped)
                existing_brands = set(obj.brand_names or [])
                new_brands = [b for b in brands if b not in existing_brands]
                if new_brands:
                    obj.brand_names = sorted(existing_brands | set(brands))
                    brands_added += len(new_brands)
                # Merge strengths (deduped)
                existing_strengths = set(obj.available_strengths or [])
                new_strengths = [s for s in strengths
                                 if s not in existing_strengths]
                if new_strengths:
                    obj.available_strengths = sorted(existing_strengths |
                                                     set(strengths))
                    strengths_added += len(new_strengths)
                # Upgrade DrugClass if it was OTHER and we now have a match
                if obj.drug_class == DrugClass.OTHER and \
                   drug_class != DrugClass.OTHER:
                    obj.drug_class = drug_class
                    class_upgrades += 1
                obj.save()
                updated += 1
            except DrugMaster.DoesNotExist:
                if dry_run:
                    created += 1
                    continue
                obj = DrugMaster.objects.create(
                    generic_name=canonical,
                    drug_class=drug_class,
                    available_strengths=strengths,
                    brand_names=brands,
                )
                created += 1

            if idx % 2000 == 0:
                self.stdout.write(
                    f"  ... {idx}/{len(generics)} generics processed "
                    f"(created={created}, updated={updated}, "
                    f"brands={brands_added}) ...")

            if limit and idx >= limit:
                break

        if dry_run:
            self.stdout.write(self.style.WARNING("--- DRY RUN ---"))

        total_db = DrugMaster.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\n{'DRY RUN' if dry_run else 'IMPORT COMPLETE'}:\n"
            f"  New generics created : {created}\n"
            f"  Existing updated     : {updated}\n"
            f"  New brand names added: {brands_added}\n"
            f"  New strengths added  : {strengths_added}\n"
            f"  DrugClass upgrades   : {class_upgrades}\n"
            f"  Total generics in DB : {total_db}"
        ))

    def _accumulate(self, csv_path: Path) -> dict:
        """Stream the CSV and accumulate per-generic data."""
        generics = defaultdict(lambda: {
            "brands": set(),
            "strengths": set(),
            "therapeutic_classes": set(),
        })

        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                count += 1
                if count % 5000 == 0:
                    self.stdout.write(f"  ... {count} rows read ...")

                generic = (row.get("generic_name") or "").strip()
                if not generic:
                    continue
                brand = (row.get("name") or "").strip()
                strength = (row.get("strength") or "").strip()
                tclass = (row.get("therapeutic_class") or "").strip()

                data = generics[generic]
                # Brand name: include if it differs from the generic name
                if brand and brand.lower() != generic.lower():
                    data["brands"].add(brand)
                if strength:
                    data["strengths"].add(strength)
                if tclass:
                    data["therapeutic_classes"].add(tclass)

        self.stdout.write(f"  Done. {count} rows, {len(generics)} unique generics.")
        return generics
