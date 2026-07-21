# BGDDR — Single-User Windows Desktop Deployment

This is the deployment guide for running BGDDR as a **single-user Windows
application** with **SQLite**, while keeping the schema fully **PostgreSQL-
compatible** for a future multi-user migration. The application architecture is
unchanged — this only packages and hardens it.

---

## 1. What you get

```
BGDDR/                     <- copy this folder anywhere (e.g. inside OneDrive)
├── BGDDR.exe              <- double-click to start (no command line needed)
├── _internal/            <- bundled Python + Django + app (do not edit)
├── db.sqlite3            <- created on first launch
├── Backups/             <- automatic timestamped database snapshots
├── Exports/             <- CSV / Excel / research datasets land here
├── Media/               <- prescription PDFs and uploads
└── Logs/                <- application log (bgddr.log)
```

All data lives **next to `BGDDR.exe`**, so putting the folder inside OneDrive
syncs the database, backups and exports between hospital and home. No
concurrent access — open it in one place at a time.

---

## 2. Build the package (one-time, on a build machine)

From the project root in PowerShell:

```powershell
.\desktop\build_exe.ps1
```

This installs the build dependencies, rebuilds the CSS (if `npm` is present),
runs PyInstaller against `desktop/BGDDR.spec`, and **self-checks** the result.
Output: **`dist\BGDDR\`** — that whole folder is the deployable package.

> Manual equivalent:
> `pyinstaller desktop\BGDDR.spec --noconfirm`
> then `dist\BGDDR\BGDDR.exe --check` to verify.

### Run from source instead (no build)
Double-click **`Start-BGDDR.bat`** in the project root, or:
```powershell
python desktop\launcher.py
```

---

## 3. First launch

1. Double-click **`BGDDR.exe`**.
2. A one-time **folder wizard** asks where **Backups**, **Media** and (optionally)
   **Updates** should be stored. It pre-fills `…\OneDrive\BGDDR-Backups`,
   `…\OneDrive\BGDDR-Media` and `…\OneDrive\BGDDR-Update` if OneDrive is detected;
   adjust with **Browse…**, or click **Use defaults** to keep backups/media next
   to the app. Leave the Update folder blank to disable in-app updates. Tick the
   copy box to move any existing `Backups/`/`Media/` files into the new locations.
   The choice is saved to `bgddr_paths.json` and not asked again.
3. A one-time dialog asks you to **create the administrator account**.
4. The browser opens at **http://127.0.0.1:8000/**.
5. A small **"BGDDR Registry is running"** window stays open — use **Stop** to
   shut down cleanly (closing it stops the server).

On first launch the app automatically: applies database migrations, seeds
reference data (roles, lab tests, drug list, study portfolio), collects static
files, and takes a startup backup (into the folder chosen in step 2).

---

## 4. Automatic backups

* A snapshot is taken **on every startup** and then **every 6 hours** while
  running (`bgddr_backup_<timestamp>_<reason>.sqlite3` in `Backups/`).
* The newest **60** are kept; older ones are pruned automatically.
* Each file is a complete, self-contained database — OneDrive-safe.

Manual control (from the project root, or a shell in the package folder):

```powershell
python manage.py backup_db                 # make a backup now
python manage.py backup_db --list          # list backups
python manage.py restore_db --list         # list restorable backups
python manage.py restore_db <name> --yes   # restore (auto safety-snapshot first)
```

> Restore overwrites the live database. Stop the app first. A `pre_restore`
> safety snapshot is always taken, so a restore is itself reversible.

---

## 5. Exports (CSV / Excel / SPSS / research-ready)

* **In the app:** Export page → CSV, Excel, or **SPSS (.sav)**. De-identified by
  default; identified export requires the `data_manager` role.
* **Command line** (writes into `Exports/` automatically):

```powershell
python manage.py export_dataset                 # de-identified CSV -> Exports/
python manage.py export_dataset --format xlsx   # Excel (+ data-dictionary sheet)
python manage.py export_dataset --format sav    # SPSS .sav (labels + value labels)
python manage.py export_dataset --identified --format sav   # with identifiers
```

* The **Excel** file carries a second **`data_dictionary`** sheet (the codebook).
* The **SPSS `.sav`** file is fully labelled: each variable has its description as
  the variable label, the correct **measurement level** (scale / ordinal /
  nominal), and **value labels** (0 = No, 1 = Yes) on the 0/1 flag variables —
  so it opens analysis-ready in SPSS with no recoding.

---

## 6. Future migration to PostgreSQL (multi-user)

Nothing in the code needs to change — the database is selected by environment
variables and the schema is ORM-only and PostgreSQL-compatible (no SQLite
features, no raw SQL, `JSONField` → `jsonb`).

```powershell
# 1. Export current data (ORM-native, portable):
python manage.py dumpdata --natural-primary --natural-foreign `
    --exclude contenttypes --exclude auth.permission --indent 2 > bgddr_data.json

# 2. Point at PostgreSQL and install the adapter:
pip install psycopg
$env:DJANGO_DB_ENGINE = "postgres"
$env:POSTGRES_DB = "bgddr"; $env:POSTGRES_USER = "bgddr"
$env:POSTGRES_PASSWORD = "..."; $env:POSTGRES_HOST = "dbhost"

# 3. Build the schema and load the data:
python manage.py migrate
python manage.py loaddata bgddr_data.json
```

For a hospital-network, multi-user deployment use `bgddr/settings_prod.py`
(secure cookies, env-driven `SECRET_KEY`/`ALLOWED_HOSTS`) behind a real WSGI
server, with the same `DJANGO_DB_ENGINE=postgres` configuration.

---

## 7. Environment variables (all optional)

| Variable | Default | Purpose |
|---|---|---|
| `BGDDR_DATA_DIR` | app folder | where db/Exports/Logs live (keep on **local disk**) |
| `BGDDR_BACKUP_DIR` | `<data>/Backups` | backup-snapshot folder — point at OneDrive to sync backups |
| `BGDDR_MEDIA_DIR` | `<data>/Media` | uploads/PDF folder — point at OneDrive to sync media |
| `BGDDR_UPDATE_DIR` | `<OneDrive>/BGDDR-Update` | folder new app versions are published to (in-app update); blank disables updates |
| `BGDDR_PORT` | `8000` | local server port |
| `BGDDR_MAX_BACKUPS` | `60` | backup retention count |
| `BGDDR_BACKUP_INTERVAL_HOURS` | `6` | periodic backup interval |
| `DJANGO_DB_ENGINE` | `sqlite` | set to `postgres` to switch backends |
| `POSTGRES_DB/USER/PASSWORD/HOST/PORT` | — | PostgreSQL connection |

`BGDDR_BACKUP_DIR` / `BGDDR_MEDIA_DIR` are normally set for you by the **first-run
folder wizard** (see §3) and remembered in `bgddr_paths.json` next to the app.
Setting either environment variable explicitly overrides the saved choice.

### Recommended layout (single PC + OneDrive)

Keep the **live application and `db.sqlite3` on local disk** (e.g. `C:\BGDDR\`)
and point **only backups and media at OneDrive**:

```
C:\BGDDR\                         <- app + db.sqlite3 (local disk, fast, safe)
   ├── BGDDR.exe / _internal\
   ├── db.sqlite3  db.sqlite3-wal  db.sqlite3-shm
   ├── Exports\  Logs\
   └── bgddr_paths.json           <- remembers your folder choice
C:\Users\<you>\OneDrive\BGDDR-Backups\   <- BGDDR_BACKUP_DIR (synced snapshots)
C:\Users\<you>\OneDrive\BGDDR-Media\     <- BGDDR_MEDIA_DIR  (synced uploads/PDFs)
C:\Users\<you>\OneDrive\BGDDR-Update\    <- BGDDR_UPDATE_DIR (published new versions)
```

**Why:** OneDrive continuously syncing a *live, actively-written* SQLite file
can corrupt it. Backup snapshots are closed, self-contained files and media are
write-once, so syncing **those** is safe and gives you off-machine copies. (WAL
journal mode is enabled on the local db for extra crash resilience — the
`-wal`/`-shm` sidecar files belong next to `db.sqlite3` on local disk and must
**not** be synced.)

---

## 8. Updating the app (from OneDrive)

New versions are published to the **update folder** (`BGDDR_UPDATE_DIR`, chosen in
the first-run wizard, default `…\OneDrive\BGDDR-Update`). The clinic PC picks
them up automatically.

### On the clinic PC (automatic)

* On each launch — and via the **Check for updates** button in the status window —
  the app compares its version against the update folder's manifest.
* If a newer version is found, a dialog shows the version and release notes and
  asks to install. **Updates are never silent.**
* On **Yes**, the app verifies the package checksum, takes a `pre_update` backup,
  closes, swaps in the new code, and reopens. **`db.sqlite3` and all data are
  left untouched** — only the program files are replaced.
* The previous program files are kept as `BGDDR.exe.old-<version>` /
  `_internal.old-<version>` next to the app, and the update log is
  `Logs\update.log`. A failed swap rolls back automatically.

### Publishing an update (maintainer, periodic)

1. Bump `__version__` in `bgddr/version.py`, then build: `.\desktop\build_exe.ps1`.
2. Zip the resulting `dist\BGDDR` folder as `BGDDR-<version>.zip` (the zip must
   contain `BGDDR.exe` and `_internal\` — either at the top level or inside a
   single wrapping folder).
3. Compute its checksum: `Get-FileHash BGDDR-<version>.zip -Algorithm SHA256`.
4. Copy the zip into the OneDrive update folder and write/overwrite `latest.json`:

   ```json
   {
     "version": "6.6.0",
     "file": "BGDDR-6.6.0.zip",
     "sha256": "<hash from step 3>",
     "notes": "What changed in this release."
   }
   ```

5. When OneDrive finishes syncing to the clinic PC, the next launch offers the update.

> The `sha256` field is strongly recommended — the app refuses a package whose
> checksum does not match. Since this runs code from a shared folder, only a
> trusted maintainer should have write access to the update folder.

---

## 9. Troubleshooting

* **Nothing happens / errors on launch** — see `Logs\bgddr.log`.
* **Port already in use** — set `BGDDR_PORT` to a free port and relaunch.
* **Forgot the admin password** — from a shell in the package folder:
  `python manage.py changepassword <username>` (set `DJANGO_SETTINGS_MODULE=bgddr.settings_desktop`).
* **Restore a backup** — see §4.
* **An update broke something** — close the app; in the app folder delete the new
  `BGDDR.exe` / `_internal`, rename `BGDDR.exe.old-<version>` → `BGDDR.exe` and
  `_internal.old-<version>` → `_internal`, then relaunch. Restore the `pre_update`
  backup (§4) if the database was already migrated. See `Logs\update.log`.
