"""Tests for OpenAlex parsing and filter building. Offline; no network.

Covers the conventions documented in CLAUDE.md: OpenAlex IDs are stripped of
their URL prefix at parse time, abstracts are reconstructed from the inverted
index, and arXiv ids are sniffed from any location URL.
"""

from vista.sources.openalex import OpenAlexWork, _invert_abstract, build_filter

WORK = {
    "id": "https://openalex.org/W2907492528",
    "doi": "https://doi.org/10.1109/tnnls.2020.2978386",
    "display_name": "A Comprehensive Survey on Graph Neural Networks",
    "publication_year": 2020,
    "cited_by_count": 9100,
    "abstract_inverted_index": {"Deep": [0], "learning": [1], "rocks": [2]},
    "primary_location": {
        "source": {"display_name": "IEEE TNNLS", "id": "https://openalex.org/S123"},
        "landing_page_url": "https://arxiv.org/abs/1901.00596",
        "pdf_url": "https://arxiv.org/pdf/1901.00596v3",
    },
    "locations": [
        {
            "is_oa": True,
            "pdf_url": "https://arxiv.org/pdf/1901.00596v3",
            "landing_page_url": "https://arxiv.org/abs/1901.00596",
        }
    ],
    "open_access": {"oa_url": "https://arxiv.org/pdf/1901.00596"},
    "authorships": [
        {"author": {"display_name": "Zonghan Wu", "orcid": "0000-0001"}},
        {"author": {"display_name": "Shirui Pan"}},
    ],
}


def test_from_api_strips_openalex_id_prefix():
    assert OpenAlexWork.from_api(WORK).id == "W2907492528"


def test_from_api_strips_venue_id_prefix():
    w = OpenAlexWork.from_api(WORK)
    assert w.venue_id == "S123"
    assert w.venue == "IEEE TNNLS"


def test_from_api_reconstructs_abstract_in_order():
    assert OpenAlexWork.from_api(WORK).abstract == "Deep learning rocks"


def test_from_api_detects_arxiv_id():
    assert OpenAlexWork.from_api(WORK).arxiv_id == "1901.00596"


def test_from_api_maps_authors():
    names = [a["name"] for a in OpenAlexWork.from_api(WORK).authors]
    assert names == ["Zonghan Wu", "Shirui Pan"]


def test_from_api_minimal_record_defaults():
    w = OpenAlexWork.from_api({"id": "W1", "display_name": "Bare"})
    assert w.id == "W1"
    assert w.title == "Bare"
    assert w.cited_by_count == 0
    assert w.abstract is None
    assert w.arxiv_id is None
    assert w.authors == []
    assert w.venue is None


def test_invert_abstract_none_and_empty():
    assert _invert_abstract(None) is None
    assert _invert_abstract({}) is None


def test_invert_abstract_orders_by_position_with_repeats():
    inv = {"hello": [0], "world": [1], "again": [2, 4], "now": [3]}
    assert _invert_abstract(inv) == "hello world again now again"


def test_build_filter_concepts_and_keyword():
    f = build_filter(concept_ids=["C1", "C2"], keyword_search="graph nets", is_oa=None)
    assert "concepts.id:C1|C2" in f
    assert "title_and_abstract.search:graph nets" in f
    assert "is_oa" not in f


def test_build_filter_year_range_and_citation_floor():
    f = build_filter(year_min=2010, year_max=2020, min_citations=30, is_oa=None)
    assert "publication_year:2010-2020" in f
    assert "cited_by_count:>29" in f  # >= 30 expressed as > 29


def test_build_filter_year_min_only():
    assert "publication_year:>2019" in build_filter(year_min=2020, is_oa=None)


def test_build_filter_is_oa_toggle():
    assert "is_oa:true" in build_filter()  # default
    assert "is_oa:false" in build_filter(is_oa=False)
