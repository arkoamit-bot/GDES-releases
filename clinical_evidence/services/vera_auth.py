"""Vera Health Authentication — Manual Browser Integration.

Provides passwordless authentication by opening the Vera Health website
in the user's default browser.  GDES never stores passwords, OTPs,
browser cookies, or session tokens.  Authentication is completed manually
on the official Vera Health website.

Local preferences remembered:
- Last Vera email (optional)
- Whether user previously connected
- Last successful verification time

Never:
- Automate login using browser scripting
- Read browser cookies
- Capture OTP
- Capture passwords
- Inject code into Vera pages
"""
from __future__ import annotations

import json
import logging
import os
import time
import webbrowser
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("bgddr.vera.auth")

VERA_WEBSITE_URL = os.environ.get(
    "VERA_WEBSITE_URL", "https://verahealth.ai"
)


# ------------------------------------------------------------------ #
# Data classes
# ------------------------------------------------------------------ #

@dataclass
class VeraConnectionState:
    """Tracks the user's manual connection to Vera Health.

    This is purely local state — no tokens or API credentials.
    """
    connected: bool = False
    email: str = ""
    last_connected_at: float = 0.0
    browser_opened_at: float = 0.0
    previously_connected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "email": self.email,
            "last_connected_at": self.last_connected_at,
            "browser_opened_at": self.browser_opened_at,
            "previously_connected": self.previously_connected,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VeraConnectionState":
        return cls(
            connected=data.get("connected", False),
            email=data.get("email", ""),
            last_connected_at=data.get("last_connected_at", 0.0),
            browser_opened_at=data.get("browser_opened_at", 0.0),
            previously_connected=data.get("previously_connected", False),
        )


# ------------------------------------------------------------------ #
# Storage backends
# ------------------------------------------------------------------ #

class SessionStorage:
    """Store connection state in Django sessions."""

    SESSION_KEY = "vera_connection_state"

    def __init__(self, request=None):
        self._request = request

    def set_request(self, request):
        self._request = request

    def load_state(self) -> VeraConnectionState:
        if not self._request:
            return VeraConnectionState()
        data = self._request.session.get(self.SESSION_KEY)
        if data:
            return VeraConnectionState.from_dict(data)
        return VeraConnectionState()

    def save_state(self, state: VeraConnectionState):
        if not self._request:
            return
        self._request.session[self.SESSION_KEY] = state.to_dict()
        if hasattr(self._request.session, "modified"):
            self._request.session.modified = True

    def clear_state(self):
        if not self._request:
            return
        if self.SESSION_KEY in self._request.session:
            del self._request.session[self.SESSION_KEY]
            if hasattr(self._request.session, "modified"):
                self._request.session.modified = True


class LocalFileStorage:
    """Store connection state in a local JSON file.

    Used when no Django request is available (e.g., management commands).
    """

    FILE_PATH = os.path.join(
        os.path.expanduser("~"), ".gdes", "vera_connection.json"
    )

    def __init__(self):
        self._state: VeraConnectionState | None = None

    def load_state(self) -> VeraConnectionState:
        if self._state is not None:
            return self._state
        try:
            with open(self.FILE_PATH, "r") as f:
                data = json.load(f)
            self._state = VeraConnectionState.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            self._state = VeraConnectionState()
        return self._state

    def save_state(self, state: VeraConnectionState):
        self._state = state
        try:
            os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
            with open(self.FILE_PATH, "w") as f:
                json.dump(state.to_dict(), f, indent=2)
        except OSError as exc:
            logger.warning("Failed to save Vera state to file: %s", exc)

    def clear_state(self):
        self._state = VeraConnectionState()
        try:
            if os.path.exists(self.FILE_PATH):
                os.remove(self.FILE_PATH)
        except OSError:
            pass


class MockStorage:
    """In-memory storage for testing."""

    def __init__(self):
        self._state = VeraConnectionState()

    def load_state(self) -> VeraConnectionState:
        return self._state

    def save_state(self, state: VeraConnectionState):
        self._state = state

    def clear_state(self):
        self._state = VeraConnectionState()


# ------------------------------------------------------------------ #
# Service
# ------------------------------------------------------------------ #

class VeraAuthService:
    """Service for manual Vera Health browser-based authentication.

    GDES responsibilities per VERA_MANUAL_BROWSER_INTEGRATION.md:
    - Open Vera website automatically
    - Detect internet connectivity
    - Remember that Vera was previously connected
    - Remember the user's Vera email locally (optional)
    - Never store passwords, OTPs, or session tokens
    """

    def __init__(self, storage=None):
        self._storage = storage or MockStorage()

    def get_state(self) -> VeraConnectionState:
        return self._storage.load_state()

    def is_connected(self) -> bool:
        state = self._storage.load_state()
        return state.connected

    def open_vera_website(self, email: str = "") -> dict[str, Any]:
        """Open the Vera Health website in the user's default browser.

        Returns a dict with status and whether the browser was opened.
        """
        state = self._storage.load_state()
        if email:
            state.email = email
        state.browser_opened_at = time.time()
        self._storage.save_state(state)

        try:
            opened = webbrowser.open(VERA_WEBSITE_URL)
            if opened:
                logger.info("Opened Vera Health website in browser")
                self._log_event("browser_opened", email)
                return {
                    "status": "browser_opened",
                    "url": VERA_WEBSITE_URL,
                    "message": "Vera Health website opened in your browser.",
                }
            else:
                logger.warning("webbrowser.open returned False")
                return {
                    "status": "browser_failed",
                    "url": VERA_WEBSITE_URL,
                    "message": (
                        "Unable to open your default web browser. "
                        "Please open Vera manually."
                    ),
                }
        except Exception as exc:
            logger.error("Failed to open browser: %s", exc)
            return {
                "status": "browser_failed",
                "url": VERA_WEBSITE_URL,
                "message": (
                    "Unable to open your default web browser. "
                    "Please open Vera manually."
                ),
            }

    def mark_connected(self, email: str = "") -> dict[str, Any]:
        """Mark that the user has completed Vera login and returned.

        Called when the user clicks "Continue Verification" after
        completing login on the Vera website.
        """
        state = self._storage.load_state()
        if email:
            state.email = email
        elif not state.email:
            state.email = ""
        state.connected = True
        state.previously_connected = True
        state.last_connected_at = time.time()
        self._storage.save_state(state)

        logger.info("Vera connection marked as connected")
        self._log_event("connected", state.email)

        return {
            "status": "connected",
            "email": state.email,
            "message": "Connected to Vera Health.",
        }

    def disconnect(self):
        """Disconnect from Vera Health (logout)."""
        state = self._storage.load_state()
        state.connected = False
        self._storage.save_state(state)

        logger.info("Vera connection cleared")
        self._log_event("disconnected", state.email)

    def mark_review_completed(
        self,
        patient_id: str,
        change_level: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record that the clinician completed a Vera review.

        Args:
            patient_id: The patient identifier.
            change_level: One of 'no_changes', 'minor', 'major'.
            details: Optional dict with change details.

        Returns:
            Dict with status and the recorded review.
        """
        state = self._storage.load_state()
        review_record = {
            "patient_id": patient_id,
            "review_date": time.time(),
            "vera_account": state.email,
            "change_level": change_level,
            "details": details or {},
        }

        self._log_event(
            "review_completed",
            state.email,
            extra=review_record,
        )

        return {
            "status": "review_recorded",
            "review": review_record,
        }

    def save_vera_response(
        self,
        patient_id: str,
        vera_response: str,
    ) -> dict[str, Any]:
        """Save the clinician's pasted Vera response for a patient.

        Stores the response in the audit trail for future reference
        and knowledge base integration.

        Args:
            patient_id: The patient identifier.
            vera_response: The text response pasted from Vera Health.

        Returns:
            Dict with status and the saved record.
        """
        state = self._storage.load_state()
        record = {
            "patient_id": patient_id,
            "saved_at": time.time(),
            "vera_account": state.email,
            "response_text": vera_response,
        }

        self._log_event(
            "vera_response_saved",
            state.email,
            extra=record,
        )

        return {
            "status": "response_saved",
            "record": record,
        }

    def get_auth_status(self) -> dict[str, Any]:
        """Get current authentication status for the frontend."""
        state = self._storage.load_state()
        return {
            "authenticated": state.connected,
            "email": state.email if state.connected else "",
            "previously_connected": state.previously_connected,
            "last_connected_at": state.last_connected_at,
        }

    def _validate_email(self, email: str) -> bool:
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _mask_email(self, email: str) -> str:
        parts = email.split("@")
        if len(parts) != 2:
            return email
        name, domain = parts
        if len(name) <= 1:
            masked = name[0] if name else "*"
        else:
            masked = name[0] + "***"
        return f"{masked}@{domain}"

    def _log_auth_event(self, event_type: str, email: str):
        self._log_event(event_type, email)

    def _log_event(self, event_type: str, email: str, extra: dict | None = None):
        from audit.models import AuditLog
        changes = {"event": event_type, "email": email}
        if extra:
            changes.update(extra)
        try:
            AuditLog.objects.create(
                model_label="vera_auth",
                object_pk=email or "unknown",
                object_repr=f"Vera auth: {event_type}",
                action="VERIFICATION",
                changes_json=changes,
            )
        except Exception as exc:
            logger.debug("Failed to log auth event: %s", exc)


def get_vera_auth_service(request=None) -> VeraAuthService:
    """Get a configured VeraAuthService instance."""
    if request:
        storage = SessionStorage(request)
    else:
        storage = LocalFileStorage()
    return VeraAuthService(storage=storage)
