# Cross-Paper Awareness Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add structured `related_papers` YAML block to the papermill schema, with repoindex-based discovery during init/refresh, and display in the status dashboard.

**Architecture:** Three markdown skill files are edited (init, status). No code, no tests — this is a plugin of prompt documents. Verification is frontmatter validation and manual inspection.

**Tech Stack:** Markdown with YAML frontmatter (Claude Code plugin conventions)

**Design doc:** `docs/plans/2026-02-20-cross-paper-awareness-design.md`

---

### Task 1: Add `related_papers` to the init schema template

**Files:**
- Modify: `skills/init/SKILL.md:235-242` (Step 7 schema template)

**Step 1: Add `related_papers: []` to the YAML template**

In `skills/init/SKILL.md`, the Step 7 schema template (the markdown code block starting at line 215) currently ends with `review_history: []` before the closing `---`. Insert `related_papers: []` between `review_history: []` and the closing `---`:

```yaml
review_history: []

related_papers: []
---
```

**Step 2: Add `related_papers` entry structure to the "List field structures" documentation**

In the same file, after the `venue.candidates` structure block (around line 296), add:

````markdown
# Each entry in related_papers[] (added by init or refresh):
related_papers:
  - path: "~/github/path/to/related-project"
    rel: "extends | extended-by | implements | implemented-by | companion | series | merged-into | supersedes"
    label: "One-line description of the relationship"
````

**Step 3: Add schema note for `related_papers`**

In the "Schema notes" section (around line 261), add:

```
- `related_papers[].rel` must be one of: `extends`, `extended-by`, `implements`, `implemented-by`, `companion`, `series`, `merged-into`, `supersedes`
- `related_papers[].path` should be absolute or `~/`-relative
```

**Step 4: Verify**

Run: `head -5 skills/init/SKILL.md` — confirm frontmatter is intact.
Run: `grep -c 'related_papers' skills/init/SKILL.md` — expect 3+ matches.

**Step 5: Commit**

```bash
git add skills/init/SKILL.md
git commit -m "feat(papermill): add related_papers to init schema template"
```

---

### Task 2: Expand init Step 6 to populate `related_papers`

**Files:**
- Modify: `skills/init/SKILL.md:186-259` (Step 6 and the notes-appending section after Step 7)

**Step 1: Rewrite the Step 6 instructions**

Replace lines 197-207 (the paragraph starting "This step is optional" through the "If any are found, mention them" paragraph) with expanded instructions that:

1. Keep the existing freeform question and repo-clue scanning (unchanged).
2. After the user describes relationships, add a new sub-step: structure them into `related_papers` entries. For each relationship mentioned, ask the user to confirm the `rel` type from the vocabulary (`extends`, `companion`, `implements`, etc.) and the path to the related project.
3. Add a repoindex discovery sub-step: if `repoindex` CLI is available (Bash tool: `command -v repoindex`), run the discovery query to find other papermill-tracked repos and present them as candidates.
4. Keep the step optional — if the user says "standalone", leave `related_papers` as `[]`.

Here is the replacement text for the section from "This step is optional" through "is that related work of yours?":

```markdown
This step is optional — if the user says "standalone" or skips it, proceed without adding anything. Do not press for detail.

If the user describes relationships or software, do two things:

1. **Freeform notes**: Note them verbatim for inclusion in the Notes section of `.papermill.md` (Step 7), under a `## Related Work and Software` heading. This preserves context for Claude in future sessions.

2. **Structured entries**: For each relationship the user describes, create a `related_papers` entry. Ask the user to confirm for each:
   - The **path** to the related project (absolute or `~/`-relative).
   - The **relationship type** (`rel`). Present the vocabulary and suggest the best fit:
     - `extends` / `extended-by` — builds on or is built upon
     - `implements` / `implemented-by` — theory ↔ software
     - `companion` — different angle on the same research
     - `series` — part of a numbered series
     - `merged-into` — absorbed into another paper
     - `supersedes` — replaces a previous version
   - A **one-line label** describing the relationship.

   Example interaction:

   > You mentioned this paper extends the foundation paper in `~/github/papers/masked-causes-in-series-systems`. I'll add:
   >
   > ```yaml
   > - path: ~/github/papers/masked-causes-in-series-systems
   >   rel: extends
   >   label: "Foundation paper — general masked-cause framework"
   > ```
   >
   > Does that look right?

### Repoindex discovery (opt-in)

After the manual question, check if `repoindex` is available (Bash tool: `command -v repoindex`). If it is:

1. Query for other papermill-tracked projects:

   ```bash
   repoindex sql "SELECT name, path FROM repos WHERE path IN (SELECT repo_path FROM files WHERE name = '.papermill.md')" --json
   ```

2. Filter out the current project from results.

3. If matches are found, present them:

   > I found **N** other papermill-tracked projects via repoindex:
   >
   > | Project | Path |
   > |---------|------|
   > | masked-causes-in-series-systems | ~/github/papers/masked-causes-in-series-systems |
   > | maskedcauses | ~/github/rlang/maskedcauses |
   > | ... | ... |
   >
   > Are any of these related to this paper? If so, I'll add them to the `related_papers` block.

4. For each confirmed match, ask for `rel` type and label as above.

If `repoindex` is not available or the query fails, skip silently and proceed.

### Repo-clue scanning

Also check for clues already in the repo (Read/Glob/Grep tools):
- CLAUDE.md, README.md for mentions of related papers or packages
- Bibliography for self-citations or references to sibling projects
- DESCRIPTION file (R package), setup.py/pyproject.toml (Python package), or package.json (Node) — these indicate associated software
- CITATION.cff for software DOIs

If any are found, mention them: "I noticed this repo contains a DESCRIPTION file for an R package called `foo` — is the paper about this package? I also see references to [X] in the bibliography — is that related work of yours?"
```

**Step 2: Update the notes-appending section after Step 7**

The existing section (lines 249-259) that appends `## Related Work and Software` to notes stays unchanged — freeform notes are still written. No edit needed here.

**Step 3: Verify**

Run: `grep -n 'repoindex' skills/init/SKILL.md` — expect matches in Step 6.
Run: `grep -n 'related_papers' skills/init/SKILL.md` — expect matches in Step 6 and Step 7.

**Step 4: Commit**

```bash
git add skills/init/SKILL.md
git commit -m "feat(papermill): add repoindex discovery and structured related_papers to init Step 6"
```

---

### Task 3: Add `related_papers` migration to refresh mode

**Files:**
- Modify: `skills/init/SKILL.md:43-52` (Refresh Mode, schema migration)
- Modify: `skills/init/SKILL.md:66-72` (Refresh Mode, fill in missing context)

**Step 1: Add migration case to Refresh Mode Step 1**

In the bulleted list of migration cases (lines 47-52), add after the `review_history` case:

```markdown
- Missing `related_papers` → add as `[]`
```

**Step 2: Expand Refresh Mode Step 3 — fill in missing context**

In the "Fill in missing context" section (line 66-72), add a new bullet after the existing ones:

```markdown
- **Related papers (Step 6)**: If `related_papers` is empty or missing, run the repoindex discovery query (if `repoindex` is available) and present any papermill-tracked projects found. Also re-ask the Step 6 question about related work and software. If `related_papers` is already populated, still offer repoindex discovery to catch newly-initialized projects: "You have N related papers linked. Want me to check for any new papermill-tracked projects?"
```

**Step 3: Verify**

Run: `grep -c 'related_papers' skills/init/SKILL.md` — expect 5+ matches now (schema, migration, context fill, Step 6, Step 7).

**Step 4: Commit**

```bash
git add skills/init/SKILL.md
git commit -m "feat(papermill): add related_papers migration to init refresh mode"
```

---

### Task 4: Add Related Papers section to status dashboard

**Files:**
- Modify: `skills/status/SKILL.md:86-91` (between Venue section and Step 4)

**Step 1: Add the Related Papers section**

After the Venue section (line 90: "If `venue.candidates` has entries, list them as bullet points.") and before Step 4 (line 92: "## Step 4: Suggest the next action"), insert:

```markdown

### Related Papers

If `related_papers` contains entries, display a markdown table:

| Project | Relationship | Description |
|---------|-------------|-------------|
| ... | ... | ... |

Where **Project** is the last path component of `path` (e.g., `masked-causes-in-series-systems`), **Relationship** is the `rel` value, and **Description** is the `label`.

If the `related_papers` list is empty or missing, show: "None linked. Run `/papermill:init` with refresh to discover related projects."
```

**Step 2: Verify**

Run: `grep -n 'Related Papers' skills/status/SKILL.md` — expect 1 match.
Run: `head -5 skills/status/SKILL.md` — confirm frontmatter intact.

**Step 3: Commit**

```bash
git add skills/status/SKILL.md
git commit -m "feat(papermill): add Related Papers section to status dashboard"
```

---

### Task 5: Bump plugin version and validate

**Files:**
- Modify: `.claude-plugin/plugin.json` (version bump)

**Step 1: Bump version**

Update the version in `.claude-plugin/plugin.json` from current to next minor (e.g., `0.2.0` → `0.3.0`).

**Step 2: Run plugin validation**

From the `papermill/` directory:

```bash
# Skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ commands/ | sort -u | while read ref; do
  resolved="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$resolved" ] || echo "BROKEN: $ref"
done
```

Expected: All skills show valid frontmatter. No BROKEN references.

**Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore(papermill): bump version to 0.3.0 for cross-paper awareness"
```
