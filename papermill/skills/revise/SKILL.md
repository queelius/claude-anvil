---
name: revise
description: >-
  Apply fixes from a multi-agent review report. Launches the reviser
  orchestrator, which triages the findings in .papermill/reviews/, dispatches
  section-writer specialists per finding domain, verifies each fix with the
  owning review specialist, and writes a revision report paired with the
  review. Closes the draft, review, revise loop. Updates .papermill/state.md.
---

# Revise From Review Findings

Launch the multi-agent revision system on an existing review report.

## Step 1: Read Context

Read `.papermill/state.md` (Read tool) if it exists for the paper path, format, and the latest `review_history` entry. Work gracefully without it.

## Step 2: Locate the Review Report

- If the user supplied a report path, use it.
- Otherwise take the newest `.papermill/reviews/*/review.md` (Glob tool, sort by date directory).
- If no report exists, stop and suggest `/papermill:review` first.

If the chosen review_history entry already has a `revised` date, tell the user and ask whether to re-revise against the same report or run a fresh review first.

## Step 3: Confirm Scope

Ask the user (AskUserQuestion) which severities to address: all findings (default), Critical + Major only, or a custom selection. Mention how many findings the report contains per severity so the choice is informed.

## Step 4: Launch the Reviser Orchestrator

Spawn the reviser agent (Agent tool, `subagent_type: papermill:reviser`) with:

    <report>{path to review.md}</report>
    <paper>{manuscript path from state.md or discovery}</paper>
    <scope>{severity filter from Step 3}</scope>
    <mode>interactive</mode>

    Work through the findings with fix-then-verify. Write revision.md next
    to the source review report.

## Step 5: Present Results

Summarize from the agent's report: findings fixed and verified, deferred items that need the author, retry failures (reverted), and the build status. Point at the revision report path.

## Step 6: Update State File

Update `.papermill/state.md` (Edit tool). If `.papermill/state.md` does not exist, skip this step and suggest `/papermill:init`. Updates:

Augment the review_history entry that matches the source report with:

```yaml
    revised: "YYYY-MM-DD"
    findings_fixed: N        # fixed-and-verified count from the revision report
```

Append a timestamped note to the markdown body summarizing the revision pass.

## Step 7: Suggest Next Steps

- If everything in scope was fixed: suggest re-running `/papermill:review` to confirm the recommendation moves toward `ready`.
- If items were deferred: list them and ask the user to decide, then offer to re-run `/papermill:revise` with their decisions.
- If the build failed: fix the build before anything else.
