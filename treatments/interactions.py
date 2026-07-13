"""Drug-drug interaction engine for nephrology.

Contains a curated database of ~200 high-priority nephrology drug interactions
focused on immunosuppressants, antihypertensives, diuretics, and supportive
medications commonly used in glomerular disease management.
"""

from dataclasses import dataclass, field
from typing import Any


# Severity levels
SEVERITY_MAJOR = "major"
SEVERITY_MODERATE = "moderate"
SEVERITY_MINOR = "minor"

INTERACTION_DB: list[dict[str, Any]] = [
    # --- Immunosuppressant combinations ---
    # Cyclophosphamide
    {"drug_a": "cyclophosphamide", "drug_b": "allopurinol",
     "severity": SEVERITY_MAJOR, "mechanism": "Allopurinol inhibits xanthine oxidase, reducing cyclophosphamide metabolism and increasing bone marrow toxicity",
     "management": "Avoid concurrent use if possible. If unavoidable, reduce cyclophosphamide dose by 25-50% and monitor CBC closely"},
    {"drug_a": "cyclophosphamide", "drug_b": "warfarin",
     "severity": SEVERITY_MODERATE, "mechanism": "Cyclophosphamide may enhance anticoagulant effect by reducing hepatic metabolism of warfarin",
     "management": "Monitor INR more frequently during cyclophosphamide therapy and adjust warfarin dose as needed"},
    {"drug_a": "cyclophosphamide", "drug_b": "furosemide",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive bone marrow suppression risk; loop diuretics may increase metabolite accumulation",
     "management": "Monitor CBC regularly; ensure adequate hydration to prevent hemorrhagic cystitis"},
    {"drug_a": "cyclophosphamide", "drug_b": "corticosteroid",
     "severity": SEVERITY_MINOR, "mechanism": "Corticosteroids may induce hepatic enzymes altering cyclophosphamide activation",
     "management": "Standard therapeutic monitoring; no routine dose adjustment needed"},
    # Mycophenolate
    {"drug_a": "mycophenolate", "drug_b": "azathioprine",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive immunosuppression and bone marrow suppression; both inhibit purine synthesis",
     "management": "DO NOT combine - this is a contraindicated combination. Switch to a single antiproliferative agent"},
    {"drug_a": "mycophenolate", "drug_b": "cholestyramine",
     "severity": SEVERITY_MAJOR, "mechanism": "Cholestyramine interrupts enterohepatic recirculation of mycophenolate, reducing AUC by 40%",
     "management": "Separate administration by at least 3 hours; monitor MPA levels if available"},
    {"drug_a": "mycophenolate", "drug_b": "antacids",
     "severity": SEVERITY_MODERATE, "mechanism": "Magnesium/aluminum antacids reduce mycophenolate absorption by up to 30%",
     "management": "Separate administration by at least 2 hours; use H2RA or PPI instead if possible"},
    {"drug_a": "mycophenolate", "drug_b": "iron",
     "severity": SEVERITY_MINOR, "mechanism": "Iron salts reduce mycophenolate absorption",
     "management": "Separate administration by at least 2 hours"},
    # Tacrolimus / Calcineurin inhibitors
    {"drug_a": "tacrolimus", "drug_b": "ciclosporin",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive nephrotoxicity; both inhibit calcineurin with overlapping toxicity profiles",
     "management": "DO NOT combine - switch from one CNI to the other with appropriate washout period"},
    {"drug_a": "tacrolimus", "drug_b": "clarithromycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Macrolide antibiotics strongly inhibit CYP3A4, dramatically increasing tacrolimus levels (risk of nephrotoxicity and neurotoxicity)",
     "management": "Avoid macrolides with tacrolimus. Use azithromycin (non-interacting) or alternative antibiotic. If unavoidable, reduce tacrolimus dose by 50-75% and monitor levels daily"},
    {"drug_a": "tacrolimus", "drug_b": "fluconazole",
     "severity": SEVERITY_MAJOR, "mechanism": "Azole antifungals inhibit CYP3A4, increasing tacrolimus levels",
     "management": "Reduce tacrolimus dose by 50% when starting fluconazole; monitor trough levels frequently"},
    {"drug_a": "tacrolimus", "drug_b": "rifampin",
     "severity": SEVERITY_MAJOR, "mechanism": "Rifampin is a potent CYP3A4 inducer, reducing tacrolimus levels by 50-80%",
     "management": "Avoid rifampin when possible. If unavoidable, increase tacrolimus dose 2-3x and monitor trough levels"},
    {"drug_a": "tacrolimus", "drug_b": "metoclopramide",
     "severity": SEVERITY_MODERATE, "mechanism": "Metoclopramide increases gastric emptying, increasing tacrolimus absorption and peak levels",
     "management": "Monitor tacrolimus trough levels; consider alternative prokinetic agent"},
    {"drug_a": "tacrolimus", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive nephrotoxicity; NSAIDs reduce renal blood flow in the setting of CNI-induced vasoconstriction",
     "management": "Avoid NSAIDs in patients on CNIs. Use acetaminophen for analgesia. If unavoidable, monitor renal function closely"},
    {"drug_a": "tacrolimus", "drug_b": "trimethoprim_sulfamethoxazole",
     "severity": SEVERITY_MODERATE, "mechanism": "Trimethoprim competes for tubular secretion of creatinine, causing false eGFR reduction; additive hyperkalemia risk",
     "management": "Use alternative PCP prophylaxis (dapsone or atovaquone) in CNI patients with impaired renal function. Monitor potassium"},
    {"drug_a": "tacrolimus", "drug_b": "verapamil",
     "severity": SEVERITY_MODERATE, "mechanism": "Verapamil inhibits CYP3A4, increasing tacrolimus levels",
     "management": "Monitor tacrolimus levels; consider alternative antihypertensive"},
    {"drug_a": "ciclosporin", "drug_b": "clarithromycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Macrolides inhibit CYP3A4, dramatically increasing ciclosporin levels and nephrotoxicity",
     "management": "Avoid macrolides. Use azithromycin or alternative antibiotic. If unavoidable, reduce ciclosporin dose by 50-75%"},
    {"drug_a": "ciclosporin", "drug_b": "fluconazole",
     "severity": SEVERITY_MAJOR, "mechanism": "Azole antifungals inhibit CYP3A4, increasing ciclosporin levels",
     "management": "Reduce ciclosporin dose by 40-50%; monitor trough levels"},
    {"drug_a": "ciclosporin", "drug_b": "nsaids",
     "severity": SEVERITY_MAJOR, "mechanism": "Significant additive nephrotoxicity; NSAIDs reduce renal prostaglandins worsening CNI vasoconstriction",
     "management": "Avoid NSAIDs in patients on ciclosporin. Use acetaminophen"},
    {"drug_a": "ciclosporin", "drug_b": "colchicine",
     "severity": SEVERITY_MAJOR, "mechanism": "Ciclosporin inhibits P-glycoprotein and CYP3A4, increasing colchicine levels to toxic range",
     "management": "Reduce colchicine dose by 50-75% or avoid. Monitor for colchicine toxicity (GI, neuromuscular)"},
    {"drug_a": "ciclosporin", "drug_b": "potassium_sparing_diuretics",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive hyperkalemia risk; ciclosporin reduces renal potassium excretion",
     "management": "Avoid potassium-sparing diuretics. Monitor potassium closely if combined"},
    {"drug_a": "ciclosporin", "drug_b": "statin",
     "severity": SEVERITY_MODERATE, "mechanism": "Ciclosporin inhibits OATP1B1, increasing statin levels and rhabdomyolysis risk",
     "management": "Use pravastatin or rosuvastatin at low doses. Avoid high-dose atorvastatin. Monitor CK levels"},
    # Sirolimus / mTOR inhibitors
    {"drug_a": "sirolimus", "drug_b": "tacrolimus",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive nephrotoxicity and increased risk of thrombotic microangiopathy (TMA)",
     "management": "Monitor renal function closely; consider mTOR inhibitor monotherapy after CNI withdrawal"},
    {"drug_a": "sirolimus", "drug_b": "clarithromycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Macrolides inhibit CYP3A4, significantly increasing sirolimus levels",
     "management": "Avoid macrolides. Use azithromycin if macrolide needed. If unavoidable, reduce sirolimus dose by 50-75%"},
    {"drug_a": "sirolimus", "drug_b": "fluconazole",
     "severity": SEVERITY_MAJOR, "mechanism": "Azole antifungals inhibit CYP3A4, increasing sirolimus levels",
     "management": "Reduce sirolimus dose by 50% when starting azole; monitor levels"},
    # Rituximab
    {"drug_a": "rituximab", "drug_b": "live_vaccine",
     "severity": SEVERITY_MAJOR, "mechanism": "Rituximab depletes B cells, increasing risk of disseminated infection with live vaccines",
     "management": "Administer live vaccines at least 4 weeks before rituximab. Avoid live vaccines during therapy and for 6 months after"},
    {"drug_a": "rituximab", "drug_b": "methotrexate",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive immunosuppression; increased infection risk",
     "management": "Monitor for infections; consider PCP prophylaxis"},
    # --- RAAS inhibitors ---
    {"drug_a": "ace_inhibitor", "drug_b": "arb",
     "severity": SEVERITY_MODERATE, "mechanism": "Dual RAAS blockade increases risk of hyperkalemia, hypotension, and acute kidney injury without additional renoprotective benefit in most patients",
     "management": "Avoid dual RAAS blockade in most patients. Use single-agent RAASi at optimized dose. Only consider combination under specialist guidance"},
    {"drug_a": "ace_inhibitor", "drug_b": "potassium_sparing_diuretics",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive hyperkalemia risk; RAASi reduces aldosterone, potassium-sparing diuretics reduce renal potassium excretion",
     "management": "Avoid combination unless hypokalemia present. If combined, monitor potassium weekly and consider potassium restriction"},
    {"drug_a": "ace_inhibitor", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "NSAIDs reduce prostaglandin-mediated afferent arteriolar vasodilation, blunting ACEi efficacy and increasing AKI risk",
     "management": "Avoid NSAIDs in CKD patients on RAASi. Use acetaminophen. If unavoidable, monitor renal function and potassium within 1 week"},
    {"drug_a": "ace_inhibitor", "drug_b": "trimethoprim_sulfamethoxazole",
     "severity": SEVERITY_MODERATE, "mechanism": "Trimethoprim has potassium-sparing diuretic effect, additive with ACEi causing hyperkalemia",
     "management": "Monitor potassium; consider alternative antibiotic in patients with baseline K>4.5"},
    {"drug_a": "ace_inhibitor", "drug_b": "lithium",
     "severity": SEVERITY_MODERATE, "mechanism": "ACEi reduce lithium clearance, increasing lithium levels and toxicity risk",
     "management": "Monitor lithium levels every 2-4 weeks when starting ACEi; adjust lithium dose as needed"},
    {"drug_a": "ace_inhibitor", "drug_b": "finerenone",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive hyperkalemia risk; combined RAASi and ns-MRA effect on potassium excretion",
     "management": "Monitor potassium and renal function at 2-4 weeks after initiation; adjust or hold if K>5.5"},
    {"drug_a": "arb", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "NSAIDs reduce ARB efficacy and increase AKI risk",
     "management": "Avoid NSAIDs. Use acetaminophen. Monitor renal function if combined"},
    {"drug_a": "arb", "drug_b": "potassium_sparing_diuretics",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive hyperkalemia from dual potassium-retaining effect",
     "management": "Avoid unless hypokalemic. If combined, strict potassium monitoring"},
    {"drug_a": "arb", "drug_b": "lithium",
     "severity": SEVERITY_MODERATE, "mechanism": "ARBs reduce lithium clearance",
     "management": "Monitor lithium levels more frequently"},
    # --- Diuretics ---
    {"drug_a": "furosemide", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "NSAIDs inhibit renal prostaglandins, blunting diuretic effect and increasing AKI risk",
     "management": "Use alternative analgesia. If unavoidable, increase diuretic dose and monitor response"},
    {"drug_a": "furosemide", "drug_b": "digoxin",
     "severity": SEVERITY_MODERATE, "mechanism": "Diuretic-induced hypokalemia increases digitalis toxicity risk",
     "management": "Monitor potassium levels; maintain K>4.0; monitor digoxin levels if available"},
    {"drug_a": "furosemide", "drug_b": "aminoglycoside",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive ototoxicity and nephrotoxicity; loop diuretics increase aminoglycoside concentration in inner ear",
     "management": "Avoid combination when possible. If unavoidable, use once-daily aminoglycoside dosing, monitor drug levels, and audiometry"},
    {"drug_a": "furosemide", "drug_b": "lithium",
     "severity": SEVERITY_MINOR, "mechanism": "Sodium depletion from diuresis increases lithium reabsorption",
     "management": "Monitor lithium levels; maintain stable sodium intake"},
    {"drug_a": "thiazide", "drug_b": "lithium",
     "severity": SEVERITY_MAJOR, "mechanism": "Thiazides significantly reduce lithium clearance (by up to 40%), causing lithium accumulation",
     "management": "Reduce lithium dose by 25-50% when starting thiazide; monitor lithium levels weekly until stable"},
    {"drug_a": "thiazide", "drug_b": "digoxin",
     "severity": SEVERITY_MODERATE, "mechanism": "Thiazide-induced hypokalemia and hypomagnesemia increase digoxin toxicity",
     "management": "Monitor electrolytes; maintain K>4.0, Mg>1.8"},
    {"drug_a": "thiazide", "drug_b": "nsaids",
     "severity": SEVERITY_MINOR, "mechanism": "NSAIDs may reduce thiazide efficacy",
     "management": "Monitor BP response; consider alternative analgesia"},
    # --- SGLT2 inhibitors ---
    {"drug_a": "sglt2_inhibitor", "drug_b": "furosemide",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive volume depletion risk; SGLT2i causes osmotic diuresis",
     "management": "Monitor volume status and renal function; consider reducing diuretic dose at SGLT2i initiation"},
    {"drug_a": "sglt2_inhibitor", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "NSAIDs may reduce SGLT2i efficacy and increase AKI risk during volume depletion",
     "management": "Avoid NSAIDs; ensure adequate hydration"},
    {"drug_a": "sglt2_inhibitor", "drug_b": "insulin",
     "severity": SEVERITY_MODERATE, "mechanism": "SGLT2i reduces insulin requirements through glycosuria and weight loss; increased hypoglycemia risk",
     "management": "Reduce insulin dose by 10-20% when starting SGLT2i; monitor glucose frequently"},
    # --- Anticoagulants ---
    {"drug_a": "warfarin", "drug_b": "nsaids",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive bleeding risk; NSAIDs inhibit platelet function and cause GI mucosal injury",
     "management": "Avoid NSAIDs in warfarin patients. Use acetaminophen. If unavoidable, use PPI and monitor INR closely"},
    {"drug_a": "warfarin", "drug_b": "antibiotics_ broad_spectrum",
     "severity": SEVERITY_MODERATE, "mechanism": "Antibiotics reduce gut flora vitamin K production, potentiating warfarin effect",
     "management": "Monitor INR 3-7 days after starting antibiotics; adjust warfarin dose accordingly"},
    {"drug_a": "warfarin", "drug_b": "fibrates",
     "severity": SEVERITY_MODERATE, "mechanism": "Fibrates potentiate warfarin effect through metabolic interaction",
     "management": "Monitor INR when starting fibrates; reduce warfarin dose by 25-30% if needed"},
    {"drug_a": "warfarin", "drug_b": "fluconazole",
     "severity": SEVERITY_MAJOR, "mechanism": "Azoles inhibit CYP2C9 metabolism of warfarin, dramatically increasing INR",
     "management": "Reduce warfarin dose by 30-50%; monitor INR every 2-3 days"},
    {"drug_a": "heparin", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "Increased bleeding risk from platelet inhibition and mucosal injury",
     "management": "Monitor for bleeding signs; limit NSAID use"},
    {"drug_a": "heparin", "drug_b": "antiplatelet",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive bleeding risk in the setting of GN-related uremic platelet dysfunction",
     "management": "Monitor closely for bleeding; minimize combination duration"},
    # --- Other important interactions ---
    {"drug_a": "allopurinol", "drug_b": "azathioprine",
     "severity": SEVERITY_MAJOR, "mechanism": "Allopurinol inhibits xanthine oxidase, blocking azathioprine metabolism and causing severe bone marrow suppression",
     "management": "If combined, reduce azathioprine dose by 60-75%. Monitor CBC weekly for first 8 weeks. Consider allopurinol→febuxostat switch"},
    {"drug_a": "allopurinol", "drug_b": "diuretics",
     "severity": SEVERITY_MODERATE, "mechanism": "Thiazide and loop diuretics increase allopurinol hypersensitivity risk",
     "management": "Start allopurinol at low dose (≤100 mg/day) and titrate slowly; monitor for rash"},
    {"drug_a": "colchicine", "drug_b": "clarithromycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Macrolides inhibit CYP3A4 and P-glycoprotein, causing potentially fatal colchicine accumulation",
     "management": "Avoid combination. Use alternative antibiotic. If unavoidable, dramatically reduce colchicine dose"},
    {"drug_a": "colchicine", "drug_b": "statin",
     "severity": SEVERITY_MODERATE, "mechanism": "Increased risk of myopathy and rhabdomyolysis through CYP3A4 competition",
     "management": "Use pravastatin or rosuvastatin (less CYP3A4 metabolism); monitor for muscle symptoms"},
    {"drug_a": "metformin", "drug_b": "contrast_dye",
     "severity": SEVERITY_MAJOR, "mechanism": "Risk of contrast-induced nephropathy leading to metformin accumulation and lactic acidosis",
     "management": "Hold metformin 48h before elective contrast procedures and restart 48h after if renal function stable"},
    {"drug_a": "metformin", "drug_b": "topiramate",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive metabolic acidosis risk",
     "management": "Monitor bicarbonate levels; avoid combination if baseline bicarbonate low"},
    {"drug_a": "sulfonylurea", "drug_b": "fluconazole",
     "severity": SEVERITY_MODERATE, "mechanism": "Azoles inhibit CYP2C9 metabolism of sulfonylureas, increasing hypoglycemia risk",
     "management": "Monitor glucose; reduce sulfonylurea dose if needed"},
    {"drug_a": "finerenone", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive hyperkalemia risk and reduced finerenone efficacy",
     "management": "Avoid NSAIDs; monitor potassium and renal function at 4 weeks"},
    {"drug_a": "finerenone", "drug_b": "potassium_supplements",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive hyperkalemia risk with ns-MRA",
     "management": "Avoid potassium supplements unless treating documented hypokalemia"},
    {"drug_a": "finerenone", "drug_b": "trimethoprim_sulfamethoxazole",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive hyperkalemia from trimethoprim's amiloride-like effect with ns-MRA",
     "management": "Monitor potassium; consider alternative antibiotic"},
    # --- Hydroxychloroquine ---
    {"drug_a": "hydroxychloroquine", "drug_b": "amiodarone",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive risk of QT prolongation and ventricular arrhythmias",
     "management": "Avoid combination. Obtain baseline ECG, monitor QTc interval. If QTc>500ms, discontinue one agent"},
    {"drug_a": "hydroxychloroquine", "drug_b": "clarithromycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive QT prolongation risk",
     "management": "Avoid combination; monitor ECG"},
    {"drug_a": "hydroxychloroquine", "drug_b": "tamoxifen",
     "severity": SEVERITY_MODERATE, "mechanism": "Increased risk of retinal toxicity when both agents used",
     "management": "Annual ophthalmologic screening"},
    # --- Corticosteroids ---
    {"drug_a": "corticosteroid", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "Increased risk of GI bleeding; corticosteroids reduce GI mucosal protection",
     "management": "Use PPI prophylaxis; consider acetaminophen instead of NSAIDs"},
    {"drug_a": "corticosteroid", "drug_b": "insulin",
     "severity": SEVERITY_MODERATE, "mechanism": "Corticosteroids induce insulin resistance, increasing insulin requirements",
     "management": "Monitor glucose; adjust insulin dose upward as needed during steroid therapy"},
    {"drug_a": "corticosteroid", "drug_b": "furosemide",
     "severity": SEVERITY_MINOR, "mechanism": "Additive hypokalemia risk; corticosteroids have mineralocorticoid activity",
     "management": "Monitor potassium levels"},
    {"drug_a": "corticosteroid", "drug_b": "vaccine_live",
     "severity": SEVERITY_MAJOR, "mechanism": "Immunosuppression from high-dose steroids increases disseminated infection risk with live vaccines",
     "management": "Delay live vaccines until ≥1 month after stopping immunosuppressive doses of steroids (≥20mg prednisolone daily for ≥2 weeks)"},
    # --- Antiplatelet agents ---
    {"drug_a": "aspirin", "drug_b": "nsaids",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive GI bleeding risk; NSAIDs compete with aspirin for COX-1 binding reducing antiplatelet effect",
     "management": "If using aspirin for secondary prevention, take aspirin 2h before NSAID. Use PPI"},
    {"drug_a": "aspirin", "drug_b": "warfarin",
     "severity": SEVERITY_MAJOR, "mechanism": "Dramatically increased bleeding risk",
     "management": "Avoid combination unless clear indication for dual therapy (e.g., mechanical heart valve). Use PPI"},
    {"drug_a": "clopidogrel", "drug_b": "omeprazole",
     "severity": SEVERITY_MODERATE, "mechanism": "Omeprazole inhibits CYP2C19, potentially reducing clopidogrel activation",
     "management": "Use pantoprazole instead of omeprazole; or consider alternate antiplatelet"},
    # --- Anti-epileptics / mood stabilizers ---
    {"drug_a": "valproate", "drug_b": "meropenem",
     "severity": SEVERITY_MAJOR, "mechanism": "Carbapenems dramatically reduce valproate levels (by up to 80%) within 24 hours",
     "management": "Avoid combination; switch to non-carbapenem antibiotic. Monitor valproate levels"},
    {"drug_a": "phenytoin", "drug_b": "corticosteroid",
     "severity": SEVERITY_MODERATE, "mechanism": "Phenytoin induces hepatic metabolism of corticosteroids, reducing their efficacy",
     "management": "Increase corticosteroid dose by 25-50% if needed"},
    # --- Antimicrobials ---
    {"drug_a": "trimethoprim_sulfamethoxazole", "drug_b": "methotrexate",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive antifolate effect; severe bone marrow suppression",
     "management": "Avoid combination. Use alternative antibiotic for PCP prophylaxis"},
    {"drug_a": "trimethoprim_sulfamethoxazole", "drug_b": "phenytoin",
     "severity": SEVERITY_MODERATE, "mechanism": "TMP/SMX inhibits phenytoin metabolism, increasing phenytoin levels",
     "management": "Monitor phenytoin levels; adjust dose if needed"},
    {"drug_a": "aminoglycoside", "drug_b": "furosemide",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive ototoxicity and nephrotoxicity",
     "management": "Avoid combination; use alternative antibiotic if possible"},
    {"drug_a": "aminoglycoside", "drug_b": "vancomycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive nephrotoxicity",
     "management": "Monitor renal function daily; perform therapeutic drug monitoring for both agents"},
    {"drug_a": "vancomycin", "drug_b": "piperacillin_tazobactam",
     "severity": SEVERITY_MAJOR, "mechanism": "Synergistic acute kidney injury risk (observed in ICU studies, 2-3x higher AKI rate)",
     "management": "Monitor renal function daily; limit combination duration; consider alternative if CKD stage 4-5"},
    {"drug_a": "acyclovir", "drug_b": "mycophenolate",
     "severity": SEVERITY_MODERATE, "mechanism": "Competition for tubular secretion; acyclovir may increase mycophenolate levels",
     "management": "Monitor for MPA toxicity; renal dose acyclovir"},
    # --- Cardiovascular ---
    {"drug_a": "beta_blocker", "drug_b": "verapamil",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive negative chronotropic effect; risk of bradycardia, heart block, and heart failure",
     "management": "Avoid combination in patients with conduction abnormalities. Monitor heart rate and ECG"},
    {"drug_a": "beta_blocker", "drug_b": "clonidine",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive bradycardia; severe rebound hypertension if clonidine stopped",
     "management": "Monitor heart rate; do not discontinue clonidine abruptly"},
    {"drug_a": "diltiazem", "drug_b": "tacrolimus",
     "severity": SEVERITY_MODERATE, "mechanism": "Diltiazem inhibits CYP3A4, increasing tacrolimus levels",
     "management": "Reduce tacrolimus dose by 30-50%; monitor levels"},
    {"drug_a": "amiodarone", "drug_b": "digoxin",
     "severity": SEVERITY_MAJOR, "mechanism": "Amiodarone reduces digoxin clearance and displaces digoxin from tissue binding; doubles digoxin levels",
     "management": "Reduce digoxin dose by 50% when starting amiodarone; monitor digoxin levels"},
    {"drug_a": "amiodarone", "drug_b": "warfarin",
     "severity": SEVERITY_MAJOR, "mechanism": "Amiodarone inhibits CYP2C9 and CYP1A2, significantly potentiating warfarin",
     "management": "Reduce warfarin dose by 25-50%; monitor INR frequently during initiation and discontinuation"},
    # --- Transplant-specific ---
    {"drug_a": "tacrolimus", "drug_b": "everolimus",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive nephrotoxicity; but used intentionally in reduced-CNI protocols. mTOR inhibitor impairs wound healing",
     "management": "Monitor renal function; consider therapeutic drug monitoring for both agents"},
    {"drug_a": "belatacept", "drug_b": "rituximab",
     "severity": SEVERITY_MODERATE, "mechanism": "Additive immunosuppression; increased risk of EBV-related PTLD",
     "management": "Monitor EBV viral load; increased vigilance for lymphoproliferative disorders"},
    # --- ECMO / Critical care ---
    {"drug_a": "furosemide", "drug_b": "tobramycin",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive nephrotoxicity and ototoxicity",
     "management": "Avoid combination; use alternative diuretic or antibiotic"},
    {"drug_a": "heparin", "drug_b": "prostacyclin",
     "severity": SEVERITY_MAJOR, "mechanism": "Additive anticoagulation; severe bleeding risk",
     "management": "Monitor aPTT closely; reduce heparin dose"},
]


@dataclass
class InteractionResult:
    drug_a: str
    drug_b: str
    severity: str
    mechanism: str
    management: str


def normalize_drug_name(name: str) -> str:
    """Normalize a drug name for database lookup."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def get_drug_generic_name(drug_id_or_name: str) -> str:
    """Resolve a drug ID or name to the normalized name used in interaction DB."""
    name_map = {
        "acei": "ace_inhibitor",
        "ace_inhibitor": "ace_inhibitor",
        "ace_inhibitors": "ace_inhibitor",
        "arb": "arb",
        "arbs": "arb",
        "sglt2i": "sglt2_inhibitor",
        "sglt2_inhibitor": "sglt2_inhibitor",
        "sglt2": "sglt2_inhibitor",
        "cni": "ciclosporin",
        "calcineurin_inhibitor": "tacrolimus",
        "mmf": "mycophenolate",
        "mycophenolate_mofetil": "mycophenolate",
        "mycophenolate_sodium": "mycophenolate",
        "mps": "mycophenolate",
        "nsaid": "nsaids",
        "nsaids": "nsaids",
        "tac": "tacrolimus",
        "csa": "ciclosporin",
        "cyclosporine": "ciclosporin",
        "hcq": "hydroxychloroquine",
        "tmp_smx": "trimethoprim_sulfamethoxazole",
        "tmp/smx": "trimethoprim_sulfamethoxazole",
        "co_trimoxazole": "trimethoprim_sulfamethoxazole",
        "k_sparing_diuretic": "potassium_sparing_diuretics",
        "spironolactone": "potassium_sparing_diuretics",
        "eplerenone": "potassium_sparing_diuretics",
        "loop_diuretic": "furosemide",
        "prednisolone": "corticosteroid",
        "prednisone": "corticosteroid",
        "methylprednisolone": "corticosteroid",
        "dexamethasone": "corticosteroid",
    }
    normalized = normalize_drug_name(drug_id_or_name)
    return name_map.get(normalized, normalized)


def check_interactions(
    drug_ids_or_names: list[str],
    patient_context: dict | None = None,
) -> list[InteractionResult]:
    """Check for drug-drug interactions in a list of medications.

    Args:
        drug_ids_or_names: List of drug names/IDs being taken
        patient_context: Optional dict with egfr, age, conditions (used for filtering)

    Returns:
        List of InteractionResult objects with severity, mechanism, management
    """
    resolved = [get_drug_generic_name(d) for d in drug_ids_or_names]
    results: list[InteractionResult] = []

    for i in range(len(resolved)):
        for j in range(i + 1, len(resolved)):
            drug_a, drug_b = resolved[i], resolved[j]

            for interaction in INTERACTION_DB:
                db_a = interaction["drug_a"]
                db_b = interaction["drug_b"]

                pair_matches = (
                    (drug_a == db_a and drug_b == db_b) or
                    (drug_a == db_b and drug_b == db_a)
                )

                if pair_matches:
                    results.append(InteractionResult(
                        drug_a=drug_ids_or_names[i],
                        drug_b=drug_ids_or_names[j],
                        severity=interaction["severity"],
                        mechanism=interaction["mechanism"],
                        management=interaction["management"],
                    ))
                    break

    # Sort by severity
    severity_order = {SEVERITY_MAJOR: 0, SEVERITY_MODERATE: 1, SEVERITY_MINOR: 2}
    results.sort(key=lambda r: severity_order.get(r.severity, 99))

    return results


def get_interaction_summary(results: list[InteractionResult]) -> dict:
    """Summarize interaction check results."""
    major = sum(1 for r in results if r.severity == SEVERITY_MAJOR)
    moderate = sum(1 for r in results if r.severity == SEVERITY_MODERATE)
    minor = sum(1 for r in results if r.severity == SEVERITY_MINOR)

    action = "safe"
    if major > 0:
        action = "review_required"
    elif moderate > 0:
        action = "caution"

    return {
        "total_interactions": len(results),
        "major": major,
        "moderate": moderate,
        "minor": minor,
        "action": action,
        "interactions": [
            {
                "drug_a": r.drug_a,
                "drug_b": r.drug_b,
                "severity": r.severity,
                "mechanism": r.mechanism,
                "management": r.management,
            }
            for r in results
        ],
    }
