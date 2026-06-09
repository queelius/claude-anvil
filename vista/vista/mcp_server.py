"""Vista MCP server.

Exposes mechanical research-lookup tools to MCP clients (Claude Code, etc.).
The server returns structured JSON. Synthesis happens in the conversation.

Run: `vista-mcp` (stdio transport).
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from vista.config import FIELDS, USER_AGENT, ensure_dirs
from vista.core import (
    broad_search,
    cache_work,
    fetch_and_extract,
    resolve_identifier,
    seminal_search,
    summarize_paper,
    topic_search,
)
from vista.pipeline.analyze import directions_from_dicts
from vista.pipeline.discover import run_discover
from vista.pipeline.extract import run_extract
from vista.pipeline.fetch import run_fetch
from vista.render.markdown import render_all
from vista.sources.openalex import OpenAlexClient
from vista.storage.db import Store

# Logs to stderr only — stdout is the MCP transport.
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="vista-mcp %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("vista.mcp")

mcp = FastMCP("vista")


def _store() -> Store:
    ensure_dirs()
    return Store.open()


def _http() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"},
        timeout=60.0,
    )


# ---------------------------------------------------------------------------
# On-demand research tools
# ---------------------------------------------------------------------------

@mcp.tool()
def topic_followups(
    topic: str,
    max_papers: int = 8,
    year_min: int = 2020,
    min_citations: int = 30,
    require_arxiv: bool = True,
) -> str:
    """Search OpenAlex for highly-cited recent papers matching a topic, fetch
    their PDFs, extract Future Work / Limitations / Discussion / Conclusion
    sections, and return as structured JSON.

    Use this when the user asks about open problems, salient or timely
    follow-up research, or research directions on a specific topic. The caller
    (the conversation) reads the returned section text and synthesizes
    directions; this tool does no LLM analysis itself.

    Args:
        topic: keyword(s); OpenAlex full-text search syntax accepted (use OR / quotes).
        max_papers: papers to fetch (default 8).
        year_min: only papers from this year or later (default 2020).
        min_citations: citation threshold (default 30; raise for popular fields).
        require_arxiv: restrict to papers also on arXiv (reliable PDF). Set False
            to include paywalled work where we may not be able to fetch the PDF.
    """
    store = _store()
    out: dict[str, Any] = {
        "topic": topic,
        "params": {
            "max_papers": max_papers,
            "year_min": year_min,
            "min_citations": min_citations,
            "require_arxiv": require_arxiv,
        },
        "papers": [],
    }
    with OpenAlexClient() as client, _http() as http:
        works = topic_search(
            client,
            topic=topic,
            year_min=year_min,
            min_citations=min_citations,
            max_papers=max_papers,
            require_arxiv=require_arxiv,
        )
        for w in works:
            cache_work(store, w, field="ad-hoc", track="topic")
            out["papers"].append(fetch_and_extract(store, w.id, http=http))
    out["paper_count"] = len(out["papers"])
    return json.dumps(out, ensure_ascii=False, indent=2)


@mcp.tool()
def paper_followups(identifier: str) -> str:
    """Look up a specific paper and return its Future Work / Limitations /
    Discussion / Conclusion sections.

    Use this when the user asks "what does paper X say about future work" or
    points at a specific reference (DOI, arXiv id, OpenAlex id, or title).

    Args:
        identifier: DOI (10.xxxx/yyy), arXiv id (2106.xxxx or cs/0001234),
            OpenAlex id (Wxxxxx), or paper title.
    """
    store = _store()
    with OpenAlexClient() as client:
        work = resolve_identifier(identifier, client)
    if work is None:
        return json.dumps({"identifier": identifier, "error": "not found"})
    cache_work(store, work, field="ad-hoc", track="paper")
    with _http() as http:
        return json.dumps(
            fetch_and_extract(store, work.id, http=http),
            ensure_ascii=False, indent=2,
        )


@mcp.tool()
def find_seminal(
    topic: str | None = None,
    year_max: int = 2019,
    year_min: int = 2000,
    min_citations: int = 1000,
    max_papers: int = 8,
) -> str:
    """Find older highly-cited papers and return their Future Work sections.

    These are the 'neglected futures' candidates: directions flagged years ago
    where the field may not have followed up. Use when the user wants the
    legacy track or asks about under-explored ideas in classical literature.

    Args:
        topic: optional keyword; omit for a citation-only top-N within the year window.
        year_max: latest publication year to include (default 2019).
        year_min: earliest year (default 2000).
        min_citations: floor; legacy papers in popular fields can sit at ~1000-10000+.
        max_papers: limit (default 8).
    """
    store = _store()
    out: dict[str, Any] = {
        "topic": topic,
        "params": {
            "year_min": year_min,
            "year_max": year_max,
            "min_citations": min_citations,
        },
        "papers": [],
    }
    with OpenAlexClient() as client, _http() as http:
        works = seminal_search(
            client,
            topic=topic,
            year_min=year_min,
            year_max=year_max,
            min_citations=min_citations,
            max_papers=max_papers,
        )
        for w in works:
            cache_work(store, w, field="ad-hoc", track="legacy")
            out["papers"].append(fetch_and_extract(store, w.id, http=http))
    out["paper_count"] = len(out["papers"])
    return json.dumps(out, ensure_ascii=False, indent=2)


@mcp.tool()
def broad_followups(
    query: str,
    fields: list[str] | None = None,
    year_min: int = 2020,
    min_citations: int = 30,
    max_papers: int = 12,
    require_arxiv: bool = True,
) -> str:
    """Cross-field exploratory search. Useful for serendipity: find directions
    in areas the user hasn't worked in, or surface follow-ups that span ML +
    stats, security + ML, etc.

    Args:
        query: keyword(s); OpenAlex search syntax.
        fields: optional list from {"ml","ai","stats","ransomware"}; restricts
            to those concepts.  Omit for fully unconstrained search.
        year_min: default 2020.
        min_citations: default 30 (looser than topic_followups for breadth).
        max_papers: default 12.
        require_arxiv: same as topic_followups.
    """
    store = _store()
    out: dict[str, Any] = {
        "query": query,
        "fields": fields,
        "params": {
            "year_min": year_min,
            "min_citations": min_citations,
            "require_arxiv": require_arxiv,
        },
        "papers": [],
    }
    with OpenAlexClient() as client, _http() as http:
        works = broad_search(
            client,
            query=query,
            fields=fields,
            year_min=year_min,
            min_citations=min_citations,
            max_papers=max_papers,
            require_arxiv=require_arxiv,
        )
        for w in works:
            cache_work(store, w, field="ad-hoc", track="broad")
            out["papers"].append(fetch_and_extract(store, w.id, http=http))
    out["paper_count"] = len(out["papers"])
    return json.dumps(out, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Stored corpus tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_directions(
    query: str,
    field: str | None = None,
    feasibility: str | None = None,
    track: str | None = None,
    user_status: str | None = None,
    limit: int = 25,
) -> str:
    """Search the local catalog of distilled research directions.

    Args:
        query: keyword search across direction text, rationale, and tags.
        field: optional ml | ai | stats | ransomware | ad-hoc.
        feasibility: optional low | medium | high.
        track: optional recent | legacy | seed | topic | broad | paper.
        user_status: optional open | interesting | started | abandoned.
        limit: default 25.
    """
    store = _store()
    clauses = ["(d.direction LIKE ? OR d.rationale LIKE ? OR d.field_tags_json LIKE ?)"]
    like = f"%{query}%"
    params: list[Any] = [like, like, like]
    if field:
        clauses.append("p.field = ?"); params.append(field)
    if feasibility:
        clauses.append("d.feasibility = ?"); params.append(feasibility)
    if track:
        clauses.append("p.track = ?"); params.append(track)
    if user_status:
        clauses.append("d.user_status = ?"); params.append(user_status)
    sql = (
        "SELECT d.id, d.direction, d.rationale, d.feasibility, d.novelty, "
        "       d.field_tags_json, d.user_status, "
        "       p.id AS paper_id, p.title, p.year, p.venue, p.cited_by_count "
        "FROM directions d JOIN papers p ON p.id = d.paper_id "
        "WHERE " + " AND ".join(clauses) +
        " ORDER BY p.cited_by_count DESC LIMIT ?"
    )
    params.append(limit)
    rows = [dict(r) for r in store.conn.execute(sql, params)]
    return json.dumps({"query": query, "count": len(rows), "results": rows},
                      ensure_ascii=False, indent=2)


@mcp.tool()
def get_paper(paper_id: str) -> str:
    """Return a stored paper's full record: metadata, sections, and any
    distilled directions."""
    store = _store()
    row = store.get_paper(paper_id)
    if row is None:
        return json.dumps({"paper_id": paper_id, "error": "not found"})
    sections = store.get_sections(paper_id)
    summary = summarize_paper(row, sections=sections)
    summary["directions"] = [dict(d) for d in store.get_directions(paper_id)]
    return json.dumps(summary, ensure_ascii=False, indent=2)


@mcp.tool()
def list_directions(
    field: str | None = None,
    track: str | None = None,
    user_status: str | None = "open",
    limit: int = 50,
) -> str:
    """List stored directions, paginated. Defaults to user_status='open'."""
    store = _store()
    clauses, params = [], []
    if field:
        clauses.append("p.field = ?"); params.append(field)
    if track:
        clauses.append("p.track = ?"); params.append(track)
    if user_status:
        clauses.append("d.user_status = ?"); params.append(user_status)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    sql = (
        "SELECT d.id, d.direction, d.feasibility, d.novelty, d.user_status, "
        "       p.title, p.year, p.cited_by_count, p.field, p.track "
        "FROM directions d JOIN papers p ON p.id = d.paper_id" + where +
        " ORDER BY p.cited_by_count DESC LIMIT ?"
    )
    params.append(limit)
    rows = [dict(r) for r in store.conn.execute(sql, params)]
    return json.dumps({"count": len(rows), "results": rows},
                      ensure_ascii=False, indent=2)


@mcp.tool()
def submit_directions(paper_id: str, directions: list[dict]) -> str:
    """Write a synthesized list of directions for a paper. Use this when the
    conversation has read a paper's section text and produced structured
    directions worth persisting. Replaces any previous directions for that
    paper.

    Each direction dict supports: direction (required), rationale, quote,
    field_tags (list), feasibility (low|medium|high), novelty (low|medium|high),
    dependencies.
    """
    store = _store()
    if store.get_paper(paper_id) is None:
        return json.dumps({"paper_id": paper_id, "error": "paper not in store"})
    rows = directions_from_dicts(paper_id, directions)
    store.replace_directions(paper_id, rows)
    return json.dumps({"paper_id": paper_id, "stored": len(rows)})


@mcp.tool()
def mark_direction(direction_id: int, status: str, notes: str | None = None) -> str:
    """Update user_status / user_notes on a stored direction.

    Args:
        direction_id: id from search_directions / list_directions.
        status: open | interesting | started | abandoned.
        notes: optional free-form note.
    """
    store = _store()
    if status not in ("open", "interesting", "started", "abandoned"):
        return json.dumps({"error": f"invalid status {status!r}"})
    with store.tx():
        store.conn.execute(
            "UPDATE directions SET user_status=?, user_notes=COALESCE(?, user_notes) "
            "WHERE id=?",
            (status, notes, direction_id),
        )
    return json.dumps({"direction_id": direction_id, "status": status, "notes": notes})


# ---------------------------------------------------------------------------
# Bulk pipeline tools
# ---------------------------------------------------------------------------

@mcp.tool()
def discover(
    fields: list[str] | None = None,
    track: str = "recent",
    per_field: int = 25,
    legacy_per_field: int = 8,
    year_min_recent: int = 2020,
) -> str:
    """Run the bulk discovery stage. Stores paper metadata in the local DB."""
    from vista.config import RunConfig
    fields = fields or list(FIELDS.keys())
    cfg = RunConfig(
        fields=fields, track=track, per_field_limit=per_field,
        legacy_per_field_limit=legacy_per_field, year_min_recent=year_min_recent,
        require_open_access=False,
    )
    store = _store()
    counts = run_discover(store, cfg)
    return json.dumps({"counts": counts})


@mcp.tool()
def extract_pending(max_papers: int = 0) -> str:
    """Fetch PDFs (if missing) and extract sections for any papers not yet
    processed. Idempotent."""
    store = _store()
    fetched = run_fetch(store, max_papers=max_papers or None)
    extracted = run_extract(store, max_papers=max_papers or None)
    return json.dumps({"fetch": fetched, "extract": extracted})


@mcp.tool()
def render_markdown() -> str:
    """Regenerate the markdown index and per-paper files under out/."""
    store = _store()
    counts = render_all(store)
    return json.dumps({"render": counts})


@mcp.tool()
def status() -> str:
    """Show counts of papers, sections, and directions per field/track."""
    store = _store()
    rows = [dict(r) for r in store.conn.execute(
        """
        SELECT p.field, p.track,
               COUNT(*) AS papers,
               SUM(p.pdf_path IS NOT NULL) AS with_pdf,
               SUM(EXISTS(SELECT 1 FROM sections s WHERE s.paper_id=p.id)) AS with_sections,
               SUM(EXISTS(SELECT 1 FROM directions d WHERE d.paper_id=p.id)) AS with_directions
        FROM papers p
        GROUP BY p.field, p.track
        ORDER BY p.field, p.track
        """
    )]
    totals = dict(store.conn.execute(
        "SELECT (SELECT COUNT(*) FROM papers) AS papers, "
        "       (SELECT COUNT(*) FROM directions) AS directions"
    ).fetchone())
    return json.dumps({"totals": totals, "by_field_track": rows},
                      ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# SQL escape hatch
# ---------------------------------------------------------------------------

# Connection-level escapes the engine guard below cannot fully contain.
# Everything else (INSERT/UPDATE/DELETE/DROP/VACUUM INTO/...) is blocked at the
# engine: run_sql executes on a mode=ro connection with PRAGMA query_only=ON,
# so keyword false-positives (a LIKE '%update%' literal, the replace() scalar
# function) no longer reject legitimate read-only queries.
_FORBIDDEN_SQL = re.compile(r"\b(attach|detach|vacuum|pragma)\b", re.IGNORECASE)


def _readonly_conn() -> sqlite3.Connection:
    """A dedicated read-only connection to the store's database file."""
    store = _store()
    db_file = store.conn.execute("PRAGMA database_list").fetchone()[2]
    if not db_file:  # in-memory store (tests): reuse the conn, engine-guarded
        store.conn.execute("PRAGMA query_only=ON")
        return store.conn
    conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


@mcp.tool()
def run_sql(query: str, limit: int = 200) -> str:
    """Run a read-only SQL query against the local store.

    Use the v_directions_full view for the common case (joining directions to
    their parent paper). DDL and DML are blocked. The query is appended with
    LIMIT if it lacks one.
    """
    if _FORBIDDEN_SQL.search(query):
        return json.dumps({"error": "only read-only queries allowed"})
    q = query.strip().rstrip(";")
    if not re.search(r"\blimit\b", q, re.IGNORECASE):
        q = f"{q} LIMIT {int(limit)}"
    conn = _readonly_conn()
    try:
        rows = [dict(r) for r in conn.execute(q)]
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        if conn is not _store().conn:
            conn.close()
        else:
            conn.execute("PRAGMA query_only=OFF")
    return json.dumps({"row_count": len(rows), "rows": rows},
                      ensure_ascii=False, indent=2)


@mcp.tool()
def get_schema() -> str:
    """Return the SQL schema and the v_directions_full view definition."""
    from vista.storage.db import SCHEMA_PATH
    return json.dumps({"schema": SCHEMA_PATH.read_text()})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """stdio MCP entry point. Configured in pyproject as `vista-mcp`."""
    mcp.run()


if __name__ == "__main__":
    main()
