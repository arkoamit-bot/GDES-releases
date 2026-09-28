"""Smoke tests for treatments app — module imports work."""

import pytest


class TestTreatmentsImports:
    """Verify treatments app modules import without errors."""

    def test_models_import(self):
        import treatments.models
        assert treatments.models is not None
        assert hasattr(treatments.models, "DrugMaster")

    def test_views_import(self):
        import treatments.views
        assert treatments.views is not None

    def test_urls_import(self):
        import treatments.urls
        assert len(treatments.urls.urlpatterns) > 0

    def test_admin_import(self):
        import treatments.admin
        assert treatments.admin is not None
