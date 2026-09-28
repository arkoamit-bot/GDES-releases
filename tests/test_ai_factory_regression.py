"""AI Factory regression tests — validate quality gates and infrastructure."""

import importlib
import sys
from pathlib import Path


class TestAIFactoryQualityGates:
    """Validate AI Factory quality gates defined in QUALITY_GATES.md."""

    def test_ruff_lint_module_importable(self):
        """Gate 1: Ruff linting — tool must be available."""
        import ruff  # noqa: F401
        assert ruff is not None

    def test_pytest_available(self):
        """Gate 3: pytest testing framework."""
        import pytest  # noqa: F401
        assert pytest.__version__ is not None

    def test_django_settings_module_set(self):
        """Verify Django settings are configured for tests."""
        from django.conf import settings
        assert settings.configured
        assert "clinical_reasoning" in settings.INSTALLED_APPS

    def test_key_apps_importable(self):
        """Critical apps must import without errors."""
        apps = [
            "clinical_reasoning",
            "analytics",
            "patients",
            "labs",
            "knowledge",
            "treatments",
        ]
        for app in apps:
            try:
                importlib.import_module(app)
            except ImportError as e:
                pytest.fail(f"App {app} failed to import: {e}")

    def test_no_circular_imports_in_critical_apps(self):
        """Verify that importing views, services, and models doesn't crash."""
        critical_paths = [
            "clinical_reasoning.views",
            "clinical_reasoning.services.engine",
            "clinical_reasoning.services.care_pathway",
            "clinical_reasoning.services.management_plan",
            "analytics.views",
            "analytics.services.prediction",
            "patients.models",
            "labs.services.results",
        ]
        for path in critical_paths:
            try:
                importlib.import_module(path)
            except ImportError as e:
                pytest.fail(f"Circular import in {path}: {e}")

    def test_migration_files_exist(self):
        """Gate 4: Migration Consistency — every app has a migrations dir."""
        apps_dir = Path(__file__).parent.parent
        apps_with_migrations = []
        apps_without_migrations = []
        for item in apps_dir.iterdir():
            if not item.is_dir():
                continue
            init_file = item / "__init__.py"
            if not init_file.exists():
                continue
            mig_dir = item / "migrations"
            if mig_dir.is_dir() and list(mig_dir.glob("*.py")):
                apps_with_migrations.append(item.name)
            else:
                apps_without_migrations.append(item.name)
        # At minimum, the core apps should have migrations
        core = {"clinical_reasoning", "analytics", "patients", "labs", "treatments"}
        missing = core - set(apps_with_migrations)
        assert not missing, f"Core apps missing migrations: {missing}"

    def test_hermes_agent_config_exists(self):
        """Verify .hermes/ directory structure is intact."""
        hermes_dir = Path(__file__).parent.parent / ".hermes"
        required = [
            "HERMES_SYSTEM.md",
            "HERMES_MASTER_BOOTSTRAP.md",
            "workflows/QUALITY_GATES.md",
            "memory/KNOWN_ISSUES.md",
            "memory/PROJECT_MEMORY.md",
        ]
        missing = [r for r in required if not (hermes_dir / r).exists()]
        assert not missing, f"Missing .hermes files: {missing}"
