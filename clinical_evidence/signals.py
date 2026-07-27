"""Signal handlers for the Clinical Evidence Intelligence module."""

import logging
import os

from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger("bgddr.evidence.signals")


@receiver(post_migrate, sender=None)
def auto_seed_vera_provider(sender, **kwargs):
    """Auto-seed the Vera Health provider configuration after migration.

    Only runs if:
      - The clinical_evidence app was just migrated.
      - The VERAHEALTH_API_KEY env var is set.
      - No ProviderConfiguration for 'vera' exists yet.
    """
    app_label = getattr(sender, "label", "")
    if app_label != "clinical_evidence":
        return

    api_key = os.environ.get("VERAHEALTH_API_KEY") or os.environ.get("VERA_API_KEY", "")
    if not api_key:
        return

    from clinical_evidence.models import ProviderConfiguration

    if ProviderConfiguration.objects.filter(provider_type="vera").exists():
        logger.debug("Vera Health provider already configured, skipping auto-seed.")
        return

    ProviderConfiguration.objects.create(
        provider_type="vera",
        is_enabled=True,
        priority=1,
        api_key_encrypted=api_key,
        api_base_url=os.environ.get(
            "VERAHEALTH_API_BASE_URL", "https://api.verahealth.ai/v1",
        ),
        extra_config={
            "model": os.environ.get("VERAHEALTH_MODEL", "vera-clinical-1"),
        },
        rate_limit_per_minute=60,
        max_retries=3,
        timeout_seconds=60,
    )
    logger.info("Auto-seeded Vera Health provider from VERAHEALTH_API_KEY env var.")
