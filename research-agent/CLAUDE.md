# CLAUDE.md: Research Agent Plugin

## What This Is

An autonomous research agent plugin for Claude Code. Given a goal and an optional eval script, the agent runs an unbounded reasoning loop: decomposing, hypothesizing, attempting (proofs, code, simulations, counterexample search), evaluating, and reflecting. It works directly in the target project directory, creating a `.research/` directory for its artifacts.

## Plugin Structure

```
research-agent/
  .claude-plugin/plugin.json    # Plugin manifest
  skills/research/SKILL.md      # Launch skill: parse goal + eval, spawn agent
  skills/status/SKILL.md        # Read-only status of an in-flight run
  skills/resume/SKILL.md        # Continue an interrupted run
  skills/synthesize/SKILL.md    # Force the run to conclude with synthesis.md
  commands/research.md          # /research-agent:research (launch)
  commands/status.md            # /research-agent:status
  commands/resume.md            # /research-agent:resume
  commands/synthesize.md        # /research-agent:synthesize
  agents/researcher.md          # The autonomous research agent (mode-aware)
  docs/superpowers/             # Design history (specs, plans). Not loaded at runtime.
  CLAUDE.md                     # This file
```

## How It Works

The agent has three modes of operation, selected by the XML tags the
launching skill passes:

- **fresh**: `<goal>...</goal>` plus `<eval>...</eval>`. Used by `/research-agent:research`. Creates `.research/`, writes goal.md, optionally runs the eval baseline, then begins the DECOMPOSE phase.
- **resume**: `<mode>resume</mode>`. Used by `/research-agent:resume`. Reads state.md and log.md, reorients, then continues from the documented current focus.
- **synthesize**: `<mode>synthesize</mode>`. Used by `/research-agent:synthesize`. Reads state.md and log.md, finalizes statuses, writes synthesis.md (with a Branch Comparison section when branches exist), exits without starting new cycles. With `<branch>name</branch>`, concludes only that branch.
- **branch**: `<mode>branch</mode>` plus `<branch>name</branch>`. Used by `/research-agent:branch`. Forks the run at its checkpoint into `.research/branches/<name>/` (own state.md, log.md, scores.jsonl, attempts/, findings/); the parent's goal.md and findings/ are shared read-only. Resume accepts `<branch>` to continue a branch.

The status skill is **not** an agent dispatch: it reads `.research/` files
directly and produces a structured summary. This is faster, cheaper, and
deterministic, and it never accidentally restarts the agent.

## The `.research/` Artifact Contract

The agent operates on the **target project's** working directory (not on
this plugin), creating and maintaining `.research/`. Every mode coordinates
through this directory; treat it as the cross-mode interface.

```
.research/
  goal.md         # Verbatim user goal + eval script path. Written once in fresh mode; never edited.
  state.md        # Current beliefs: sub-problems, hypotheses, current focus. Updated every REFLECT.
  log.md          # Append-only cycle log. The defense against context compression.
  scores.jsonl    # One JSON line per eval run: {cycle, attempt, exit, score, ts}. Status reads this for the eval trend.
  attempts/       # One subdirectory per attempt: NNN-<slug>/notes.md plus artifacts.
  findings/       # Confirmed results promoted out of attempts/.
  synthesis.md    # Final deliverable. Presence => the run has concluded.
  branches/<name>/  # Forked strategy lines: each holds its own state.md, log.md,
                    # scores.jsonl, attempts/, findings/, and (when concluded)
                    # synthesis.md. Branches never write the parent's goal.md,
                    # log.md, or state.md; promotion into the parent's findings/
                    # happens only at synthesis, with a provenance note.
```

Discipline points the agent enforces: `log.md` is append-only; `state.md`
is the source of truth for "where am I?"; `synthesis.md` is the single
document a future reader relies on. Any new mode you add must respect
these invariants. The branch mode follows exactly this rule: it never rewrites `goal.md` or
rewinds `log.md`; it forks into the `branches/<name>/` sibling subtree.

## Editing Guidelines

- The agent prompt (`agents/researcher.md`) contains the full research methodology and mode dispatch. It is intentionally large. Keep sections well-organized with clear headers.
- Each skill (`skills/<name>/SKILL.md`) is thin. The skill's job is to parse user intent and prepare the right XML tags for the agent (or, for status, read files directly). Do not put research methodology in skills.
- Commands are one-liners. Keep them that way.
- Skills that dispatch the researcher use `subagent_type: research-agent:researcher` (see `skills/resume/SKILL.md` and `skills/synthesize/SKILL.md`). Any new mode that runs the agent must use the same subagent_type so it inherits the canonical system prompt.
- The agent uses `model: fable`, which resolves to the latest Fable (currently Fable 5 with the 1M context window when the harness enables it). Long research runs still need file-system persistence (`log.md`, `state.md`, `attempts/`) because very long runs may compress earlier history; the disk is always the source of truth.

When adding a new mode (e.g., a "branch" mode that forks a research run from a checkpoint), edit four files in lockstep: (1) a new `skills/<mode>/SKILL.md`, (2) a new `commands/<mode>.md`, (3) a new section in the agent's `Initialization` block documenting the mode and its XML trigger tag, and (4) the mode list in the "How It Works" section of this file. If the new mode reads or writes `.research/`, also extend the Artifact Contract section above to describe any new files or new shape on existing ones.

## Capabilities

The researcher has three categories of tools:

1. **File and shell**: `Bash`, `BashOutput`, `KillShell`, `Read`, `Write`, `Edit`, `Glob`, `Grep`. The Bash + BashOutput + KillShell combination lets the researcher launch long-running experiments with `run_in_background: true`, monitor accumulated output, and terminate runs that have stalled.
2. **Research**: `WebSearch`, `WebFetch` for prior-art lookups, paper retrieval, and reference verification.
3. **Delegation**: `Task` for spawning child sub-agents that pursue parallel approaches (different proof strategies, different parameter regimes, different literature angles). Sub-agent results return as structured summaries that the researcher integrates into `log.md`. Working artifacts from a child sub-agent should land in a sibling subdirectory under `attempts/` so they are visible to status, resume, and synthesize.

Note the two-level use of `Task`. The launching skills use `Task` with `subagent_type: research-agent:researcher` to spawn the *top-level* researcher. The researcher itself then uses `Task` for parallel exploration of *child* sub-agents. They are the same tool but different roles. Do not conflate them when editing.

When extending the agent, prefer giving it more capability in these existing categories over adding new ones. Adding more tool categories without a clear use case dilutes the prompt.
