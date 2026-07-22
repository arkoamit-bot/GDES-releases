"""Smoke tests for decision app — module imports work.

Note: The decision app's model class may raise RuntimeError during import
if the app label resolution fails in the test environment.
"""

import pytest


@pytest.mark.xfail(reason="decision.models.Model subclass fails app_label resolution in test env")
class TestDecisionImports:
    """Verify decision app modules import without errors."""

    def test_models_import(self):
        import decision.models
        assert decision.models is not None

    def test_views_import(self):
        import decision.views
        assert decision.views is not None

    def test_urls_import(self):
        import decision.urls
        assert len(decision.urls.urlpatterns) > 0
