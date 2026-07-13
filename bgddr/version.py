"""Single source of truth for the application version.

Bump this before building a release you intend to publish to the OneDrive update
folder. The desktop self-updater compares this value against the `version` field
in the update folder's ``latest.json`` manifest to decide whether a newer build
is available. Use a simple dotted numeric form, e.g. "6.5.0", "6.6.0".
"""

__version__ = "6.5.0"
