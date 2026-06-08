"""Offline tests for analyzer input prep and direction coercion. No API key.

These exercise everything in the analyzer except the live SDK call: building
the prompt, coercing model output dicts into Direction rows, and skipping
papers with no analyzable content.
"""

import json

from vista.pipeline.analyze import (
    _build_user_message,
    directions_from_dicts,
    prepare_one_paper,
)


def test_directions_from_dicts_basic():
    items = [
        {
            "direction": "Study X",
            "rationale": "because",
            "field_tags": ["ml", "nlp"],
            "feasibility": "high",
            "novelty": "medium",
            "quote": "q",
            "dependencies": "gpu",
        }
    ]
    out = directions_from_dicts("W1", items)
    assert len(out) == 1
    d = out[0]
    assert d.paper_id == "W1"
    assert d.direction == "Study X"
    assert json.loads(d.field_tags_json) == ["ml", "nlp"]
    assert d.feasibility == "high"


def test_directions_from_dicts_drops_items_without_direction():
    out = directions_from_dicts("W1", [{"rationale": "orphan"}, {"direction": "ok"}])
    assert [d.direction for d in out] == ["ok"]


def test_directions_from_dicts_empty_optionals_become_none():
    d = directions_from_dicts("W1", [{"direction": "D"}])[0]
    assert d.rationale is None
    assert d.quote is None
    assert d.feasibility is None
    assert json.loads(d.field_tags_json) == []


def test_prepare_one_paper_none_for_empty_or_missing_sections():
    paper = {"id": "W1", "title": "T", "year": 2020, "venue": "V",
             "field": "ml", "track": "recent", "abstract": "A"}
    assert prepare_one_paper(paper, []) is None
    empty = [{"section_type": "conclusion", "heading": "C", "content": ""}]
    assert prepare_one_paper(paper, empty) is None


def test_prepare_one_paper_builds_prompts():
    paper = {"id": "W1", "title": "Cool Paper", "year": 2020, "venue": "NeurIPS",
             "field": "ml", "track": "recent", "abstract": "An abstract."}
    sections = [{"section_type": "future_work", "heading": "Future Work",
                 "content": "We should study Y."}]
    out = prepare_one_paper(paper, sections)
    assert out is not None
    assert out["paper_id"] == "W1"
    assert out["section_types"] == ["future_work"]
    assert "Cool Paper" in out["user_prompt"]
    assert "We should study Y." in out["user_prompt"]
    assert out["system_prompt"]


def test_build_user_message_includes_metadata_and_truncates():
    paper = {"id": "W1", "title": "T", "year": 2021, "venue": "ICML", "abstract": "Abs"}
    sections = [{"section_type": "discussion", "heading": "Discussion",
                 "content": "x" * 13000}]
    msg = _build_user_message(paper, sections)
    assert "Title: T" in msg
    assert "Year: 2021" in msg
    assert "Venue: ICML" in msg
    assert "Discussion" in msg
    assert "[...truncated]" in msg  # content over 12000 chars is clipped
    assert len(msg) < 13000
