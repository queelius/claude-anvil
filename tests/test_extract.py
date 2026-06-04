"""Tests for section extraction heading regex and section-walker."""

from vista.pipeline.extract import SECTION_PATTERNS, find_sections


def _heads(text: str):
    return {s.section_type: s for s in find_sections(text)}


def test_heading_patterns_match_common_forms():
    cases = [
        ("Future Work", "future_work"),
        ("6. Future Work", "future_work"),
        ("VI. Future Directions", "future_work"),
        ("Open Problems", "future_work"),
        ("Limitations", "limitations"),
        ("5.2 Threats to validity", "limitations"),
        ("Discussion", "discussion"),
        ("Conclusion", "conclusion"),
        ("Concluding remarks", "conclusion"),
    ]
    for line, expected in cases:
        assert any(p.match(line) for p in [SECTION_PATTERNS[expected]]), \
            f"{expected} pattern should match {line!r}"


def test_negative_examples():
    # Body sentences should not match.
    not_headings = [
        "We discuss future work in section 6.",
        "In future work we will improve the model.",
        "The conclusion is straightforward.",
        "Discussion of related work is below.",
    ]
    for line in not_headings:
        for stype, pat in SECTION_PATTERNS.items():
            assert not pat.match(line), f"{stype} should NOT match {line!r}"


def test_section_capture_stops_at_next_heading():
    text = """
4 Method

Some method content.

5 Future Work
We will study X.
We will study Y.

6 Conclusion

We conclude.

References

[1] Foo et al
""".strip()
    found = _heads(text)
    assert "future_work" in found
    fw = found["future_work"]
    assert "study X" in fw.content
    assert "study Y" in fw.content
    # Conclusion content captured but stops at References.
    assert "conclusion" in found
    assert "We conclude" in found["conclusion"].content
    assert "Foo et al" not in found["conclusion"].content


def test_dedup_keeps_longer():
    text = """
3 Conclusion
Short.

7 Conclusion
Much longer conclusion section with substantive content that we should keep.

References
""".strip()
    found = _heads(text)
    assert "Much longer" in found["conclusion"].content
