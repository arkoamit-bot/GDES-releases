from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "events"
    verbose_name = "Event Orchestration"

    def ready(self):
        from .signal_handlers import connect_all
        connect_all()
