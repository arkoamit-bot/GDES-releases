"""GitHub self-update: auth-header + private/public download-URL selection."""
from desktop import launcher


def test_headers_public_no_auth(monkeypatch):
    monkeypatch.setattr(launcher, "_GITHUB_TOKEN", "")
    h = launcher._github_headers()
    assert "Authorization" not in h
    assert h["User-Agent"] == "GDES-Updater"


def test_headers_private_adds_bearer(monkeypatch):
    monkeypatch.setattr(launcher, "_GITHUB_TOKEN", "ghp_secret")
    h = launcher._github_headers(accept="application/octet-stream")
    assert h["Authorization"] == "Bearer ghp_secret"
    assert h["Accept"] == "application/octet-stream"


def test_version_compare():
    # shared with the OneDrive channel
    from bgddr.updater import is_newer
    assert is_newer("6.6.1", "6.5.0") is True
    assert is_newer("6.6.1", "6.6.1") is False
    assert is_newer("6.6.0", "6.6.1") is False


def test_apply_update_writes_breadcrumb_and_visible_helper(tmp_path, monkeypatch):
    """apply_update must log a breadcrumb BEFORE spawning (so a blocked helper is
    diagnosable) and spawn a VISIBLE console (not hidden), with a robust helper."""
    from bgddr import updater

    spawned = {}
    def fake_popen(args, creationflags=0, close_fds=True):
        spawned["args"] = args
        spawned["flags"] = creationflags
        return object()
    monkeypatch.setattr(updater.subprocess, "Popen", fake_popen)
    # The flag only exists on Windows; supply it so the check also runs on Linux CI.
    monkeypatch.setattr(updater.subprocess, "CREATE_NEW_CONSOLE", 0x10, raising=False)

    app = tmp_path / "app"; (app / "Logs").mkdir(parents=True)
    staging = tmp_path / "staging"; staging.mkdir()
    log_file = app / "Logs" / "update.log"

    ok = updater.apply_update(app_dir=app, staging_root=staging,
                              old_version="7.3.5", new_version="7.3.6",
                              log_path=log_file)
    assert ok is True
    # breadcrumb written before spawn
    assert "spawning helper 7.3.5 -> 7.3.6" in log_file.read_text(encoding="utf-8")
    # NOT hidden (no -WindowStyle Hidden) -> AV-friendly visible console
    assert "-WindowStyle" not in spawned["args"] or "Hidden" not in spawned["args"]
    create_new_console = getattr(updater.subprocess, "CREATE_NEW_CONSOLE", 0x10)
    assert spawned["flags"] & create_new_console
    # helper script hardened: retry + GDES.exe naming
    helper_text = (updater.Path(updater.tempfile.gettempdir()) / "gdes_update_7.3.6.ps1").read_text(encoding="utf-8")
    assert "MoveRetry" in helper_text and "GDES.exe" in helper_text
