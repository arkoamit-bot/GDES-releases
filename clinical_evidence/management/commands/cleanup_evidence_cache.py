"""
Remove expired evidence cache entries.

    python manage.py cleanup_evidence_cache
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from clinical_evidence.models import EvidenceCache


class Command(BaseCommand):
    help = "Remove expired evidence cache entries."

    def handle(self, *args, **options):
        now = timezone.now()
        deleted, _ = EvidenceCache.objects.filter(expires_at__lte=now).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} expired cache entries."))
