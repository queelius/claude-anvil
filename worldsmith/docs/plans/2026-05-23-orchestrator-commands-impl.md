# Orchestrator Commands: Implementation Plan

> **For agentic workers:** Execute task-by-task. Each task is a single atomic commit. Steps use checkbox (`- [ ]`) syntax.

**Goal**: Add `/worldsmith:draft` and `/worldsmith:revise` as thin wrappers around the writer and rewriter orchestrators, including help.md cleanup and version bump.

**Design doc**: `docs/plans/2026-05-23-orchestrator-commands-design.md`

---

## Chunk 1: New Commands

### Task 1: Add `/worldsmith:draft` command

Wrapper for the writer orchestrator. Mirrors the structure of `commands/review.md`.

**Files**:
- Create: `commands/draft.md`

- [ ] **Step 1**: Write the command file with frontmatter and body.

Frontmatter:

```yaml
---
description: Launch the writer orchestrator to draft scenes, chapters, lore, or character work
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[work-name] [assignment, e.g. 'chapter 5', 'Greymoor battle', 'develop the Ashwalker culture']"
---
```

Body sections (mirror review.md):
- Brief description of the writer's role (multi-agent drafting, lore/scene/character specialists in parallel)
- Forward `$ARGUMENTS` as the assignment via Task launch prompt
- Multi-Work Awareness section identical in shape to review.md
- Reference to `${CLAUDE_PLUGIN_ROOT}/skills/worldsmith-methodology/...` if needed
- Note: this is for new content. For revising existing prose against a review, use `/worldsmith:revise`.

- [ ] **Step 2**: Verify frontmatter parses (head -5).

- [ ] **Step 3**: Commit.

```bash
git add commands/draft.md
git commit -m "feat(worldsmith): add /worldsmith:draft command for writer orchestrator"
```

---

### Task 2: Add `/worldsmith:revise` command

Wrapper for the rewriter orchestrator. Slightly richer than draft: must discover the latest review report.

**Files**:
- Create: `commands/revise.md`

- [ ] **Step 1**: Write the command file with frontmatter and body.

Frontmatter:

```yaml
---
description: Launch the rewriter orchestrator to apply fixes from a review report
allowed-tools: Read, Glob, Grep, Bash, Task
argument-hint: "[work-name] [review-path | severity HIGH|MEDIUM|LOW | category consistency|craft|voice|structure]"
---
```

Body sections:
- Brief description of the rewriter's role (fix-then-verify, dispatches writer specialists for fixes and reviewer specialists for verification)
- Review report discovery logic (latest `.worldsmith/reviews/<date>/[work-name]/review.md`)
- Filter parsing: severity and category filters extracted from `$ARGUMENTS` and forwarded to the rewriter
- Multi-Work Awareness section
- Failure case: if no review report exists, instruct the user to run `/worldsmith:review` first

- [ ] **Step 2**: Verify frontmatter parses (head -5).

- [ ] **Step 3**: Commit.

```bash
git add commands/revise.md
git commit -m "feat(worldsmith): add /worldsmith:revise command for rewriter orchestrator"
```

---

## Chunk 2: Docs

### Task 3: Update help.md

Three changes:
1. Add `/worldsmith:draft` and `/worldsmith:revise` rows to the Commands table.
2. Fix the inaccurate "Launched by: `/worldsmith:check all` or direct" attribution for the reviewer (the check command runs diagnostics directly and cannot launch agents). Update writer and rewriter rows to point at the new commands.
3. Add a new "Drafting and revising" workflow section.

**Files**:
- Modify: `commands/help.md`

- [ ] **Step 1**: Update Commands table.

Add after the `/worldsmith:review` row:

```
| `/worldsmith:draft [work] [assignment]` | Launch the writer orchestrator: scenes, chapters, lore, or character work |
| `/worldsmith:revise [work] [filter]` | Launch the rewriter orchestrator: apply fixes from a review report |
```

- [ ] **Step 2**: Fix Agents table attributions.

Change:
```
| **reviewer** | ... | `/worldsmith:check all` or direct |
| **writer** | ... | Direct request |
| **rewriter** | ... | `/worldsmith:review` output or direct |
```

To:
```
| **reviewer** | ... | `/worldsmith:review` |
| **writer** | ... | `/worldsmith:draft` |
| **rewriter** | ... | `/worldsmith:revise` |
```

- [ ] **Step 3**: Add workflow section.

After "Adding or changing lore," insert:

```markdown
**Drafting new content:**
1. `/worldsmith:draft chapter 5` (or specify a scene, lore entry, or character work)
2. The writer orchestrator routes to lore/scene/character specialists in parallel
3. Output lands in the manuscript directory and canonical docs are updated

**Revising after a review:**
1. `/worldsmith:review` produces a review report in `.worldsmith/reviews/`
2. `/worldsmith:revise` reads the latest report, fixes findings, verifies each fix
3. Optionally filter: `/worldsmith:revise HIGH` or `/worldsmith:revise consistency`
```

- [ ] **Step 4**: Commit.

```bash
git add commands/help.md
git commit -m "feat(worldsmith): update help.md for /worldsmith:draft and /worldsmith:revise"
```

---

### Task 4: Update worldsmith CLAUDE.md

Update the Plugin Structure tree to reflect 7 slash commands instead of 5.

**Files**:
- Modify: `CLAUDE.md`

- [ ] **Step 1**: Change the commands line in the Plugin Structure tree.

From:
```
commands/{init-world,change,check,review,help}.md  # 5 slash commands
```

To:
```
commands/{init-world,change,check,review,draft,revise,help}.md  # 7 slash commands
```

- [ ] **Step 2**: Commit (will be combined with version bump in Task 5).

---

### Task 5: Bump version and update marketplace

Per parent CLAUDE.md: marketplace.json, plugin.json, and the parent CLAUDE.md table must all be updated together.

**Files**:
- Modify: `.claude-plugin/plugin.json`
- Modify: `../.claude-plugin/marketplace.json`
- Modify: `../CLAUDE.md`

- [ ] **Step 1**: Bump `.claude-plugin/plugin.json` from `0.8.0` to `0.9.0`.

- [ ] **Step 2**: Bump worldsmith entry in `../.claude-plugin/marketplace.json` from `0.8.0` to `0.9.0`.

- [ ] **Step 3**: Bump worldsmith row in `../CLAUDE.md` plugin table from `0.8.0` to `0.9.0`.

- [ ] **Step 4**: Commit (combined with Task 4 CLAUDE.md update).

```bash
git add CLAUDE.md .claude-plugin/plugin.json ../.claude-plugin/marketplace.json ../CLAUDE.md
git commit -m "feat(worldsmith): bump to 0.9.0 for orchestrator commands"
```

---

## Chunk 3: Validation

### Task 6: Run validation block

**Commands** (from worldsmith CLAUDE.md):

- [ ] Skill frontmatter
- [ ] Command frontmatter (all 7 files)
- [ ] Agent frontmatter (unchanged)
- [ ] `${CLAUDE_PLUGIN_ROOT}` references resolve
- [ ] Hook scripts executable

- [ ] **Step 1**: Run the full validation block from `CLAUDE.md`.

- [ ] **Step 2**: Push.

```bash
git push
```

---

## Commit summary (expected)

1. `docs(worldsmith): add orchestrator commands design plan`
2. `docs(worldsmith): add orchestrator commands impl plan`
3. `feat(worldsmith): add /worldsmith:draft command for writer orchestrator`
4. `feat(worldsmith): add /worldsmith:revise command for rewriter orchestrator`
5. `feat(worldsmith): update help.md for /worldsmith:draft and /worldsmith:revise`
6. `feat(worldsmith): bump to 0.9.0 for orchestrator commands`

Six small commits, in line with the per-step pattern of previous impl plans.
