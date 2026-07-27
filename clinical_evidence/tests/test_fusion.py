"""Unit tests for clinical evidence fusion — dedup and type-safe conversion."""

from unittest.mock import MagicMock

from clinical_evidence.providers.base import EvidenceItem
from clinical_evidence.services.fusion import (
    deduplicate,
    _is_duplicate,
    _evidence_result_to_item,
)


# ---------------------------------------------------------------------------
# _evidence_result_to_item
# ---------------------------------------------------------------------------

class TestEvidenceResultToItem:
    def test_converts_all_fields(self):
        result = MagicMock()
        result.source_type = "pubmed"
        result.title = "Test Study"
        result.authors = "Smith J"
        result.journal = "Kidney Int"
        result.publication_date = "2024-01-01"
        result.pmid = "12345"
        result.pmcid = "PMC67890"
        result.doi = "10.1234/test"
        result.abstract = "Test abstract"
        result.url = "http://example.com"
        result.evidence_level = "rct"
        result.study_design = "rct"
        result.citation_count = 50
        result.journal_impact = 5.0
        result.sample_size = 200
        result.keywords = ["kidney"]
        result.mesh_terms = ["nephrol"]
        result.relevance_score = 0.85
        result.raw_data = {"extra": "data"}

        item = _evidence_result_to_item(result)

        assert isinstance(item, EvidenceItem)
        assert item.source_type == "pubmed"
        assert item.title == "Test Study"
        assert item.authors == "Smith J"
        assert item.journal == "Kidney Int"
        assert item.pmid == "12345"
        assert item.pmcid == "PMC67890"
        assert item.doi == "10.1234/test"
        assert item.abstract == "Test abstract"
        assert item.url == "http://example.com"
        assert item.evidence_level == "rct"
        assert item.study_design == "rct"
        assert item.citation_count == 50
        assert item.journal_impact == 5.0
        assert item.sample_size == 200
        assert item.keywords == ["kidney"]
        assert item.mesh_terms == ["nephrol"]
        assert item.relevance_score == 0.85
        assert item.raw_data == {"extra": "data"}

    def test_handles_none_keywords_and_mesh(self):
        result = MagicMock()
        result.source_type = "pubmed"
        result.title = "Test"
        result.authors = ""
        result.journal = ""
        result.publication_date = None
        result.pmid = ""
        result.pmcid = ""
        result.doi = ""
        result.abstract = ""
        result.url = ""
        result.evidence_level = None
        result.study_design = None
        result.citation_count = None
        result.journal_impact = None
        result.sample_size = None
        result.keywords = None
        result.mesh_terms = None
        result.relevance_score = None
        result.raw_data = None

        item = _evidence_result_to_item(result)

        assert item.keywords == []
        assert item.mesh_terms == []
        assert item.raw_data == {}


# ---------------------------------------------------------------------------
# _is_duplicate
# ---------------------------------------------------------------------------

class TestIsDuplicate:
    def test_same_pmid_is_duplicate(self):
        a = MagicMock()
        a.pmid = "12345"
        a.doi = ""
        a.title = "First"
        b = MagicMock()
        b.pmid = "12345"
        b.doi = ""
        b.title = "Second"
        assert _is_duplicate(a, b) is True

    def test_same_doi_is_duplicate(self):
        a = MagicMock()
        a.pmid = ""
        a.doi = "10.1234/test"
        a.title = "First"
        b = MagicMock()
        b.pmid = ""
        b.doi = "10.1234/TEST"
        b.title = "Second"
        assert _is_duplicate(a, b) is True

    def test_similar_title_is_duplicate(self):
        a = MagicMock()
        a.pmid = ""
        a.doi = ""
        a.title = "Treatment of IgA nephropathy with corticosteroids"
        b = MagicMock()
        b.pmid = ""
        b.doi = ""
        b.title = "Treatment of IgA nephropathy with corticosteroids"
        assert _is_duplicate(a, b) is True

    def test_different_titles_not_duplicate(self):
        a = MagicMock()
        a.pmid = ""
        a.doi = ""
        a.title = "Cardiac arrhythmia management"
        b = MagicMock()
        b.pmid = ""
        b.doi = ""
        b.title = "Renal transplant outcomes"
        assert _is_duplicate(a, b) is False

    def test_different_pmid_not_duplicate(self):
        a = MagicMock()
        a.pmid = "11111"
        a.doi = ""
        a.title = "Cardiac arrhythmia management in adults"
        b = MagicMock()
        b.pmid = "22222"
        b.doi = ""
        b.title = "Renal transplant outcomes after five years"
        assert _is_duplicate(a, b) is False


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

class TestDeduplicate:
    def test_removes_pmid_duplicates(self):
        a = MagicMock()
        a.pmid = "12345"
        a.doi = ""
        a.title = "First"
        b = MagicMock()
        b.pmid = "12345"
        b.doi = ""
        b.title = "Second"
        unique = deduplicate([a, b])
        assert len(unique) == 1

    def test_removes_doi_duplicates(self):
        a = MagicMock()
        a.pmid = ""
        a.doi = "10.1234/test"
        a.title = "First"
        b = MagicMock()
        b.pmid = ""
        b.doi = "10.1234/test"
        b.title = "Second"
        unique = deduplicate([a, b])
        assert len(unique) == 1

    def test_keeps_unique_items(self):
        a = MagicMock()
        a.pmid = "11111"
        a.doi = "10.1111/a"
        a.title = "Cardiac arrhythmia management in adults"
        b = MagicMock()
        b.pmid = "22222"
        b.doi = "10.2222/b"
        b.title = "Renal transplant outcomes after five years"
        c = MagicMock()
        c.pmid = "33333"
        c.doi = "10.3333/c"
        c.title = "Diabetic nephropathy progression and treatment"
        unique = deduplicate([a, b, c])
        assert len(unique) == 3

    def test_empty_list_returns_empty(self):
        assert deduplicate([]) == []

    def test_single_item_returns_single(self):
        a = MagicMock()
        a.pmid = "12345"
        a.doi = ""
        a.title = "Only one"
        assert len(deduplicate([a])) == 1
