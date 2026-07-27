from django.apps import AppConfig


class ClinicalEvidenceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clinical_evidence"
    verbose_name = "Clinical Evidence Intelligence"

    def ready(self):
        try:
            import clinical_evidence.signals  # noqa
        except Exception:
            pass
        # Only start the health monitor in production, not during tests or dev.
        import os
        if not os.environ.get("RUN_TESTS") and not os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith("test"):
            try:
                from clinical_evidence.services import monitoring
                monitoring.start_health_monitor()
            except Exception:
                pass
