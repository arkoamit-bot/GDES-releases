"""Tests for the guarded Vera auto-paste.

The point of these tests is the *guard*: the clipboard holds a full case note,
so a paste must never fire unless the foreground window is verifiably a browser
showing Vera. Everything is mocked -- no real keystroke is ever sent.
"""
import sys
from unittest.mock import patch

import pytest

from clinical_evidence.services import vera_autopaste as ap


@pytest.mark.skipif(sys.platform != "win32", reason="Win32 structures")
class TestKeystrokeStructs:
    """Build the real INPUT records -- SendInput is never called.

    Regression: dwExtraInfo was passed as None (it is a ULONG_PTR), so every
    paste died with "NoneType object cannot be interpreted as an integer".
    Mocking _send_ctrl_v hid this, hence this test.
    """

    def test_builds_four_events_without_error(self):
        events, INPUT = ap._build_ctrl_v_events()
        assert len(events) == 4

    def test_events_are_ctrl_v_down_then_up(self):
        events, _ = ap._build_ctrl_v_events()
        VK_CONTROL, VK_V, KEYUP = 0x11, 0x56, 0x0002
        assert [e.ki.wVk for e in events] == [VK_CONTROL, VK_V, VK_V, VK_CONTROL]
        assert [bool(e.ki.dwFlags & KEYUP) for e in events] == [False, False, True, True]
        assert all(e.ki.dwExtraInfo == 0 for e in events)
        assert all(e.type == 1 for e in events)  # INPUT_KEYBOARD


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
    """_click_input_area is always mocked -- a real click would move the mouse
    of whoever is running the tests."""

    @pytest.fixture(autouse=True)
    def _as_if_windows(self):
        # The guard logic is platform-independent once the Win32 calls are
        # mocked; without this every case returns "unsupported" on Linux CI.
        with patch.object(ap, "is_supported", return_value=True):
            yield

    def test_pastes_when_vera_is_foreground(self):
        with patch.object(ap, "_foreground_info", return_value=("Vera Health", "chrome.exe")), \
             patch.object(ap, "_click_input_area", return_value=True), \
             patch.object(ap, "_send_ctrl_v", return_value=True) as send, \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "pasted"
        assert send.call_count == 1

    def test_clicks_the_composer_before_pasting(self):
        # Focusing the window is not enough: without the caret in an editable
        # element Ctrl+V is swallowed, or lands in the address bar.
        calls = []
        with patch.object(ap, "_foreground_info", return_value=("Vera Health", "chrome.exe")), \
             patch.object(ap, "_click_input_area", side_effect=lambda: calls.append("click") or True), \
             patch.object(ap, "_send_ctrl_v", side_effect=lambda: calls.append("paste") or True), \
             patch.object(ap, "SETTLE_SECONDS", 0):
            ap.autopaste_into_vera(timeout=1)
        assert calls == ["click", "paste"]

    def test_click_can_be_disabled(self):
        with patch.dict("os.environ", {"GDES_VERA_AUTOPASTE_CLICK": "0"}), \
             patch.object(ap, "_foreground_info", return_value=("Vera Health", "chrome.exe")), \
             patch.object(ap, "_click_input_area") as click, \
             patch.object(ap, "_send_ctrl_v", return_value=True), \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "pasted"
        click.assert_not_called()

    def test_aborts_if_focus_changes_after_click(self):
        seq = [("Vera Health", "chrome.exe"),   # poll match
               ("Vera Health", "chrome.exe"),   # after settle
               ("GDES — Patient GN-0042", "chrome.exe")]  # after click
        with patch.object(ap, "_foreground_info", side_effect=seq), \
             patch.object(ap, "_click_input_area", return_value=True), \
             patch.object(ap, "_send_ctrl_v") as send, \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "not_focused"
        send.assert_not_called()

    def test_pastes_even_if_the_click_fails(self):
        # A failed click is not fatal -- the composer may already be focused.
        with patch.object(ap, "_foreground_info", return_value=("Vera Health", "chrome.exe")), \
             patch.object(ap, "_click_input_area", side_effect=OSError("no window")), \
             patch.object(ap, "_send_ctrl_v", return_value=True), \
             patch.object(ap, "SETTLE_SECONDS", 0):
            result = ap.autopaste_into_vera(timeout=1)
        assert result["status"] == "pasted"

    def test_click_target_lands_in_veras_ask_box(self):
        # Measured on a maximised Edge window (1591x855 client): Vera's "Ask"
        # card spans y 437-547, x 607-1275. The first attempt aimed at a
        # bottom strip (y~737) and hit empty page, so the paste went nowhere.
        win_w, win_h = 1591, 855
        x = win_w // 2
        y = int(win_h * ap.click_y_fraction())
        assert 437 <= y <= 547, f"y={y} outside the Ask box"
        assert 607 <= x <= 1275, f"x={x} outside the Ask box"

    def test_click_y_fraction_is_clamped(self):
        for value in ("99", "-5", "nonsense"):
            with patch.dict("os.environ", {"GDES_VERA_AUTOPASTE_CLICK_Y": value}):
                assert 0.2 <= ap.click_y_fraction() <= 0.9

    def test_settle_is_env_tunable(self):
        with patch.dict("os.environ", {"GDES_VERA_AUTOPASTE_SETTLE": "6.5"}):
            assert ap.settle_seconds() == 6.5
        with patch.dict("os.environ", {"GDES_VERA_AUTOPASTE_SETTLE": "nonsense"}):
            assert ap.settle_seconds() == ap.SETTLE_SECONDS

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
             patch.object(ap, "_click_input_area", return_value=True), \
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
