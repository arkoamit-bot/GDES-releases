# =====================================================================
#  Package dist\GDES into the self-update zip (dist\update\GDES-<ver>.zip)
#  and refresh latest.json for the OneDrive channel.
#
#  WHY THIS SCRIPT EXISTS
#  ----------------------
#  v7.3.11 was published at 195 MB instead of ~106 MB. The build folder had
#  accumulated 1,212 OneDrive "conflict copies" -- files renamed with the
#  device suffix (e.g. python314-Dr-Wasim.dll, GDES-Dr-Wasim.exe) when the
#  same OneDrive folder is written from two machines. Zipping the folder
#  wholesale shipped every one of them: 101 MB of dead weight downloaded by
#  every clinic PC, including a stale duplicate of the app executable.
#
#  This script excludes that pattern and REFUSES to produce a zip that still
#  contains one, so the mistake cannot be repeated silently.
#
#  Usage:
#    .\desktop\make_update_zip.ps1            # version from bgddr\version.py
#    .\desktop\make_update_zip.ps1 -Notes "..."
# =====================================================================
param(
    [string] $Notes = "",
    [string] $DistDir = "dist\GDES"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# --- version from the single source of truth ---
$verPy = Get-Content "bgddr\version.py" -Raw
if ($verPy -notmatch '__version__\s*=\s*"([^"]+)"') { throw "Cannot read __version__ from bgddr\version.py" }
$version = $Matches[1]
Write-Host "==> Packaging GDES $version" -ForegroundColor Cyan

if (-not (Test-Path $DistDir)) { throw "Build output not found: $DistDir (run desktop\build_exe.ps1 first)." }

# --- strip OneDrive conflict copies from the build output ---
$conflicts = Get-ChildItem $DistDir -Recurse -File | Where-Object { $_.Name -like "*-Dr-Wasim*" }
if ($conflicts) {
    $mb = [math]::Round(($conflicts | Measure-Object Length -Sum).Sum / 1MB, 1)
    Write-Host "==> Removing $($conflicts.Count) OneDrive conflict copies ($mb MB)" -ForegroundColor Yellow
    $conflicts | Remove-Item -Force
}

$staging = "dist\update"
New-Item -ItemType Directory -Force $staging | Out-Null
$zipPath = Join-Path $staging "GDES-$version.zip"
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

# The zip root must contain GDES.exe + _internal (the updater swaps those two).
Write-Host "==> Compressing $DistDir ..." -ForegroundColor Cyan
Compress-Archive -Path (Join-Path $DistDir "*") -DestinationPath $zipPath -CompressionLevel Optimal

# --- verify before anyone can publish it ---
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path $zipPath))
try {
    # Compress-Archive writes backslash separators on PS 5.1; normalise so
    # the root checks below work on either.
    $names = $zip.Entries | ForEach-Object { $_.FullName.Replace("\", "/") }
    $bad = $names | Where-Object { $_ -like "*-Dr-Wasim*" }
    if ($bad) { throw "Zip still contains $($bad.Count) OneDrive conflict copies -- aborting." }
    if (-not ($names -contains "GDES.exe")) {
        throw "GDES.exe is not at the zip root -- the updater would not find it."
    }
    if (-not ($names | Where-Object { $_ -like "_internal/*" })) {
        throw "_internal\ is not at the zip root -- the updater would not find it."
    }
    Write-Host "   $($zip.Entries.Count) entries, GDES.exe + _internal at root, no conflict copies." -ForegroundColor Green
} finally { $zip.Dispose() }

$sha = (Get-FileHash $zipPath -Algorithm SHA256).Hash.ToLower()
$sizeMb = [math]::Round((Get-Item $zipPath).Length / 1MB, 1)

if (-not $Notes) { $Notes = "GDES $version." }
@{ version = $version; file = "GDES-$version.zip"; sha256 = $sha; notes = $Notes } |
    ConvertTo-Json | Set-Content (Join-Path $staging "latest.json") -Encoding utf8

Write-Host ""
Write-Host "DONE: $zipPath ($sizeMb MB)" -ForegroundColor Green
Write-Host "  sha256: $sha" -ForegroundColor Green
Write-Host ""
Write-Host "Publish with:" -ForegroundColor Cyan
Write-Host "  `$env:GITHUB_TOKEN = '<token with contents:write>'"
Write-Host "  .\desktop\publish_github_release.ps1 -Repo arkoamit-bot/GDES-releases -ZipPath $zipPath"
