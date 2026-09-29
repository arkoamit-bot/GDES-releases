"""
Seed the Vera Health AI provider configuration.

Reads credentials from environment variables and creates (or updates) the
ProviderConfiguration row for Vera Health, then runs an authentication check.

Environment variables used:
  VERAHEALTH_API_KEY       — API key (preferred)
  VERA_API_KEY             — Fallback API key
  VERAHEALTH_API_BASE_URL  — Base URL (default: https://api.verahealth.ai/v1)
  VERAHEALTH_MODEL         — Model version (default: vera-clinical-1)

Usage:
    python manage.py seed_vera_provider
    python manage.py seed_vera_provider --api-key=sk-xxxxx
    python manage.py seed_vera_provider --priority=5 --disable
"""
import os

from django.core.management.base import BaseCommand

from clinical_evidence.models import ProviderConfiguration


class Command(BaseCommand):
    help = "Create or update the Vera Health AI provider configuration."

    def add_arguments(self, parser):
        parser.add_argument("--api-key", type=str, default="",
                            help="Vera Health API key (overrides env vars)")
        parser.add_argument("--api-base-url", type=str, default="",
                            help="API base URL (overrides env var / default)")
        parser.add_argument("--model", type=str, default="",
                            help="Model name (overrides env var / default)")
        parser.add_argument("--priority", type=int, default=1,
                            help="Provider priority (lower = queried first, default: 1)")
        parser.add_argument("--disable", action="store_true",
                            help="Disable the provider after creating")
        parser.add_argument("--no-auth-check", action="store_true",
                            help="Skip authentication check")

    def handle(self, *args, **options):
        api_key = (
            options["api_key"]
            or os.environ.get("VERAHEALTH_API_KEY")
            or os.environ.get("VERA_API_KEY", "")
        )
        api_base_url = (
            options["api_base_url"]
            or os.environ.get("VERAHEALTH_API_BASE_URL", "https://api.verahealth.ai/v1")
        )
        model = (
            options["model"]
            or os.environ.get("VERAHEALTH_MODEL", "vera-clinical-1")
        )
        priority = options["priority"]
        is_enabled = not options["disable"]

        if not api_key:
            self.stdout.write(self.style.WARNING(
                "No API key found. Set VERAHEALTH_API_KEY env var or pass --api-key."
            ))
            return

        config, created = ProviderConfiguration.objects.update_or_create(
            provider_type="vera",
            defaults={
                "is_enabled": is_enabled,
                "priority": priority,
                "api_key_encrypted": api_key,
                "api_base_url": api_base_url,
                "extra_config": {"model": model},
                "rate_limit_per_minute": 60,
                "max_retries": 3,
                "timeout_seconds": 60,
            },
        )

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f"{action} Vera Health provider configuration "
            f"(priority={priority}, enabled={is_enabled})."
        ))

        if not options["no_auth_check"] and is_enabled:
            self._check_auth(config)

    def _check_auth(self, config: ProviderConfiguration) -> None:
        from clinical_evidence.services.orchestrator import get_provider_instance

        self.stdout.write("  Checking authentication... ", ending="")
        try:
            instance = get_provider_instance(config)
            instance.authenticate()
            self.stdout.write(self.style.SUCCESS("OK"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR("FAILED"))
            self.stdout.write(self.style.ERROR(f"  {exc}"))
