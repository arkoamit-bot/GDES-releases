from django.apps import AppConfig


class StudiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "studies"

    def ready(self):
        # Import the eligibility module so its @register_eligibility examples
        # are registered at startup.
        from .services import eligibility  # noqa: F401

        # Wire automatic eligibility screening to the domain-event bus so every
        # patient is continuously evaluated for the recruiting studies.
        from .event_handlers import connect_handlers
        connect_handlers()
