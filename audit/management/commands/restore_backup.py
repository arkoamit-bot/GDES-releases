"""Restore the live database from a backup archive (P1-1).

    python manage.py restore_backup <path-to-backup.zip>
    python manage.py restore_backup --list

Restores from a ZIP archive (tiered backups) or a legacy .sqlite3 snapshot.
A defensive backup of the current DB is taken first, and the archive is
integrity-checked before it is swapped in — a corrupt archive never overwrites
the live database.
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restore the database from a backup ZIP (or legacy .sqlite3 snapshot)."

    def add_arguments(self, parser):
        parser.add_argument("archive", nargs="?", help="Path to a .zip or .sqlite3 backup")
        parser.add_argument("--list", action="store_true",
                            help="List available tiered backups and exit")
        parser.add_argument("--yes", action="store_true",
                            help="Skip the confirmation prompt (non-interactive)")

    def handle(self, *args, **options):
        from django.conf import settings
        from bgddr import backup as backup_mod

        base = Path(backup_mod._backup_dir())

        if options["list"]:
            found = False
            for tier in ("Daily", "Weekly", "Monthly"):
                tier_dir = base / tier
                zips = sorted(tier_dir.glob("*.zip"), reverse=True) if tier_dir.is_dir() else []
                if zips:
                    found = True
                    self.stdout.write(self.style.MIGRATE_HEADING(f"{tier}:"))
                    for z in zips:
                        self.stdout.write(f"  {z}")
            if not found:
                self.stdout.write("No tiered backups found under " + str(base))
            return

        archive = options.get("archive")
        if not archive:
            raise CommandError("Provide a backup path, or use --list.")
        archive_path = Path(archive)
        if not archive_path.exists():
            raise CommandError(f"Backup not found: {archive_path}")

        if not options["yes"]:
            self.stdout.write(self.style.WARNING(
                f"This will OVERWRITE the live database at "
                f"{settings.DATABASES['default']['NAME']} with:\n  {archive_path}\n"
                "A safety backup of the current DB will be taken first."
            ))
            confirm = input("Type 'yes' to proceed: ").strip().lower()
            if confirm != "yes":
                self.stdout.write("Aborted.")
                return

        if archive_path.suffix.lower() == ".zip":
            ok = backup_mod.restore_zip_backup(archive_path)
        else:
            ok = backup_mod.restore_from_backup(archive_path)

        if ok:
            self.stdout.write(self.style.SUCCESS(f"Database restored from {archive_path.name}."))
        else:
            raise CommandError("Restore failed — see backup.log. The live database was not changed.")
