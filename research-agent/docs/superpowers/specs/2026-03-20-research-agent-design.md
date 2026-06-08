# Research Agent: Design Spec

**Date:** 2026-03-20
**Plugin:** `research-agent`
**Version:** 0.1.0
**Status:** Draft

## Overview

An autonomous research agent plugin for the Claude Code marketplace. Given a natural-language goal and an optional eval script, the agent runs an unbounded reasoning loop (writing proofs, code, tests, simulations, and counterexample searches) until the goal is achieved, declared unachievable, or the user interrupts.

The agent is fire-and-forget. It makes all decisions autonomously and communicates only through files it writes to disk.

## Requirements

- **Goal format:** Natural-language description + optional path to an executable eval script
- **Research modalities:** Formal proofs, code + unit tests, simulations/experiments, counterexample search, Lean/formal verification programs. All available from v0.1; agent chooses dynamically
- **Session model:** Single long-running Claude Code session, no orchestrator or restart loop
- **Model:** `claude-opus-4-6` (Opus 4.6 with 1M context window) for maximum reasoning depth and session coherence
- **Workspace:** Agent works directly in the target project directory, creating a `.research/` directory for its artifacts
- **Output:** Append-only research log, surviving code/proof artifacts, and a polished synthesis document
- **Autonomy:** Fully autonomous, no user interaction during execution
- **Distribution:** Claude Code plugin in the `queelius` marketplace

## Architecture

### Plugin Structure

```
research-agent/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── research/
│       └── SKILL.md
├── commands/
│   └── research.md
├── agents/
│   └── researcher.md
└── CLAUDE.md
```

**`commands/research.md`** Thin slash command. Triggers the research skill.

**`skills/research/SKILL.md`** Launch skill. Parses the user's goal and optional eval script path from their message, then spawns the researcher agent via the Agent tool.

**`agents/researcher.md`** The monolithic autonomous research agent. Contains the full research methodology as a system prompt. Uses `claude-opus-4-6` (1M context) as its model, chosen for long-session coherence. This is where all the logic lives.

### The Research Loop

The agent follows an unbounded cycle:

```
GOAL (user-provided)
  │
  ▼
DECOMPOSE: break the goal into sub-problems and open questions
  │
  ▼
HYPOTHESIZE: form a concrete, testable hypothesis about one sub-problem
  │
  ▼
ATTEMPT: choose a modality and execute:
  │   • Write a formal proof or derivation
  │   • Write code + unit tests
  │   • Run a simulation or experiment
  │   • Search for a counterexample
  │   • Write a Lean/formal verification program
  │
  ▼
EVALUATE: did it work?
  │   • If eval script exists: run it, check exit code and output
  │   • If not: reason about the result against the goal
  │   • Log the outcome
  │
  ▼
REFLECT: what did we learn?
  │   • Revise sub-problem decomposition
  │   • Mark hypotheses as confirmed / refuted / inconclusive
  │   • Identify new sub-problems or hypotheses
  │   • Decide: continue current thread, pivot, or conclude
  │
  └──▶ loop back to HYPOTHESIZE (or DECOMPOSE if the landscape shifted)
```

**Termination conditions:**
1. Goal achieved (eval exits 0, or theorem proved, or agent is satisfied)
2. Agent concludes the goal is unachievable and documents why
3. User interrupts the session

### Artifact Layout

The agent creates `.research/` in the target project root:

```
<target-project>/
└── .research/
    ├── goal.md              # Original goal + eval script path (if any)
    ├── log.md               # Append-only research journal
    ├── state.md             # Current beliefs, open hypotheses, sub-problems
    ├── attempts/            # One dir per attempt, numbered sequentially
    │   ├── 001-<slug>/
    │   │   ├── notes.md     # What was tried and what happened
    │   │   └── ...          # Artifacts (code, proofs, test files)
    │   ├── 002-<slug>/
    │   │   └── ...
    │   └── ...
    ├── findings/            # Confirmed results only
    │   └── ...              # Proved theorems, validated code, etc.
    └── synthesis.md         # Final deliverable, written at conclusion
```

**Invariants:**
- `log.md` is append-only. The agent never edits previous entries.
- `state.md` is mutable. Updated each cycle with current beliefs.
- `attempts/` preserves everything, including failed attempts.
- `findings/` contains only verified, confirmed results.
- `synthesis.md` is written once when the agent concludes.

Code artifacts start in their attempt directory and get promoted to `findings/` (or the project root) upon confirmation.

The agent does not modify the project's `.gitignore`. If the user wants to exclude `.research/` from version control, they can add it themselves.

### Research Log Format

Each cycle appends a self-contained entry to `log.md`:

```markdown
# Research Log

## Goal
<natural-language goal>

## Eval
<path to eval script, or "self-evaluation">

---

### Cycle N (<ISO-8601 timestamp>)
**Phase:** <DECOMPOSE | HYPOTHESIZE | ATTEMPT | EVALUATE | REFLECT>
**Hypothesis:** <what's being tested, if applicable>
**Modality:** <proof | code+tests | simulation | counterexample | lean>
**Attempt:** `attempts/<NNN>-<slug>/`
**Result:** <pass/fail with brief explanation>
**Eval score:** <numeric score if eval script returned one>
**Reflection:** <what was learned, what to do next>
```

### Eval Script Interface

The eval script contract:

- **Input:** The agent runs the script via `bash` from the project root
- **Exit code:** `0` = goal achieved, non-zero = not yet
- **Stdout:** Parsed as feedback, either a JSON object with `score` and/or `msg` fields, or free text
- **Frequency:** Run after each attempt cycle (when an eval script is provided)

The agent tracks score progression over time. A stalling or declining score informs the REFLECT phase. The agent uses it to decide when to pivot strategies.

When no eval script is provided, the agent self-evaluates by reasoning against the natural-language goal and logs a structured self-assessment.

### Agent System Prompt Structure

The `researcher.md` agent prompt is organized into these sections:

1. **Identity & mission.** Autonomous research agent, patient and methodical, runs indefinitely.
2. **The research loop.** The full DECOMPOSE → HYPOTHESIZE → ATTEMPT → EVALUATE → REFLECT cycle as the agent's core operating procedure.
3. **Modality playbooks.** Concise guidance for each research mode:
   - Formal proofs: structure, proof strategies, when to try contradiction, when to pivot to counterexample search
   - Code + tests: small testable programs, always run them, treat test failures as signal
   - Simulations: design with clear hypotheses, vary parameters, analyze results
   - Counterexample search: systematic edge case exploration, random testing, boundary analysis
   - Lean/formal verification: when to reach for machine-checked proofs
4. **Logging discipline.** Non-negotiable rules for maintaining log.md, state.md, and attempt notes.
5. **Decision-making autonomy.** When to pivot vs. persist, when to declare done, how to handle uncertainty.
6. **Termination protocol.** How to conclude, requirement to write synthesis.md.
7. **Tool list.** Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch.

### Agent Tool Set

The researcher agent is granted:

| Tool | Purpose |
|------|---------|
| Bash | Run code, tests, simulations, eval scripts |
| Read | Read project files, prior attempts, log |
| Write | Create new files (code, proofs, notes) |
| Edit | Modify existing files |
| Glob | Find files by pattern |
| Grep | Search file contents |
| WebSearch | Search for relevant papers, algorithms, prior art |
| WebFetch | Retrieve web content |

## Interaction Flow

1. User invokes `/research` with their goal (and optionally an eval script path)
2. The **command** delegates to the **skill**
3. The **skill** parses the goal and eval path, then launches the **agent** via the Agent tool
4. The **agent** creates `.research/`, writes `goal.md`, begins the loop
5. The agent runs autonomously (decomposing, hypothesizing, attempting, evaluating, reflecting) logging everything
6. When done (or interrupted), the agent writes `synthesis.md` and returns

The user can monitor progress at any time by reading `.research/log.md`.

## Design Decisions

**Why monolithic (not orchestrator + specialists)?**
Reasoning coherence. When a proof attempt fails and suggests a simulation, that insight lives in the same context window. The agent makes lateral connections between formal and empirical results because it holds everything in one thread. The research log on disk compensates for eventual context compression.

**Why single session (not checkpoint + restart)?**
Simplest architecture. No serialization/deserialization overhead, no orchestrator script. The state files (log.md, state.md) exist primarily as insurance against context compression, not as a restart mechanism.

**Why .research/ in the target project?**
The agent needs to write and run code in the project. Keeping research artifacts colocated means the agent can reference project files naturally and its code artifacts can import project modules. The `.research/` prefix keeps things organized and gitignore-friendly.

## Future Considerations (Not in v0.1)

- **Resume support:** Read `.research/state.md` on launch to continue a prior session
- **Progress notifications:** Periodic summaries pushed to the user (Slack, email)
- **Parallel exploration:** Spawn subagents for independent sub-problems
- **Integration with papermill:** Hand off findings to papermill for paper drafting
