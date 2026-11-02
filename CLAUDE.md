# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code **plugin marketplace** named `queelius-plugins` (the `name` in `.claude-plugin/marketplace.json`; the GitHub repo is `queelius/claude-anvil`). All plugins but one are distributed from this repo; research-communication is listed here with a `github` source and lives in its own private repo, `queelius/writing-style`. Most plugins are Markdown with YAML frontmatter; vista (Python, pytest via uv) and kdp's MCP server (TypeScript, vitest via npm) carry real code and tests, and worldsmith/bookwright have hook scripts with shell and pytest suites. CI (`.github/workflows/validate.yml`) runs all of them plus `scripts/check-plugins.py`.

**Install**: `/plugin marketplace add queelius/claude-anvil`
**Install a plugin**: `/plugin install repoindex@queelius-plugins`

| Plugin | Dir | Purpose |
|--------|-----|---------|
| **papermill** | `papermill/` | Academic paper lifecycle: thesis, lit survey, experiment, review, venue, submission |
| **worldsmith** | `worldsmith/` | Documentation-first fiction worldbuilding (the "Silmarillion approach") |
| **pub-pipeline** | `pub-pipeline/` | Publication workflows: R/CRAN/JOSS, Python/PyPI |
| **mf** | `mf/` | Metafunctor site management: CLI workflows over the Hugo site |
| **repoindex** | `repoindex/` | Repository intelligence (repo-polish, repo-explorer) plus five workflow slash commands. MCP-first over a local git catalog |
| **alex-confidential** | `alex-confidential/` | Confidentiality toolkit: cryptoid, pagevault, gpg |
| **kdp** | `kdp/` | Amazon KDP book publishing: manuscript audit, listing craft, submission workflow, cover MCP server |
| **crier** | `crier/` | Cross-post blog content to multiple platforms via the crier MCP server |
| **research-agent** | `research-agent/` | Autonomous research agent with a status/resume/synthesize/branch control surface for long runs |
| **vista** | `vista/` | Surface salient research directions from highly-cited papers. Live OpenAlex search, PDF section extraction, structured catalog |
| **bookwright** | `bookwright/` | Non-fiction book authoring: LaTeX + paired computational notebooks, multi-agent drafting/review, design→plan→draft→integrate workflow |
| **research-communication** | external: `queelius/writing-style` | Readable research writing: main idea first, terms defined before use, faithful revision; a review skill runs blind reviewers on a draft. Its components and tests live in that repo, so `check-plugins.py` skips them; installing it needs GitHub access to that private repo (`gh auth login` and `gh auth setup-git`) |

Versions are not listed here on purpose: each plugin's `.claude-plugin/plugin.json` is the only place a version lives (see Version Bumps).

### How this machine consumes the marketplace

`~/.claude/settings.json` declares `queelius-plugins` under `extraKnownMarketplaces` as a `directory` source pointing at this checkout. Relative-path plugins from a directory marketplace **load in place** from this working tree (the copy under `~/.claude/plugins/cache/` is bookkeeping, not what runs), so local edits take effect at the next session start or `/reload-plugins` with no version bump. Other users add the GitHub source and get updates via `claude plugin marketplace update` / `claude plugin update`, which is what the version bump is for.

### Per-repo plugin scoping (context economy)

The three authoring plugins (papermill, worldsmith, bookwright) are 38 of the marketplace's agents and are mutually exclusive by project type: a repo is a paper, a novel, or a textbook, never all three. Their catalog entries set `"defaultEnabled": false`, and on this machine they are also `false` at user scope (`enabledPlugins` in `~/.claude/settings.json`); enable one per repo. Settings precedence is user < project < local, so add to that repo's `.claude/settings.json`:

```json
{ "enabledPlugins": { "papermill@queelius-plugins": true } }
```

or run `/plugin enable papermill@queelius-plugins` from inside the repo. mf, pub-pipeline, kdp, crier, and research-agent are enabled globally. repoindex, vista, and alex-confidential are also `false` at user scope as of 2026-10 (repoindex's MCP server is configured separately at user scope in `~/.claude.json`, so its tools stay available without the plugin; see repoindex/CLAUDE.md for why the plugin does not ship a `.mcp.json`); enable them the same way when needed. Check `enabledPlugins` in `~/.claude/settings.json` rather than trusting this list.

### Three plugins say "research" and they occupy different stages

`vista`, `research-agent`, and `papermill` all sound like the same thing and are not:

- **vista (*finds the questions*).** Read-only reconnaissance over the *published literature*. Mines the Future Work / Limitations / Discussion / Conclusion sections of highly-cited OpenAlex papers and synthesizes candidate directions. The MCP server is deliberately *mechanical* (returns raw section text plus metadata as JSON, no LLM calls); the in-conversation Claude does the synthesis. Bounded and fast.
- **research-agent (*attacks a question*).** An autonomous reasoning loop (decompose, hypothesize, attempt, evaluate, reflect) that proves theorems, writes code, runs simulations, and hunts counterexamples, persisting everything to `.research/` in the *target project*. Runs until it concludes, is asked to stop, or exhausts an optional budget; the deliverable is `.research/synthesis.md`.
- **papermill (*writes the paper*).** Multi-agent thesis/draft/review/venue lifecycle once you have results to report. Its proof, simulation, and experiment skills are interactive, paper-scoped design aids; research-agent executes those modalities autonomously.

The natural pipeline is **vista, then research-agent, then papermill**: scope a direction, work it, write it up. The shared word "synthesis" is the main trap: vista synthesizes *other people's* stated future work, while research-agent synthesizes *its own* attempt results.

## Plugin Anatomy

```
<plugin>/
├── .claude-plugin/plugin.json   # Manifest: name, version, description, author (the only version)
├── skills/<name>/SKILL.md       # Skills: the core logic AND the /plugin:<name> slash entry points
├── commands/<name>.md            # Legacy-format slash commands (only where no same-name skill exists)
├── agents/<name>.md              # Subagents with system prompts
├── hooks/hooks.json              # Event handlers (optional)
├── .mcp.json                     # MCP server registration (optional)
└── CLAUDE.md                     # Per-plugin editing guidance (read before editing; not loaded at runtime)
```

Not all plugins use every component. alex-confidential has only a skill. crier, kdp, and vista ship MCP servers.

## File Format Conventions

### Skills (`skills/<name>/SKILL.md`)
YAML frontmatter with `name` and `description` (description contains trigger phrases for auto-detection). A skill is also the slash command `/plugin:<name>`, and supports the command frontmatter (`argument-hint`, `allowed-tools`, `disable-model-invocation`) and `$ARGUMENTS`. Put reference material in `skills/<name>/references/` and point to it with `${CLAUDE_PLUGIN_ROOT}`.

### Commands (`commands/<name>.md`)
Commands are the older format; the docs recommend skills for new work. **Never give a command the same name as a skill in the same plugin**: on a clash the command wins (verified on Claude Code 2.1.306), so the skill's description and body never load and a one-line "run the X skill" wrapper turns `/plugin:x` into a dead end. `scripts/check-plugins.py` fails on a clash. Existing commands (worldsmith, bookwright, repoindex, crier's chronicler) are standalone workflows with no same-name skill.

### Agents (`agents/<name>.md`)
YAML frontmatter with `name`, `description`, `tools` (list of allowed tools), `model`, and `color`. Body is the agent's system prompt. The tool that spawns subagents is `Agent` (formerly `Task`).

**Agent description policy (context cost).** Every enabled plugin's agent descriptions load into the main context of every session; agent bodies load only when spawned. So descriptions follow two tiers. User-facing entry points (the writer/reviewer/rewriter/reviser/iterator orchestrators, surveyor, researcher, joss-writer/joss-reviewer, the repoindex, crier, and vista agents) keep descriptions with at most two `<example>` blocks so auto-delegation can route to them. Internal specialists (section writers, scouts, auditors, checkers: anything an orchestrator dispatches by qualified name) use a single-sentence description ending with "not intended for direct invocation" and NO example blocks.

**Subagents cannot ask the user.** Claude Code removes `AskUserQuestion` from every subagent, even when listed in `tools`. Never grant it to an agent. Agents return judgment calls as a structured Decisions Needed block and the dispatching skill or command (main session) asks and re-dispatches; each authoring plugin documents its schema in one reference file. Nesting is limited to 3 subagent layers below the main session by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); the deepest chain here (iterator, rewriter, specialist) uses all 3.

**Pass paths, not contents.** Orchestrators give specialists file paths to Read, never pasted manuscripts: an Agent prompt is output tokens the orchestrator must generate.

**Agent model policy.** Heavy agents (orchestrators, content writers, judgment auditors) use `model: inherit` so they run on whatever model the user selected for the session. Do NOT pin `model: fable` in agent frontmatter: a subagent spawn that explicitly requests Fable can be rejected by an `availableModels` policy, the account's Fable access, or a Claude Code version older than v2.1.170, whereas `inherit` sidesteps all three. Mechanical auditors and cheap analysis agents (spec-auditor, cross-ref-auditor, format-validator, field-scout, software-auditor, community-auditor, surveyor, citation-verifier, repo-explorer, the crier agents) pin `sonnet` or `haiku`. vista's `PREMIUM_MODEL = claude-fable-5-1` is exempt: it is a direct Anthropic API call from the vista CLI, not a subagent spawn.

### Hooks (`hooks/hooks.json`)
worldsmith (SessionStart project detection; PostToolUse propagation reminders and cliche detection), bookwright (PostToolUse LaTeX macro-leak check), crier (SessionStart crier/MCP install check), and kdp (SessionStart dependency check, silent outside book projects). Rules:
- Quote `"${CLAUDE_PLUGIN_ROOT}"` in hook commands.
- Hooks run as separate processes and never see variables written to `$CLAUDE_ENV_FILE`; gate each hook on files on disk.
- A PostToolUse hook runs after the write; exit 2 feeds stderr back to Claude but does not undo anything, so messages must say "flagged", not "blocked".
- Hooks needing PyYAML must find an interpreter that has it (the `python3` first on PATH may not); see bookwright's `hooks/scripts/find_python.sh` and worldsmith's `worldsmith_python`.

### Slash-name collisions across plugins

Several plugins share bare names, which is fine because every entry is namespaced as `/plugin:name`. Always qualify in docs and examples:

| Bare name | Defined by |
|-----------|------------|
| `/draft`, `/revise` | papermill, worldsmith, bookwright |
| `/review` | papermill, worldsmith, bookwright, research-communication |
| `/iterate`, `/check`, `/help` | worldsmith, bookwright |
| `/init` | papermill, bookwright |
| `/status` | papermill, research-agent |

## Cross-Plugin Patterns

**State files**: papermill (`.papermill/state.md`), pub-pipeline (`.claude/pub-pipeline.local.md`), kdp (`.claude/kdp.local.md`), and research-agent (`.research/`) keep per-project state in the *target* project. Each plugin defines its schema in one file and the other files point to it.

**One source of truth for facts.** Facts that another system owns are read from it, not copied: mf reads the site's own CLAUDE.md, crier derives platforms and limits from `crier_doctor` and `crier://platforms`, repoindex queries enums and uses `ops audit`/`digest` output, kdp's specs live in `mcp/src/lib/kdp-specs.ts`. A copied table is a bug waiting to drift.

**`${CLAUDE_PLUGIN_ROOT}` references**: Skills and agents reference sibling files via this variable. Verify the target exists (`scripts/check-plugins.py` does).

**Author metadata via deets CLI**: Plugins needing author info (papermill, pub-pipeline) fall back to `deets show --format json` after per-project config.

**Audit report pattern** (pub-pipeline, kdp): structured gap reports with Critical (Must Fix) / Warnings (Should Fix) / Passed sections.

**Propagation discipline** (worldsmith): role-based docs (timeline authority, lore, systems, characters, style conventions, outline, themes, editorial backlog), not hardcoded filenames. Canonical docs are updated before manuscript text.

## Validation

From the repo root:

```bash
python3 scripts/check-plugins.py        # structure: frontmatter, clashes, agent refs, plugin-root refs
claude plugin validate .                # marketplace manifest
for d in */; do [ -f "$d/.claude-plugin/plugin.json" ] && claude plugin validate "$d"; done
(cd vista && uv run pytest -q)
(cd kdp/mcp && npm ci && npm test)
for t in worldsmith/tests/*.sh bookwright/tests/*.sh; do bash "$t"; done
python3 -m pytest -q worldsmith/tests   # needs PyYAML + pytest
```

`claude plugin validate` warns that each plugin-root `CLAUDE.md` is not loaded and that plugins have no icon; both are expected (those files are maintainer guidance).

## Version Bumps

The version lives in **one place**: each plugin's `.claude-plugin/plugin.json`. Catalog entries in `marketplace.json` carry no `version` (when both exist, `plugin.json` wins and the validator warns). Bump it when a change should reach GitHub installs; local directory-source use needs no bump. crier and kdp also have a Codex manifest (`.codex-plugin/plugin.json`) whose version tracks `plugin.json` with a `+codex.<timestamp>` suffix; update it in the same commit.

## Editing Guidelines

- Each plugin has its own CLAUDE.md with plugin-specific conventions; read it before editing that plugin
- Skills are self-contained and are the slash entry points; never add a same-name command wrapper
- State each rule once (in the skill or a `references/` file) and point to it from agents and commands
- Agents need well-defined tool lists: only grant tools the agent actually needs
- No em-dashes in prose (the user's style rule)
- All plugins share one git history: use conventional commit prefixes scoped to plugin, e.g. `feat(pub-pipeline):`, `fix(worldsmith):`
