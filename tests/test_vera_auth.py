"""Tests for Vera Health Authentication — Manual Browser Integration."""
import time
import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.django_db


class TestVeraConnectionState:
    def test_state_creation(self):
        from clinical_evidence.services.vera_auth import VeraConnectionState

        state = VeraConnectionState()
        assert not state.connected
        assert state.email == ""
        assert state.last_connected_at == 0.0

    def test_state_serialization(self):
        from clinical_evidence.services.vera_auth import VeraConnectionState

        state = VeraConnectionState(
            connected=True,
            email="test@example.com",
            last_connected_at=time.time(),
            previously_connected=True,
        )
        data = state.to_dict()
        assert data["connected"] is True
        assert data["email"] == "test@example.com"
        assert data["previously_connected"] is True

        restored = VeraConnectionState.from_dict(data)
        assert restored.connected is True
        assert restored.email == "test@example.com"


class TestVeraAuthService:
    def test_initial_state_disconnected(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        assert not service.is_connected()

    def test_open_vera_website(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        with patch("clinical_evidence.services.vera_auth.webbrowser.open", return_value=True):
            result = service.open_vera_website(email="test@example.com")
            assert result["status"] == "browser_opened"
            assert "verahealth.ai" in result["url"]

    def test_open_vera_website_browser_fails(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        with patch("clinical_evidence.services.vera_auth.webbrowser.open", return_value=False):
            result = service.open_vera_website()
            assert result["status"] == "browser_failed"
            assert "Unable to open" in result["message"]

    def test_open_vera_website_exception(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        with patch("clinical_evidence.services.vera_auth.webbrowser.open", side_effect=OSError("no browser")):
            result = service.open_vera_website()
            assert result["status"] == "browser_failed"

    def test_mark_connected(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        result = service.mark_connected(email="test@example.com")
        assert result["status"] == "connected"
        assert service.is_connected()

    def test_mark_connected_saves_email(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        service.mark_connected(email="test@example.com")
        state = service.get_state()
        assert state.email == "test@example.com"
        assert state.previously_connected is True

    def test_disconnect(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        service.mark_connected(email="test@example.com")
        assert service.is_connected()
        service.disconnect()
        assert not service.is_connected()

    def test_auth_status_disconnected(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        status = service.get_auth_status()
        assert status["authenticated"] is False
        assert status["email"] == ""

    def test_auth_status_connected(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        service.mark_connected(email="test@example.com")
        status = service.get_auth_status()
        assert status["authenticated"] is True
        assert status["email"] == "test@example.com"

    def test_email_validation(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        assert service._validate_email("test@example.com")
        assert service._validate_email("user.name+tag@domain.co.uk")
        assert not service._validate_email("invalid")
        assert not service._validate_email("@no-user.com")
        assert not service._validate_email("no-domain@")

    def test_mask_email(self):
        from clinical_evidence.services.vera_auth import VeraAuthService, MockStorage

        service = VeraAuthService(storage=MockStorage())
        assert service._mask_email("test@example.com") == "t***@example.com"
        assert service._mask_email("a@b.com") == "a@b.com"


class TestMockStorage:
    def test_save_and_load(self):
        from clinical_evidence.services.vera_auth import MockStorage, VeraConnectionState

        storage = MockStorage()
        state = VeraConnectionState(connected=True, email="test@example.com")
        storage.save_state(state)
        loaded = storage.load_state()
        assert loaded.connected is True
        assert loaded.email == "test@example.com"

    def test_clear(self):
        from clinical_evidence.services.vera_auth import MockStorage, VeraConnectionState

        storage = MockStorage()
        storage.save_state(VeraConnectionState(connected=True))
        storage.clear_state()
        loaded = storage.load_state()
        assert loaded.connected is False


class TestSessionStorage:
    def test_save_and_load(self):
        from clinical_evidence.services.vera_auth import SessionStorage, VeraConnectionState

        mock_request = MagicMock()
        mock_request.session = {}

        storage = SessionStorage(mock_request)
        state = VeraConnectionState(connected=True, email="test@example.com")
        storage.save_state(state)

        loaded = storage.load_state()
        assert loaded.connected is True
        assert loaded.email == "test@example.com"

    def test_clear(self):
        from clinical_evidence.services.vera_auth import SessionStorage, VeraConnectionState

        mock_request = MagicMock()
        mock_request.session = {}
        storage = SessionStorage(mock_request)
        storage.save_state(VeraConnectionState(connected=True))
        storage.clear_state()

        loaded = storage.load_state()
        assert loaded.connected is False

    def test_no_request(self):
        from clinical_evidence.services.vera_auth import SessionStorage

        storage = SessionStorage()
        state = storage.load_state()
        assert state.connected is False
        storage.save_state(state)
        storage.clear_state()
