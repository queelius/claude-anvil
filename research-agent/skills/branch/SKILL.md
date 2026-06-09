---
name: branch
description: >-
  Fork an in-flight research-agent run at its current checkpoint into a named
  branch with its own state, log, and attempts, sharing the parent's goal and
  findings read-only. Use to pursue a competing strategy without disturbing
  the main line. The synthesize skill later compares branches.
---

# Branch a Research Run

Fork the current run so a competing strategy can be explored in parallel with (or instead of) the main line, without touching the main line's state.

## Step 1: Parse Arguments

Extract from the user's message:

1. **Branch name** (required): kebab-case identifier, e.g. `induction-proof`, `adversarial-search`. Derive one from the stated strategy if the user did not name it explicitly, and confirm it.
2. **Branch focus** (optional): one or two sentences describing what this branch should pursue differently from the main line.

## Step 2: Verify the Run and the Name

- `.research/goal.md` must exist (Read tool); if not, there is nothing to branch: suggest `/research-agent:research`.
- `.research/branches/<name>/` must NOT already exist (Glob tool). If it does, offer `/research-agent:resume <name>` instead, or a different name.

## Step 3: Launch the Researcher in Branch Mode

Spawn the researcher agent (Agent tool, `subagent_type: research-agent:researcher`) with this prompt structure:

    <mode>branch</mode>

    <branch>{kebab-case name}</branch>

    <branch-focus>
    {the focus, or "explore an alternative approach to the goal"}
    </branch-focus>

    <working_directory>
    {absolute path to current working directory}
    </working_directory>

    Fork the run at its current checkpoint per your branch-mode
    initialization. Never write to the parent's goal.md, log.md, or
    state.md; all branch work lives under .research/branches/{name}/.

## Step 4: Inform the User

> Branch `{name}` forked from the current checkpoint. It works under `.research/branches/{name}/` with its own state, log, and attempts; the goal and the parent's confirmed findings are shared read-only.
>
> - `/research-agent:status` shows all branches alongside the main line
> - `/research-agent:resume {name}` continues this branch later
> - `/research-agent:synthesize {name}` concludes just this branch; a main-line `/research-agent:synthesize` compares all branches
