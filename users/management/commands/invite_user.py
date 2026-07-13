"""
Create an invitation to join the BGDDR registry.

Usage:
    python manage.py invite_user doctor@birdem.org --role investigator
    python manage.py invite_user patho@birdem.org --role pathologist --first "Dr." --last "Rahman"

The command prints the invitation acceptance URL for the admin to copy/share.
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from users.models import Invitation


class Command(BaseCommand):
    help = "Invite a user to the BGDDR registry by email."

    def add_arguments(self, parser):
        parser.add_argument("email", help="Email address of the invitee")
        parser.add_argument("--role", default="readonly",
                            choices=["data_manager", "statistician", "readonly",
                                     "coordinator", "investigator", "pathologist"],
                            help="Registry role (default: readonly)")
        parser.add_argument("--first", default="", help="First name")
        parser.add_argument("--last", default="", help="Last name")
        parser.add_argument("--by", default=None, help="Username of the inviter (admin)")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise CommandError(f"A user with email '{email}' already exists.")

        inviter = None
        if options["by"]:
            try:
                inviter = User.objects.get(username=options["by"])
            except User.DoesNotExist:
                raise CommandError(f"Inviter '{options['by']}' not found.")

        inv = Invitation.create(email=email, role=options["role"], created_by=inviter)
        self.stdout.write(self.style.SUCCESS(f"Invitation created for {email} ({options['role']})."))
        self.stdout.write(f"Token: {inv.token}")
        self.stdout.write(
            self.style.HTTP_INFO(
                f"Accept URL: /invitation/{inv.token}/"))
        self.stdout.write(
            "Share this URL with the invitee. It expires in 7 days.")
