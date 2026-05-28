---
description: Fast mechanical diagnostics on a section, chapter, part, or full book
allowed-tools: Read, Bash, Glob, Grep
argument-hint: "[section | chapter | part | book] [name]"
---

# /bookwright:check

Run mechanical diagnostics. No editorial judgment; checks that can be automated.

## What it runs

1. Build the book: `cd book && make cleanall && make`. Expects exit 0.
2. Cross-reference resolution: grep `book.log` for `Reference undefined` and `Citation undefined`. Expects only the documented baseline.
3. Per-chapter page-count audit: read `book.toc`, compute per-chapter page spans, compare to the per-chapter targets in the plan files. Expects each chapter within plus-or-minus 30 percent of its target.
4. Running-thread inventory: for each thread named in the master spec, grep chapter files for thread keywords; verify the thread carries across the chapters the spec assigned it to.
5. Soul-voice audit: re-run the soul-voice hook's pattern checks across all chapter .tex files (the hook runs at edit time, but `/check` re-runs as a defense-in-depth audit).
6. LaTeX-macro-leak audit: re-run the macro-leak hook's pattern checks.

## Scope

- `section <path>`: only the named section file.
- `chapter <name>`: all section files in `book/chapters/<chapter>/`.
- `part <name>`: all chapters in the named Part.
- `book`: everything (default if no scope given).

## Output

A short bullet report: each check's PASS/FAIL/NOTE. On FAIL, surface the specific lines or refs. No fix attempted; this is read-only diagnostics.
