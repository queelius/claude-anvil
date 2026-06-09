"""Extract Future Work / Limitations / Discussion / Conclusion sections from PDFs.

Strategy: pdftotext (poppler) -> heading regex -> section content. Falls back
to PyMuPDF-derived text if pdftotext is unavailable. We greedily collect the
text from a matched heading until the next plausible heading.
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from vista.config import TEXT_DIR
from vista.storage.db import Section, Store

log = logging.getLogger(__name__)


# Heading patterns we treat as the start of a section we care about. Anchored
# at the start of a (stripped) line, allowing optional numbering like "6.",
# "VI.", "6.1", or "Chapter 7".
SECTION_PATTERNS: dict[str, re.Pattern] = {
    "future_work": re.compile(
        r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.?\s+)?"
        r"(?:(?:conclusions?|limitations?|summary|discussion)\s+and\s+)?"
        r"(future\s+work|future\s+research|future\s+directions?|open\s+(?:problems?|questions?|directions?)|outlook)"
        r"\s*[:\.]?\s*$",
        re.IGNORECASE,
    ),
    "limitations": re.compile(
        r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.?\s+)?"
        r"(limitations?|threats\s+to\s+validity|caveats)"
        r"\s*[:\.]?\s*$",
        re.IGNORECASE,
    ),
    "discussion": re.compile(
        r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.?\s+)?"
        r"(discussion|discussion\s+and\s+(?:future\s+work|conclusions?))"
        r"\s*[:\.]?\s*$",
        re.IGNORECASE,
    ),
    "conclusion": re.compile(
        r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.?\s+)?"
        r"(conclusions?|concluding\s+remarks|summary\s+and\s+conclusions?)"
        r"\s*[:\.]?\s*$",
        re.IGNORECASE,
    ),
}

# Generic heading: a short line of mostly title-case words, used to terminate
# section capture. Conservative — tuned to avoid eating body paragraphs.
GENERIC_HEADING = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.\s+|[A-Z]\.\s+)"
    r"[A-Z][A-Za-z0-9\-:,&\s]{2,80}\s*$"
)
REFS_HEADING = re.compile(
    r"^\s*(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.?\s+)?"
    r"(references|bibliography|acknowledge?ments?|appendix(?:\s+[A-Z0-9]+)?|appendices|supplementary\s+material)"
    r"\s*[:\.]?\s*$",
    re.IGNORECASE)
MAX_SECTION_LINES = 200  # safety cap


@dataclass
class ExtractedSection:
    section_type: str
    heading: str
    content: str


def pdf_to_text(pdf_path: Path) -> str:
    """Convert PDF to plain text.

    Prefer PyMuPDF — it is column-aware and keeps headings (e.g. "5 Conclusion")
    on their own line in two-column conference papers, which our heading regex
    relies on. Fall back to `pdftotext` (poppler) if PyMuPDF is unavailable.
    """
    cached = TEXT_DIR / (pdf_path.stem + ".txt")
    if cached.exists() and cached.stat().st_mtime >= pdf_path.stat().st_mtime:
        return cached.read_text(errors="replace")

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    text = ""
    pymupdf_mod = None
    try:
        import pymupdf as pymupdf_mod  # type: ignore
    except ImportError:
        try:
            import fitz as pymupdf_mod  # type: ignore
        except ImportError:
            pymupdf_mod = None

    if pymupdf_mod is not None:
        try:
            with pymupdf_mod.open(pdf_path) as doc:
                text = "\n".join(page.get_text() for page in doc)
        except Exception as e:
            log.warning("pymupdf failed (%s); falling back to pdftotext", e)
            text = ""

    if not text:
        try:
            out = subprocess.run(
                ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
                capture_output=True, check=True, timeout=60,
            )
            text = out.stdout.decode("utf-8", errors="replace")
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            raise RuntimeError(f"PDF text extraction failed: {e}") from e

    cached.write_text(text)
    return text


def find_sections(text: str) -> list[ExtractedSection]:
    """Locate sections by scanning headings.

    For each line we test against the known section patterns; on match we
    capture subsequent lines until the next heading-looking line.
    """
    lines = text.splitlines()
    found: list[ExtractedSection] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match_type = None
        match_heading = None
        for stype, pat in SECTION_PATTERNS.items():
            m = pat.match(line)
            if m:
                match_type = stype
                match_heading = m.group(1)
                break
        if not match_type:
            i += 1
            continue

        body: list[str] = []
        j = i + 1
        blank_streak = 0
        while j < len(lines) and len(body) < MAX_SECTION_LINES:
            l = lines[j].rstrip()
            stripped = l.strip()

            # Stop at references / acknowledgments / appendix headings unconditionally.
            if REFS_HEADING.match(stripped):
                break
            # Stop at another tracked section heading.
            if any(p.match(stripped) for p in SECTION_PATTERNS.values()):
                break
            # Stop at a likely generic heading after at least a couple lines.
            # Exception: long numbered lines ("2. Better calibration under
            # distribution shift across many domains") are enumerated content,
            # not headings; require the numbered form to be short and
            # title-like before treating it as a terminator.
            if len(body) > 3 and GENERIC_HEADING.match(stripped) and len(stripped) < 80:
                if not (stripped[:1].isdigit() and len(stripped.split()) > 6):
                    break

            body.append(l)
            blank_streak = blank_streak + 1 if not stripped else 0
            # If we have three consecutive blank-ish lines, treat as section end.
            if blank_streak >= 3 and len(body) > 5:
                break
            j += 1

        content = "\n".join(body).strip()
        if content:
            found.append(ExtractedSection(match_type, match_heading or line, content))
        i = max(j, i + 1)
    return _dedupe_keep_first(found)


def _dedupe_keep_first(sections: list[ExtractedSection]) -> list[ExtractedSection]:
    """If multiple sections of the same type are found (e.g., per-chapter),
    keep the longest one — that's typically the one with the meaningful content."""
    by_type: dict[str, ExtractedSection] = {}
    for s in sections:
        cur = by_type.get(s.section_type)
        if cur is None or len(s.content) > len(cur.content):
            by_type[s.section_type] = s
    # Order: future_work, limitations, discussion, conclusion
    order = ["future_work", "limitations", "discussion", "conclusion"]
    return [by_type[k] for k in order if k in by_type]


def extract_paper(pdf_path: Path) -> list[ExtractedSection]:
    text = pdf_to_text(pdf_path)
    return find_sections(text)


def run_extract(store: Store, *, max_papers: int | None = None) -> dict[str, int]:
    rows = store.papers(needs_extraction=True)
    if max_papers:
        rows = rows[:max_papers]
    out = {"attempted": 0, "with_sections": 0, "no_sections": 0}
    for row in rows:
        out["attempted"] += 1
        pdf_path = Path(row["pdf_path"])
        if not pdf_path.exists():
            log.warning("PDF missing on disk: %s", pdf_path)
            continue
        try:
            secs = extract_paper(pdf_path)
        except Exception as e:
            log.warning("extract failed for %s: %s", row["id"], e)
            continue
        if secs:
            store.upsert_sections(
                Section(
                    paper_id=row["id"],
                    section_type=s.section_type,
                    heading=s.heading,
                    content=s.content,
                    method="regex",
                )
                for s in secs
            )
            out["with_sections"] += 1
        else:
            out["no_sections"] += 1
            # Insert a placeholder so we don't keep retrying.
            store.upsert_sections([
                Section(
                    paper_id=row["id"],
                    section_type="conclusion",
                    heading=None,
                    content="",
                    method="regex-empty",
                )
            ])
    return out
