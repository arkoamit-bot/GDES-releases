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
