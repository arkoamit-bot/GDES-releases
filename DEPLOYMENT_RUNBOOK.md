# GDES / BGDDR — Desktop Deployment Runbook (Clinical Pilot)

Single-PC, single-user Windows pilot. Django + SQLite + Waitress, packaged with
PyInstaller (**onedir**) and installed per-user via Inno Setup. This runbook is
the operational companion to the P0–P2 hardening work.

> **Golden safety rule.** The live `db.sqlite3` (+ its `-wal`/`-shm` sidecars)
> must live on **local disk**, never in a cloud-synced folder. The launcher
> refuses to start against a synced DB path (override only with
> `BGDDR_ALLOW_SYNCED_DB=1`, dev-only). Only the **ZIP backups** may sync.

---

## 1. Where things live (packaged install)

| Item | Location |
|---|---|
| Application | `%LOCALAPPDATA%\GDES\` (`BGDDR.exe` + `_internal\`) |
| Live database | `%LOCALAPPDATA%\GDES\Data\db.sqlite3` (local, non-synced) |
| Logs | `…\GDES\Data\Logs\` → `application.log`, `startup.log`, `backup.log`, `migration.log` |
| Backups (tiered ZIP) | `…\GDES\Data\Backups\{Daily,Weekly,Monthly}\` (may be redirected to OneDrive) |
| Exports / Imports / Temp / Media | `…\GDES\Data\{Exports,Imports,Temp,Media}\` |
| KB version stamp | `…\GDES\Data\.kb_version` |

The data directory defaults to `%LOCALAPPDATA%\GDES\Data`. Override with
`BGDDR_DATA_DIR`. Backups/Media can be pointed at OneDrive via the first-run
folder wizard or `BGDDR_BACKUP_DIR` / `BGDDR_MEDIA_DIR`.

---

## 2. Build (on the Windows build box)

```powershell
# from the repo root (bgddr\)
python -m pytest -q                      # must be green
.\desktop\build_exe.ps1                  # onedir build -> dist\BGDDR\, self-check certified
```
`build_exe.ps1` runs PyInstaller against `desktop\BGDDR.spec` (onedir), runs the
packaged `--check` self-test, and writes `version.json` + `RELEASE_REPORT.md`.
**Do not** ship the onefile build (`BGDDR_onefile.spec`) — it is marked non-pilot.

### Make the installer
1. Place `MicrosoftEdgeWebview2Setup.exe` (Evergreen bootstrapper, download from
   Microsoft) in `desktop\installer\`.
2. Build with Inno Setup:
   ```powershell
   iscc desktop\installer\GDES.iss           # -> dist\installer\Setup_GDES_<version>.exe
   ```

---

## 3. Code signing / SmartScreen (P2-3)

Unsigned PyInstaller exes trip Windows SmartScreen and some hospital AV.

- **Preferred:** sign `BGDDR.exe` **and** `Setup_GDES_*.exe` with an OV or EV
  Authenticode certificate (`signtool sign /fd sha256 /tr <timestamp-url> …`).
  An EV cert clears SmartScreen reputation immediately.
- **Interim (unsigned):** on first launch choose **More info → Run anyway**, and
  ask hospital IT to allowlist `%LOCALAPPDATA%\GDES\` in the AV/EDR product.

---

## 4. Install on the clinic PC (per-user, no admin)

1. Copy `Setup_GDES_<version>.exe` to the PC and run it (no admin prompt).
2. It installs to `%LOCALAPPDATA%\GDES\`, creates Desktop + Start-Menu shortcuts,
   and installs the WebView2 runtime **only if missing**.
3. Launch. First run: choose Backup/Media folders (OneDrive recommended for
   backups), then create the administrator account.

---

## 5. First-run behaviour (what the launcher does)

1. Resolve a **local** data dir; **abort** if it is cloud-synced (P0-1).
2. **Single-instance** guard: a 2nd launch opens the browser and exits (P0-4).
3. Ensure a display surface; WebView2 optional (app uses the default browser) (P0-3).
4. **Safe migrate** (P0-2): snapshot → `integrity_check` → migrate → **rollback on
   failure**, logged to `migration.log`.
5. **Version-gated seeding** (P1-2): seeds the KB only on first run or a KB
   version bump; idempotent; never clobbers edited rules on same-version launches.
6. **Startup health summary** (P1-3) to `startup.log`; launch is **blocked only**
   on critical failure (no active KB rules / DB unreadable).
7. Startup **tiered ZIP backup** (P1-1), then every 6 h.

---

## 6. Backups & restore

- Tiered ZIPs accumulate under `Data\Backups\{Daily,Weekly,Monthly}\`
  (retention 7 / 8 / 12). Each is a WAL-safe, integrity-checked snapshot.
- **Restore** (from the app folder, a command window in `%LOCALAPPDATA%\GDES`):
  ```
  BGDDR.exe  (is a GUI app; for maintenance use the bundled python:)
  # onedir builds expose manage.py behaviour via the launcher only; on the DEV
  # box the equivalent is:
  python manage.py restore_backup --list
  python manage.py restore_backup "….\Backups\Daily\bgddr_<ts>_scheduled.zip"
  ```
  Restore takes a defensive backup of the current DB, verifies the archive's
  `integrity_check`, then swaps it in. A corrupt archive never overwrites the DB.
- For a clinician-friendly restore, use the admin **Backup & Restore console**
  (spliced into `/admin/` by `bgddr/admin_backup.py`).

---

## 7. Applying an update

1. Rebuild + re-sign; produce a new `Setup_GDES_<newversion>.exe`.
2. Run it on the clinic PC. Inno Setup upgrades the app files **in place** and
   **leaves `Data\` untouched**.
3. On next launch, safe-migrate runs (snapshot + rollback protection), and KB
   seeding re-runs **only if** `PACKAGED_KB_VERSION` was bumped.

---

## 8. Pre-pilot verification checklist (gate the build on ALL green)

Automated (dev box):
```
python manage.py check
python manage.py test           # or: python -m pytest -q
python manage.py makemigrations --check --dry-run     # no missing migrations
grep -rn "numeric_value" clinical_reasoning/           # -> empty (regression guard)
grep -n "OneDrive" bgddr/settings.py                   # -> warning comments only
python -m pytest tests/test_desktop_hardening.py tests/test_desktop_backup.py tests/test_kb_version.py -q
```

Manual (Windows build box / clean VM):
- [ ] Single installer produces a working app (no Python/pip, no admin).
- [ ] Live DB resolves to a LOCAL path; launcher refuses a synced DB path.
- [ ] WebView2 present or auto-installed; browser fallback works.
- [ ] Two double-clicks → one server (single-instance guard).
- [ ] First run: safe-migrate + idempotent seed + startup ZIP backup + health summary in `startup.log`.
- [ ] Simulated bad migration rolls back to the pre-migration snapshot (see below).
- [ ] Tiered ZIP backups appear (Daily/Weekly/Monthly); `restore_backup` round-trips.
- [ ] All four rotating logs are written.

**Simulating a bad migration (rollback proof):** on the dev box, add a throwaway
migration that raises in its `RunPython`, run the launcher's `initialise` path (or
`desktop.safe_migrate.run_safe_migrate`), and confirm the DB is restored from the
`premigration_*.sqlite3` snapshot and `migration.log` records it. (Automated
equivalent: `tests/test_desktop_hardening.py::test_safe_migrate_rolls_back_on_failure`.)

---

## 9. Troubleshooting

| Symptom | Action |
|---|---|
| "Unsafe data location" dialog on start | DB path is cloud-synced. Move `Data\` to local disk / set `BGDDR_DATA_DIR`. |
| Second launch does nothing | Single-instance guard; the first window is already running. |
| Blank browser page | Check `startup.log`; ensure Waitress bound `127.0.0.1:8000`. |
| "Startup blocked — critical KB problem" | No active rules / DB unreadable — restore a recent backup. |
| SmartScreen warning | Sign the binaries (§3) or More info → Run anyway. |

---

## 10. Final verification results (July 2026)

```
python manage.py check                              → System check identified no issues (0 silenced)
python manage.py test                                → 245 passed in 19.56s
python manage.py makemigrations --check --dry-run     → No changes detected
grep "numeric_value" clinical_reasoning/              → (none — regression guard clean)
grep "OneDrive" bgddr/settings.py                     → warning comments only (lines 36,42,187)
Hardening + backup + KB version tests                 → 31 passed (18+4+9)
Tiered backup create on real DB                       → Daily/Weekly/Monthly ZIPs verified
restore_backup --list                                 → lists tiered archives
```

**Automated checklist: ALL GREEN.** P0/P1/P2 acceptance verified.
Manual items below require a clean Windows VM.

## 11. Out of scope for this pilot
GitHub auto-update as the primary channel, PostgreSQL/server, multi-user,
SMS/email gateways, cloud AI, multi-center. Defer until after a successful
single-clinic pilot.
