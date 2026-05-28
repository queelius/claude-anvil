# Design: bookwright (Claude Code plugin for non-fiction long-form manuscripts)

**Author:** Alexander Towell
**Date:** 2026-05-28
**Status:** Design (pre-implementation)
**Sibling plugin:** `worldsmith` (fiction; lives at `~/github/alex-claude-plugins/worldsmith/`)
**Inspiration project:** Bernoulli textbook (`~/github/bernoulli/`); 18 chapters drafted in a multi-month session, encoding the workflow this plugin generalizes.

## 1. Purpose

`bookwright` is a documentation-first methodology and multi-agent toolchain for **technical non-fiction long-form manuscripts**. Same Silmarillion-style discipline as worldsmith: the design spec and per-chapter plans ARE the book; manuscript prose derives from them. The plugin codifies the workflow that produced the Bernoulli textbook so it can be applied to future technical books without re-inventing the discipline each time.

Scope: technical textbooks and research-derived monographs. Not memoir, not popular trade, not journalism (those need different tooling and would dilute the plugin's prompts).

Sibling positioning:
- `worldsmith` = fiction long-form, world-as-doc methodology, prose-craft auditors.
- `papermill` = academic papers, single-deliverable, citation-heavy.
- `bookwright` = technical non-fiction long-form, chapter/section/spec/plan hierarchy, math/cross-ref/notebook auditors.

## 2. Philosophy (inherited from worldsmith, adapted for non-fiction)

- **Specs first, manuscript second.** Master design spec → per-Part design specs → per-chapter implementation plans → per-section drafts. When a structural decision changes (running threads, page budgets, deferral plans), update the spec/plan FIRST, then propagate to the manuscript.
- **Path A subagent discipline.** Per-section drafting is: implementer subagent → spec-compliance reviewer subagent → quality reviewer subagent → fix subagent if substantive findings. This was the cadence that worked for the Bernoulli textbook; it protects main-conversation context and catches issues per-section rather than per-chapter.
- **Notebooks are empirical verifiers.** A chapter with a paired notebook MUST execute end-to-end with numerical-sanity targets matching prose claims. Broken notebook = broken chapter.
- **Running threads are tracked explicitly.** The design spec names 3-5 running threads (e.g., the BSC, the Bloom filter, Miller-Rabin in Bernoulli). Each chapter carries N of M threads; the integration check verifies the inventory.
- **Cross-reference integrity is mechanical.** Every section file has a header comment block documenting which labels resolve already vs forward refs. The cross-ref auditor verifies the inventory.
- **Deferral discipline.** Earlier chapters can name forward deferrals ("we'll address this in §X"); the integration check verifies every named deferral is retired in its target section.
- **Source-paper reformulation is cite-don't-copy.** When the book draws on prior research papers (Bernoulli drew on nine), the reformulator agent reads the paper and produces fresh pedagogical prose with citations to the paper for results, not paragraph-for-paragraph copy.

## 3. Stack

**LaTeX-primary.** Prose source is LaTeX (book class), with biblatex + biber. The plugin's prompts assume this; agents read and write `.tex` files; the `Makefile` Plan 0 scaffolds is `cleanall + biber + pdflatex` pipeline.

**Pluggable notebooks.** `/init` asks the user which notebook stack:
- **Python via uv + Jupyter** (Bernoulli default).
- **R via renv + R Markdown**.
- **Quarto** (.qmd polyglot).

A project-local config file `docs/superpowers/bookwright.config.yaml` records the choice. The `notebook-author` agent reads this config and adapts its instructions accordingly.

**Soul-voice hooks.** Reuse the existing `soul` plugin's hook. It catches Unicode em-dashes plus a curated list of academic-marketing buzzword phrases. Battle-tested in the Bernoulli session; no need to reinvent.

## 4. Components

### 4.1 Commands (9)

| Command | Purpose |
|---|---|
| `/bookwright:init [book-name]` | Scaffold a book repo: `book/`, `notebooks/`, `papers/`, `docs/superpowers/`, frontmatter/appendix stubs, preamble, Makefile, soul-voice + macro-leak hooks. Asks the user for notebook stack choice and persists to `docs/superpowers/bookwright.config.yaml`. |
| `/bookwright:design [part]` | Write a master spec or per-Part design spec via Socratic Q&A. Output to `docs/superpowers/specs/YYYY-MM-DD-<part>-design.md`. Includes the Bernoulli spec structure: audience, structural decisions, running threads, page budget, sequencing, success criteria. |
| `/bookwright:plan [chapter]` | Write a per-chapter implementation plan derived from the relevant design spec. Output to `docs/superpowers/plans/YYYY-MM-DD-<chapter>.md`. Includes Path A discipline checklist, per-task content checklists, cross-reference map. |
| `/bookwright:draft [chapter\|section]` | Launch the `writer` orchestrator. For a chapter, runs the full Path A sequence: scaffolding → per-section implementer → spec-compliance review → quality review → fix loop. For a single section, runs one task end-to-end. |
| `/bookwright:notebook [chapter]` | Draft + execute the paired notebook for a chapter. Separable so notebooks can be added or refreshed without re-drafting prose. Uses the configured notebook stack. |
| `/bookwright:check [scope]` | Fast diagnostics. Scopes: `section`, `chapter`, `part`, `book`. Runs: build clean, label resolution, page-count audit (per-chapter targets vs $\pm 30\%$ band), running-thread inventory, soul-voice audit, LaTeX-macro-leak audit. No editorial judgment; mechanical only. |
| `/bookwright:review [scope]` | Heavy multi-agent editorial review. Dispatches `math-auditor`, `spec-auditor`, `quality-auditor`, `cross-ref-auditor` in parallel; synthesizes findings into a unified report. |
| `/bookwright:integrate [scope]` | Per-Part or full-book integration check (mirrors Bernoulli Plan 4/8/13/15/18 Task 10 pattern). Writes an integration-pass record documenting verification results, known deferred items, and open follow-ups. |
| `/bookwright:help` | Quick reference for all commands, agents, and skills. |

### 4.2 Agents (10)

**Orchestrators (4):** mirror worldsmith's pattern.

| Agent | Role | Launched by |
|---|---|---|
| `writer` | Multi-agent drafting orchestrator. Dispatches `section-writer` + `notebook-author` + appropriate auditors in Path A discipline. | `/bookwright:draft` |
| `reviewer` | Multi-agent review orchestrator. Dispatches the four specialist auditors in parallel. | `/bookwright:review` |
| `rewriter` | Fix-then-verify orchestrator. Reads review report; dispatches fix subagents per finding; dispatches the relevant auditor to verify each fix. | (separate, currently merged into `writer` via fix loop; could be split out) |
| `iterator` | Autonomous review-fix loop until convergence or iteration cap. Mirrors worldsmith iterator. | (optional, future) |

**Drafting specialists (3):**

| Agent | Role |
|---|---|
| `section-writer` | Drafts prose sections per content checklist + page budget + cross-reference requirements. Produces header comment blocks documenting label resolution. Inherits voice from prior chapters. |
| `notebook-author` | Drafts + executes paired notebooks. Reads `bookwright.config.yaml` for stack; supports Jupyter/R Markdown/Quarto. Verifies numerical-sanity targets and reports empirical-vs-theoretical match. |
| `source-reformulator` | Reads source papers (typically in sibling-monorepo paths) and reformulates for textbook prose. Cite-don't-copy discipline: results are cited, not reproduced verbatim. |

**Review specialists (4):**

| Agent | Role |
|---|---|
| `spec-auditor` | Checks drafted section against the per-chapter plan's content checklist. Reports missing items, items in wrong order, page-budget violations. |
| `quality-auditor` | Cold-read reviewer. Reads the section without seeing the plan; reports pedagogical clarity issues, hidden assumptions, unmotivated jumps, claim/evidence gaps. |
| `math-auditor` | Verifies arithmetic, formula derivations, worked examples BY HAND. **Textbook-specific; the Bernoulli session caught real bugs this way that no other auditor surfaced** (chapter 5 §5.2 $(1-e^{-2})^{20}$ value error; chapter 5 §5.4 Bloom space estimate error; chapter 6 §6.1 predicate-OR vs bit-OR-Bloom conflation). |
| `cross-ref-auditor` | Verifies `\Cref{}` targets exist; checks for label-name collisions; flags forward refs that resolve in later plans vs unexpected unresolved refs. Generates the cross-reference map for the integration record. |

### 4.3 Skills (3, progressive disclosure)

Each skill follows the latest Anthropic plugin conventions: short triggering description in YAML frontmatter; detailed instructions in body.

| Skill | Triggers when... | Encodes |
|---|---|---|
| `bookwright:textbook-methodology` | Drafting prose tasks for a bookwright project. | Atom-outward design discipline; deferral conventions ("we'll address this in §X" + later chapter retires it); running threads (named in spec; each chapter carries N of M; integration verifies inventory); page budgets with 20-30% overshoot tolerance; header comment block convention; Path A subagent dispatch pattern. |
| `bookwright:cross-reference-discipline` | Writing cross-referenced sections. | Header comment block template; label naming conventions (`sec:`, `def:`, `prop:`, `thm:`, `cor:`, `ex:`, `ch:`); when to use prose-only vs `\Cref{}`; forward-ref documentation; the integration check's expected baseline of known undefined refs. |
| `bookwright:notebook-paired-with-prose` | Notebook tasks for a bookwright project. | When notebooks are required (chapters with worked examples requiring empirical verification) vs optional (theory-only chapters); numerical-sanity-target convention; how to phrase markdown narrative; execute-from-fresh-kernel requirement; common stack-specific gotchas (Python `uv run`, R `renv::run`, Quarto `quarto render`). |

### 4.4 Hooks (2, via `hooks.json`)

| Hook | Purpose |
|---|---|
| **Soul-voice hook** | Reuse the existing `soul` plugin's hook. The `soul` plugin must be installed separately by the user; `bookwright`'s README and `/bookwright:init` output document this dependency. Catches Unicode em-dashes plus the curated buzzword-phrase list maintained in that plugin. No new code in `bookwright` itself. |
| **LaTeX-macro-leak hook** | New, textbook-specific. PostToolUse hook on `Write`/`Edit` for `.tex` files. Blocks if non-comment lines contain: `\texttt{\textbackslash <command>` patterns, `"alex.sty"` mentions, `"the macro \..."` constructs, `"rendered as"`. These were the leak patterns the Bernoulli post-Plan-17 fix scrubbed from chapters 1/2/7. |

### 4.5 Project file structure (what `/init` scaffolds)

```
<book-name>/
├── book/                          # LaTeX sources (always present)
│   ├── chapters/                  # Per-chapter directories with section files
│   │   ├── ch01-<topic>.tex       # Chapter wrapper file (label + learning-outcomes + section inputs)
│   │   ├── ch01/                  # Section subfiles
│   │   │   ├── <section1>.tex
│   │   │   ├── <section2>.tex
│   │   │   ├── ...
│   │   │   ├── bibliographic-notes.tex
│   │   │   └── exercises.tex
│   │   └── ... (more chapters)
│   ├── frontmatter/               # titlepage, copyright, preface
│   ├── appendices/                # appendix stubs
│   ├── parts/                     # part1-<topic>.tex through partN-<topic>.tex
│   ├── alex.sty (or analog)       # Notation macros (shared with paper repos if applicable)
│   ├── preamble.tex
│   ├── references.bib
│   ├── book.tex
│   └── Makefile                   # cleanall + biber + pdflatex pipeline
├── notebooks/                     # (Python/Jupyter; if `uv` stack)
│   OR rmd/                        # (R Markdown)
│   OR qmd/                        # (Quarto)
├── papers/                        # Source papers (subtrees); optional
└── docs/
    └── superpowers/
        ├── specs/                 # Master spec + per-Part design specs
        ├── plans/                 # Per-chapter implementation plans + integration-pass records
        └── bookwright.config.yaml # Notebook stack choice + project settings
```

### 4.6 Tests

A `tests/` directory with smoke tests that exercise:
- `/bookwright:init` on a fresh directory produces a valid LaTeX project (`pdflatex` exits 0 on the scaffolded book).
- `/bookwright:check` on the scaffolded book reports the expected baseline (no false positives).
- The LaTeX-macro-leak hook blocks the patterns it should and allows the patterns it should.

Mirrors worldsmith's `tests/` discipline.

## 5. Bernoulli-lessons-encoded table

| Bernoulli lesson | Where it lives in bookwright |
|---|---|
| Atom-outward design, ch1 drafted LAST | `textbook-methodology` skill |
| Three running threads per Part | `textbook-methodology` skill + reviewer's thread-inventory check |
| Soul-voice constraints | shared `soul` plugin hook (declared as dependency) |
| LaTeX-macro-name leaks in prose | new dedicated hook in `bookwright/hooks/` |
| Per-task Path A discipline (impl → spec-check → quality-check → fix) | baked into `/draft` and the `writer` orchestrator |
| Math-correctness arithmetic | dedicated `math-auditor` agent |
| Cross-reference integrity, header comment blocks | `cross-reference-discipline` skill + `cross-ref-auditor` agent |
| Page budget with 20-30% overshoot tolerance | `textbook-methodology` skill + check command tolerance |
| Notebook as empirical verifier | dedicated `notebook-author` agent + `notebook-paired-with-prose` skill |
| Deferral cashing ("we'll cover in ch X" → ch X retires it) | `textbook-methodology` skill + integration-check verifies all named deferrals are resolved |
| Per-Part + full-book integration checks | dedicated `/integrate` command + integration-pass record template |
| Source-paper reformulation (cite don't subsume) | dedicated `source-reformulator` agent |
| Pluggable notebook stack | `bookwright.config.yaml` + agent prompts read it |

## 6. How we use the plugin-dev plugin to build this

Per Anthropic's current plugin-development best practices, we use the plugin-dev tools rather than hand-rolling:

| Step | Tool |
|---|---|
| Scaffold the plugin directory + `plugin.json` + base structure | `plugin-dev:create-plugin` skill |
| Write each of the 10 agent files (with proper YAML frontmatter, `<example>` blocks for routing, allowed-tools) | `plugin-dev:agent-creator` subagent per agent |
| Write each of the 3 skill files (with progressive-disclosure structure, trigger phrases, body content) | Manual draft + `plugin-dev:skill-reviewer` subagent per skill for verification |
| Validate the final plugin (plugin.json correctness, command frontmatter, agent descriptions, skill structure) | `plugin-dev:plugin-validator` subagent |

## 7. Repository layout

The plugin lives at `~/github/alex-claude-plugins/bookwright/` as a sibling to `worldsmith`, `papermill`, etc. The parent `~/github/alex-claude-plugins/` is the `claude-anvil` monorepo. The `bookwright/` directory follows the plugin-standard layout:

```
bookwright/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── LICENSE
├── CLAUDE.md                       # plugin-internal guidance (optional)
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
│   ├── writer.md
│   ├── reviewer.md
│   ├── rewriter.md
│   ├── iterator.md
│   ├── section-writer.md
│   ├── notebook-author.md
│   ├── source-reformulator.md
│   ├── spec-auditor.md
│   ├── quality-auditor.md
│   ├── math-auditor.md
│   └── cross-ref-auditor.md
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
│       └── specs/
│           └── 2026-05-28-bookwright-design.md  # this file
└── tests/
    ├── test-init.sh
    ├── test-check.sh
    └── test-macro-leak-hook.sh
```

## 8. Open Action Items (resolve during implementation)

1. **`rewriter` and `iterator` orchestrators.** Section 4.2 lists both, but the Bernoulli session merged the rewriter behavior into the `writer` orchestrator's fix loop and never used an iterator. Decide: ship both as separate agents for symmetry with worldsmith, or ship `rewriter` and defer `iterator` to v0.2.
2. **`source-reformulator` agent scope.** The Bernoulli reformulation came from sibling-monorepo papers. Should the agent assume a `papers/` subdirectory exists, or take an arbitrary path argument? Probably the latter, but agent prompt language should be ready.
3. **`notebook-author` notebook-execution gotchas.** Python+uv works; R+renv works; Quarto polyglot has its own gotchas (cell-by-cell execution depends on engine choice). The notebook author should test on at least one R or Quarto project before declaring multi-stack support.
4. **Integration-pass record template.** The Bernoulli integration records (Plan 4/8/13/15/18 Task 10) have a consistent structure. The plugin should ship a template that the `/integrate` command fills in.

## 9. Out of Scope

- Memoir, popular trade, journalism (different prose conventions; different review needs).
- Single-paper academic submissions (use `papermill`).
- Fiction (use `worldsmith`).
- Multi-author collaboration workflows (would need git-merge handling, draft attribution; out of scope for v0.1).
- Publisher-specific formatting (Springer style, Cambridge style, etc.); handled per-project in the user's preamble, not in the plugin.
- ISBN registration, marketing copy, KDP submission (use the existing `kdp` plugin).

## 10. Success Criteria

The plugin is successful if:

1. A new technical-textbook project can be scaffolded with `/bookwright:init <name>` and immediately produces a buildable LaTeX project.
2. A user who has read the Bernoulli textbook's plan files (in `~/github/bernoulli/docs/superpowers/plans/`) can recognize each pattern there as a `bookwright` command, agent, or skill.
3. A fresh chapter can be drafted with `/bookwright:draft chapter5` and produce output of comparable quality to what the manual Bernoulli session produced for chapter 5.
4. The `math-auditor` catches at least one arithmetic error on a real worked example during testing (matches the Bernoulli failure rate of catching ~3-4 such errors over 18 chapters).
5. The `LaTeX-macro-leak hook` blocks the patterns that escaped the Bernoulli session and required a post-Plan-17 cleanup commit.
6. The plugin passes `plugin-dev:plugin-validator` cleanly.

## 11. Versioning

- **v0.1.0**: ship the 9 commands; 9 agents (`writer` + `reviewer` orchestrators + 3 drafting specialists + 4 review specialists; defer `rewriter` + `iterator` to v0.2); 3 skills; 2 hooks (soul-voice declared as dependency on the `soul` plugin, macro-leak hook in plugin). Validate against the Bernoulli textbook as a regression test (run `/bookwright:check book` on bernoulli and verify expected baseline).
- **v0.2.0**: add `rewriter` + `iterator` orchestrators; add Quarto stack support to `notebook-author`.
- **v0.3.0**: add R + renv stack support; templates for common book types (monograph, edited collection, lecture-notes).
