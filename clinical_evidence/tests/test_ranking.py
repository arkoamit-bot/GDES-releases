"""Unit tests for clinical evidence ranking — clinical relevance scoring."""

import pytest
from datetime import date

from clinical_evidence.providers.base import EvidenceItem
from clinical_evidence.services.ranking import (
    score_item,
    rank_items,
    _kidney_relevance_score,
    _disease_specificity_score,
)


def _make_item(**overrides) -> EvidenceItem:
    defaults = {
        "source_type": "pubmed",
        "title": "",
        "authors": "",
        "journal": "",
        "publication_date": None,
        "pmid": "",
        "pmcid": "",
        "doi": "",
        "abstract": "",
        "url": "",
        "evidence_level": None,
        "study_design": None,
        "citation_count": None,
        "journal_impact": None,
        "sample_size": None,
        "keywords": [],
        "mesh_terms": [],
        "relevance_score": None,
        "raw_data": {},
    }
    defaults.update(overrides)
    return EvidenceItem(**defaults)


# ---------------------------------------------------------------------------
# score_item
# ---------------------------------------------------------------------------

class TestScoreItem:
    def test_minimal_item_returns_baseline_score(self):
        item = _make_item()
        score = score_item(item)
        assert score == pytest.approx(50.0)

    def test_meta_analysis_adds_high_evidence_level_score(self):
        item = _make_item(evidence_level="1a")
        score = score_item(item)
        # 50 + (100 * 0.25) = 75
        assert score == pytest.approx(75.0)

    def test_rct_adds_high_score(self):
        item = _make_item(evidence_level="1b")
        score = score_item(item)
        # 50 + (90 * 0.25) = 72.5
        assert score == pytest.approx(72.5)

    def test_expert_opinion_adds_low_score(self):
        item = _make_item(evidence_level="5")
        score = score_item(item)
        # 50 + (20 * 0.25) = 55
        assert score == pytest.approx(55.0)

    def test_study_design_meta_analysis_adds_score(self):
        item = _make_item(study_design="meta_analysis")
        score = score_item(item)
        # 50 + (100 * 0.15) = 65
        assert score == pytest.approx(65.0)

    def test_recent_publication_gets_full_recency_score(self):
        item = _make_item(publication_date=date.today())
        score = score_item(item)
        # 50 + (100 * 0.15) = 65
        assert score == pytest.approx(65.0)

    def test_old_publication_gets_decayed_score(self):
        item = _make_item(publication_date=date(2015, 1, 1))
        score = score_item(item)
        # 50 + recency * 0.15 — old paper should be less than 65
        assert score < 65.0

    def test_high_citation_count_adds_score(self):
        item = _make_item(citation_count=1000)
        score = score_item(item)
        assert score > 50.0

    def test_zero_citation_count_does_not_crash(self):
        item = _make_item(citation_count=0)
        score = score_item(item)
        assert score == pytest.approx(50.0)

    def test_large_sample_size_adds_score(self):
        item = _make_item(sample_size=10000)
        score = score_item(item)
        assert score > 50.0

    def test_kidney_journal_adds_score(self):
        item = _make_item(journal="Kidney International")
        score = score_item(item)
        assert score > 50.0

    def test_non_kidney_journal_no_kidney_bonus(self):
        item = _make_item(journal="Nature Medicine")
        score = score_item(item)
        # No kidney journal bonus, just baseline
        assert score == pytest.approx(50.0)

    def test_kidney_keyword_in_title_adds_score(self):
        item = _make_item(title="Proteinuria in glomerulonephritis")
        score = score_item(item)
        assert score > 50.0

    def test_disease_specificity_increases_score(self):
        item = _make_item(
            title="IgA nephropathy treatment outcomes",
            keywords=["iga_nephropathy"],
        )
        score = score_item(item, disease_id="iga_nephropathy")
        assert score > 50.0

    def test_score_capped_at_100(self):
        item = _make_item(
            evidence_level="meta_analysis",
            study_design="meta_analysis",
            publication_date=date.today(),
            citation_count=10000,
            journal="Kidney International",
            title="glomerulonephritis treatment",
            keywords=["kidney", "nephrol", "glomerulonephritis"],
            mesh_terms=["kidney", "nephrol"],
            sample_size=50000,
            relevance_score=1.0,
        )
        score = score_item(item, disease_id="glomerulonephritis")
        assert score <= 100.0

    def test_score_floor_at_0(self):
        # This shouldn't normally happen with valid inputs, but verify clamp
        item = _make_item()
        score = score_item(item)
        assert score >= 0.0


# ---------------------------------------------------------------------------
# _kidney_relevance_score
# ---------------------------------------------------------------------------

class TestKidneyRelevanceScore:
    def test_kidney_journal_gets_high_score(self):
        item = _make_item(journal="Journal of the American Society of Nephrology")
        score = _kidney_relevance_score(item)
        assert score >= 40.0

    def test_kidney_keyword_in_title_increases_score(self):
        item = _make_item(title="Renal outcomes in CKD")
        score = _kidney_relevance_score(item)
        assert score > 0.0

    def test_kidney_keyword_in_mesh_increases_score(self):
        item = _make_item(mesh_terms=["glomerulonephritis", "proteinuria"])
        score = _kidney_relevance_score(item)
        assert score > 0.0

    def test_non_kidney_item_scores_zero(self):
        item = _make_item(title="Cardiac arrhythmia", journal="JAMA Cardiology")
        score = _kidney_relevance_score(item)
        assert score == 0.0

    def test_score_capped_at_100(self):
        item = _make_item(
            journal="Kidney International",
            title="kidney renal nephrol glomerulonephritis",
            keywords=["kidney", "nephrol", "renal"],
            mesh_terms=["kidney", "nephrol", "renal"],
        )
        score = _kidney_relevance_score(item)
        assert score <= 100.0


# ---------------------------------------------------------------------------
# _disease_specificity_score
# ---------------------------------------------------------------------------

class TestDiseaseSpecificityScore:
    def test_exact_disease_in_title_returns_100(self):
        item = _make_item(title="IgA nephropathy treatment outcomes")
        score = _disease_specificity_score(item, "iga_nephropathy")
        assert score == 100.0

    def test_disease_terms_in_keywords_increases_score(self):
        item = _make_item(keywords=["iga", "nephropathy"])
        score = _disease_specificity_score(item, "iga_nephropathy")
        assert score > 0.0

    def test_no_match_returns_zero(self):
        item = _make_item(title="Cardiac arrhythmia", keywords=["heart"])
        score = _disease_specificity_score(item, "iga_nephropathy")
        assert score == 0.0

    def test_partial_term_match_scales(self):
        item = _make_item(keywords=["nephropathy"])
        score = _disease_specificity_score(item, "iga_nephropathy")
        # "iga" is 3 chars (filtered), only "nephropathy" matches => 1/1 * 80 = 80
        assert 0 < score <= 80


# ---------------------------------------------------------------------------
# rank_items
# ---------------------------------------------------------------------------

class TestRankItems:
    def test_returns_same_count(self):
        items = [_make_item() for _ in range(5)]
        ranked = rank_items(items)
        assert len(ranked) == 5

    def test_high_evidence_item_ranks_first(self):
        low = _make_item(evidence_level="5", title="Low quality")
        high = _make_item(evidence_level="1a", title="High quality")
        ranked = rank_items([low, high])
        assert ranked[0].title == "High quality"

    def test_relevance_score_set_on_ranked_items(self):
        items = [_make_item(evidence_level="meta_analysis")]
        ranked = rank_items(items)
        assert ranked[0].relevance_score is not None
        assert 0 <= ranked[0].relevance_score <= 1.0

    def test_empty_list_returns_empty(self):
        assert rank_items([]) == []

    def test_kidney_journal_ranks_higher_than_non_kidney(self):
        kidney = _make_item(journal="Kidney International", title="renal study")
        non_kidney = _make_item(journal="JAMA Cardiology", title="heart study")
        ranked = rank_items([non_kidney, kidney])
        assert ranked[0].title == "renal study"
