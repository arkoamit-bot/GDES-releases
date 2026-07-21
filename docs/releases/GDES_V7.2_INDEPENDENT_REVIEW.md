# GDES Version 7.2 — Independent Clinical & Technical Review (Objective-Based)

**Reviewer:** Claude Code — independent external audit
**Date:** 2026-07-12
**Basis:** Direct inspection of current source + live `db.sqlite3` (8 patients, 618
active knowledge rules, 206 automated tests). This review reflects the code **as it
stands today**, after the recent safety and dashboard fixes — not earlier reports.
**Question answered against your four stated objectives**, not a generic checklist.

---

## How this review was done

I re-derived the state of the system from the code and database rather than trusting
prior audit documents (several of which are now out of date because the issues they
described have since been fixed). Every finding below carries a `file:line` or a live
query so you can re-check it. I ran the full test suite (**206 passed**) and executed
the entire CDS pipeline end-to-end against all 8 real patients.

**Headline:** The safety-critical defects from the previous audit (drug-toxicity
engine, `value_numeric`, management-plan wiring, dashboards) **have been fixed and
verified.** The system now behaves as one integrated, automated platform. The
remaining gaps are concentrated in **(a) the differential-scoring logic**,
**(b) clinical-governance *operation* (not structure)**, and **(c) two objective-level
automation gaps (research eligibility, SMS).** None are patient-endangering; the AI is
assistive, sound in content, and overridable.

---

# 1. Overall Architecture Assessment

**Verdict: Coherent and maintainable. No redesign warranted.**

- One Django project, 26 apps, cleanly split into a **registry core** (patients,
  encounters, labs, pathology, prescriptions, treatments, analytics, studies, clinic
  UI) and an **AI/CDS layer** (knowledge, clinical_reasoning, followup, events,
  timeline).
- **Integration is real, not cosmetic.** An event bus (`events/signal_handlers.py`
  → `events/dispatcher.py` → `clinical_reasoning/event_handlers.py`) auto-recomputes
  the clinical profile and outcomes on every relevant save (patient, encounter, lab,
  biopsy, treatment exposure, clinical event). High-volume events are marked async;
  when no Celery broker is configured (the desktop default, `CELERY_BROKER_URL=""`),
  `dispatch()` **degrades gracefully to in-process execution** (dispatcher.py:94-102).
  I verified this path runs.
- Data model is consistent; the registry UI and the CDS layer now read the **same**
  field names (the earlier schema drift is gone — no `numeric_value` references
  remain).

**Residual architecture issues** (all Low, safe to defer or do under freeze):
- Dead/deprecated `decision` app still in `INSTALLED_APPS` (URLs already disabled).
- `TEST-*`/seed fixture rules are ACTIVE in the production knowledge base and their
  GuidelineSource abbreviation shows as **"TEST 2026"** on live differentials —
  production rules should cite KDIGO, not "TEST".
- Two follow-up mechanisms coexist (`followup` engine + `clinical_reasoning`
  scheduler); pick one for the pilot.

---

# 2. Clinical Workflow Assessment

**Verdict: The full journey is present and now connected end-to-end.**

| Step | State | Evidence |
|------|-------|----------|
| Registration → Assessment → Labs → Biopsy | ✅ Solid | clinic forms, correct schema |
| Differential diagnosis | ⚠️ Works but **ranking is biased** | see Issue **H-1** |
| Suggested investigations | ✅ Auto (investigation_engine) | verified all 8 patients |
| Diagnosis confirmation | ✅ | pathology / primary_diagnosis |
| Management plan | ✅ Now renders in UI | `clinic/views.py:336` fix + auto-profile; `patient_detail.html:527` |
| Treatment / Monitoring | ✅ | management_plan + monitoring_plan surfaced |
| Follow-up | ✅ engine; ⚠️ SMS is a stub | followup engine (207 tasks generated) |
| SMS reminder | ❌ Stub only | `reminders/tasks.py:23` `[SMS stub]` |
| Outcome recording | ✅ Auto on lab/clinical events | `compute_patient_outcome` via event bus |
| Research enrollment | ⚠️ **Manual, not automatic** | see Issue **M-1** |

The patient-detail page now shows differential, KDIGO-aligned management plan
(first/second/rescue lines, contraindications, safety checks), monitoring plan, and
follow-up schedule — the flagship CDS output is finally visible to the clinician.

**Missing from the journey:** imaging is not a first-class step (captured only as free
text). Not a blocker for a GN pilot.

---

# 3. Clinical Safety Assessment

**Verdict: Safe for an assistive pilot. Previous blockers fixed; verified.**

Confirmed **fixed and working** (previous audit blockers):
- Drug-toxicity engine now reads real meds from `TreatmentExposure(ongoing=True)` and
  real labs via `value_numeric`; runs error-free on all 8 patients.
- Leukopenia (WBC) / hypogammaglobulinemia (IgG) direction corrected
  (`ToxicityRule.direction="low"`) — a normal WBC on MMF no longer mis-fires as
  "critical". Integration-tested (`tests/test_cds_integration.py`).
- Treatment-failure / relapse detection no longer crash on real labs.
- Pregnancy screening correctly warns on mycophenolate / cyclophosphamide / ACEi-ARB
  / statins (`management_plan.py:619`).

**Residual safety-adjacent items:**
- Risk-factor severity boost in drug toxicity relies on `patient.diabetes_status`
  only; comorbidity/allergy inputs were removed (dead apps). Low impact.
- Silent-failure pattern is reduced but a few `except Exception:` blocks remain in the
  CDS path; those now mostly `logger.exception(...)`. Keep tightening.

No unsafe recommendations, missing contraindication lists, or dangerous automatic
actions were found. The system never prescribes or acts autonomously — it proposes,
and the clinician disposes.

---

# 4. Medical Knowledge Assessment

**Verdict: Strong content; one important scoring flaw; governance data not populated.**

- **Coverage is excellent:** 618 active rules across **23 diseases** — native GN,
  transplant rejection (TCMR/AMR), BK virus, drug-induced entities — well beyond the
  "18 diseases" claim. Treatment content is current and correctly cited (IgAN:
  RAASi+SGLT2i, sparsentan/PROTECT, budesonide/NefIgArd; MN: rituximab/MENTOR,
  Ponticelli).
- **Evidence grades** populated on all rules; **guideline source** on all rules.

**But:**
- **H-1 (High) — Differential scoring is inflated and biased** (details below). The
  ranked differential is dominated by how *many* rules a disease has, not how well the
  patient matches. This is the single most important knowledge-engine defect.
- **G-1 (High) — Governance metadata unpopulated:** 0/618 rules have a named reviewer,
  a validation date, or a next-review date; `confidence_score` is a constant `0.0`;
  `recommendation_id` is empty. The knowledge is good, but nobody has formally
  signed it off.

---

# 5. Integration Assessment

**Verdict: Behaves as one integrated system.**

The event bus is the connective tissue and it works: a lab result save →
`LAB_RESULT_CREATED` → recompute outcome **and** clinical profile → management/
monitoring/follow-up plans update → dashboards reflect it. Registry, reasoning,
knowledge, management planning, follow-up, and UI are genuinely wired together. This
was the weakest area in the prior audit and is now the strongest.

Remaining disconnection: **Research (studies) is not on the event bus** — patients are
not automatically evaluated for study eligibility on registration (Issue M-1).

---

# 6. User Experience Assessment

**Verdict: Good for a busy clinic, now that CDS is visible.**

- Guided clinic forms, a workflow progress strip, one-page patient view with trend
  charts, differential, management plan, and audit trail.
- Recommendations now appear at the right time (auto-generated on data entry).
- Dashboards (Overview / Enrollment / Outcomes / Compliance) now show live data (all
  four were previously blank; fixed this session).

Minor UX items:
- The differential shows a raw numeric score (e.g. **795**) that is not clinically
  interpretable — compounded by H-1. Normalize to a %/confidence or hide the raw
  number.
- Synchronous reasoning+outcome on every save is fine for 8 patients but may add
  perceptible latency to data entry as the registry grows (Low).

---

# 7. Pilot Readiness Assessment

**Verdict: Ready for a single-center assistive pilot, with minor corrections.**

- ✅ Single-PC SQLite, offline, OneDrive-safe data dir, auto-backup (6-hourly/60),
  graceful no-Celery degradation.
- ✅ Registry + prescription + CDS + dashboards all functional on real data.
- ⚠️ Enforce **one active machine at a time** (OneDrive-synced SQLite corrupts under
  concurrent writers; two DB files already exist in the repo).
- ⚠️ Before presenting the AI layer as "clinically governed," complete G-1 (reviewer
  sign-off) and either populate or hide `confidence_score`.
- ⚠️ Retire `TEST-*` rules / fix the "TEST 2026" source so differentials cite real
  guidelines.

---

# 8. Prioritized Issues

Each issue: **why it matters · clinical impact · technical impact · recommended
solution · effort.**

> **Update 2026-07-12 — H-1 and M-1 below have since been FIXED and verified
> (210 tests pass).** H-1: rules now score only when they fire, and the
> differential shows a normalized relative confidence. M-1: automatic study
> eligibility screening is now wired to the event bus. Details retained below
> with resolution notes.

### H-1 (High) — Differential score sums `base_score` of non-matching rules ✅ FIXED
- **What:** `evaluate_entry` (`knowledge/services.py:318-343`) sets
  `total_score = base_score` and returns it **even when no condition matches**;
  `evaluate_patient_rules` then sums this across *every* rule of a disease. Verified on
  patient `000000`: **C3 glomerulopathy = 75 with 0 matched rules** (sum of base_scores
  of 26 non-matching C3 rules); **IgA = 785 with 1 matched rule** (32 rules' priors).
- **Why it matters:** the ranked differential is driven by *rule count per disease*,
  not patient fit — IgA (32 rules) and diabetic nephropathy structurally rank top for
  almost everyone. The score is clinically meaningless (795) and unexplainable, which
  directly violates your Explainability and AI-Philosophy objectives.
- **Clinical impact:** misleading diagnostic ranking; erodes clinician trust; a
  clinician who anchors on the top differential could be led toward the
  most-rules disease rather than the best-fitting one.
- **Technical impact:** localized to the scorer; ~5–10 lines.
- **Recommended solution:** only credit a rule when it actually fires — e.g. in
  `evaluate_entry`, `total_score = (base_score + Σ matched weights) if matched else 0`;
  and/or apply a single per-disease prior instead of summing per-rule base_scores.
  Then normalize the displayed score to a 0–100 confidence. **Re-validate the
  differential against a few known cases with a nephrologist before/after.**
- **Effort:** 0.5–1 day code; +0.5 day clinical validation.
- **✅ Resolution:** `knowledge/services.py` `evaluate_entry` now credits a rule
  (base prior + matched-condition weights) only when ≥1 condition matches; a
  non-firing rule scores 0. `engine._build_differential` drops zero-score
  diseases and adds a normalized `confidence` (% share of fired-rule weight).
  Verified: differentials are now patient-specific (e.g. `000000`: anti-GBM 39%,
  IgA 26%, ANCA 26%) with no phantom zero-match top hits. **Still needs a
  nephrologist to validate the new ranking on real cases before go-live.**

### G-1 (High) — Clinical governance metadata is unpopulated
- **What (live DB):** 0/618 rules have `approved_by`, `date_validated`, or
  `next_review_date`; `confidence_score = 0.0` for all; `recommendation_id` empty;
  `RecommendationAudit` table empty.
- **Why it matters:** your own governance objective requires every recommendation to
  answer "who reviewed it / when validated / next review / confidence." Structurally
  the schema supports all of this; operationally none is filled in. The system cannot
  yet honestly claim to be "clinically governed."
- **Clinical impact:** no accountable human sign-off on the active rule set; a
  displayed confidence would be false (currently correctly hidden by
  `patient_detail.html:759`).
- **Technical impact:** none — this is curation/data, not code.
- **Recommended solution:** a nephrologist reviews and batch-approves the active set
  (populate `approved_by`, `date_validated`, `next_review_date`); set a real
  `confidence_score` or leave it hidden; wire the override action to write
  `RecommendationAudit`. Provide an admin action for batch approval.
- **Effort:** 1–3 days of clinician curation (can be done via a management command +
  admin action); small dev support.

### M-1 (Medium) — Research eligibility is not automatic ✅ FIXED
- **What:** `studies` is not subscribed to the event bus; `eligibility.py` is a manual
  decorator framework with 2 example studies. Enrollment is manual.
- **Why it matters:** Objective 4 states every patient should be **automatically**
  evaluated for eligibility / missing research variables / cohort assignment.
- **Clinical/research impact:** missed enrollments; registry does not yet function as
  an automatic research recruiter.
- **Recommended solution:** subscribe a `studies` handler to `PATIENT_UPDATED` /
  `CLINICAL_ASSESSMENT_*` that runs registered eligibility checks and flags candidates
  on the patient page.
- **Effort:** 1–2 days.
- **✅ Resolution:** `studies/services/auto_screen.py` + `studies/event_handlers.py`
  now subscribe eligibility screening to `PATIENT_*`, `LAB_RESULT_*`,
  `CLINICAL_ASSESSMENT_*`, and `BIOPSY_CREATED`. On any relevant save a patient is
  re-screened against every recruiting study **that has encoded criteria**;
  eligible patients get a screening `StudyEnrollment` and a green "Eligible" badge
  in the Research tab, and records flip to ineligible (with reasons) if criteria
  stop being met. Clinician decisions are never overwritten. Backfill:
  `python manage.py auto_screen_patients`. Verified end-to-end via the event bus;
  4 new tests. **Only 2 studies currently have encoded criteria — add criteria
  functions for the other recruiting studies to widen automatic screening.**

### M-2 (Medium) — SMS reminders are stubs
- **What:** `reminders/tasks.py:23` `send_sms` only logs `[SMS stub]`.
- **Why it matters:** Objective 3 lists SMS reminders; follow-up continuity partly
  depends on them. (You already label this "planned," so this is expectation-setting.)
- **Recommended solution:** integrate one gateway (local BD SMS provider or Twilio)
  behind the existing stub, or relabel the feature "clinician reminder log" for the
  pilot so it doesn't imply automated messaging.
- **Effort:** 1–2 days for a single gateway.

### M-3 (Medium) — Safety-path tests still lean on mocks
- **What:** unit tests mock the ORM retrieval functions; `tests/test_cds_integration.py`
  now covers the real path for toxicity, but treatment-failure/relapse/eligibility
  integration coverage is thin.
- **Recommended solution:** extend django_db integration tests to the remaining CDS
  services so schema drift can't silently return false negatives again.
- **Effort:** 1 day.

### L-1..L-3 (Low)
- Remove dead `decision` app; retire `TEST-*` rules and fix the "TEST 2026" source;
  consolidate the two follow-up mechanisms. Consider moving reasoning/outcome
  recompute to a background thread if data-entry latency grows.
- **Effort:** 0.5–1 day total.

---

# Final Question

> **Would you approve GDES for a controlled single-center nephrology pilot?**

## **APPROVED WITH MINOR CORRECTIONS**

**Reasoning.**

- **Clinically:** the system is safe for its stated purpose — an *assistive*,
  explainable, overridable decision-support layer on top of a solid registry. The
  previous patient-safety blockers are genuinely fixed and verified end-to-end. The
  medical content is current and guideline-aligned. Nothing acts autonomously.
- **Technically:** it now behaves as one integrated, automated system; 206 tests pass;
  the desktop deployment degrades gracefully without external services.
- **The corrections are "minor" in the sense that none blocks a *safe* pilot**, but two
  should be done before the AI layer is *presented to clinicians as governed and
  quantitative*:
  1. **Fix H-1** (differential scoring) so the ranking and score are clinically
     meaningful and explainable — highest-value single change, ~1 day.
  2. **Complete G-1** (reviewer sign-off + confidence populated-or-hidden) so the
     governance claim is true — mostly clinician curation, not code.
  M-1 (auto research eligibility) and M-2 (SMS) are objective-completeness gaps that
  can follow during the pilot.

If H-1 and G-1 are addressed before go-live, this is a **strong, trustworthy pilot
system**. I would not withhold approval for a supervised pilot in which the clinician
reviews every recommendation — which is exactly the stated AI philosophy.

---

## Recommended pre-pilot checklist
1. Fix H-1 differential scoring; normalize/display confidence; re-validate on 5 real cases.
2. Nephrologist batch-approves the active rule set (G-1); hide or populate confidence.
3. Retire `TEST-*` rules; correct the guideline source shown on differentials.
4. Decide SMS: integrate one gateway or relabel as reminder log.
5. Document "one active machine at a time"; verify backups.
6. (During pilot) wire automatic research eligibility (M-1); extend integration tests (M-3).
