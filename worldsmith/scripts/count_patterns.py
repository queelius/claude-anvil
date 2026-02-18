#!/usr/bin/env python3
"""Count prose patterns across manuscript files.

Reads pattern definitions from a markdown file and counts occurrences.
Override the default patterns by placing a patterns.md in .worldsmith/
in your project root.

Usage: count_patterns.py <manuscript-glob> [patterns-file]
Example: count_patterns.py "chapters/*.md"
Example: count_patterns.py "manuscript/*.tex" my-patterns.md
"""

import sys
import re
import glob
import os


def parse_patterns(path):
    """Parse a patterns.md file into [(category, [(type, pattern)])]."""
    categories = []
    current_name = None
    current_patterns = []

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("## "):
                if current_name:
                    categories.append((current_name, current_patterns))
                current_name = line[3:].strip()
                current_patterns = []
            elif current_name and line.startswith("<!-- regex:") and line.endswith("-->"):
                pattern = line[len("<!-- regex:"):-len("-->")].strip()
                current_patterns.append(("regex", pattern))
            elif current_name and line and not line.startswith("#") and not line.startswith("<!--"):
                for p in line.split(","):
                    p = p.strip()
                    if p:
                        current_patterns.append(("literal", p))

    if current_name:
        categories.append((current_name, current_patterns))

    return categories


def count_pattern(files_text, pattern_type, pattern):
    """Count occurrences of a pattern across pre-read file texts."""
    if pattern_type == "regex":
        rx = re.compile(pattern, re.IGNORECASE)
        return sum(len(rx.findall(text)) for text in files_text)
    else:
        rx = re.compile(r"\b" + re.escape(pattern) + r"\b", re.IGNORECASE)
        return sum(len(rx.findall(text)) for text in files_text)


def find_patterns_file(explicit_arg=None):
    """Resolve patterns file: explicit arg > .worldsmith/ override > bundled default."""
    if explicit_arg:
        return explicit_arg
    project_override = os.path.join(".worldsmith", "patterns.md")
    if os.path.isfile(project_override):
        return project_override
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "patterns.md")


def main():
    if len(sys.argv) < 2:
        print("Usage: count_patterns.py <manuscript-glob> [patterns.md]", file=sys.stderr)
        sys.exit(1)

    manuscript_glob = sys.argv[1]
    files = sorted(glob.glob(manuscript_glob, recursive=True))
    if not files:
        print(f"No files matching: {manuscript_glob}", file=sys.stderr)
        sys.exit(1)

    patterns_path = find_patterns_file(sys.argv[2] if len(sys.argv) >= 3 else None)
    if not os.path.isfile(patterns_path):
        print(f"Patterns file not found: {patterns_path}", file=sys.stderr)
        sys.exit(1)

    # Read all files once
    files_text = []
    for path in files:
        try:
            with open(path) as f:
                files_text.append(f.read())
        except (IOError, UnicodeDecodeError):
            continue

    categories = parse_patterns(patterns_path)

    print("=== Prose Pattern Audit ===")
    print(f"Patterns: {patterns_path}")
    print(f"Files: {len(files)}")
    print()

    for category, patterns in categories:
        print(f"--- {category} ---")
        for ptype, pattern in patterns:
            count = count_pattern(files_text, ptype, pattern)
            if count > 0:
                label = f"/{pattern}/" if ptype == "regex" else pattern
                print(f"  {label:<24s} {count}")
        print()

    total_words = sum(len(text.split()) for text in files_text)
    print("--- Manuscript Size ---")
    print(f"  Total words: ~{total_words}")


if __name__ == "__main__":
    main()
