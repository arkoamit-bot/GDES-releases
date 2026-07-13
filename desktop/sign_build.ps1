# =====================================================================
#  Authenticode code-signing for the GDES desktop build.
#
#  Signing order matters: sign BGDDR.exe FIRST, rebuild the installer so it
#  embeds the signed exe, THEN sign the installer.
#
#    1) .\desktop\build_exe.ps1
#    2) .\desktop\sign_build.ps1 -Files dist\BGDDR\BGDDR.exe   -Thumbprint <TP>
#    3) iscc desktop\installer\GDES.iss
#    4) .\desktop\sign_build.ps1 -Files dist\installer\Setup_GDES_6.5.0.exe -Thumbprint <TP>
#
#  Certificate options:
#    -Thumbprint <hex>    use a cert already in Cert:\CurrentUser\My
#                         (real OV/EV cert, or the pilot self-signed one)
#    -PfxPath <file> -PfxPassword <pwd>   sign from a .pfx directly
#
#  For a real EV cert on a hardware token, sign with the token's CSP instead
#  (this script's -Thumbprint path works if the token exposes the key to CNG).
# =====================================================================
param(
    [Parameter(Mandatory = $true)] [string[]] $Files,
    [string] $Thumbprint,
    [string] $PfxPath,
    [string] $PfxPassword,
    [string] $TimestampUrl = "http://timestamp.digicert.com"
)
$ErrorActionPreference = "Stop"

# --- Locate signtool.exe (latest Windows SDK) ------------------------------
$signtool = (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source
if (-not $signtool) {
    $signtool = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName | Select-Object -Last 1 -ExpandProperty FullName
}
if (-not $signtool) { throw "signtool.exe not found. Install the Windows 10/11 SDK." }
Write-Host "signtool: $signtool" -ForegroundColor Cyan

# --- Build the common signtool arguments -----------------------------------
$common = @("/fd", "sha256", "/tr", $TimestampUrl, "/td", "sha256")
if ($Thumbprint) {
    $common += @("/sha1", $Thumbprint)
} elseif ($PfxPath) {
    if (-not (Test-Path $PfxPath)) { throw "PFX not found: $PfxPath" }
    $common += @("/f", $PfxPath)
    if ($PfxPassword) { $common += @("/p", $PfxPassword) }
} else {
    throw "Provide -Thumbprint or -PfxPath."
}

foreach ($file in $Files) {
    if (-not (Test-Path $file)) { throw "File to sign not found: $file" }
    Write-Host "==> Signing $file" -ForegroundColor Cyan
    & $signtool sign @common $file
    if ($LASTEXITCODE -ne 0) { throw "signtool sign failed for $file (exit $LASTEXITCODE)." }
    # Verify via Get-AuthenticodeSignature (avoids signtool's native-stderr quirk
    # under PS 5.1). A self-signed cert reads NotTrusted/UnknownError on a machine
    # that has not imported it yet; a purchased OV/EV cert reads Valid.
    $sig = Get-AuthenticodeSignature $file
    if ($sig.Status -eq 'Valid') {
        Write-Host "  [OK] signed, timestamped, chain Valid on this machine." -ForegroundColor Green
    } else {
        Write-Host ("  [OK] signed + timestamped (Authenticode status on THIS machine: {0})." -f $sig.Status) -ForegroundColor Yellow
        Write-Host "       For the self-signed pilot cert this is expected until" -ForegroundColor Yellow
        Write-Host "       GDES_Pilot_CodeSign.cer is imported into Trusted Root + Trusted Publishers." -ForegroundColor Yellow
    }
}
Write-Host "Done. Verify in Explorer -> file Properties -> Digital Signatures." -ForegroundColor Green
