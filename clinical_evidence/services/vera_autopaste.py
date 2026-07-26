"""Guarded auto-paste of the Vera prompt into the browser (Windows only).

Background
----------
"Request Prescription from Vera" copies a structured case note to the clipboard
and opens https://verahealth.ai in a new tab; the clinician then presses Ctrl+V.
The browser's same-origin policy makes it *impossible* for GDES JavaScript to
type into Vera's page, so the last step is done at the OS level instead: send a
single Ctrl+V to the foreground window.

Why the guard matters
---------------------
The clipboard holds a full case note (patient data).  A blind, timed keystroke
would paste it into whatever window happens to be focused -- an email, another
patient's record -- if the clinician alt-tabs during the few seconds the page is
loading.  So this module NEVER pastes on a timer.  It polls until the foreground
window is verifiably *a browser showing Vera*, re-checks immediately before
sending, and otherwise gives up silently.  Worst case: nothing happens and the
clinician presses Ctrl+V themselves (the clipboard copy is untouched).

Focusing the composer
---------------------
Making Vera's *window* foreground is not sufficient: Ctrl+V goes to whatever
element holds the caret.  Right after window.open that is often the address bar
(the case note would land in the omnibox) or nothing at all (the keystroke is
silently swallowed -- "delivered" but nothing appears).  So, after the guard
passes, a single click is placed in Vera's "Ask" box -- a card in the middle of
the *already-verified* Vera window -- before pasting.

Deliberate non-goals
--------------------
- Never presses Enter -- the clinician must see the prompt before submitting.
- Never reads the clipboard, the page, or anything from Vera.
- Never injects script into Vera pages (see the policy in vera_auth.py).
- No patient data passes through this module; it only sends a keystroke.
"""
from __future__ import annotations

import logging
import os
import sys
import time

logger = logging.getLogger("bgddr.vera.autopaste")

# Browsers whose window may legitimately receive the paste.
BROWSER_EXES = {
    "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe",
    "opera.exe", "opera_gx.exe", "vivaldi.exe", "chromium.exe",
}
# The foreground window title must also look like Vera, so we never paste into
# some other tab the clinician switched to.
TITLE_HINTS = ("vera",)

# Poll for the Vera window for this long before giving up.
DEFAULT_TIMEOUT = 15.0
POLL_INTERVAL = 0.4
# Let the page finish loading and render its input after the window appears.
# Ctrl+V is a no-op until an editable element holds the caret, so this is
# deliberately generous; tune with GDES_VERA_AUTOPASTE_SETTLE.
SETTLE_SECONDS = 3.5
# Where to click to focus Vera's composer, as a fraction of window height.
#
# We always open a FRESH verahealth.ai tab, so the clinician always lands on the
# "Ask" screen, whose input box is a large card in the middle of the page -- not
# a bottom strip like most chat UIs. Measured at ~0.57 of window height on a
# maximised Edge window; the card is ~110px tall, so 0.56 has room to spare
# whether or not the bookmarks bar is shown. Tune with
# GDES_VERA_AUTOPASTE_CLICK_Y if Vera changes its layout.
CLICK_Y_FRACTION = 0.56


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, "").strip())
    except (TypeError, ValueError):
        return default


def settle_seconds() -> float:
    return max(0.0, _env_float("GDES_VERA_AUTOPASTE_SETTLE", SETTLE_SECONDS))


def click_y_fraction() -> float:
    """Clamped so a bad env value can never click outside the page area."""
    return min(0.9, max(0.2, _env_float("GDES_VERA_AUTOPASTE_CLICK_Y",
                                        CLICK_Y_FRACTION)))


def is_enabled() -> bool:
    """Auto-paste is on by default on Windows; GDES_VERA_AUTOPASTE=0 disables."""
    return (os.environ.get("GDES_VERA_AUTOPASTE", "1").strip().lower()
            not in ("0", "false", "no", "off"))


def click_focus_enabled() -> bool:
    """Click the page's input area before pasting.

    Focusing the window is not enough: if the caret is still in the address bar
    (common right after window.open) Ctrl+V would paste the case note into the
    omnibox, and if no element is focused it does nothing at all.  A click in
    the chat-input strip puts the caret where it belongs.  Disable with
    GDES_VERA_AUTOPASTE_CLICK=0.
    """
    return (os.environ.get("GDES_VERA_AUTOPASTE_CLICK", "1").strip().lower()
            not in ("0", "false", "no", "off"))


def is_supported() -> bool:
    """Only Windows -- the keystroke is sent through the Win32 API."""
    return sys.platform == "win32"


# ------------------------------------------------------------------ #
# Win32 plumbing
# ------------------------------------------------------------------ #

def _win32():
    """Import ctypes/wintypes lazily so this module is importable anywhere."""
    import ctypes
    from ctypes import wintypes
    return ctypes, wintypes


def _foreground_info() -> tuple[str, str]:
    """Return (window_title, executable_basename) of the foreground window.

    Returns ("", "") if it cannot be determined.  Titles are never logged --
    a GDES window title can carry a patient identifier.
    """
    if not is_supported():
        return ("", "")
    try:
        ctypes, wintypes = _win32()
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ("", "")

        length = user32.GetWindowTextLengthW(hwnd)
        title = ""
        if length:
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value or ""

        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        exe = ""
        if pid.value:
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
            if handle:
                try:
                    size = wintypes.DWORD(1024)
                    buf = ctypes.create_unicode_buffer(size.value)
                    if kernel32.QueryFullProcessImageNameW(
                            handle, 0, buf, ctypes.byref(size)):
                        exe = os.path.basename(buf.value or "")
                finally:
                    kernel32.CloseHandle(handle)
        return (title, exe)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("foreground window lookup failed: %s", exc)
        return ("", "")


def _click_input_area() -> bool:
    """Left-click Vera's "Ask" box to put the caret in it before pasting.

    The box is a card in the middle of the page (see CLICK_Y_FRACTION), so the
    click lands at the horizontal centre of the window a little below halfway.
    The cursor is put back where the clinician left it.

    Only ever called after the Vera guard has passed, so the click cannot land
    in another application.
    """
    ctypes, wintypes = _win32()
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False

    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return False

    width = rect.right - rect.left
    height = rect.bottom - rect.top
    if width < 200 or height < 200:
        return False

    x = rect.left + width // 2
    y = rect.top + int(height * click_y_fraction())
    logger.info("auto-paste: clicking Ask box at (%s,%s) in %sx%s window",
                x, y, width, height)

    prev = wintypes.POINT()
    have_prev = bool(user32.GetCursorPos(ctypes.byref(prev)))

    MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.15)

    if have_prev:
        user32.SetCursorPos(prev.x, prev.y)
    return True


def looks_like_vera(title: str, exe: str) -> bool:
    """True only when the window is a known browser AND its title mentions Vera.

    Both halves are required: the browser check stops a paste into a native app,
    and the title check stops a paste into a different tab of the same browser.
    """
    if (exe or "").lower() not in BROWSER_EXES:
        return False
    low = (title or "").lower()
    return any(hint in low for hint in TITLE_HINTS)


def _build_ctrl_v_events():
    """Build the four INPUT records for Ctrl down, V down, V up, Ctrl up.

    Split out from _send_ctrl_v so the ctypes layout can be exercised in tests
    without delivering a real keystroke.  Returns (events_array, INPUT_type).
    """
    ctypes, wintypes = _win32()

    ULONG_PTR = wintypes.WPARAM
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYUP = 0x0002
    VK_CONTROL = 0x11
    VK_V = 0x56

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                    ("dwExtraInfo", ULONG_PTR)]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                    ("wParamH", wintypes.WORD)]

    class _INPUTUNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]

    def key(vk: int, up: bool) -> INPUT:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        # dwExtraInfo is a ULONG_PTR: it must be 0, not None.
        inp.ki = KEYBDINPUT(wVk=vk, wScan=0,
                            dwFlags=KEYEVENTF_KEYUP if up else 0,
                            time=0, dwExtraInfo=0)
        return inp

    events = (INPUT * 4)(
        key(VK_CONTROL, False), key(VK_V, False),
        key(VK_V, True), key(VK_CONTROL, True),
    )
    return events, INPUT


def _send_ctrl_v() -> bool:
    """Send one Ctrl+V through SendInput.  Returns True if it was accepted."""
    ctypes, wintypes = _win32()
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    events, INPUT = _build_ctrl_v_events()

    user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
    user32.SendInput.restype = wintypes.UINT

    sent = user32.SendInput(4, events, ctypes.sizeof(INPUT))
    if sent != 4:
        # Usually UIPI: the foreground window belongs to an elevated process.
        logger.warning("SendInput delivered %s/4 events (err %s)",
                       sent, ctypes.get_last_error())
        return False
    return True


# ------------------------------------------------------------------ #
# Public entry point
# ------------------------------------------------------------------ #

def autopaste_into_vera(timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Wait for the Vera browser window, focus its composer, then send Ctrl+V.

    Returns {"status": ..., "message": ...} where status is one of:
      pasted       -- the keystroke was delivered
      not_focused  -- Vera never became the foreground window (nothing sent)
      send_failed  -- Windows refused the keystroke (nothing pasted)
      unsupported  -- not Windows
      disabled     -- turned off via GDES_VERA_AUTOPASTE=0

    Every outcome is safe: the clipboard still holds the prompt, so the
    clinician can always paste manually.
    """
    manual = "Switch to Vera and press Ctrl+V to paste the case note."

    if not is_enabled():
        return {"status": "disabled", "message": manual}
    if not is_supported():
        return {"status": "unsupported", "message": manual}

    deadline = time.monotonic() + max(0.0, float(timeout))
    matched = False
    while time.monotonic() < deadline:
        title, exe = _foreground_info()
        if looks_like_vera(title, exe):
            matched = True
            # Vera's own page title -- no patient data. Logged because it is
            # the only way to tell "matched the wrong window" from "the paste
            # went nowhere" after the fact.
            logger.info("auto-paste: matched %s window %r", exe, title[:80])
            break
        time.sleep(POLL_INTERVAL)

    if not matched:
        logger.info("auto-paste skipped: Vera window never came to the foreground")
        return {"status": "not_focused", "message": manual}

    # Let the page settle, then re-check: the clinician may have switched away
    # while we waited, and a stale match would paste patient data elsewhere.
    time.sleep(settle_seconds())
    title, exe = _foreground_info()
    if not looks_like_vera(title, exe):
        logger.info("auto-paste aborted: foreground changed during settle")
        return {"status": "not_focused", "message": manual}

    # Put the caret in the composer. Without this the window has focus but no
    # editable element does, so Ctrl+V is silently swallowed -- or worse, lands
    # in the address bar.
    if click_focus_enabled():
        try:
            clicked = _click_input_area()
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("auto-paste: click-to-focus failed: %s", exc)
            clicked = False
        logger.info("auto-paste: click-to-focus %s",
                    "ok" if clicked else "skipped")
        # The click cannot leave the app, but re-check anyway before pasting.
        title, exe = _foreground_info()
        if not looks_like_vera(title, exe):
            logger.info("auto-paste aborted: foreground changed after click")
            return {"status": "not_focused", "message": manual}

    try:
        ok = _send_ctrl_v()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("auto-paste failed: %s", exc)
        ok = False

    if not ok:
        return {"status": "send_failed", "message": manual}

    logger.info("auto-paste: Ctrl+V delivered to the Vera window")
    return {
        "status": "pasted",
        "message": "Case note pasted into Vera. Review it, then press Enter.",
    }
