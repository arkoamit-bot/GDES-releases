"""P1-2 version-gated seeding + P1-3 health summary."""
import pytest

from knowledge import kb_version as kv


@pytest.fixture
def stamp(tmp_path, monkeypatch):
    p = tmp_path / ".kb_version"
    monkeypatch.setattr(kv, "_stamp_path", lambda: p)
    return p


def test_should_seed_when_no_stamp(stamp):
    assert kv.get_installed_kb_version() is None
    assert kv.should_seed_kb("6.5") is True


def test_should_seed_when_packaged_newer(stamp):
    kv.stamp_kb_version("6.4")
    assert kv.should_seed_kb("6.5") is True


def test_should_not_seed_when_same_version(stamp):
    kv.stamp_kb_version("6.5")
    assert kv.should_seed_kb("6.5") is False


def test_should_not_seed_when_installed_newer(stamp):
    kv.stamp_kb_version("7.0")
    assert kv.should_seed_kb("6.5") is False


def test_stamp_roundtrip(stamp):
    kv.stamp_kb_version("6.5")
    assert kv.get_installed_kb_version() == "6.5"


def test_version_parse_handles_nonnumeric():
    assert kv._parse("6.5") == (6, 5)
    assert kv._parse("6.5a") == (6, 0)
    assert kv._parse("7") > kv._parse("6.9")


# --- P1-3 health summary (uses the deterministic test KB from conftest) ------
@pytest.mark.django_db
def test_health_summary_ok_with_active_rules(django_db_setup):
    summary = kv.kb_health_summary()
    assert summary["rules_active"] > 0
    assert summary["status"] == "ok"
    assert summary["critical"] == []


# --- P1-2 seeder idempotency (seed twice -> identical counts) ----------------
@pytest.mark.django_db
def test_seed_knowledge_base_is_idempotent(django_db_setup):
    from django.core.management import call_command
    from knowledge.models import KnowledgeBaseEntry
    import io
    sink = io.StringIO()
    call_command("seed_knowledge_base", stdout=sink, verbosity=0)
    first = KnowledgeBaseEntry.objects.count()
    call_command("seed_knowledge_base", stdout=sink, verbosity=0)
    second = KnowledgeBaseEntry.objects.count()
    assert first == second
