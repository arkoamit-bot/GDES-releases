"""Build a research dataset from a Django queryset.

Intended for export to CSV / Excel / SPSS.  The queryset should be
pre-filtered and ordered by the caller; this module just flattens the
objects into a (column_names, rows) tuple suitable for the writers.
"""
from __future__ import annotations

from typing import Any

from django.db import models


# Default export columns for the patient-level research dataset.
# Each entry: (field_name, verbose_label).
_DEFAULT_COLUMNS: list[tuple[str, str]] = [
    ("patient_id", "Patient ID"),
    ("name", "Name"),
    ("sex", "Sex"),
    ("dob", "Date of Birth"),
    ("enrollment_date", "Enrollment Date"),
    ("diabetes_status", "Diabetes Status"),
    ("latest_egfr", "Latest eGFR"),
]


def _extract_value(obj: models.Model, field_name: str) -> Any:
    """Safely extract a value from a model instance.

    Handles both simple fields and FK__attr lookups.
    Returns empty string on AttributeError or RelatedObjectDoesNotExist.
    """
    try:
        parts = field_name.split("__")
        value = obj
        for part in parts:
            value = getattr(value, part)
        if callable(value):
            value = value()
        return value if value is not None else ""
    except Exception:
        return ""


def build_dataset(
    queryset: models.QuerySet,
    columns: list[tuple[str, str]] | None = None,
) -> tuple[list[str], list[list[Any]]]:
    """Flatten a queryset into a header list and list-of-rows.

    Parameters
    ----------
    queryset : QuerySet
        Pre-filtered, pre-ordered queryset (e.g. Patient.objects.all()).
    columns : list[(field_name, label)] or None
        Which fields to include.  Defaults to ``_DEFAULT_COLUMNS``.

    Returns
    -------
    (headers, rows)
        *headers* is a list of column-name strings.
        *rows*    is a list of lists, one per object.
    """
    if columns is None:
        columns = _DEFAULT_COLUMNS

    headers = [label for _, label in columns]
    field_names = [field for field, _ in columns]

    rows: list[list[Any]] = []
    for obj in queryset:
        rows.append([_extract_value(obj, fn) for fn in field_names])

    return headers, rows
