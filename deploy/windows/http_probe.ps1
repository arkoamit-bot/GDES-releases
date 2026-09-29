# Is it down, or is it busy? One answer, used by the watchdog and the deploy.
#
# WHY THIS EXISTS
#
# Both scripts asked curl for %{http_code} and threw the exit code away. curl
# reports 000 for BOTH of these, and they are not the same thing:
#
#     nothing listening      http_code=000   curl_exit=7   (couldn't connect)
#     healthy but too slow   http_code=000   curl_exit=28  (timed out)
#     healthy, fair timeout  http_code=200   curl_exit=0
#
# Measured on this machine, not assumed.
#
# So a service that was merely SLOW read as a service that was DOWN. On
# 16 September 2026 the deploy pulled at 07:35 and then ran 5,435 tests,
# saturating the machine for about nine minutes. The watchdog fired at 07:40
# and again at 07:45 - its ordinary five-minute cadence - found the edge
# check timing out under that load, concluded Caddy was down, and restarted
# a perfectly healthy reverse proxy. Twice. The second restart did not come
# back inside the watchdog's own ten-second grace, so it logged "Needs a
# human", and the deploy's own verification landed in the window it had just
# created and reported a failed deploy that had in fact fully succeeded.
#
# The outage was caused by the thing watching for outages.
#
# THE RULE
#
# A refused connection is evidence. A timeout is not: it means the answer did
# not arrive in the time allowed, which is also what a loaded machine looks
# like. So a timeout is retried, with more patience, before anything is
# restarted - and the log says which of the two it saw, so that "it was down"
# and "it was slow" stop being the same line.
#
# --connect-timeout separately from --max-time is what makes the distinction
# sharp: a TCP connection that is accepted proves something is listening,
# whatever happens to the response afterwards.
#
# PURE ASCII, like every script beside it. PowerShell 5.1 reads a BOM-less
# UTF-8 file as ANSI and silently mangles anything multi-byte.

function Get-HttpProbe {
    <#
      .SYNOPSIS
      One HTTP probe, reported with WHY it failed.

      Returns an object with Code ('200', '000', ...), Exit (curl's) and
      Reason ('ok' | 'refused' | 'timeout' | 'curlNN'). Never throws: a
      watchdog that dies on a failed probe is a watchdog that stops watching.
    #>
    param(
        [Parameter(Mandatory)][string]$Url,
        [string]$HostHeader,
        [int]$TimeoutSeconds = 15,
        [int]$ConnectTimeoutSeconds = 5
    )
    # The connect timeout must expire BEFORE the overall one, or a host that
    # never completes a handshake is reported as a timeout rather than as a
    # refusal - which collapses the distinction this function exists to
    # make, and sends the caller off to retry something that is genuinely
    # down. Found by running it: --max-time 2 with --connect-timeout 5
    # reported a dead port as 'timeout'.
    $connect = [Math]::Min($ConnectTimeoutSeconds, [Math]::Max(1, $TimeoutSeconds - 1))
    $cargs = @('-s', '-o', 'NUL', '-w', '%{http_code}',
               '--connect-timeout', "$connect",
               '--max-time', "$TimeoutSeconds")
    if ($HostHeader) { $cargs += @('-H', "Host: $HostHeader") }
    $cargs += $Url

    $code = ''
    $exit = -1
    try {
        $code = (& curl.exe $cargs | Out-String)
        $exit = $LASTEXITCODE
    } catch {
        $code = ''
        $exit = -1
    }
    # curl's exit code is REPORTED, not left lying around. Without this the
    # caller's $LASTEXITCODE is whatever the last probe returned - so a
    # deploy that succeeded, then probed a not-yet-ready port, would end on
    # curl's 7 and be recorded as a failed run by deploy_task.ps1.
    $global:LASTEXITCODE = 0

    $code = ([string]$code).Trim()
    if ($code -notmatch '^\d{3}$') { $code = '000' }

    $reason = 'curl' + $exit
    if ($exit -eq 0)  { $reason = 'ok' }
    if ($exit -eq 7)  { $reason = 'refused' }
    if ($exit -eq 28) { $reason = 'timeout' }

    return [pscustomobject]@{ Code = $code; Exit = $exit; Reason = $reason }
}

function Test-ProbeDown {
    <#
      .SYNOPSIS
      Whether a probe result means the service is not serving.

      000 (no answer at all) and 502 (the proxy has no healthy upstream) are
      the two that mean "not serving". Every other code - 200, 302, 403, even
      500 - came from something alive, and restarting it would turn a bad
      page into an outage.
    #>
    param([Parameter(Mandatory)]$Probe)
    return ($Probe.Code -eq '000' -or $Probe.Code -eq '502')
}

function Get-HttpProbeConfirmed {
    <#
      .SYNOPSIS
      A probe, and a second opinion when the first one merely timed out.

      A refused connection is taken at face value: nothing is listening.
      A timeout is not, because that is what this machine looks like while
      it runs the test suite. The retry gets twice the patience.
    #>
    param(
        [Parameter(Mandatory)][string]$Url,
        [string]$HostHeader,
        [int]$TimeoutSeconds = 15,
        [int]$PauseSeconds = 10
    )
    $first = Get-HttpProbe -Url $Url -HostHeader $HostHeader -TimeoutSeconds $TimeoutSeconds
    if (-not (Test-ProbeDown $first)) { return $first }
    if ($first.Reason -ne 'timeout') { return $first }

    Start-Sleep -Seconds $PauseSeconds
    $second = Get-HttpProbe -Url $Url -HostHeader $HostHeader `
        -TimeoutSeconds ($TimeoutSeconds * 2)
    return $second
}

function Wait-HttpOk {
    <#
      .SYNOPSIS
      Poll until it serves, or until the patience runs out.

      For use after a restart. A fixed sleep is a guess about how long a
      Django process takes to import 105 modules on a machine that has just
      finished running the test suite; polling is not.
    #>
    param(
        [Parameter(Mandatory)][string]$Url,
        [string]$HostHeader,
        [int]$ForSeconds = 120,
        [int]$EverySeconds = 5
    )
    $deadline = (Get-Date).AddSeconds($ForSeconds)
    $probe = $null
    do {
        $probe = Get-HttpProbe -Url $Url -HostHeader $HostHeader
        if (-not (Test-ProbeDown $probe)) { return $probe }
        Start-Sleep -Seconds $EverySeconds
    } while ((Get-Date) -lt $deadline)
    return $probe
}
