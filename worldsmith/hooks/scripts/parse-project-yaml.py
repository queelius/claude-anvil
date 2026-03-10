#!/usr/bin/env python3
"""
parse-project-yaml.py — Parse a worldsmith project.yaml and output structured data.

Usage:
    parse-project-yaml.py <path-to-project.yaml> [--env | --human]

Arguments:
    <path-to-project.yaml>   Path to the project.yaml file, typically
                             <project_root>/.worldsmith/project.yaml
    --env                    Output shell-eval-able variable assignments
                             (WORLDSMITH_UNIVERSE, WORLDSMITH_WORK_0_NAME, etc.)
    --human                  Output a human-readable summary with file counts
                             (default if flag is omitted)

Exit codes:
    0   Success
    1   File not found, unreadable, or invalid YAML / schema

Examples:
    # Source into current shell (for hooks):
    eval "$(parse-project-yaml.py .worldsmith/project.yaml --env)"

    # Print summary at SessionStart:
    parse-project-yaml.py .worldsmith/project.yaml --human
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


DEFAULT_FILE_TYPES = ["md", "tex", "txt"]


def die(msg: str) -> None:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def load_project_yaml(yaml_path: Path) -> dict:
    if not yaml_path.exists():
        die(f"File not found: {yaml_path}")
    try:
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        die(f"Invalid YAML in {yaml_path}: {exc}")
    if not isinstance(data, dict):
        die(f"project.yaml must be a YAML mapping, got: {type(data).__name__}")
    return data


def validate(data: dict) -> tuple[str, str, list[dict]]:
    """Validate top-level schema and return (universe, lore_dir, works)."""
    universe = data.get("universe")
    if not universe or not isinstance(universe, str):
        die("project.yaml must have a non-empty 'universe' string field")

    lore_dir = data.get("lore", "")
    if not isinstance(lore_dir, str):
        die("'lore' field must be a string path")

    raw_works = data.get("works")
    if not raw_works or not isinstance(raw_works, list):
        die("project.yaml must have a non-empty 'works' list")

    valid_types = {"novel", "novella", "short-story", "collection"}
    works = []
    for i, w in enumerate(raw_works):
        if not isinstance(w, dict):
            die(f"works[{i}] must be a mapping")
        name = w.get("name")
        if not name or not isinstance(name, str):
            die(f"works[{i}] must have a non-empty 'name' string")
        work_type = w.get("type", "")
        if work_type not in valid_types:
            die(f"works[{i}] 'type' must be one of {sorted(valid_types)}, got: {work_type!r}")
        manuscript = w.get("manuscript", "")
        if not isinstance(manuscript, str):
            die(f"works[{i}] 'manuscript' must be a string path")
        master = w.get("master", "")
        if master is None:
            master = ""
        raw_ft = w.get("file_types", DEFAULT_FILE_TYPES)
        if isinstance(raw_ft, list):
            file_types = [str(t).lstrip(".") for t in raw_ft]
        else:
            die(f"works[{i}] 'file_types' must be a list")
        works.append({
            "name": name,
            "type": work_type,
            "manuscript": manuscript,
            "master": master,
            "file_types": file_types,
        })

    return universe, lore_dir, works


def count_files(project_dir: Path, manuscript: str, file_types: list[str]) -> int:
    """Count files in manuscript dir matching any of file_types extensions."""
    ms_path = project_dir / manuscript
    if not ms_path.is_dir():
        return 0
    count = 0
    extensions = {f".{ft}" for ft in file_types}
    for entry in ms_path.rglob("*"):
        if entry.is_file() and entry.suffix in extensions:
            count += 1
    return count


def shell_quote(value: str) -> str:
    """Wrap value in double quotes, escaping embedded double quotes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def output_env(universe: str, lore_dir: str, works: list[dict]) -> None:
    lines = []
    lines.append(f"WORLDSMITH_UNIVERSE={shell_quote(universe)}")
    lines.append(f"WORLDSMITH_LORE_DIR={shell_quote(lore_dir)}")
    lines.append(f"WORLDSMITH_WORK_COUNT={len(works)}")
    work_names = ":".join(w["name"] for w in works)
    lines.append(f"WORLDSMITH_WORKS={shell_quote(work_names)}")
    for i, w in enumerate(works):
        prefix = f"WORLDSMITH_WORK_{i}"
        lines.append(f"{prefix}_NAME={shell_quote(w['name'])}")
        lines.append(f"{prefix}_TYPE={shell_quote(w['type'])}")
        lines.append(f"{prefix}_MANUSCRIPT={shell_quote(w['manuscript'])}")
        lines.append(f"{prefix}_MASTER={shell_quote(w['master'])}")
        lines.append(f"{prefix}_FILETYPES={shell_quote(','.join(w['file_types']))}")
    print("\n".join(lines))


def output_human(universe: str, lore_dir: str, works: list[dict], project_dir: Path) -> None:
    print(f"Universe: {universe}")
    if lore_dir:
        print(f"Lore directory: {lore_dir}")
    print()
    print("Works:")
    for w in works:
        n_files = count_files(project_dir, w["manuscript"], w["file_types"])
        file_label = f"{n_files} file{'s' if n_files != 1 else ''}"
        ms = w["manuscript"] or "(no manuscript)"
        print(f"  - {w['name']} [{w['type']}] — {ms} ({file_label})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse a worldsmith project.yaml and output structured data.",
        add_help=True,
    )
    parser.add_argument(
        "yaml_path",
        metavar="project.yaml",
        help="Path to the project.yaml file (e.g. .worldsmith/project.yaml)",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--env",
        action="store_true",
        help="Output shell-eval-able variable assignments",
    )
    mode_group.add_argument(
        "--human",
        action="store_true",
        help="Output human-readable summary (default)",
    )
    args = parser.parse_args()

    yaml_path = Path(args.yaml_path).resolve()
    # Derive project_dir: if path ends in .worldsmith/project.yaml, go two levels up
    # More generally: project_dir = yaml_path.parent.parent
    project_dir = yaml_path.parent.parent

    data = load_project_yaml(yaml_path)
    universe, lore_dir, works = validate(data)

    if args.env:
        output_env(universe, lore_dir, works)
    else:
        # --human is default
        output_human(universe, lore_dir, works, project_dir)


if __name__ == "__main__":
    main()
