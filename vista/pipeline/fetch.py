"""Download OA PDFs to the local cache."""

from __future__ import annotations

import datetime as dt
import logging
import re
from pathlib import Path

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from vista.config import PDF_DIR, USER_AGENT
from vista.storage.db import Store

log = logging.getLogger(__name__)


def _pdf_path_for(paper_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_]", "_", paper_id)
    return PDF_DIR / f"{safe}.pdf"


def _arxiv_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"


def _candidate_urls(row) -> list[str]:
    urls: list[str] = []
    if row["arxiv_id"]:
        urls.append(_arxiv_pdf_url(row["arxiv_id"]))
    if row["pdf_url"]:
        urls.append(row["pdf_url"])
    if row["oa_url"]:
        urls.append(row["oa_url"])
    # Dedup, preserve order
    seen, out = set(), []
    for u in urls:
        if u and u not in seen:
            out.append(u)
            seen.add(u)
    return out


@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=1, max=10))
def _download(url: str, dest: Path, client: httpx.Client) -> bool:
    with client.stream("GET", url, follow_redirects=True) as r:
        r.raise_for_status()
        ctype = r.headers.get("content-type", "").lower()
        # Some servers return HTML for paywalled content with 200 OK.
        if "pdf" not in ctype and not url.endswith(".pdf"):
            log.warning("non-PDF content-type from %s: %s", url, ctype)
            return False
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as fh:
            for chunk in r.iter_bytes():
                fh.write(chunk)
        # Sanity check: PDFs start with %PDF-
        with open(tmp, "rb") as fh:
            head = fh.read(8)
        if not head.startswith(b"%PDF"):
            log.warning("downloaded file is not a PDF: %s (head=%r)", url, head)
            tmp.unlink(missing_ok=True)
            return False
        tmp.replace(dest)
        return True


def fetch_pdf(row, *, client: httpx.Client) -> Path | None:
    dest = _pdf_path_for(row["id"])
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    for url in _candidate_urls(row):
        log.info("fetching %s -> %s", url, dest.name)
        try:
            if _download(url, dest, client):
                return dest
        except httpx.HTTPError as e:
            log.warning("failed %s: %s", url, e)
            continue
        except Exception as e:  # broad guard, keep going
            log.warning("error fetching %s: %s", url, e)
            continue
    return None


def run_fetch(store: Store, *, max_papers: int | None = None) -> dict[str, int]:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    rows = store.papers(needs_pdf=True)
    if max_papers:
        rows = rows[:max_papers]
    out = {"attempted": 0, "ok": 0, "failed": 0}
    with httpx.Client(
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*"},
        timeout=60.0,
    ) as client:
        for row in rows:
            out["attempted"] += 1
            path = fetch_pdf(row, client=client)
            if path:
                out["ok"] += 1
                store.update_paper_pdf(
                    row["id"], str(path), dt.datetime.utcnow().isoformat()
                )
            else:
                out["failed"] += 1
    return out
