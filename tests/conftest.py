"""Shared test fixtures for the GDES test suite.

Separates testing into three layers:
  1. Unit tests     — no database, no knowledge, pure business logic
  2. Integration tests — use deterministic test knowledge fixture
  3. Acceptance tests — rely on production knowledge base (seeded separately)
"""
import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Load the deterministic test knowledge base once per test session.

    Integration tests that need rules should depend on this fixture or
    call load_test_knowledge() directly.
    """
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command("load_test_knowledge")
