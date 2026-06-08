"""Seed papers from user BibTeX files.

Resolves each entry to OpenAlex via DOI when present, otherwise via title search.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable, Iterator

import bibtexparser  # type: ignore

from vista.sources.openalex import OpenAlexClient
from vista.storage.db import Paper, Store

log = logging.getLogger(__name__)


def parse_bibtex(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", errors="replace") as fh:
        db = bibtexparser.load(fh)
    return [dict(e) for e in db.entries]


def _resolve(entry: dict, client: OpenAlexClient):
    doi = entry.get("doi") or entry.get("DOI")
    if doi:
        w = client.work_by_doi(doi)
        if w:
            return w
    # Fallback: title search via filter
    title = entry.get("title") or entry.get("TITLE")
    if not title:
        return None
    title_clean = title.strip().strip("{}")
    # Use OpenAlex search filter
    for w in client.works(filter_str=f"title.search:{title_clean}", per_page=5, max_results=5):
        if w.title.lower().strip() == title_clean.lower().strip():
            return w
        # tolerate a slight prefix/suffix mismatch
        if title_clean.lower().strip()[:60] in w.title.lower():
            return w
    return None


def seed_from_bib(
    store: Store,
    paths: Iterable[Path],
    *,
    field: str,
    track: str = "seed",
    mailto: str | None = None,
) -> dict[str, int]:
    counts = {"entries": 0, "resolved": 0, "stored": 0, "missing": 0}
    with OpenAlexClient(mailto=mailto) as client:
        for p in paths:
            entries = parse_bibtex(p)
            for e in entries:
                counts["entries"] += 1
                w = _resolve(e, client)
                if not w:
                    counts["missing"] += 1
                    log.info("could not resolve %s", e.get("title", "?")[:80])
                    continue
                counts["resolved"] += 1
                paper = Paper(
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
                store.upsert_paper(paper)
                counts["stored"] += 1
    return counts


def discover_bibs_in_repo(roots: Iterable[Path]) -> Iterator[Path]:
    """Recursively yield .bib files under each root path."""
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*.bib"):
            yield p
