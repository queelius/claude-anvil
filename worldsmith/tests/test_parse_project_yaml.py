"""Tests for hooks/scripts/parse-project-yaml.py schema validation and output.

Run: python3 -m pytest tests/   (needs PyYAML; skipped otherwise)
"""

import os
import shlex
import subprocess
import sys

import pytest

pytest.importorskip("yaml")

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks", "scripts",
                      "parse-project-yaml.py")


def run(tmp_path, text, mode="--env"):
    ws = tmp_path / ".worldsmith"
    ws.mkdir(exist_ok=True)
    (ws / "project.yaml").write_text(text)
    return subprocess.run([sys.executable, SCRIPT, str(ws / "project.yaml"), mode],
                          capture_output=True, text=True)


def env_dict(stdout):
    return dict(shlex.split(line)[0].split("=", 1) for line in stdout.splitlines())


VALID = """\
universe: Testverse
lore: shared
works:
  - name: Book One
    type: novel
    manuscript: books/one
    file_types: [.md, tex]
    lore: books/one/lore
  - name: Tale
    type: short-story
    manuscript: tales
"""


def test_env_output(tmp_path):
    r = run(tmp_path, VALID)
    assert r.returncode == 0, r.stderr
    env = env_dict(r.stdout)
    assert env["WORLDSMITH_WORK_COUNT"] == "2"
    assert env["WORLDSMITH_WORK_0_NAME"] == "Book One"
    assert env["WORLDSMITH_WORK_0_FILETYPES"] == "md,tex"
    assert env["WORLDSMITH_WORK_1_FILETYPES"] == "md,tex,txt"
    assert env["WORLDSMITH_WORK_0_LORE"] == "books/one/lore"
    assert env["WORLDSMITH_WORKS"] == "Book One:Tale"


def test_export_output_keeps_multiline_values(tmp_path):
    text = VALID.replace("name: Tale", 'name: "Tale\\nPart two"')
    r = run(tmp_path, text, "--export")
    assert r.returncode == 0, r.stderr
    out = subprocess.run(["bash", "-c", r.stdout + '\nprintf %s "$WORLDSMITH_WORK_1_NAME"'],
                         capture_output=True, text=True).stdout
    assert out == "Tale\nPart two"
    # one export per assignment: 4 universe-level + 6 per work
    assert sum(line.startswith("export WORLDSMITH_") for line in r.stdout.splitlines()) == 16


def test_human_output_counts_files(tmp_path):
    (tmp_path / "tales").mkdir()
    (tmp_path / "tales" / "a.md").write_text("x")
    r = run(tmp_path, VALID, "--human")
    assert r.returncode == 0, r.stderr
    assert "Tale [short-story]: tales (1 file)" in r.stdout


def test_nonfiction_type_accepted(tmp_path):
    # Essays and nonfiction books (e.g. Broken Things, Multitudes) share the
    # lore-first workflow; `type` is informational and must not reject them.
    text = VALID.replace("type: short-story", "type: nonfiction")
    r = run(tmp_path, text, "--human")
    assert r.returncode == 0, r.stderr
    assert "Tale [nonfiction]: tales" in r.stdout


@pytest.mark.parametrize("text,msg", [
    ("- a\n- b\n", "must be a YAML mapping"),
    ("works: [{name: a, type: novel}]\n", "'universe'"),
    ("universe: U\nlore: [x]\nworks: [{name: a, type: novel}]\n", "'lore' field"),
    ("universe: U\n", "non-empty 'works'"),
    ("universe: U\nworks: [3]\n", "works[0] must be a mapping"),
    ("universe: U\nworks: [{type: novel}]\n", "'name'"),
    ("universe: U\nworks: [{name: a, type: epic}]\n", "'type' must be one of"),
    ("universe: U\nworks: [{name: a, type: novel, manuscript: [x]}]\n", "'manuscript'"),
    ("universe: U\nworks: [{name: a, type: novel, file_types: md}]\n", "'file_types'"),
    ("universe: U\nworks: [{name: a, type: novel, lore: [x]}]\n", "'lore' must be"),
    ("universe: [unclosed\n", "Invalid YAML"),
])
def test_schema_errors(tmp_path, text, msg):
    r = run(tmp_path, text)
    assert r.returncode == 1
    assert msg in r.stderr
    assert r.stdout == ""
