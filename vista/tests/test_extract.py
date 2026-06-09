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


def test_combined_and_dotless_heading_forms():
    # Combined closing headings must classify as future_work, and dotless
    # roman numerals must parse.
    cases = [
        ("Conclusions and Future Work", "future_work"),
        ("Conclusion and Future Work", "future_work"),
        ("Limitations and Future Work", "future_work"),
        ("Summary and Future Work", "future_work"),
        ("7 CONCLUSION", "conclusion"),
        ("VII CONCLUSION", "conclusion"),
        ("Outlook", "future_work"),
    ]
    for line, expected in cases:
        assert SECTION_PATTERNS[expected].match(line), \
            f"{expected} pattern should match {line!r}"


def test_refs_heading_variants_terminate_capture():
    text = "\n".join([
        "Conclusion",
        "We summarize the contributions here.",
        "More concluding prose follows in this paragraph.",
        "Further detail on scope and impact.",
        "Closing thoughts on the approach overall.",
        "Acknowledgements",
        "We thank grant 12345 and the anonymous reviewers.",
        "Appendix A",
        "Proof of Theorem 1 goes here.",
    ])
    secs = _heads(text)
    assert "conclusion" in secs
    content = secs["conclusion"].content
    assert "thank grant" not in content, "British Acknowledgements must terminate capture"
    assert "Proof of Theorem" not in content, "Numbered appendix must terminate capture"


def test_numbered_future_work_items_are_not_headings():
    text = "\n".join([
        "Future Work",
        "We see several promising directions ahead.",
        "There are many things left to explore here.",
        "Several concrete avenues stand out to us.",
        "1. Better calibration under distribution shift across many domains",
        "2. Extending the framework to multimodal settings with new losses",
        "References",
    ])
    secs = _heads(text)
    assert "future_work" in secs
    content = secs["future_work"].content
    assert "Better calibration" in content, "enumerated items are content, not headings"
    assert "multimodal settings" in content
