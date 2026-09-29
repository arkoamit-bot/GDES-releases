# Restore a GDES backup. Run once before real patients go on this server, and
# after any change to the backup job: an untested backup is a belief.
#
#   .\restore.ps1                        # newest dump -> gdes_restore_test (safe)
#   .\restore.ps1 -Dump E:\gdes-data\backups\gdes-2026-09-28.dump
#   .\restore.ps1 -Target gdes -Force    # OVERWRITES the live database
#
# The default target is a scratch database, dropped again afterwards unless
# -Keep. Restoring over the live one needs -Force. Stop the "GDES Server" task
# first if you do.
#
# PURE ASCII on purpose (PowerShell 5.1 reads BOM-less UTF-8 as ANSI).

param(
    [string]$Dump,
    [string]$Target = 'gdes_restore_test',
    [switch]$Force,
    [switch]$Keep
)

$ErrorActionPreference = 'Stop'
$Bin  = 'C:\Program Files\PostgreSQL\16\bin'
$Dest = 'E:\gdes-data\backups'

if (-not $Dump) {
    $newest = Get-ChildItem $Dest -Filter 'gdes-*.dump' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $newest) { throw "No dumps in $Dest" }
    $Dump = $newest.FullName
}
if (-not (Test-Path $Dump)) { throw "No such dump: $Dump" }
if ($Target -eq 'gdes' -and -not $Force) { throw "Refusing to restore over the live database without -Force." }
if ($Target -notmatch '^[a-z_][a-z0-9_]*$') { throw "Target must be a plain database name." }

Write-Output "restoring $Dump -> $Target"
$env:PGPASSWORD = (Get-Content 'E:\dkdr-data\postgres-superuser.txt' -Raw).Trim()
$env:PGHOST = '127.0.0.1'
$env:PGPORT = '5432'
try {
    & "$Bin\psql.exe" -q -U postgres -v ON_ERROR_STOP=1 `
        -c "SET client_min_messages = warning;" `
        -c "DROP DATABASE IF EXISTS $Target;" `
        -c "CREATE DATABASE $Target OWNER gdes ENCODING 'UTF8' TEMPLATE template0;"
    if ($LASTEXITCODE -ne 0) { throw "could not recreate $Target" }

    & "$Bin\pg_restore.exe" -U postgres -d $Target --no-owner --role=gdes $Dump
    if ($LASTEXITCODE -ne 0) { throw "pg_restore failed with exit code $LASTEXITCODE" }

    $q = "SELECT 'patients' AS what, count(*) FROM patients_patient UNION ALL SELECT 'encounters', count(*) FROM encounters_clinicalencounter UNION ALL SELECT 'lab_results', count(*) FROM labs_labresult UNION ALL SELECT 'biopsies', count(*) FROM pathology_biopsy UNION ALL SELECT 'prescriptions', count(*) FROM prescriptions_prescription UNION ALL SELECT 'lab_tests', count(*) FROM labs_labtest UNION ALL SELECT 'drugs', count(*) FROM treatments_drugmaster UNION ALL SELECT 'users', count(*) FROM auth_user ORDER BY 1;"
    Write-Output "`n--- restored ($Target) ---"
    & "$Bin\psql.exe" -U postgres -d $Target -c $q
    if ($Target -ne 'gdes') {
        Write-Output "`n--- live (gdes), for comparison ---"
        & "$Bin\psql.exe" -U postgres -d gdes -c $q
    }
    Write-Output "Uploaded files are not in the dump: unpack the matching media-*.zip into E:\gdes-data\app\Media."
}
finally {
    if ($Target -ne 'gdes' -and -not $Keep) {
        & "$Bin\psql.exe" -q -U postgres -c "DROP DATABASE IF EXISTS $Target;" | Out-Null
        Write-Output "scratch database $Target dropped (use -Keep to inspect it)."
    }
    $env:PGPASSWORD = $null
}
