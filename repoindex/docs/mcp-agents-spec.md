# Repoindex Plugin: MCP-First Agent Redesign

## Background

repoindex v0.15.0 has full MCP/CLI parity with 6 tools:

| Tool | Purpose |
|------|---------|
| `get_manifest()` | Database overview (tables, counts, languages) |
| `get_schema(table?)` | SQL DDL introspection |
| `run_sql(query)` | Read-only SQL (SELECT/WITH, max 500 rows) |
| `refresh(sources?)` | Trigger metadata refresh |
| `tag(repo, action, tag)` | Manage user-assigned tags |
| `export(output_dir, query?)` | Produce longecho-compliant arkiv archive |

The SQL data model has 4 tables: `repos`, `publications`, `events`, `tags`. All joins through `repo_id`.

Since MCP tools are natively available to the LLM, the CLI reference skills (`repoindex`, `repo-query`, `repo-status`) are redundant. The plugin should shift from "teach the LLM how to use the CLI" to "provide agents that orchestrate MCP tools for complex workflows."

## What to remove

| Component | Type | Why remove |
|-----------|------|------------|
| `skills/repoindex/` | Skill | CLI reference docs. MCP tool descriptions + `get_schema()` cover this. |
| `skills/repo-polish/` | Skill | Becomes the `repo-polish` agent (see below). |
| `commands/repo-query` | Command | `run_sql` handles this directly. |
| `commands/repo-status` | Command | A few `run_sql` calls produce the same dashboard. |

## What to keep

| Component | Type | Why keep |
|-----------|------|----------|
| `agents/repo-explorer` | Agent | Multi-query analysis. Update to use MCP tools instead of CLI. |

## New agents

### 1. `repo-doctor` agent

**Purpose:** Collection health triage. "What needs attention across my repos?"

**Trigger phrases:** "check my repos", "what needs work?", "collection health", "which repos need attention?", "repo audit"

**What it does (multi-step, using MCP tools):**

1. **Query dirty repos** (uncommitted changes):
   ```sql
   SELECT name, path FROM repos WHERE is_clean = 0
   ```

2. **Query repos ahead of remote** (unpushed commits):
   ```sql
   SELECT name, ahead FROM repos WHERE ahead > 0
   ```

3. **Query quality gaps** (missing license, README, CI):
   ```sql
   SELECT name,
     CASE WHEN has_license = 0 THEN 'no license' END,
     CASE WHEN has_readme = 0 THEN 'no readme' END,
     CASE WHEN has_ci = 0 THEN 'no CI' END
   FROM repos
   WHERE has_license = 0 OR has_readme = 0 OR has_ci = 0
   ```

4. **Query stale repos** (no recent commits, not archived):
   ```sql
   SELECT r.name, MAX(e.timestamp) as last_activity
   FROM repos r LEFT JOIN events e ON r.id = e.repo_id
   WHERE r.github_is_archived = 0
   GROUP BY r.id
   HAVING last_activity < datetime('now', '-90 days')
   ORDER BY last_activity
   ```

5. **Query unmirrored repos** (future, when mirrors table exists):
   ```sql
   SELECT name FROM repos WHERE id NOT IN (SELECT repo_id FROM mirrors WHERE platform_id = 'codeberg')
   ```

6. **Query publication gaps** (detected but not published):
   ```sql
   SELECT r.name, p.registry FROM publications p
   JOIN repos r ON p.repo_id = r.id WHERE p.published = 0
   ```

7. **Synthesize a prioritized action list:**
   - Critical: dirty repos, unpushed commits
   - Important: missing license/README, unpublished packages
   - Maintenance: stale repos, quality gaps

**Model:** sonnet (fast, judgment-oriented)
**Tools:** MCP repoindex tools only (run_sql, get_manifest)
**Color:** yellow (attention/warning)

### 2. `repo-polish` agent

**Purpose:** Single-repo release preparation. "Prepare this repo for release."

**Trigger phrases:** "polish this repo", "prepare for release", "audit this repo", "set up metadata", "improve README", "add citation"

**What it does (multi-step):**

1. **Audit the repo** via MCP:
   ```sql
   SELECT * FROM repos WHERE name = ?
   SELECT * FROM publications WHERE repo_id = ?
   SELECT tag, source FROM tags WHERE repo_id = ?
   ```

2. **Identify gaps** (structured checklist):
   - README exists? Quality?
   - LICENSE present?
   - CITATION.cff present? DOI?
   - CI configured?
   - Published on PyPI/CRAN? Version match?
   - GitHub topics/description set?
   - codemeta.json present?
   - CHANGELOG present?

3. **Deterministic fixes** (via shell, with --dry-run first):
   ```bash
   repoindex ops generate citation --dry-run "name == 'REPO'"
   repoindex ops generate codemeta --dry-run "name == 'REPO'"
   repoindex ops github set-topics --from-pyproject --dry-run "name == 'REPO'"
   ```

4. **AI-assisted fixes** (prose that needs judgment):
   - README writing/improvement
   - Description copywriting
   - Topic suggestions

5. **Re-audit** to confirm improvements.

**Model:** opus (needs deep codebase understanding for README/description writing)
**Tools:** All tools (MCP + Read + Bash for file generation)
**Color:** green (improvement/growth)

### 3. Updated `repo-explorer` agent

Keep the existing agent but switch from CLI to MCP tools:

**Changes:**
- Replace `Bash` tool (running `repoindex sql "..."`) with `run_sql` MCP tool
- Replace `repoindex status` with `get_manifest` MCP tool
- Replace `repoindex show REPO --json` with `run_sql("SELECT * FROM repos WHERE name = ?")`
- Keep `Read` tool for reading actual repo files when needed

**Model:** sonnet (analysis, not prose)
**Tools:** MCP repoindex tools + Read
**Color:** cyan (unchanged)

## Implementation plan

### Step 1: Create `repo-doctor` agent

Create `agents/repo-doctor.md` with YAML frontmatter and prompt.

### Step 2: Convert `repo-polish` from skill to agent

Create `agents/repo-polish.md`. Move the workflow from the skill SKILL.md into the agent prompt, updating CLI references to use MCP tools where possible. Keep Bash for `ops generate` commands (these are write operations that don't have MCP equivalents yet).

### Step 3: Update `repo-explorer` agent

Replace CLI-based instructions with MCP tool references in the agent prompt.

### Step 4: Remove redundant skills and commands

- Delete `skills/repoindex/`
- Delete `skills/repo-polish/`
- Delete or update commands that are now covered by MCP

### Step 5: Update CLAUDE.md

Reflect the new architecture: MCP-first agents, no CLI reference skills needed.

### Step 6: Update plugin.json

Verify agent registration, remove skill references if the plugin manifest needs updating.

## Design principles

1. **MCP tools are the primary interface.** Agents call `run_sql`, `tag`, `export`, etc. directly. No CLI formatting or output parsing.
2. **Agents are for multi-step workflows.** Single queries go through `run_sql` directly (no agent needed).
3. **Deterministic ops stay in Bash.** `repoindex ops generate` commands write files. These don't have MCP equivalents and don't need them (they're infrequent, explicit operations).
4. **The "teach the LLM" pattern is obsolete.** MCP tool descriptions ARE the documentation. Skills that document CLI flags are redundant.
