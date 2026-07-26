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
# Let the page finish loading and focus its input after the window appears.
SETTLE_SECONDS = 1.5


def is_enabled() -> bool:
    """Auto-paste is on by default on Windows; GDES_VERA_AUTOPASTE=0 disables."""
    return (os.environ.get("GDES_VERA_AUTOPASTE", "1").strip().lower()
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
    """Wait for the Vera browser window, then send one Ctrl+V.

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
            break
        time.sleep(POLL_INTERVAL)

    if not matched:
        logger.info("auto-paste skipped: Vera window never came to the foreground")
        return {"status": "not_focused", "message": manual}

    # Let the page settle, then re-check: the clinician may have switched away
    # while we waited, and a stale match would paste patient data elsewhere.
    time.sleep(SETTLE_SECONDS)
    title, exe = _foreground_info()
    if not looks_like_vera(title, exe):
        logger.info("auto-paste aborted: foreground changed during settle")
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
