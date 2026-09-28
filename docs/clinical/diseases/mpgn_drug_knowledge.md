# Membranoproliferative GN (MPGN) — Drug Knowledge Base

**Document ID:** MPGN-DRUG-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Drug Knowledge  

---

## 1. Document Purpose

Drug knowledge specification for Membranoproliferative GN (MPGN) pharmacotherapy. All treatment is off-label.

---

## 2. Drug Classification

| Drug Class | Role | Evidence |
|---|---|---|
| Corticosteroids | IC-MPGN first-line immunosuppression | KDIGO 2C |
| MMF | IC-MPGN steroid-sparing/maintenance | KDIGO 2C |
| Cyclophosphamide | Severe/crescentic IC-MPGN | KDIGO 2C |
| Rituximab | Refractory IC-MPGN | KDIGO 2D |
| Eculizumab | Progressive C3G | KDIGO 2D |
| DAAs | HCV-associated MPGN | KDIGO 1A |
| Clone-directed therapy | MGRS-associated | ISN 2023 |
| RAASi | Proteinuria renoprotection | KDIGO 1B |
| Plasma exchange | CFH autoantibody C3G / RPGN | KDIGO 2D |

---

## 3. Key Drugs

### 3.1 Corticosteroids
- Prednisone 1 mg/kg/day (max 80 mg) PO x8 wks then taper over 6-12 mo
- Pulse MP 500-1000 mg IV x3 for crescentic/RPGN

### 3.2 MMF
- 1-2 g/day PO divided BID
- Monitor CBC, LFT monthly

### 3.3 Cyclophosphamide
- IV 500-750 mg/m2 monthly x3-6
- Mesna prophylaxis, adequate hydration

### 3.4 Rituximab
- 375 mg/m2 IV weekly x4 or 1 g IV day 1 and 15
- Screen HBV before use

### 3.5 Eculizumab (C3G)
- 900 mg IV weekly x4, then 1200 mg q2w
- Meningococcal vaccination mandatory (ACWY + MenB)
- Monitor CH50 for dosing adequacy

### 3.6 DAAs (HCV-MPGN)
- Glecaprevir/pibrentasvir 8-12 wks
- Sofosbuvir/velpatasvir 12 wks

### 3.7 Complement Inhibitors (Trial)
- Iptacopan (factor B inhibitor): 200 mg PO BID
- Vemircopan (factor D inhibitor): dosing per protocol

---

## 4. Drug Selection Algorithm

```
MPGN Diagnosed
    |
IF Classification
    |
+---IC-MPGN---+    +---C3G---+
|              |    |         |
Cause?        Idiopathic  Supportive care
|              |    |         |
Treat cause   Pred + MMF  Progressing?
|              |    |         |
Response?     Refractory:   Yes:    No:
|              |    RTX    Eculizumab RAASi
Stable CKD    CYC if     |
             crescentic  Trial if
                         refractory
```
