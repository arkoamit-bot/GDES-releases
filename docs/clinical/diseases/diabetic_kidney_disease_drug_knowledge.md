# Diabetic Kidney Disease — Drug Knowledge Base

**Document ID:** DKD-DRUG-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Drug Knowledge  

---

## 1. Document Purpose

Complete drug knowledge specification for Diabetic Kidney Disease pharmacotherapy.

---

## 2. Drug Classification Overview

| Drug Class | Role | Setting | Evidence Level |
|---|---|---|---|
| RAASi (ACEi/ARB) | Albuminuria reduction, renoprotection | First-line for all with albuminuria | KDIGO 1A |
| SGLT2i (dapagliflozin, empagliflozin) | Cardiorenal protection | All DKD with eGFR >=20 | KDIGO 1A |
| Finerenone (nsMRA) | Additional albuminuria reduction | Persistent ACR >=30 | KDIGO 1A |
| GLP-1 RA (semaglutide, dulaglutide) | Glycemic + CV + weight | Overweight + suboptimal glucose | ADA 1A |
| Metformin | First-line glucose control | eGFR >30 | ADA 1A |
| Statins (atorvastatin, rosuvastatin) | CV risk reduction | All DKD | ESC 1A |
| Diuretics (furosemide, thiazide) | Volume/BP management | Edema/resistant HTN | KDIGO 1B |
| CCB (amlodipine) | Add-on BP control | Resistant hypertension | KDIGO 1B |

---

## 3. RAASi (ACEi/ARB)

| Drug | Starting Dose | Target Dose | Notes |
|---|---|---|---|
| Lisinopril | 5-10 mg daily | 20-40 mg daily | ACEi first-line |
| Enalapril | 5 mg daily | 20 mg BID | ACEi alternative |
| Losartan | 25-50 mg daily | 100 mg daily | ARB first-line |
| Valsartan | 80 mg daily | 320 mg daily | ARB alternative |
| Ramipril | 2.5 mg daily | 10 mg daily | CV benefit proven |

Monitor K+ and Cr 2-4 wks after initiation/titration. Avoid combination ACEi + ARB.

---

## 4. SGLT2i

| Drug | Dose | eGFR Threshold | Notes |
|---|---|---|---|
| Dapagliflozin | 10 mg daily | >=20 | DAPA-CKD proven |
| Empagliflozin | 10 mg daily | >=20 | EMPA-KIDNEY proven |
| Canagliflozin | 100 mg daily | >=30 | CREDENCE proven |

Monitor volume status, genital mycotic infections. Euglycemic DKA warning (type 1 DM).

---

## 5. Finerenone (nsMRA)

**Dose:** 10 mg daily -> 20 mg daily if K+ <=4.8 and eGFR stable.
**CI:** eGFR <25, K+ >5.0, concomitant strong CYP3A4 inhibitors.
**Monitor:** K+ at 2-4 weeks.

---

## 6. GLP-1 RA

| Drug | Dose | CV Benefit | Weight Loss |
|---|---|---|---|
| Semaglutide (Ozempic) | 0.5-1 mg/week SC | SUSTAIN-6 positive | 5-10% |
| Semaglutide (Wegovy) | 2.4 mg/week SC | SELECT positive | 10-15% |
| Dulaglutide (Trulicity) | 1.5-4.5 mg/week SC | REWIND positive | 3-5% |

---

## 7. Drug Selection Algorithm

```
DKD Confirmed
      |
  +---+---+
  |       |
Albuminuria  Normoalbuminuria
  |       |
RAASi titrate  Monitor ACR annually
  |       |
  +---eGFR >=20
  |       |
Add SGLT2i  Consider GLP-1 RA if:
  |         HbA1c >7% or obesity
  +---ACR persistently >=30
  |       |
Add Finerenone 10-20 mg
  |       |
BP not at target <130/80
  |       |
Add CCB or thiazide
  |       |
Statin for all
```
