---
description: Write a master spec or per-Part design spec via Socratic dialogue with the user
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
argument-hint: "[master | part1 | part2 | ...]"
---

# /bookwright:design

Write a master design spec (book-level audience, structure, threads) or a per-Part design spec (chapters in this Part, their sections, page budgets) for the active bookwright project.

## What it produces

A design-spec markdown file at `docs/superpowers/specs/YYYY-MM-DD-<scope>-design.md`.

A master spec covers: thesis, audience, format/tone, structure (parts + chapters), running threads, citation policy, repository layout, prerequisites, exercises convention, sequencing/build plan, risks, out-of-scope, success criteria.

A per-Part spec covers: purpose of this part, inherited commitments from the master spec, per-chapter outline tables (section / title / pages / source / purpose), forward/backward reference map, page budget, sequencing for the per-chapter implementation plans, open action items, risks, out-of-scope, success criteria.

## Steps

1. Read the master spec if it exists (for per-Part work).
2. Run a Socratic Q&A with the user (use AskUserQuestion) on: audience, scope, structure, sources, notebook discipline, page budgets, running threads.
3. Synthesize answers into a design-spec markdown file. Follow the structure of the Bernoulli spec at `~/github/bernoulli/docs/superpowers/specs/2026-05-02-bernoulli-textbook-part1-design.md` as the reference template.
4. Save to the spec path; report it back to the user.
5. Suggest next step: `/bookwright:plan chapterN` for the first chapter.
