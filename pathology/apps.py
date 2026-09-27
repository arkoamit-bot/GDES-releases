from django.apps import AppConfig


class PathologyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pathology"

    def ready(self):
        # Any save of a biopsy part -- guided form, amendment, review
        # finalization, API, admin -- refreshes the patient's pathology
        # summary through the one projection service.
        from django.db.models.signals import post_delete, post_save

        from . import models as m
        from .services.projection import request_projection

        def _patient_id(instance):
            biopsy = instance if isinstance(instance, m.Biopsy) else instance.biopsy
            return biopsy.patient_id

        def _on_change(sender, instance, **kwargs):
            if kwargs.get("raw"):
                return
            try:
                patient_id = _patient_id(instance)
            except m.Biopsy.DoesNotExist:
                return
            request_projection(patient_id)

        for model in (m.Biopsy, m.GNDiagnosis, m.IgANScore, m.LupusPathology,
                      m.FSGSPathology, m.PathologyReview):
            post_save.connect(_on_change, sender=model,
                              dispatch_uid=f"pathology:project:{model.__name__}:save")
            post_delete.connect(_on_change, sender=model,
                                dispatch_uid=f"pathology:project:{model.__name__}:delete")

        from audit.recording import register
        register(m.PathologyReport)
        register(m.PathologyFinding)
