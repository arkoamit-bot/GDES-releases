"""
BGDDR desktop launcher — single-user Windows build.

Double-clicking BGDDR.exe (or running this file) will:

  1. point the data directory at the application folder (local disk),
  2. on first run, ask where Backups/ and Media/ should live (a folder wizard;
     the live db.sqlite3 stays on local disk, backups/media can go to OneDrive),
  3. apply database migrations and seed reference data on first run,
  4. collect static files,
  5. ensure an administrator account exists (first-run dialog),
  6. take a startup backup and start a periodic backup timer,
  7. serve the app with Waitress on http://127.0.0.1:8000,
  8. open the browser and show a small status window with a Stop button.

No command-line interaction is required for normal use. The same Django code
runs here on SQLite and, later, unchanged on PostgreSQL (set DJANGO_DB_ENGINE).
"""
from __future__ import annotations

import io
import json
import logging
import os
import shutil
import sys
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

HOST = "127.0.0.1"
PORT = int(os.environ.get("BGDDR_PORT", "8000"))
URL = f"http://{HOST}:{PORT}/"

# Holds the single-instance guard socket for the process lifetime (P0-4).
_INSTANCE_LOCK = None


def app_dir() -> Path:
    """Folder that contains the running app (and db.sqlite3, Backups/, ...).

    Frozen (PyInstaller): the directory of the .exe. Source: the project root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _import_hardening():
    """Import the desktop hardening helpers (works both frozen and from source)."""
    try:
        from desktop import hardening  # noqa: PLC0415
        return hardening
    except Exception:
        import hardening  # type: ignore  # noqa: PLC0415
        return hardening


def bootstrap_env() -> Path:
    """Set the env BEFORE importing Django so settings see the right paths.

    Returns the resolved DATA directory (where db.sqlite3, Logs/, markers live).
    Packaged builds default to a local, no-admin, non-synced location
    (%LOCALAPPDATA%\\GDES\\Data); source runs keep the project root so dev is
    unchanged. An explicit BGDDR_DATA_DIR always wins.
    """
    app = app_dir()
    if str(app) not in sys.path:
        sys.path.insert(0, str(app))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings_desktop")

    data_dir = os.environ.get("BGDDR_DATA_DIR")
    if not data_dir:
        if getattr(sys, "frozen", False):
            data_dir = str(_import_hardening().resolve_local_data_dir())
        else:
            data_dir = str(app)
        os.environ["BGDDR_DATA_DIR"] = data_dir
    return Path(data_dir).resolve()


def log(msg: str) -> None:
    """Log safely. In the windowed .exe sys.stdout is None, so guard print and
    always send the message to the file logger (Logs/bgddr.log)."""
    try:
        if sys.stdout is not None:
            sys.stdout.write(f"[BGDDR] {msg}\n")
            sys.stdout.flush()
    except Exception:
        pass
    try:
        logging.getLogger("bgddr").info(msg)
    except Exception:
        pass


# A sink for management-command output: their self.stdout.write() must never
# touch the real (possibly None) stdout in the windowed build.
_SINK = io.StringIO()


# --------------------------------------------------------------------------- #
# Backup / media folder configuration (runs BEFORE Django loads)
# --------------------------------------------------------------------------- #
# The live db.sqlite3 must stay on local disk, but Backups/ and Media/ can point
# at a OneDrive-synced folder. The user chooses those two locations once, on the
# first launch of the packaged app, via a small folder wizard. The choice is
# saved next to the app (bgddr_paths.json) and exported as the BGDDR_BACKUP_DIR /
# BGDDR_MEDIA_DIR env vars, which bgddr/settings.py already honours.
_PATHS_CONFIG_NAME = "bgddr_paths.json"


def _read_paths_config(cfg_path: Path) -> dict | None:
    """Load a previously saved {backup_dir, media_dir} config, or None."""
    try:
        if cfg_path.exists():
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except (OSError, ValueError) as exc:
        log(f"Could not read {cfg_path.name}: {exc}")
    return None


def _write_paths_config(cfg_path: Path, data: dict) -> None:
    """Persist the chosen folders next to the app (local disk)."""
    try:
        cfg_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        log(f"Saved backup/media folder choice to {cfg_path.name}.")
    except OSError as exc:
        log(f"Could not write {cfg_path.name}: {exc}")


def _default_folder_suggestions(root: Path) -> tuple[str, str, str]:
    """Suggest OneDrive\\GDES-Backups / -Media / -Update if OneDrive is present,
    else app-folder defaults for backup/media and a blank update folder."""
    onedrive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer") \
        or os.environ.get("OneDriveCommercial") or ""
    if onedrive and Path(onedrive).is_dir():
        base = Path(onedrive)
        return (str(base / "GDES-Backups"), str(base / "GDES-Media"),
                str(base / "GDES-Update"))
    return str(root / "Backups"), str(root / "Media"), ""


def _copy_existing(src: Path, dst: Path) -> None:
    """One-time migration of existing files from an app-folder default into the
    newly chosen location. Never overwrites newer files; failures are non-fatal."""
    try:
        if not src.is_dir() or src.resolve() == dst.resolve():
            return
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            target = dst / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            elif not target.exists():
                shutil.copy2(item, target)
        log(f"Copied existing {src.name}/ contents into {dst}.")
    except (OSError, shutil.Error) as exc:
        log(f"Could not copy existing {src.name}/: {exc}")


def _folder_wizard(root: Path):
    """First-run dialog to pick the Backups and Media folders.

    Returns {"backup_dir","media_dir","migrate"} or None if unavailable/cancelled.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except Exception:
        return None

    def_backup, def_media, def_update = _default_folder_suggestions(root)

    win = tk.Tk()
    win.title("BGDDR — Choose backup, media & update folders")
    win.geometry("580x340")
    win.resizable(False, False)

    tk.Label(win, text="Where should backups, media and updates be stored?",
             font=("Segoe UI", 11, "bold")).pack(pady=(14, 2))
    tk.Label(win, wraplength=540, justify="left", fg="#475569", font=("Segoe UI", 9),
             text="The live database stays on this PC. Backup snapshots and uploaded "
                  "files can be placed in a OneDrive folder so they sync safely. The "
                  "update folder is where new app versions are published; leave it "
                  "blank to disable in-app updates. You can change these later via the "
                  "BGDDR_BACKUP_DIR / BGDDR_MEDIA_DIR / BGDDR_UPDATE_DIR environment "
                  "variables.").pack(padx=16, pady=(0, 10))

    frm = tk.Frame(win)
    frm.pack(padx=16, fill="x")

    def _row(label, default, r):
        tk.Label(frm, text=label, width=14, anchor="w").grid(row=r, column=0, pady=5, sticky="w")
        var = tk.StringVar(value=default)
        ent = tk.Entry(frm, textvariable=var, width=44)
        ent.grid(row=r, column=1, pady=5)

        def browse():
            chosen = filedialog.askdirectory(initialdir=default or str(root), title=label)
            if chosen:
                var.set(chosen)

        tk.Button(frm, text="Browse…", command=browse).grid(row=r, column=2, padx=(6, 0))
        return var

    backup_var = _row("Backup folder", def_backup, 0)
    media_var = _row("Media folder", def_media, 1)
    update_var = _row("Update folder", def_update, 2)

    migrate_var = tk.BooleanVar(value=True)
    tk.Checkbutton(win, variable=migrate_var,
                   text="Copy any existing Backups/ and Media/ files into the new folders",
                   fg="#475569").pack(pady=(8, 4))

    result = {"val": None}

    def save():
        b, m, u = backup_var.get().strip(), media_var.get().strip(), update_var.get().strip()
        if not b or not m:
            messagebox.showerror("BGDDR", "Backup and Media folders are required."); return
        try:  # confirm we can actually create/write them
            Path(b).mkdir(parents=True, exist_ok=True)
            Path(m).mkdir(parents=True, exist_ok=True)
            if u:
                Path(u).mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("BGDDR", f"Cannot create folder:\n{exc}"); return
        result["val"] = {"backup_dir": b, "media_dir": m, "update_dir": u,
                         "migrate": migrate_var.get()}
        win.destroy()

    row = tk.Frame(win)
    row.pack(pady=12)
    tk.Button(row, text="Save", width=12, command=save).grid(row=0, column=0, padx=6)
    tk.Button(row, text="Use defaults", width=12,
              command=lambda: (result.update(val=None), win.destroy())).grid(row=0, column=1, padx=6)
    win.mainloop()
    return result["val"]


def configure_data_paths(root: Path, interactive: bool = True) -> None:
    """Resolve where Backups/ and Media/ live and export them as env vars BEFORE
    Django loads.

    Precedence: explicit env var > saved config (bgddr_paths.json) > first-run
    wizard (packaged .exe only) > default (subfolders of the app directory).
    """
    have_backup = bool(os.environ.get("BGDDR_BACKUP_DIR"))
    have_media = bool(os.environ.get("BGDDR_MEDIA_DIR"))
    if have_backup and have_media:
        return  # caller set both explicitly; honour them as-is

    cfg_path = root / _PATHS_CONFIG_NAME
    saved = _read_paths_config(cfg_path)

    # First launch of the packaged app: ask once.
    if saved is None and interactive and getattr(sys, "frozen", False):
        chosen = _folder_wizard(root)
        if chosen:
            if chosen.get("migrate"):
                _copy_existing(root / "Backups", Path(chosen["backup_dir"]))
                _copy_existing(root / "Media", Path(chosen["media_dir"]))
            saved = {"backup_dir": chosen["backup_dir"], "media_dir": chosen["media_dir"]}
            if chosen.get("update_dir"):
                saved["update_dir"] = chosen["update_dir"]
            _write_paths_config(cfg_path, saved)
        else:
            # "Use defaults": remember the suggested folders so OneDrive remains
            # the backup target when it is available.
            def_backup, def_media, def_update = _default_folder_suggestions(root)
            for folder in (def_backup, def_media, def_update):
                if folder:
                    Path(folder).mkdir(parents=True, exist_ok=True)
            saved = {"backup_dir": def_backup, "media_dir": def_media}
            if def_update:
                saved["update_dir"] = def_update
            _write_paths_config(cfg_path, saved)

    if not saved:
        return  # settings.py falls back to app-folder defaults

    if not have_backup and saved.get("backup_dir"):
        os.environ["BGDDR_BACKUP_DIR"] = saved["backup_dir"]
    if not have_media and saved.get("media_dir"):
        os.environ["BGDDR_MEDIA_DIR"] = saved["media_dir"]


# --------------------------------------------------------------------------- #
# In-app update (from the OneDrive update folder or GitHub Releases)
# --------------------------------------------------------------------------- #
_GITHUB_REPO = os.environ.get("BGDDR_GITHUB_REPO", "arkoamit-bot/GDES").strip()
# Optional read-only token for a PRIVATE releases repo. Prefer a PUBLIC releases
# repo (no token needed, no token shipped to clinic PCs). If you must use a
# private repo, set BGDDR_GITHUB_TOKEN to a fine-grained token with read-only
# access to that repo's Contents/Releases.
_GITHUB_TOKEN = os.environ.get("BGDDR_GITHUB_TOKEN", "").strip()
_GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"


def _github_headers(accept: str = "application/vnd.github+json") -> dict:
    h = {"Accept": accept, "User-Agent": "GDES-Updater"}
    if _GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {_GITHUB_TOKEN}"
    return h


def _resolve_update_dir(root: Path) -> str | None:
    """Where published updates live. Returns the single best candidate.
    (Legacy — prefer _collect_update_dirs for multi-dir fallback.)"""
    dirs = _collect_update_dirs(root)
    return dirs[0] if dirs else None


def _collect_update_dirs(root: Path) -> list[str]:
    """Return all candidate update directories, highest priority first.

    Env var > saved config > <OneDrive>/GDES-Update > <OneDrive>/BGDDR-Update.
    The caller tries each in order; the first that has a newer manifest wins.
    """
    dirs: list[str] = []
    env = os.environ.get("BGDDR_UPDATE_DIR")
    if env:
        dirs.append(env)
    saved = _read_paths_config(root / _PATHS_CONFIG_NAME) or {}
    if saved.get("update_dir") and saved["update_dir"] not in dirs:
        dirs.append(saved["update_dir"])
    onedrive = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer") \
        or os.environ.get("OneDriveCommercial") or ""
    if onedrive and Path(onedrive).is_dir():
        for name in ("GDES-Update", "BGDDR-Update"):
            cand = str(Path(onedrive) / name)
            if cand not in dirs and Path(cand).is_dir():
                dirs.append(cand)
    return dirs


def _github_update_available(current: str) -> dict | None:
    """Check GitHub Releases for a newer onedir zip asset."""
    if not _GITHUB_REPO:
        return None
    try:
        import urllib.request

        from bgddr.updater import is_newer

        url = _GITHUB_API.format(repo=_GITHUB_REPO)
        req = urllib.request.Request(url, headers=_github_headers())
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        version = str(data.get("tag_name") or data.get("name") or "").strip().lstrip("v")
        if not version or not is_newer(version, current):
            return None

        assets = data.get("assets") or []
        preferred = (f"GDES-{version}.zip", f"GDES_{version}.zip", f"BGDDR-{version}.zip")
        asset = next((a for a in assets if a.get("name") in preferred), None)
        if asset is None:
            asset = next(
                (
                    a for a in assets
                    if str(a.get("name", "")).lower().endswith(".zip")
                    and ("gdes" in str(a.get("name", "")).lower()
                         or "bgddr" in str(a.get("name", "")).lower())
                ),
                None,
            )
        if not asset or not asset.get("browser_download_url"):
            log(f"GitHub release {version} has no GDES zip asset.")
            return None

        sha256 = ""
        digest = str(asset.get("digest") or "").strip()
        if digest.lower().startswith("sha256:"):
            sha256 = digest.split(":", 1)[1].lower()

        return {
            "version": version,
            "file": asset["name"],
            "url": asset["browser_download_url"],
            "api_url": asset.get("url", ""),  # asset API URL — used for private repos
            "sha256": sha256,
            "notes": data.get("body") or "",
        }
    except Exception as exc:
        code = getattr(exc, "code", None)
        if code == 404:
            log(f"GitHub update check: repo '{_GITHUB_REPO}' not found (404). "
                "Set BGDDR_GITHUB_REPO env var if the repo was moved or renamed.")
        else:
            log(f"GitHub update check failed: {exc}")
        return None


def _github_download_and_stage(manifest: dict, log=print) -> Path | None:
    """Download a GitHub release asset, then reuse the normal verifier/stager."""
    # For a PRIVATE repo the browser_download_url 404s without a session; the
    # asset API URL + an octet-stream Accept + token works. Public repos use the
    # plain browser_download_url (no token needed).
    if _GITHUB_TOKEN and manifest.get("api_url"):
        url = manifest["api_url"]
        headers = _github_headers(accept="application/octet-stream")
    else:
        url = manifest.get("url")
        headers = {"User-Agent": "GDES-Updater"}
    if not url:
        log("No download URL in GitHub update manifest.")
        return None
    try:
        import urllib.request

        from bgddr import updater

        download_dir = Path(tempfile.mkdtemp(prefix="gdes-gh-update-"))
        zip_path = download_dir / manifest["file"]
        req = urllib.request.Request(url, headers=headers)
        log(f"Downloading {manifest['file']} from GitHub ...")
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(zip_path, "wb") as out:
                shutil.copyfileobj(resp, out)
        staged = updater.verify_and_stage(download_dir, manifest, log=log)
        shutil.rmtree(download_dir, ignore_errors=True)
        return staged
    except Exception as exc:
        log(f"GitHub download/stage failed: {exc}")
        return None


def _tk_root():
    """Return (root, owned). Reuse the live default Tk root if one exists (e.g.
    the status window is open), else create a hidden throwaway root we own."""
    import tkinter as tk
    existing = getattr(tk, "_default_root", None)
    if existing is not None:
        return existing, False
    root = tk.Tk(); root.withdraw()
    return root, True


def _info_msg(title: str, text: str) -> None:
    try:
        from tkinter import messagebox
        root, owned = _tk_root()
        messagebox.showinfo(title, text, parent=root)
        if owned:
            root.destroy()
    except Exception:
        log(text)


def _update_prompt(current: str, manifest: dict) -> bool:
    """Ask whether to install the available update. Returns True to proceed."""
    try:
        from tkinter import messagebox
    except Exception:
        return False
    notes = (manifest.get("notes") or "").strip()
    body = (f"A new version of GDES is available.\n\n"
            f"Installed:  {current}\nAvailable:  {manifest['version']}\n"
            + (f"\n{notes}\n" if notes else "")
            + "\nThe app will close, update itself, and reopen. Your data and "
              "backups are not touched. Install now?")
    root, owned = _tk_root()
    ok = messagebox.askyesno("GDES - Update available", body, parent=root)
    if owned:
        root.destroy()
    return bool(ok)


def run_update_check(root: Path, interactive: bool = True) -> bool:
    """Check the update folder and, if the user confirms, stage the new build and
    spawn the swap helper. Returns True if an update is being applied — the caller
    must then exit so the helper can replace the files.

    Only meaningful for the packaged .exe; a no-op when running from source.
    """
    if not getattr(sys, "frozen", False):
        return False
    try:
        from bgddr import updater
        from bgddr.version import __version__ as current
    except Exception as exc:
        log(f"Update check unavailable: {exc}")
        return False

    manifest = None
    update_dir = None
    github_mode = False
    for candidate in _collect_update_dirs(root):
        try:
            md = updater.check_for_update(Path(candidate), current)
            if md:
                manifest = md
                update_dir = candidate
                break
        except Exception as exc:
            log(f"Update check failed for {candidate}: {exc}")
            continue
    if not manifest:
        manifest = _github_update_available(current)
        github_mode = bool(manifest)
    if not manifest:
        log(f"Up to date (version {current}).")
        return False

    log(f"Update available: {current} -> {manifest['version']}")
    if interactive and not _update_prompt(current, manifest):
        log("User postponed the update.")
        return False

    if github_mode:
        staging = _github_download_and_stage(manifest, log=log)
    else:
        staging = updater.verify_and_stage(Path(update_dir), manifest, log=log)
    if not staging:
        if interactive:
            _info_msg("GDES - Update failed",
                      "The update could not be verified or extracted. "
                      "See Logs\\update.log. Your app is unchanged.")
        return False

    # A safety snapshot before we hand over to the swap helper.
    try:
        from bgddr.backup import create_tiered_backup
        create_tiered_backup(reason="pre_update")
    except Exception as exc:
        log(f"pre-update backup warning: {exc}")

    # The code (BGDDR.exe + _internal) lives in the APP folder, which is NOT the
    # data dir: since the data dir was moved to %LOCALAPPDATA%\GDES\Data, the
    # swap must target app_dir(), not `root` (the data dir). Getting this wrong
    # makes the updater "succeed" but silently swap nothing.
    code_dir = app_dir()
    started = updater.apply_update(
        app_dir=code_dir, staging_root=staging,
        old_version=current, new_version=manifest["version"],
        log_path=Path(root) / "Logs" / "update.log", log=log,
    )
    if started and interactive:
        _info_msg("GDES - Updating",
                  f"Updating to {manifest['version']}. GDES will close and reopen "
                  "in a moment.")
    return started


# --------------------------------------------------------------------------- #
# First-run initialisation
# --------------------------------------------------------------------------- #
def initialise(data_dir: Path) -> None:
    """Migrate, seed, and collect static. Idempotent; safe on every launch."""
    from django.core.management import call_command

    def run_cmd(*args, **kwargs):
        # Route all command output to the sink (stdout is None in windowed mode).
        kwargs.setdefault("stdout", _SINK)
        kwargs.setdefault("stderr", _SINK)
        call_command(*args, **kwargs)

    log("Applying database migrations ...")
    # P0-2: snapshot -> integrity-check -> migrate -> restore-on-failure.
    try:
        from desktop.safe_migrate import run_safe_migrate
    except Exception:
        from safe_migrate import run_safe_migrate  # type: ignore
    from django.conf import settings as _settings
    result = run_safe_migrate(
        log_path=Path(_settings.LOGS_DIR) / "migration.log", notify=log,
    )
    if result.get("skipped"):
        log("  (database already up to date)")

    marker = data_dir / ".initialized"
    if not marker.exists():
        log("First run - seeding reference data ...")
        for cmd in ("seed_roles", "seed_labs", "seed_drugs", "seed_studies"):
            try:
                run_cmd(cmd, verbosity=0)
            except Exception as exc:  # a seed failing must not block startup
                log(f"  (skipped {cmd}: {exc})")

    # P1-2: version-gated KB seeding. Runs on first launch AND whenever the
    # packaged KB version is newer than what's installed; skipped otherwise so
    # a same-version relaunch never re-touches a clinician-edited knowledge base.
    from knowledge.kb_version import (
        should_seed_kb, stamp_kb_version, get_installed_kb_version, PACKAGED_KB_VERSION,
    )
    if should_seed_kb():
        log(f"Seeding knowledge base "
            f"(installed={get_installed_kb_version() or 'none'} -> {PACKAGED_KB_VERSION}) ...")
        for cmd in ("seed_knowledge_base", "seed_v4_knowledge",
                     "seed_clinical_cases", "seed_drug_knowledge",
                     "seed_drug_intelligence", "activate_entries"):
            try:
                run_cmd(cmd, verbosity=0)
            except Exception as exc:
                log(f"  (skipped {cmd}: {exc})")
        stamp_kb_version()
    else:
        log(f"Knowledge base up to date (v{get_installed_kb_version()}); skipping seed.")

    if not marker.exists():
        try:
            marker.write_text("ok", encoding="utf-8")
        except OSError:
            pass

    log("Collecting static files ...")
    try:
        run_cmd("collectstatic", interactive=False, verbosity=0)
    except Exception as exc:
        log(f"  (collectstatic warning: {exc})")


def ensure_admin(interactive: bool = True) -> None:
    """Guarantee at least one superuser. Prompt once via a small Tk dialog."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    if User.objects.filter(is_superuser=True).exists():
        return

    username, password = _admin_dialog() if interactive else (None, None)
    if not username:  # dialog cancelled — fall back to a documented default
        username, password = "admin", "bgddr-admin"
        log("Admin dialog cancelled; created default admin / bgddr-admin "
            "(change it in the admin immediately).")
    User.objects.create_superuser(username=username, password=password)
    log(f"Administrator account '{username}' created.")


def _admin_dialog():
    """Return (username, password) from a tiny Tk form, or (None, None)."""
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        return None, None

    result = {"u": None, "p": None}
    win = tk.Tk()
    win.title("BGDDR — Create administrator")
    win.geometry("360x230")
    win.resizable(False, False)

    tk.Label(win, text="First run: create the administrator account",
             font=("Segoe UI", 10, "bold")).pack(pady=(14, 8))
    frm = tk.Frame(win)
    frm.pack(padx=16, fill="x")

    tk.Label(frm, text="Username").grid(row=0, column=0, sticky="w", pady=4)
    u = tk.Entry(frm, width=24)
    u.insert(0, "admin")
    u.grid(row=0, column=1, pady=4)
    tk.Label(frm, text="Password").grid(row=1, column=0, sticky="w", pady=4)
    p = tk.Entry(frm, width=24, show="*")
    p.grid(row=1, column=1, pady=4)
    tk.Label(frm, text="Confirm").grid(row=2, column=0, sticky="w", pady=4)
    p2 = tk.Entry(frm, width=24, show="*")
    p2.grid(row=2, column=1, pady=4)

    def submit():
        if not u.get().strip():
            messagebox.showerror("BGDDR", "Username is required."); return
        if len(p.get()) < 6:
            messagebox.showerror("BGDDR", "Password must be at least 6 characters."); return
        if p.get() != p2.get():
            messagebox.showerror("BGDDR", "Passwords do not match."); return
        result["u"], result["p"] = u.get().strip(), p.get()
        win.destroy()

    tk.Button(win, text="Create", width=12, command=submit).pack(pady=14)
    win.mainloop()
    return result["u"], result["p"]


# --------------------------------------------------------------------------- #
# Backups
# --------------------------------------------------------------------------- #
def start_backups() -> None:
    from django.conf import settings

    from bgddr.backup import create_tiered_backup

    # P1-1: tiered, integrity-checked ZIP archives (Daily/Weekly/Monthly).
    create_tiered_backup(reason="startup")
    hours = max(1, int(settings.BACKUP_CONFIG.get("interval_hours", 6)))

    def loop():
        while True:
            time.sleep(hours * 3600)
            try:
                create_tiered_backup(reason="scheduled")
            except Exception as exc:
                log(f"Scheduled backup warning: {exc}")

    threading.Thread(target=loop, daemon=True, name="bgddr-backup").start()
    log(f"Backups: startup ZIP snapshot taken; every {hours}h thereafter.")


# --------------------------------------------------------------------------- #
# Desktop shortcut (first run)
# --------------------------------------------------------------------------- #
def create_desktop_shortcut(data_dir: Path) -> None:
    """On first launch of the packaged .exe, drop a Desktop shortcut so the user
    can relaunch easily. Runs once (guarded by a marker); errors are non-fatal."""
    if not getattr(sys, "frozen", False):
        return  # only meaningful for the packaged exe
    marker = data_dir / ".shortcut_done"
    if marker.exists():
        return
    try:
        import subprocess

        exe = Path(sys.executable).resolve()
        desktop = Path(os.path.join(os.path.expanduser("~"), "Desktop"))
        if not desktop.is_dir():
            return
        lnk = desktop / "BGDDR Registry.lnk"
        ps = (
            "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}');"
            "$s.TargetPath='{exe}';"
            "$s.WorkingDirectory='{wd}';"
            "$s.IconLocation='{exe}';"
            "$s.Description='BGDDR Registry';"
            "$s.Save()"
        ).format(lnk=str(lnk), exe=str(exe), wd=str(exe.parent))
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=20, check=False)
        log(f"Desktop shortcut created: {lnk}")
    except Exception as exc:
        log(f"Could not create desktop shortcut: {exc}")
    finally:
        try:
            marker.write_text("ok", encoding="utf-8")
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# Server + status window
# --------------------------------------------------------------------------- #
def make_server():
    import time as _t
    from waitress import create_server
    from django.core.wsgi import get_wsgi_application

    log("make_server: starting get_wsgi_application()...")
    _t0 = _t.time()
    application = get_wsgi_application()  # honours DJANGO_SETTINGS_MODULE
    log(f"make_server: WSGI app ready in {_t.time()-_t0:.1f}s")
    _t0 = _t.time()
    srv = create_server(application, host=HOST, port=PORT, threads=8)
    log(f"make_server: waitress server created in {_t.time()-_t0:.1f}s")
    return srv


def run(server, root: Path) -> None:
    threading.Thread(target=server.run, daemon=True, name="bgddr-waitress").start()
    log(f"Serving at {URL}")
    time.sleep(1.0)
    try:
        webbrowser.open(URL)
    except Exception:
        pass
    _status_window(server, root)


def _status_window(server, root: Path) -> None:
    """A small always-available window so the user can stop the app cleanly."""
    try:
        import tkinter as tk
    except Exception:
        # No GUI available — block until Ctrl+C.
        log("Running headless. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass
        return

    win = tk.Tk()
    win.title("BGDDR Registry")
    win.geometry("380x170")
    win.resizable(False, False)

    try:
        from bgddr.version import __version__ as _ver
    except Exception:
        _ver = ""
    tk.Label(win, text="BGDDR Registry is running" + (f"  ·  v{_ver}" if _ver else ""),
             font=("Segoe UI", 12, "bold")).pack(pady=(18, 4))
    tk.Label(win, text=URL, fg="#1d4ed8", font=("Segoe UI", 10)).pack()
    tk.Label(win, text="Keep this window open while you use the app.",
             fg="#64748b", font=("Segoe UI", 8)).pack(pady=(2, 10))

    row = tk.Frame(win)
    row.pack()
    tk.Button(row, text="Open in browser", width=15,
              command=lambda: webbrowser.open(URL)).grid(row=0, column=0, padx=4)

    def stop():
        log("Stopping ...")
        try:
            server.close()
        except Exception:
            pass
        win.destroy()
        os._exit(0)

    def check_updates():
        try:
            applying = run_update_check(root, interactive=True)
        except Exception as exc:
            log(f"Update check error: {exc}")
            applying = False
        if applying:  # user accepted — shut down so the helper can swap files
            log("Update accepted; shutting down for swap.")
            try:
                server.close()
            except Exception:
                pass
            win.destroy()
            os._exit(0)

    # Offer the button when a local update folder exists or GitHub is configured.
    if getattr(sys, "frozen", False) and (_resolve_update_dir(root) or _GITHUB_REPO):
        tk.Button(row, text="Check for updates", width=15,
                  command=check_updates).grid(row=0, column=1, padx=4)
    tk.Button(row, text="Stop", width=9, command=stop).grid(row=0, column=2, padx=4)
    win.protocol("WM_DELETE_WINDOW", stop)
    win.mainloop()


def _fatal_dialog(title: str, text: str) -> None:
    """Show a blocking error dialog (best effort) then let the caller exit."""
    try:
        from tkinter import messagebox
        root, owned = _tk_root()
        messagebox.showerror(title, text, parent=root)
        if owned:
            root.destroy()
    except Exception:
        log(text)


def ensure_webview2(root: Path) -> None:
    """P0-3: make sure a browser surface is available on a clean machine.

    This launcher displays the app in the system default browser (not an embedded
    WebView2), so WebView2 is not strictly required — but if a future embedded
    build needs it, we detect it here and run the bundled Evergreen bootstrapper
    (silent, per-user, no admin) when present. Missing WebView2 never blocks
    launch; the browser fallback always applies.
    """
    hardening = _import_hardening()
    try:
        if hardening.is_webview2_installed():
            return
    except Exception:
        return
    # Not installed (or non-Windows). Try a bundled per-user bootstrapper if we
    # ship one next to the exe; otherwise just continue with the browser.
    setup = root / "MicrosoftEdgeWebview2Setup.exe"
    if getattr(sys, "frozen", False) and setup.exists():
        try:
            import subprocess
            log("WebView2 runtime not found; installing bundled Evergreen runtime ...")
            subprocess.run(
                [str(setup), "/silent", "/install"],
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=300, check=False,
            )
        except Exception as exc:
            log(f"WebView2 bootstrap warning (continuing with browser): {exc}")
    else:
        log("WebView2 runtime not detected; the app opens in your default browser.")


def _ensure_settings_desktop() -> None:
    """Synthesise ``bgddr.settings_desktop`` in ``sys.modules`` when frozen.

    PyInstaller's PYZ archive bundles compiled bytecode for ``bgddr.settings``
    but often fails to include ``bgddr.settings_desktop`` because its relative
    import (``from .settings import *``) can trigger a circular or incomplete
    analysis at build time.  Rather than fighting PyInstaller's collection, we
    create the module at runtime: import ``bgddr.settings``, shallow-copy every
    attribute, apply the desktop overrides, and register the result so Django's
    ``django.setup()`` can find it as a normal module.
    """
    import types, importlib, secrets

    if "bgddr.settings_desktop" in sys.modules:
        return  # already available (source run or future PyInstaller fix)

    base = importlib.import_module("bgddr.settings")
    mod = types.ModuleType("bgddr.settings_desktop")
    mod.__package__ = "bgddr"
    mod.__path__ = []  # mark as package to satisfy any sub-imports
    # Shallow-copy every public attribute from settings.
    for _k in dir(base):
        if _k.startswith("_"):
            continue
        setattr(mod, _k, getattr(base, _k))
    # Desktop overrides.
    mod.DEBUG = False
    mod.ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
    mod.CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]
    # Persist the SECRET_KEY so sessions survive restarts.
    try:
        _key_file = base.BGDDR_DATA_DIR / ".secret_key"
        if _key_file.exists():
            mod.SECRET_KEY = _key_file.read_text(encoding="utf-8").strip()
        else:
            mod.SECRET_KEY = secrets.token_urlsafe(64)
            _key_file.write_text(mod.SECRET_KEY, encoding="utf-8")
    except OSError:
        mod.SECRET_KEY = secrets.token_urlsafe(64)

    sys.modules["bgddr.settings_desktop"] = mod


def main() -> None:
    check = "--check" in sys.argv  # headless smoke test of the packaged build
    data_dir = bootstrap_env()
    # Resolve/prompt for Backups & Media locations and export them as env vars
    # BEFORE Django reads settings. Skipped when running the headless self-check.
    configure_data_paths(data_dir, interactive=not check)
    _ensure_settings_desktop()
    import django
    django.setup()

    log(f"Data directory: {data_dir}")

    hardening = _import_hardening()

    # P0-1: never run against a cloud-synced live DB (WAL sync = corruption).
    from django.conf import settings as _dj_settings
    try:
        hardening.assert_db_path_local(_dj_settings.DATABASES["default"]["NAME"])
    except RuntimeError as exc:
        log(str(exc))
        if not check:
            _fatal_dialog("BGDDR — Unsafe data location", str(exc))
        os._exit(2)

    # P0-4: single-instance guard — refuse to start a 2nd server on the same DB.
    if not check:
        guard_port = int(os.environ.get("BGDDR_GUARD_PORT", "8765"))
        try:
            globals()["_INSTANCE_LOCK"] = hardening.acquire_single_instance(HOST, guard_port)
        except hardening.SingleInstanceError:
            log("Another BGDDR instance is already running; opening the browser and exiting.")
            try:
                webbrowser.open(URL)
            except Exception:
                pass
            os._exit(0)

        # P0-3: ensure a display surface (browser fallback always applies).
        ensure_webview2(data_dir)

    # Check for a published update early: if the user accepts, we stage it and
    # exit here so the helper can swap the files (no point migrating/serving the
    # about-to-be-replaced version).
    if not check and run_update_check(data_dir, interactive=True):
        log("Update in progress; exiting so the helper can swap files.")
        os._exit(0)
    initialise(data_dir)

    # P1-3: startup health summary. Log always; block only on CRITICAL failures
    # (empty active KB / unreadable DB) so a minor mismatch never strands the clinic.
    try:
        from knowledge.kb_version import kb_health_summary
        health = kb_health_summary()
        log("Knowledge health: " + ", ".join(
            f"{k}={health[k]}" for k in
            ("kb_version", "diseases", "rules_active", "rules_total", "pathways", "cases", "guidelines")
        ) + f", status={health['status']}")
        if health["status"] == "critical" and not check:
            msg = ("Startup blocked — critical knowledge-base problem:\n  "
                   + "\n  ".join(health["critical"])
                   + "\n\nRestore a recent backup or reinstall.")
            log(msg)
            _fatal_dialog("BGDDR — Startup blocked", msg)
            os._exit(3)
    except Exception as exc:
        log(f"Health summary warning (continuing): {exc}")

    ensure_admin(interactive=not check)

    if check:
        server = make_server()           # binds the port to prove it works
        server.close()
        # Prove the compiled SPSS writer (pyreadstat) is bundled & working.
        try:
            from exports.services.writers import to_sav
            blob = to_sav(["x"], [{"x": 1}], defs={"x": ("integer", "", "test")})
            assert blob[:4] == b"$FL2"
            log("Self-check: SPSS .sav export OK.")
        except Exception as exc:
            log(f"Self-check WARNING: SPSS export failed: {exc}")
        log("Self-check OK: migrate, seed, static, admin, and server all wired.")
        return
    create_desktop_shortcut(data_dir)
    start_backups()
    log("main: about to call make_server()...")
    server = make_server()
    # Start error reporting (hook + scheduler) AFTER the server is created.
    # Moving this after make_server() avoids a PyInstaller frozen-build deadlock
    # where background-thread imports block get_wsgi_application().
    if not check:
        try:
            from feedback.services.exception_hook import install_hook
            from feedback.services.scheduler import start_scheduler
            install_hook()
            start_scheduler()
            log("Error reporting system initialised.")
        except Exception as exc:
            log(f"Error reporting init warning: {exc}")
    run(server, data_dir)


if __name__ == "__main__":
    main()
