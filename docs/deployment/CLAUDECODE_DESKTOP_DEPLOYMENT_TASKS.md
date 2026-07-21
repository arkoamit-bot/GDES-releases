# CLAUDECODE_DESKTOP_DEPLOYMENT_TASKS.md
# GDES / BGDDR — Desktop Deployment Hardening for Clinical Pilot

**Run this file in Claude Code from the repo root (`bgddr/`).**
It is an execution spec: work the tasks top-to-bottom, verify each with the
stated command, and stop for review if a P0 acceptance check fails.

---

## 0. How to use this file (read first)

- **This is a corrective + hardening pass, not a rebuild.** Most of the desktop
  scaffolding already exists — do NOT recreate it. Extend it.
- **Do not change the framework.** Keep Django + SQLite + Waitress + pywebview
  (WebView2) + PyInstaller. Do NOT introduce Tauri, Electron, Rust, or Nuitka.
- **Never break the test suite or the registry core.** After every task run the
  relevant tests. The current suite passes (≈205 in `tests/` plus per-app tests).
- **Patient-safety rule:** the live SQLite DB and its `-wal`/`-shm` sidecars must
  never live in a cloud-synced (OneDrive) folder. Only ZIP backups sync.
- Work on a branch: `git checkout -b feat/desktop-pilot-hardening`.
- If a task is already fully satisfied, verify it, note "already done," and move on.

### What already exists (confirm before editing — don't duplicate)

| Concern | Where it already lives | State |
|---|---|---|
| Data-dir separation via env | `bgddr/settings.py` (`BGDDR_DATA_DIR`, `BGDDR_DB_PATH`, `BGDDR_BACKUP_DIR`, `BGDDR_MEDIA_DIR`) | present |
| SQLite WAL + 30s busy timeout | `bgddr/settings.py` DATABASES OPTIONS | present |
| Backup module | `bgddr/backup.py`, `BACKUP_CONFIG` in settings (6h interval, 60 snapshots) | present but **`.sqlite3` snapshots, not tiered ZIP** |
| Desktop launcher | `desktop/launcher.py` (migrate + seed on first run, folder picker keeps DB local, startup + periodic backup) | present |
| PyInstaller specs | `desktop/BGDDR.spec` (onedir), `desktop/BGDDR_onefile.spec` | both present |
| Build script | `desktop/build_exe.ps1` | present |
| Batch launchers | `Start-BGDDR.bat`, `start_gdes.bat` | present |

---

## Ground rules for acceptance

- `python manage.py check` must pass after every change.
- `python manage.py test` (or the targeted app) must pass after every change.
- Prefer additive, reversible changes. Keep diffs small and local.
- Windows-only build steps (PyInstaller, Inno Setup, WebView2) can't be executed
  in a non-Windows dev shell — for those, produce the scripts/config and a
  `DEPLOYMENT_RUNBOOK.md`, and mark them "verify on Windows build box."

---

# P0 — Must fix before the pilot build

### P0-1 — Enforce the live DB local; forbid it in OneDrive
**Problem.** `settings.py` still defaults `BGDDR_DB_PATH` under `BGDDR_DATA_DIR`,
and the header comment (around the "Data directory" block) still says the whole
data folder "can sit inside OneDrive and sync cleanly." That contradicts the
deployment rule and is a real corruption risk (WAL/SHM sidecars + cloud sync).

**Do:**
1. In `bgddr/settings.py`, rewrite the data-directory comment block so it states
   plainly: the live `db.sqlite3` (+ `-wal`/`-shm`) must stay on **local disk**;
   only `Backups/` (ZIP) may point at a synced folder.
2. Add a **startup safety check** (in `desktop/launcher.py` before `migrate`, and
   also as a `manage.py check` custom check if practical): if the resolved DB
   path contains a known cloud-sync segment (`OneDrive`, `Dropbox`, `Google Drive`,
   `iCloudDrive`), refuse to start with a clear diagnostic and instructions,
   unless `BGDDR_ALLOW_SYNCED_DB=1` is explicitly set (escape hatch for devs).
3. Default the local data dir to a reliably-writable, no-admin location:
   `%LOCALAPPDATA%\GDES\Data` (fall back to `Documents\BGDDR` if unavailable).
   `C:\BGDDR\` at drive root can require admin — do not hard-require it.

**Acceptance:**
- `grep -n "OneDrive" bgddr/settings.py` shows only the *warning* comment, not a
  default that places the DB there.
- Launcher aborts with a readable message when `BGDDR_DB_PATH` points into an
  `OneDrive` path and `BGDDR_ALLOW_SYNCED_DB` is unset (add a unit test for the
  path-check helper).
- `python manage.py check` and `python manage.py test` pass.

---

### P0-2 — Safe migration-on-update: backup → verify → migrate → rollback
**Problem.** Update day runs migrations against the real patient DB. A bad
migration can corrupt/destroy data. A generic "startup backup" is not enough.

**Do (in `desktop/launcher.py`, first-run and every-launch migrate path):**
1. Before running `migrate`, detect if there are unapplied migrations
   (`migrate --plan` / `showmigrations`). If none, skip the rest.
2. If there are, take a **labeled pre-migration snapshot**
   (`backups/premigration_YYYYMMDD_HHMMSS.sqlite3` + zip) and run
   `PRAGMA integrity_check` on the live DB; abort the migration if the DB is
   already corrupt (tell the user to restore a backup).
3. Run `migrate`. On any exception, **restore the pre-migration snapshot**, log
   to `migration.log`, and show a clear diagnostic dialog — never leave a
   half-migrated DB in place.
4. Write outcome (versions from/to, result) to `migration.log`.

**Acceptance:**
- Simulate a failing migration in a throwaway test DB and confirm the original DB
  is restored byte-for-byte (add an integration test around the helper that wraps
  migrate; it may shell out to a temp copy).
- `migration.log` records a pre-migration snapshot path on every real migration.

---

### P0-3 — WebView2 runtime bootstrap on clean machines
**Problem.** pywebview needs the Edge **WebView2** runtime. A locked-down hospital
PC may not have it → blank window on launch. Not currently handled.

**Do:**
1. At launch (`desktop/launcher.py`), detect WebView2 (registry key
   `HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}`
   / `HKCU` equivalent, or the pywebview runtime probe).
2. If missing: run the bundled **Evergreen bootstrapper**
   (`MicrosoftEdgeWebview2Setup.exe`, per-user, no admin) silently, then continue.
   If it can't install, fall back to opening the app in the default browser at
   `http://127.0.0.1:<port>/` and show a one-line notice.
3. Add `MicrosoftEdgeWebview2Setup.exe` to the installer payload and the runbook.

**Acceptance:**
- Launcher has a `ensure_webview2()` step invoked before window creation, with a
  browser fallback path. Document the manual test on a clean VM in the runbook.

---

### P0-4 — Single-instance guard
**Problem.** One PC, but a clinician will double-click the shortcut twice → two
Waitress processes on the same SQLite file (the classic corruption path).

**Do (in `desktop/launcher.py`):**
1. Before starting Waitress, attempt to bind the fixed localhost port (e.g.
   `127.0.0.1:8765`). If already bound, assume an instance is running: focus/raise
   the existing window if feasible, otherwise just exit quietly — do NOT start a
   second server. (A lockfile in the data dir is an acceptable alternative.)

**Acceptance:**
- Launching twice in quick succession results in exactly one server process
  (document the manual test; add a unit test for the port/lock helper).

---

# P1 — Strongly recommended before pilot

### P1-1 — Tiered ZIP backups with integrity check + tested restore
**Problem.** `BACKUP_CONFIG` currently keeps flat 6-hourly `.sqlite3` snapshots.
The deployment plan wants tiered ZIP archives and a real restore path.

**Do:**
1. Extend `bgddr/backup.py` to produce **ZIP** archives and organize into
   `Daily/`, `Weekly/`, `Monthly/` under `BGDDR_BACKUP_DIR` with retention
   7 / 8 / 12. Keep the existing 6-hourly snapshot as the "daily" source or add a
   daily roll-up — your call, but implement the tiers + retention pruning.
2. Before archiving, run `PRAGMA integrity_check`; skip/flag a corrupt source
   rather than rotating a good backup out for a bad one.
3. Add a **one-click restore** command/entrypoint (management command
   `restore_backup <zip>` and/or a launcher menu item) that: stops writes, backs
   up the current DB defensively, extracts, verifies `integrity_check`, swaps in.
4. Only ZIPs go to the synced folder; live DB stays local (ties to P0-1).

**Acceptance:**
- Running the backup produces a valid ZIP in the correct tier; retention prunes
  correctly (add unit tests for the pruning/tiering logic with a fake clock).
- `restore_backup` round-trips: backup → mutate → restore → data matches.

---

### P1-2 — Idempotent, version-gated seeding
**Problem.** On an *update* the installer re-runs against an existing DB. Seeding
must not duplicate rules or clobber a clinician-edited knowledge base.

**Do:**
1. Ensure all first-run seeders (reference data, KB, drug knowledge) are
   **idempotent** (upsert / get_or_create) and gated on a stored **knowledge
   version** stamp. If the packaged KB version ≤ the DB's version, skip.
2. Record the active KB version somewhere queryable and show it in the startup
   health summary (P1-3).

**Acceptance:**
- Running the seed command twice yields identical row counts (add a test:
  seed → count → seed → count equal).
- Editing a rule then re-running seed does not overwrite the edit (unless a real
  version bump intends to).

---

### P1-3 — Startup health summary that blocks only on critical failures
**Do:**
1. At launch, print/log the knowledge health summary (Diseases, Rules, Pathways,
   Cases, Guidelines, KB version, Health Status) to `startup.log` and the splash.
2. **Block launch only on critical failures** (e.g. no active KB rules, DB
   unopenable); **warn and continue** on non-critical mismatches (e.g. a cosmetic
   count difference) so a minor issue never strands the clinic.

**Acceptance:**
- Health summary appears in `startup.log`; a simulated critical failure blocks
  with a diagnostic; a simulated non-critical warning still launches.

---

### P1-4 — Runtime dirs + split, rotated logs
**Do:**
1. Ensure `logs`, `backups`, `exports`, `imports`, `temp` are auto-created under
   the data dir (some already are via settings; confirm `imports`/`temp`).
2. Split logging into `application.log`, `backup.log`, `startup.log`,
   `migration.log` with rotation (`RotatingFileHandler`). Extend the existing
   `LOGGING` dict in `settings.py`.

**Acceptance:**
- All four log files are created and written by their respective subsystems; each
  rotates at a sane size (e.g. 5 MB × 5).

---

# P2 — Packaging & install (produce scripts + runbook; verify on Windows)

### P2-1 — Standardize on `--onedir`; retire onefile for the pilot
Keep `desktop/BGDDR.spec` (onedir) as the pilot build. Mark
`BGDDR_onefile.spec` as non-pilot (faster startup, no temp extraction, friendlier
to AV and WebView2 with onedir). Update `build_exe.ps1` to build onedir only for
the pilot target.

### P2-2 — Inno Setup installer (per-user, no admin)
Create `desktop/installer/GDES.iss` (Inno Setup) that:
- installs app into `%LOCALAPPDATA%\GDES\` (no admin, no Program Files),
- creates Desktop + Start Menu shortcuts to the launcher,
- creates data/logs/backup dirs (or lets the launcher's first-run picker do it),
- bundles `MicrosoftEdgeWebview2Setup.exe` and runs it if WebView2 is absent,
- never shows a console window,
- on upgrade, leaves the existing local DB untouched (migrations handled at launch
  per P0-2).
Output name: `Setup_GDES_7.x.exe`.

### P2-3 — Code signing / SmartScreen note
Unsigned PyInstaller exes trip SmartScreen/AV on hospital PCs. In the runbook,
document: (a) preferred — sign the launcher + installer with an OV/EV cert;
(b) interim — "More info → Run anyway" + ask IT to allowlist `%LOCALAPPDATA%\GDES\`.

### P2-4 — `DEPLOYMENT_RUNBOOK.md`
Write a runbook covering: build steps (Windows), clean-VM install test, WebView2
check, first-run initialization, where the DB/backups live, how to restore, how to
apply an update, and the pre-pilot verification checklist below.

---

# Final build-verification checklist (gate the pilot build on ALL green)

Run and paste results into the runbook:

```
python manage.py check
python manage.py test
python manage.py makemigrations --check --dry-run   # no missing migrations
grep -rn "numeric_value" clinical_reasoning/          # -> empty (regression guard)
grep -n "OneDrive" bgddr/settings.py                  # -> warning comment only
```

Manual on the Windows build box / clean VM:
- [ ] Single installer produces a working app (no Python/pip, no admin).
- [ ] Live DB resolves to a LOCAL path; launcher refuses a synced DB path.
- [ ] WebView2 present or auto-installed; browser fallback works.
- [ ] Two double-clicks → one server (single-instance guard).
- [ ] First run: migrate + idempotent seed + startup backup + health summary.
- [ ] Simulated bad migration rolls back to pre-migration snapshot.
- [ ] Tiered ZIP backups appear in the synced folder; restore round-trips.
- [ ] All four rotating logs written.

---

# Out of scope for this pilot (do NOT build now)

GitHub auto-update, custom online updater, PostgreSQL/server, multi-user,
SMS/email gateways, cloud AI services, multi-center. Defer until after a
successful single-clinic pilot.

---

# Suggested commit sequence

1. `P0-1 enforce local DB + synced-path guard`
2. `P0-2 safe migrate: snapshot/verify/rollback`
3. `P0-3 WebView2 bootstrap + browser fallback`
4. `P0-4 single-instance guard`
5. `P1-1 tiered ZIP backups + tested restore`
6. `P1-2 idempotent version-gated seeding`
7. `P1-3 startup health gating`
8. `P1-4 runtime dirs + rotated logs`
9. `P2 packaging: onedir, Inno Setup, runbook`

Keep each commit self-contained with its tests. Report any P0 acceptance failure
and pause for review rather than working around it.
