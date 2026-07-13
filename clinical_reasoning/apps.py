from django.apps import AppConfig


class ClinicalReasoningConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "clinical_reasoning"
    verbose_name = "Clinical Reasoning Engine"

    def ready(self):
        from .event_handlers import connect_handlers
        connect_handlers()
