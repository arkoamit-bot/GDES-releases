"""
Curated CRF code lists ported from the BIRDEM GN Clinic CRF (crf_spec.json).
Each is a Django choices list [(value, label)] — value == label (human-readable),
so dropdowns replace free-text boxes for data entry.
"""


SEX = [
    ("Male", "Male"),
    ("Female", "Female"),
    ("Other", "Other"),
    ("Unknown", "Unknown"),
]

DIABETES_STATUS = [
    ("No diabetes", "No diabetes"),
    ("Type 1 DM", "Type 1 DM"),
    ("Type 2 DM", "Type 2 DM"),
    ("Other", "Other"),
    ("Unknown", "Unknown"),
]

SMOKING = [
    ("Never", "Never"),
    ("Current", "Current"),
    ("Former", "Former"),
    ("Unknown", "Unknown"),
]

PRESENTATION = [
    ("Nephrotic syndrome", "Nephrotic syndrome"),
    ("Nephritic syndrome", "Nephritic syndrome"),
    ("RPGN", "RPGN"),
    ("AKI", "AKI"),
    ("AKI on CKD", "AKI on CKD"),
    ("CKD with proteinuria", "CKD with proteinuria"),
    ("Asymptomatic urinary abnormality", "Asymptomatic urinary abnormality"),
    ("Active sediment", "Active sediment"),
    ("Other", "Other"),
]

OEDEMA = [
    ("None", "None"),
    ("Mild", "Mild"),
    ("Moderate", "Moderate"),
    ("Severe-anasarca", "Severe-anasarca"),
]

RETINOPATHY = [
    ("No", "No"),
    ("NPDR", "NPDR"),
    ("PDR", "PDR"),
    ("Maculopathy", "Maculopathy"),
    ("Unknown", "Unknown"),
    ("Not assessed", "Not assessed"),
]

CVD = [
    ("None", "None"),
    ("IHD", "IHD"),
    ("Stroke", "Stroke"),
    ("HF", "HF"),
    ("PAD", "PAD"),
    ("Multiple", "Multiple"),
    ("Unknown", "Unknown"),
]

HAEMATURIA = [
    ("Absent", "Absent"),
    ("Microscopic", "Microscopic"),
    ("Macroscopic", "Macroscopic"),
    ("Unknown", "Unknown"),
]

ADEQUACY = [
    ("Adequate", "Adequate"),
    ("Limited", "Limited"),
    ("Inadequate", "Inadequate"),
    ("Unknown", "Unknown"),
]

SEVERITY = [
    ("None", "None"),
    ("Mild", "Mild"),
    ("Moderate", "Moderate"),
    ("Severe", "Severe"),
    ("Unknown", "Unknown"),
]

PATHOLOGY = [
    ("IgAN", "IgAN"),
    ("Membranous nephropathy", "Membranous nephropathy"),
    ("FSGS", "FSGS"),
    ("MCD", "MCD"),
    ("Lupus nephritis", "Lupus nephritis"),
    ("ANCA GN", "ANCA GN"),
    ("Anti-GBM", "Anti-GBM"),
    ("MPGN-C3G", "MPGN-C3G"),
    ("Infection-related GN", "Infection-related GN"),
    ("DKD only", "DKD only"),
    ("Other", "Other"),
]

PATIENT_CATEGORY = [
    ("GN only", "GN only"),
    ("Diabetes + GN", "Diabetes + GN"),
    ("Diabetes + DKD + GN", "Diabetes + DKD + GN"),
    ("Diabetes + DKD only", "Diabetes + DKD only"),
    ("Non-diagnostic", "Non-diagnostic"),
    ("Suspected GN no biopsy", "Suspected GN no biopsy"),
]

GN_BROAD_GROUP = [
    ("Primary GN", "Primary GN"),
    ("Secondary GN", "Secondary GN"),
    ("DKD only", "DKD only"),
    ("DKD + GN", "DKD + GN"),
    ("Hereditary GBM disease", "Hereditary GBM disease"),
    ("Monoclonal gammopathy-related", "Monoclonal gammopathy-related"),
    ("TMA/glomerular vascular injury", "TMA/glomerular vascular injury"),
    ("Other/non-diagnostic", "Other/non-diagnostic"),
]

GN_PATHOGENESIS_GROUP = [
    ("Immune-complex", "Immune-complex"),
    ("Pauci-immune", "Pauci-immune"),
    ("Anti-GBM/linear antibody", "Anti-GBM/linear antibody"),
    ("Complement-mediated", "Complement-mediated"),
    ("Podocytopathy", "Podocytopathy"),
    ("Metabolic DKD", "Metabolic DKD"),
    ("Monoclonal protein-related", "Monoclonal protein-related"),
    ("Hereditary GBM", "Hereditary GBM"),
    ("Vascular/TMA", "Vascular/TMA"),
    ("Other/unknown", "Other/unknown"),
]

PRIMARY_SECONDARY_STATUS = [
    ("Primary", "Primary"),
    ("Secondary", "Secondary"),
    ("DKD only", "DKD only"),
    ("DKD + GN", "DKD + GN"),
    ("Hereditary", "Hereditary"),
    ("Uncertain", "Uncertain"),
    ("Not applicable", "Not applicable"),
]

SPECIFIC_GN_DIAGNOSIS = [
    ("IgA nephropathy", "IgA nephropathy"),
    ("IgA vasculitis nephritis", "IgA vasculitis nephritis"),
    ("Membranous nephropathy - PLA2R positive", "Membranous nephropathy - PLA2R positive"),
    ("Membranous nephropathy - PLA2R negative", "Membranous nephropathy - PLA2R negative"),
    ("Membranous nephropathy - secondary/associated", "Membranous nephropathy - secondary/associated"),
    ("Minimal change disease", "Minimal change disease"),
    ("FSGS - primary", "FSGS - primary"),
    ("FSGS - secondary/adaptive", "FSGS - secondary/adaptive"),
    ("FSGS - genetic/suspected genetic", "FSGS - genetic/suspected genetic"),
    ("FSGS - collapsing variant", "FSGS - collapsing variant"),
    ("FSGS - tip lesion variant", "FSGS - tip lesion variant"),
    ("FSGS - cellular variant", "FSGS - cellular variant"),
    ("FSGS - perihilar variant", "FSGS - perihilar variant"),
    ("FSGS - NOS", "FSGS - NOS"),
    ("Lupus nephritis class I", "Lupus nephritis class I"),
    ("Lupus nephritis class II", "Lupus nephritis class II"),
    ("Lupus nephritis class III", "Lupus nephritis class III"),
    ("Lupus nephritis class IV", "Lupus nephritis class IV"),
    ("Lupus nephritis class V", "Lupus nephritis class V"),
    ("Lupus nephritis class III+V", "Lupus nephritis class III+V"),
    ("Lupus nephritis class IV+V", "Lupus nephritis class IV+V"),
    ("ANCA-associated pauci-immune crescentic GN - MPO", "ANCA-associated pauci-immune crescentic GN - MPO"),
    ("ANCA-associated pauci-immune crescentic GN - PR3", "ANCA-associated pauci-immune crescentic GN - PR3"),
    ("ANCA-associated pauci-immune crescentic GN - ANCA negative", "ANCA-associated pauci-immune crescentic GN - ANCA negative"),
    ("Anti-GBM disease", "Anti-GBM disease"),
    ("C3 glomerulopathy - C3 glomerulonephritis", "C3 glomerulopathy - C3 glomerulonephritis"),
    ("C3 glomerulopathy - dense deposit disease", "C3 glomerulopathy - dense deposit disease"),
    ("Immune-complex MPGN", "Immune-complex MPGN"),
    ("Infection-related GN - post-streptococcal", "Infection-related GN - post-streptococcal"),
    ("Infection-related GN - staphylococcal/IgA-dominant", "Infection-related GN - staphylococcal/IgA-dominant"),
    ("Infection-related GN - endocarditis-associated", "Infection-related GN - endocarditis-associated"),
    ("Infection-related GN - hepatitis B associated", "Infection-related GN - hepatitis B associated"),
    ("Infection-related GN - hepatitis C associated", "Infection-related GN - hepatitis C associated"),
    ("Cryoglobulinaemic GN", "Cryoglobulinaemic GN"),
    ("Monoclonal immunoglobulin deposition disease", "Monoclonal immunoglobulin deposition disease"),
    ("Proliferative GN with monoclonal Ig deposits - PGNMID", "Proliferative GN with monoclonal Ig deposits - PGNMID"),
    ("Amyloidosis - renal", "Amyloidosis - renal"),
    ("Fibrillary GN", "Fibrillary GN"),
    ("Immunotactoid GN", "Immunotactoid GN"),
    ("C1q nephropathy", "C1q nephropathy"),
    ("Thin basement membrane nephropathy", "Thin basement membrane nephropathy"),
    ("Alport syndrome / hereditary nephritis", "Alport syndrome / hereditary nephritis"),
    ("Thrombotic microangiopathy with glomerular injury", "Thrombotic microangiopathy with glomerular injury"),
    ("Diabetic kidney disease only - no GN", "Diabetic kidney disease only - no GN"),
    ("Diabetic kidney disease + IgA nephropathy", "Diabetic kidney disease + IgA nephropathy"),
    ("Diabetic kidney disease + membranous nephropathy", "Diabetic kidney disease + membranous nephropathy"),
    ("Diabetic kidney disease + FSGS", "Diabetic kidney disease + FSGS"),
    ("Diabetic kidney disease + lupus nephritis", "Diabetic kidney disease + lupus nephritis"),
    ("Diabetic kidney disease + ANCA GN", "Diabetic kidney disease + ANCA GN"),
    ("Diabetic kidney disease + infection-related GN", "Diabetic kidney disease + infection-related GN"),
    ("Diabetic kidney disease + other GN", "Diabetic kidney disease + other GN"),
    ("Hypertensive nephrosclerosis only - no GN", "Hypertensive nephrosclerosis only - no GN"),
    ("Tubulointerstitial nephritis predominant", "Tubulointerstitial nephritis predominant"),
    ("Other specified GN", "Other specified GN"),
    ("Unclassified GN", "Unclassified GN"),
    ("Inadequate biopsy / non-diagnostic", "Inadequate biopsy / non-diagnostic"),
]

ANCA = [
    ("PR3 positive", "PR3 positive"),
    ("MPO positive", "MPO positive"),
    ("Positive unspecified", "Positive unspecified"),
    ("Negative", "Negative"),
    ("Not done", "Not done"),
]

DIALYSIS = [
    ("No dialysis", "No dialysis"),
    ("Temporary dialysis", "Temporary dialysis"),
    ("Maintenance haemodialysis", "Maintenance haemodialysis"),
    ("Peritoneal dialysis", "Peritoneal dialysis"),
    ("Transplant", "Transplant"),
    ("Unknown", "Unknown"),
]

DEATH_CAUSE = [
    ("Kidney failure", "Kidney failure"),
    ("Cardiovascular", "Cardiovascular"),
    ("Infection", "Infection"),
    ("Malignancy", "Malignancy"),
    ("Other", "Other"),
    ("Unknown", "Unknown"),
]

VITAL = [
    ("Alive", "Alive"),
    ("Dead", "Dead"),
    ("Unknown", "Unknown"),
]

REMISSION = [
    ("Complete remission", "Complete remission"),
    ("Partial remission", "Partial remission"),
    ("No response", "No response"),
    ("Relapse", "Relapse"),
    ("Not assessed", "Not assessed"),
]

INFECTION = [
    ("None", "None"),
    ("Mild outpatient", "Mild outpatient"),
    ("Hospitalised", "Hospitalised"),
    ("Severe sepsis", "Severe sepsis"),
    ("Unknown", "Unknown"),
]

TRACKING_STATUS = [
    ("Active", "Active"),
    ("Visit due", "Visit due"),
    ("Overdue", "Overdue"),
    ("Completed 5-year follow-up", "Completed 5-year follow-up"),
    ("Lost to follow-up", "Lost to follow-up"),
    ("Withdrawn consent", "Withdrawn consent"),
    ("Died", "Died"),
]

FINERENONE_CONTEXT = [
    ("Diabetic CKD", "Diabetic CKD"),
    ("Non-diabetic CKD", "Non-diabetic CKD"),
    ("Other", "Other"),
    ("Unknown", "Unknown"),
]

RAAS = [
    ("None", "None"),
    ("ACEi", "ACEi"),
    ("ARB", "ARB"),
    ("Both sequentially", "Both sequentially"),
    ("Contraindicated", "Contraindicated"),
]

STEROID = [
    ("None", "None"),
    ("Oral only", "Oral only"),
    ("IV pulse + oral", "IV pulse + oral"),
    ("IV pulse only", "IV pulse only"),
    ("Unknown", "Unknown"),
]

BIOPSY_STATUS = [
    ("Done", "Done"),
    ("Not done", "Not done"),
    ("Planned", "Planned"),
    ("Contraindicated", "Contraindicated"),
    ("Refused", "Refused"),
]

SOCIOECONOMIC = [
    ("Low", "Low"),
    ("Lower-middle", "Lower-middle"),
    ("Middle", "Middle"),
    ("Upper-middle", "Upper-middle"),
    ("High", "High"),
]

EDUCATION = [
    ("None", "None"),
    ("Primary", "Primary"),
    ("Secondary", "Secondary"),
    ("Higher secondary", "Higher secondary"),
    ("Graduate", "Graduate"),
    ("Postgraduate", "Postgraduate"),
]

# Administrative divisions of Bangladesh (residence), + outside option.
DIVISION = [
    ("Dhaka", "Dhaka"),
    ("Chattogram", "Chattogram"),
    ("Rajshahi", "Rajshahi"),
    ("Khulna", "Khulna"),
    ("Barishal", "Barishal"),
    ("Sylhet", "Sylhet"),
    ("Rangpur", "Rangpur"),
    ("Mymensingh", "Mymensingh"),
    ("Outside Bangladesh", "Outside Bangladesh"),
]

OCCUPATION = [
    ("Housewife", "Housewife"),
    ("Service - Government", "Service - Government"),
    ("Service - Private", "Service - Private"),
    ("Business", "Business"),
    ("Farmer / Agriculture", "Farmer / Agriculture"),
    ("Day labourer", "Day labourer"),
    ("Garment worker", "Garment worker"),
    ("Driver", "Driver"),
    ("Teacher", "Teacher"),
    ("Professional", "Professional"),
    ("Student", "Student"),
    ("Retired", "Retired"),
    ("Unemployed", "Unemployed"),
    ("Other", "Other"),
]

# Oedema grade (clinical 0 / 1+ ... 4+); stored as the integer 0-4.
OEDEMA_GRADE = [
    (0, "0 (none)"),
    (1, "1+"),
    (2, "2+"),
    (3, "3+"),
    (4, "4+"),
]

# --- Baseline A–E expansion (workflow module) -------------------------------
ALCOHOL = [
    ("never", "Never"),
    ("former", "Former"),
    ("current", "Current"),
]

VOLUME_STATUS = [
    ("euvolemic", "Euvolemic"),
    ("hypervolemic", "Hypervolemic / overloaded"),
    ("hypovolemic", "Hypovolemic / depleted"),
]

# Presenting syndrome — multi-select (a patient can present with more than one).
PRESENTATION_SYNDROMES = [
    ("isolated_proteinuria", "Isolated proteinuria"),
    ("isolated_hematuria", "Isolated hematuria"),
    ("proteinuria_hematuria", "Proteinuria + hematuria"),
    ("nephrotic", "Nephrotic syndrome"),
    ("nephritic", "Nephritic syndrome"),
    ("nephritic_nephrotic", "Nephritic-nephrotic syndrome"),
    ("rpgn", "Rapidly progressive GN"),
    ("aki", "Unexplained AKI"),
    ("ckd", "Unexplained CKD"),
    ("hypertension", "Hypertension"),
    ("incidental", "Incidental urinary abnormality"),
]

# Presenting symptoms — multi-select.
PRESENTING_SYMPTOMS = [
    ("edema", "Edema"),
    ("oliguria", "Oliguria"),
    ("gross_hematuria", "Gross hematuria"),
    ("hypertension", "Hypertension"),
    ("fever", "Fever"),
    ("rash", "Rash"),
    ("arthralgia", "Arthralgia"),
    ("weight_loss", "Weight loss"),
    ("pulmonary", "Pulmonary symptoms"),
    ("other", "Others"),
]

# --- Examination finding dropdowns -----------------------------------------
FUNDOSCOPY = [
    ("normal", "Normal"),
    ("npdr", "Non-proliferative DR (NPDR)"),
    ("pdr", "Proliferative DR (PDR)"),
    ("maculopathy", "Diabetic maculopathy"),
    ("hypertensive", "Hypertensive retinopathy"),
    ("not_done", "Not done"),
]

SKIN_FINDINGS = [
    ("none", "None"),
    ("malar_rash", "Malar / butterfly rash"),
    ("purpura", "Palpable purpura"),
    ("vasculitic", "Vasculitic rash / ulcer"),
    ("livedo", "Livedo reticularis"),
    ("photosensitivity", "Photosensitivity / discoid"),
    ("pallor", "Pallor"),
    ("other", "Other"),
]

JOINT_FINDINGS = [
    ("none", "None"),
    ("arthralgia", "Arthralgia (no swelling)"),
    ("synovitis", "Synovitis / active arthritis"),
    ("deformity", "Deformity"),
    ("other", "Other"),
]

# Common secondary causes / associations for a secondary GN.
SECONDARY_CAUSE = [
    ("sle", "SLE / lupus"),
    ("hbv", "Hepatitis B"),
    ("hcv", "Hepatitis C"),
    ("hiv", "HIV"),
    ("diabetes", "Diabetes mellitus"),
    ("amyloidosis", "Amyloidosis"),
    ("paraprotein", "Monoclonal gammopathy / paraprotein"),
    ("malignancy", "Malignancy"),
    ("infection", "Infection-related (post-infectious)"),
    ("drug", "Drug-induced"),
    ("vasculitis", "Systemic vasculitis (ANCA)"),
    ("other", "Other"),
]
