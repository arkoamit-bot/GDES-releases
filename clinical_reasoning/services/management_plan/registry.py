"""Profile registry and factory for disease treatment profiles.

Provides a central registry that disease profile modules register into on
import.  The ``ManagementPlanFactory`` wraps the generation logic and is the
single entry-point the rest of the application uses.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class ProfileRegistry:
    """Central registry for disease treatment profiles.

    Profiles register themselves on import via ``register()``.  The registry
    provides lookup, enumeration, and backward-compatible merging.
    """

    _profiles: dict[str, dict[str, Any]] = {}

    @classmethod
    def register(cls, key: str, profile: dict[str, Any]) -> None:
        """Register a disease profile under its key."""
        cls._profiles[key] = profile

    @classmethod
    def get(cls, key: str) -> dict[str, Any] | None:
        """Look up a profile by disease key."""
        return cls._profiles.get(key)

    @classmethod
    def all_keys(cls) -> list[str]:
        """Return all registered profile keys, sorted."""
        return sorted(cls._profiles.keys())

    @classmethod
    def merge_all(cls) -> dict[str, dict[str, Any]]:
        """Return all profiles as a single dict (backward compatibility)."""
        return dict(cls._profiles)

    @classmethod
    def clear(cls) -> None:
        """Remove all registered profiles (for testing)."""
        cls._profiles.clear()


# ---------------------------------------------------------------------------
# Factory — single entry-point for plan generation
# ---------------------------------------------------------------------------

def get_profile(disease_id: str) -> dict[str, Any] | None:
    """Look up a disease profile from the registry."""
    return ProfileRegistry.get(disease_id)


def all_profiles() -> dict[str, dict[str, Any]]:
    """Return all registered profiles (backward-compatible alias)."""
    return ProfileRegistry.merge_all()
