# GDES backup: database dump + uploaded files. Daily 02:15 ("GDES Backup").
#
# Adapted from the DKD registry's backup.ps1 and its three rules:
#   1. An error reading storage is a FAILURE, never an empty backup.
#   2. Nothing is published until complete (.partial names, then move).
#   3. A manifest written last is the only proof a backup happened.
#
# Copy E:\gdes-data\backups to a second physical device. A sync folder
# propagates a deletion as faithfully as a file.
#
# PURE ASCII on purpose (PowerShell 5.1 reads BOM-less UTF-8 as ANSI).

$ErrorActionPreference = 'Stop'
$Stamp  = Get-Date -Format 'yyyy-MM-dd'
$Root   = 'E:\GDES server'
$Dest   = 'E:\gdes-data\backups'
$Media  = 'E:\gdes-data\app\Media'
$PgDump = 'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe'

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

function Get-EnvValue($name) {
    $m = Select-String -Path (Join-Path $Root '.env') -Pattern "^$name=(.*)$"
    if (-not $m) { throw "$name missing from .env" }
    return $m.Matches[0].Groups[1].Value.Trim()
}

# From .env, never argv: a password on the command line is visible to every
# account on the machine.
$env:PGPASSWORD = Get-EnvValue 'POSTGRES_PASSWORD'
$env:PGUSER     = Get-EnvValue 'POSTGRES_USER'
$env:PGHOST     = '127.0.0.1'
$env:PGPORT     = '5432'
$Db             = Get-EnvValue 'POSTGRES_DB'

$DumpFinal   = Join-Path $Dest "gdes-$Stamp.dump"
$DumpPartial = "$DumpFinal.partial"
if (Test-Path $DumpPartial) { Remove-Item $DumpPartial -Force }
& $PgDump -Fc -f $DumpPartial $Db
if ($LASTEXITCODE -ne 0) { throw "pg_dump failed with exit code $LASTEXITCODE" }
$env:PGPASSWORD = $null
if (-not (Test-Path $DumpPartial)) { throw "pg_dump wrote no file" }
$DumpSize = (Get-Item $DumpPartial).Length
if ($DumpSize -lt 1024) { throw "pg_dump wrote only $DumpSize bytes - refusing to publish it" }
$DumpHash = (Get-FileHash $DumpPartial -Algorithm SHA256).Hash

if (-not (Test-Path -LiteralPath $Media -PathType Container)) {
    throw "media root $Media is missing - refusing to record a backup that claims there are no files"
}
$MediaFiles   = @(Get-ChildItem -LiteralPath $Media -Recurse -File)
$MediaCount   = $MediaFiles.Count
$MediaArchive = Join-Path $Dest "media-$Stamp.zip"
$MediaPartial = Join-Path $Dest "media-$Stamp.partial.zip"
$MediaHash    = ''
if (Test-Path $MediaPartial) { Remove-Item $MediaPartial -Force }
if ($MediaCount -gt 0) {
    Compress-Archive -Path (Join-Path $Media '*') -DestinationPath $MediaPartial -CompressionLevel Optimal
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Zip = [System.IO.Compression.ZipFile]::OpenRead($MediaPartial)
    try { $Archived = @($Zip.Entries | Where-Object { $_.Name -ne '' }).Count } finally { $Zip.Dispose() }
    if ($Archived -ne $MediaCount) {
        throw "media archive holds $Archived file(s) but $MediaCount were found - refusing to publish it"
    }
    $MediaHash = (Get-FileHash $MediaPartial -Algorithm SHA256).Hash
    Move-Item $MediaPartial $MediaArchive -Force
}

Move-Item $DumpPartial $DumpFinal -Force

$Manifest = Join-Path $Dest "backup-$Stamp.json"
[ordered]@{
    stamp           = $Stamp
    completed_at    = (Get-Date -Format s)
    database        = (Split-Path $DumpFinal -Leaf)
    database_bytes  = $DumpSize
    database_sha256 = $DumpHash
    media_files     = $MediaCount
    media_archive   = $(if ($MediaCount -eq 0) { '' } else { Split-Path $MediaArchive -Leaf })
    media_sha256    = $MediaHash
} | ConvertTo-Json | Out-File -FilePath "$Manifest.partial" -Encoding ascii
Move-Item "$Manifest.partial" $Manifest -Force

# 30 days of history. The trailing wildcard is required: -Include without it
# silently matches nothing (found the hard way on the DKD server).
$Cutoff = (Get-Date).AddDays(-30)
Get-ChildItem (Join-Path $Dest '*') -Include 'gdes-*.dump','media-*.zip','backup-*.json' -File |
    Where-Object { $_.LastWriteTime -lt $Cutoff } | Remove-Item -Force
Get-ChildItem (Join-Path $Dest '*') -Include '*.partial','*.partial.zip' -File |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-1) } | Remove-Item -Force

# One generation of service-log rollover.
Get-ChildItem 'E:\gdes-data\app\Logs' -Filter '*.err' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 20MB } |
    ForEach-Object { Move-Item $_.FullName "$($_.FullName).1" -Force }

Write-Output "$(Get-Date -Format s)  backup ok: gdes-$Stamp.dump ($DumpSize bytes), media $MediaCount file(s)"
