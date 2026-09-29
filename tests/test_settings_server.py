"""bgddr.settings_server: the LAN server profile (deploy/windows).

Each case imports the settings module in a fresh interpreter with a controlled
environment, so the test process's own settings are untouched.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOOD = {
    "DJANGO_SECRET_KEY": "x" * 64,
    "DJANGO_ALLOWED_HOSTS": "192.168.7.55,dr-wasim,127.0.0.1",
    "GDES_CSRF_TRUSTED_ORIGINS": "http://192.168.7.55:8080",
    "POSTGRES_PASSWORD": "a" * 32,
}
PROBE = (
    "import json, bgddr.settings_server as s;"
    "print(json.dumps({'debug': s.DEBUG, 'engine': s.DATABASES['default']['ENGINE'],"
    "'session': s.SESSION_COOKIE_NAME, 'csrf': s.CSRF_COOKIE_NAME,"
    "'secure': s.SESSION_COOKIE_SECURE, 'hosts': s.ALLOWED_HOSTS,"
    "'origins': s.CSRF_TRUSTED_ORIGINS, 'health': s.DATABASES['default']['CONN_HEALTH_CHECKS']}))"
)


def _load(tmp_path, **env):
    data = tmp_path / "gdes-data"
    base = {k: v for k, v in os.environ.items()
            if not k.startswith(("DJANGO_", "POSTGRES_", "GDES_", "BGDDR_"))}
    base.update({"BGDDR_DATA_DIR": str(data), "GDES_ENV_FILE": str(tmp_path / "none.env")})
    base.update(env)
    return subprocess.run([sys.executable, "-c", PROBE], cwd=ROOT, env=base,
                          capture_output=True, text=True)


def test_server_profile(tmp_path):
    out = _load(tmp_path, **GOOD)
    assert out.returncode == 0, out.stderr
    cfg = json.loads(out.stdout.strip().splitlines()[-1])
    assert cfg["debug"] is False
    assert cfg["engine"] == "django.db.backends.postgresql"
    # Distinct from DKD's cookies on the same host (browsers ignore the port).
    assert cfg["session"] == "gdes_sessionid" and cfg["csrf"] == "gdes_csrftoken"
    assert cfg["secure"] is False                        # phase 1: plain HTTP LAN
    assert cfg["hosts"] == ["192.168.7.55", "dr-wasim", "127.0.0.1"]
    assert cfg["origins"] == ["http://192.168.7.55:8080"]
    assert cfg["health"] is True


def test_https_makes_cookies_secure(tmp_path):
    out = _load(tmp_path, GDES_HTTPS="1", **GOOD)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout.strip().splitlines()[-1])["secure"] is True


def test_refuses_missing_secret_hosts_or_db_password(tmp_path):
    for missing in ("DJANGO_SECRET_KEY", "DJANGO_ALLOWED_HOSTS", "POSTGRES_PASSWORD"):
        env = {k: v for k, v in GOOD.items() if k != missing}
        out = _load(tmp_path, **env)
        assert out.returncode != 0 and missing in out.stderr, missing


def test_refuses_synced_data_dir(tmp_path):
    out = _load(tmp_path, BGDDR_DATA_DIR=str(tmp_path / "OneDrive" / "gdes"), **GOOD)
    assert out.returncode != 0 and "cloud-synced" in out.stderr


def test_reads_env_file(tmp_path):
    env_file = tmp_path / "server.env"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in GOOD.items()), encoding="utf-8")
    out = _load(tmp_path, GDES_ENV_FILE=str(env_file))
    assert out.returncode == 0, out.stderr
