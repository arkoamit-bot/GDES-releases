"""Desktop self-update from a (OneDrive-synced) update folder.

Stdlib-only and Django-free so it can run before ``django.setup()`` and inside
the frozen build. The maintainer periodically drops two things into the update
folder (``BGDDR_UPDATE_DIR``, e.g. ``…\\OneDrive\\BGDDR-Update``):

    latest.json          {"version": "6.6.0", "file": "BGDDR-6.6.0.zip",
                          "sha256": "<hex>", "notes": "…"}
    BGDDR-6.6.0.zip      a freshly built dist\\BGDDR (BGDDR.exe + _internal\\)

On launch (and via a "Check for updates" button) the app compares its own
``bgddr.version.__version__`` against the manifest. If newer AND the user
confirms, the zip is checksum-verified and extracted to a staging folder, and a
detached PowerShell helper swaps *only* the code (BGDDR.exe + _internal\\) once
this process exits — leaving db.sqlite3 and all data untouched — then relaunches.
The previous code is renamed to ``*.old-<version>`` so a swap failure rolls back
automatically and a bad release can be reverted by hand.

Security note: this executes a build supplied via a shared folder. It is
therefore always *prompted* (never silent) and refuses to apply a package whose
SHA-256 does not match the manifest when a checksum is provided.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

MANIFEST_NAME = "latest.json"


# --------------------------------------------------------------------------- #
# Version comparison
# --------------------------------------------------------------------------- #
def parse_version(value: str) -> tuple[int, ...]:
    """Turn '6.6.0' into (6, 6, 0). Non-numeric parts degrade to 0."""
    parts: list[int] = []
    for chunk in str(value).split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts) or (0,)


def is_newer(candidate: str, current: str) -> bool:
    return parse_version(candidate) > parse_version(current)


# --------------------------------------------------------------------------- #
# Manifest / availability
# --------------------------------------------------------------------------- #
def read_manifest(update_dir: Path) -> dict | None:
    """Return the parsed manifest dict, or None if missing/invalid."""
    manifest = Path(update_dir) / MANIFEST_NAME
    try:
        if manifest.is_file():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("version") and data.get("file"):
                return data
    except (OSError, ValueError):
        pass
    return None


def check_for_update(update_dir: Path, current_version: str) -> dict | None:
    """Return the manifest if it advertises a newer version than current."""
    manifest = read_manifest(update_dir)
    if manifest and is_newer(manifest["version"], current_version):
        return manifest
    return None


# --------------------------------------------------------------------------- #
# Verify + stage
# --------------------------------------------------------------------------- #
def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _find_build_root(base: Path) -> Path | None:
    """Locate the folder holding GDES.exe + _internal within an extracted zip
    (top level, or one directory down if the zip wraps it in a folder).
    Also tolerates legacy BGDDR.exe name."""
    candidates = [base] + [p for p in base.iterdir() if p.is_dir()]
    for cand in candidates:
        if ((cand / "GDES.exe").is_file() or (cand / "BGDDR.exe").is_file()) \
                and (cand / "_internal").is_dir():
            return cand
    return None


def verify_and_stage(update_dir: Path, manifest: dict, log=print) -> Path | None:
    """Checksum-verify the update zip and extract it. Returns the folder that
    contains BGDDR.exe + _internal, or None on any failure."""
    zip_path = Path(update_dir) / manifest["file"]
    if not zip_path.is_file():
        log(f"Update file not found: {zip_path}")
        return None

    want = (manifest.get("sha256") or "").strip().lower()
    if want:
        got = _sha256(zip_path)
        if got != want:
            log(f"Checksum mismatch — refusing update (want {want[:12]}…, got {got[:12]}…).")
            return None
    else:
        log("Manifest has no sha256 — proceeding without checksum verification.")

    staging = Path(tempfile.mkdtemp(prefix="bgddr-update-"))
    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(staging)
    except (OSError, zipfile.BadZipFile) as exc:
        log(f"Could not extract update package: {exc}")
        return None

    root = _find_build_root(staging)
    if root is None:
        log("Update package does not contain BGDDR.exe / _internal.")
        return None
    return root


# --------------------------------------------------------------------------- #
# Apply (spawn detached helper)
# --------------------------------------------------------------------------- #
_HELPER_PS1 = r"""
$ErrorActionPreference = "Stop"
$log = "{log}"
function Log($m) {{ try {{ Add-Content -Path $log -Value ("[update] " + (Get-Date -Format o) + " " + $m) }} catch {{}} }}

Log "waiting for pid {pid} to exit"
try {{ Wait-Process -Id {pid} -Timeout 90 }} catch {{}}
Start-Sleep -Seconds 1

$app        = "{app}"
$staging    = "{staging}"
$exe        = Join-Path $app "GDES.exe"
$internal   = Join-Path $app "_internal"
$bakExe     = Join-Path $app "GDES.exe.old-{oldver}"
$bakInt     = Join-Path $app "_internal.old-{oldver}"

# Fallback: also handle legacy BGDDR.exe name
if (-not (Test-Path $exe)) {{
    $exe = Join-Path $app "BGDDR.exe"
    $bakExe = Join-Path $app "BGDDR.exe.old-{oldver}"
}}

try {{
    if (Test-Path $bakExe) {{ Remove-Item $bakExe -Force }}
    if (Test-Path $bakInt) {{ Remove-Item $bakInt -Recurse -Force }}
    Move-Item $exe $bakExe
    Move-Item $internal $bakInt
    # Accept either GDES.exe or BGDDR.exe from the staging folder
    $newExe = Join-Path $staging "GDES.exe"
    if (-not (Test-Path $newExe)) {{ $newExe = Join-Path $staging "BGDDR.exe" }}
    Move-Item $newExe $exe
    Move-Item (Join-Path $staging "_internal") $internal
    Log "swapped code -> {newver} (previous kept as *.old-{oldver})"
}} catch {{
    Log ("swap failed: " + $_.Exception.Message + " -- rolling back")
    if ((Test-Path $bakExe) -and -not (Test-Path $exe)) {{ Move-Item $bakExe $exe }}
    if ((Test-Path $bakInt) -and -not (Test-Path $internal)) {{ Move-Item $bakInt $internal }}
    if (Test-Path $exe) {{ Start-Process $exe }}
    exit 1
}}

try {{ Remove-Item $staging -Recurse -Force }} catch {{}}
Log "relaunching {newver}"
Start-Process $exe
"""


def apply_update(app_dir: Path, staging_root: Path, old_version: str,
                 new_version: str, log_path: Path | None = None, log=print) -> bool:
    """Write and spawn a detached helper that, once THIS process exits, swaps the
    code in ``app_dir`` with the staged build and relaunches. Returns True if the
    helper was launched (the caller should then exit the app)."""
    app_dir = Path(app_dir)
    log_file = str(log_path) if log_path else str(app_dir / "Logs" / "update.log")
    script = _HELPER_PS1.format(
        pid=os.getpid(), app=str(app_dir), staging=str(staging_root),
        oldver=old_version, newver=new_version, log=log_file,
    )
    helper = Path(tempfile.gettempdir()) / f"bgddr_update_{new_version}.ps1"
    try:
        helper.write_text(script, encoding="utf-8")
    except OSError as exc:
        log(f"Could not write updater helper: {exc}")
        return False

    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) \
        | getattr(subprocess, "DETACHED_PROCESS", 0) \
        | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-WindowStyle", "Hidden", "-File", str(helper)],
            creationflags=flags, close_fds=True,
        )
        return True
    except OSError as exc:
        log(f"Could not start updater helper: {exc}")
        return False
