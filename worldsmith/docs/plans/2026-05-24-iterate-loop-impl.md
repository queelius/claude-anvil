# Autonomous Iterate Loop: Implementation Plan

> **For agentic workers:** Execute task-by-task. Each task is a single atomic commit. Steps use checkbox (`- [ ]`) syntax.

**Goal**: Ship `/worldsmith:iterate`, the autonomous review-fix-review loop. New iterator agent, new command, small rewriter extension for stake-classified judgments.

**Design doc**: `docs/plans/2026-05-24-iterate-loop-design.md`

---

## Chunk 1: Rewriter extension (stake field)

### Task 1: Add stake-classification to rewriter agent

The rewriter's Phase 2 (Triage) gains an optional `stake: low|medium|high` field on needs-judgment findings. The rewriter also documents an iterate-mode contract that other orchestrators (the iterator) can rely on.

**Files**:
- Modify: `agents/rewriter.md`

- [ ] **Step 1**: In Phase 2 (Triage), add a new subsection describing stake classification.

Insert after the "Needs judgment" bullet:

```markdown
### Stake classification (for needs-judgment findings)

Each needs-judgment finding gets an optional `stake` field with one of:

- **low**: Cosmetic or stylistic. "This sentence could be tighter, here are two phrasings." A best-guess pick is safe and reversible.
- **medium**: Style or structure that affects a single passage. "The transition into this scene could go three ways." A best-guess pick is defensible with documented rationale.
- **high**: Plot, character, or world stakes. "Should this character betray the protagonist?" "Does this scene change the antagonist's motivation?" A best-guess is dangerous; the author must decide.

When invoked directly via /worldsmith:revise, the stake field is metadata only. The existing AskUserQuestion-per-judgment flow is unchanged. When invoked by the iterator agent in iterate mode, stake drives best-guess versus defer decisions.
```

- [ ] **Step 2**: Add an "Iterate mode" section after Phase 2 documenting the contract.

```markdown
### Iterate mode (invocation by the iterator orchestrator)

When the iterator agent launches this agent, the launch prompt includes:

```xml
<mode>iterate</mode>
<pause-on>high|all|none</pause-on>
<output-dir>.worldsmith/iterate/<timestamp>/<work>/round-NNN/</output-dir>
```

In iterate mode:

- Do NOT use AskUserQuestion. The iterator runs autonomously and will batch all judgments at the end of the loop.
- For needs-judgment findings:
  - pause-on=high: best-guess on stake=low|medium with rationale, defer stake=high to deferred-judgments section
  - pause-on=all: defer all needs-judgment findings to deferred-judgments section
  - pause-on=none: best-guess all needs-judgment findings regardless of stake
- Write the revision report to the specified output-dir as revision.md (not the default .worldsmith/reviews/ path).
- Include a machine-readable deferred-judgments section in YAML:

```yaml
deferred-judgments:
  - finding-id: <unique-id>
    location: <file:line>
    severity: HIGH|MEDIUM|LOW
    stake: high
    original-finding: <text>
    suggested-options:
      - <option-1>
      - <option-2>
      - <option-3>
```

The iterator reads this section to build the end-of-loop user checkpoint.

When invoked directly (not from iterator), all of this is irrelevant: the rewriter's existing /worldsmith:revise flow takes over.
```

- [ ] **Step 3**: Commit.

```bash
git add agents/rewriter.md
git commit -m "feat(worldsmith): rewriter supports stake-classified judgments and iterate mode"
```

---

## Chunk 2: Iterator agent

### Task 2: Create agents/iterator.md

The new orchestrator. Mirrors reviewer.md and rewriter.md in shape but with loop-driving logic.

**Files**:
- Create: `agents/iterator.md`

- [ ] **Step 1**: Write the agent file.

Frontmatter:

```yaml
---
name: iterator
description: >-
  Autonomous review-fix-review loop orchestrator. Repeatedly invokes the
  reviewer and rewriter agents until convergence (no HIGH findings remain),
  a regression-plateau is detected, or the iteration cap is hit. Defers
  high-stake creative-judgment findings to a single end-of-loop user
  checkpoint, then runs one final revision pass with the user's answers.

  <example>
  Context: User wants to drive a manuscript from rough to clean autonomously.
  user: "Run the autonomous loop on Hemorrhagic"
  assistant: "I'll launch the iterator agent to run the review-fix-review loop."
  </example>
  <example>
  Context: User wants a thorough pass with strict convergence.
  user: "Iterate to zero MEDIUM findings, give it 12 rounds"
  assistant: "I'll launch the iterator agent with --threshold medium --max-iterations 12."
  </example>
tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
model: opus
color: green
---
```

Body sections (mirror reviewer.md and rewriter.md):

- Opening prose: role description
- Context Strategy (1M context note, pass full review reports to specialists)
- Available Agents (reviewer, rewriter) with launch protocol
- Workflow:
  - Phase 1: Comprehension (read CLAUDE.md, project.yaml, parse args, resolve work)
  - Phase 2: Initialize state (create session dir, write state.md with config)
  - Phase 3: Iteration loop (the core: launch reviewer, count findings, check convergence, launch rewriter in iterate mode, parse revision report, check plateau, repeat)
  - Phase 4: Deferred-judgment checkpoint (AskUserQuestion batching, with meta-question if > 12)
  - Phase 5: Final revision round (rewriter with user answers)
  - Phase 6: Summary report
- Ground Rules:
  - Never call the rewriter without iterate-mode flags (would cause it to AskUserQuestion mid-loop)
  - Always write round artifacts to the session dir, never default paths
  - Plateau detection takes priority over iteration cap (stop earlier if no progress)
  - Token cost is significant; the summary must include a best-effort estimate so the user can calibrate future runs

- [ ] **Step 2**: Verify frontmatter parses (head -10).

- [ ] **Step 3**: Commit.

```bash
git add agents/iterator.md
git commit -m "feat(worldsmith): add iterator orchestrator agent for autonomous review-fix loop"
```

---

## Chunk 3: Command wrapper

### Task 3: Create commands/iterate.md

Thin wrapper, same shape as `/worldsmith:draft` and `/worldsmith:revise`.

**Files**:
- Create: `commands/iterate.md`

- [ ] **Step 1**: Write the command file.

Frontmatter:

```yaml
---
description: Autonomous review-fix-review loop until convergence or iteration cap
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[work-name] [--max-iterations N] [--threshold high|medium|zero] [--pause-on high|all|none]"
---
```

Body sections:

- Brief description: composes /worldsmith:review and /worldsmith:revise in a loop, with a single end-of-loop user checkpoint for high-stake judgments
- Default behavior call-out: max 8 rounds, stop when zero HIGH findings, defer high-stake judgments to checkpoint
- Flag documentation
- Cost warning: significant token spend per run; recommended for finishing-pass work, not every-edit usage
- Multi-Work Awareness section (same shape as /worldsmith:draft and /worldsmith:revise)
- Forwards `$ARGUMENTS` (with work-name resolved) to the iterator agent via Task

- [ ] **Step 2**: Verify frontmatter parses.

- [ ] **Step 3**: Commit.

```bash
git add commands/iterate.md
git commit -m "feat(worldsmith): add /worldsmith:iterate command for autonomous loop"
```

---

## Chunk 4: Docs

### Task 4: Update help.md

**Files**:
- Modify: `commands/help.md`

- [ ] **Step 1**: Add `/worldsmith:iterate` row to Commands table.

After the `/worldsmith:revise` row:

```
| `/worldsmith:iterate [work] [flags]` | Autonomous review-fix loop until convergence (composes review and revise) |
```

- [ ] **Step 2**: Add `iterator` row to Agents table.

After the `rewriter` row:

```
| **iterator** | Autonomous review-fix-review loop with end-of-loop user checkpoint | `/worldsmith:iterate` |
```

- [ ] **Step 3**: Add a workflow section after "Revising after a review".

```markdown
**Running the autonomous loop (finishing pass):**
1. `/worldsmith:iterate` (defaults: 8 rounds, stop when zero HIGH findings, defer high-stake judgments)
2. The iterator runs reviewer + rewriter in a loop, writing per-round artifacts to `.worldsmith/iterate/<timestamp>/`
3. At the end, batches any deferred high-stake judgments into a single AskUserQuestion checkpoint
4. After you resolve, runs one final revise round with your answers
5. Reports total fixes, regressions, convergence status, and cost estimate
```

- [ ] **Step 4**: Commit.

```bash
git add commands/help.md
git commit -m "docs(worldsmith): document /worldsmith:iterate in help.md"
```

---

### Task 5: Update CLAUDE.md

**Files**:
- Modify: `CLAUDE.md`

- [ ] **Step 1**: Update Plugin Structure tree.

Commands count line: `commands/{init-world,change,check,review,draft,revise,iterate,help}.md  # 8 slash commands`

Agents section: add `agents/iterator.md  # Iterator orchestrator (autonomous review-fix loop)` after the rewriter line.

- [ ] **Step 2**: Update the "File Format Conventions > Agents" section to mention the iterator alongside reviewer/writer/rewriter as the fourth orchestrator.

In the Orchestrators bullet list, add after rewriter:

```markdown
- **iterator**: Autonomous review-fix-review loop. Composes reviewer and rewriter in a convergence-driven loop with end-of-loop batched user checkpoint for high-stake judgments. Writes per-round artifacts to `.worldsmith/iterate/<timestamp>/`.
```

- [ ] **Step 3**: Commit (combined with version bump in Task 6).

---

### Task 6: Bump version 0.10.0 -> 0.11.0

**Files**:
- Modify: `.claude-plugin/plugin.json`
- Modify: `../.claude-plugin/marketplace.json`
- Modify: `../CLAUDE.md`

- [ ] **Step 1**: Bump `.claude-plugin/plugin.json` 0.10.0 -> 0.11.0.
- [ ] **Step 2**: Bump worldsmith row in `../.claude-plugin/marketplace.json` 0.10.0 -> 0.11.0.
- [ ] **Step 3**: Bump worldsmith row in `../CLAUDE.md` 0.10.0 -> 0.11.0.

- [ ] **Step 4**: Commit combined with Task 5 CLAUDE.md update.

```bash
git add CLAUDE.md .claude-plugin/plugin.json ../.claude-plugin/marketplace.json ../CLAUDE.md
git commit -m "feat(worldsmith): bump to 0.11.0 for /worldsmith:iterate"
```

---

## Chunk 5: Plans and Validation

### Task 7: Commit the plans

Lands BEFORE Task 1 in actual execution order. Listed here because the plan files themselves are part of the deliverable.

- [ ] **Step 1**: Commit.

```bash
git add docs/plans/2026-05-24-iterate-loop-design.md docs/plans/2026-05-24-iterate-loop-impl.md
git commit -m "docs(worldsmith): add iterate loop design and impl plans"
```

---

### Task 8: Validation

- [ ] Skill frontmatter (unchanged)
- [ ] Command frontmatter (all 8 files)
- [ ] Agent frontmatter (all 11 files including new iterator)
- [ ] `${CLAUDE_PLUGIN_ROOT}` references resolve
- [ ] Hook scripts executable
- [ ] Test harness still passes (`./tests/test-cliche-scoping.sh`)
- [ ] No em-dashes in new prose (soul hook compliance)
- [ ] Version sync across all three locations

Run the full validation block from CLAUDE.md.

---

## Commit summary (expected, in execution order)

1. `docs(worldsmith): add iterate loop design and impl plans`
2. `feat(worldsmith): rewriter supports stake-classified judgments and iterate mode`
3. `feat(worldsmith): add iterator orchestrator agent for autonomous review-fix loop`
4. `feat(worldsmith): add /worldsmith:iterate command for autonomous loop`
5. `docs(worldsmith): document /worldsmith:iterate in help.md`
6. `feat(worldsmith): bump to 0.11.0 for /worldsmith:iterate`

Six commits, atomic per concern. The plans land first, then the work flows bottom-up: agent extension, new agent, new command, docs, version.

## Manual smoke test (post-merge, before release)

Iterator behavior is hard to unit-test. Verify in a real project:

1. In a project with known small issues, run `/worldsmith:iterate --max-iterations 3`.
2. Confirm session dir is created at `.worldsmith/iterate/<timestamp>/<work>/`.
3. Confirm per-round review.md and revision.md files appear.
4. If high-stake judgments are deferred, confirm the AskUserQuestion checkpoint fires at the end (not mid-loop).
5. Confirm summary.md has per-round counts and a convergence reason.
6. Time and token cost should match the design estimate (~5-15 min/round, ~80-150 specialist calls for 8 rounds).
