# =====================================================================
#  Build the GDES single-user Windows desktop package (GDES.exe).
#  Run from the project root:   .\desktop\build_exe.ps1
# =====================================================================
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "==> Ensuring build dependencies ..." -ForegroundColor Cyan
# pip writes progress/warnings to stderr; under $ErrorActionPreference='Stop'
# (PowerShell 5.1) that would abort the script even on success. Relax locally.
$prevEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
python -m pip install --quiet pyinstaller waitress whitenoise openpyxl
if ($LASTEXITCODE -ne 0) {
    Write-Warning "pip reported a non-zero exit; continuing (dependencies may already be installed)."
}
$ErrorActionPreference = $prevEAP

Write-Host "==> Rebuilding compiled CSS (if npm is available) ..." -ForegroundColor Cyan
if (Get-Command npm -ErrorAction SilentlyContinue) {
    try { npm run build:css } catch { Write-Host "   (skipped CSS rebuild)" }
}

Write-Host "==> Cleaning previous build ..." -ForegroundColor Cyan
if (Test-Path "$root\build") { Remove-Item "$root\build" -Recurse -Force }
if (Test-Path "$root\dist\GDES") { Remove-Item "$root\dist\GDES" -Recurse -Force }

Write-Host "==> Running PyInstaller ..." -ForegroundColor Cyan
python -m PyInstaller "$root\desktop\BGDDR.spec" --noconfirm --distpath "$root\dist" --workpath "$root\build"

$exe = "$root\dist\GDES\GDES.exe"
if (-not (Test-Path $exe)) {
    Write-Error "Build failed: $exe not found."
    return
}

# ------------------------------------------------------------------ #
#  Post-build: create runtime directories in the distribution         #
# ------------------------------------------------------------------ #
$pkg = "$root\dist\GDES"
Write-Host "==> Creating runtime directories ..." -ForegroundColor Cyan
foreach ($dir in @("backups", "logs", "config", "media")) {
    $full = Join-Path $pkg $dir
    if (-not (Test-Path $full)) { New-Item -ItemType Directory -Path $full | Out-Null }
}

# ------------------------------------------------------------------ #
#  Self-check the packaged build (must pass before we certify it)     #
# ------------------------------------------------------------------ #
Write-Host "==> Self-checking the packaged build ..." -ForegroundColor Cyan
$checkData = Join-Path ([System.IO.Path]::GetTempPath()) ("gdes-selfcheck-data-" + [guid]::NewGuid().ToString("N"))
if (Test-Path $checkData) { Remove-Item $checkData -Recurse -Force }
New-Item -ItemType Directory -Path $checkData | Out-Null
$oldDataDir = $env:BGDDR_DATA_DIR
$selfCheckExit = 1
try {
    $env:BGDDR_DATA_DIR = $checkData
    # GDES.exe is a GUI-subsystem (windowed) binary: the call operator "&" does
    # NOT wait for it and never sets $LASTEXITCODE, so a crashing self-check would
    # slip through unnoticed. Start-Process -Wait -PassThru actually blocks on the
    # process and captures its real exit code.
    $proc = Start-Process -FilePath $exe -ArgumentList "--check" -Wait -PassThru
    $selfCheckExit = $proc.ExitCode
    # P1-4: launcher/boot narrative now goes to startup.log (was bgddr.log).
    foreach ($lf in @("startup.log", "application.log", "bgddr.log")) {
        $scLog = Join-Path $checkData "Logs\$lf"
        if (Test-Path $scLog) { Get-Content $scLog | ForEach-Object { Write-Host "   $_" }; break }
    }
} finally {
    if ($null -eq $oldDataDir) {
        Remove-Item Env:\BGDDR_DATA_DIR -ErrorAction SilentlyContinue
    } else {
        $env:BGDDR_DATA_DIR = $oldDataDir
    }
    if (Test-Path $checkData) { Remove-Item $checkData -Recurse -Force }
}
if ($selfCheckExit -ne 0) {
    Write-Error "Self-check FAILED (exit $selfCheckExit): the packaged app did not start cleanly. Build NOT certified -- see the log output above."
    return
}
Write-Host "  [OK] Self-check passed (exit 0)." -ForegroundColor Green
$selfCheckStatus = "Passed"

# ------------------------------------------------------------------ #
#  Generate version.json                                              #
# ------------------------------------------------------------------ #
Write-Host "==> Generating version.json ..." -ForegroundColor Cyan

# Read version from source
$versionPy = Get-Content "$root\bgddr\version.py" -Raw
if ($versionPy -match '__version__\s*=\s*"([^"]+)"') {
    $appVersion = $Matches[1]
} else {
    $appVersion = "0.0.0"
}

$versionObj = [ordered]@{
    product        = "GDES"
    version        = $appVersion
    build_date     = (Get-Date -Format "yyyy-MM-dd")
    knowledge_version = $appVersion
    active_rules   = 0
    diseases       = 0
    tests          = 0
}

# Try to count knowledge base stats from the seed source files
$seedFile = "$root\knowledge\management\commands\seed_knowledge_base.py"
if (Test-Path $seedFile) {
    $seedContent = Get-Content $seedFile -Raw
    # Count disease keys
    $diseaseMatches = [regex]::Matches($seedContent, '^\s+"(\w+)":\s*\{', 'Multiline')
    $versionObj.diseases = $diseaseMatches.Count
    # Count rules
    $ruleMatches = [regex]::Matches($seedContent, '\(\[', 'Multiline')
    $versionObj.active_rules = $ruleMatches.Count
}

# Count test functions
$testCount = 0
Get-ChildItem -Path "$root" -Recurse -Filter "tests*.py" -Exclude "*.pyc" | ForEach-Object {
    if ($_.FullName -notmatch "\\(dist|build|\.venv|node_modules)\\") {
        $content = Get-Content $_.FullName -Raw
        $defMatches = [regex]::Matches($content, 'def\s+test_\w+')
        $testCount += $defMatches.Count
    }
}
$versionObj.tests = $testCount

$versionJson = $versionObj | ConvertTo-Json -Depth 4
$versionJson | Out-File -FilePath (Join-Path $pkg "version.json") -Encoding utf8
Write-Host "  version.json: v$($appVersion), $($versionObj.diseases) diseases, $($versionObj.active_rules) rules, $($versionObj.tests) tests"

# ------------------------------------------------------------------ #
#  Generate RELEASE_REPORT.md                                         #
# ------------------------------------------------------------------ #
Write-Host "==> Generating RELEASE_REPORT.md ..." -ForegroundColor Cyan

$report = @"
# GDES Release Report

**Product:** GDES (Glomerular Disease Evaluation System)
**Version:** $appVersion
**Build Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm")
**Platform:** Windows (PyInstaller desktop build)

---

## Build Verification

| Check | Status |
|-------|--------|
| Executable | GDES.exe ($([math]::Round((Get-Item $exe).Length / 1MB, 1)) MB) |
| PyInstaller | Completed successfully |
| Self-check | $selfCheckStatus |

## Distribution Contents

| Directory | Status |
|-----------|--------|
| templates/ | $(if (Test-Path "$pkg\templates") {'Included'} else {'MISSING'}) |
| static/ | $(if (Test-Path "$pkg\static") {'Included'} else {'MISSING'}) |
| docs/ | $(if (Test-Path "$pkg\docs") {'Included'} else {'MISSING'}) |
| backups/ | Created (empty) |
| logs/ | Created (empty) |
| config/ | Created (empty) |
| media/ | Created (empty) |

## Knowledge Base

| Metric | Value |
|--------|-------|
| Diseases | $($versionObj.diseases) |
| Clinical rules | $($versionObj.active_rules) |
| Test cases | $($versionObj.tests) |
| Seeding | First-run auto-seed via launcher.py |

## Seed Commands (first run)

1. seed_roles
2. seed_labs
3. seed_drugs
4. seed_studies
5. seed_knowledge_base
6. seed_v4_knowledge
7. seed_clinical_cases
8. seed_drug_knowledge
9. activate_entries

## Deployment Instructions

1. Copy the entire ``dist/GDES/`` folder to the target computer.
2. Double-click ``GDES.exe``.
3. On first launch, the app will:
   - Apply database migrations
   - Seed all reference data and knowledge base
   - Collect static files
   - Prompt for administrator account creation
4. The application is ready to use after the first-launch setup completes.

## Notes

- No manual setup is required.
- The knowledge base is embedded in the Python source and seeded on first run.
- Database (SQLite) is created next to the executable on first launch.
- Backup and media directories default to the application folder.
"@

$report | Out-File -FilePath (Join-Path $pkg "RELEASE_REPORT.md") -Encoding utf8

# ------------------------------------------------------------------ #
#  Generate README-FIRST.txt (plain run instructions for the clinic)  #
# ------------------------------------------------------------------ #
Write-Host "==> Generating README-FIRST.txt ..." -ForegroundColor Cyan
$readme = @"
==============================================================
 GDES Registry  -  How to run this program        (v$appVersion)
==============================================================

1) START
   - Double-click  GDES.exe
   - A small window "GDES Registry is running" appears - KEEP IT OPEN
     while you use the program.
   - Your web browser opens automatically at:
         http://127.0.0.1:8000/
     If it does not, click "Open in browser" in that small window.

2) FIRST TIME ONLY
   - You will be asked WHERE to keep Backups, Media and Updates.
     Recommended: your OneDrive folders, so backups are copied off
     this PC automatically. (Leave "Update folder" blank if you do
     not use in-app updates.)
   - You will be asked to create an ADMINISTRATOR username and
     password. Please set a real password and keep it safe.
     (If you skip it, a default  admin / bgddr-admin  is created -
     change it immediately from inside the program.)

3) EVERY DAY USE
   - Log in in the browser and use the left-hand menu.
   - Help is built in:  left menu -> "Help & Guides"
        * User Guide          (data entry, analysis, export)
        * Administrator Guide  (backups, restore, updates, accounts)

4) STOP
   - Click the "Stop" button in the small window.
   - Just closing the browser tab does NOT stop the program.

5) IMPORTANT
   - Keep THIS folder on the computer's local disk (e.g. C:\BGDDR).
     Do NOT put it inside a OneDrive-synced folder - only the
     Backups / Media / Update folders should be on OneDrive.
   - Do NOT run two copies at the same time.
   - Do NOT edit or delete the "_internal" folder.
   - Your data (db.sqlite3), Exports and Logs are created next to
      GDES.exe. Backups are taken automatically on start and every
     few hours.

6) IF SOMETHING GOES WRONG
   - Look in  Logs\bgddr.log  (in this folder).
   - "Port already in use": close other copies and try again.
   - Full details: DESKTOP_DEPLOYMENT.md (in this folder / docs).
==============================================================
"@
$readme | Out-File -FilePath (Join-Path $pkg "README-FIRST.txt") -Encoding utf8

# ------------------------------------------------------------------ #
#  Runtime validation                                                 #
# ------------------------------------------------------------------ #
Write-Host "==> Validating distribution ..." -ForegroundColor Cyan
$validationFailed = $false
$internal = Join-Path $pkg "_internal"

# Required directories — some live at package root, others inside _internal/
$rootDirs = @("backups", "logs", "config", "media")
foreach ($dir in $rootDirs) {
    $full = Join-Path $pkg $dir
    if (Test-Path $full) {
        Write-Host "  [OK] $dir/" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $dir/ MISSING" -ForegroundColor Red
        $validationFailed = $true
    }
}

$internalDirs = @("templates", "static", "docs")
foreach ($dir in $internalDirs) {
    $full = Join-Path $internal $dir
    if (Test-Path $full) {
        $count = (Get-ChildItem -Path $full -Recurse -File).Count
        Write-Host "  [OK] _internal/$dir/ ($count files)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] _internal/$dir/ MISSING" -ForegroundColor Red
        $validationFailed = $true
    }
}

# Required files
$requiredFiles = @("GDES.exe", "version.json", "RELEASE_REPORT.md", "README-FIRST.txt")
foreach ($file in $requiredFiles) {
    $full = Join-Path $pkg $file
    if (Test-Path $full) {
        $sizeMB = [math]::Round((Get-Item $full).Length / 1KB, 1)
        Write-Host "  [OK] $file (${sizeMB} KB)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $file MISSING" -ForegroundColor Red
        $validationFailed = $true
    }
}

# Check documentation PDF exists (may be in _internal/docs/ or docs/)
$pdfFound = $false
foreach ($docsPath in @("$internal\docs", "$pkg\docs")) {
    if (Test-Path $docsPath) {
        Get-ChildItem -Path $docsPath -Recurse -Filter "*.pdf" -ErrorAction SilentlyContinue | ForEach-Object { $pdfFound = $true }
    }
}
if ($pdfFound) {
    Write-Host "  [OK] Documentation PDFs found" -ForegroundColor Green
} else {
    Write-Host "  [WARN] No PDF documentation found in docs/" -ForegroundColor Yellow
}

if ($validationFailed) {
    Write-Error "Distribution validation FAILED. Check the errors above."
    return
}

Write-Host ""
Write-Host "BUILD COMPLETE (self-check certified) -> $pkg" -ForegroundColor Green
Write-Host "Copy the 'dist\GDES' folder to its final location and run GDES.exe." -ForegroundColor Green
