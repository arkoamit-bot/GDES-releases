"""Smoke tests for users app — module imports work."""

import pytest


class TestUsersImports:
    """Verify users app modules import without errors."""

    def test_models_import(self):
        import users.models
        assert users.models is not None

    def test_views_import(self):
        import users.views
        assert users.views is not None

    def test_urls_import(self):
        import users.urls
        assert len(users.urls.urlpatterns) > 0

    def test_admin_import(self):
        import users.admin
        assert users.admin is not None
