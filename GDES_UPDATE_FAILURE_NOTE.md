# GDES Self-Update Failure — Findings & Recommendation

**Date:** 2026-07-18 · **Case:** v7.3.5 → v7.3.6 update "could not be verified or extracted"

## Finding
The self-update pipeline works at **every step except the final file-swap**:
detect ✅ → download ✅ → SHA-256 verify ✅ → extract to staging ✅ (a complete,
valid 7.3.6 build sat in temp) → **swap ❌ never happened**.

**Root cause:** the swap helper — a *hidden, detached PowerShell* that renames
`GDES.exe`/`_internal` — was spawned but **never executed** (no `update.log`, no
`.old` backup, staging left uncleaned). Running that exact swap **manually
succeeded instantly**, so the logic is correct. The automated hidden helper is
being **blocked by antivirus / endpoint protection** (a hidden process renaming
`.exe`s is textbook malware behaviour). A one-off transient GitHub `502` on the
~100 MB download also surfaced the same generic error dialog.

## Actions taken
- The affected PC was **manually updated to 7.3.6** (old build kept as `.old-7.3.5`).
- Hardened the updater (next build): **visible** helper console instead of
  hidden/detached, a **breadcrumb** written to `update.log` before spawn (so a
  block is diagnosable), file-lock **retry**, and **download retry with backoff**.

## Recommendation
1. **Allowlist `%LOCALAPPDATA%\GDES\`** in Defender/EDR on each clinic PC — the
   reliable fix for auto-update.
2. Build/roll out **7.3.7 from the hardened code**; install it once (installer or
   allowlisted auto-update). From 7.3.7 onward, auto-updates use the visible
   helper and should apply reliably.
3. Keep the **installer (`Setup_GDES_*.exe`) as the fallback** for locked-down
   machines where AV cannot be changed.
4. Name release assets consistently **`GDES-<ver>.zip`**.

**Bottom line:** not a build/download defect — an AV-blocked swap. Allowlist the
app folder and ship the hardened build; the installer remains the guaranteed path.
