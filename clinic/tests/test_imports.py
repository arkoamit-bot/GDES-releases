"""Smoke tests for clinic app — module imports work."""

import pytest


class TestClinicImports:
    """Verify clinic app modules import without errors."""

    def test_views_import(self):
        import clinic.views
        assert clinic.views is not None

    def test_urls_import(self):
        import clinic.urls
        assert len(clinic.urls.urlpatterns) > 0

    def test_forms_import(self):
        import clinic.forms
        assert clinic.forms is not None
