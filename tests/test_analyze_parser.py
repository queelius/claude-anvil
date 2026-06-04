"""Unit tests for analyzer JSON parsing — runs without an API key."""

from vista.pipeline.analyze import _extract_json_array


def test_pure_json():
    out = _extract_json_array('[{"direction": "A"}, {"direction": "B"}]')
    assert len(out) == 2
    assert out[0]["direction"] == "A"


def test_with_code_fence():
    text = '```json\n[{"direction": "A"}]\n```'
    out = _extract_json_array(text)
    assert len(out) == 1


def test_with_prose_around():
    text = 'Sure, here is the JSON:\n[{"direction": "A"}]\nLet me know.'
    out = _extract_json_array(text)
    assert len(out) == 1


def test_garbage():
    out = _extract_json_array("this is not JSON at all")
    assert out == []


def test_empty_array():
    out = _extract_json_array("[]")
    assert out == []


def test_dropped_non_dict():
    out = _extract_json_array('[{"direction": "A"}, "raw string", null]')
    assert len(out) == 1
