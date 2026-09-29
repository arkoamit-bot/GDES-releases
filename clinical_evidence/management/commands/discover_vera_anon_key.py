"""Management command to help discover the Vera Health Supabase anon key.

Usage:
    python manage.py discover_vera_anon_key

This command checks known locations where the Supabase anon key may be
stored and provides instructions for the user to find it in their browser
if not found automatically.

The anon key is required by the VeraWebSessionProvider to authenticate
via Supabase Auth at auth.verahealth.ai.
"""

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Discover the Vera Health Supabase anon key for web session auth"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(
            "Searching for Vera Health Supabase anon key...\n"
        ))

        key = self._check_env()
        if key:
            self._show_key(key, "VERA_SUPABASE_ANON_KEY environment variable")
            return

        key = self._check_vera_config()
        if key:
            self._show_key(key, "Vera ProviderConfiguration")
            return

        self._show_instructions()

    def _check_env(self) -> str | None:
        import os
        return os.environ.get("VERA_SUPABASE_ANON_KEY")

    def _check_vera_config(self) -> str | None:
        try:
            from clinical_evidence.models import ProviderConfiguration
            configs = ProviderConfiguration.objects.filter(
                provider_type="vera_web",
            )
            for config in configs:
                anon = config.extra_config.get("supabase_anon_key")
                if anon:
                    return anon
        except Exception:
            pass
        return None

    def _show_key(self, key: str, source: str):
        self.stdout.write(self.style.SUCCESS(f"Found anon key in: {source}"))
        self.stdout.write(f"\nAnon key: {key}\n")
        self.stdout.write(self.style.WARNING(
            "To configure VeraWebSessionProvider:\n"
            "  python manage.py seed_vera_web_provider"
        ))

    def _show_instructions(self):
        self.stdout.write(self.style.WARNING(
            "Supabase anon key not found in environment or database.\n"
        ))
        self.stdout.write(
            "To find it manually:\n"
            "\n"
            "  1. Open Vera Health in Chrome/Edge and log in.\n"
            "  2. Press F12 (DevTools) -> Application -> Local Storage.\n"
            "  3. Look for key: 'sb-eqrfvjm8-auth-token'.\n"
            "  4. Parse the JSON value; it contains access_token, etc.\n"
            "     The anon key is NOT in localStorage. You need to find it\n"
            "     in the page source or network requests.\n"
            "\n"
            "  Alternative: Use Chrome DevTools > Network tab.\n"
            "  1. Log in to Vera Health.\n"
            "  2. In Network tab, filter by 'auth.verahealth.ai'.\n"
            "  3. Click any request to see request headers.\n"
            "  4. Copy the 'apikey' header value.\n"
        )
        self.stdout.write(self.style.SUCCESS(
            "Once you have the key, set it:\n"
            "  export VERA_SUPABASE_ANON_KEY='your_key_here'\n"
        ))
