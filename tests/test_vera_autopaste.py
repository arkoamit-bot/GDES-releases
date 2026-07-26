"""Tests for the guarded Vera auto-paste.

The point of these tests is the *guard*: the clipboard holds a full case note,
so a paste must never fire unless the foreground window is verifiably a browser
showing Vera. Everything is mocked -- no real keystroke is ever sent.
"""
from unittest.mock import patch

from clinical_evidence.services import vera_autopaste as ap


class TestGuard:
    def test_accepts_browser_showing_vera(self):
        assert ap.looks_like_vera("Vera Health - Chrome", "chrome.exe")
        assert ap.looks_like_vera("vera health ai — Mozilla Firefox", "firefox.exe")

    def test_rejects_non_browser_even_with_vera_in_title(self):
        # A Word document named "Vera" must never receive the case note.
        assert not ap.looks_like_vera("Vera notes.docx - Word", "WINWORD.EXE")

    def test_rejects_browser_on_a_different_tab(self):
        # Clinician switched tabs: the paste would land in the wrong page.
        assert not ap.looks_like_vera("GDES — Patient GN-0042", "chrome.exe")
        assert not ap.looks_like_vera("Gmail - Inbox", "msedge.exe")

    def test_rejects_empty(self):
        assert not ap.looks_like_vera("", "")


class TestAutopaste:
    def test_pastes_when_vera_is_foreground(self):
        with patch.object(ap, "_foreground_info", return_value=("Vera Health", "chrome.exe")), \
             patch.object(ap, "_send_ctrl_v", return_value=True) as send, \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "pasted"
        assert send.call_count == 1

    def test_sends_nothing_when_vera_never_focused(self):
        with patch.object(ap, "_foreground_info", return_value=("Inbox", "outlook.exe")), \
             patch.object(ap, "_send_ctrl_v") as send, \
             patch.object(ap, "POLL_INTERVAL", 0):
            result = ap.autopaste_into_vera(timeout=0.2)
        assert result["status"] == "not_focused"
        send.assert_not_called()

    def test_aborts_if_focus_changes_during_settle(self):
        # The critical case: Vera is focused, the clinician alt-tabs to another
        # patient's record while the page loads -> the paste must NOT fire.
        seq = [("Vera Health", "chrome.exe"), ("GDES — Patient GN-0042", "chrome.exe")]
        with patch.object(ap, "_foreground_info", side_effect=seq), \
             patch.object(ap, "_send_ctrl_v") as send, \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "not_focused"
        send.assert_not_called()

    def test_reports_send_failure(self):
        with patch.object(ap, "_foreground_info", return_value=("Vera Health", "chrome.exe")), \
             patch.object(ap, "_send_ctrl_v", return_value=False), \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "send_failed"
        assert "Ctrl+V" in result["message"]

    def test_disabled_by_env(self):
        with patch.dict("os.environ", {"GDES_VERA_AUTOPASTE": "0"}), \
             patch.object(ap, "_send_ctrl_v") as send:
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "disabled"
        send.assert_not_called()

    def test_unsupported_off_windows(self):
        with patch.object(ap, "is_supported", return_value=False), \
             patch.object(ap, "_send_ctrl_v") as send:
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "unsupported"
        send.assert_not_called()

    def test_never_presses_enter(self):
        # Submitting on the clinician's behalf is out of scope by design.
        import inspect
        src = inspect.getsource(ap)
        assert "VK_RETURN" not in src
