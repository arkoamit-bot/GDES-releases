"""
Signal-based audit recorder. Register a model and every create/update/delete is
captured as AuditLog rows — per-field old->new on update — attributed to the
current actor (see audit.local).

    from audit.recording import register
    register(Patient, exclude=["latest_egfr"])

No external dependencies; uses Django's pre_save / post_save / post_delete.
"""
from __future__ import annotations

from django.db.models.signals import post_delete, post_save, pre_save

from .local import current_actor, current_reason

_CONFIG: dict = {}     # model -> set(excluded field names)


def _tracked_fields(model):
    excluded = _CONFIG.get(model, set())
    fields = []
    for f in model._meta.concrete_fields:
        if f.primary_key:
            continue
        if getattr(f, "auto_now", False) or getattr(f, "auto_now_add", False):
            continue
        if f.name in excluded or f.attname in excluded:
            continue
        fields.append(f)
    return fields


def _serialize(instance, field):
    try:
        val = field.value_from_object(instance)
    except Exception:
        val = getattr(instance, field.attname, None)
    return None if val is None else str(val)


def _label(model):
    return f"{model._meta.app_label}.{model.__name__}"


def _pre_save(sender, instance, **kwargs):
    if not instance.pk:
        instance._audit_old = None
        return
    try:
        old = sender._base_manager.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._audit_old = None
        return
    instance._audit_old = {f.name: _serialize(old, f) for f in _tracked_fields(sender)}


def _post_save(sender, instance, created, **kwargs):
    from .models import AuditLog
    user = current_actor()
    reason = current_reason()
    label = _label(sender)
    pk = str(instance.pk)
    repr_ = str(instance)[:200]

    if created:
        AuditLog.objects.create(
            model_label=label, object_pk=pk, object_repr=repr_,
            action=AuditLog.Action.CREATE, changed_by=user, change_reason=reason)
        return

    old = getattr(instance, "_audit_old", None)
    if old is None:
        return
    rows = []
    for f in _tracked_fields(sender):
        new_val = _serialize(instance, f)
        old_val = old.get(f.name)
        if old_val != new_val:
            rows.append(AuditLog(
                model_label=label, object_pk=pk, object_repr=repr_,
                action=AuditLog.Action.UPDATE, field_name=f.name,
                old_value=old_val, new_value=new_val,
                changed_by=user, change_reason=reason))
    if rows:
        AuditLog.objects.bulk_create(rows)


def _post_delete(sender, instance, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        model_label=_label(sender), object_pk=str(instance.pk),
        object_repr=str(instance)[:200], action=AuditLog.Action.DELETE,
        changed_by=current_actor(), change_reason=current_reason())


def register(model, *, exclude=()):
    """Start auditing a model. Idempotent per model."""
    _CONFIG[model] = set(exclude)
    uid = f"audit:{_label(model)}"
    pre_save.connect(_pre_save, sender=model, dispatch_uid=uid + ":pre")
    post_save.connect(_post_save, sender=model, dispatch_uid=uid + ":post")
    post_delete.connect(_post_delete, sender=model, dispatch_uid=uid + ":del")


def history_for(instance):
    """Convenience: AuditLog queryset for one object, newest first."""
    from .models import AuditLog
    return AuditLog.objects.filter(
        model_label=_label(type(instance)), object_pk=str(instance.pk))
