from django.apps import AppConfig


def on_pathology_change(sender, instance, **kwargs):
    """Any save of a biopsy part -- guided form, amendment, review
    finalization, API, admin -- refreshes the patient's pathology summary
    through the one projection service.

    Module level on purpose: a function defined inside ready() is held only
    by the signal's weak reference and can be garbage-collected, silently
    disconnecting the projection (seen on the clinic server, 2026-09-29).
    """
    if kwargs.get("raw"):
        return
    from . import models as m
    from .services.projection import request_projection
    try:
        biopsy = instance if isinstance(instance, m.Biopsy) else instance.biopsy
        patient_id = biopsy.patient_id
    except m.Biopsy.DoesNotExist:
        return
    request_projection(patient_id)


class PathologyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pathology"

    def ready(self):
        from django.db.models.signals import post_delete, post_save

        from . import models as m

        for model in (m.Biopsy, m.GNDiagnosis, m.IgANScore, m.LupusPathology,
                      m.FSGSPathology, m.PathologyReview):
            post_save.connect(on_pathology_change, sender=model, weak=False,
                              dispatch_uid=f"pathology:project:{model.__name__}:save")
            post_delete.connect(on_pathology_change, sender=model, weak=False,
                                dispatch_uid=f"pathology:project:{model.__name__}:delete")

        from audit.recording import register
        register(m.PathologyReport)
        register(m.PathologyFinding)
