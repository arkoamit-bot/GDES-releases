# =====================================================================
#  Publish a GDES update to GitHub Releases (the self-update channel).
#
#  Clinic PCs check <repo>/releases/latest and download the BGDDR-<ver>.zip
#  asset (see desktop/launcher.py _github_update_available). This script
#  creates the release and uploads that asset.
#
#  Prereqs:
#    1. Build the app + the update zip first:
#         .\desktop\build_exe.ps1
#         # then create dist\update\BGDDR-<ver>.zip (see the runbook / the
#         # zip step used for the OneDrive channel) OR pass -ZipPath.
#    2. A GitHub token with CONTENTS:WRITE on the target repo, via -Token or
#       the GITHUB_TOKEN env var. (Fine-grained, single-repo, is safest.)
#
#  Usage:
#    $env:GITHUB_TOKEN = "ghp_xxx"
#    .\desktop\publish_github_release.ps1 -Repo arkoamit-bot/GDES-releases -ZipPath dist\update\BGDDR-6.6.1.zip
#
#  SECURITY: prefer a PUBLIC "releases-only" repo (e.g. arkoamit-bot/GDES-releases)
#  that holds only the built zips — then clinic PCs need NO token. Point them at
#  it with BGDDR_GITHUB_REPO. Do NOT ship a token that can read your private
#  source repo to clinic machines.
# =====================================================================
param(
    [string] $Repo,
    [string] $ZipPath,
    [string] $Token = $env:GITHUB_TOKEN,
    [string] $Notes = ""
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# --- version from bgddr/version.py ---
$verPy = Get-Content "bgddr\version.py" -Raw
if ($verPy -notmatch '__version__\s*=\s*"([^"]+)"') { throw "Cannot read __version__ from bgddr\version.py" }
$version = $Matches[1]
$tag = "v$version"

if (-not $Repo) {
    $url = (git remote get-url origin 2>$null)
    if ($url -match "github\.com[:/](.+?)(\.git)?$") { $Repo = $Matches[1] }
}
if (-not $Repo)  { throw "No -Repo and no git origin found." }
if (-not $Token) { throw "No token. Set -Token or `$env:GITHUB_TOKEN (needs contents:write on $Repo)." }
if (-not $ZipPath) { $ZipPath = "dist\update\BGDDR-$version.zip" }
if (-not (Test-Path $ZipPath)) { throw "Update zip not found: $ZipPath (build it first)." }
if (-not $Notes) { $Notes = "GDES $version. Automated self-update package." }

$hdr = @{ Authorization = "Bearer $Token"; "User-Agent" = "GDES-Publisher"; Accept = "application/vnd.github+json" }
$api = "https://api.github.com/repos/$Repo"
Write-Host "==> Publishing $tag to $Repo" -ForegroundColor Cyan

# --- create the release (or reuse if the tag already exists) ---
try {
    $rel = Invoke-RestMethod -Uri "$api/releases/tags/$tag" -Headers $hdr -Method Get
    Write-Host "   release $tag already exists (id $($rel.id)); reusing." -ForegroundColor Yellow
} catch {
    $body = @{ tag_name = $tag; name = "GDES $version"; body = $Notes; draft = $false; prerelease = $false } | ConvertTo-Json
    $rel = Invoke-RestMethod -Uri "$api/releases" -Headers $hdr -Method Post -Body $body -ContentType "application/json"
    Write-Host "   created release $tag (id $($rel.id))." -ForegroundColor Green
}

# --- delete an existing asset of the same name, then upload ---
$assetName = Split-Path $ZipPath -Leaf
$existing = $rel.assets | Where-Object { $_.name -eq $assetName }
if ($existing) {
    Invoke-RestMethod -Uri "$api/releases/assets/$($existing.id)" -Headers $hdr -Method Delete | Out-Null
    Write-Host "   removed old asset $assetName." -ForegroundColor Yellow
}
$uploadUrl = "https://uploads.github.com/repos/$Repo/releases/$($rel.id)/assets?name=$assetName"
$uploadHdr = @{ Authorization = "Bearer $Token"; "User-Agent" = "GDES-Publisher" }
Write-Host "==> Uploading $assetName ($([math]::Round((Get-Item $ZipPath).Length/1MB,1)) MB) ..." -ForegroundColor Cyan
$asset = Invoke-RestMethod -Uri $uploadUrl -Headers $uploadHdr -Method Post -InFile $ZipPath -ContentType "application/zip"
Write-Host "   uploaded: $($asset.browser_download_url)" -ForegroundColor Green
Write-Host ""
Write-Host "DONE. Clinic PCs on version < $version will now offer this update on next launch." -ForegroundColor Green
Write-Host "(They must be able to reach $Repo — public repo = no token; private = set BGDDR_GITHUB_TOKEN on each PC.)" -ForegroundColor Green
