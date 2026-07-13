"""
Restore the database from a timestamped backup (single-user desktop deployment).

    python manage.py restore_db --list                 # show restorable backups
    python manage.py restore_db <name|path> --yes       # restore (overwrites DB)

A safety snapshot of the current database is taken automatically before the
restore (reason "pre_restore"), so a mistaken restore is itself reversible.
Stop the application before restoring so nothing is mid-write.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bgddr.backup import list_backups, restore_from_backup


class Command(BaseCommand):
    help = "Restore the database from a backup file (overwrites the current DB)."

    def add_arguments(self, parser):
        parser.add_argument("backup", nargs="?",
                            help="Backup filename (in Backups/) or full path.")
        parser.add_argument("--list", action="store_true",
                            help="List restorable backups and exit.")
        parser.add_argument("--yes", action="store_true",
                            help="Skip the confirmation prompt.")

    def handle(self, *args, **opts):
        backups = list_backups()
        if opts["list"] or not opts["backup"]:
            if not backups:
                self.stdout.write("No backups found.")
                return
            self.stdout.write("Restorable backups (newest first):")
            for b in backups:
                self.stdout.write(f"  {b['created'][:19]}  [{b['reason']}]  {b['name']}")
            if not opts["backup"]:
                self.stdout.write("\nRe-run with:  python manage.py restore_db <name> --yes")
            return

        # Resolve the backup: accept a bare filename (look in Backups/) or a path.
        target = Path(opts["backup"])
        if not target.exists():
            target = Path(settings.BACKUP_CONFIG["directory"]) / opts["backup"]
        if not target.exists():
            raise CommandError(f"Backup not found: {opts['backup']}")

        if not opts["yes"]:
            self.stdout.write(self.style.WARNING(
                f"This OVERWRITES the current database with:\n  {target.name}\n"
                "A pre-restore safety backup will be taken first.\n"
                "Re-run with --yes to proceed."))
            return

        if restore_from_backup(target):
            self.stdout.write(self.style.SUCCESS(
                f"Database restored from {target.name}. Restart the application."))
        else:
            raise CommandError("Restore failed — see Logs/bgddr.log.")
