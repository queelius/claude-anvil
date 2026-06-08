"""Core helpers for on-demand research lookups.

These functions wrap the discover/fetch/extract pipeline for use by the MCP
server. Each call: search OpenAlex live, cache PDFs and extracted sections to
the local store, and return a structured payload the conversation can read.

The MCP layer is mechanical. No LLM calls happen here. Synthesis is the
caller's job.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
import re
from pathlib import Path
from typing import Any

import httpx

from vista.config import ARXIV_SOURCE_ID, FIELDS, USER_AGENT
from vista.pipeline.extract import extract_paper
from vista.pipeline.fetch import fetch_pdf
from vista.sources.openalex import OpenAlexClient, OpenAlexWork, build_filter
from vista.storage.db import Paper, Section, Store

log = logging.getLogger(__name__)

ARXIV_RE = re.compile(r"^(?:arxiv:)?(\d{4}\.\d{4,5}|[a-z\-]+/\d{7})$", re.IGNORECASE)
DOI_RE = re.compile(r"^(?:doi:|https?://(?:dx\.)?doi\.org/)?(10\.\d{4,9}/\S+)$", re.IGNORECASE)
OPENALEX_RE = re.compile(r"^(?:https?://openalex\.org/)?(W\d+)$")


# ---------------------------------------------------------------------------
# Identifier resolution
# ---------------------------------------------------------------------------

def resolve_identifier(identifier: str, client: OpenAlexClient) -> OpenAlexWork | None:
    """Resolve a free-form paper identifier (DOI, arXiv id, OpenAlex id, or title)."""
    s = identifier.strip()
    m = OPENALEX_RE.match(s)
    if m:
        return client.work_by_id(m.group(1))
    m = DOI_RE.match(s)
    if m:
        return client.work_by_doi(m.group(1))
    m = ARXIV_RE.match(s)
    if m:
        # Search by arXiv id via locations filter.
        for w in client.works(
            filter_str=f"locations.source.id:{ARXIV_SOURCE_ID}",
            per_page=5,
            max_results=5,
            sort="cited_by_count:desc",
        ):
            if w.arxiv_id and w.arxiv_id.lower() == m.group(1).lower():
                return w
        return None
    # Fall back to title search.
    for w in client.works(
        filter_str=f"title.search:{s}", per_page=5, max_results=5, sort="cited_by_count:desc"
    ):
        if w.title.lower().strip()[:80] == s.lower().strip()[:80]:
            return w
        if s.lower()[:60] in w.title.lower():
            return w
    return None


# ---------------------------------------------------------------------------
# Live searches
# ---------------------------------------------------------------------------

def topic_search(
    client: OpenAlexClient,
    *,
    topic: str,
    year_min: int = 2020,
    year_max: int | None = None,
    min_citations: int = 20,
    max_papers: int = 10,
    require_arxiv: bool = True,
) -> list[OpenAlexWork]:
    parts = [build_filter(
        year_min=year_min,
        year_max=year_max,
        min_citations=min_citations,
        keyword_search=topic,
    )]
    if require_arxiv:
        parts.append(f"locations.source.id:{ARXIV_SOURCE_ID}")
    filt = ",".join(p for p in parts if p)
    return list(client.works(filter_str=filt, max_results=max_papers))


def seminal_search(
    client: OpenAlexClient,
    *,
    topic: str | None,
    year_max: int = 2019,
    year_min: int = 2000,
    min_citations: int = 1000,
    max_papers: int = 10,
    require_arxiv: bool = False,
) -> list[OpenAlexWork]:
    """Old highly-cited papers. The 'neglected futures' candidates."""
    parts = [build_filter(
        year_min=year_min,
        year_max=year_max,
        min_citations=min_citations,
        keyword_search=topic,
    )]
    if require_arxiv:
        parts.append(f"locations.source.id:{ARXIV_SOURCE_ID}")
    filt = ",".join(p for p in parts if p)
    return list(client.works(filter_str=filt, max_results=max_papers))


def broad_search(
    client: OpenAlexClient,
    *,
    query: str,
    fields: list[str] | None = None,
    year_min: int = 2020,
    min_citations: int = 30,
    max_papers: int = 15,
    require_arxiv: bool = True,
) -> list[OpenAlexWork]:
    """Cross-field exploratory search. Combines keyword + (optional) concept ORs."""
    concept_ids: list[str] = []
    if fields:
        for f in fields:
            concept_ids.extend(FIELDS.get(f, {}).get("concept_ids", []))
    parts = [build_filter(
        concept_ids=concept_ids or None,
        year_min=year_min,
        min_citations=min_citations,
        keyword_search=query,
    )]
    if require_arxiv:
        parts.append(f"locations.source.id:{ARXIV_SOURCE_ID}")
    filt = ",".join(p for p in parts if p)
    return list(client.works(filter_str=filt, max_results=max_papers))


# ---------------------------------------------------------------------------
# Single-paper roundtrip: cache, fetch, extract
# ---------------------------------------------------------------------------

def cache_work(store: Store, w: OpenAlexWork, *, field: str, track: str) -> None:
    p = Paper(
        id=w.id,
        doi=w.doi,
        arxiv_id=w.arxiv_id,
        title=w.title,
        authors_json=json.dumps(w.authors, ensure_ascii=False),
        year=w.year,
        venue=w.venue,
        venue_id=w.venue_id,
        abstract=w.abstract,
        cited_by_count=w.cited_by_count,
        field=field,
        track=track,
        oa_url=w.oa_url,
        pdf_url=w.pdf_url,
        raw_json=json.dumps(w.raw, ensure_ascii=False),
    )
    store.upsert_paper(p)


def fetch_and_extract(
    store: Store,
    paper_id: str,
    *,
    http: httpx.Client | None = None,
) -> dict[str, Any]:
    """Idempotent: fetch PDF if missing, extract sections if missing.

    Returns a structured summary the caller can present to a synthesizer.
    """
    row = store.get_paper(paper_id)
    if row is None:
        return {"paper_id": paper_id, "error": "not in store"}

    own_http = http is None
    if own_http:
        http = httpx.Client(
            headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"},
            timeout=60.0,
        )
    try:
        if not row["pdf_path"] or not Path(row["pdf_path"]).exists():
            pdf_path = fetch_pdf(row, client=http)
            if pdf_path:
                store.update_paper_pdf(
                    paper_id, str(pdf_path), dt.datetime.utcnow().isoformat()
                )
                row = store.get_paper(paper_id)
            else:
                return summarize_paper(row, sections=[], note="pdf_unavailable")

        existing_sections = store.get_sections(paper_id)
        if not existing_sections or all(not s["content"] for s in existing_sections):
            try:
                extracted = extract_paper(Path(row["pdf_path"]))
            except Exception as e:
                log.warning("extract failed for %s: %s", paper_id, e)
                extracted = []
            if extracted:
                store.upsert_sections(
                    Section(
                        paper_id=paper_id,
                        section_type=s.section_type,
                        heading=s.heading,
                        content=s.content,
                        method="regex",
                    )
                    for s in extracted
                )
            sections = store.get_sections(paper_id)
        else:
            sections = existing_sections

        return summarize_paper(row, sections=sections)
    finally:
        if own_http:
            http.close()


def summarize_paper(row, *, sections: list, note: str | None = None) -> dict[str, Any]:
    """Render a paper + its sections to the structured shape MCP tools return."""
    authors = []
    try:
        authors = json.loads(row["authors_json"] or "[]")
    except json.JSONDecodeError:
        pass
    section_payload: list[dict[str, Any]] = []
    for s in sections:
        if not s["content"]:
            continue
        section_payload.append({
            "type": s["section_type"],
            "heading": s["heading"],
            "content": s["content"],
            "char_count": len(s["content"]),
        })

    arxiv_id = row["arxiv_id"]
    out: dict[str, Any] = {
        "paper_id": row["id"],
        "title": row["title"],
        "authors": [a.get("name") for a in authors if a.get("name")][:8],
        "year": row["year"],
        "venue": row["venue"],
        "cited_by_count": row["cited_by_count"],
        "doi": row["doi"],
        "arxiv_id": arxiv_id,
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None,
        "doi_url": (
            row["doi"] if (row["doi"] or "").startswith("http")
            else (f"https://doi.org/{row['doi']}" if row["doi"] else None)
        ),
        "abstract": row["abstract"],
        "field": row["field"],
        "track": row["track"],
        "sections": section_payload,
    }
    if note:
        out["note"] = note
    return out
