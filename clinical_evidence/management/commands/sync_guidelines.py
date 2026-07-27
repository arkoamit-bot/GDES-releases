"""
Sync guideline recommendations from a JSON file or API endpoint.

    python manage.py sync_guidelines path/to/guidelines.json
    python manage.py sync_guidelines --source=KDIGO --year=2024
"""
import json
import os

from django.core.management.base import BaseCommand, CommandError

from clinical_evidence.constants import VALIDATION_SOURCES
from clinical_evidence.models import GuidelineRecommendation


class Command(BaseCommand):
    help = "Import / sync guideline recommendations for evidence validation."

    def add_arguments(self, parser):
        parser.add_argument("filepath", nargs="?", type=str, default="",
                            help="Path to JSON file with recommendations")
        parser.add_argument("--source", type=str, default="",
                            help="Guideline source abbreviation (e.g. KDIGO)")
        parser.add_argument("--year", type=int, default=0, help="Publication year")
        parser.add_argument("--dry-run", action="store_true", help="Validate without importing")

    def handle(self, *args, **options):
        filepath = options["filepath"]
        source = options["source"]
        year = options["year"]
        dry_run = options["dry_run"]

        if filepath:
            if not os.path.exists(filepath):
                raise CommandError(f"File not found: {filepath}")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            recommendations = data if isinstance(data, list) else data.get("recommendations", [])
        elif source:
            recommendations = self._fetch_from_source(source, year)
        else:
            raise CommandError("Provide a filepath or --source.")

        created = 0
        updated = 0
        errors = 0

        for rec in recommendations:
            try:
                rec_id = rec.get("recommendation_id") or rec.get("id")
                if not rec_id:
                    errors += 1
                    continue
                defaults = {
                    "disease_id": rec.get("disease_id", ""),
                    "title": rec.get("title", ""),
                    "recommendation_text": rec.get("recommendation_text", ""),
                    "evidence_grade": rec.get("evidence_grade", ""),
                    "recommendation_strength": rec.get("recommendation_strength", ""),
                    "guideline_version": rec.get("guideline_version", ""),
                    "publication_date": rec.get("publication_date"),
                    "review_date": rec.get("review_date"),
                    "url": rec.get("url", ""),
                    "keywords": rec.get("keywords", []),
                    "is_active": rec.get("is_active", True),
                }
                if dry_run:
                    continue
                _, was_created = GuidelineRecommendation.objects.update_or_create(
                    recommendation_id=rec_id,
                    guideline_source=rec.get("guideline_source", source),
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Error: {exc}"))
                errors += 1

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"Dry run: {len(recommendations)} recommendations validated, "
                f"{errors} errors."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"{created} created, {updated} updated, {errors} errors."
            ))

    def _fetch_from_source(self, source: str, year: int) -> list[dict]:
        choices = dict(VALIDATION_SOURCES)
        if source not in choices:
            raise CommandError(f"Unknown source '{source}'. Choices: {', '.join(choices)}")
        return []
