# GDES_VERA_CASE_SUMMARY.md

# GDES → Vera Clinical Case Summary

Version: 1.0

Priority: High

---

# Objective

Replace the verbose consultation letter with a concise, structured case summary that can be copied directly into Vera Health.

The summary should contain only the essential clinical information required for treatment planning.

---

# User Interface

Display two sections.

---

## Case Summary

| Field | Value |
|------|------|
| Diagnosis | IgA Nephropathy / IgA Vasculitis Nephritis |
| Patient | 54 years • Male • Weight 77.0 kg |
| Height | 177 cm |
| Blood Pressure | 155/77 mmHg |
| eGFR | 71.9 mL/min/1.73m² |
| Serum Creatinine | 1.2 mg/dL |
| Proteinuria | 2.2 g/day |
| CKD Stage | G2 |
| Relevant Comorbidities | Hypertension |
| Current Medication | Atorvastatin |
| Kidney Biopsy | IgA Nephropathy, Crescents absent |
| Current GDES Assessment | Active disease with persistent proteinuria |

---

## Copy for Vera

Generate a plain-text summary that can be copied with one click.

```
Please review the following patient independently and generate a structured, evidence-based management plan.

Patient Summary

Diagnosis:
IgA Nephropathy / IgA Vasculitis Nephritis

Age:
54 years

Sex:
Male

Weight:
77 kg

Height:
177 cm

Blood Pressure:
155/77 mmHg

eGFR:
71.9 mL/min/1.73m²

Serum Creatinine:
1.2 mg/dL

24-hour Urine Protein:
2.2 g/day

CKD Stage:
G2

Relevant Comorbidities:
Hypertension

Current Medication:
Atorvastatin

Kidney Biopsy:
IgA Nephropathy
Crescents absent

Please provide:

1. Confirmation or revision of the diagnosis.

2. Disease severity and risk assessment.

3. A personalised treatment plan based on:
   • Age
   • Sex
   • Weight
   • Renal function
   • Current clinical findings

4. Drug recommendations including:
   • Drug name
   • Dose
   • Frequency
   • Duration
   • Renal dose adjustment
   • Monitoring requirements

5. Monitoring plan and follow-up schedule.

6. Contraindications and drug interactions.

7. Supporting guideline recommendations and evidence.

Please provide your recommendations in a structured clinical format.
```

---

# Buttons

- Copy for Vera
- Open Vera Health
- Print Case Summary
- Export PDF

---

# Design Principles

The summary should:

- Be no longer than one screen.
- Include only clinically relevant information.
- Exclude lengthy GDES treatment recommendations.
- Exclude narrative explanations.
- Be easy to read by both clinicians and AI systems.
- Be automatically populated from the patient's current record.
- Be suitable for future use with other clinical AI systems.

---

# Acceptance Criteria

✓ One-page concise case summary.

✓ One-click "Copy for Vera".

✓ Automatic population from patient data.

✓ Clear request for an independent structured treatment plan.

✓ Requests personalised drug dosing based on patient characteristics.

✓ Requests monitoring and follow-up recommendations.

✓ Requests evidence and guideline support.

✓ No unnecessary narrative or duplicated information.