# research-agent

An autonomous research agent for Claude Code. Give it a goal and (optionally) an
eval script; it runs an unbounded reasoning loop, decomposing the problem,
forming hypotheses, attempting solutions (proofs, code, simulations,
counterexample search), evaluating results, and reflecting on what to try next.
It is fire-and-forget: the agent works on its own and writes everything to disk.

## Install

```
/plugin install research-agent@queelius
```

## Commands

| Command | What it does |
|---------|--------------|
| `/research-agent:research <goal> [eval script at ./eval.sh]` | Launch a fresh run. The goal is the body of your message; an eval script is optional. |
| `/research-agent:status` | Read-only progress: cycle count, current focus, and eval trend. Does not touch the agent. |
| `/research-agent:resume` | Continue an interrupted run after a session restart. |
| `/research-agent:synthesize` | Force the run to conclude and write `synthesis.md`. Mainline synthesis compares branches. |
| `/research-agent:branch <name> [focus]` | Fork the run at its checkpoint into a named branch pursuing a competing strategy. |

## Example

```
/research-agent:research Prove or disprove that every even number greater than 2
is the sum of two primes. eval script at ./goldbach_check.sh
```

Then, while it runs:

```
/research-agent:status        # check cycle progress and eval trend
/research-agent:synthesize    # force a wrap-up once results are good enough
```

## The eval contract (optional)

If you pass an eval script, the agent runs it from the working directory with no
arguments. Exit 0 means the goal is achieved; exit 1 means not yet (and if the
last stdout line is `score: <float>`, that float is recorded); any other exit
code is treated as a script error and the agent self-evaluates that cycle.
Results accumulate in `.research/scores.jsonl`. Without a script, the agent
self-evaluates throughout.

## Where output lands

The agent works in your **target project's** directory (not in the plugin) and
maintains a `.research/` directory:

```
.research/
  goal.md         verbatim goal + eval path; written once, never edited
  state.md        current beliefs: sub-problems, hypotheses, current focus
  log.md          append-only cycle log (the defense against context compression)
  attempts/       one subdirectory per attempt, with notes and artifacts
  findings/       confirmed results promoted out of attempts/
  synthesis.md    the final deliverable; its presence means the run concluded
  branches/<name>/  forked strategy lines (own state/log/attempts; goal and
                    parent findings shared read-only)
```

Disk is the source of truth: very long runs may compress earlier conversation
history, so `log.md` and `state.md` let the agent (and `/resume`) reorient. The
single document a future reader relies on is `synthesis.md`.

## Notes

- The agent runs on `model: inherit`, so it uses your session's model. Pick Fable
  for long autonomous runs with `/model fable` (its 1M context window comes with
  the session).
- For internal and editing details, see `CLAUDE.md`.
