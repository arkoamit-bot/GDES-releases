# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for a SINGLE-FILE portable BGDDR build.

*** NON-PILOT (P2-1) ***
Do NOT use this for the clinical pilot. The pilot ships the ONEDIR build
(desktop/BGDDR.spec via desktop/build_exe.ps1): faster startup, no per-launch
temp extraction, and friendlier to antivirus and the WebView2 runtime. This
onefile spec is kept only for ad-hoc portable demos.

Build from the project root:

    pyinstaller desktop/BGDDR_onefile.spec --noconfirm

Produces ONE file: dist/BGDDR.exe — everything (Python, Django, all apps,
templates, static, pandas/pyreadstat) is bundled inside it. Copy that single
exe anywhere and run it; db.sqlite3, Backups/, Exports/, Media/ and Logs/ are
created next to the exe on first run.

Trade-off vs the folder build: one-file is more convenient to share, but starts
a little slower (it unpacks to a temp folder on each launch).
"""
import os
from pathlib import Path

from PyInstaller.utils.hooks import (collect_submodules, collect_data_files,
                                     collect_dynamic_libs)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bgddr.settings_desktop")

PROJECT = Path(os.getcwd())

LOCAL_APPS = [
    "bgddr", "patients", "encounters", "baseline", "labs", "pathology",
    "treatments", "prescriptions", "analytics", "audit", "studies", "safety",
    "scheduling", "biomarkers", "users", "exports", "api", "clinic",
]

THIRD_PARTY = [
    "django", "rest_framework", "jazzmin", "whitenoise", "waitress",
    "openpyxl", "et_xmlfile",
    "pyreadstat", "pandas", "numpy", "dateutil", "pytz",
]

hiddenimports = []
for pkg in THIRD_PARTY + LOCAL_APPS:
    hiddenimports += collect_submodules(pkg)
hiddenimports += [
    "django.db.backends.sqlite3",
    "django.db.backends.sqlite3.base",
    "django.db.backends.postgresql",
]

binaries = collect_dynamic_libs("pyreadstat")

datas = []
datas += collect_data_files("django")
datas += collect_data_files("rest_framework")
datas += collect_data_files("jazzmin")
for rel in ("templates", "static"):
    src = PROJECT / rel
    if src.is_dir():
        datas.append((str(src), rel))
for app in LOCAL_APPS:
    for rel in ("templates", "static"):
        src = PROJECT / app / rel
        if src.is_dir():
            datas.append((str(src), f"{app}/{rel}"))

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

# ONE-FILE: bundle binaries + zipfiles + datas directly into the EXE, no COLLECT.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="BGDDR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
