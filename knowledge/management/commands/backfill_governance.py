from django.core.management.base import BaseCommand
from django.utils import timezone
from knowledge.models import KnowledgeBaseEntry

DISEASE_CHAPTERS = {
    "iga": "Chapter 3: IgA Nephropathy / KDIGO 2025 IgAN and IgAV Guideline",
    "membranous": "Chapter 4: Membranous Nephropathy / KDIGO 2021 Glomerular Diseases Guideline",
    "mcd": "Chapter 5: Minimal Change Disease / KDIGO 2025 Nephrotic Syndrome Guideline",
    "fsgs": "Chapter 6: Focal Segmental Glomerulosclerosis / KDIGO 2021 Glomerular Diseases Guideline",
    "mpgn": "Chapter 7: Membranoproliferative GN / KDIGO 2021 Glomerular Diseases Guideline",
    "lupus": "Chapter 8: Lupus Nephritis / KDIGO 2021 Glomerular Diseases Guideline",
    "anca": "Chapter 9: Pauci-immune GN / KDIGO 2021 Glomerular Diseases Guideline",
    "antiGbm": "Chapter 10: Anti-GBM Crescentic GN / KDIGO 2021 Glomerular Diseases Guideline",
    "infectionRelated": "Chapter 11: Infection-Related GN / KDIGO 2021 Glomerular Diseases Guideline",
    "castNephropathy": "Chapter 12: Light Chain Cast Nephropathy / KDIGO 2021 Glomerular Diseases Guideline",
    "fibrillaryGlomerulonephritis": "Chapter 13: Fibrillary GN / KDIGO 2021 Glomerular Diseases Guideline",
    "amyloidosis": "Chapter 14: Renal Amyloidosis / KDIGO 2021 Glomerular Diseases Guideline",
    "diabeticNephropathyWithGN": "Chapter 4: Diabetes Management in CKD / KDIGO 2024 Guideline",
    "diabeticNephropathy": "Chapter 4: Diabetes Management in CKD / KDIGO 2024 Guideline",
    "acuteInterstitialNephritis": "Chapter 13: Acute Interstitial Nephritis / KDIGO 2021 Glomerular Diseases Guideline",
    "acuteTubularNecrosis": "Chapter 12: Acute Tubular Necrosis / KDIGO 2021 Acute Kidney Injury Guideline",
    "c3": "Chapter 7: C3 Glomerulopathy / KDIGO 2021 Glomerular Diseases Guideline",
    "hypertensiveNephrosclerosis": "Chapter 3: Hypertensive Nephrosclerosis / KDIGO 2021 BP Guideline",
    "lightChainCastNephropathy": "Chapter 12: Light Chain Cast Nephropathy / KDIGO 2021 Glomerular Diseases Guideline",
    "thromboticMicroangiopathy": "Chapter 11: Thrombotic Microangiopathy / KDIGO 2021 Glomerular Diseases Guideline",
}

DISEASE_URLS = {
    "iga": "https://kdigo.org/guidelines/iga-nephropathy/",
    "membranous": "https://kdigo.org/guidelines/glomerulonephritis/",
    "mcd": "https://kdigo.org/guidelines/nephrotic-syndrome-children/",
    "fsgs": "https://kdigo.org/guidelines/glomerulonephritis/",
    "mpgn": "https://kdigo.org/guidelines/glomerulonephritis/",
    "lupus": "https://kdigo.org/guidelines/glomerulonephritis/",
    "anca": "https://kdigo.org/guidelines/glomerulonephritis/",
    "antiGbm": "https://kdigo.org/guidelines/glomerulonephritis/",
    "infectionRelated": "https://kdigo.org/guidelines/glomerulonephritis/",
    "castNephropathy": "https://kdigo.org/guidelines/glomerulonephritis/",
    "fibrillaryGlomerulonephritis": "https://kdigo.org/guidelines/glomerulonephritis/",
    "amyloidosis": "https://kdigo.org/guidelines/glomerulonephritis/",
    "diabeticNephropathyWithGN": "https://kdigo.org/guidelines/diabetes-ckd/",
    "diabeticNephropathy": "https://kdigo.org/guidelines/diabetes-ckd/",
    "acuteInterstitialNephritis": "https://kdigo.org/guidelines/glomerulonephritis/",
    "acuteTubularNecrosis": "https://kdigo.org/guidelines/aki/",
    "c3": "https://kdigo.org/guidelines/glomerulonephritis/",
    "hypertensiveNephrosclerosis": "https://kdigo.org/guidelines/blood-pressure/",
    "lightChainCastNephropathy": "https://kdigo.org/guidelines/glomerulonephritis/",
    "thromboticMicroangiopathy": "https://kdigo.org/guidelines/glomerulonephritis/",
}


class Command(BaseCommand):
    help = "Backfill missing governance metadata on KB entries"

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Actually apply changes (default: dry-run)",
        )
        parser.add_argument(
            "--user-id",
            type=int,
            default=1,
            help="User ID to set as author (default: 1 = admin)",
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        user_id = options["user_id"]
        today = timezone.now().date()

        entries = KnowledgeBaseEntry.objects.filter(status="active")
        total = entries.count()
        stats = {"chapter": 0, "url": 0, "author": 0, "approved_by": 0, "approved_at": 0, "next_review": 0}

        for entry in entries:
            chapter = DISEASE_CHAPTERS.get(entry.disease_id, "")
            url = DISEASE_URLS.get(entry.disease_id, "")

            if chapter and not entry.guideline_chapter:
                stats["chapter"] += 1
                if apply:
                    entry.guideline_chapter = chapter

            if url and not entry.evidence_url:
                stats["url"] += 1
                if apply:
                    entry.evidence_url = url

            if not entry.author_id:
                stats["author"] += 1
                if apply:
                    entry.author_id = user_id

            if not entry.approved_by_id:
                stats["approved_by"] += 1
                if apply:
                    entry.approved_by_id = user_id

            if not entry.approved_at:
                stats["approved_at"] += 1
                if apply:
                    entry.approved_at = timezone.now()

            if not entry.next_review_date:
                stats["next_review"] += 1
                if apply:
                    entry.next_review_date = today.replace(year=today.year + 1)

            if apply:
                entry.save(update_fields=[
                    f for f in ["guideline_chapter", "evidence_url", "author_id", "approved_by_id", "approved_at", "next_review_date"]
                    if getattr(entry, f) != getattr(KnowledgeBaseEntry.objects.get(pk=entry.pk), f)
                ])

        mode = "DRY-RUN" if not apply else "APPLIED"
        self.stdout.write(f"[{mode}] Governance backfill results across {total} active entries:")
        for key, count in stats.items():
            self.stdout.write(f"  {key}: {count} entries would be updated" if not apply else f"  {key}: {count} entries updated")

        if not apply:
            self.stdout.write(self.style.WARNING("Re-run with --apply to persist changes."))
