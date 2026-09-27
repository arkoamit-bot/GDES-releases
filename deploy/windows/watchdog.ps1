# GDES watchdog. Runs every 5 minutes as SYSTEM ("GDES Watchdog" task).
#
# Asks whether the ports answer HTTP, not whether a process exists: a
# scheduled task running cmd.exe stays "Running" after the server inside it
# has died (the DKD registry learned this on 30 August 2026).
#
# Restarts only GDES processes. It identifies them precisely (gdes_serve.py,
# gdes-caddy.exe) so it can never kill the DKD registry's waitress or caddy
# on the same machine.
#
# PURE ASCII on purpose: PowerShell 5.1 reads BOM-less UTF-8 as ANSI.

$ErrorActionPreference = 'Continue'

$Root = 'E:\GDES server'
$Log  = 'E:\gdes-data\app\Logs\watchdog.log'

$AppUrl  = 'http://127.0.0.1:8100/login/'
$AppHost = '192.168.7.55'
$EdgeUrl = 'http://192.168.7.55:8080/login/'

function Write-Log($msg) {
    $line = "{0}  {1}" -f (Get-Date -Format 's'), $msg
    try { Add-Content -Path $Log -Value $line -Encoding ascii } catch { }
    Write-Output $line
}

. (Join-Path $Root 'deploy\windows\http_probe.ps1')

function Restart-Gdes($task, $why) {
    Write-Log "RESTARTING '$task' - $why"
    try {
        Stop-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        if ($task -eq 'GDES Server') {
            Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
                Where-Object { $_.CommandLine -like '*gdes_serve.py*' } |
                ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        }
        if ($task -eq 'GDES Caddy') {
            Get-Process 'gdes-caddy' -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
        Start-ScheduledTask -TaskName $task
        Start-Sleep -Seconds 10
    } catch {
        Write-Log "RESTART FAILED for '$task': $($_.Exception.Message)"
    }
}

$appProbe = Get-HttpProbeConfirmed -Url $AppUrl -HostHeader $AppHost
$app = $appProbe.Code
if (Test-ProbeDown $appProbe) {
    Restart-Gdes 'GDES Server' "app not answering on 127.0.0.1:8100 ($($appProbe.Reason))"
    $appProbe = Wait-HttpOk -Url $AppUrl -HostHeader $AppHost -ForSeconds 90
    $app = $appProbe.Code
    if (Test-ProbeDown $appProbe) { Write-Log "STILL DOWN after restart: app ($($appProbe.Reason)). Needs a human." }
    else { Write-Log "recovered: app now returns $app" }
}

$edgeProbe = Get-HttpProbeConfirmed -Url $EdgeUrl
$edge = $edgeProbe.Code
if (Test-ProbeDown $edgeProbe) {
    if (-not (Test-ProbeDown $appProbe)) {
        Restart-Gdes 'GDES Caddy' "edge returned $edge ($($edgeProbe.Reason)) while the app returned $app"
        $edgeProbe = Wait-HttpOk -Url $EdgeUrl -ForSeconds 60
        $edge = $edgeProbe.Code
        if (Test-ProbeDown $edgeProbe) { Write-Log "STILL DOWN after restart: edge ($edge, $($edgeProbe.Reason)). Needs a human." }
        else { Write-Log "recovered: edge now returns $edge" }
    }
}
elseif ($edge -eq '421') {
    Write-Log "MISCONFIGURED: edge returns 421 for $EdgeUrl - the Caddyfile site address does not match this machine's address. Restarting will not fix it."
}

# One ok line a day, so silence means the watchdog itself is broken.
$today = Get-Date -Format 'yyyy-MM-dd'
$seen = $false
if (Test-Path $Log) {
    $seen = [bool](Select-String -Path $Log -SimpleMatch -Pattern "$today" -ErrorAction SilentlyContinue |
                   Where-Object { $_.Line -match 'ok  app=' })
}
if (-not $seen) { Write-Log "ok  app=$app edge=$edge" }
