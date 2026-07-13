# GDES_FINAL_PILOT_READINESS_REPORT.md

**System:** GDES
**Reviewer:** Claude Code (independent)
**Date:** 2026-07-12
**Question:** Is GDES ready for a controlled single-center clinical pilot at BIRDEM?

---

## Bottom line

**Not in its current form — but it is close, and the blockers are small and
bounded.** Two viable paths to a safe pilot:

- **Path A (recommended): fix the CDS layer.** Resolve safety blockers
  S-1…S-4 (a handful of field/wiring fixes), add integration tests, populate
  reviewer sign-off on the knowledge base, then pilot the full system.
- **Path B (fallback): registry-only pilot.** Feature-flag the entire AI/CDS
  layer OFF and pilot the registry + prescription workflow, which **is safe and
  usable today**. Add CDS later as a validated increment.

Shipping the CDS layer **as-is** is not acceptable, because it silently
under-reports drug toxicity and relapse and its flagship management plan never
displays.

---

## Readiness scorecard

| Dimension | Ready? | Notes |
|-----------|:------:|-------|
| Single-PC / SQLite deployment | ✅ | `BGDDR_DATA_DIR`, 30 s busy timeout, PostgreSQL-ready. |
| Offline operation | ✅ | No external service required at runtime. |
| Automatic backup | ✅ | 6-hourly, 60 snapshots (`bgddr/backup.py`). |
| Registry data capture | ✅ | Register→assess→lab→biopsy→prescribe→outcome all work. |
| Prescription workflow | ✅ | Draft/final immutability, PDF, reconciliation. |
| Research enrollment | ✅ | Eligibility + randomization present. |
| Audit trail (data) | ✅ | Audit middleware + `AuditLog`. |
| **Drug-toxicity surveillance** | ❌ | **Blocker S-1/S-2** — non-functional / crashes. |
| **Treatment-failure & relapse detection** | ❌ | **Blocker S-3** — 500s on real labs / false negatives. |
| **Management / monitoring / follow-up plans in UI** | ❌ | **Blocker S-4** — never render. |
| CDS auto-trigger | ⚠️ | No routine trigger; only 3/8 patients have a profile (W-2). |
| Knowledge governance sign-off | ⚠️ | 0/618 active rules reviewer-approved / validated (K-2). |
| SMS reminders | ⚠️ | Framework only; no gateway. |

---

## Deployment-specific risks

1. **OneDrive + SQLite concurrency.** Safe for one machine; **will corrupt** if
   the synced `db.sqlite3` is opened on two machines at once. → Enforce a
   documented "one active machine at a time" rule; never run the app on hospital
   and home PCs simultaneously. The two DB files already present
   (`db.sqlite3`, `db-Dr-Wasim.sqlite3`) suggest this risk is real.
2. **No routine CDS trigger (W-2).** Even after S-4 is fixed, CDS panels stay
   blank unless a profile has been generated. → Add a signal to regenerate the
   `ClinicalProfile` on encounter/lab/biopsy save.
3. **Test rules active in production data (K-4).** → Retire `TEST-*` before go
   live so they don't distort the differential.
4. **API surface exposed but unused/broken (A-4).** → Disable the broken CDS
   routes for the pilot if Path B, or fix + wire them if Path A.
5. **"195 tests passing" ≠ safe.** The suite mocks the broken paths (see
   `GDES_FINAL_CODE_QUALITY_REPORT.md`). Do not treat CI-green as clinical
   validation.

---

## Minimum go-live checklist

**If Path A (full system):**
- [ ] Fix S-1 (med + lab retrieval), S-2 (WBC/IgG direction), S-3
      (`value_numeric`), S-4 (disease id source).
- [ ] Add django_db integration tests covering the above.
- [ ] Add automatic `ClinicalProfile` regeneration trigger (W-2).
- [ ] Named clinical reviewer approves active KB rules; set `date_validated`,
      `next_review_date`; set a real `confidence_score` or hide it (K-2).
- [ ] Retire `TEST-*` rules; choose canonical seed.
- [ ] Manual end-to-end dry run on 3–5 real-shaped patients.

**If Path B (registry-only, faster & safe):**
- [ ] Feature-flag CDS/AI endpoints and UI panels OFF.
- [ ] Confirm registry + prescription + outcome + research paths on real data.
- [ ] Document "CDS disabled in this pilot" for users.
- [ ] One-machine-at-a-time operating rule; verify backups.

---

## Recommendation

Proceed on **Path A if the fixes and re-validation can be completed and signed
off before the pilot start date**; otherwise launch on **Path B** now (it is
safe) and fold the CDS layer in as a validated second increment. Either way, the
system should **not** go live with the CDS layer in its current broken state.
