"""Tests for the SQLite store: idempotent writes and needs_* resume flags.

Runs fully offline against an in-memory database. These characterize the
"idempotent and resumable" contract the pipeline relies on: each stage's
"unfinished" set is defined by the absence (or empty-placeholder presence) of
rows in the next table.
"""

from vista.storage.db import Direction, Paper, Section, Store


def _store() -> Store:
    return Store.open(":memory:")


def _paper(pid: str, **kw) -> Paper:
    base = dict(title=f"Paper {pid}", field="ml", track="recent")
    base.update(kw)
    return Paper(id=pid, **base)


def test_open_initializes_schema():
    s = _store()
    names = {
        r["name"]
        for r in s.conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
        )
    }
    assert {"papers", "sections", "directions", "runs", "v_directions_full"} <= names


def test_upsert_paper_is_idempotent():
    s = _store()
    s.upsert_paper(_paper("W1", cited_by_count=10))
    s.upsert_paper(_paper("W1", cited_by_count=99))  # same id, new value
    rows = s.papers()
    assert len(rows) == 1, "re-upsert must update, not duplicate"
    assert rows[0]["cited_by_count"] == 99


def test_needs_pdf_requires_a_url_and_no_path():
    s = _store()
    s.upsert_paper(_paper("has_url", oa_url="http://x/a.pdf"))
    s.upsert_paper(_paper("no_url"))  # nothing to fetch from
    s.upsert_paper(_paper("done", oa_url="http://x/b.pdf", pdf_path="/tmp/b.pdf"))
    assert {r["id"] for r in s.papers(needs_pdf=True)} == {"has_url"}


def test_flags_progress_through_stages():
    s = _store()
    s.upsert_paper(_paper("W1", oa_url="http://x/a.pdf"))
    # Stage 1: needs a PDF, nothing downstream yet.
    assert [r["id"] for r in s.papers(needs_pdf=True)] == ["W1"]
    assert s.papers(needs_extraction=True) == []
    assert s.papers(needs_analysis=True) == []

    # After fetch.
    s.update_paper_pdf("W1", "/tmp/a.pdf", "2020-01-01")
    assert s.papers(needs_pdf=True) == []
    assert [r["id"] for r in s.papers(needs_extraction=True)] == ["W1"]

    # After extract.
    s.upsert_sections([Section("W1", "conclusion", "Conclusion", "We conclude.")])
    assert s.papers(needs_extraction=True) == []
    assert [r["id"] for r in s.papers(needs_analysis=True)] == ["W1"]

    # After analyze.
    s.replace_directions("W1", [Direction("W1", "Investigate X")])
    assert s.papers(needs_analysis=True) == []


def test_empty_placeholder_section_clears_needs_extraction():
    # The "regex-empty" negative cache: a paper that yielded no real sections
    # still gets a placeholder row so it is not re-extracted forever.
    s = _store()
    s.upsert_paper(_paper("W1", oa_url="http://x/a.pdf"))
    s.update_paper_pdf("W1", "/tmp/a.pdf", "2020-01-01")
    assert [r["id"] for r in s.papers(needs_extraction=True)] == ["W1"]
    s.upsert_sections([Section("W1", "conclusion", None, "", method="regex-empty")])
    assert s.papers(needs_extraction=True) == [], "placeholder row stops re-extraction"


def test_upsert_sections_conflict_updates_in_place():
    s = _store()
    s.upsert_paper(_paper("W1"))
    s.upsert_sections([Section("W1", "conclusion", "C", "first")])
    s.upsert_sections([Section("W1", "conclusion", "C", "second")])  # same key
    secs = s.get_sections("W1")
    assert len(secs) == 1
    assert secs[0]["content"] == "second"


def test_replace_directions_replaces_not_appends():
    s = _store()
    s.upsert_paper(_paper("W1"))
    s.replace_directions("W1", [Direction("W1", "A"), Direction("W1", "B")])
    assert len(s.get_directions("W1")) == 2
    s.replace_directions("W1", [Direction("W1", "C")])
    dirs = s.get_directions("W1")
    assert [d["direction"] for d in dirs] == ["C"]


def test_papers_field_and_track_filters():
    s = _store()
    s.upsert_paper(_paper("a", field="ml", track="recent"))
    s.upsert_paper(_paper("b", field="ai", track="recent"))
    s.upsert_paper(_paper("c", field="ml", track="legacy"))
    assert {r["id"] for r in s.papers(field="ml")} == {"a", "c"}
    assert {r["id"] for r in s.papers(track="recent")} == {"a", "b"}
    assert {r["id"] for r in s.papers(field="ml", track="legacy")} == {"c"}


def test_delete_paper_cascades_to_sections_and_directions():
    # Foreign keys are ON; deleting a paper removes its children.
    s = _store()
    s.upsert_paper(_paper("W1"))
    s.upsert_sections([Section("W1", "conclusion", "C", "x")])
    s.replace_directions("W1", [Direction("W1", "A")])
    with s.tx():
        s.conn.execute("DELETE FROM papers WHERE id = 'W1'")
    assert s.get_sections("W1") == []
    assert s.get_directions("W1") == []


def test_begin_and_finish_run_records_provenance():
    s = _store()
    run_id = s.begin_run({"fields": ["ml"], "track": "recent"})
    s.finish_run(run_id, notes='{"discover": 3}')
    row = s.conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    assert row["finished_at"] is not None
    assert "discover" in row["notes"]


def test_upsert_preserves_fetch_provenance():
    # A re-discover builds Papers with pdf_path=None; it must not clobber the
    # pdf_path/fetched_at that the fetch stage recorded.
    s = _store()
    s.upsert_paper(_paper("W9"))
    s.conn.execute(
        "UPDATE papers SET pdf_path='/tmp/w9.pdf', fetched_at='2026-01-01' WHERE id='W9'"
    )
    s.conn.commit()
    s.upsert_paper(_paper("W9", cited_by_count=123))  # re-discover
    row = s.get_paper("W9")
    assert row["pdf_path"] == "/tmp/w9.pdf", "re-discover must not reset pdf_path"
    assert row["fetched_at"] == "2026-01-01"
    assert row["cited_by_count"] == 123, "other columns still update"
