"""Seed V4.0 drug knowledge: mechanism, side effects, monitoring, dosage.

Expands existing DrugMaster records with comprehensive clinical pharmacology data.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from treatments.models import DrugMaster


DRUG_KNOWLEDGE = {
    "Prednisolone": {
        "mechanism": "Synthetic glucocorticoid with potent anti-inflammatory and immunosuppressive effects. Binds glucocorticoid receptors, inhibiting NF-kB and AP-1 transcription factors, reducing pro-inflammatory cytokine production (IL-1, IL-2, IL-6, TNF-alpha, IFN-gamma). Suppresses T-cell proliferation and activation.",
        "common_side_effects": ["Weight gain", "Insomnia", "Mood changes", "Increased appetite",
                                 "Acne", "Bruising", "Osteoporosis", "Hyperglycemia",
                                 "Hypertension", "Moon face", "Buffalo hump", "Striae"],
        "serious_side_effects": ["Adrenal suppression", "Osteoporosis/fractures", "Avascular necrosis",
                                 "Peptic ulcer disease", "Pancreatitis", "Psychosis",
                                 "Cushing syndrome", "Growth retardation (children)",
                                 "Immunosuppression/infection", "Glaucoma", "Cataracts"],
        "monitoring_parameters": "Blood glucose (weekly during high-dose), BP (each visit), bone density (annual if >3 months), ophthalmology (annual), growth chart (children). Monitor for infection symptoms.",
        "stopping_criteria": "Do not stop abruptly after >2 weeks (taper required). Stop if severe psychosis, uncontrolled infection, or avascular necrosis develops.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2021", "chapter": "IgAN", "recommendation": "Consider prednisolone 0.5-1mg/kg/day for IgAN with persistent proteinuria >1g/day"},
            {"source": "KDIGO 2021", "chapter": "MCD", "recommendation": "First-line for MCD: prednisolone 1mg/kg/day for 4-16 weeks"},
        ],
        "typical_dosage": "0.5-1 mg/kg/day orally; max 80 mg/day. Taper over 4-8 weeks.",
        "maximum_dose": "80 mg/day (1 mg/kg/day for induction)",
        "transplant_considerations": "Part of standard maintenance immunosuppression. Higher doses for acute rejection treatment. Monitor for PTDM and infection.",
    },
    "Mycophenolate Mofetil": {
        "mechanism": "Selective inhibitor of inosine monophosphate dehydrogenase (IMPDH), blocking de novo purine synthesis in proliferating T and B lymphocytes. Reduces lymphocyte proliferation, antibody production, and adhesion molecule expression.",
        "common_side_effects": ["Diarrhea (most common)", "Nausea/vomiting", "Abdominal pain",
                                 "Leukopenia", "Anemia", "Headache", "Tremor", "Insomnia"],
        "serious_side_effects": ["Opportunistic infections (CMV, BK, PCP, EBV)",
                                  "Bone marrow suppression (severe leukopenia, anemia)",
                                  "GI ulceration/hemorrhage", "Teratogenicity (FDA Category D)",
                                  "PTLD", "Progressive multifocal leukoencephalopathy"],
        "monitoring_parameters": "CBC weekly x4 then monthly for 3 months. Regular LFTs. Pregnancy test before starting and monthly. Monitor for GI symptoms and infections.",
        "stopping_criteria": "Stop if severe neutropenia (ANC <1000), uncontrolled infection, or pregnancy. Discontinue MMF and switch to AZA 12 weeks before planned conception.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2024", "chapter": "Lupus Nephritis", "recommendation": "First-line induction and maintenance for lupus nephritis"},
            {"source": "KDIGO 2021", "chapter": "Membranous", "recommendation": "Alternative immunosuppressant for resistant membranous nephropathy"},
        ],
        "typical_dosage": "500-1500 mg BID; target dose 2g/day for induction, 1-2g/day for maintenance.",
        "maximum_dose": "3 g/day",
        "transplant_considerations": "Standard maintenance immunosuppression. Reduce dose for leukopenia. GI side effects common - consider enteric-coated mycophenolate sodium.",
    },
    "Rituximab": {
        "mechanism": "Chimeric monoclonal antibody against CD20 on B lymphocytes. Depletes B cells via antibody-dependent cellular cytotoxicity, complement-dependent cytotoxicity, and apoptosis. Reduces autoantibody production and antigen presentation.",
        "common_side_effects": ["Infusion reactions (fever, chills, rigors, hypotension)",
                                 "Headache", "Nausea", "Fatigue", "Pruritus", "Rash"],
        "serious_side_effects": ["Severe infusion reactions (bronchospasm, anaphylaxis)",
                                  "Progressive multifocal leukoencephalopathy (JC virus)",
                                  "Hepatitis B reactivation (screening required)",
                                  "Severe infections (PCP, CMV, ?COVID-19)",
                                  "Neutropenia (late-onset)", "Hypogammaglobulinemia",
                                  "Cardiac arrhythmias", "Tumor lysis syndrome"],
        "monitoring_parameters": "CBC, LFTs pre-infusion. HBV screening mandatory (HBsAg, HBcAb). CD19/20 counts to confirm B-cell depletion (optional). Immunoglobulin levels if recurrent infections.",
        "stopping_criteria": "Stop for severe infusion reaction, PML, or severe infection. Re-treat when B cells recover if remission not achieved.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2021", "chapter": "Membranous", "recommendation": "First-line therapy for membranous nephropathy"},
            {"source": "KDIGO 2024", "chapter": "ANCA", "recommendation": "First-line induction agent for ANCA vasculitis"},
            {"source": "KDIGO 2021", "chapter": "MCD", "recommendation": "Second-line for steroid-dependent/frequent-relapse MCD"},
        ],
        "typical_dosage": "1g IV x2 doses 2 weeks apart (nephrology protocol). Alternatively 375 mg/m2 weekly x4 (lymphoma protocol).",
        "maximum_dose": "1 g per infusion",
        "transplant_considerations": "Used for ABMR treatment (often with IVIG + PLEX). HBV reactivation risk significant. Monitor for opportunistic infections.",
    },
    "Cyclophosphamide": {
        "mechanism": "Alkylating agent that cross-links DNA, inhibiting cell proliferation. Prodrug activated by hepatic CYP450 to phosphoramide mustard and acrolein. Particularly active against rapidly dividing lymphocytes.",
        "common_side_effects": ["Nausea/vomiting", "Alopecia", "Bone marrow suppression",
                                 "Hemorrhagic cystitis (acrolein metabolite)",
                                 "Amenorrhea/infertility", "Fatigue"],
        "serious_side_effects": ["Bone marrow suppression (severe neutropenia, thrombocytopenia)",
                                  "Hemorrhagic cystitis (prevent with mesna + hydration)",
                                  "Infertility (gonadal toxicity - dose-dependent)",
                                  "Teratogenicity (Category D)", "Cardiotoxicity (high dose)",
                                  "Pulmonary fibrosis", "SIADH",
                                  "Bladder cancer (long-term, dose-related)",
                                  "Myelodysplasia/leukemia (secondary malignancy)"],
        "monitoring_parameters": "CBC weekly during therapy. Urinalysis daily (hemorrhagic cystitis). Maintain urine output >3L/day + mesna. LFTs. Long-term: annual urinalysis and cystoscopy after cumulative dose >20-50g.",
        "stopping_criteria": "Stop if ANC <1500, platelets <50,000, hemorrhagic cystitis, or severe infection. Cumulative dose limit: 36g or 6 months course.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2024", "chapter": "Lupus Nephritis", "recommendation": "Induction for severe lupus nephritis (Euro-Lupus protocol)"},
            {"source": "KDIGO 2024", "chapter": "ANCA", "recommendation": "Induction for ANCA vasculitis when rituximab not available/contraindicated"},
            {"source": "KDIGO 2021", "chapter": "Anti-GBM", "recommendation": "Essential component of anti-GBM disease treatment with PLEX and steroids"},
        ],
        "typical_dosage": "Oral: 2 mg/kg/day. IV: 0.5-1 g/m2 monthly (NIH protocol) or 500 mg q2weeks (Euro-Lupus protocol).",
        "maximum_dose": "1.5 g/m2 per pulse; cumulative max ~36g",
        "transplant_considerations": "Used for severe rejection when other agents fail. High infection risk. Avoid in unstable patients.",
    },
    "Dapagliflozin": {
        "mechanism": "Selective sodium-glucose cotransporter 2 (SGLT2) inhibitor. Reduces glucose reabsorption in proximal tubule, causing glycosuria. Also reduces sodium reabsorption, reducing intraglomerular pressure. Improves oxygen delivery to tubules. Reduces inflammation and fibrosis via ketone body shift.",
        "common_side_effects": ["Genital mycotic infections (vulvovaginal candidiasis, balanitis)",
                                 "Polyuria", "Volume depletion", "Orthostatic hypotension",
                                 "Thirst", "Headache"],
        "serious_side_effects": ["Diabetic ketoacidosis (euglycemic DKA)", "Fournier gangrene (rare)",
                                  "Acute kidney injury (volume depletion)", "Lower limb amputation (canagliflozin mostly)",
                                  "Bone fracture risk"],
        "monitoring_parameters": "eGFR and volume status before initiation. Monitor for UTI and genital infection symptoms. Hold during acute illness, fasting, or surgery (sick day rules).",
        "stopping_criteria": "Hold during acute illness with reduced oral intake, prior to major surgery (hold 1-2 days), or if eGFR declines >30% after initiation. Discontinue if ketoacidosis develops.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2024", "chapter": "DKD", "recommendation": "First-line for DKD independent of glycemic control; eGFR >25"},
            {"source": "KDIGO 2024", "chapter": "CKD", "recommendation": "Recommended for CKD with proteinuria regardless of diabetes status"},
        ],
        "typical_dosage": "10 mg once daily. No dose adjustment needed for renal function (initiate if eGFR >25).",
        "maximum_dose": "10 mg/day",
        "transplant_considerations": "Increased risk of UTIs and volume depletion. Limited data in transplant. Consider cautiously.",
    },
    "Finerenone": {
        "mechanism": "Non-steroidal, selective mineralocorticoid receptor antagonist (ns-MRA). Blocks MR-mediated inflammation and fibrosis in kidney and heart. Higher receptor selectivity and potency than spironolactone with less sex-hormone related side effects.",
        "common_side_effects": ["Hyperkalemia", "Hypotension", "Headache", "Dizziness"],
        "serious_side_effects": ["Severe hyperkalemia (K >6.0)", "Acute kidney injury",
                                  "Adrenal insufficiency (rare)"],
        "monitoring_parameters": "Serum potassium at baseline, 2-4 weeks after initiation, then monthly x3, then 3-monthly. eGFR monitoring. Hold if K >5.5 or eGFR decline >30%.",
        "stopping_criteria": "Discontinue if K >6.0 despite management. Hold if acute illness or add nephrotoxic drugs. Reassess if eGFR declines >30%.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2024", "chapter": "DKD", "recommendation": "Recommend for CKD with proteinuria and diabetes despite RAASi + SGLT2i"},
        ],
        "typical_dosage": "10 mg once daily if eGFR 25-60; 20 mg once daily if eGFR >60. Titrate based on potassium.",
        "maximum_dose": "20 mg/day",
        "transplant_considerations": "Limited transplant data. High hyperkalemia risk with CNIs.",
    },
    "Hydroxychloroquine": {
        "mechanism": "Antimalarial with immunomodulatory properties. Inhibits TLR signaling, reduces inflammatory cytokine production (IL-1, IL-6, TNF-alpha, IFN-alpha), interferes with antigen presentation in autoimmune diseases. Accumulates in lysosomes, raising pH and reducing autoantigen processing.",
        "common_side_effects": ["Nausea/diarrhea (usually transient)", "Headache", "Dizziness",
                                 "Pruritus", "Skin rash", "Alopecia"],
        "serious_side_effects": ["Retinal toxicity/retinopathy (irreversible; risk increases after 5 years or >5mg/kg)",
                                  "Cardiomyopathy (restrictive, rare)", "QT prolongation",
                                  "Neuropsychiatric effects (rare)", "Hypoglycemia",
                                  "G6PD hemolysis (caution)"],
        "monitoring_parameters": "Baseline and annual ophthalmology (fundoscopy, VF, SD-OCT). Baseline ECG (QTc). CBC, LFTs, G6PD screening in high-risk populations.",
        "stopping_criteria": "Stop if retinal toxicity detected (irreversible). Reduce dose if GI intolerance. Discontinue if QTc >500ms.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2024", "chapter": "Lupus Nephritis", "recommendation": "HCQ should be used in all patients with lupus nephritis unless contraindicated"},
            {"source": "ERA 2022", "chapter": "SLE", "recommendation": "HCQ reduces lupus flares and improves survival"},
        ],
        "typical_dosage": "200-400 mg/day (≤5 mg/kg real body weight).",
        "maximum_dose": "5 mg/kg/day",
        "transplant_considerations": "Generally safe post-transplant for SLE patients. Monitor for QT prolongation with CNIs.",
    },
    "Tacrolimus": {
        "mechanism": "Calcineurin inhibitor. Binds FK-binding protein 12, inhibiting calcineurin phosphatase → blocks NF-AT activation → reduces IL-2 and other cytokine gene transcription → suppresses T-cell activation and proliferation.",
        "common_side_effects": ["Tremor", "Headache", "Hypertension", "Hyperkalemia",
                                 "Hypomagnesemia", "Insomnia", "Diarrhea", "Nausea",
                                 "Post-transplant diabetes (PTDM)", "Nephrotoxicity"],
        "serious_side_effects": ["Acute and chronic nephrotoxicity", "Thrombotic microangiopathy (TMA)",
                                  "Posterior reversible encephalopathy syndrome (PRES)",
                                  "Neurotoxicity (seizures, encephalopathy)",
                                  "Severe infections (CMV, BK, EBV)",
                                  "PTLD (EBV-driven)", "Cardiomyopathy (rare)"],
        "monitoring_parameters": "Trough levels (target varies by indication: 5-15 ng/mL in transplant, 2-10 ng/mL in GN). BP, eGFR, K, Mg weekly initially, then monthly. Fasting glucose/HbA1c. ECG if symptomatic.",
        "stopping_criteria": "Reduce dose if nephrotoxicity or neurotoxicity. Hold if TMA, PRES, or severe infection. Discontinue if no response after 6 months in GN treatment.",
        "evidence_level": "1",
        "guideline_recommendations": [
            {"source": "KDIGO 2021", "chapter": "MCD", "recommendation": "Effective steroid-sparing agent for MCD"},
            {"source": "KDIGO 2021", "chapter": "Membranous", "recommendation": "CNI-based regimen for resistant membranous (alternative to rituximab)"},
            {"source": "KDIGO 2024", "chapter": "Transplant", "recommendation": "Cornerstone of maintenance immunosuppression"},
        ],
        "typical_dosage": "0.05-0.2 mg/kg/day divided BID. Adjust to target trough level.",
        "maximum_dose": "Based on levels; typical max 10-15 mg/day",
        "transplant_considerations": "First-line maintenance immunosuppression with MMF. Monitor trough levels 3-monthly. Manage hypertension, diabetes, and nephrotoxicity.",
    },
}


class Command(BaseCommand):
    help = "Seed V4.0 drug knowledge: mechanism, side effects, monitoring, dosage"

    def handle(self, *args, **options):
        count = 0
        for drug_name, knowledge in DRUG_KNOWLEDGE.items():
            try:
                drug = DrugMaster.objects.get(generic_name__iexact=drug_name)
            except DrugMaster.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"DrugMaster '{drug_name}' not found, skipping"))
                continue

            updated = 0
            if knowledge.get("mechanism"):
                drug.mechanism_of_action = knowledge["mechanism"]
                updated += 1
            if knowledge.get("common_side_effects"):
                drug.common_side_effects = knowledge["common_side_effects"]
                updated += 1
            if knowledge.get("serious_side_effects"):
                drug.serious_side_effects = knowledge["serious_side_effects"]
                updated += 1
            if knowledge.get("monitoring_parameters"):
                drug.monitoring_parameters = knowledge["monitoring_parameters"]
                updated += 1
            if knowledge.get("stopping_criteria"):
                drug.stopping_criteria = knowledge["stopping_criteria"]
                updated += 1
            if knowledge.get("evidence_level"):
                drug.evidence_level = knowledge["evidence_level"]
                updated += 1
            if knowledge.get("guideline_recommendations"):
                drug.guideline_recommendations = knowledge["guideline_recommendations"]
                updated += 1
            if knowledge.get("typical_dosage"):
                drug.typical_dosage = knowledge["typical_dosage"]
                updated += 1
            if knowledge.get("maximum_dose"):
                drug.maximum_dose = knowledge["maximum_dose"]
                updated += 1
            if knowledge.get("transplant_considerations"):
                drug.transplant_considerations = knowledge["transplant_considerations"]
                updated += 1

            drug.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Updated {count} drugs with expanded knowledge fields"
        ))
