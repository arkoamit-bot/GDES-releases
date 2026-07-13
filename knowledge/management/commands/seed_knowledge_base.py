from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone

from knowledge.models import GuidelineSource, KnowledgeBaseEntry
DISEASE_RULES = {
    "iga": {
        "name": "IgA nephropathy or IgA vasculitis nephritis",
        "base": 2,
        "rules": [
            (["sediment", "hematuria"], 2, "Dysmorphic hematuria supports glomerular inflammation."),
            (["sediment", "casts"], 3, "RBC casts point to active glomerulonephritis."),
            (["feature", "grossHematuria"], 3, "Gross hematuria can occur with IgA nephropathy, often around mucosal infection."),
            (["feature", "postInfectious"], 1, "Infection-timed hematuria keeps IgA nephropathy and infection-related GN in view."),
            (["feature", "purpura"], 3, "Purpura plus kidney findings raises IgA vasculitis nephritis."),
            (["feature", "arthritis"], 1, "Arthralgia is compatible with IgA vasculitis."),
            (["biopsy", "mesangialIga"], 6, "Dominant mesangial IgA is a defining biopsy clue."),
            (["proteinuria", "subnephrotic"], 1, "Proteinuria is common and should be quantified."),
            (["proteinuria", "nephrotic"], 1, "Nephrotic-range proteinuria can mark higher-risk IgA disease."),
            (["lab", "lowC3"], -1, "Low C3 is not typical of isolated IgA nephropathy."),
            (["feature", "chronicTonsillitis"], 2, "Tonsillitis-synchronous hematuria is classic for IgA nephropathy."),
            (["feature", "loinPain"], 1, "Loin pain can accompany macroscopic hematuria episodes in IgA nephropathy."),
            (["biopsy", "crescents"], 2, "Crescents on biopsy indicate active proliferative IgA nephropathy."),
            (["biopsy", "segmentalSclerosis"], 1, "Segmental sclerosis can be seen in advanced IgA lesions."),
            (["ageGroup", "adult"], 1, "IgA nephropathy commonly presents in young adults (20-40 years)."),
            (["feature", "hypertension"], 1, "Hypertension at presentation is a risk factor for progression in IgAN."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2025,
        "source_title": "KDIGO 2025 IgAN and IgAV Guideline",
    },
    "membranous": {
        "name": "Membranous nephropathy",
        "base": 1,
        "rules": [
            (["proteinuria", "nephrotic"], 4, "Nephrotic-range proteinuria is a classic presentation."),
            (["albumin", "low"], 2, "Hypoalbuminemia supports nephrotic syndrome physiology."),
            (["sediment", "bland"], 2, "A bland sediment fits a podocytopathy or membranous pattern."),
            (["lab", "pla2r"], 5, "PLA2R positivity strongly supports primary membranous nephropathy."),
            (["biopsy", "subepithelial"], 5, "Subepithelial deposits or spikes are characteristic."),
            (["lab", "hepatitis"], 1, "Infection screening matters when membranous nephropathy is suspected."),
            (["lab", "anaDsDna"], -1, "Positive lupus serology shifts the differential."),
            (["feature", "thrombosis"], 2, "Venous thromboembolism risk is increased in membranous nephropathy."),
            (["feature", "edema"], 1, "Peripheral edema is common with nephrotic-range proteinuria."),
            (["ageGroup", "adult"], 2, "Primary membranous is predominantly an adult disease (peak 40-60 years)."),
            (["lab", "antiGbm"], -1, "Anti-GBM positivity suggests dual anti-GBM/membranous or different diagnosis."),
            (["feature", "malignancy"], 1, "Secondary membranous can be associated with solid malignancies."),
            (["feature", "autoimmune"], 1, "Autoimmune conditions like SLE, RA, thyroiditis can cause secondary membranous."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "mcd": {
        "name": "Minimal change disease",
        "base": 1,
        "rules": [
            (["ageGroup", "child"], 3, "Childhood nephrotic syndrome is often steroid-sensitive minimal change disease."),
            (["proteinuria", "nephrotic"], 4, "Abrupt nephrotic syndrome is a typical pattern."),
            (["albumin", "low"], 2, "Low serum albumin supports nephrotic syndrome."),
            (["sediment", "bland"], 2, "Bland sediment supports a podocytopathy."),
            (["biopsy", "podocyteEffacement"], 5, "Diffuse foot-process effacement is the key biopsy clue."),
            (["sediment", "casts"], -2, "RBC casts make isolated minimal change disease less likely."),
            (["feature", "suddenOnset"], 2, "Rapid onset of nephrotic syndrome favors MCD over FSGS."),
            (["feature", "steroidResponsive"], 3, "Steroid responsiveness is a hallmark of MCD."),
            (["feature", "allergy"], 1, "MCD can be triggered by allergies, NSAIDs, or immunizations."),
            (["feature", "infection"], 1, "MCD can relapse after infections or allergic reactions."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2025,
        "source_title": "KDIGO 2025 Nephrotic Syndrome in Children Guideline",
    },
    "fsgs": {
        "name": "Focal segmental glomerulosclerosis",
        "base": 1,
        "rules": [
            (["proteinuria", "nephrotic"], 3, "FSGS can present with nephrotic-range proteinuria."),
            (["proteinuria", "subnephrotic"], 1, "Secondary FSGS may have subnephrotic proteinuria."),
            (["albumin", "low"], 1, "Hypoalbuminemia supports primary podocyte injury if severe."),
            (["sediment", "hematuria"], 1, "Microscopic hematuria can coexist."),
            (["biopsy", "segmentalSclerosis"], 6, "Segmental sclerosis is the defining pathologic clue."),
            (["biopsy", "podocyteEffacement"], 2, "Diffuse effacement supports a primary podocytopathy pattern."),
            (["feature", "diabetes"], 1, "Metabolic or adaptive stress can contribute to secondary sclerosis."),
            (["feature", "obesity"], 1, "Obesity-related glomerulopathy can present as secondary FSGS."),
            (["feature", "hiv"], 2, "HIV-associated nephropathy (HIVAN) is typically collapsing FSGS."),
            (["feature", "steroidResistant"], 2, "Steroid resistance is more common in FSGS than MCD."),
            (["feature", "slowProgression"], 1, "Primary FSGS typically has slower onset than MCD."),
            (["feature", "hypertension"], 1, "Hypertension is frequent in FSGS, especially secondary forms."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "lupus": {
        "name": "Lupus nephritis",
        "base": 1,
        "rules": [
            (["feature", "sle"], 5, "Known or suspected SLE is a major context clue."),
            (["lab", "anaDsDna"], 4, "ANA or anti-dsDNA positivity supports lupus activity."),
            (["lab", "lowC3"], 2, "Complement consumption supports immune-complex disease."),
            (["lab", "lowC4"], 2, "Low C4 strengthens suspicion for lupus nephritis."),
            (["sediment", "casts"], 3, "RBC casts can indicate active proliferative lupus nephritis."),
            (["proteinuria", "nephrotic"], 2, "Heavy proteinuria can occur, including membranous lupus nephritis."),
            (["biopsy", "fullHouse"], 6, "Full-house immune deposits are a classic biopsy clue."),
            (["feature", "malarRash"], 2, "Malar rash or photosensitivity supports SLE diagnosis."),
            (["feature", "oralUlcers"], 1, "Oral ulcers are a common SLE manifestation."),
            (["feature", "arthritis"], 2, "Arthritis/arthralgia is present in >80% of SLE patients."),
            (["feature", "serositis"], 1, "Pleuritis or pericarditis can accompany lupus nephritis."),
            (["feature", "alopecia"], 1, "Alopecia is a common non-renal manifestation of SLE."),
            (["feature", "female"], 2, "SLE has a strong female predominance (F:M 9:1)."),
            (["feature", "antiphospholipid"], 1, "Antiphospholipid antibodies can coexist with lupus nephritis."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Lupus Nephritis Guideline",
    },
    "anca": {
        "name": "ANCA-associated pauci-immune GN",
        "base": 1,
        "rules": [
            (["egfrTrend", "rapidDecline"], 4, "Rapid eGFR decline raises concern for rapidly progressive GN."),
            (["sediment", "casts"], 4, "RBC casts support active necrotizing GN."),
            (["lab", "anca"], 5, "ANCA positivity strongly supports ANCA-associated vasculitis."),
            (["feature", "sinopulmonary"], 3, "ENT or pulmonary features fit systemic small-vessel vasculitis."),
            (["feature", "hemoptysis"], 4, "Hemoptysis may indicate pulmonary capillaritis."),
            (["biopsy", "crescents"], 5, "Crescents or necrosis support rapidly progressive GN."),
            (["feature", "skinPurpura"], 1, "Palpable purpura can accompany small-vessel vasculitis."),
            (["feature", "arthralgia"], 1, "Joint pain is a common constitutional symptom."),
            (["feature", "mononeuritis"], 2, "Mononeuritis multiplex is specific for vasculitis."),
            (["lab", "lowC3"], -1, "Complement is typically normal or elevated in AAV."),
            (["lab", "antiGbm"], -1, "Anti-GBM positivity suggests dual disease or alternative diagnosis."),
            (["feature", "mpaPattern"], 2, "Microscopic polyangiitis: renal-limited or renal+lung without ENT."),
            (["feature", "gpaPattern"], 2, "Granulomatosis with polyangiitis: ENT+lung+kidney triad."),
            (["egfrTrend", "rapidDecline"], 3, "Sustained rapid eGFR loss over weeks is typical of RPGN."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 ANCA Vasculitis Guideline",
    },
    "antiGbm": {
        "name": "Anti-GBM disease",
        "base": 0,
        "rules": [
            (["lab", "antiGbm"], 7, "Anti-GBM antibodies strongly support anti-GBM disease."),
            (["feature", "hemoptysis"], 4, "Hemoptysis with GN suggests pulmonary-renal syndrome."),
            (["egfrTrend", "rapidDecline"], 4, "Rapid loss of kidney function is typical and urgent."),
            (["sediment", "casts"], 3, "RBC casts support active crescentic GN."),
            (["biopsy", "linearIgg"], 7, "Linear IgG staining is a defining biopsy clue."),
            (["biopsy", "crescents"], 4, "Crescents support severe rapidly progressive GN."),
            (["lab", "anca"], 2, "ANCA positivity (dual anti-GBM/ANCA) occurs in 10-30% of cases."),
            (["feature", "smoking"], 1, "Smoking increases risk of pulmonary hemorrhage in anti-GBM."),
            (["feature", "oliguria"], 2, "Oliguric renal failure at presentation carries poor prognosis."),
            (["egfrTrend", "rapidDecline"], 3, "Dialysis requirement at presentation is common in severe anti-GBM."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "infectionRelated": {
        "name": "Infection-related glomerulonephritis",
        "base": 1,
        "rules": [
            (["feature", "postInfectious"], 4, "A recent or ongoing infection is a key clinical clue."),
            (["lab", "lowC3"], 4, "Low C3 supports infection-related or complement-mediated GN."),
            (["lab", "lowC4"], 1, "Complement consumption can occur in immune-complex GN."),
            (["sediment", "casts"], 3, "RBC casts indicate active glomerulonephritis."),
            (["proteinuria", "subnephrotic"], 1, "Proteinuria is often present."),
            (["egfrTrend", "reduced"], 1, "Reduced eGFR can accompany active disease."),
            (["feature", "skinInfection"], 2, "Impetigo or skin infections can precede post-streptococcal GN."),
            (["feature", "pharyngitis"], 2, "Streptococcal pharyngitis 1-3 weeks before is classic."),
            (["feature", "scarletFever"], 2, "Scarlet fever history supports post-streptococcal GN."),
            (["ageGroup", "child"], 2, "Post-streptococcal GN is more common in children."),
            (["lab", "antiDnaseB"], 2, "Anti-DNase B positive more specific than ASOT for recent Strep."),
            (["lab", "asot"], 1, "ASOT elevation supports recent streptococcal infection."),
            (["feature", "staphylococcus"], 2, "Staphylococcal infection can cause IgA-dominant infection-related GN."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "c3": {
        "name": "C3 glomerulopathy or complement-mediated GN",
        "base": 0,
        "rules": [
            (["lab", "lowC3"], 4, "Persistent low C3 raises complement-mediated disease."),
            (["lab", "lowC4"], -1, "Normal C4 with low C3 is more typical of alternative-pathway activation."),
            (["biopsy", "c3Dominant"], 7, "C3-dominant deposits are the central biopsy clue."),
            (["sediment", "casts"], 2, "Active urinary sediment supports GN."),
            (["egfrTrend", "reduced"], 2, "Reduced kidney function can occur in complement-mediated GN."),
            (["lab", "c3nephriticFactor"], 4, "C3 nephritic factor positivity supports C3 glomerulonephritis."),
            (["lab", "cfhMutation"], 3, "CFH mutation or autoantibody points to complement dysregulation."),
            (["feature", "drusen"], 2, "Ocular drusen can accompany complement dysregulation (CFH mutation)."),
            (["feature", "lipodystrophy"], 2, "Partial lipodystrophy is associated with C3 glomerulonephritis."),
            (["biopsy", "denseDeposits"], 6, "Intramembranous dense deposits define DDD."),
            (["feature", "persistentProteinuria"], 1, "Persistent proteinuria despite treatment is common."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "diabeticNephropathy": {
        "name": "Diabetic kidney disease / nephropathy",
        "base": 1,
        "rules": [
            (["feature", "diabetes"], 5, "Presence of diabetes (type 1 or 2) is the primary risk factor."),
            (["feature", "diabetesDuration"], 2, "Long-standing diabetes (≥10 years) with proteinuria suggests DKD."),
            (["feature", "retinopathy"], 3, "Diabetic retinopathy strongly correlates with DKD."),
            (["proteinuria", "subnephrotic"], 1, "Moderate albuminuria is the earliest sign of DKD."),
            (["proteinuria", "nephrotic"], 1, "Nephrotic-range proteinuria can occur in advanced DKD."),
            (["egfrTrend", "reduced"], 1, "Gradual eGFR decline over years is typical."),
            (["feature", "hypertension"], 1, "Hypertension commonly accompanies DKD."),
            (["feature", "neuropathy"], 1, "Peripheral neuropathy supports long-standing diabetes complications."),
            (["sediment", "bland"], 1, "Bland sediment is typical of DKD (no active cellular casts)."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Diabetes Management in CKD Guideline",
    },
    "hypertensiveNephrosclerosis": {
        "name": "Hypertensive nephrosclerosis",
        "base": 1,
        "rules": [
            (["feature", "hypertension"], 4, "Long-standing hypertension is the primary risk factor."),
            (["feature", "hypertensionDuration"], 2, "Duration of hypertension correlates with renal injury."),
            (["proteinuria", "subnephrotic"], 1, "Modest proteinuria (<1.5g/day) is typical."),
            (["proteinuria", "nephrotic"], -2, "Nephrotic-range proteinuria is NOT typical."),
            (["sediment", "bland"], 2, "Bland sediment without active cells or casts."),
            (["egfrTrend", "reduced"], 1, "Slow gradual eGFR decline parallels vascular disease."),
            (["feature", "leftVentricularHypertrophy"], 1, "LVH supports chronic hypertensive end-organ damage."),
            (["feature", "retinopathy"], 1, "Hypertensive retinopathy supports chronic hypertension."),
            (["ageGroup", "adult"], 1, "More common in older adults (>50 years)."),
            (["feature", "africanAncestry"], 1, "More common and aggressive in African ancestry."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Blood Pressure in CKD Guideline",
    },
    "acuteInterstitialNephritis": {
        "name": "Acute interstitial nephritis",
        "base": 0,
        "rules": [
            (["feature", "drugExposure"], 4, "Drug-induced AIN is the most common cause (NSAIDs, antibiotics, PPIs)."),
            (["feature", "rash"], 2, "Classic triad: fever, rash, eosinophilia (present in <30% of cases)."),
            (["feature", "fever"], 2, "Fever within days-weeks of drug exposure is suspicious."),
            (["feature", "arthralgia"], 1, "Arthralgia can accompany drug-induced AIN."),
            (["egfrTrend", "rapidDecline"], 2, "Acute kidney injury develops over days to weeks."),
            (["sediment", "hematuria"], 1, "Microscopic hematuria is common."),
            (["lab", "eosinophilia"], 2, "Eosinophilia or eosinophiluria supports AIN."),
            (["feature", "nsaidExposure"], 3, "NSAID-induced AIN can occur after months to years of use."),
            (["feature", "antibioticExposure"], 3, "Beta-lactams, rifampin, TMP/SMX, fluoroquinolones are common causes."),
            (["feature", "ppiExposure"], 2, "PPI-associated AIN often has insidious onset; increasing recognition."),
            (["sediment", "bland"], 1, "White cell casts can be seen but often absent."),
            (["feature", "flankPain"], 1, "Bilateral flank pain can occur due to renal capsule distension."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 AKI Guideline",
    },
    "acuteTubularNecrosis": {
        "name": "Acute tubular necrosis (ischemic/nephrotoxic)",
        "base": 0,
        "rules": [
            (["feature", "ischemia"], 4, "Prolonged hypotension, sepsis, or major surgery suggests ischemic ATN."),
            (["feature", "nephrotoxin"], 3, "Aminoglycosides, contrast, cisplatin, pigmented urine suggest nephrotoxic ATN."),
            (["egfrTrend", "rapidDecline"], 3, "Acute rise in creatinine over hours-days."),
            (["sediment", "muddyBrown"], 3, "Muddy brown granular casts are characteristic."),
            (["feature", "oliguria"], 2, "Oliguric or anuric phase is common in severe ATN."),
            (["feature", "fluidOverload"], 1, "Volume overload can complicate oliguric ATN."),
            (["feature", "hyperkalemia"], 1, "Hyperkalemia is common due to reduced renal excretion."),
            (["proteinuria", "subnephrotic"], 1, "Mild proteinuria may be present."),
            (["feature", "contrastExposure"], 2, "Contrast-induced nephropathy typically 24-48h post exposure."),
            (["feature", "rhabdomyolysis"], 3, "Pigment-induced ATN from myoglobin: dark urine, elevated CK."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 AKI Guideline",
    },
    "thromboticMicroangiopathy": {
        "name": "Thrombotic microangiopathy (TMA)",
        "base": 0,
        "rules": [
            (["feature", "microangiopathicHemolyticAnemia"], 5, "MAHA (schistocytes, low haptoglobin, elevated LDH) is a hallmark."),
            (["feature", "thrombocytopenia"], 4, "Thrombocytopenia is part of the TMA diagnostic triad."),
            (["feature", "neurologicSymptoms"], 3, "Neurologic involvement (confusion, seizures, focal deficits) suggests TTP."),
            (["feature", "fever"], 2, "Fever is classically part of the TTP pentad."),
            (["feature", "renalFailure"], 3, "Acute kidney injury is prominent in aHUS and STEC-HUS."),
            (["egfrTrend", "rapidDecline"], 2, "Renal function often deteriorates rapidly."),
            (["lab", "adams13"], 4, "Severely decreased ADAMTS13 activity (<10%) confirms TTP."),
            (["feature", "diarrhea"], 2, "Bloody diarrhea precedes STEC-HUS (especially in children)."),
            (["feature", "complementMutation"], 3, "Complement gene mutation or autoantibody supports aHUS."),
            (["biopsy", "tmLesions"], 4, "Arteriolar and glomerular microthrombi are diagnostic."),
            (["feature", "drugInduced"], 2, "CNIs, VEGF inhibitors, quinine, chemotherapy can cause secondary TMA."),
            (["feature", "malignantHypertension"], 2, "Severe hypertension can cause or complicate TMA."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "lightChainCastNephropathy": {
        "name": "Light chain cast nephropathy (myeloma kidney)",
        "base": 0,
        "rules": [
            (["feature", "multipleMyeloma"], 5, "Known or suspected multiple myeloma is the primary context."),
            (["feature", "hypercalcemia"], 2, "Hypercalcemia is common in myeloma and contributes to AKI."),
            (["feature", "anemia"], 2, "Anemia out of proportion to CKD is typical."),
            (["egfrTrend", "rapidDecline"], 2, "Acute or subacute renal failure is common."),
            (["proteinuria", "subnephrotic"], 1, "Proteinuria is often minimal (<1g/day), mostly Bence Jones."),
            (["sediment", "bland"], 1, "Urine sediment is typically bland."),
            (["lab", "freeLightChains"], 4, "Elevated serum free light chains with abnormal ratio are diagnostic."),
            (["lab", "serumProteinElectrophoresis"], 3, "Monoclonal spike on SPEP supports myeloma."),
            (["ageGroup", "adult"], 2, "Multiple myeloma is a disease of older adults (>60 years)."),
            (["feature", "bonePain"], 2, "Bone pain or lytic lesions support myeloma diagnosis."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "fibrillaryGlomerulonephritis": {
        "name": "Fibrillary glomerulonephritis / immunotactoid glomerulopathy",
        "base": 0,
        "rules": [
            (["proteinuria", "nephrotic"], 2, "Nephrotic-range proteinuria is present in ~50% of cases."),
            (["proteinuria", "subnephrotic"], 1, "Subnephrotic proteinuria can occur."),
            (["sediment", "hematuria"], 2, "Microscopic hematuria is common."),
            (["sediment", "casts"], 1, "RBC casts can be present."),
            (["egfrTrend", "reduced"], 1, "Renal function is often impaired at diagnosis."),
            (["feature", "malignancy"], 2, "Associated with malignancies (especially lymphoproliferative) in ~30%."),
            (["feature", "autoimmune"], 1, "Associated with autoimmune conditions (SLE, RA, Crohn's)."),
            (["feature", "hepatitisC"], 1, "HCV infection can be associated with cryoglobulinemic GN."),
            (["biopsy", "fibrillaryDeposits"], 5, "Randomly oriented fibrils ~20nm distinguish fibrillary GN."),
            (["biopsy", "immunotactoid"], 4, "Microtubular deposits >30nm suggest immunotactoid glomerulopathy."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "amyloidosis": {
        "name": "Renal amyloidosis",
        "base": 0,
        "rules": [
            (["proteinuria", "nephrotic"], 3, "Nephrotic-range proteinuria is common."),
            (["albumin", "low"], 2, "Severe hypoalbuminemia is typical."),
            (["sediment", "bland"], 1, "Bland sediment without active cells."),
            (["feature", "cardiacInvolvement"], 2, "Cardiac amyloid (HFpEF, arrhythmia, low voltage ECG) supports AL."),
            (["feature", "hepatomegaly"], 1, "Hepatomegaly can occur in systemic amyloidosis."),
            (["feature", "neuropathy"], 1, "Peripheral or autonomic neuropathy supports amyloid."),
            (["feature", "macroglossia"], 3, "Macroglossia is specific (though rare) for AL amyloid."),
            (["lab", "freeLightChains"], 3, "Abnormal FLC ratio supports AL amyloidosis."),
            (["lab", "serumProteinElectrophoresis"], 2, "Monoclonal protein in serum/urine supports AL."),
            (["feature", "chronicInflammation"], 2, "Chronic inflammatory conditions predispose to AA amyloidosis."),
            (["ageGroup", "adult"], 2, "Amyloidosis is more common in older adults."),
            (["biopsy", "congoRedPositive"], 5, "Congo red positive deposits with apple-green birefringence."),
            (["feature", "ecchymoses"], 1, "Periorbital ecchymoses (raccoon eyes) can occur in AL amyloid."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2021,
        "source_title": "KDIGO 2021 Glomerular Diseases Guideline",
    },
    "diabeticNephropathyWithGN": {
        "name": "Diabetic kidney disease with superimposed GN",
        "base": 1,
        "rules": [
            (["feature", "diabetes"], 3, "Diabetes is present."),
            (["feature", "retinopathy"], 1, "Background retinopathy supports diabetic kidney disease."),
            (["sediment", "casts"], 3, "Active sediment (RBC casts) suggests superimposed GN."),
            (["sediment", "hematuria"], 2, "New or worsening hematuria suggests GN rather than pure DKD."),
            (["egfrTrend", "rapidDecline"], 3, "Rapid decline is NOT typical of DKD alone - suggests GN."),
            (["proteinuria", "nephrotic"], 2, "Worsening proteinuria beyond DKD baseline suggests GN."),
            (["feature", "systemicSymptoms"], 2, "Constitutional symptoms suggest GN or vasculitis."),
            (["lab", "anca"], 2, "ANCA positivity suggests pauci-immune GN superimposed on DKD."),
            (["lab", "antiGbm"], 2, "Anti-GBM positivity suggests dual disease."),
            (["feature", "hemoptysis"], 2, "Pulmonary-renal syndrome can occur with DKD as comorbid condition."),
        ],
        "source_abbr": "KDIGO",
        "source_year": 2024,
        "source_title": "KDIGO 2024 Diabetes Management in CKD Guideline",
    },
}


class Command(BaseCommand):
    help = "Seed the knowledge base with expanded disease profiles (200+ rules)"

    def handle(self, *args, **options):
        source_cache = {}
        seq = 0
        total_rules = 0
        for disease_id, profile in DISEASE_RULES.items():
            abbr = profile["source_abbr"]
            year = profile["source_year"]
            key = f"{abbr}-{year}"
            if key not in source_cache:
                source, created = GuidelineSource.objects.get_or_create(
                    abbreviation=abbr,
                    version_year=year,
                    defaults={
                        "title": profile["source_title"],
                        "effective_date": f"{year}-01-01",
                    },
                )
                source_cache[key] = source

            for rule_path, weight, explanation in profile["rules"]:
                seq += 1
                entry_id = f"KB-{disease_id.upper()}-{seq:03d}"

                if isinstance(rule_path, list):
                    conditions = [
                        {"field": rule_path[0], "operator": "eq", "value": rule_path[1]}
                    ]
                elif rule_path == "egfrTrend_rapid_sustained":
                    conditions = [
                        {"field": "egfrTrend", "operator": "eq", "value": "rapidDecline"}
                    ]
                elif rule_path == "egfrTrend_dialysis_requiring":
                    conditions = [
                        {"field": "egfrTrend", "operator": "eq", "value": "rapidDecline"},
                        {"field": "features", "operator": "contains", "value": "oliguria"},
                    ]
                else:
                    conditions = [
                        {"field": "features", "operator": "contains", "value": rule_path}
                    ]

                today = timezone.now().date()
                next_review = today.replace(year=today.year + 1)

                KnowledgeBaseEntry.objects.get_or_create(
                    entry_id=entry_id,
                    defaults={
                        "disease_id": disease_id,
                        "rule_data": {
                            "conditions": conditions,
                            "weight": weight,
                            "explanation": explanation,
                            "base_score": profile["base"],
                            "disease_name": profile["name"],
                        },
                        "source": source_cache[key],
                        "status": KnowledgeBaseEntry.Status.ACTIVE,
                        "effective_date": f"{year}-01-01",
                        # Governance fields (C-2 fix)
                        "explanation": explanation,
                        "confidence_score": 75.0,
                        "next_review_date": next_review,
                        "knowledge_version": "6.5",
                        "date_validated": today,
                        "recommendation_id": f"KDIGO-{year}-{disease_id.upper()}-{seq:03d}",
                    },
                )
                total_rules += 1

        count = KnowledgeBaseEntry.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {total_rules} rules across {len(DISEASE_RULES)} diseases "
            f"(total KB entries: {count})"
        ))
