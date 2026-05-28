# bookwright v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build v0.1 of the `bookwright` Claude Code plugin: a multi-agent toolchain for technical non-fiction long-form manuscripts, encoding the Bernoulli-textbook workflow.

**Architecture:** Plugin lives at `~/github/alex-claude-plugins/bookwright/` inside the `claude-anvil` monorepo. Standard plugin layout: `.claude-plugin/plugin.json`, `commands/`, `agents/`, `skills/`, `hooks/`. Two orchestrator agents (`writer`, `reviewer`) plus 7 specialist agents (3 drafting + 4 review). 9 commands. 3 progressive-disclosure skills. 2 hooks: the soul-voice hook is a declared dependency on the separately-installed `soul` plugin; the LaTeX-macro-leak hook is new in this plugin. Implementation uses `plugin-dev:create-plugin`, `plugin-dev:agent-creator`, `plugin-dev:skill-reviewer`, and `plugin-dev:plugin-validator` per Anthropic's current plugin-development guidance.

**Tech Stack:** Markdown for plugin component files (skills, agents, commands), JSON for `plugin.json` and `hooks.json`, Bash for the macro-leak hook script, BATS or plain bash for smoke tests.

**Spec source of truth:** `~/github/alex-claude-plugins/bookwright/docs/superpowers/specs/2026-05-28-bookwright-design.md`.

**Inspiration project (reference for prose patterns and notebook conventions):** `~/github/bernoulli/` (18 drafted chapters, 15 executed notebooks, ~30 plan files; the workflow this plugin encodes).

**Sibling plugin (reference for plugin layout):** `~/github/alex-claude-plugins/worldsmith/`.

---

## File Structure

After this plan completes, the bookwright plugin has:

```
bookwright/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── LICENSE                                 # MIT
├── CLAUDE.md                               # plugin-internal guidance
├── commands/
│   ├── init.md
│   ├── design.md
│   ├── plan.md
│   ├── draft.md
│   ├── notebook.md
│   ├── check.md
│   ├── review.md
│   ├── integrate.md
│   └── help.md
├── agents/
│   ├── writer.md                           # orchestrator
│   ├── reviewer.md                         # orchestrator
│   ├── section-writer.md                   # drafting specialist
│   ├── notebook-author.md                  # drafting specialist
│   ├── source-reformulator.md              # drafting specialist
│   ├── spec-auditor.md                     # review specialist
│   ├── quality-auditor.md                  # review specialist
│   ├── math-auditor.md                     # review specialist
│   └── cross-ref-auditor.md                # review specialist
├── skills/
│   ├── textbook-methodology/
│   │   └── SKILL.md
│   ├── cross-reference-discipline/
│   │   └── SKILL.md
│   └── notebook-paired-with-prose/
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   └── scripts/
│       └── check-latex-macro-leak.sh
├── docs/
│   └── superpowers/
│       ├── specs/
│       │   └── 2026-05-28-bookwright-design.md     # (already exists)
│       └── plans/
│           └── 2026-05-29-bookwright-v0.1-implementation.md  # (this file)
└── tests/
    ├── test-init.sh
    ├── test-check.sh
    └── test-macro-leak-hook.sh
```

---

## Working Directory

All file paths in this plan are absolute. The working git repo for commits is `~/github/alex-claude-plugins/` (the `claude-anvil` monorepo); the plugin lives at `~/github/alex-claude-plugins/bookwright/`. Each commit's message subject should be prefixed with `bookwright:` to match the monorepo's per-plugin convention.

---

## Pre-flight: Inspect worldsmith as a template

Before any task, read these worldsmith files as reference for file format conventions:

- `~/github/alex-claude-plugins/worldsmith/.claude-plugin/plugin.json` (manifest shape)
- `~/github/alex-claude-plugins/worldsmith/commands/draft.md` (command frontmatter pattern: `description`, `allowed-tools`, `argument-hint`)
- `~/github/alex-claude-plugins/worldsmith/agents/writer.md` (agent frontmatter pattern: `name`, `description` with `<example>` blocks)
- `~/github/alex-claude-plugins/worldsmith/skills/worldsmith-methodology/SKILL.md` (skill frontmatter pattern: `name`, `description`, body)
- `~/github/alex-claude-plugins/worldsmith/hooks/hooks.json` (hook declaration shape)
- `~/github/alex-claude-plugins/worldsmith/README.md` (README structure)

Implementers do NOT need to read worldsmith's full agent prompts; only file format and YAML frontmatter conventions. The agent CONTENT for bookwright is specified per-task in this plan.

---

## Tasks

### Phase A: Plugin Scaffold

### Task 1: Create `plugin.json` manifest

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/.claude-plugin/plugin.json`

- [ ] **Step 1: Create the `.claude-plugin/` directory**

```bash
mkdir -p ~/github/alex-claude-plugins/bookwright/.claude-plugin
```

- [ ] **Step 2: Write `plugin.json`**

```json
{
  "name": "bookwright",
  "version": "0.1.0",
  "description": "Documentation-first methodology and multi-agent toolchain for technical non-fiction long-form manuscripts. The Bernoulli-textbook approach: design spec and chapter plans drive the manuscript.",
  "author": {
    "name": "Alexander Towell"
  },
  "repository": "https://github.com/queelius/claude-anvil",
  "license": "MIT",
  "keywords": [
    "non-fiction",
    "textbook",
    "monograph",
    "writing",
    "editorial",
    "multi-agent",
    "latex",
    "jupyter"
  ]
}
```

- [ ] **Step 3: Verify JSON is valid**

```bash
python3 -m json.tool ~/github/alex-claude-plugins/bookwright/.claude-plugin/plugin.json
```

Expected: pretty-printed JSON, exit code 0.

- [ ] **Step 4: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/.claude-plugin/plugin.json && git commit -m "$(cat <<'EOF'
bookwright: initial plugin.json manifest

Plugin name "bookwright", version 0.1.0. Description names the
scope (technical non-fiction long-form) and the methodology
(documentation-first, design-spec-drives-manuscript). Keywords for
plugin-marketplace discovery.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Create README, LICENSE, CLAUDE.md

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/README.md`
- Create: `~/github/alex-claude-plugins/bookwright/LICENSE`
- Create: `~/github/alex-claude-plugins/bookwright/CLAUDE.md`

- [ ] **Step 1: Read worldsmith's README and LICENSE for shape**

```bash
head -80 ~/github/alex-claude-plugins/worldsmith/README.md
cat ~/github/alex-claude-plugins/worldsmith/LICENSE
```

- [ ] **Step 2: Write `LICENSE` (MIT)**

Copy `~/github/alex-claude-plugins/worldsmith/LICENSE` verbatim to `~/github/alex-claude-plugins/bookwright/LICENSE` and adjust the copyright year if needed (current copyright line should read "Copyright (c) 2026 Alexander Towell" or similar; match worldsmith's exact format).

```bash
cp ~/github/alex-claude-plugins/worldsmith/LICENSE ~/github/alex-claude-plugins/bookwright/LICENSE
```

- [ ] **Step 3: Write `README.md`**

```markdown
# bookwright

A Claude Code plugin for documentation-first technical-textbook writing. The Bernoulli-textbook approach: **the design spec and per-chapter plans drive the manuscript**, with multi-agent drafting, math-correctness auditing, cross-reference integrity, and per-Part integration checks.

Sibling to `worldsmith` (fiction) and `papermill` (academic papers); bookwright owns the long-form non-fiction technical book.

## Philosophy

- **Specs first, manuscript second.** Master design spec, per-Part design specs, per-chapter implementation plans, per-section drafts. Update the spec when a structural decision changes, then propagate to the prose.
- **Path A discipline per section.** Implementer subagent, then spec-compliance review, then quality review, then fix loop. Per-task subagent dispatch protects main context and catches issues at the section grain.
- **Notebooks are empirical verifiers.** A chapter with a paired notebook must execute end-to-end with numerical-sanity targets that match prose claims. Broken notebook means broken chapter.
- **Running threads tracked explicitly.** The design spec names threads (e.g., the BSC, the Bloom filter); each chapter carries its share; integration checks verify the inventory.
- **Cross-reference integrity is mechanical.** Every section file has a header comment block documenting label resolution. The cross-ref auditor verifies the inventory.

## Installation

```bash
# Via the marketplace
/plugin marketplace add queelius/claude-anvil
/plugin install bookwright@queelius

# Or local install
claude plugin add ~/github/alex-claude-plugins/bookwright
```

**Required co-installation:** the `soul` plugin from the same marketplace, for the soul-voice hook (banned-phrase enforcement). bookwright declares this as a dependency; the macro-leak hook ships with bookwright itself.

## What's Included

### Commands (9)

| Command | Purpose |
|---------|---------|
| `/bookwright:init [book-name]` | Scaffold a fresh book project (LaTeX + notebooks + spec/plan dirs) |
| `/bookwright:design [part]` | Write master or per-Part design spec via Socratic dialogue |
| `/bookwright:plan [chapter]` | Write per-chapter implementation plan from the relevant design spec |
| `/bookwright:draft [chapter\|section]` | Launch the writer orchestrator for prose drafting |
| `/bookwright:notebook [chapter]` | Draft and execute the paired notebook for a chapter |
| `/bookwright:check [scope]` | Fast mechanical diagnostics (build, labels, page counts, threads, soul-voice) |
| `/bookwright:review [scope]` | Heavy multi-agent editorial review (4 specialists in parallel) |
| `/bookwright:integrate [scope]` | Per-Part or full-book integration check plus integration-pass record |
| `/bookwright:help` | Quick reference for commands, agents, and skills |

### Agents (9 in v0.1)

**Orchestrators (2):** `writer`, `reviewer`. v0.2 adds `rewriter` and `iterator`.

**Drafting specialists (3):** `section-writer`, `notebook-author`, `source-reformulator`.

**Review specialists (4):** `spec-auditor`, `quality-auditor`, `math-auditor`, `cross-ref-auditor`.

The `math-auditor` deserves a callout: in the Bernoulli textbook session, it would have caught arithmetic errors in chapter 5 §5.2, chapter 5 §5.4, chapter 6 §6.1, and chapter 10 §10.4 that escaped generic quality review. Worth a separate auditor.

### Skills (3, auto-triggered)

| Skill | Triggers when... |
|-------|------------------|
| `bookwright:textbook-methodology` | Drafting prose for a bookwright project |
| `bookwright:cross-reference-discipline` | Writing cross-referenced sections |
| `bookwright:notebook-paired-with-prose` | Drafting or executing a paired notebook |

### Hooks (2)

| Hook | Source |
|------|--------|
| Soul-voice (banned-phrase enforcement) | `soul` plugin dependency |
| LaTeX-macro-leak | Ships with bookwright |

## What "bookwright" Is Not For

- Fiction (use `worldsmith`).
- Single-paper academic submissions (use `papermill`).
- Memoir, popular trade, journalism (different prose conventions; not in scope).
- Multi-author collaboration workflows (not in v0.1).
- ISBN registration and KDP submission (use the `kdp` plugin).

## License

MIT.
```

- [ ] **Step 4: Write `CLAUDE.md` (plugin-internal guidance)**

```markdown
# CLAUDE.md (bookwright plugin)

This file is internal to the bookwright plugin. It is consumed by Claude Code when working ON the plugin (developing it), not when the plugin is invoked by an end user.

## Repository context

bookwright is one plugin in the `~/github/alex-claude-plugins/` (`claude-anvil`) monorepo. Sibling plugins include `worldsmith` (fiction), `papermill` (academic papers), `soul` (banned-phrase hooks).

## Development conventions

- Plugin component files (commands, agents, skills) are Markdown with YAML frontmatter.
- All command names use the `/bookwright:NAME` prefix in user-facing docs.
- Commit messages use `bookwright:` subject prefix.
- The plugin's design spec is at `docs/superpowers/specs/2026-05-28-bookwright-design.md`.
- v0.1 ships 9 agents (defers `rewriter` and `iterator` to v0.2).

## Testing

`tests/` contains shell smoke tests. To run all:

```bash
cd ~/github/alex-claude-plugins/bookwright/tests && bash test-init.sh && bash test-check.sh && bash test-macro-leak-hook.sh
```

## Validation

Before releasing, run `plugin-dev:plugin-validator` against this plugin.
```

- [ ] **Step 5: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/README.md bookwright/LICENSE bookwright/CLAUDE.md && git commit -m "$(cat <<'EOF'
bookwright: README, LICENSE (MIT), and plugin-internal CLAUDE.md

README sketches philosophy, command surface, agents, skills, hooks.
LICENSE is MIT (copy from worldsmith). CLAUDE.md is plugin-internal
development guidance (not user-facing).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Scaffold empty directories for commands, agents, skills, hooks, tests

**Files:**
- Create directories under `~/github/alex-claude-plugins/bookwright/`.

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p ~/github/alex-claude-plugins/bookwright/commands
mkdir -p ~/github/alex-claude-plugins/bookwright/agents
mkdir -p ~/github/alex-claude-plugins/bookwright/skills/textbook-methodology
mkdir -p ~/github/alex-claude-plugins/bookwright/skills/cross-reference-discipline
mkdir -p ~/github/alex-claude-plugins/bookwright/skills/notebook-paired-with-prose
mkdir -p ~/github/alex-claude-plugins/bookwright/hooks/scripts
mkdir -p ~/github/alex-claude-plugins/bookwright/tests
```

- [ ] **Step 2: Verify directory tree**

```bash
find ~/github/alex-claude-plugins/bookwright -type d | sort
```

Expected output includes all directories listed above.

- [ ] **Step 3: No commit** (git does not track empty directories; subsequent tasks add files that get committed).

---

### Phase B: Hooks

### Task 4: Write the LaTeX-macro-leak hook script

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/hooks/scripts/check-latex-macro-leak.sh`

**Purpose:** PostToolUse hook on Write/Edit for `.tex` files. Blocks if non-comment lines contain LaTeX-source-detail patterns that would leak into reader-facing prose. The Bernoulli session's post-Plan-17 fix surfaced these patterns; this hook prevents them from re-appearing.

- [ ] **Step 1: Write the script**

```bash
#!/usr/bin/env bash
# check-latex-macro-leak.sh
#
# PostToolUse hook for Write/Edit on .tex files.
# Blocks if reader-visible prose contains references to LaTeX source-tool
# detail: macro names in \texttt{}, mentions of style packages, "rendered
# as" / "the macro" patterns.
#
# Reads the new file content from stdin (the hook protocol provides it),
# inspects it, exits 0 if clean, exits 1 with an explanation if it finds
# a leak.

set -euo pipefail

INPUT=$(cat)

# Extract the file path the hook is operating on.
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    print(d.get('tool_input', {}).get('file_path', ''), end='')
except Exception:
    pass
")

# Skip non-tex files.
case "$FILE_PATH" in
    *.tex) ;;
    *) exit 0 ;;
esac

# Extract the new file content. For Write, that's tool_input.content.
# For Edit, that's tool_input.new_string (the post-edit fragment).
CONTENT=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
ti = d.get('tool_input', {})
print(ti.get('content', ti.get('new_string', '')), end='')
")

# Build a temp file holding only non-comment lines.
TMP=$(mktemp)
trap 'rm -f $TMP' EXIT
printf '%s\n' "$CONTENT" | sed 's/^%.*//' > "$TMP"

# Pattern checks. Each pattern, if matched, is a leak.
LEAKS=()

if grep -qE '\\texttt\{\\textbackslash[ ]?[a-zA-Z]' "$TMP"; then
    LEAKS+=("macro-name in \\texttt{\\textbackslash ...}: '\\texttt{\\textbackslash foo}' style reveals LaTeX macros to the reader")
fi

if grep -qiE '(\bthe macro\b|\brendered as\b)' "$TMP"; then
    LEAKS+=("'the macro' or 'rendered as' phrases reveal LaTeX implementation detail")
fi

if grep -qE '\balex\.sty\b|\btexttt\{alex\.sty\}' "$TMP"; then
    LEAKS+=("reference to 'alex.sty' (or any style package) belongs in source comments only, not reader prose")
fi

if [[ ${#LEAKS[@]} -gt 0 ]]; then
    echo "{\"systemMessage\": \"LaTeX-macro-leak hook blocked the write to ${FILE_PATH}. Reader-facing prose must not reveal LaTeX source-tool detail. Found:\\n$(printf -- '- %s\\n' "${LEAKS[@]}")\"}"
    exit 2
fi

exit 0
```

- [ ] **Step 2: Make the script executable**

```bash
chmod +x ~/github/alex-claude-plugins/bookwright/hooks/scripts/check-latex-macro-leak.sh
```

- [ ] **Step 3: Smoke-test the script (positive case: clean .tex passes)**

```bash
CLEAN_INPUT='{"tool_input": {"file_path": "foo.tex", "content": "Standard prose with $\\fprate$ and $\\fnrate$ in math mode. The Bloom filter has FPR \\fprate."}}'
echo "$CLEAN_INPUT" | bash ~/github/alex-claude-plugins/bookwright/hooks/scripts/check-latex-macro-leak.sh
echo "Exit: $?"
```

Expected: exit 0 (no output).

- [ ] **Step 4: Smoke-test the script (negative case: macro leak blocks)**

```bash
LEAK_INPUT='{"tool_input": {"file_path": "foo.tex", "content": "The macro \\texttt{\\textbackslash fprate} renders as $\\fprate$."}}'
echo "$LEAK_INPUT" | bash ~/github/alex-claude-plugins/bookwright/hooks/scripts/check-latex-macro-leak.sh
echo "Exit: $?"
```

Expected: exit 2 with a JSON `systemMessage` describing the leak.

- [ ] **Step 5: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/hooks/scripts/check-latex-macro-leak.sh && git commit -m "$(cat <<'EOF'
bookwright: LaTeX-macro-leak PostToolUse hook script

PostToolUse hook for Write/Edit on .tex files. Blocks reader-facing
prose patterns that leak LaTeX source-tool detail: \texttt{\textbackslash...}
macro names, "the macro" or "rendered as" phrasing, alex.sty mentions.
Reads JSON from stdin (the hook protocol), inspects post-edit content,
exits 2 with a systemMessage on leak.

The Bernoulli session's post-Plan-17 fix scrubbed three chapters
where these patterns escaped per-chapter review; this hook prevents
them from re-appearing in any project that installs bookwright.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Write `hooks/hooks.json` declaring the macro-leak hook

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/hooks/hooks.json`

- [ ] **Step 1: Read worldsmith's hooks.json as format reference**

```bash
cat ~/github/alex-claude-plugins/worldsmith/hooks/hooks.json
```

- [ ] **Step 2: Write `hooks.json`**

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": {
          "tool_name": "Write|Edit"
        },
        "hooks": [
          {
            "type": "command",
            "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/scripts/check-latex-macro-leak.sh"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Verify JSON validity**

```bash
python3 -m json.tool ~/github/alex-claude-plugins/bookwright/hooks/hooks.json
```

Expected: pretty-printed JSON, exit 0.

- [ ] **Step 4: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/hooks/hooks.json && git commit -m "$(cat <<'EOF'
bookwright: hooks.json declares the LaTeX-macro-leak PostToolUse hook

Matches Write and Edit tool invocations; runs the macro-leak script
on each. The script self-filters to .tex files internally, so the
matcher is broad (any Write/Edit) rather than per-file-extension.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Phase C: Commands (9 tasks)

Each command is one `.md` file with YAML frontmatter + body. The body should be a 10-30 line description of what the command does and how it dispatches subagents or runs verifications. Detailed prose is optional; clarity and accuracy matter more than length.

For all 9 commands, the YAML frontmatter follows this pattern (adapt the `description`, `allowed-tools`, `argument-hint` per command):

```yaml
---
description: <one-line summary used in /help and the marketplace>
allowed-tools: <comma-separated list>
argument-hint: "<bracketed example>"
---
```

### Task 6: Write `commands/init.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/init.md`

- [ ] **Step 1: Write the command file**

```markdown
---
description: Scaffold a fresh non-fiction book project (LaTeX + pluggable notebook + spec/plan directories)
allowed-tools: Read, Write, Bash, Glob, AskUserQuestion
argument-hint: "[book-name]"
---

# /bookwright:init

Scaffold a fresh book project at the current working directory (or a named subdirectory). Asks the user for a notebook stack choice and persists the choice to `docs/superpowers/bookwright.config.yaml`.

## What it creates

- `book/` with `chapters/`, `frontmatter/`, `appendices/`, `parts/`, `alex.sty` (or empty placeholder for project's own notation), `preamble.tex`, `references.bib`, `book.tex`, `Makefile`.
- `notebooks/` (Jupyter) OR `rmd/` (R Markdown) OR `qmd/` (Quarto) per user choice.
- `papers/` (empty; user can git-subtree-add source papers later).
- `docs/superpowers/specs/` and `docs/superpowers/plans/`.
- `docs/superpowers/bookwright.config.yaml` recording the notebook stack choice and other project settings.

## Steps

1. Ask the user (via AskUserQuestion) which notebook stack: Python+uv+Jupyter / R+renv+RMarkdown / Quarto / none.
2. Create the directory tree.
3. Write a minimal `book.tex` that includes empty `parts/part1.tex` and references it.
4. Write a minimal `Makefile` with the standard cleanall + biber + pdflatex pipeline.
5. Write the `bookwright.config.yaml` recording user choices.
6. Write a README in the new project root summarizing the layout.
7. Initialize git if not already initialized; commit the scaffold.
8. Report success and suggest next steps: `/bookwright:design master` (or `/bookwright:design part1`).

## Dependencies

- The `soul` plugin should be installed in the user's Claude environment for the soul-voice hook to fire on .tex writes in the new project. `init` should remind the user of this if not already done.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/init.md && git commit -m "bookwright: /bookwright:init command scaffolds a fresh book project"
```

---

### Task 7: Write `commands/design.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/design.md`

- [ ] **Step 1: Write the file**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/design.md && git commit -m "bookwright: /bookwright:design command writes master or per-Part design specs"
```

---

### Task 8: Write `commands/plan.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/plan.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Write a per-chapter implementation plan from the relevant design spec
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
argument-hint: "<chapter-name-or-number>"
---

# /bookwright:plan

Produce a per-chapter implementation plan from the relevant design spec. The plan is the basis for `/bookwright:draft`.

## What it produces

A plan markdown file at `docs/superpowers/plans/YYYY-MM-DD-<chapter-name>.md` with:

- Goal, architecture summary, tech stack, scope, base SHA.
- Source-material list (which papers/sections to reformulate).
- Lessons inherited from prior plans (page-budget discipline, banned-phrase reminders, cross-ref discipline).
- File structure: which chapter and section subfiles get created.
- Cross-reference map: which labels this chapter defines and which it references.
- Per-task list (typically 8-10 tasks: scaffold + per-section + bib notes + exercises + notebook + integration).
- Each task with content checklist, page-budget target, header-comment-block requirement, commit message.

## Steps

1. Read the master spec and the relevant per-Part spec.
2. Read the chapter's stub file in `book/chapters/` if it exists.
3. Walk the per-section spec items from the per-Part spec; turn each into a Task with its content checklist.
4. Add scaffold Task 1, bib-notes Task N-1, exercises Task N, and (if applicable) notebook Task N+1.
5. Save the plan to the plans directory.
6. Report it back; suggest next step: `/bookwright:draft <chapter>` to execute the plan.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/plan.md && git commit -m "bookwright: /bookwright:plan command writes per-chapter implementation plans"
```

---

### Task 9: Write `commands/draft.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/draft.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Launch the writer orchestrator for prose drafting (whole chapter or single section)
allowed-tools: Read, Glob, Grep, Task
argument-hint: "<chapter-name | section-path>"
---

# /bookwright:draft

Launch the `writer` orchestrator agent to draft prose. Argument can be a whole chapter (the writer iterates through its per-section tasks) or a single section path (one task end-to-end).

## What the writer does (briefly)

For each section task in the relevant plan:

1. Reads the plan's content checklist and content-source list.
2. Dispatches the appropriate drafting specialist:
   - `section-writer` for narrative prose.
   - `notebook-author` if the task includes a paired notebook.
   - `source-reformulator` if the task requires reformulating an external paper.
3. After the draft commits, dispatches `spec-auditor` and `quality-auditor` in parallel for review.
4. If either auditor surfaces substantive findings, dispatches a fix subagent and re-runs the relevant auditor to verify.
5. Reports the task's commit SHAs and word counts back to the user.

## When to use what

- `/bookwright:draft chapter5` runs ALL section tasks of chapter 5 in sequence (scaffold first, then sections, then bib + exercises, then notebook).
- `/bookwright:draft ch05/bloom-from-scratch.tex` runs only that one section task.

For per-Part or full-book integration verification, use `/bookwright:integrate` instead. For editorial review of an existing chapter (no drafting), use `/bookwright:review`.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/draft.md && git commit -m "bookwright: /bookwright:draft command launches the writer orchestrator"
```

---

### Task 10: Write `commands/notebook.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/notebook.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Draft and execute the paired notebook for a chapter (separable from prose drafting)
allowed-tools: Read, Write, Bash, Glob, Task
argument-hint: "<chapter-name-or-number>"
---

# /bookwright:notebook

Dispatch the `notebook-author` agent to draft (or refresh) the paired notebook for a chapter. Separate command from `/bookwright:draft` so notebooks can be updated without re-drafting prose.

## What it does

1. Reads the chapter's plan file to find the notebook content checklist and numerical-sanity targets.
2. Reads `docs/superpowers/bookwright.config.yaml` to determine notebook stack (Python+uv / R+renv / Quarto).
3. Dispatches the `notebook-author` agent to draft or update the notebook.
4. The agent executes the notebook end-to-end and reports execution exit code + observed numerical values.
5. If execution fails or observed values miss the sanity targets, surfaces the discrepancy for the user to review.

## Stack-specific execution commands

- Python+uv+Jupyter: `cd <project-dir>/notebooks && uv run jupyter nbconvert --to notebook --execute <name>.ipynb --output <name>.ipynb`
- R+renv+RMarkdown: `cd <project-dir>/rmd && Rscript -e 'rmarkdown::render("<name>.Rmd")'`
- Quarto: `cd <project-dir>/qmd && quarto render <name>.qmd`
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/notebook.md && git commit -m "bookwright: /bookwright:notebook command drafts and executes paired notebooks"
```

---

### Task 11: Write `commands/check.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/check.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Fast mechanical diagnostics on a section, chapter, part, or full book
allowed-tools: Read, Bash, Glob, Grep
argument-hint: "[section | chapter | part | book] [name]"
---

# /bookwright:check

Run mechanical diagnostics. No editorial judgment; checks that can be automated.

## What it runs

1. Build the book: `cd book && make cleanall && make`. Expects exit 0.
2. Cross-reference resolution: grep `book.log` for `Reference undefined` and `Citation undefined`. Expects only the documented baseline.
3. Per-chapter page-count audit: read `book.toc`, compute per-chapter page spans, compare to the per-chapter targets in the plan files. Expects each chapter within plus-or-minus 30 percent of its target.
4. Running-thread inventory: for each thread named in the master spec, grep chapter files for thread keywords; verify the thread carries across the chapters the spec assigned it to.
5. Soul-voice audit: re-run the soul-voice hook's pattern checks across all chapter .tex files (the hook runs at edit time, but `/check` re-runs as a defense-in-depth audit).
6. LaTeX-macro-leak audit: re-run the macro-leak hook's pattern checks.

## Scope

- `section <path>`: only the named section file.
- `chapter <name>`: all section files in `book/chapters/<chapter>/`.
- `part <name>`: all chapters in the named Part.
- `book`: everything (default if no scope given).

## Output

A short bullet report: each check's PASS/FAIL/NOTE. On FAIL, surface the specific lines or refs. No fix attempted; this is read-only diagnostics.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/check.md && git commit -m "bookwright: /bookwright:check command runs mechanical diagnostics"
```

---

### Task 12: Write `commands/review.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/review.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Heavy multi-agent editorial review (4 specialist auditors in parallel)
allowed-tools: Read, Glob, Grep, Task
argument-hint: "[section | chapter | part | book] [name]"
---

# /bookwright:review

Launch the `reviewer` orchestrator. Dispatches all four review specialists in parallel: `spec-auditor`, `quality-auditor`, `math-auditor`, `cross-ref-auditor`. Synthesizes the findings into a unified report.

## Scope

- `section <path>`: one section. Single-pass review by all four auditors.
- `chapter <name>`: all sections of the named chapter.
- `part <name>`: all chapters of the named Part.
- `book`: everything (heavy; do not use casually).

## Output

A unified review report saved to `docs/superpowers/reviews/YYYY-MM-DD-<scope>.md`, with sections from each auditor: spec compliance, quality (cold-read), math correctness, cross-references. The user can then run `/bookwright:integrate` to apply fixes if any auditor surfaced substantive findings.

## Distinction from /bookwright:check and /bookwright:integrate

- `/bookwright:check` is fast, mechanical, no judgment.
- `/bookwright:review` is heavy, editorial, full multi-agent dispatch.
- `/bookwright:integrate` is per-Part or full-book verification with a written integration-pass record.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/review.md && git commit -m "bookwright: /bookwright:review command launches multi-agent editorial review"
```

---

### Task 13: Write `commands/integrate.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/integrate.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Per-Part or full-book integration check with a written integration-pass record
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: "[part | book] [name]"
---

# /bookwright:integrate

Run the integration check that mirrors the Bernoulli textbook's Plan 4/8/13/15/18 Task 10 pattern.

## What it does

1. Run `/bookwright:check book` (or the appropriate scope) and capture results.
2. Verify the cross-reference map: chapter labels defined exactly once, expected forward refs match the baseline, no unexpected unresolved refs.
3. Compute per-Part page totals against spec targets.
4. Run a running-thread inventory across the chapters in scope.
5. Run the soul-voice and macro-leak audits.
6. Write an integration-pass record to `docs/superpowers/plans/YYYY-MM-DD-<scope>-integration-pass.md` with:
   - Date, plan reference, HEAD SHA at integration time.
   - Verification results table.
   - Known deferred items (documented forward refs that resolve in later work).
   - Open follow-ups for the polish plan.
7. Commit the record.

## When to run it

- After completing the last chapter of a Part.
- After completing the full book draft (full-book scope).
- Before publishing to verify the deferred-items list is empty or appropriately documented.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/integrate.md && git commit -m "bookwright: /bookwright:integrate command runs per-Part or full-book integration check"
```

---

### Task 14: Write `commands/help.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/commands/help.md`

- [ ] **Step 1: Write the file**

```markdown
---
description: Quick reference for bookwright commands, agents, and skills
allowed-tools: Read
argument-hint: ""
---

# /bookwright:help

Print a quick reference.

## Commands

- `/bookwright:init [name]`: scaffold a fresh book project.
- `/bookwright:design [master | partN]`: write a design spec via Socratic dialogue.
- `/bookwright:plan <chapter>`: write a per-chapter implementation plan from the spec.
- `/bookwright:draft <chapter | section>`: launch the writer orchestrator.
- `/bookwright:notebook <chapter>`: draft and execute the paired notebook.
- `/bookwright:check [scope]`: mechanical diagnostics (build, labels, page audit, threads, hooks).
- `/bookwright:review [scope]`: heavy multi-agent editorial review.
- `/bookwright:integrate [scope]`: per-Part or full-book integration check plus written record.
- `/bookwright:help`: this reference.

## Agents (v0.1)

Orchestrators: `writer`, `reviewer`. Drafting specialists: `section-writer`, `notebook-author`, `source-reformulator`. Review specialists: `spec-auditor`, `quality-auditor`, `math-auditor`, `cross-ref-auditor`.

## Skills (auto-triggered)

- `bookwright:textbook-methodology`: prose-drafting tasks.
- `bookwright:cross-reference-discipline`: cross-referenced sections.
- `bookwright:notebook-paired-with-prose`: notebook tasks.

## Hooks

- Soul-voice (banned-phrase enforcement): provided by the `soul` plugin.
- LaTeX-macro-leak: provided by bookwright itself.

## Typical workflow

1. `/bookwright:init mybook` then `cd mybook`.
2. `/bookwright:design master`, then `/bookwright:design part1`, etc.
3. For each chapter: `/bookwright:plan chN`, then `/bookwright:draft chN`.
4. Per-Part close: `/bookwright:integrate part1`.
5. Full-book close: `/bookwright:integrate book`.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/commands/help.md && git commit -m "bookwright: /bookwright:help command prints quick reference"
```

---

### Phase D: Agents (9 tasks)

Each agent is one `.md` file with rich YAML frontmatter (`name`, `description` with multiple `<example>` blocks for routing) plus a body containing the agent's prompt. The body is the most important part: it instructs the agent exactly what to read, what to produce, and what discipline to follow.

**Use `plugin-dev:agent-creator` for each agent.** That subagent produces well-formed frontmatter automatically. Each task below specifies WHAT to tell `plugin-dev:agent-creator` (the agent's purpose, the routing examples, the body content), then invokes it.

If `plugin-dev:agent-creator` is unavailable for any reason, hand-roll using `~/github/alex-claude-plugins/worldsmith/agents/writer.md` as a format template.

### Task 15: Write `agents/writer.md` (orchestrator)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/writer.md`

- [ ] **Step 1: Read the worldsmith writer as the format template**

```bash
cat ~/github/alex-claude-plugins/worldsmith/agents/writer.md
```

- [ ] **Step 2: Invoke `plugin-dev:agent-creator` with this spec**

Spec to pass to the agent-creator:

```
Agent name: writer
Plugin: bookwright

Role: Multi-agent drafting orchestrator for technical non-fiction. Acts as lead author: reads the relevant chapter plan, walks through its per-section tasks, dispatches the appropriate drafting specialist for each (section-writer, notebook-author, or source-reformulator), then dispatches spec-auditor + quality-auditor in parallel for review. If either auditor surfaces substantive findings, dispatches a fix subagent and re-runs the relevant auditor to verify. Reports task commit SHAs and word counts.

Tools: Read, Write, Edit, Glob, Grep, Bash, Task, AskUserQuestion

Routing examples (3 to 4):
1. User says "Draft chapter 5" → assistant launches writer orchestrator.
2. User says "Write section bloom-from-scratch.tex" → assistant launches writer orchestrator on the single section.
3. User says "Fix the chapter 7 review findings" → assistant launches writer orchestrator with the review report as input.

Prompt body should encode:
- Path A discipline: per-task implementer → spec-compliance review → quality review → fix loop.
- Page budget tolerance: aim for the per-section target; allow plus-or-minus 30 percent.
- Header comment block requirement: every section starts with a comment block documenting label resolution.
- Soul-voice constraints: no Unicode em-dash, no curated banned phrases (soul plugin hook enforces).
- No reader-visible LaTeX macro names (macro-leak hook enforces).
- Commit message convention: HEREDOC with subject line "book: <action>" and Co-Authored-By trailer.
- Do not stage book.pdf (binary artifact; build artifact only).
- Read the relevant plan file fully before dispatching subagents.
```

- [ ] **Step 3: Verify the produced file has valid frontmatter and a body with the discipline points listed above.**

```bash
head -30 ~/github/alex-claude-plugins/bookwright/agents/writer.md
```

- [ ] **Step 4: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/writer.md && git commit -m "bookwright: writer orchestrator agent (multi-agent drafting)"
```

---

### Task 16: Write `agents/reviewer.md` (orchestrator)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/reviewer.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: reviewer
Plugin: bookwright

Role: Multi-agent editorial review orchestrator. Reads the in-scope sections (single section, full chapter, full Part, or full book), dispatches all four review specialists (spec-auditor, quality-auditor, math-auditor, cross-ref-auditor) in parallel, then synthesizes the four findings into a unified report saved to docs/superpowers/reviews/YYYY-MM-DD-<scope>.md.

Tools: Read, Glob, Grep, Task, Write

Routing examples:
1. User says "Review chapter 5" → launch reviewer orchestrator with scope=chapter, name=ch05.
2. User says "Review section X" → launch reviewer with scope=section, name=X.
3. User says "Heavy multi-agent review of the full book" → launch reviewer with scope=book.

Prompt body should encode:
- Dispatch the four specialists in parallel using one Task tool call per specialist.
- After all four return, deduplicate findings (same issue surfaced by two auditors gets one entry).
- Categorize by severity: BLOCKING (factually wrong, build-breaking), SUBSTANTIVE (real but not blocking), MINOR (style, nit).
- Report should include per-finding: location (file + line if possible), severity, what the finding is, suggested fix.
- Save the report; do NOT auto-fix. Fixes are the user's call, possibly via /bookwright:draft with the report as input.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/reviewer.md && git commit -m "bookwright: reviewer orchestrator agent (multi-agent editorial review)"
```

---

### Task 17: Write `agents/section-writer.md` (drafting specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/section-writer.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: section-writer
Plugin: bookwright

Role: Drafts a single prose section per the task's content checklist, page budget, label requirements, and notation discipline. Produces a section file with a header cross-reference comment block (documenting which labels resolve and which are forward refs), the prose itself, any required theorem/proposition/definition environments, and a closing signpost to the next section.

Tools: Read, Write, Edit, Glob, Grep, Bash

Routing examples:
1. Launched by the writer orchestrator with a task spec: "Draft §5.2 The Bloom Filter From Scratch (~7pp); content checklist: [construction, FNR=0 argument, FPR derivation, optimal k, worked example, signpost]; cite \Cref{thm:composition}."
2. Launched on a single task end-to-end; produces one file, runs the build to verify, commits.

Prompt body should encode:
- Read all source files named in the task spec BEFORE drafting.
- Read prior sections in the same chapter for voice continuity.
- Match the existing voice (sentence rhythm, math notation density, signposting style).
- Header comment block at the top of the file listing DEFINED labels (this section), RESOLVED labels (from prior sections/chapters), FORWARD labels (resolve later).
- Use the alex.sty notation macros (or the project's analog) consistently.
- DO NOT write LaTeX macro names in reader-facing prose (the macro-leak hook will block).
- DO NOT use Unicode em-dash or any banned phrase (the soul-voice hook will block).
- Build the book (cd book && make cleanall && make) before committing; exit 0 required.
- Commit with HEREDOC message; do not stage book.pdf.
- Report back: build exit code, commit SHA, word count.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/section-writer.md && git commit -m "bookwright: section-writer drafting specialist"
```

---

### Task 18: Write `agents/notebook-author.md` (drafting specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/notebook-author.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: notebook-author
Plugin: bookwright

Role: Drafts and executes paired notebooks for a chapter. Reads docs/superpowers/bookwright.config.yaml for the notebook stack (Python+uv / R+renv / Quarto); reads the chapter's plan for content checklist and numerical-sanity targets; writes the notebook as valid nbformat-4 JSON (or .Rmd / .qmd as appropriate); executes end-to-end; reports execution exit code and observed numerical values against sanity targets.

Tools: Read, Write, Bash, Glob

Routing examples:
1. Launched by writer orchestrator: "Draft and execute the chapter 5 notebook per Task 9 of Plan 5."
2. Launched directly via /bookwright:notebook ch05.
3. Refresh a previously-drafted notebook after the chapter prose changed.

Prompt body should encode:
- Read the chapter's plan section for the notebook (typically the last task before integration).
- Read the bookwright.config.yaml for stack choice; adapt execution command.
- Read prior notebooks for style continuity (cell count discipline, markdown voice, plot style).
- Stack-specific execution commands:
  - Python+uv+Jupyter: cd <project>/notebooks && uv run jupyter nbconvert --to notebook --execute <name>.ipynb --output <name>.ipynb
  - R+renv+RMarkdown: cd <project>/rmd && Rscript -e 'rmarkdown::render("<name>.Rmd")'
  - Quarto: cd <project>/qmd && quarto render <name>.qmd
- After execution, compare observed numerical values to the sanity targets in the plan; report match/mismatch.
- If execution fails or values miss targets, surface the discrepancy and the notebook output for user review.
- Commit only after successful execution with all sanity targets met (or with documented acceptable variance).
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/notebook-author.md && git commit -m "bookwright: notebook-author drafting specialist (Jupyter/R Markdown/Quarto)"
```

---

### Task 19: Write `agents/source-reformulator.md` (drafting specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/source-reformulator.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: source-reformulator
Plugin: bookwright

Role: Reads source papers (typically in a sibling-monorepo path passed as an argument) and reformulates the relevant content for textbook prose. Cite-don't-copy discipline: cite the paper for results that need attribution but produce fresh pedagogical prose, do not reproduce paragraphs verbatim.

Tools: Read, Glob, Grep

Routing examples:
1. Launched by section-writer when a task spec says "reformulate papers/bernoulli_sets/sections/algebra_of_sets.tex for §5.2".
2. Launched directly when the user is drafting a section that depends on external source material.

Prompt body should encode:
- Read the source paper(s) fully before reformulating.
- Identify the results that need attribution; produce a cite list.
- Produce fresh prose at a pedagogical depth (more concrete examples than the paper, more handholding).
- Do not reproduce paragraphs verbatim; rewrite to match the textbook's voice.
- Return: a markdown summary of the source material + a draft prose passage + a cite list (BibTeX keys for what the section will need).
- This agent does NOT write directly to the book/ tree; it produces input for section-writer to use.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/source-reformulator.md && git commit -m "bookwright: source-reformulator drafting specialist (cite-don't-copy)"
```

---

### Task 20: Write `agents/spec-auditor.md` (review specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/spec-auditor.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: spec-auditor
Plugin: bookwright

Role: Reads a drafted section and verifies it meets the per-chapter plan's content checklist. Reports missing items, items in the wrong order, page-budget violations, label-definition gaps.

Tools: Read, Glob, Grep

Routing examples:
1. Launched by writer orchestrator after a section is drafted.
2. Launched by reviewer orchestrator as one of four parallel auditors.

Prompt body should encode:
- Read the relevant plan file to find the task spec for this section.
- Read the drafted section file.
- For each item in the content checklist, verify presence (cite line numbers).
- Check page budget: compare actual word count to the target band.
- Check labels: all labels named in the plan are defined; no extra ad-hoc labels.
- Check cross-references: header comment block exists; backward refs all resolve; forward refs documented.
- Report: a bullet list of PASS/FAIL/NOTE items, closing one-sentence verdict.
- Do NOT edit the file. Report-only.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/spec-auditor.md && git commit -m "bookwright: spec-auditor review specialist (checks against plan content checklist)"
```

---

### Task 21: Write `agents/quality-auditor.md` (review specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/quality-auditor.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: quality-auditor
Plugin: bookwright

Role: Cold-read editorial reviewer. Reads a section WITHOUT seeing the plan; reports pedagogical clarity issues, hidden assumptions, unmotivated jumps, claim/evidence gaps, prose-craft weaknesses.

Tools: Read, Glob

Routing examples:
1. Launched by writer orchestrator after a section is drafted (parallel with spec-auditor).
2. Launched by reviewer orchestrator as one of four parallel auditors.

Prompt body should encode:
- Read the section file alone; do NOT read the plan file.
- Read prior chapter sections for voice continuity reference.
- Ask: does each step follow from the previous? Are there silent assumptions? Are the worked examples actually illustrative? Does the prose match the chapter's established voice?
- Report findings as bullets, organized by location.
- Closing one-sentence verdict: "ships as is" / "minor polish" / "substantive revision needed".
- Do NOT edit the file.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/quality-auditor.md && git commit -m "bookwright: quality-auditor review specialist (cold-read editorial review)"
```

---

### Task 22: Write `agents/math-auditor.md` (review specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/math-auditor.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: math-auditor
Plugin: bookwright

Role: Verifies arithmetic, formula derivations, and worked examples in a section BY HAND. Computes each numerical result independently and compares to the prose; reports discrepancies and suggests corrections.

Tools: Read, Bash, Glob

Routing examples:
1. Launched by reviewer orchestrator as one of four parallel auditors.
2. Launched directly when the user suspects a math error in a specific section.

Prompt body should encode:
- Read the section file.
- For each numerical worked example, recompute by hand or via a Python one-liner (use Bash for sympy/numpy).
- For each formula derivation, walk the algebra step by step.
- For each cited theorem from prior chapters, verify the section uses the theorem within its stated hypotheses.
- Report: bullet list of math findings with severity (BLOCKING for wrong numbers; SUBSTANTIVE for unjustified jumps; MINOR for notation inconsistencies).
- The Bernoulli session's math-auditor would have caught: chapter 5 §5.2 (1-e^{-2})^{20} ≈ 0.0117 (wrong; correct is 0.0546); chapter 5 §5.4 Bloom space estimate at fpr=0.01 ≈ 14.4n (wrong; correct is 9.6n); chapter 6 §6.1 predicate-OR vs bit-OR-Bloom conflation. Reference these as the kind of finding expected.
- Closing verdict: ships, minor fix, substantive revision.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/math-auditor.md && git commit -m "bookwright: math-auditor review specialist (verifies arithmetic and derivations by hand)"
```

---

### Task 23: Write `agents/cross-ref-auditor.md` (review specialist)

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/agents/cross-ref-auditor.md`

- [ ] **Step 1: Invoke `plugin-dev:agent-creator` with this spec**

```
Agent name: cross-ref-auditor
Plugin: bookwright

Role: Verifies cross-reference integrity for a section, chapter, Part, or full book. Checks that \Cref{} targets exist; flags label-name collisions; categorizes undefined refs as expected (per the documented baseline) vs unexpected.

Tools: Read, Bash, Glob, Grep

Routing examples:
1. Launched by reviewer orchestrator as one of four parallel auditors.
2. Launched by the /bookwright:integrate command as part of the per-Part or full-book check.

Prompt body should encode:
- For each section file in scope, parse the header comment block to read DEFINED, RESOLVED, FORWARD label lists.
- Verify the header's DEFINED matches actual \label{} declarations in the file (no missing entries, no extra unlisted labels).
- For RESOLVED labels, verify each one is defined somewhere in the book/ tree.
- For FORWARD labels, verify each is documented in some plan file as expected-to-resolve-later.
- Grep book.log (after a build) for "Reference undefined" warnings; categorize each as expected (matches the documented baseline) or unexpected (a real bug).
- Report: bullet list of cross-ref findings; closing verdict.
- This is also the agent that generates the cross-reference map table that goes into the integration-pass record.
```

- [ ] **Step 2: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/agents/cross-ref-auditor.md && git commit -m "bookwright: cross-ref-auditor review specialist (verifies label integrity)"
```

---

### Phase E: Skills (3 tasks)

Each skill is one `SKILL.md` file in its own subdirectory, following progressive-disclosure conventions: short triggering description in YAML frontmatter; detailed instructions in body.

**Use `plugin-dev:skill-reviewer` to validate each skill after writing it.**

### Task 24: Write `skills/textbook-methodology/SKILL.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/skills/textbook-methodology/SKILL.md`

- [ ] **Step 1: Write the skill file**

```markdown
---
name: textbook-methodology
description: Use when drafting prose sections for a bookwright (technical non-fiction) project. Encodes the Bernoulli-textbook workflow: atom-outward design, deferral discipline, running threads, page budgets, Path A subagent pattern, header comment block convention.
metadata:
  type: methodology
---

# Textbook Methodology (bookwright)

The Bernoulli-textbook approach: discipline that makes long-form technical books actually finishable.

## Atom-outward design

When designing a Part, sequence the chapters so the FOUNDATION chapter is drafted LAST. The Bernoulli textbook drafted chapter 1 (the noisy bit, the foundational atom) after chapters 2, 3, 4, because chapter 1 is best written knowing where the reader is being taken. The same pattern applies at the Part level: the part introduction chapter benefits from being drafted after the technical chapters it introduces.

## Deferral discipline

Earlier chapters often need to mention a topic that gets full treatment later. Use the "we'll address this in §X" pattern: name the deferral explicitly, cite the section that will retire it, and make sure the integration check verifies that the target section actually does.

Examples from the Bernoulli textbook:
- Chapter 1 §1.4 said "the full treatment of estimation lives in chapter 7." Chapter 7 §7.1 explicitly says it retires this deferral, and §7.2-7.3 cash in.
- Chapter 1 exercise 10 said "what would a non-noisy-bit look like? See chapter 16." Chapter 16 §16.1 lists this as one of the deferrals it cashes.

## Running threads

The master spec names 3-5 running threads (recurring concepts/examples that appear across chapters). Each chapter carries N of M threads. The integration check verifies each thread appears in the chapters the spec assigned it to.

Bernoulli threads: BSC (binary symmetric channel), biased coin, classifier verdict, Bloom filter, Miller-Rabin, Bernoulli[T] type. Each carries through multiple chapters; the integration check produces an inventory.

## Page budgets

Per-section page targets are stated in the per-chapter plan. Plans 1-3 of Bernoulli came in 30-43% over target; Plans 4+ adjusted by aiming for the LOWER end of the target band to land near nominal. Tolerance: plus-or-minus 30 percent is the integration-check band.

If a section comes in significantly over, reviewers should ask: is the math density justifying it (acceptable), or is the prose padded (cut)?

## Path A subagent discipline

For each section drafting task, the cadence is:

1. Implementer subagent: drafts the section per the plan's content checklist, builds the book, commits.
2. spec-auditor subagent: checks against the content checklist.
3. quality-auditor subagent: cold-reads for clarity and craft.
4. If either auditor surfaces substantive findings: a fix subagent applies the changes, then the relevant auditor is re-run to verify.

This pattern protects main conversation context and catches issues per-section rather than per-chapter.

## Header comment block convention

Every section file starts with a comment block (LaTeX `%` lines) that documents:

- DEFINED here: labels this section creates.
- RESOLVED: labels from prior chapters that this section cites (cite each, with file path).
- FORWARD: labels this section cites that resolve in later sections/chapters (cite the resolving section).

The cross-ref-auditor reads these blocks to verify integrity.

## Source-paper reformulation

If the book draws on prior research papers, the cite-don't-copy discipline applies: cite the paper for results, produce fresh pedagogical prose. The source-reformulator agent handles this.

## Commit discipline

- One drafting task = one commit.
- Commit message HEREDOC with subject "book: <action>" and Co-Authored-By trailer.
- Do NOT stage book.pdf (binary artifact; rebuild from source).
- Review fixes get their own commits ("book: fix chapter X §X.Y per quality review").

## What this skill does NOT cover

- Cross-reference label naming and the header comment block template: see `bookwright:cross-reference-discipline`.
- Notebook execution and numerical-sanity-target conventions: see `bookwright:notebook-paired-with-prose`.
```

- [ ] **Step 2: Invoke `plugin-dev:skill-reviewer` on this file**

The skill-reviewer subagent verifies frontmatter correctness, trigger-phrase quality, body structure.

- [ ] **Step 3: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/skills/textbook-methodology/SKILL.md && git commit -m "bookwright: textbook-methodology skill (Bernoulli workflow discipline)"
```

---

### Task 25: Write `skills/cross-reference-discipline/SKILL.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/skills/cross-reference-discipline/SKILL.md`

- [ ] **Step 1: Write the skill file**

```markdown
---
name: cross-reference-discipline
description: Use when writing cross-referenced sections in a bookwright project. Covers the header comment block template, label-naming conventions, when to use prose-only vs Cref, forward-reference documentation, and the integration-check baseline.
metadata:
  type: convention
---

# Cross-reference Discipline (bookwright)

LaTeX cross-references are mechanical. The trouble with them is that LaTeX silently emits "Reference undefined" warnings without erroring out, and over a long manuscript a single typo can cascade into chapters of broken refs that nobody notices. This skill encodes the discipline that prevents that.

## Header comment block (every section)

Every section file starts with a comment block. Template:

```
% §X.Y Section Title
%
% Cross-reference resolution status:
%
% DEFINED here: labels this section creates.
%   \label{sec:foo}
%   \label{def:bar}
%   \label{thm:baz}
%
% RESOLVED (chapter X):
%   \Cref{sec:foo-prior}    -- file: book/chapters/chXX/foo.tex
%   \Cref{def:bar-prior}    -- file: book/chapters/chXX/bar.tex
%
% FORWARD REFS (resolve in later sections/chapters):
%   \Cref{sec:foo-future}   -- target: ch. Y §Y.Z (this plan's Task N)
%   \Cref{ch:future-chapter} -- target: ch. Z (drafted in a future plan)
```

Why: the cross-ref-auditor and the integration check both read these blocks. The comment is the section's contract with the rest of the book.

## Label naming conventions

- `sec:foo-bar`: section labels (kebab-case after the type prefix).
- `def:foo-bar`: definitions.
- `prop:foo-bar`: propositions.
- `thm:foo-bar`: theorems.
- `cor:foo-bar`: corollaries.
- `lem:foo-bar`: lemmas.
- `eq:foo-bar`: display equations.
- `tab:foo-bar`: tables.
- `fig:foo-bar`: figures.
- `alg:foo-bar`: algorithms.
- `ex:chN-M`: exercises (chapter N, exercise number M).
- `ch:foo-bar`: chapters.

Label names should be the section/concept name in kebab-case. Avoid generic names like `sec:intro` or `def:1` that collide across chapters.

## When to use \Cref vs prose-only

- Use `\Cref{...}` when the target label EXISTS at build time.
- Use prose-only (e.g., "chapter 17 covers this") when:
  - The target chapter is not yet drafted (Plan 0 stubs aside).
  - The reference is informal ("the next chapter," "the appendix").
  - The reference is to an external paper (use `\cite{}` instead).

The Bernoulli baseline of "expected unresolved refs" includes `ch:composition` (chapter 4 forward into Part II; chapter 6's label is `ch:set-composition`; never renamed) and `ch:sketches` (chapter 9 prose; chapter 10's label is `ch:sketches-estimators`). These are documented in the integration-pass record so they pass the audit.

## Forward-reference documentation

When you write a forward ref, EITHER:

1. The target label exists in a Plan 0 stub file (chapter-level forward refs to undrafted chapters resolve to the stub's label).
2. The target is documented as "resolves in plan N" in the header comment block of THIS section AND in the plan file for the section that will define the label.

A forward ref undocumented in either place is a bug.

## Integration-check baseline

When `/bookwright:integrate` runs, it greps `book.log` for `Reference undefined`. It expects the set of unresolved refs to match the documented baseline. Any UNEXPECTED unresolved ref is a FAIL.

When you add a new section, EITHER its labels resolve immediately (the section file defines them) OR you add the labels to the documented baseline as expected forward refs in the integration-pass record.

## Cross-ref auditor

The cross-ref-auditor agent reads section header comment blocks and verifies them against actual `\label{}` declarations and `\Cref{}` invocations. Run it after drafting if you want to catch issues per-section.
```

- [ ] **Step 2: Invoke `plugin-dev:skill-reviewer` on this file**

- [ ] **Step 3: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/skills/cross-reference-discipline/SKILL.md && git commit -m "bookwright: cross-reference-discipline skill (header comment block + label conventions)"
```

---

### Task 26: Write `skills/notebook-paired-with-prose/SKILL.md`

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/skills/notebook-paired-with-prose/SKILL.md`

- [ ] **Step 1: Write the skill file**

```markdown
---
name: notebook-paired-with-prose
description: Use when drafting or executing a paired notebook for a bookwright chapter. Covers when notebooks are required vs optional, numerical-sanity-target convention, exec-from-fresh-kernel requirement, and stack-specific execution commands (Jupyter/R Markdown/Quarto).
metadata:
  type: convention
---

# Notebook Paired with Prose (bookwright)

In a technical textbook, paired notebooks are not optional decoration. They are empirical verifiers: a chapter that claims a formula or worked example has a notebook that COMPUTES the formula and shows the empirical result matches. Broken notebook means broken chapter.

## When notebooks are required vs optional

Required:

- Any chapter with a worked numerical example. The notebook must compute the same example and match.
- Any chapter with an algorithm. The notebook implements it and runs it.
- Any chapter with an empirical claim ("the SE is roughly 0.05"). The notebook simulates and verifies.

Optional or omitted:

- Theory-only chapters (no worked examples, no algorithms). Bernoulli's chapters 4, 13, 17 had no notebooks; the master spec marks them theory-only.
- Bridge chapters that exist only to connect Parts.

The master spec's chapter outline marks which chapters have notebooks. The per-chapter plan's notebook task spec lists the content + numerical-sanity targets.

## Numerical-sanity-target convention

The plan lists explicit targets like:

- "Empirical FPR at $\fprate = 0.01$, k=7: within plus-or-minus 0.005 of theoretical 0.0078."
- "Wald CI coverage at $n_0 = 200, \fprate = 0.05$: in $[0.93, 0.97]$ band."

The notebook-author agent computes these and compares. Match = pass. Miss = flag for user review (could be the prose is wrong, could be the notebook is wrong, could be sampling noise).

## Exec-from-fresh-kernel requirement

Notebooks MUST execute end-to-end from a fresh kernel with no errors. The notebook-author runs:

- Python+uv+Jupyter: `cd <project>/notebooks && uv run jupyter nbconvert --to notebook --execute <name>.ipynb --output <name>.ipynb`
- R+renv+RMarkdown: `cd <project>/rmd && Rscript -e 'rmarkdown::render("<name>.Rmd")'`
- Quarto: `cd <project>/qmd && quarto render <name>.qmd`

Exit code 0 is required for commit.

## Common gotchas

- Python: forgetting to seed the RNG produces non-reproducible outputs. Always `np.random.default_rng(seed=42)` or similar.
- Python: dependencies must be in `pyproject.toml`. New dependencies require `cd <project> && uv add <pkg>` before re-executing.
- R: `renv::status()` should be clean; new packages require `renv::install("pkg")` then `renv::snapshot()`.
- Quarto: cell-by-cell execution depends on engine; if mixing R + Python, configure the engine carefully.
- All stacks: explicitly seed any randomness. Markdown cells should describe what the code cell will do, not just narrate it.

## Cell discipline

- Title cell (markdown): names the chapter and notebook.
- Setup cell (code): imports + seeded RNG.
- Body cells: alternating code + markdown for narrative + numerical verification.
- Discussion / open-question cell (markdown): forward-reference downstream chapters if relevant.

Match the cell count of prior chapter notebooks for the project (typically 12-18 cells). Light notebooks have ~10; substantive have ~16-20.

## Pluggable stack

The project's `docs/superpowers/bookwright.config.yaml` records the stack choice (set during `/bookwright:init`). The notebook-author reads this config before drafting. Stack-specific commands above; stack-specific conventions (Python uv, R renv, Quarto rendering) are picked up from the config.

## Skipping a notebook

If a chapter is theory-only per the master spec, skip the notebook task entirely. Do NOT write an empty placeholder notebook (clutters the project). The integration check verifies which chapters have notebooks vs theory-only.
```

- [ ] **Step 2: Invoke `plugin-dev:skill-reviewer` on this file**

- [ ] **Step 3: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/skills/notebook-paired-with-prose/SKILL.md && git commit -m "bookwright: notebook-paired-with-prose skill (notebook discipline)"
```

---

### Phase F: Tests

### Task 27: Write smoke tests for init, check, and the macro-leak hook

**Files:**
- Create: `~/github/alex-claude-plugins/bookwright/tests/test-init.sh`
- Create: `~/github/alex-claude-plugins/bookwright/tests/test-check.sh`
- Create: `~/github/alex-claude-plugins/bookwright/tests/test-macro-leak-hook.sh`

These are shell smoke tests. They are NOT exhaustive; they verify the plugin's components are at least correctly shaped.

- [ ] **Step 1: Write `test-init.sh`**

```bash
#!/usr/bin/env bash
# Smoke test: the plugin.json is valid and declares the expected fields.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# plugin.json exists
[ -f "$PLUGIN_ROOT/.claude-plugin/plugin.json" ] || { echo "FAIL: plugin.json missing"; exit 1; }

# plugin.json is valid JSON
python3 -m json.tool "$PLUGIN_ROOT/.claude-plugin/plugin.json" > /dev/null || { echo "FAIL: plugin.json invalid"; exit 1; }

# plugin.json declares name=bookwright
NAME=$(python3 -c "import json; print(json.load(open('$PLUGIN_ROOT/.claude-plugin/plugin.json'))['name'])")
[ "$NAME" = "bookwright" ] || { echo "FAIL: plugin name is '$NAME' not 'bookwright'"; exit 1; }

# README exists
[ -f "$PLUGIN_ROOT/README.md" ] || { echo "FAIL: README.md missing"; exit 1; }

# Required directories exist
for dir in commands agents skills hooks tests; do
    [ -d "$PLUGIN_ROOT/$dir" ] || { echo "FAIL: $dir/ missing"; exit 1; }
done

# Each command file exists
for cmd in init design plan draft notebook check review integrate help; do
    [ -f "$PLUGIN_ROOT/commands/$cmd.md" ] || { echo "FAIL: commands/$cmd.md missing"; exit 1; }
done

# Each agent file exists
for ag in writer reviewer section-writer notebook-author source-reformulator spec-auditor quality-auditor math-auditor cross-ref-auditor; do
    [ -f "$PLUGIN_ROOT/agents/$ag.md" ] || { echo "FAIL: agents/$ag.md missing"; exit 1; }
done

# Each skill exists
for sk in textbook-methodology cross-reference-discipline notebook-paired-with-prose; do
    [ -f "$PLUGIN_ROOT/skills/$sk/SKILL.md" ] || { echo "FAIL: skills/$sk/SKILL.md missing"; exit 1; }
done

# Hooks
[ -f "$PLUGIN_ROOT/hooks/hooks.json" ] || { echo "FAIL: hooks/hooks.json missing"; exit 1; }
[ -x "$PLUGIN_ROOT/hooks/scripts/check-latex-macro-leak.sh" ] || { echo "FAIL: hooks/scripts/check-latex-macro-leak.sh missing or not executable"; exit 1; }

echo "PASS: bookwright plugin structure check"
```

- [ ] **Step 2: Write `test-check.sh`**

```bash
#!/usr/bin/env bash
# Smoke test: all command, agent, skill files have valid YAML frontmatter.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

FAILED=0

check_frontmatter() {
    local file="$1"
    local first_line
    first_line=$(head -n 1 "$file")
    if [ "$first_line" != "---" ]; then
        echo "FAIL: $file does not start with '---' (no YAML frontmatter)"
        FAILED=$((FAILED + 1))
        return
    fi
    # Try to extract the frontmatter block and parse it as YAML.
    # Python's yaml module is the most portable check.
    python3 - "$file" << 'PYEOF'
import sys, yaml
path = sys.argv[1]
with open(path) as f:
    lines = f.readlines()
if lines[0].strip() != "---":
    print(f"FAIL: {path} no frontmatter")
    sys.exit(1)
end = None
for i, line in enumerate(lines[1:], start=1):
    if line.strip() == "---":
        end = i
        break
if end is None:
    print(f"FAIL: {path} frontmatter not closed")
    sys.exit(1)
fm = "".join(lines[1:end])
try:
    yaml.safe_load(fm)
except Exception as e:
    print(f"FAIL: {path} frontmatter invalid YAML: {e}")
    sys.exit(1)
PYEOF
    if [ $? -ne 0 ]; then FAILED=$((FAILED + 1)); fi
}

for cmd in init design plan draft notebook check review integrate help; do
    check_frontmatter "$PLUGIN_ROOT/commands/$cmd.md"
done
for ag in writer reviewer section-writer notebook-author source-reformulator spec-auditor quality-auditor math-auditor cross-ref-auditor; do
    check_frontmatter "$PLUGIN_ROOT/agents/$ag.md"
done
for sk in textbook-methodology cross-reference-discipline notebook-paired-with-prose; do
    check_frontmatter "$PLUGIN_ROOT/skills/$sk/SKILL.md"
done

if [ $FAILED -gt 0 ]; then
    echo "FAIL: $FAILED file(s) had invalid frontmatter"
    exit 1
fi

echo "PASS: all component files have valid YAML frontmatter"
```

- [ ] **Step 3: Write `test-macro-leak-hook.sh`**

```bash
#!/usr/bin/env bash
# Smoke test: the macro-leak hook blocks the patterns it should and allows clean prose.

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$PLUGIN_ROOT/hooks/scripts/check-latex-macro-leak.sh"

# Positive case: clean .tex content passes
CLEAN='{"tool_input": {"file_path": "foo.tex", "content": "Standard prose with $\\fprate$ in math mode. The Bloom filter has $\\fprate = 0.01$."}}'
if ! echo "$CLEAN" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: clean .tex content should pass but was rejected"
    exit 1
fi

# Negative case 1: \texttt{\textbackslash fprate} blocks
LEAK1='{"tool_input": {"file_path": "foo.tex", "content": "The macro \\texttt{\\textbackslash fprate} renders as $\\fprate$."}}'
if echo "$LEAK1" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: macro-name leak should block but passed"
    exit 1
fi

# Negative case 2: "alex.sty" mention blocks
LEAK2='{"tool_input": {"file_path": "foo.tex", "content": "The four rates are written via the standard alex.sty macros."}}'
if echo "$LEAK2" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: alex.sty mention should block but passed"
    exit 1
fi

# Non-tex file: should be skipped (exit 0)
NONTEX='{"tool_input": {"file_path": "foo.md", "content": "The macro \\texttt{\\textbackslash fprate} renders as something."}}'
if ! echo "$NONTEX" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: non-.tex file should be skipped but was blocked"
    exit 1
fi

# Comment-only line: should be allowed
COMMENT='{"tool_input": {"file_path": "foo.tex", "content": "% This comment mentions \\texttt{\\textbackslash fprate} and alex.sty.\\nStandard prose."}}'
if ! echo "$COMMENT" | bash "$HOOK" > /dev/null 2>&1; then
    echo "FAIL: comment-line containing leak patterns should pass but was blocked"
    exit 1
fi

echo "PASS: macro-leak hook accepts clean prose, blocks leaks, skips non-tex, allows comments"
```

- [ ] **Step 4: Make tests executable**

```bash
chmod +x ~/github/alex-claude-plugins/bookwright/tests/test-init.sh
chmod +x ~/github/alex-claude-plugins/bookwright/tests/test-check.sh
chmod +x ~/github/alex-claude-plugins/bookwright/tests/test-macro-leak-hook.sh
```

- [ ] **Step 5: Run all three tests**

```bash
cd ~/github/alex-claude-plugins/bookwright/tests && bash test-init.sh && bash test-check.sh && bash test-macro-leak-hook.sh
```

Expected: three `PASS:` lines, exit 0.

- [ ] **Step 6: Commit**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/tests/ && git commit -m "$(cat <<'EOF'
bookwright: smoke tests (structure, frontmatter, macro-leak hook)

test-init.sh: verifies plugin.json shape and all component files exist.
test-check.sh: verifies all command/agent/skill .md files have valid YAML frontmatter.
test-macro-leak-hook.sh: verifies the hook blocks the patterns it should and allows clean prose.

All three pass at v0.1 commit time.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Phase G: Validation and v0.1.0 tag

### Task 28: Run `plugin-dev:plugin-validator` and address any findings

**Files:**
- Modify (if validator surfaces findings): whichever files the validator flags.

- [ ] **Step 1: Invoke `plugin-dev:plugin-validator`**

Pass it the plugin path: `~/github/alex-claude-plugins/bookwright/`.

- [ ] **Step 2: Review the validator's report**

Expected categories of findings:

- Missing required fields in plugin.json (none expected; Task 1 covered them).
- Agent frontmatter missing required keys (e.g., no `description`).
- Skill frontmatter missing `name` or `description`.
- Hook declaration shape issues.

If any findings: fix them inline; re-run the validator.

- [ ] **Step 3: Re-run smoke tests**

```bash
cd ~/github/alex-claude-plugins/bookwright/tests && bash test-init.sh && bash test-check.sh && bash test-macro-leak-hook.sh
```

Expected: three PASS lines.

- [ ] **Step 4: Commit any fixes from validator**

```bash
cd ~/github/alex-claude-plugins && git add bookwright/ && git commit -m "bookwright: address plugin-validator findings"
```

(Skip if no changes.)

- [ ] **Step 5: Tag v0.1.0**

```bash
cd ~/github/alex-claude-plugins && git tag -a bookwright-v0.1.0 -m "bookwright v0.1.0: initial release"
```

- [ ] **Step 6: Report**

Summarize: number of commits made, plugin component counts (commands, agents, skills, hooks, tests), validator status (PASS), tag created. Note v0.2 deferred items (`rewriter` and `iterator` orchestrators; Quarto stack support refinements).

---

## Self-Review

After completing the plan:

**1. Spec coverage:** Each major spec section maps to tasks:
- Spec §3 (Stack): Task 1 (plugin.json), Task 6 (init command persists stack choice).
- Spec §4.1 (Commands, 9): Tasks 6-14.
- Spec §4.2 (Agents, 11; v0.1 ships 9): Tasks 15-23.
- Spec §4.3 (Skills, 3): Tasks 24-26.
- Spec §4.4 (Hooks, 2): Task 4-5 (macro-leak hook); soul-voice via README dependency note (Task 2).
- Spec §4.5 (Project file structure): Task 6 init command produces this.
- Spec §4.6 (Tests): Task 27.
- Spec §6 (How we use plugin-dev): used in Tasks 15-23 (agent-creator), 24-26 (skill-reviewer), 28 (plugin-validator).

The `rewriter` and `iterator` orchestrators are deferred to v0.2 per spec §11; this plan ships v0.1 only.

**2. Placeholder scan:** No "TBD" / "TODO" patterns. Each task has concrete commit messages and exact bash commands. The agent prompts that get passed to `plugin-dev:agent-creator` specify content + tools + routing examples explicitly.

**3. Type consistency:** All commands use the `/bookwright:NAME` convention. All agent files match the names listed in the spec §4.2 table. All skill names match spec §4.3. The hook script name matches the path in hooks.json.

---

## Execution Handoff

Plan complete and saved to `~/github/alex-claude-plugins/bookwright/docs/superpowers/plans/2026-05-29-bookwright-v0.1-implementation.md`. Two execution options:

1. **Subagent-Driven (recommended):** I dispatch a fresh subagent per task (or per phase, since the phases group naturally), review between tasks, fast iteration.

2. **Inline Execution:** Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
