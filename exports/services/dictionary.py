"""Column definitions for the research dataset export.

Provides SPSS-style metadata (variable labels, value labels, measurement
levels) used by the ``to_sav`` writer.  Can also drive a data-dictionary
sheet in Excel exports.
"""
from __future__ import annotations

from typing import Any


# Each entry: variable_name → {
#     "label":      human-readable description,
#     "values":     dict mapping internal codes → labels (if categorical),
#     "measure":    "scale" | "nominal" | "ordinal",
#     "type":       "numeric" | "string",
# }
_COLUMN_DEFS: dict[str, dict[str, Any]] = {
    "patient_id": {
        "label": "Unique patient identifier",
        "values": {},
        "measure": "nominal",
        "type": "string",
    },
    "name": {
        "label": "Patient name",
        "values": {},
        "measure": "nominal",
        "type": "string",
    },
    "sex": {
        "label": "Biological sex",
        "values": {"M": "Male", "F": "Female", "O": "Other"},
        "measure": "nominal",
        "type": "string",
    },
    "dob": {
        "label": "Date of birth",
        "values": {},
        "measure": "scale",
        "type": "string",
    },
    "enrollment_date": {
        "label": "Registry enrollment date",
        "values": {},
        "measure": "scale",
        "type": "string",
    },
    "diabetes_status": {
        "label": "Diabetes status at enrollment",
        "values": {
            "t1": "Type 1",
            "t2": "Type 2",
            "other": "Other",
            "none": "No diabetes",
        },
        "measure": "nominal",
        "type": "string",
    },
    "latest_egfr": {
        "label": "Most recent eGFR (mL/min/1.73m²)",
        "values": {},
        "measure": "scale",
        "type": "numeric",
    },
}


def column_defs() -> dict[str, dict[str, Any]]:
    """Return the full column-definition mapping.

    Returns
    -------
    dict
        ``{variable_name: {"label": str, "values": dict, "measure": str, "type": str}}``
    """
    return dict(_COLUMN_DEFS)
