"""Drug Intelligence feature — seeder idempotency + pages."""
import io

import pytest
from django.core.management import call_command

pytestmark = pytest.mark.django_db


def _seed():
    call_command("seed_drug_intelligence", stdout=io.StringIO())


def test_seed_is_idempotent_and_links_indications():
    from knowledge.models import DrugIntelligence, Disease
    # The seeder links only Disease rows that exist; create one so linking is tested.
    Disease.objects.get_or_create(id="membranous", defaults={"name": "Membranous Nephropathy"})
    _seed()
    first = DrugIntelligence.objects.count()
    assert first >= 10
    _seed()
    assert DrugIntelligence.objects.count() == first  # no duplicates
    rtx = DrugIntelligence.objects.get(pk="rituximab")
    assert rtx.drug_class
    assert rtx.indications.filter(pk="membranous").exists()
    assert rtx.serious_side_effects  # JSON list populated


def _client():
    from django.test import Client
    from django.contrib.auth import get_user_model
    u = get_user_model().objects.create_superuser("didx", password="x123456")
    c = Client(); c.force_login(u)
    return c


def test_list_page_lists_drugs():
    _seed()
    c = _client()
    r = c.get("/clinic/drugs/", HTTP_HOST="localhost")
    assert r.status_code == 200
    assert b"Rituximab" in r.content


def test_search_filters():
    _seed()
    c = _client()
    r = c.get("/clinic/drugs/?q=tacro", HTTP_HOST="localhost")
    body = r.content.decode()
    assert "Tacrolimus" in body and "Rituximab" not in body


def test_detail_page_renders_monograph():
    _seed()
    c = _client()
    r = c.get("/clinic/drugs/rituximab/", HTTP_HOST="localhost")
    assert r.status_code == 200
    body = r.content.decode().lower()
    assert "mechanism" in body and "hepatitis b" in body


def test_unknown_drug_404():
    _seed()
    c = _client()
    assert c.get("/clinic/drugs/nope/", HTTP_HOST="localhost").status_code == 404
