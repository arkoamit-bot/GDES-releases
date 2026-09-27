# Running GDES as a clinic-LAN server on the Windows box (DR-WASIM)

GDES runs beside the DKD registry on the same machine, built the same way
(see `E:\DKDR server\docs\WINDOWS_SERVER.md`), and kept apart from it.

| | DKD registry | GDES |
|---|---|---|
| Clinic address | `http://192.168.7.55/` | **`http://192.168.7.55:8080/`** |
| App server | waitress `127.0.0.1:8000` | `gdes_serve.py` (waitress) `127.0.0.1:8100` |
| Proxy | `caddy.exe` on :80, admin `:2019` | `gdes-caddy.exe` on :8080, admin `:2020` |
| Database | PostgreSQL 16, db/login `dkdr` | same PostgreSQL 16, db/login **`gdes`** |
| Code | `E:\DKDR server` | `E:\GDES server` |
| State | `E:\dkdr-data` | `E:\gdes-data` (`app\` data + logs, `backups\`, `bin\`, `caddy\`) |
| Tasks (SYSTEM) | `DKDR *` | `GDES Server`, `GDES Caddy`, `GDES Watchdog`, `GDES Backup` (02:15) |
| Firewall | TCP 80 from 192.168.7.0/24 | TCP 8080 from 192.168.7.0/24 (Private profile) |

Status: **trial server.** It runs branch
`claude/opus-linkage-histopathology-review-7c2d25`, which has not had clinical
sign-off, on an empty database. No real patient data until that sign-off and
the ethics/data-governance approval DKD's guide describes also cover GDES.

## How the two apps are kept from interfering

- **Cookies.** Browsers share cookies across ports on one host, so GDES uses
  `gdes_sessionid` / `gdes_csrftoken`. With the default names, logging into
  one app would log clinicians out of the other.
- **The DKD watchdog.** When it restarts DKD it kills every process whose
  command line contains `waitress` and every process named `caddy`. GDES runs
  as `python deploy\windows\gdes_serve.py` and `gdes-caddy.exe`, which match
  neither. Keep those names.
- **Caddy admin API.** DKD's Caddy owns `127.0.0.1:2019`; GDES's uses `2020`.
  Two Caddies on the default would leave the second unable to start.
- **The GDES watchdog** only ever stops `gdes_serve.py` and `gdes-caddy`.

## Install (done once) and repair

Everything except the elevated step is prepared already: code in
`E:\GDES server`, a Python 3.11 venv with pinned packages
(`deploy\windows\constraints.txt`).

From an **elevated** PowerShell:

```
powershell -ExecutionPolicy Bypass -File "E:\GDES server\deploy\windows\install.ps1"
```

It generates `DJANGO_SECRET_KEY` and the database password itself (never
printed) into `E:\GDES server\.env` (locked to SYSTEM, Administrators and you),
creates the `gdes` login and database, runs `server_init` (migrate, reference
data, knowledge base, static files), registers the tasks and the firewall rule,
starts everything and checks both addresses answer. Re-running it keeps the
data and secrets and re-registers the tasks.

Then create your account yourself:

```
& "E:\GDES server\deploy\windows\gdes-manage.bat" createsuperuser
```

Always use `gdes-manage.bat` for management commands: plain
`python manage.py` uses the development settings and a different database.

## Day to day

```
# is it up? (ask the port, not the task - a task can say Running while dead)
curl.exe -s -o NUL -w "%{http_code}" http://192.168.7.55:8080/login/
curl.exe -s -o NUL -w "%{http_code}" -H "Host: 192.168.7.55" http://127.0.0.1:8100/login/

# logs (start with the watchdog)
Get-Content E:\gdes-data\app\Logs\watchdog.log -Tail 20
Get-Content E:\gdes-data\app\Logs\server.err -Tail 40
Get-Content E:\gdes-data\app\Logs\caddy.err -Tail 40

# restart (elevated)
Stop-ScheduledTask -TaskName 'GDES Server'; Start-ScheduledTask -TaskName 'GDES Server'

# backup now / rehearse a restore into a scratch database
powershell -File "E:\GDES server\deploy\windows\backup.ps1"
powershell -File "E:\GDES server\deploy\windows\restore.ps1"
```

## Updating the code

```
cd "E:\GDES server"
git pull
.venv\Scripts\python.exe -m pip install -r requirements-server.txt -c deploy\windows\constraints.txt
deploy\windows\gdes-manage.bat server_init
Stop-ScheduledTask -TaskName 'GDES Server'; Start-ScheduledTask -TaskName 'GDES Server'   (elevated)
```

Take a backup first. `server_init` is idempotent.

## When the address changes

Change together, or GDES answers nothing and says nothing about why:
`DJANGO_ALLOWED_HOSTS` and `GDES_CSRF_TRUSTED_ORIGINS` in `.env`; the site
address in `deploy\windows\Caddyfile`; `$LanSubnet` in `install.ps1` (re-run
it); `$AppHost`/`$EdgeUrl` in `watchdog.ps1`.

## Known limits

- PDF prescriptions: WeasyPrint needs GTK, which this machine lacks, so PDFs
  use the xhtml2pdf fallback (no Bengali glyphs; printed wording is English).
  Browser printing is unaffected.
- The weekly MedEx drug-catalogue refresh and the desktop's in-app feedback
  scheduler are started by the desktop launcher only; they do not run here.
- Windows 10 22H2 is out of support (see DKD's guide) - the same risk applies.
- Phase 2 (HTTPS, other centres): replace the site address with a hostname,
  set `GDES_HTTPS=1`, and open 443 - as in DKD's guide.
