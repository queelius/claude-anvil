---
description: Launch multi-agent editorial review — consistency, craft, voice, and structure auditors in parallel
allowed-tools: Read, Write, Glob, Grep, Bash, Task
argument-hint: "[scope: full manuscript, or specific chapters e.g. 'chapters 3-5']"
---

# /worldsmith:review

Launch the **reviewer** orchestrator agent for a deep, multi-agent editorial review.

This spawns 4 specialist auditors in parallel (consistency, craft, voice, structure), cross-verifies critical findings, and produces a unified report to `.worldsmith/reviews/YYYY-MM-DD/`.

Pass `$ARGUMENTS` as the review scope. If no scope is specified, review the full manuscript.

This is the thorough review. For a lighter single-pass diagnostic, use `/worldsmith:check`.
