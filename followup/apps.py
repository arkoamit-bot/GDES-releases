from django.apps import AppConfig


class FollowupConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "followup"
    verbose_name = "Follow-up Engine"

    def ready(self):
        from . import event_handlers
        event_handlers.connect_handlers()
        from .services import engine
        engine.connect_signals()
