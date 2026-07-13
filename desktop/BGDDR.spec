# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the BGDDR single-user Windows desktop build.

Build from the project root:

    pyinstaller desktop/BGDDR.spec --noconfirm

Produces  dist/BGDDR/BGDDR.exe  plus its support files. Copy the dist/BGDDR
folder to where the user wants it (e.g. inside OneDrive); db.sqlite3, Backups/,
Exports/, Media/ and Logs/ are created next to BGDDR.exe on first run.
"""
import os
from pathlib import Path

from PyInstaller.utils.hooks import (collect_submodules, collect_data_files,
                                     collect_dynamic_libs)

# Build with the desktop settings so any settings-driven collection is correct.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings_desktop")

PROJECT = Path(os.getcwd())

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
]

# Third-party packages whose Python submodules must be fully bundled.
THIRD_PARTY = [
    "django", "rest_framework", "jazzmin", "whitenoise", "waitress",
    "openpyxl", "et_xmlfile",
    # SPSS .sav export (pyreadstat is a compiled extension on top of pandas).
    "pyreadstat", "pandas", "numpy", "dateutil", "pytz",
    # Background tasks — Celery's Django fixup & kombuserialisation.
    "celery", "kombu", "billiard", "vine",
]

hiddenimports = []
for pkg in THIRD_PARTY + LOCAL_APPS:
    hiddenimports += collect_submodules(pkg)
# Database backends + management are imported lazily by name.
hiddenimports += [
    "django.db.backends.sqlite3",
    "django.db.backends.sqlite3.base",
    "django.db.backends.postgresql",
]

# pyreadstat ships compiled .pyd/.dll binaries that must be collected explicitly.
binaries = collect_dynamic_libs("pyreadstat")

# --- Data files (templates, static, locale, migrations as data too) --------
datas = []
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
    excludes=["tkinter.test", "test", "tests"],
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
    name="BGDDR",
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
    name="BGDDR",
)
