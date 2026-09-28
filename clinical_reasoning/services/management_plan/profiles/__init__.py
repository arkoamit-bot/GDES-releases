"""Disease treatment profiles sub-package.

Importing this package auto-registers all disease profiles with the
:class:`~management_plan.registry.ProfileRegistry`.  Each sub-module
is responsible for one disease category.
"""
from __future__ import annotations

# Import each profile module so it auto-registers its profiles.
from . import (  # noqa: F401
    autoimmune,
    complement,
    diabetic,
    hereditary,
    infection,
    primary,
    rare,
    transplant,
)

__all__ = [
    "autoimmune",
    "complement",
    "diabetic",
    "hereditary",
    "infection",
    "primary",
    "rare",
    "transplant",
]
