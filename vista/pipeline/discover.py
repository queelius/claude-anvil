"""Discover candidate papers via OpenAlex and write them to the store."""

from __future__ import annotations

import json
import logging
from typing import Iterator

from vista.config import ARXIV_SOURCE_ID, FIELDS, RunConfig
from vista.sources.openalex import OpenAlexClient, OpenAlexWork, build_filter
from vista.storage.db import Paper, Store

log = logging.getLogger(__name__)


def discover_field(
    client: OpenAlexClient,
    *,
    field: str,
    track: str,
    cfg: RunConfig,
) -> Iterator[OpenAlexWork]:
    """Yield top-cited works for a (field, track) combination."""
    fconf = FIELDS[field]
    if track == "recent":
        year_min = cfg.year_min_recent
        year_max = None
        min_cites = fconf.get("min_citations_recent", 30)
        limit = cfg.per_field_limit
    elif track == "legacy":
        year_min = cfg.year_min_legacy
        year_max = cfg.year_max_legacy
        min_cites = fconf.get("min_citations_legacy", 300)
        limit = cfg.legacy_per_field_limit
    else:
        raise ValueError(f"unknown track {track}")

    strategy = fconf.get("fulltext_filter", "any")
    venue_ids = fconf.get("venue_ids") or None
    extra_location_filters: list[str] = []
    if strategy == "arxiv-required":
        # Require the work to also have a location at arXiv. This guarantees
        # we can fetch a PDF directly from arxiv.org.
        extra_location_filters.append(f"locations.source.id:{ARXIV_SOURCE_ID}")
        venue_ids = None  # OpenAlex venue coverage of NeurIPS/ICML is sparse.

    filt = build_filter(
        concept_ids=fconf.get("concept_ids"),
        venue_ids=venue_ids,
        year_min=year_min,
        year_max=year_max,
        min_citations=min_cites,
        is_oa=None,  # don't pre-filter; we'll handle at fetch time
        keyword_search=fconf.get("keywords") if strategy == "any" else None,
    )
    if extra_location_filters:
        filt = filt + "," + ",".join(extra_location_filters)
    log.info("[%s/%s] OpenAlex filter: %s", field, track, filt)
    yield from client.works(filter_str=filt, max_results=limit)


def store_works(store: Store, works: Iterator[OpenAlexWork], *, field: str, track: str) -> int:
    n = 0
    for w in works:
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
        n += 1
    return n


def run_discover(store: Store, cfg: RunConfig, *, mailto: str | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    tracks = ["recent", "legacy"] if cfg.track == "both" else [cfg.track]
    with OpenAlexClient(mailto=mailto) as client:
        for field in cfg.fields:
            for track in tracks:
                works = discover_field(client, field=field, track=track, cfg=cfg)
                n = store_works(store, works, field=field, track=track)
                counts[f"{field}/{track}"] = n
                log.info("[%s/%s] stored %d papers", field, track, n)
    return counts
