"""Offline tests for identifier resolution dispatch.

resolve_identifier classifies a free-form string (OpenAlex id, DOI, arXiv id,
or title) and calls the right client method. A fake client records the calls,
so no network is touched.
"""

from vista.core import resolve_identifier
from vista.sources.openalex import OpenAlexWork


def _work(**kw) -> OpenAlexWork:
    base = dict(
        id="W1", doi=None, title="T", abstract=None, year=None, venue=None,
        venue_id=None, cited_by_count=0, authors=[], oa_url=None, pdf_url=None,
        arxiv_id=None, raw={},
    )
    base.update(kw)
    return OpenAlexWork(**base)


class FakeClient:
    def __init__(self, *, work=None, works_list=None):
        self.work = work
        self.works_list = works_list or []
        self.calls = []

    def work_by_id(self, wid):
        self.calls.append(("by_id", wid))
        return self.work

    def work_by_doi(self, doi):
        self.calls.append(("by_doi", doi))
        return self.work

    def works(self, **kw):
        self.calls.append(("works", kw))
        return iter(self.works_list)


def test_resolve_bare_openalex_id():
    c = FakeClient(work=_work(id="W42"))
    out = resolve_identifier("W42", c)
    assert out.id == "W42"
    assert c.calls == [("by_id", "W42")]


def test_resolve_openalex_url_is_stripped():
    c = FakeClient(work=_work(id="W42"))
    resolve_identifier("https://openalex.org/W42", c)
    assert c.calls == [("by_id", "W42")]


def test_resolve_doi():
    c = FakeClient(work=_work())
    resolve_identifier("10.1109/tnnls.2020.2978386", c)
    assert c.calls[0] == ("by_doi", "10.1109/tnnls.2020.2978386")


def test_resolve_arxiv_id_matches_within_results():
    target = _work(id="Wx", arxiv_id="2106.01234")
    c = FakeClient(works_list=[_work(id="Wo", arxiv_id="2000.99999"), target])
    out = resolve_identifier("2106.01234", c)
    assert out is target
    assert c.calls[0][0] == "works"


def test_resolve_title_fallback():
    target = _work(id="Wt", title="A Comprehensive Survey on Graph Neural Networks")
    c = FakeClient(works_list=[target])
    out = resolve_identifier("A Comprehensive Survey on Graph Neural Networks", c)
    assert out is target


def test_resolve_returns_none_when_nothing_matches():
    c = FakeClient(works_list=[])
    assert resolve_identifier("Totally Unmatched Title Xyzzy", c) is None
