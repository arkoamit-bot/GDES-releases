"""Seed V4.0 clinical case library for validation.

Creates gold-standard clinical cases for each supported disease.
Each case represents a typical or atypical presentation with expected
reasoning outputs for automated validation.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from knowledge.models import Disease, ClinicalCase


CASES = {
    "iga": [
        {
            "case_id": "CASE-IGA-TYP-001",
            "title": "Classic IgA Nephropathy in a Young Adult",
            "presentation_type": "typical",
            "history": "A 28-year-old male presents with episodes of visible hematuria coinciding with upper respiratory tract infections. He reports foamy urine and mild ankle swelling. No prior kidney disease. He is otherwise healthy.",
            "examination": "BP 138/86 mmHg. No edema. No purpura. Normal ENT exam.",
            "lab_data": {
                "creatinine": 1.1, "eGFR": 78, "UPCR": 1.2,
                "serum_albumin": 3.8, "C3": 120, "C4": 28,
                "urine_rbc": "30-50/hpf (dysmorphic)", "urine_casts": "RBC casts present",
            },
            "biopsy_data": {
                "light_microscopy": "Mesangial hypercellularity, M1 E0 S0 T0 C0",
                "immunofluorescence": "Dominant mesangial IgA (3+)",
                "electron_microscopy": "Mesangial electron-dense deposits",
            },
            "diagnosis": "IgA nephropathy (Oxford MEST-C M1E0S0T0C0)",
            "expected_differential": [
                {"disease": "IgA Nephropathy", "score": 85, "rank": 1},
                {"disease": "Thin Basement Membrane", "score": 5, "rank": 2},
                {"disease": "Infection-related GN", "score": 3, "rank": 3},
            ],
            "expected_reasoning": [
                "Step 1: Hematuria + RBC casts indicate glomerular source",
                "Step 2: Infection-timed hematuria raises IgA nephropathy",
                "Step 3: Biopsy confirms dominant mesangial IgA",
                "Step 4: Low-risk Oxford MEST-C (M1E0S0T0C0)",
                "Step 5: Assess progression risk - low based on eGFR 78, UPCR 1.2",
            ],
            "expected_recommendations": [
                "Start RAASi (ACEi/ARB) for proteinuria >0.5g/day",
                "BP target <130/80 mmHg",
                "Lifestyle: low salt diet, avoid nephrotoxins",
                "Monitor proteinuria and eGFR every 3 months",
            ],
            "expected_monitoring": ["3-monthly UPCR", "3-monthly eGFR", "6-monthly BP check"],
            "expected_followup": ["Nephrology follow-up every 3 months", "Annual influenza vaccination",
                                   "Pneumococcal vaccination"],
            "treatment": "Ramipril 5mg daily was started. BP improved to 125/78. Proteinuria decreased to UPCR 0.6 at 3 months.",
            "outcome": "Stable disease with residual hematuria and mild proteinuria. eGFR stable at 80. No immunosuppression needed.",
            "is_gold_standard": True,
        },
        {
            "case_id": "CASE-IGA-RISK-002",
            "title": "High-Risk IgA with Crescentic Disease",
            "presentation_type": "rapid",
            "history": "A 35-year-old male presents with macroscopic hematuria, rapid weight gain (8kg in 2 weeks), and frothy urine. He had an URTI 2 weeks ago. No prior renal history.",
            "examination": "BP 155/95 mmHg. Bilateral pitting edema to thighs. No rash.",
            "lab_data": {
                "creatinine": 2.8, "eGFR": 28, "UPCR": 3.5, "serum_albumin": 2.9,
                "C3": 110, "C4": 25, "urine_rbc": ">100/hpf",
                "urine_casts": "RBC casts + granular casts",
            },
            "biopsy_data": {
                "light_microscopy": "Mesangial + endocapillary hypercellularity, 30% crescents",
                "immunofluorescence": "Dominant mesangial IgA (3+)",
                "electron_microscopy": "Mesangial and subendothelial deposits",
                "oxford_score": "M1 E1 S1 T0 C2",
            },
            "diagnosis": "IgA nephropathy with active crescentic disease (M1E1S1T0C2)",
            "expected_differential": [
                {"disease": "IgA Nephropathy", "score": 90, "rank": 1},
                {"disease": "ANCA Vasculitis", "score": 5, "rank": 2},
                {"disease": "Anti-GBM Disease", "score": 2, "rank": 3},
            ],
            "expected_reasoning": [
                "Step 1: RPGN presentation with crescents on biopsy",
                "Step 2: Dominant IgA confirms IgA vasculitis/nephropathy",
                "Step 3: ANCA and anti-GBM serology negative (rule out dual disease)",
                "Step 4: High-risk features: crescents, proteinuria >3g, eGFR <30",
                "Step 5: Requires urgent immunosuppression",
            ],
            "expected_recommendations": [
                "Methylprednisolone 1g IV x3 pulses then oral taper",
                "Consider cyclophosphamide or MMF for crescentic disease",
                "RAASi once stable",
                "SGLT2i if proteinuria persists after induction",
                "BP target <130/80",
            ],
            "expected_monitoring": ["Weekly eGFR and UPCR during induction",
                                     "Monthly CBC, LFTs on immunosuppression",
                                     "Quantify proteinuria monthly"],
            "expected_followup": ["Nephrology weekly during induction",
                                   "Transition to 3-monthly after remission",
                                   "Plan steroid taper over 6 months"],
            "treatment": "Methylprednisolone 1g IV x3 followed by prednisolone 0.8mg/kg/day. MMF 1g BID started. Ramipril added after 4 weeks.",
            "outcome": "eGFR improved to 45 at 3 months. Proteinuria reduced to UPCR 1.2. Remission achieved at 6 months.",
            "is_gold_standard": True,
        },
    ],
    "membranous": [
        {
            "case_id": "CASE-MEM-TYP-001",
            "title": "Primary Membranous Nephropathy with PLA2R Positivity",
            "presentation_type": "typical",
            "history": "A 52-year-old male presents with 6 weeks of progressive leg swelling, frothy urine, and 6kg weight gain. No hematuria. No prior kidney disease. No NSAID use.",
            "examination": "BP 142/88 mmHg. Bilateral pitting edema to knees. No rash. Normal lung fields.",
            "lab_data": {
                "creatinine": 0.9, "eGFR": 92, "UPCR": 8.5,
                "serum_albumin": 2.4, "total_protein": 5.2,
                "C3": 115, "C4": 30, "PLA2R_antibody": 286, "THSD7A": "Negative",
                "urine_rbc": "5-10/hpf", "urine_casts": "None",
            },
            "biopsy_data": {
                "light_microscopy": "Normal glomeruli by LM (Stage I)",
                "immunofluorescence": "Granular IgG (3+) along GBM, C3 (1+), PLA2R positive",
                "electron_microscopy": "Subepithelial electron-dense deposits Stage I-II",
            },
            "diagnosis": "Primary membranous nephropathy, Stage I-II, PLA2R-associated",
            "expected_differential": [
                {"disease": "Membranous Nephropathy", "score": 92, "rank": 1},
                {"disease": "Lupus Nephritis (Class V)", "score": 4, "rank": 2},
                {"disease": "MCD", "score": 2, "rank": 3},
            ],
            "expected_reasoning": [
                "Step 1: Nephrotic syndrome with bland sediment",
                "Step 2: PLA2R positive strongly supports primary membranous",
                "Step 3: Biopsy shows subepithelial deposits + granular IgG",
                "Step 4: Rule out secondary causes (SLE, HBV, malignancy)",
                "Step 5: High-risk features: proteinuria >8g, albumin <2.5",
            ],
            "expected_recommendations": [
                "Anticoagulation for albumin <2.5 (VTE risk)",
                "RAASi for proteinuria reduction",
                "Rituximab 1g IV x2 doses 2 weeks apart",
                "Restrict salt, monitor weight daily",
            ],
            "expected_monitoring": ["Monthly UPCR, albumin, eGFR, PLA2R titer"],
            "expected_followup": ["Nephrology monthly x6, then 3-monthly",
                                   "PLA2R titer monitoring q3 months"],
            "treatment": "Rituximab 1g IV days 1 and 15. RAASi titrated. Anticoagulation held due to patient preference.",
            "outcome": "PLA2R titer declined to 45 at 3 months. Partial remission at 6 months: UPCR 3.2, albumin 3.1. Complete remission at 12 months: UPCR 0.3, albumin 3.8.",
            "is_gold_standard": True,
        },
    ],
    "lupus": [
        {
            "case_id": "CASE-LUPUS-001",
            "title": "Active Class IV Lupus Nephritis",
            "presentation_type": "typical",
            "history": "A 24-year-old female with known SLE (diagnosed 2 years ago) presents with facial rash, joint pain, and new-onset leg swelling. She has been non-adherent to HCQ for 6 months.",
            "examination": "BP 146/92 mmHg. Malar rash. Oral ulcers. Bilateral ankle edema. Mild synovitis of MCP joints.",
            "lab_data": {
                "creatinine": 1.8, "eGFR": 42, "UPCR": 4.2,
                "serum_albumin": 2.8, "ANA": "1:1280 speckled",
                "anti_dsdna": 245, "C3": 48, "C4": 8,
                "CBC": "Hb 10.2, WBC 3.1, Platelets 185",
                "urine_rbc": "30-50/hpf", "urine_casts": "RBC casts + granular casts",
            },
            "biopsy_data": {
                "light_microscopy": "Diffuse proliferative GN (Class IV-G)",
                "immunofluorescence": "Full-house: IgG 3+, IgA 2+, IgM 1+, C3 3+, C1q 2+",
                "electron_microscopy": "Subendothelial deposits, mesangial deposits",
                "activity_index": 14, "chronicity_index": 2,
            },
            "diagnosis": "Lupus nephritis Class IV-G (A) with high activity",
            "expected_differential": [
                {"disease": "Lupus Nephritis", "score": 95, "rank": 1},
                {"disease": "ANCA Vasculitis", "score": 2, "rank": 2},
                {"disease": "Membranous", "score": 1, "rank": 3},
            ],
            "expected_reasoning": [
                "Step 1: Young female with SLE + active urinary sediment",
                "Step 2: Low C3/C4 + high anti-dsDNA = immune complex disease",
                "Step 3: Full-house IF on biopsy = lupus nephritis",
                "Step 4: Class IV with activity index 14 = high disease activity",
                "Step 5: Chronicity index 2 = early chronic changes",
            ],
            "expected_recommendations": [
                "Induction: MMF 2-3g/day + corticosteroids (pulse then taper)",
                "Restart HCQ 400mg/day",
                "RAASi for proteinuria",
                "Hydroxychloroquine 400mg daily",
                "PCP prophylaxis with TMP/SMX",
            ],
            "expected_monitoring": ["Monthly: eGFR, UPCR, C3/C4, anti-dsDNA, CBC",
                                     "Biannual: lipids, glucose"],
            "expected_followup": ["Nephrology monthly x6, then 3-monthly",
                                   "Rheumatology co-management"],
            "treatment": "MMF 1.5g BID started. Methylprednisolone 500mg IV x3 then prednisolone 40mg/day. HCQ 400mg/day. Ramipril 10mg/day. TMP/SMX prophylaxis.",
            "outcome": "At 6 months: Cr 1.1, UPCR 1.0, C3 85, C4 18, anti-dsDNA 48. Partial renal response. Tapering steroids.",
            "is_gold_standard": True,
        },
    ],
    "diabeticNephropathy": [
        {
            "case_id": "CASE-DKD-001",
            "title": "Diabetic Kidney Disease in Long-standing Type 2 DM",
            "presentation_type": "typical",
            "history": "A 62-year-old male with type 2 diabetes for 15 years, hypertension, and dyslipidemia. Poor glycemic control (HbA1c 8.5%). Not on SGLT2i or GLP-1 RA. Recently noted foamy urine.",
            "examination": "BP 152/90 mmHg. BMI 32. Background diabetic retinopathy. Reduced sensation to monofilament. No edema.",
            "lab_data": {
                "creatinine": 1.5, "eGFR": 48, "ACR": 450,
                "HbA1c": 8.5, "serum_albumin": 3.6,
                "urine_rbc": "0-2/hpf", "urine_casts": "None",
                "fasting_glucose": 185,
            },
            "biopsy_data": {},
            "diagnosis": "Diabetic kidney disease (CKD Stage G3bA3)",
            "expected_differential": [
                {"disease": "Diabetic Kidney Disease", "score": 90, "rank": 1},
                {"disease": "Hypertensive Nephrosclerosis", "score": 5, "rank": 2},
                {"disease": "FSGS", "score": 2, "rank": 3},
            ],
            "expected_reasoning": [
                "Step 1: Long-standing diabetes with retinopathy = strong for DKD",
                "Step 2: ACR 450 = moderately increased albuminuria (A3)",
                "Step 3: Bland sediment supports DKD over GN",
                "Step 4: No need for biopsy unless atypical features develop",
                "Step 5: High-risk profile: eGFR <60, ACR >300, HbA1c >7",
            ],
            "expected_recommendations": [
                "Start SGLT2i (dapagliflozin 10mg or empagliflozin 10mg)",
                "Maximize RAASi (ACEi/ARB titrated)",
                "Intensify glycemic control: add GLP-1 RA (semaglutide)",
                "BP target <130/80",
                "Statin therapy (atorvastatin 20mg)",
                "Low salt, low sugar diet",
            ],
            "expected_monitoring": ["3-monthly: eGFR, ACR, HbA1c, BP, electrolytes"],
            "expected_followup": ["Nephrology 3-monthly", "Cardiology annual",
                                   "Ophthalmology annual", "Foot exam annually"],
            "treatment": "Empagliflozin 10mg started. Ramipril increased to 10mg. Semaglutide 0.5mg weekly added. Metformin continued.",
            "outcome": "At 6 months: ACR 280, HbA1c 7.2, eGFR 48 (stable). BP 128/78.",
            "is_gold_standard": True,
        },
    ],
    "alport": [
        {
            "case_id": "CASE-ALP-001",
            "title": "X-Linked Alport Syndrome in a Young Male",
            "presentation_type": "typical",
            "history": "A 22-year-old male with persistent microscopic hematuria since childhood. Progressive hearing loss noted in teenage years. Family history: maternal uncle had ESKD at age 35, maternal grandfather with hearing loss and kidney disease.",
            "examination": "BP 138/86 mmHg. High-frequency hearing loss on audiometry. Anterior lenticonus on slit-lamp exam. Dot-and-fleck retinopathy. No edema.",
            "lab_data": {
                "creatinine": 1.6, "eGFR": 52, "ACR": 350,
                "serum_albumin": 3.8, "urine_rbc": ">100/hpf (dysmorphic)",
                "urine_casts": "RBC casts",
            },
            "biopsy_data": {
                "light_microscopy": "Focal segmental glomerulosclerosis, mesangial expansion",
                "immunofluorescence": "Negative (no immune deposits)",
                "electron_microscopy": "GBM thickening, splitting, lamellation (basket weave); variable thinning",
                "collagen_staining": "Absent alpha5(IV) in GBM",
            },
            "diagnosis": "X-linked Alport syndrome (COL4A5 mutation)",
            "expected_differential": [
                {"disease": "Alport Syndrome", "score": 95, "rank": 1},
                {"disease": "Thin Basement Membrane", "score": 2, "rank": 2},
                {"disease": "IgA Nephropathy", "score": 1, "rank": 3},
            ],
            "expected_reasoning": [
                "Step 1: Persistent hematuria since childhood = hereditary",
                "Step 2: Hearing loss + ocular findings + family history = Alport",
                "Step 3: EM shows GBM lamellation = pathognomonic",
                "Step 4: X-linked inheritance pattern from family history",
                "Step 5: Proteinuria + eGFR decline indicates progressive nephropathy",
            ],
            "expected_recommendations": [
                "Start RAASi (ACEi/ARB) to reduce proteinuria",
                "Consider SGLT2i for additional renoprotection",
                "Hearing aids for hearing loss",
                "Genetic counseling for family planning",
                "Avoid nephrotoxins, maintain hydration",
            ],
            "expected_monitoring": ["3-monthly: eGFR, ACR, BP", "Annual audiometry",
                                     "Annual ophthalmology"],
            "expected_followup": ["Nephrology 3-monthly", "Audiologist annually",
                                   "Ophthalmology annually"],
            "treatment": "Ramipril 10mg daily. Empagliflozin 10mg daily added. Hearing aids fitted.",
            "outcome": "After 12 months: eGFR 49 (stable), ACR 280, BP 126/78. Progressive hearing loss stabilized with aids.",
            "is_gold_standard": True,
        },
    ],
    "cryoglobulinemic": [
        {
            "case_id": "CASE-CRYO-001",
            "title": "HCV-Associated Cryoglobulinemic GN",
            "presentation_type": "typical",
            "history": "A 58-year-old male with chronic HCV (untreated), presents with palpable purpura on lower extremities, arthralgia, and bilateral leg swelling. He reports dark urine for 2 weeks.",
            "examination": "BP 144/88 mmHg. Palpable purpura on calves. Bilateral knee arthritis. Ankle edema. Reduced sensation in stocking distribution.",
            "lab_data": {
                "creatinine": 2.2, "eGFR": 32, "UPCR": 3.8,
                "serum_albumin": 3.0, "C3": 52, "C4": 4,
                "RF": 256, "cryocrit": 5,
                "HCV_PCR": 2.4e6, "HCV_genotype": "1b",
                "ANA": "Negative", "ANCA": "Negative",
                "urine_rbc": "30-50/hpf", "urine_casts": "RBC casts",
            },
            "biopsy_data": {
                "light_microscopy": "MPGN pattern with double contours",
                "immunofluorescence": "IgG 2+, IgM 2+, C3 3+, C1q 1+",
                "electron_microscopy": "Subendothelial deposits, intracapillary thrombi",
            },
            "diagnosis": "Cryoglobulinemic GN secondary to chronic HCV",
            "expected_differential": [
                {"disease": "Cryoglobulinemic GN", "score": 88, "rank": 1},
                {"disease": "Lupus Nephritis", "score": 4, "rank": 2},
                {"disease": "ANCA Vasculitis", "score": 3, "rank": 3},
                {"disease": "MPGN (other)", "score": 2, "rank": 4},
            ],
            "expected_reasoning": [
                "Step 1: HCV infection + purpura + arthralgia = cryoglobulinemia",
                "Step 2: Very low C4 with low C3 is classic for cryoglobulinemia",
                "Step 3: RF positive reflects IgM rheumatoid factor",
                "Step 4: Biopsy: MPGN with IgG+IgM+C3 and thrombi",
                "Step 5: Treatment should target HCV first",
            ],
            "expected_recommendations": [
                "Initiate direct-acting antiviral therapy for HCV",
                "For severe renal: rituximab 375mg/m2 x4 weekly",
                "Corticosteroids for acute inflammation",
                "RAASi for proteinuria",
            ],
            "expected_monitoring": ["Monthly: eGFR, UPCR, C3/C4, RF, cryocrit",
                                     "HCV viral load q3 months"],
            "expected_followup": ["Nephrology monthly during induction",
                                   "Hepatology for HCV management"],
            "treatment": "DAA therapy (sofosbuvir/velpatasvir) x12 weeks. Rituximab 375mg/m2 weekly x4. Prednisolone 30mg/day taper.",
            "outcome": "HCV cleared at 12 weeks. Cryocrit 0 at 6 months. eGFR improved to 48. UPCR 0.8.",
            "is_gold_standard": True,
        },
    ],
}


class Command(BaseCommand):
    help = "Seed V4.0 clinical case library for validation"

    @transaction.atomic
    def handle(self, *args, **options):
        count = 0
        for disease_id, case_list in CASES.items():
            try:
                disease = Disease.objects.get(id=disease_id)
            except Disease.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Disease {disease_id} not found, skipping cases"))
                continue

            for case_data in case_list:
                case_data["disease"] = disease
                _, created = ClinicalCase.objects.update_or_create(
                    case_id=case_data["case_id"],
                    defaults=case_data,
                )
                if created:
                    count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {count} clinical cases (total: {ClinicalCase.objects.count()})"
        ))
