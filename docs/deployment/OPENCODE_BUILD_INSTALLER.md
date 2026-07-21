# OPENCODE_BUILD_INSTALLER.md
# Build the GDES / BGDDR Windows Installer (`Setup_GDES_7.3.0.exe`)

**Run this in OpenCode on the Windows build PC, from the repo root (`bgddr\`).**
Goal: produce a single per-user installer at
`dist\installer\Setup_GDES_7.3.0.exe`.

This is a **build/packaging runbook**, not a code-change task. All the source,
the PyInstaller spec, and the Inno Setup script already exist. Do not modify app
code. Execute the steps in order; each step has a **verify** gate — if a gate
fails, stop and report rather than continuing.

---

## 0. Hard requirements (read first)

- **Must run on Windows 10/11.** A Windows `.exe` installer cannot be produced on
  Linux/macOS. If the current shell is not Windows, stop and say so.
- **Do not** switch build tooling. Use the existing PyInstaller **onedir** spec
  (`desktop\BGDDR.spec`) and the existing Inno Setup script
  (`desktop\installer\GDES.iss`).
- **Do not** put the DB or any patient data in the build. The installer ships the
  app only; data is created at first launch under `%LOCALAPPDATA%\GDES\Data`.
- Version for this build: **7.3.0** (the `.iss` still defaults to 6.5.0, so the
  version is overridden at compile time in Step 4 — do not edit the `.iss` just
  for the number).

Key paths this runbook uses:

| What | Path |
|---|---|
| App build script | `desktop\build_exe.ps1` |
| PyInstaller spec (onedir) | `desktop\BGDDR.spec` |
| Onedir build output | `dist\BGDDR\BGDDR.exe` (+ `_internal\`) |
| Inno Setup script | `desktop\installer\GDES.iss` |
| WebView2 bootstrapper (must be added) | `desktop\installer\MicrosoftEdgeWebview2Setup.exe` |
| Final installer output | `dist\installer\Setup_GDES_7.3.0.exe` |

---

## 1. Verify prerequisites

Run these checks. Install anything missing, then re-check.

```powershell
python --version                      # 3.11–3.13 expected
python -m pip --version
# Inno Setup compiler on PATH:
iscc /?                               # if "not recognized", install Inno Setup 6
```

- **Inno Setup 6** (provides `iscc.exe`): install from https://jrsoftware.org/isdl.php
  (per-user is fine). If `iscc` isn't on PATH, use its full path, typically
  `"$Env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"` or
  `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"`.
- **PyInstaller / waitress / whitenoise / openpyxl** — `build_exe.ps1` installs
  these automatically; no action needed.

**Verify gate:** `python --version` and `iscc /?` both succeed.

---

## 2. Pre-build quality gate (must be green)

Do not package a failing build.

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run     # no missing migrations
python manage.py test                                 # full suite must pass
```

**Verify gate:** all three succeed. If `test` fails, STOP and report — the
installer build is blocked.

---

## 3. Vendor the WebView2 Evergreen bootstrapper

The installer bundles this so clean hospital PCs get the runtime. It is not yet
in the repo.

```powershell
$dest = "desktop\installer\MicrosoftEdgeWebview2Setup.exe"
Invoke-WebRequest -Uri "https://go.microsoft.com/fwlink/p/?LinkId=2124703" `
  -OutFile $dest
```

- `LinkId=2124703` is Microsoft's official permanent link to the Evergreen
  **Bootstrapper** (tiny, per-user, no admin).
- If the download is blocked by hospital网络/proxy, obtain the same file manually
  from Microsoft's "Download the WebView2 Runtime" page (Evergreen Bootstrapper)
  and place it at the path above.

**Verify gate:**
```powershell
Test-Path desktop\installer\MicrosoftEdgeWebview2Setup.exe   # -> True
```
(The `.iss` uses `skipifsourcedoesntexist`, so a missing file won't fail the
compile — but then clean machines won't get WebView2. Treat a missing bootstrapper
as a build failure for the pilot.)

---

## 4. Build the app, then compile the installer

### 4a. Build the onedir app (PyInstaller + self-check)

```powershell
.\desktop\build_exe.ps1
```

This cleans previous output, runs PyInstaller against `desktop\BGDDR.spec`, creates
runtime dirs, and runs the packaged self-check (`BGDDR.exe --check`).

**Verify gate:**
```powershell
Test-Path dist\BGDDR\BGDDR.exe        # -> True
```
The script prints the self-check log; confirm it ends without an error and the
knowledge/health summary looks complete. If the self-check exit code is non-zero,
STOP and report.

### 4b. Compile the installer with the 7.3.0 version

```powershell
# Use full path to ISCC if `iscc` isn't on PATH.
iscc /DAppVersion=7.3.0 desktop\installer\GDES.iss
```

`/DAppVersion=7.3.0` overrides the `.iss` default, so the output is named
`Setup_GDES_7.3.0.exe` and the installer reports version 7.3.0.

**Verify gate:**
```powershell
Test-Path dist\installer\Setup_GDES_7.3.0.exe                 # -> True
(Get-Item dist\installer\Setup_GDES_7.3.0.exe).Length/1MB     # sane size (tens–hundreds of MB)
```

---

## 5. Smoke-test the installer (build box or clean VM)

Prefer a **clean Windows VM** with no Python and no dev tools — that is the real
pilot target.

1. Double-click `Setup_GDES_7.3.0.exe`. It must install **without an admin
   prompt** into `%LOCALAPPDATA%\GDES`.
2. It creates Desktop + Start Menu shortcuts and (if WebView2 was absent) installs
   the runtime silently.
3. Launch **GDES Registry**. On first run it should: pick/confirm a **local**
   data folder, run migrations, seed the KB, take a startup backup, show the
   health summary, and open the app window (WebView2) — no console window.
4. Confirm the live DB is at a **local** path (e.g. `%LOCALAPPDATA%\GDES\Data\`),
   **not** in OneDrive. Confirm `Data\Logs\` has `startup.log`, `application.log`,
   `backup.log`, `migration.log`.
5. Register a test patient, confirm decision support / management plan render,
   then confirm a backup ZIP appears in the configured backup folder.
6. Re-run the installer over the existing install (upgrade path): the existing
   `Data\` DB must be **preserved** and untouched.

**Verify gate:** all six pass. Note any SmartScreen prompt — if the exe is
unsigned, Windows will show "More info → Run anyway" (see runbook §P2-3 / signing).

---

## 6. Deliverable

Hand off **`dist\installer\Setup_GDES_7.3.0.exe`** — a single file the clinic runs
with no Python, no pip, no admin rights.

Record in `DEPLOYMENT_RUNBOOK.md`: the build date, the Python/Inno Setup versions
used, the WebView2 bootstrapper version, the self-check result, and the smoke-test
checklist outcome.

---

## Troubleshooting

- **`iscc` not recognized** → use the full path to `ISCC.exe`, or install Inno
  Setup 6.
- **PyInstaller build fails on a missing module/data file** → it's a
  `hiddenimports`/`datas` gap in `desktop\BGDDR.spec`; add the missing entry there
  and rebuild (do not hand-copy files into `dist\`).
- **App launches but window is blank** → WebView2 runtime missing; confirm Step 3
  bundled the bootstrapper and that the installer's `[Run]` step executed. The
  launcher's browser fallback (P0-3) should still open `http://127.0.0.1:<port>/`.
- **"database is locked" / corruption on first run** → verify the resolved DB path
  is local, not OneDrive; the P0-1 guard should refuse a synced path unless
  `BGDDR_ALLOW_SYNCED_DB=1` is set. Never point the live DB at a synced folder.
- **SmartScreen / antivirus blocks the exe** → unsigned build; sign the launcher
  and installer with an OV/EV cert (preferred), or have IT allowlist
  `%LOCALAPPDATA%\GDES\` for the pilot.

---

## Out of scope

Do not add auto-update, a custom updater, PostgreSQL, or multi-user support in this
build. This runbook produces the single-PC pilot installer only.
