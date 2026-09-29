"""Collapse duplicate recommendation-audit rows written before the trail was idempotent.

The recommendation generators run on every page render, and create_audit_record
used to write a new row each time. One patient accumulated 44 rows for 8 distinct
recommendations -- a log of page views rather than of clinical decisions, which
is what made the traceability list unreadable.

Safety: the EARLIEST row of each identical set is kept (that is when the
recommendation was actually made), and any row a clinician has touched --
approved, rejected, overridden, or reviewed -- is never deleted, even if it
duplicates another. Reports by default; pass --apply to delete.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count


class Command(BaseCommand):
    help = "Collapse duplicate RecommendationAudit rows (same patient/type/disease/text)."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true",
                            help="Delete the duplicates. Without this, only reports.")

    def handle(self, *args, **options):
        from knowledge.models import RecommendationAudit

        groups = (RecommendationAudit.objects
                  .values("patient_id", "recommendation_type", "disease_id",
                          "recommendation_text")
                  .annotate(n=Count("id"))
                  .filter(n__gt=1))

        doomed, protected = [], 0
        for g in groups:
            rows = list(RecommendationAudit.objects.filter(
                patient_id=g["patient_id"],
                recommendation_type=g["recommendation_type"],
                disease_id=g["disease_id"],
                recommendation_text=g["recommendation_text"],
            ).order_by("issued_at"))
            for row in rows[1:]:                       # keep the first
                acted_on = (row.approval_status != "pending"
                            or row.reviewed_at is not None
                            or row.expert_reviewer_id is not None
                            or bool(row.override_reason))
                if acted_on:
                    protected += 1
                    continue
                doomed.append(row.pk)

        total = RecommendationAudit.objects.count()
        self.stdout.write(f"{total} audit rows, {len(groups)} duplicated recommendations")
        self.stdout.write(f"{len(doomed)} redundant rows; {protected} kept (clinician acted on them)")

        if not doomed:
            return
        if not options["apply"]:
            self.stdout.write(self.style.WARNING("Dry run — pass --apply to delete."))
            return

        RecommendationAudit.objects.filter(pk__in=doomed).delete()
        self.stdout.write(self.style.SUCCESS(
            f"Deleted {len(doomed)} duplicates; {RecommendationAudit.objects.count()} rows remain."))
