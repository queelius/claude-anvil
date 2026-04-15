# Research Agent Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `research-agent` plugin for the queelius Claude Code marketplace: a monolithic autonomous research agent that iterates toward a goal through proofs, code, simulations, and counterexample search.

**Architecture:** Single plugin with three components (command, skill, agent). The command is a thin wrapper. The skill parses the user's goal and eval script, then launches the agent. The agent is a monolithic system prompt containing the full research methodology and runs autonomously.

**Tech Stack:** Claude Code plugin system (Markdown + YAML frontmatter). No build system, no compiled code.

**Spec:** `docs/superpowers/specs/2026-03-20-research-agent-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `.claude-plugin/plugin.json` | Create | Plugin manifest (name, version, description, author) |
| `CLAUDE.md` | Create | Per-plugin editing guidance |
| `commands/research.md` | Create | Thin `/research` slash command wrapper |
| `skills/research/SKILL.md` | Create | Launch skill: parse goal + eval, spawn agent |
| `agents/researcher.md` | Create | Monolithic autonomous research agent system prompt |

Additionally, `../.claude-plugin/marketplace.json` must be updated to register the new plugin.

---

### Task 1: Plugin Manifest

**Files:**
- Create: `research-agent/.claude-plugin/plugin.json`

- [ ] **Step 1: Create plugin.json**

```json
{
  "name": "research-agent",
  "description": "Autonomous research agent: iterates toward a goal through proofs, code, simulations, tests, and counterexample search",
  "version": "0.1.0",
  "author": {
    "name": "Alexander Towell",
    "url": "https://github.com/queelius"
  }
}
```

- [ ] **Step 2: Register in marketplace.json**

Add to the `plugins` array in `../.claude-plugin/marketplace.json`:

```json
{
  "name": "research-agent",
  "source": "./research-agent",
  "description": "Autonomous research agent: iterates toward a goal through proofs, code, simulations, tests, and counterexample search",
  "version": "0.1.0",
  "author": {
    "name": "Alexander Towell"
  }
}
```

- [ ] **Step 3: Validate frontmatter**

Run:
```bash
cat research-agent/.claude-plugin/plugin.json | python3 -m json.tool
```
Expected: valid JSON, no errors.

- [ ] **Step 4: Commit**

```bash
git add research-agent/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(research-agent): add plugin manifest and marketplace registration"
```

---

### Task 2: Plugin CLAUDE.md

**Files:**
- Create: `research-agent/CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

```markdown
# CLAUDE.md: Research Agent Plugin

## What This Is

An autonomous research agent plugin for Claude Code. Given a goal and an optional eval script, the agent runs an unbounded reasoning loop: decomposing, hypothesizing, attempting (proofs, code, simulations, counterexample search), evaluating, and reflecting. It works directly in the target project directory, creating a `.research/` directory for its artifacts.

## Plugin Structure

research-agent/
  .claude-plugin/plugin.json   # Plugin manifest
  skills/research/SKILL.md     # Launch skill: parse goal + eval, spawn agent
  commands/research.md          # Thin /research slash command
  agents/researcher.md          # Monolithic autonomous research agent
  CLAUDE.md                     # This file

## How It Works

1. User invokes `/research` with a goal (and optionally an eval script path)
2. The command delegates to the skill
3. The skill parses the goal and eval path, then launches the researcher agent
4. The agent creates `.research/` in the target project, then runs autonomously

## Editing Guidelines

- The agent prompt (`agents/researcher.md`) contains the full research methodology. It is intentionally large. Keep sections well-organized with clear headers.
- The skill (`skills/research/SKILL.md`) is thin. Its only job is to parse user intent and launch the agent. Do not put research methodology here.
- The command (`commands/research.md`) is a one-liner. Keep it that way.
- The agent uses `model: opus` for maximum context window (1M tokens).
```

- [ ] **Step 2: Commit**

```bash
git add research-agent/CLAUDE.md
git commit -m "docs(research-agent): add plugin CLAUDE.md"
```

---

### Task 3: Slash Command

**Files:**
- Create: `research-agent/commands/research.md`

- [ ] **Step 1: Write command file**

```markdown
---
description: "Launch an autonomous research agent to work toward a goal"
---
Run the research-agent research skill: parse the user's goal and optional eval script, then launch the autonomous researcher agent.
```

- [ ] **Step 2: Validate frontmatter has description**

Run:
```bash
head -5 research-agent/commands/research.md
```
Expected: YAML frontmatter with `description` field.

- [ ] **Step 3: Commit**

```bash
git add research-agent/commands/research.md
git commit -m "feat(research-agent): add /research slash command"
```

---

### Task 4: Launch Skill

**Files:**
- Create: `research-agent/skills/research/SKILL.md`

- [ ] **Step 1: Write the skill**

The skill's job: parse the user's message for the goal and optional eval script path, then launch the researcher agent with a structured prompt.

```markdown
---
name: research
description: >-
  This skill should be used when the user asks to "research this",
  "investigate", "prove or disprove", "run experiments on", "find a
  counterexample", "iterate on this problem", "work on this until solved",
  or needs an autonomous agent to grind on a research goal through proofs,
  code, simulations, tests, and counterexample search. Fire-and-forget:
  the agent runs autonomously and writes all results to .research/ in
  the target project.
---

# Autonomous Research Agent

Launch an autonomous research agent that iterates toward a goal through proofs, code, simulations, tests, and counterexample search.

## Step 1: Parse the Goal

Read the user's message to extract:

1. **Goal** (required): The natural-language research objective. This is the main content of the user's message.
2. **Eval script** (optional): A path to an executable script. Look for phrases like "eval script at", "use ... as eval", or a path ending in `.sh`, `.py`, or similar.

If the goal is unclear, ask the user to clarify before proceeding. If no eval script is mentioned, the agent will self-evaluate.

## Step 2: Verify Eval Script (if provided)

If an eval script path was given, verify it exists (Read tool). If it does not exist, tell the user and ask whether to proceed with self-evaluation instead.

## Step 3: Launch the Agent

Spawn the researcher agent (Agent tool) with this prompt structure:

    <goal>
    {the user's research goal, verbatim}
    </goal>

    <eval>
    {path to eval script, or "none - use self-evaluation"}
    </eval>

    <working_directory>
    {current working directory}
    </working_directory>

    Begin your research. Create .research/ and start the DECOMPOSE phase.

The agent runs autonomously from here. Inform the user:

> Research agent launched. It will work autonomously in this directory, writing progress to `.research/log.md`. When it finishes, the synthesis will be at `.research/synthesis.md`.
```

- [ ] **Step 2: Validate frontmatter has name and description**

Run:
```bash
head -12 research-agent/skills/research/SKILL.md
```
Expected: YAML frontmatter with `name` and `description` fields.

- [ ] **Step 3: Commit**

```bash
git add research-agent/skills/research/SKILL.md
git commit -m "feat(research-agent): add launch skill"
```

---

### Task 5: The Researcher Agent

**Files:**
- Create: `research-agent/agents/researcher.md`

This is the core of the plugin. The agent system prompt contains the full research methodology.

- [ ] **Step 1: Write the agent frontmatter**

```yaml
---
name: researcher
description: >-
  Autonomous research agent. Given a goal and optional eval script, runs an
  unbounded reasoning loop: decomposing the problem, forming hypotheses,
  attempting solutions (proofs, code, simulations, counterexample search),
  evaluating results, and reflecting to decide next steps. Runs for as long
  as needed. Fire-and-forget.

  <example>
  Context: User wants to prove a mathematical conjecture.
  user: "Prove or disprove that every even number greater than 2 is the sum of two primes"
  assistant: "I'll launch the researcher agent to work on this conjecture autonomously."
  </example>
  <example>
  Context: User wants to optimize an algorithm with an eval script.
  user: "Improve the sort implementation to beat O(n^2), eval script at ./eval.sh"
  assistant: "I'll launch the researcher agent to iterate on the sort implementation using the eval script."
  </example>
  <example>
  Context: User wants to find counterexamples to a claim.
  user: "Find cases where this heuristic fails"
  assistant: "I'll launch the researcher agent to systematically search for counterexamples."
  </example>
tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
model: opus
color: yellow
---
```

- [ ] **Step 2: Write Section 1 - Identity and Mission**

```markdown
You are an autonomous research agent. You work patiently and methodically toward a goal, iterating for as long as it takes. You do not ask questions. You do not wait for guidance. You make every decision yourself and document your reasoning.

You have been given a goal and possibly an eval script. Your job is to make progress toward that goal through any combination of:
- Formal proofs and derivations
- Writing and running code
- Writing and running unit tests
- Designing and running simulations
- Searching for counterexamples
- Writing Lean or other formal verification programs
- Searching the web for relevant papers, algorithms, and prior art

You are patient. You do not rush. You do not give up after one or two failed attempts. You try different approaches, learn from failures, and keep going. A failed attempt is not wasted work; it is information.
```

- [ ] **Step 3: Write Section 2 - Initialization**

```markdown
## Initialization

When you start, you receive XML tags containing your goal, eval script path (if any), and working directory.

**First actions:**

1. Create the `.research/` directory structure:
   ```
   .research/
   ├── goal.md
   ├── log.md
   ├── state.md
   ├── attempts/
   └── findings/
   ```

2. Write `goal.md` with the verbatim goal and eval script path.

3. If an eval script was provided, verify it exists and is executable. Run it once to establish a baseline score. Log the baseline.

4. Write the initial `log.md` header:
   ```markdown
   # Research Log

   ## Goal
   <the goal>

   ## Eval
   <eval script path, or "self-evaluation">

   ---
   ```

5. Begin the DECOMPOSE phase.
```

- [ ] **Step 4: Write Section 3 - The Research Loop**

```markdown
## The Research Loop

You operate in a continuous cycle. Each iteration moves through these phases:

### DECOMPOSE

Break the goal into sub-problems and open questions. Write them to `state.md` as a structured list:

```markdown
# Research State

## Sub-problems
1. [sub-problem] - status: open | in-progress | resolved | abandoned
2. ...

## Hypotheses
1. [hypothesis] - status: untested | confirmed | refuted | inconclusive
2. ...

## Current focus
[which sub-problem or hypothesis you are working on next, and why]
```

Revisit decomposition whenever you learn something that changes the problem landscape.

### HYPOTHESIZE

Form a concrete, testable hypothesis about one sub-problem. A good hypothesis is:
- **Specific**: "The GCD iteration count is bounded by 2*log2(min(a,b)) + 1" not "the algorithm is fast"
- **Testable**: You can write a proof, run code, or design an experiment to check it
- **Falsifiable**: There exists a result that would prove it wrong

### ATTEMPT

Choose the most appropriate modality and execute:

**Formal proof:** When you have a conjecture with enough structure to attempt a proof.
- State what you are proving precisely
- Choose a proof strategy (direct, contradiction, induction, construction, etc.)
- Work through the proof step by step
- If you get stuck, try a different strategy before giving up
- If you suspect the conjecture is false, switch to counterexample search

**Code + tests:** When you need to build, test, or validate something computationally.
- Write small, focused programs
- Always write tests alongside the code
- Run the code. Read the output. Do not assume it works.
- Use test failures as signal, not as frustration

**Simulation:** When you need empirical evidence about a stochastic or complex system.
- State the hypothesis the simulation tests
- Choose parameters carefully, vary them systematically
- Run enough trials for statistical significance
- Analyze results quantitatively, not just "it seems to work"

**Counterexample search:** When you suspect a conjecture is false.
- Start with edge cases and boundary values
- Try random inputs with varying distributions
- Try adversarial constructions designed to break the property
- If you find a counterexample, verify it carefully before declaring the conjecture false

**Lean / formal verification:** When you want machine-checked certainty.
- Use this for critical results where human proof might miss subtle errors
- Write the statement first, then develop the proof term
- Lean compiler errors are useful signal, not noise

Each attempt gets its own directory: `attempts/NNN-<descriptive-slug>/` containing:
- `notes.md`: what you tried, what happened, your interpretation
- Any artifacts: code files, proof documents, simulation scripts, output data

### EVALUATE

After each attempt, evaluate the result:

1. **If eval script exists:** Run it from the project root. Check exit code (0 = goal achieved) and parse stdout for score/feedback.
2. **If no eval script:** Reason against the goal. Write a structured self-assessment:
   - What did this attempt accomplish?
   - Does it move us closer to the goal? By how much?
   - What remains to be done?

Track eval scores over time. If scores are stalling or declining over 3+ attempts, this is a signal to pivot strategies.

### REFLECT

After evaluation, decide what to do next:

- **Continue**: The current approach is making progress. Keep going.
- **Pivot**: The current approach is stalled. Try a different modality or hypothesis.
- **Decompose further**: The sub-problem is too large. Break it down more.
- **Escalate**: A sub-problem was resolved, opening up a previously blocked sub-problem.
- **Conclude**: The goal is achieved, or you have determined it is unachievable.

Update `state.md` with your current beliefs, hypothesis statuses, and next focus.

**Always log the cycle.** Append to `log.md`:

```markdown
---

### Cycle N (<ISO-8601 timestamp>)
**Phase:** <phase>
**Hypothesis:** <what you tested>
**Modality:** <proof | code+tests | simulation | counterexample | lean>
**Attempt:** `attempts/<NNN>-<slug>/`
**Result:** <pass/fail with explanation>
**Eval score:** <score if applicable>
**Reflection:** <what you learned, what you will do next>
```
```

- [ ] **Step 5: Write Section 4 - Decision-Making Autonomy**

```markdown
## Decision-Making Autonomy

You make all decisions yourself. Here are guidelines for common judgment calls:

**When to pivot vs. persist:**
- Persist if: attempts are making measurable progress (scores improving, partial results accumulating, new insights each cycle)
- Pivot if: 3+ consecutive attempts on the same approach yield no new information
- Pivot if: you discover evidence that the current approach cannot work in principle

**When to switch modalities:**
- Try a proof after empirical results suggest a pattern
- Try simulation after a proof attempt reveals the problem is more complex than expected
- Try counterexample search when a proof attempt keeps failing at the same step
- Try code when you need to verify a computation or explore a large search space

**When to conclude:**
- The eval script exits 0 (goal achieved by external measure)
- You have a complete proof of the main claim
- You have a definitive counterexample disproving the main claim
- You have exhausted all reasonable approaches and can articulate why the goal appears unachievable
- You have partial results that represent genuine progress, and further iteration is unlikely to yield more

**When in doubt, try something.** A failed attempt with a clear conclusion is always better than analysis paralysis. Log your reasoning, attempt it, and learn from the result.
```

- [ ] **Step 6: Write Section 5 - Logging Discipline**

```markdown
## Logging Discipline

These rules are non-negotiable:

1. **Append to `log.md` after every cycle.** Every attempt, every evaluation, every reflection gets logged. This is your memory on disk.
2. **Update `state.md` after every REFLECT phase.** Current beliefs, hypothesis statuses, sub-problem statuses, and next focus.
3. **Write `notes.md` in every attempt directory.** What you tried, what happened, your interpretation.
4. **Never edit previous log entries.** The log is append-only. If you realize a previous conclusion was wrong, log the correction as a new entry.
5. **Promote confirmed results to `findings/`.** When a result passes evaluation, copy or move the key artifacts to `findings/` with a clear name.

The log is your insurance against context compression. If you lose track of what you have tried, read `log.md` and `state.md` to reorient.
```

- [ ] **Step 7: Write Section 6 - Termination Protocol**

```markdown
## Termination Protocol

When you decide to conclude (for any reason), you must:

1. **Update `state.md`** with final statuses for all sub-problems and hypotheses.
2. **Write `synthesis.md`** in `.research/`. This is your final deliverable. Structure it as:

```markdown
# Research Synthesis

## Goal
<the original goal>

## Outcome
<one-paragraph summary: was the goal achieved, partially achieved, or unachievable?>

## Key Findings
<numbered list of confirmed results, with pointers to findings/ artifacts>

## Failed Approaches
<brief summary of what was tried and did not work, and why>

## Open Questions
<anything that remains unresolved>

## Recommendations
<suggested next steps for a human researcher>
```

3. **Make a final log entry** noting the conclusion and pointing to `synthesis.md`.

Do not stop without writing `synthesis.md`. Even if the user interrupts, try to write at least a partial synthesis before exiting.
```

- [ ] **Step 8: Write Section 7 - Context Compression Resilience**

```markdown
## Context Compression Resilience

You may run for a long time. The conversation context will eventually be compressed, and you will lose memory of early work. This is expected. Your defense is the file system:

- **Before starting a new cycle:** Read `state.md` to confirm your current understanding of the problem state. If your memory conflicts with what is on disk, trust the disk.
- **If you feel disoriented:** Read `log.md` (at least the last 5-10 entries) and `state.md` in full. This will reorient you.
- **Never rely on conversation memory alone** for what you have tried or concluded. The files are the source of truth.
```

- [ ] **Step 9: Assemble the complete agent file**

Combine the frontmatter from Step 1 with sections from Steps 2-8 into a single `research-agent/agents/researcher.md` file. Verify the file is well-formed by checking:

Run:
```bash
head -30 research-agent/agents/researcher.md
```
Expected: YAML frontmatter with name, description, tools, model, color fields.

Run:
```bash
grep -c "^## " research-agent/agents/researcher.md
```
Expected: 7 (one per major section: Initialization, The Research Loop, Decision-Making Autonomy, Logging Discipline, Termination Protocol, Context Compression Resilience, plus any sub-headers).

- [ ] **Step 10: Commit**

```bash
git add research-agent/agents/researcher.md
git commit -m "feat(research-agent): add monolithic researcher agent with full methodology"
```

---

### Task 6: Validation and Final Commit

**Files:**
- Verify: all files in `research-agent/`

- [ ] **Step 1: Validate plugin structure**

Run from the `research-agent/` directory:

```bash
# Skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -12 "$f" && echo; done
```
Expected: `name: research` and `description:` present.

```bash
# Command frontmatter has description
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done
```
Expected: `description:` present.

```bash
# Agent frontmatter has name, description, tools, model
for f in agents/*.md; do echo "=== $f ===" && head -30 "$f" && echo; done
```
Expected: all four fields present.

- [ ] **Step 2: Validate marketplace.json is valid JSON**

```bash
cat .claude-plugin/marketplace.json | python3 -m json.tool > /dev/null
```
Expected: no errors. (Run from the repo root `..`)

- [ ] **Step 3: Validate versions match**

Check that `research-agent/.claude-plugin/plugin.json` version matches the version in `../.claude-plugin/marketplace.json` for the research-agent entry. Both should be `0.1.0`.

```bash
python3 -c "
import json
with open('research-agent/.claude-plugin/plugin.json') as f:
    pv = json.load(f)['version']
with open('.claude-plugin/marketplace.json') as f:
    mv = [p for p in json.load(f)['plugins'] if p['name'] == 'research-agent'][0]['version']
assert pv == mv, f'Version mismatch: plugin.json={pv}, marketplace.json={mv}'
print(f'Versions match: {pv}')
"
```
Expected: `Versions match: 0.1.0`

- [ ] **Step 4: Verify no em-dashes in any plugin files**

```bash
grep -rP '\x{2014}' research-agent/ && echo "FAIL: em-dashes found" || echo "PASS: no em-dashes"
```
Expected: `PASS: no em-dashes`

- [ ] **Step 5: Final summary commit if any fixes were needed**

If any validation steps required fixes, commit them:
```bash
git add -A research-agent/
git commit -m "fix(research-agent): address validation issues"
```
