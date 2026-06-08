"""OpenAlex client. Free, no API key. Polite header recommended.

Docs: https://docs.openalex.org/
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Iterator

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from vista.config import USER_AGENT

API = "https://api.openalex.org"


@dataclass
class OpenAlexWork:
    id: str
    doi: str | None
    title: str
    abstract: str | None
    year: int | None
    venue: str | None
    venue_id: str | None
    cited_by_count: int
    authors: list[dict]
    oa_url: str | None
    pdf_url: str | None
    arxiv_id: str | None
    raw: dict

    @classmethod
    def from_api(cls, w: dict) -> "OpenAlexWork":
        oa = w.get("open_access", {}) or {}
        primary = w.get("primary_location") or {}
        source = primary.get("source") or {}
        venue = source.get("display_name")
        venue_id = source.get("id")
        if venue_id and venue_id.startswith("https://openalex.org/"):
            venue_id = venue_id.rsplit("/", 1)[-1]

        # Find arXiv id from any location
        arxiv_id = None
        for loc in [primary] + (w.get("locations") or []):
            if not loc:
                continue
            url = (loc.get("landing_page_url") or "") + " " + (loc.get("pdf_url") or "")
            m = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+/[0-9]{7})", url)
            if m:
                arxiv_id = m.group(1)
                break

        # OA pdf preference: primary -> any oa location
        pdf_url = primary.get("pdf_url")
        if not pdf_url:
            for loc in w.get("locations") or []:
                if loc.get("is_oa") and loc.get("pdf_url"):
                    pdf_url = loc.get("pdf_url")
                    break

        oid = w["id"]
        if oid.startswith("https://openalex.org/"):
            oid = oid.rsplit("/", 1)[-1]

        return cls(
            id=oid,
            doi=w.get("doi"),
            title=w.get("display_name") or w.get("title") or "",
            abstract=_invert_abstract(w.get("abstract_inverted_index")),
            year=w.get("publication_year"),
            venue=venue,
            venue_id=venue_id,
            cited_by_count=w.get("cited_by_count") or 0,
            authors=[
                {
                    "name": (a.get("author") or {}).get("display_name"),
                    "orcid": (a.get("author") or {}).get("orcid"),
                }
                for a in w.get("authorships") or []
            ],
            oa_url=oa.get("oa_url"),
            pdf_url=pdf_url,
            arxiv_id=arxiv_id,
            raw=w,
        )


def _invert_abstract(inv: dict | None) -> str | None:
    if not inv:
        return None
    positions: list[tuple[int, str]] = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions) or None


class OpenAlexClient:
    def __init__(self, *, mailto: str | None = None, timeout: float = 30.0):
        ua = USER_AGENT if not mailto else f"vista/0.1 (mailto:{mailto})"
        self.client = httpx.Client(
            base_url=API,
            headers={"User-Agent": ua, "Accept": "application/json"},
            timeout=timeout,
        )

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "OpenAlexClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    @retry(stop=stop_after_attempt(4), wait=wait_exponential_jitter(initial=1, max=15))
    def _get(self, path: str, params: dict[str, Any]) -> dict:
        r = self.client.get(path, params=params)
        if r.status_code == 429:
            r.raise_for_status()
        r.raise_for_status()
        return r.json()

    def works(self, *, filter_str: str, sort: str = "cited_by_count:desc",
              per_page: int = 50, max_results: int | None = None) -> Iterator[OpenAlexWork]:
        cursor = "*"
        seen = 0
        while True:
            data = self._get(
                "/works",
                {"filter": filter_str, "sort": sort, "per-page": per_page, "cursor": cursor},
            )
            for w in data.get("results", []):
                yield OpenAlexWork.from_api(w)
                seen += 1
                if max_results and seen >= max_results:
                    return
            cursor = (data.get("meta") or {}).get("next_cursor")
            if not cursor:
                return

    def work_by_doi(self, doi: str) -> OpenAlexWork | None:
        clean = doi.lower().removeprefix("https://doi.org/").removeprefix("doi:")
        try:
            data = self._get(f"/works/doi:{clean}", {})
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        return OpenAlexWork.from_api(data)

    def work_by_id(self, work_id: str) -> OpenAlexWork | None:
        wid = work_id
        if wid.startswith("https://openalex.org/"):
            wid = wid.rsplit("/", 1)[-1]
        try:
            data = self._get(f"/works/{wid}", {})
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        return OpenAlexWork.from_api(data)


def build_filter(
    *,
    concept_ids: list[str] | None = None,
    venue_ids: list[str] | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    min_citations: int | None = None,
    is_oa: bool | None = True,
    types: list[str] | None = None,
    keyword_search: str | None = None,
) -> str:
    parts: list[str] = []
    if concept_ids:
        parts.append("concepts.id:" + "|".join(concept_ids))
    if venue_ids:
        parts.append("primary_location.source.id:" + "|".join(venue_ids))
    if year_min and year_max:
        parts.append(f"publication_year:{year_min}-{year_max}")
    elif year_min:
        parts.append(f"publication_year:>{year_min - 1}")
    elif year_max:
        parts.append(f"publication_year:<{year_max + 1}")
    if min_citations is not None:
        parts.append(f"cited_by_count:>{min_citations - 1}")
    if is_oa is not None:
        parts.append(f"is_oa:{'true' if is_oa else 'false'}")
    if types:
        parts.append("type:" + "|".join(types))
    if keyword_search:
        # OpenAlex supports `default.search` via the `search` param, but we
        # prefer filter-style: title_and_abstract.search
        parts.append(f"title_and_abstract.search:{keyword_search}")
    return ",".join(parts)
