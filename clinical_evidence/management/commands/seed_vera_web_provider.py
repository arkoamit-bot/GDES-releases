"""Management command to create/update a VeraWebSessionProvider configuration.

Usage:
    python manage.py seed_vera_web_provider
        --email doctor@example.com
        --password supersecret
        --anon-key "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

Optional:
    --no-auth-check    Skip authentication test after seeding
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Seed the Vera Web session provider configuration"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Vera Health account email")
        parser.add_argument("--password", required=True, help="Vera Health account password")
        parser.add_argument("--anon-key", required=True, help="Supabase anon key for auth.verahealth.ai")
        parser.add_argument("--no-auth-check", action="store_true", help="Skip auth test")

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]
        anon_key = options["anon_key"]
        no_auth_check = options["no_auth_check"]

        from clinical_evidence.models import ProviderConfiguration

        config, created = ProviderConfiguration.objects.update_or_create(
            provider_type="vera_web",
            defaults={
                "display_name": "Vera Health Web Session",
                "description": (
                    f"Vera Health web session auth. "
                    f"User: {email}"
                ),
                "is_enabled": True,
                "priority": 5,
                "max_retries": 3,
                "timeout_seconds": 60,
                "extra_config": {
                    "vera_web_email": email,
                    "vera_web_password": password,
                    "supabase_anon_key": anon_key,
                },
            },
        )

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f"{action} VeraWebSessionProvider configuration (ID: {config.id})"
        ))

        if not no_auth_check:
            self.stdout.write("Testing authentication...")
            try:
                from clinical_evidence.services.orchestrator import get_provider_instance
                instance = get_provider_instance(config)
                if instance.authenticate():
                    self.stdout.write(self.style.SUCCESS("Authentication successful!"))
                else:
                    self.stdout.write(self.style.WARNING("Authentication returned False"))
            except Exception as exc:
                raise CommandError(f"Authentication failed: {exc}")
