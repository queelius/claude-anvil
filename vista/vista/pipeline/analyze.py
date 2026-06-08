"""LLM analyzer.

Primary path is the MCP server in `vista.mcp_server`, which exposes tools
that an MCP client (Claude Code, etc.) can call directly. The LLM never has
to be the Anthropic SDK; it can be whoever is on the other end of the MCP
connection.

This module keeps an opt-in Anthropic-API path for fully unattended batch
runs (cron, CI, etc.) where you don't want a human in the loop. The
`anthropic` package is an optional dep.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from vista.config import DEFAULT_MODEL
from vista.storage.db import Direction, Store

log = logging.getLogger(__name__)


SYSTEM_PROMPT = """You are a research analyst distilling concrete research \
directions from the "Future Work", "Limitations", "Discussion", and \
"Conclusion" sections of academic papers.

Your job: given the abstract and section text from one paper, produce a JSON \
array of *actionable* research directions. Each direction should be one that a \
graduate student or researcher could plausibly pursue as a project.

For each direction, output an object with these fields:
- "direction": one sentence stating what to investigate. Be concrete; avoid \
generic wishes like "more experiments" or "better models". If the paper is \
vague, refine the direction into the most specific actionable form supported \
by the text.
- "rationale": one or two sentences on why this direction matters, grounded \
in the paper's findings or limitations.
- "quote": a short verbatim phrase from the input text that motivated this \
direction (max ~30 words, exact substring of the input).
- "field_tags": array of 1-4 lower-case tags (e.g., ["nlp", "interpretability", \
"reinforcement-learning"]).
- "feasibility": "low" | "medium" | "high" — how realistic for a small team in \
2-3 quarters.
- "novelty": "low" | "medium" | "high" — relative to the apparent state of the \
field.
- "dependencies": short note on prerequisites (data, hardware, theory) or null.

Rules:
- Output ONLY a JSON array. No prose, no markdown fences.
- Aim for 3-8 directions. If fewer than 3 are well-supported, return however \
many are well-supported (even zero).
- Do not invent directions not grounded in the text.
- If the input is mostly boilerplate or empty, return [].
"""


def _client():
    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise RuntimeError(
            "anthropic package not installed; pip install -e '.[api]' or use the MCP server"
        ) from e
    return Anthropic()


def prepare_one_paper(paper_row, section_rows) -> dict[str, Any] | None:
    """Build a single paper's analyzer input. Returns None if no analyzable content."""
    if not section_rows or all(not r["content"] for r in section_rows):
        return None
    paper = dict(paper_row)
    sections = [dict(s) for s in section_rows if s["content"]]
    if not sections:
        return None
    user_msg = _build_user_message(paper, sections)
    return {
        "paper_id": paper["id"],
        "title": paper["title"],
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "field": paper.get("field"),
        "track": paper.get("track"),
        "section_types": [s["section_type"] for s in sections],
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_msg,
    }


def directions_from_dicts(paper_id: str, items: list[dict]) -> list[Direction]:
    """Coerce a list of {direction, rationale, ...} dicts into Direction rows."""
    out: list[Direction] = []
    for it in items:
        d = it.get("direction")
        if not d:
            continue
        out.append(
            Direction(
                paper_id=paper_id,
                direction=str(d),
                rationale=str(it.get("rationale") or "") or None,
                quote=str(it.get("quote") or "") or None,
                field_tags_json=json.dumps(it.get("field_tags") or [], ensure_ascii=False),
                feasibility=str(it.get("feasibility") or "") or None,
                novelty=str(it.get("novelty") or "") or None,
                dependencies=str(it.get("dependencies") or "") or None,
            )
        )
    return out


def _build_user_message(paper: dict[str, Any], sections: list[dict]) -> str:
    parts: list[str] = []
    parts.append(f"# Paper\n\nTitle: {paper['title']}")
    if paper.get("year"):
        parts.append(f"Year: {paper['year']}")
    if paper.get("venue"):
        parts.append(f"Venue: {paper['venue']}")
    if paper.get("abstract"):
        parts.append(f"\nAbstract:\n{paper['abstract']}")

    parts.append("\n# Sections")
    for s in sections:
        if not s.get("content"):
            continue
        parts.append(f"\n## {s['section_type'].replace('_', ' ').title()}")
        if s.get("heading"):
            parts.append(f"(heading: {s['heading']})")
        # Truncate per section to keep token use modest.
        content = s["content"]
        if len(content) > 12000:
            content = content[:12000] + "\n[...truncated]"
        parts.append(content)
    return "\n".join(parts)


def _extract_json_array(text: str) -> list[dict]:
    text = text.strip()
    # Strip code fences if model returns them despite instructions.
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # Try to grab the first array via bracket scanning.
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or end < start:
            return []
        try:
            data = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return []
    if not isinstance(data, list):
        return []
    return [d for d in data if isinstance(d, dict)]


def analyze_paper(
    paper_row,
    section_rows: list,
    *,
    model: str = DEFAULT_MODEL,
    client=None,
) -> list[Direction]:
    if not section_rows or all(not r["content"] for r in section_rows):
        return []
    if client is None:
        client = _client()

    paper = dict(paper_row)
    sections = [dict(s) for s in section_rows]
    user_msg = _build_user_message(paper, sections)

    resp = client.messages.create(
        model=model,
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_msg}],
    )
    text = "".join(
        block.text for block in resp.content if getattr(block, "type", "") == "text"
    )
    items = _extract_json_array(text)

    directions: list[Direction] = []
    for it in items:
        d = it.get("direction")
        if not d:
            continue
        directions.append(
            Direction(
                paper_id=paper["id"],
                direction=str(d),
                rationale=str(it.get("rationale") or "") or None,
                quote=str(it.get("quote") or "") or None,
                field_tags_json=json.dumps(it.get("field_tags") or [], ensure_ascii=False),
                feasibility=str(it.get("feasibility") or "") or None,
                novelty=str(it.get("novelty") or "") or None,
                dependencies=str(it.get("dependencies") or "") or None,
            )
        )
    return directions


def run_analyze(
    store: Store,
    *,
    model: str = DEFAULT_MODEL,
    max_papers: int | None = None,
) -> dict[str, int]:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set; cannot run analyzer")
    rows = store.papers(needs_analysis=True)
    if max_papers:
        rows = rows[:max_papers]
    out = {"attempted": 0, "with_directions": 0, "no_directions": 0}
    client = _client()
    for row in rows:
        out["attempted"] += 1
        sections = store.get_sections(row["id"])
        try:
            directions = analyze_paper(row, sections, model=model, client=client)
        except Exception as e:
            log.warning("analyze failed for %s: %s", row["id"], e)
            continue
        store.replace_directions(row["id"], directions)
        if directions:
            out["with_directions"] += 1
        else:
            out["no_directions"] += 1
    return out
