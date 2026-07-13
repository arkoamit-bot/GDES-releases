"""JSON serialization helpers for JSONField-safe data."""
from decimal import Decimal
from typing import Any


def json_safe(value: Any) -> Any:
    """Recursively convert non-serializable types (Decimal, etc.) to serializable forms."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return tuple(json_safe(item) for item in value)
    if isinstance(value, set):
        return sorted(json_safe(item) for item in value)
    return value
