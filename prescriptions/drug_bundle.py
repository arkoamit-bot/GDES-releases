"""Apply the drug list shipped in the app, once per bundle version.

An app update replaces code, not the database, so a newer drug list in
``prescriptions/data/dkdr_drugs.csv.gz`` would never reach an installed PC on
its own. The launcher (and ``server_init``) call :func:`apply_if_newer` after
migrations: it imports the bundle when its version is newer than the one
stamped in the data directory, then stamps it, so ordinary relaunches do
nothing.

The import is additive and runs in one transaction (see ``import_dkdr_drugs``);
``reclassify_drug_classes --apply`` then corrects the drug classes an older
importer got wrong. A failure is logged and leaves the stamp alone, so the next
launch tries again.
"""
from __future__ import annotations

from pathlib import Path

# Bump when prescriptions/data/dkdr_drugs.csv.gz is regenerated, and also when
# the import reads it differently -- 2026.09.30.1 re-applies the same file now
# that the importer takes routes from each product's dosage form, so an
# installed PC stops offering an injection-only drug as oral.
BUNDLE_VERSION = "2026.09.30.2"

_STAMP_NAME = ".drug_bundle_version"


def _stamp_path() -> Path:
    from django.conf import settings
    return Path(getattr(settings, "BGDDR_DATA_DIR", settings.BASE_DIR)) / _STAMP_NAME


def installed_version() -> str | None:
    p = _stamp_path()
    try:
        if p.exists():
            return p.read_text(encoding="utf-8").strip() or None
    except OSError:
        pass
    return None


def should_apply() -> bool:
    from prescriptions.management.commands.import_dkdr_drugs import BUNDLE_PATH
    if not BUNDLE_PATH.exists():
        return False
    return (installed_version() or "") < BUNDLE_VERSION


def apply_if_newer(log=print, stdout=None, stderr=None) -> bool:
    """Import the shipped drug list if it is newer. Returns True if applied."""
    if not should_apply():
        return False
    from django.core.management import call_command
    log(f"Updating the drug list (installed={installed_version() or 'none'} "
        f"-> {BUNDLE_VERSION}); this can take a minute ...")
    kwargs = {"stdout": stdout, "stderr": stderr} if stdout is not None else {}
    call_command("import_dkdr_drugs", "--bundle", "--create-generics",
                 "--fold-salts", **kwargs)
    call_command("reclassify_drug_classes", "--apply", **kwargs)
    try:
        _stamp_path().write_text(BUNDLE_VERSION, encoding="utf-8")
    except OSError as exc:
        log(f"  (could not stamp drug list version: {exc})")
    return True
