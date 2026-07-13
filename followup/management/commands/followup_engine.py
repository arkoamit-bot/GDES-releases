"""Management command to interact with the follow-up engine.

Usage:
  python manage.py followup_engine compute_plans
  python manage.py followup_engine run_escalation
  python manage.py followup_engine dashboard
  python manage.py followup_engine plan <patient_id>
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from patients.models import Patient


class Command(BaseCommand):
    help = "Interact with the follow-up engine"

    def add_arguments(self, parser):
        parser.add_argument(
            "action",
            choices=["compute_plans", "run_escalation", "dashboard", "plan"],
        )
        parser.add_argument("patient_id", nargs="?", default=None)

    def handle(self, *args, **options):
        action = options["action"]
        if action == "compute_plans":
            self._compute_plans()
        elif action == "run_escalation":
            self._run_escalation()
        elif action == "dashboard":
            self._dashboard()
        elif action == "plan":
            if not options["patient_id"]:
                raise CommandError("patient_id is required for the plan action")
            self._plan(options["patient_id"])

    def _compute_plans(self):
        from followup.services.engine import compute_all_plans
        self.stdout.write("Computing follow-up plans for all registered patients...")
        results = compute_all_plans()
        ok_count = sum(1 for r in results if r[1] == "ok")
        fail = sum(1 for r in results if r[1] != "ok")
        self.stdout.write(self.style.SUCCESS(f"Done. {ok_count} ok, {fail} failed."))
        for pid, status in results:
            if status != "ok":
                self.stdout.write(self.style.WARNING(f"  {pid}: {status}"))

    def _run_escalation(self):
        from followup.services.escalation import run_escalation, get_overdue_summary
        self.stdout.write("Running escalation...")
        count = run_escalation()
        self.stdout.write(self.style.SUCCESS(f"Escalated {count} tasks."))
        summary = get_overdue_summary()
        for row in summary:
            self.stdout.write(f"  Level {row['escalation_level']}: {row['count']} tasks")

    def _dashboard(self):
        from followup.services.dashboard import get_daily_summary
        data = get_daily_summary()
        self.stdout.write(f"Follow-up Dashboard - {data['as_of']}")
        self.stdout.write("-" * 50)
        s = data["summary"]
        self.stdout.write(f"  Due today:       {s['due_today']}")
        self.stdout.write(f"  Overdue:         {s['overdue']}")
        self.stdout.write(f"  High risk:       {s['high_risk']}")
        self.stdout.write(f"  Missed:          {s['missed']}")
        self.stdout.write(f"  Drug monitoring: {s['drug_monitoring']}")
        self.stdout.write(f"  Lab monitoring:  {s['lab_monitoring']}")
        if data["recent_relapses"]:
            self.stdout.write("\nRecent relapses:")
            for p in data["recent_relapses"]:
                self.stdout.write(f"  - {p['patient_id']}: {p['name']}")
        if data["rapid_egfr_decline"]:
            self.stdout.write("\nRapid eGFR decline:")
            for p in data["rapid_egfr_decline"]:
                self.stdout.write(f"  - {p['patient_id']}: eGFR {p['latest_egfr']}")

    def _plan(self, patient_id):
        from followup.services.engine import compute_followup_plan
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            raise CommandError(f"Patient {patient_id} not found")
        plan = compute_followup_plan(patient)
        self.stdout.write(f"Follow-up Plan for {patient.patient_id} ({patient.name})")
        self.stdout.write("-" * 50)
        self.stdout.write(f"  Protocol:           {plan['protocol_name']} ({plan['protocol']})")
        self.stdout.write(f"  Risk category:      {plan['risk_category']} (score: {plan['risk_score']})")
        self.stdout.write(f"  Visit interval:     {plan['visit_interval_days']} days")
        self.stdout.write(f"  Next visit:         {plan['next_visit_date']}")
        tasks = patient.followup_tasks.filter(status__in=["pending", "overdue"])
        if tasks:
            self.stdout.write(f"\nActive tasks ({tasks.count()}):")
            for t in tasks.order_by("due_date"):
                status_icon = "!" if t.status == "overdue" else " "
                self.stdout.write(
                    f"  {status_icon} {t.get_task_type_display():25s} "
                    f"due {t.due_date}  [{t.priority}]"
                )
        else:
            self.stdout.write("\nNo active tasks.")
