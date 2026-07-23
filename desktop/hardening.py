"""Desktop deployment hardening helpers (testable, no Django import at module load).

Covers the pure-logic parts of the P0 pilot-hardening tasks so they can be unit
tested off a Windows build box:

- P0-1  cloud-synced-DB guard + a safe local data-dir resolver
- P0-3  WebView2 runtime detection (+ browser fallback decision)
- P0-4  single-instance guard via an exclusive localhost port bind

None of these import Django; the launcher wires them in at the right moments.
"""
from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

# Folder-name segments that indicate a cloud-sync root. Matched case-insensitively
# against each part of the resolved path.
CLOUD_SYNC_SEGMENTS = (
    "onedrive",
    "dropbox",
    "google drive",
    "googledrive",
    "icloud drive",
    "iclouddrive",
    "icloud~",
    "box sync",
    "boxsync",
)


# --------------------------------------------------------------------------- #
# P0-1 — cloud-synced DB guard + local data-dir resolver
# --------------------------------------------------------------------------- #
def cloud_sync_segment(path) -> str | None:
    """Return the offending path segment if `path` sits under a known cloud-sync
    folder, else None. Case-insensitive, matches whole path components.

        cloud_sync_segment(r"C:\\Users\\x\\OneDrive\\BGDDR\\db.sqlite3") -> "OneDrive"
        cloud_sync_segment(r"C:\\Users\\x\\AppData\\Local\\GDES\\db.sqlite3") -> None
    """
    if not path:
        return None
    # Normalise separators so we can always split manually — Path.parts on
    # Linux does NOT parse Windows-style paths into directory components.
    normalised = str(path).replace("\\", "/")
    parts = normalised.split("/")
    for part in parts:
        low = part.strip().lower()
        for seg in CLOUD_SYNC_SEGMENTS:
            # exact component match, or component starts with the marker
            if low == seg or low.startswith(seg):
                return part
    return None


def assert_db_path_local(db_path, allow_synced: bool | None = None) -> None:
    """Raise RuntimeError if the live DB path is inside a cloud-synced folder.

    The escape hatch is BGDDR_ALLOW_SYNCED_DB=1 (or allow_synced=True), for devs
    who knowingly accept the risk. Production/pilot must never set it.
    """
    if allow_synced is None:
        allow_synced = os.environ.get("BGDDR_ALLOW_SYNCED_DB", "").strip() in ("1", "true", "True", "yes")
    if allow_synced:
        return
    seg = cloud_sync_segment(db_path)
    if seg:
        raise RuntimeError(
            "Refusing to start: the live database would live inside a cloud-synced "
            f"folder ('{seg}').\n\n"
            f"    DB path: {db_path}\n\n"
            "A sync client (OneDrive/Dropbox/Google Drive/iCloud) can copy a "
            "half-written database page and permanently corrupt patient data.\n"
            "Move the data folder to LOCAL disk (e.g. %LOCALAPPDATA%\\GDES\\Data) "
            "by setting BGDDR_DATA_DIR / BGDDR_DB_PATH, and keep only the ZIP "
            "backups in the synced folder.\n"
            "Developers who accept the risk can set BGDDR_ALLOW_SYNCED_DB=1."
        )


def resolve_local_data_dir() -> Path:
    """A reliably-writable, no-admin LOCAL data directory for the packaged app.

    Preference: %LOCALAPPDATA%\\GDES\\Data  ->  ~/Documents/BGDDR  ->  ~/.gdes/Data.
    Never returns a cloud-synced path; the first candidate that is writable and
    not cloud-synced wins.
    """
    candidates: list[Path] = []
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        candidates.append(Path(local_appdata) / "GDES" / "Data")
    home = Path(os.path.expanduser("~"))
    candidates.append(home / "Documents" / "BGDDR")
    candidates.append(home / ".gdes" / "Data")

    for cand in candidates:
        if cloud_sync_segment(cand):
            continue
        try:
            cand.mkdir(parents=True, exist_ok=True)
            # prove it is writable
            probe = cand / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return cand.resolve()
        except OSError:
            continue
    # Last resort: a temp dir (should never happen on a real desktop).
    import tempfile
    fallback = Path(tempfile.gettempdir()) / "GDES" / "Data"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback.resolve()


# --------------------------------------------------------------------------- #
# P0-4 — single-instance guard (exclusive localhost port bind)
# --------------------------------------------------------------------------- #
class SingleInstanceError(RuntimeError):
    """Raised when another instance already holds the guard port."""


def acquire_single_instance(host: str, port: int) -> socket.socket:
    """Bind an exclusive socket on (host, port) as a whole-app lock.

    Returns the held socket (keep a reference for the process lifetime). Raises
    SingleInstanceError if the port is already bound — i.e. another instance is
    running — so the caller can focus/exit instead of starting a 2nd server on
    the same SQLite file.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Deliberately do NOT set SO_REUSEADDR: we WANT a second bind to fail.
    try:
        s.bind((host, port))
        s.listen(1)
    except OSError as exc:
        s.close()
        raise SingleInstanceError(
            f"Another BGDDR instance is already running on {host}:{port}."
        ) from exc
    return s


# --------------------------------------------------------------------------- #
# P0-3 — WebView2 runtime detection
# --------------------------------------------------------------------------- #
_WEBVIEW2_CLIENT_GUID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"


def is_webview2_installed() -> bool:
    """Detect the Edge WebView2 Evergreen runtime via its registry keys.

    Returns False on non-Windows or when the runtime is absent. Never raises.
    """
    if sys.platform != "win32":
        return False
    try:
        import winreg  # type: ignore
    except Exception:
        return False

    subkeys = (
        (winreg.HKEY_LOCAL_MACHINE,
         rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{_WEBVIEW2_CLIENT_GUID}"),
        (winreg.HKEY_LOCAL_MACHINE,
         rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{_WEBVIEW2_CLIENT_GUID}"),
        (winreg.HKEY_CURRENT_USER,
         rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{_WEBVIEW2_CLIENT_GUID}"),
    )
    for hive, path in subkeys:
        try:
            with winreg.OpenKey(hive, path) as key:
                version, _ = winreg.QueryValueEx(key, "pv")
                if version and version not in ("0.0.0.0", ""):
                    return True
        except FileNotFoundError:
            continue
        except OSError:
            continue
    return False
