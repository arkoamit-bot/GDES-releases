"""
Create or list timestamped SQLite backups (single-user desktop deployment).

    python manage.py backup_db                  # create a "manual" backup
    python manage.py backup_db --reason nightly # tag the reason
    python manage.py backup_db --list           # list existing backups

Backups land in the Backups/ folder (BACKUP_CONFIG["directory"]), which is
OneDrive-safe (one self-contained file per snapshot). Retention is enforced
automatically (BACKUP_CONFIG["max_backups"]).
"""
from django.core.management.base import BaseCommand

from bgddr.backup import create_backup, list_backups


class Command(BaseCommand):
    help = "Create a timestamped backup of the database (or list existing backups)."

    def add_arguments(self, parser):
        parser.add_argument("--reason", default="manual",
                            help="Short tag stored in the backup filename.")
        parser.add_argument("--list", action="store_true",
                            help="List existing backups instead of creating one.")

    def handle(self, *args, **opts):
        if opts["list"]:
            backups = list_backups()
            if not backups:
                self.stdout.write("No backups found.")
                return
            self.stdout.write(f"{len(backups)} backup(s):")
            for b in backups:
                self.stdout.write(
                    f"  {b['created'][:19]}  {b['size_mb']:>6.2f} MB  "
                    f"[{b['reason']}]  {b['name']}")
            return

        path = create_backup(reason=opts["reason"])
        if path:
            self.stdout.write(self.style.SUCCESS(f"Backup created: {path}"))
        else:
            self.stderr.write(self.style.ERROR(
                "Backup failed (database file not found?). See Logs/bgddr.log."))
