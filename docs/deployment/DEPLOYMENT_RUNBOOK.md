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

### 2.1 Full manual rebuild — cheat-sheet
Run from the repo root (`bgddr\`) in PowerShell after any code/KB change:
```powershell
# 0. (once) prerequisites on the build box:
#    - Python + deps:   python -m pip install pyinstaller waitress whitenoise openpyxl pyreadstat pandas
#    - Inno Setup 6:    winget install --id JRSoftware.InnoSetup
#    - Windows SDK (for signtool) — already present if Visual Studio/SDK installed

# 1. (optional) bump the version for a published update:
#    edit bgddr\version.py           -> __version__ = "6.6.0"
#    edit desktop\installer\GDES.iss -> #define AppVersion "6.6.0"

# 2. Gate on tests
python -m pytest -q

# 3. Build the app (onedir) + self-check certification
.\desktop\build_exe.ps1
#    …or directly (skips the self-check/report):
#    python -m PyInstaller desktop\BGDDR.spec --noconfirm --distpath dist --workpath build

# 4. (optional) sign the app exe FIRST (so the installer embeds a signed exe)
.\desktop\sign_build.ps1 -Files dist\BGDDR\BGDDR.exe -Thumbprint <CERT_THUMBPRINT>

# 5. Build the installer
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" desktop\installer\GDES.iss
#    -> dist\installer\Setup_GDES_<version>.exe

# 6. (optional) sign the installer
.\desktop\sign_build.ps1 -Files dist\installer\Setup_GDES_<version>.exe -Thumbprint <CERT_THUMBPRINT>
```
Notes:
- **Order matters for signing:** sign `BGDDR.exe` (step 4) *before* building the
  installer (step 5), then sign the installer (step 6).
- The current **pilot self-signed** cert thumbprint is
  `72B2EA2AD59EECA18B219A7FC36D0D19BE65F576` (in `Cert:\CurrentUser\My`). For a
  real release use your OV/EV cert thumbprint instead.
- Only `BGDDR.spec` (onedir) is for the pilot; do not build `BGDDR_onefile.spec`.
- After bumping the KB (`knowledge/kb_version.py PACKAGED_KB_VERSION`), existing
  installs re-seed the new knowledge automatically at next launch (P1-2).

---

## 3. Code signing / SmartScreen (P2-3)

Unsigned exes trip Windows SmartScreen and some hospital AV. Sign **`BGDDR.exe`
first**, rebuild the installer, then sign the installer (`desktop\sign_build.ps1`).

### 3a. Production (wide distribution) — buy a real certificate
Use an **OV** or **EV** Authenticode cert (EV clears SmartScreen reputation
immediately). Import it (or plug in the EV token), then:
```powershell
.\desktop\build_exe.ps1
.\desktop\sign_build.ps1 -Files dist\BGDDR\BGDDR.exe -Thumbprint <YOUR_CERT_TP>
iscc desktop\installer\GDES.iss
.\desktop\sign_build.ps1 -Files dist\installer\Setup_GDES_6.5.0.exe -Thumbprint <YOUR_CERT_TP>
```
(Or `-PfxPath cert.pfx -PfxPassword ****`.) Both files are SHA-256 signed and
RFC-3161 timestamped, so they stay valid after the cert expires.

### 3b. Pilot (single clinic PC) — self-signed cert, trusted on that PC
A self-signed cert is fine for one known machine: sign with it, then import the
public cert into that PC's trust stores so Windows shows a consistent publisher
and no "unknown publisher" warning.

Already produced in this repo:
- `desktop\installer\GDES_Pilot_CodeSign.cer` — the **public** cert (safe to share).
- The private key stays in the signer's `Cert:\CurrentUser\My` (never exported/committed).

On the **clinic PC**, import the public cert once:
```powershell
# Per-user (no admin): trusts it for the logged-in clinician.
Import-Certificate -FilePath GDES_Pilot_CodeSign.cer -CertStoreLocation Cert:\CurrentUser\Root
Import-Certificate -FilePath GDES_Pilot_CodeSign.cer -CertStoreLocation Cert:\CurrentUser\TrustedPublisher
# Per-machine (needs admin, trusts all users):
#   Import-Certificate -FilePath GDES_Pilot_CodeSign.cer -CertStoreLocation Cert:\LocalMachine\Root
#   Import-Certificate -FilePath GDES_Pilot_CodeSign.cer -CertStoreLocation Cert:\LocalMachine\TrustedPublisher
```
A self-signed cert does **not** raise SmartScreen reputation on the open
internet — it only removes the warning on machines that trust it. For anything
beyond the single pilot PC, use 3a.

### 3c. Interim (do nothing)
On first launch choose **More info → Run anyway**, and ask hospital IT to
allowlist `%LOCALAPPDATA%\GDES\` in the AV/EDR product.

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

Two channels — both swap only `BGDDR.exe` + `_internal\` (the app folder) and
leave `Data\` (db + backups) untouched; the previous code is kept as `*.old-<ver>`
for rollback. The updater is always **prompted**, never silent.

### 7a. Installer (manual)
1. Rebuild + re-sign; produce a new `Setup_GDES_<newversion>.exe`.
2. Run it on the clinic PC. Inno Setup upgrades in place, leaves `Data\` untouched.
3. On next launch, safe-migrate runs and KB seeding re-runs only if
   `PACKAGED_KB_VERSION` was bumped.

### 7b. GitHub Releases (self-update over the internet — recommended for many PCs)
The app checks `<repo>/releases/latest` on launch (and via "Check for updates"),
downloads the `BGDDR-<ver>.zip` asset, verifies its digest, and swaps the code.
Repo comes from `BGDDR_GITHUB_REPO` (default `arkoamit-bot/GDES`).

**Publish a release (maintainer, once per version):**
```powershell
.\desktop\build_exe.ps1                     # build + sign the app
# create the update zip (BGDDR.exe + _internal at the zip root):
#   the same dist\update\BGDDR-<ver>.zip used for the OneDrive channel
$env:GITHUB_TOKEN = "<token with contents:write on the releases repo>"
.\desktop\publish_github_release.ps1 -Repo <owner/releases-repo> -ZipPath dist\update\BGDDR-<ver>.zip
```
GitHub computes the asset SHA-256 digest automatically; the app verifies it.

**⚠️ Public vs private — security decision:**
- **Recommended:** a **PUBLIC "releases-only" repo** (e.g. `arkoamit-bot/GDES-releases`)
  holding just the built zips (no source). Clinic PCs need **no token**; point them
  at it with `BGDDR_GITHUB_REPO`. Your private source repo stays private.
- **Private repo:** works, but each clinic PC needs `BGDDR_GITHUB_TOKEN` (a
  fine-grained, single-repo, **read-only** token). Shipping a token that can read
  your private *source* repo to clinic machines is a leakage risk — use the
  public releases-repo instead.

Note: the currently-configured repo `arkoamit-bot/GDES` is **private and has no
releases yet**, so self-update is inactive until you publish one (and decide
public-releases-repo vs private+token).

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
