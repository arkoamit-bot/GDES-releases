"""V8 Layer 5 — gated online evidence retrieval (safety guards, no network)."""
import pytest

from clinical_reasoning.services import evidence_retrieval as ev


def test_disabled_by_default(settings):
    settings.AI_ONLINE_EVIDENCE_ENABLED = False
    assert ev.is_enabled() is False
    with pytest.raises(ev.EvidenceRetrievalDisabled):
        ev.search_evidence("IgA nephropathy treatment")


def test_phi_guard_blocks_identifier_like_queries(settings):
    settings.AI_ONLINE_EVIDENCE_ENABLED = True  # even when enabled…
    with pytest.raises(ValueError):
        ev.search_evidence("patient MRN 123456 IgA")   # digit run
    with pytest.raises(ValueError):
        ev.search_evidence("contact john@example.com")  # email


def test_only_pubmed_is_an_approved_source():
    assert ev.APPROVED_SOURCES == ("PubMed / PubMed Central (NCBI)",)
