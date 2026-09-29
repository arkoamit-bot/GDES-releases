# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the GDES single-user Windows desktop build.

Build from the project root:

    pyinstaller desktop/BGDDR.spec --noconfirm

Produces  dist/GDES/GDES.exe  plus its support files. Copy the dist/GDES
folder to where the user wants it (e.g. inside OneDrive); db.sqlite3, Backups/,
Exports/, Media/ and Logs/ are created next to GDES.exe on first run.
"""
# --- Build-time shim for Python 3.14 shutil.copyfile COLLECT bug ----------
# Patches BOTH shutil.copyfile AND PyInstaller's assemble to handle the
# [Errno 22] Invalid argument that occurs when reading certain binary files.
import shutil as _shutil_shim
import os as _os_shim
if not getattr(_shutil_shim, "_gdes_patched", False):
    _orig_copyfile = _shutil_shim.copyfile
    def _safe_copyfile(src, dst, *, follow_symlinks=True):
        try:
            return _orig_copyfile(src, dst, follow_symlinks=follow_symlinks)
        except OSError:
            # Fallback: binary chunk copy with per-chunk error handling
            try:
                size = _os_shim.path.getsize(src)
            except Exception:
                size = 0
            with open(src, "rb") as _fs, open(dst, "wb") as _fd:
                pos = 0
                while True:
                    try:
                        _fs.seek(pos)
                        data = _fs.read(1024 * 1024)
                    except (OSError, ValueError):
                        break
                    if not data:
                        break
                    _fd.write(data)
                    pos += len(data)
    _shutil_shim.copyfile = _safe_copyfile
    _shutil_shim._gdes_patched = True

# Also patch PyInstaller's COLLECT.assemble to use the safe copy
try:
    import PyInstaller.building.api as _api
    _orig_assemble = _api.COLLECT.assemble
    def _safe_assemble(self):
        import shutil
        _saved = shutil.copyfile
        shutil.copyfile = _safe_copyfile
        try:
            return _orig_assemble(self)
        finally:
            shutil.copyfile = _saved
    _api.COLLECT.assemble = _safe_assemble
except Exception:
    pass

import os
from pathlib import Path

from PyInstaller.utils.hooks import (collect_data_files, collect_dynamic_libs,
                                     collect_all as _collect_all)

# Build with the desktop settings so any settings-driven collection is correct.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings_desktop")

PROJECT = Path(os.getcwd())

# OneDrive renames the losing copy with the device name when this folder is
# synced from two machines. Add a suffix here for every device that syncs it.
CONFLICT_SUFFIXES = ("-Dr-Wasim", "-Home")

# Local Django apps that ship templates / static / migrations.
# NOTE: keep in sync with INSTALLED_APPS in bgddr/settings.py. Django imports
# apps dynamically (importlib), so PyInstaller's static analysis will NOT find
# an app's submodules on its own — anything left out of this list can build
# "successfully" and still crash (or silently drop its templates) at runtime.
LOCAL_APPS = [
    "bgddr", "patients", "encounters", "baseline", "labs", "pathology",
    "treatments", "prescriptions", "analytics", "audit", "studies", "safety",
    "scheduling", "biomarkers", "users", "exports", "api", "clinic",
    # GDES clinical decision support + later phases
    "clinical", "knowledge", "timeline", "reminders", "fhir", "events",
    "clinical_reasoning", "followup",
    "feedback",
    # Vera Health integration (auth + the guarded auto-paste). This was missing
    # until 7.3.12, so no packaged build shipped its loose .py files.
    "clinical_evidence",
    # "auth" is NOT in INSTALLED_APPS — it is a bare module included directly by
    # bgddr/urls.py (path("auth/", include("auth.urls"))). Nothing else imports it,
    # so PyInstaller left it out of 7.3.12 and EVERY request 500'd with
    # ModuleNotFoundError: No module named 'auth' (the URLconf failed to import).
    # Keep it listed here even though it is not a Django app.
    "auth",
    # Same situation: bgddr/urls.py includes decision.urls (legacy evaluate_case
    # endpoints) but "decision" is not in INSTALLED_APPS, so it too was omitted.
    "decision",
]
# Guard: every local Django app must be listed above, or its templates and
# loose .py files are silently dropped from the build.
def _check_local_apps_cover_installed_apps():
    import ast
    settings_py = PROJECT / "bgddr" / "settings.py"
    try:
        tree = ast.parse(settings_py.read_text(encoding="utf-8"))
    except Exception:
        return
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign)
                and any(getattr(t, "id", "") == "INSTALLED_APPS" for t in node.targets)):
            continue
        for element in getattr(node.value, "elts", []):
            name = getattr(element, "value", None)
            if not isinstance(name, str):
                continue
            root = name.split(".")[0]
            if (PROJECT / root / "__init__.py").exists() and root not in LOCAL_APPS:
                print(f"BGDDR.spec WARNING: local app {root!r} is in INSTALLED_APPS "
                      f"but not in LOCAL_APPS — its files will not be bundled.")
_check_local_apps_cover_installed_apps()

# Third-party packages whose Python submodules must be fully bundled.
THIRD_PARTY = [
    # Shared clinical intelligence (CKD-EPI 2021 eGFR, KDIGO grid, renal dose).
    # labs/services/egfr.py is a thin shim over this, so leaving it out packages
    # an app that cannot compute an eGFR -- and eGFR drives CKD staging, the
    # outcome endpoints and the dosing checks.
    "gdes_core",
    "django", "rest_framework", "jazzmin", "whitenoise", "waitress",
    "openpyxl", "et_xmlfile",
    # SPSS .sav export (pyreadstat is a compiled extension on top of pandas).
    "pyreadstat", "pandas", "numpy", "dateutil", "pytz",
    # Background tasks — Celery's Django fixup & kombuserialisation.
    "celery", "kombu", "billiard", "vine",
    # Security headers (INSTALLED_APPS + MIDDLEWARE) and login rate limiting.
    # Missing from the 7.4.0 build candidate: Django could not start at all.
    "csp", "django_ratelimit",
]

# --- Build-time guard -------------------------------------------------------
# Every third-party package named in settings (INSTALLED_APPS, MIDDLEWARE,
# backends...) must be bundled, or Django cannot start. The self-check caught
# csp / django_ratelimit only after a full build; fail here instead.
def _check_settings_packages_are_bundled():
    import ast
    import importlib.util
    import sys as _sys
    tree = ast.parse((PROJECT / "bgddr" / "settings.py").read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        value = getattr(node, "value", None)
        dotted = r"[a-z_][a-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+"
        if (isinstance(node, ast.Constant) and isinstance(value, str)
                and _re_settings.fullmatch(dotted, value)):
            roots.add(value.split(".")[0])
    stdlib = set(getattr(_sys, "stdlib_module_names", ()))
    missing = sorted(r for r in roots
                     if r not in THIRD_PARTY and r not in LOCAL_APPS and r not in stdlib
                     and r != "bgddr" and importlib.util.find_spec(r) is not None)
    if missing:
        raise SystemExit(
            f"BGDDR.spec: settings.py uses {missing}, which are not in THIRD_PARTY. "
            "Add them, or the packaged app cannot start.")
import re as _re_settings
_check_settings_packages_are_bundled()

# --- Build-time guard -------------------------------------------------------
# Every module that bgddr/urls.py pulls in via include("<mod>.urls") MUST be in
# LOCAL_APPS, or PyInstaller silently omits it and EVERY request 500s at runtime
# with ModuleNotFoundError while importing the URLconf. This bit 7.3.12 (the bare
# "auth" module, which is not in INSTALLED_APPS so app-based checks miss it).
# Fail the build here instead of shipping a broken exe.
import re as _re
_urls_src = (PROJECT / "bgddr" / "urls.py").read_text(encoding="utf-8")
_included = set(_re.findall(r'include\(\s*["\']([\w_]+)\.urls["\']', _urls_src))
_missing = sorted(m for m in _included if m not in LOCAL_APPS)
if _missing:
    raise SystemExit(
        "BGDDR.spec: bgddr/urls.py includes these modules that are NOT in "
        f"LOCAL_APPS: {_missing}. Add them to LOCAL_APPS, or the packaged app "
        "will 500 on every request."
    )

# Collect everything: modules, data files, and binaries for all packages.
hiddenimports = []
datas = []
binaries = []
for pkg in THIRD_PARTY + LOCAL_APPS:
    app_datas, app_bins, app_his = _collect_all(pkg)
    hiddenimports += app_his
    datas += app_datas
    binaries += app_bins
# Database backends + management are imported lazily by name.
hiddenimports += [
    "django.db.backends.sqlite3",
    "django.db.backends.sqlite3.base",
    "django.db.backends.postgresql",
    "bgddr.settings_desktop",
]

# pyreadstat ships compiled .pyd/.dll binaries that must be collected explicitly.
binaries += collect_dynamic_libs("pyreadstat")
datas += collect_data_files("django")        # admin/auth templates & static
datas += collect_data_files("rest_framework")
datas += collect_data_files("jazzmin")

# Project-level templates and compiled static assets.
for rel in ("templates", "static"):
    src = PROJECT / rel
    if src.is_dir():
        datas.append((str(src), rel))

# Each app's templates/ and static/ folders.
for app in LOCAL_APPS:
    for rel in ("templates", "static"):
        src = PROJECT / app / rel
        if src.is_dir():
            datas.append((str(src), f"{app}/{rel}"))

# Clinical documentation for the desktop package.
for rel in ("docs",):
    src = PROJECT / rel
    if src.is_dir():
        datas.append((str(src), rel))

# settings_desktop is now synthesised at runtime by launcher._ensure_settings_desktop()
# — no need to bundle the .py file, which caused import conflicts in the PYZ.

# NUCLEAR OPTION: copy every .py file from each local app into _internal/ so
# Django can find them at runtime even if PyInstaller's PYZ analysis dropped
# the compiled bytecode.  This costs ~5 MB extra and guarantees availability.
import fnmatch as _fnmatch
for app in LOCAL_APPS:
    app_dir = PROJECT / app
    if not app_dir.is_dir():
        continue
    for py_file in app_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        # OneDrive conflict copies ("version-Dr-Wasim.py") are stale duplicates;
        # bundling them ships dead code and bloats every clinic PC's download.
        if any(suffix in py_file.name for suffix in CONFLICT_SUFFIXES):
            continue
        rel = py_file.relative_to(PROJECT)
        datas.append((str(py_file), str(rel.parent)))

block_cipher = None

a = Analysis(
    [str(PROJECT / "desktop" / "launcher.py")],
    pathex=[str(PROJECT), str(PROJECT / "desktop")],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "test", "tests",
              "pandas.tests", "numpy.tests", "numpy.typing.tests",
              "scipy.tests", "celery.contrib.pytest", "kombu.tests"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GDES",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                       # no console window for normal use
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GDES",
)
