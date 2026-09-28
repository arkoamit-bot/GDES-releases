# Cryoglobulinemic GN — Drug Knowledge Base

**Document ID:** CRYO-DRUG-v1.0  
**Date:** 2026-07-10  
**Version:** 1.0  
**Status:** Final  
**Domain:** Drug Knowledge  

---

## 1. Document Purpose

This document provides the complete drug knowledge specification for Cryoglobulinemic GN pharmacotherapy. DAA therapy is first-line for HCV-associated disease; rituximab is the immunosuppression of choice for moderate-severe disease. All agents for CryoGN are used based on observational data and vasculitis trial extrapolation.

---

## 2. Drug Classification Overview

| Drug Class | Role | Setting | Evidence Level |
|---|---|---|---|
| DAAs (glecaprevir/pibrentasvir, sofosbuvir/velpatasvir) | HCV eradication | First-line for HCV-CryoGN | EASL 1A |
| Rituximab (anti-CD20) | B-cell depletion | Moderate-severe disease | KDIGO 1B |
| Corticosteroids | Anti-inflammatory | Severe/RPGN/vasculitis | KDIGO 2C |
| Plasma exchange | Cryoglobulin removal | RPGN/dialysis-dependent | KDIGO 2D |
| Cyclophosphamide | Immunosuppression | Refractory disease | KDIGO 2D |
| ACEi/ARB | Renoprotection | Persistent proteinuria | KDIGO 1B |
| Diuretics | Volume management | Oedema | KDIGO 1B |
| Antihypertensives | BP control | Hypertension | KDIGO 1B |

---

## 3. Direct-Acting Antivirals (DAAs)

### 3.1 Pangenotypic Regimens

| Drug | Dose | Duration | Notes |
|---|---|---|---|
| Glecaprevir/Pibrentasvir | 3 tablets daily with food | 8-12 weeks | First-line, pangenotypic, NS3/4A + NS5A |
| Sofosbuvir/Velpatasvir | 1 tablet daily | 12 weeks | Pangenotypic, NS5B + NS5A |
| Sofosbuvir/Velpatasvir/Voxilaprevir | 1 tablet daily with food | 8 weeks | Rescue therapy for DAA failure |

### 3.2 Monitoring
- HCV RNA at week 4, end of treatment, SVR12
- LFT monitoring monthly
- Drug-drug interactions (especially with immunosuppression)

---

## 4. Rituximab

### 4.1 Indication
Moderate-severe CryoGN: Cr 2.0-3.0, moderate vasculitis, RPGN.

| Regimen | Dose | Route | Frequency |
|---|---|---|---|
| Induction | 375 mg/m2 | IV | Weekly x4 |
| Maintenance (if indicated) | 375 mg/m2 | IV | Repeat at 6 months |

### 4.2 Adverse Effects
Infusion reactions, HBV reactivation (screen HBsAg/HBcAb), hypogammaglobulinemia, PML (rare).

---

## 5. Corticosteroids

### 5.1 Indication
Severe CryoGN with RPGN, life-threatening vasculitis, mononeuritis multiplex.

| Formulation | Dose | Route | Duration |
|---|---|---|---|
| Methylprednisolone | 500-1000 mg/day | IV | 3 days (pulse) |
| Prednisone | 0.5-1 mg/kg/day (max 80 mg) | PO | Taper over 3-6 months |

---

## 6. Plasma Exchange

| Setting | Volume | Sessions |
|---|---|---|
| RPGN with dialysis dependency | 1.5 plasma volume | 5-7 |
| Severe vasculitis with mononeuritis | 1.5 plasma volume | 5-7 |

---

## 7. Cyclophosphamide

### 7.1 Indication
Refractory to rituximab or contraindication to rituximab.

| Regimen | Dose | Route | Frequency |
|---|---|---|---|
| IV pulse | 500-750 mg/m2 | IV | Monthly x3-6 |

### 7.2 Adverse Effects
Bone marrow suppression, haemorrhagic cystitis, gonadal toxicity, malignancy.

---

## 8. ACEi/ARB

### 8.1 Indication
Persistent proteinuria >0.5 g/day after treatment initiation.

| Drug | Starting Dose | Target Dose |
|---|---|---|
| Lisinopril | 5-10 mg daily | 20-40 mg daily |
| Losartan | 25-50 mg daily | 100 mg daily |

---

## 9. Type I Cryoglobulinemia Agents

| Drug | Regimen | Indication |
|---|---|---|
| Bortezomib | 1.3 mg/m2 SC days 1,4,8,11 q21d | MGUS/myeloma-associated |
| Daratumumab | 16 mg/kg IV weekly | Refractory/relapsed |
| Dexamethasone | 20-40 mg weekly | Adjunct |

---

## 10. Vaccination

| Vaccine | Timing |
|---|---|
| HBV (if negative) | Before rituximab if possible |
| Pneumococcal (PCV20 + PPSV23) | Before immunosuppression |
| Influenza | Annual |
| COVID-19 | Per guidelines |

---

## 11. Drug Selection Algorithm

```
CryoGN Confirmed
      |
  +---+---+
  |       |
HCV+   Non-HCV
  |       |
  +---Mild-Moderate
  |       |
  |   DAAs first-line
  |       |
  +---Moderate-Severe
  |       |
  |   DAAs + RTX + Steroids
  |       |
  +---RPGN/Severe Vasculitis
  |       |
  |   Pulse MP + RTX + PLEX
  |       |
  +---Refractory
      |
  Cyclophosphamide / alternative DAA
```
