# Multi-Work Universe Support

**Date**: 2026-03-10
**Status**: Design
**Scope**: Plugin-wide (config, hooks, agents, commands, skills)

## Motivation

Worldsmith currently assumes **one repo = one work = one manuscript**. This model breaks when a universe contains multiple works: a novel and its short story spin-offs, a novella and a planned short story collection, or a series of related novels in the same repo.

Real projects that need this today:

| Repo | Universe | Shared Lore | Works |
|------|----------|-------------|-------|
| `the-policy` | Policy-verse | `lore/` (8 docs + subdirs) | Novel (26 chapters in `chapters/`), "Hemorrhagic" short story (planned, `stories/hemorrhagic/`) |
| `vaelyndra` | Vaelyndra | `docs/` (7 docs) | Novella (12 chapters), short story collection (planned) |

The pattern: **shared canonical lore, separate manuscripts**. A short story and its parent novel must be auditable independently but verified against the same timeline, characters, and world facts.

### What breaks without this

1. **`/worldsmith:review`** globs `chapters/` or `manuscript/` for manuscript files. It would never discover `stories/hemorrhagic/*.tex`.
2. **Detection script** reports manuscript count from first matching directory (`chapters/` or `manuscript/`). Misses satellite works entirely.
3. **Review agents** receive `<manuscript>` scoped to the primary work. No way to say "review just the short story."
4. **`/worldsmith:check`** runs diagnostics against the primary manuscript only.
5. **Writer agent** outputs to `chapters/` by default. No awareness of where a spin-off's manuscript lives.
6. **Review report paths** (`.worldsmith/reviews/YYYY-MM-DD/`) don't distinguish which work was reviewed.

### What already works without changes

- **Cliche detection hook** fires on any Write/Edit to `.tex`/`.md` files regardless of directory. Works.
- **Propagation reminder hook** fires on doc or manuscript edits. Works (it identifies files by directory name, and `stories/` would need to be added to the manuscript directory list, but that's a one-line fix).
- **Lore sharing** is automatic since both works live in the same repo and reference the same `lore/` or `docs/` directory.
- **Canonical hierarchy** is universe-level, not work-level. No change needed.

## Design

### 1. Project Configuration: `.worldsmith/project.yaml`

New optional file. If absent, worldsmith behaves exactly as today (single-work inference). If present, it defines the universe and its works.

```yaml
# .worldsmith/project.yaml
universe: the-policy

lore: lore/          # Path to shared canonical docs (relative to repo root)

works:
  - name: The Policy
    type: novel
    manuscript: chapters/
    lore: docs/the-policy/    # Optional: work-specific lore (characters, locations unique to this novel)
    master: The_Policy.tex    # Optional: LaTeX master file
    file_types: [tex]         # What extensions to glob for manuscript files

  - name: Hemorrhagic
    type: short-story
    manuscript: stories/hemorrhagic/
    lore: docs/hemorrhagic/   # Optional: work-specific lore
    file_types: [tex]
```

**Design decisions:**

- **`universe`**: A string identifier. Purely informational for now (displayed in detection output, used in review reports). Could later enable cross-repo universe references.
- **`lore`**: Explicit path to the shared canonical doc directory. Replaces the current `docs/` vs `lore/` inference.
- **`works`**: Ordered list. First entry is the "primary" work (used as default when no work is specified).
- **`type`**: One of `novel`, `novella`, `short-story`, `collection`. Informational; could later drive type-specific review behavior (e.g., collections need per-story structure auditing).
- **`manuscript`**: Directory path relative to repo root. This is what agents glob for manuscript files.
- **`master`**: Optional. The LaTeX/Markdown master file that `\input{}`s or references chapter files. Useful for build commands.
- **`file_types`**: What file extensions constitute manuscript files in this work's directory. Defaults to `[md, tex, txt]`.
- **per-work `lore`**: Optional. Directory path for work-specific canonical docs (characters unique to this story, locations only relevant to this novella). When present, agents read both the shared `lore` directory and the work's local `lore` directory. Shared lore takes precedence over local lore when they conflict.

**Backward compatibility:** If `project.yaml` does not exist, worldsmith infers a single anonymous work from the first matching directory (`chapters/`, `manuscript/`). All existing projects work unchanged.

### 2. Detection Script Update

**File:** `hooks/scripts/detect-worldsmith-project.sh`

**Changes:**

1. After confirming `.worldsmith/` exists, check for `.worldsmith/project.yaml`.
2. If found, parse it (bash yaml parsing via grep/sed for this simple structure, or delegate to a small python script).
3. Report universe name and all works with their types and manuscript paths.
4. Export `WORLDSMITH_WORKS` as a colon-separated list of work names (for other hooks to consume).
5. If not found, fall through to existing inference logic (no behavior change).

**Updated output example:**

```
Worldsmith project detected.

Universe: the-policy
Lore directory: lore/
Documents found:
  - characters.md (235 lines)
  - timeline.md (88 lines)
  ...

Works:
  - The Policy [novel] — chapters/ (26 files)
  - Hemorrhagic [short-story] — stories/hemorrhagic/ (3 files)

This is a worldsmith project with 2 works sharing lore/.
```

### 3. Propagation Reminder Update

**File:** `hooks/scripts/propagation-reminder.sh`

**Change:** Add `stories/` to the list of directories classified as manuscript directories (alongside `chapters/`, `manuscript/`, `scenes/`). This is a one-line addition.

### 4. Command Updates

#### `/worldsmith:review [work-name | scope]`

**File:** `commands/review.md`

**Changes:**

- Parse `$ARGUMENTS` for a work name. If a recognized work name is found, scope the review to that work's manuscript directory.
- If no work name is specified and multiple works exist, review the **primary work** (first in `project.yaml`) and note this in the report.
- The argument can combine work name and scope: `/worldsmith:review Hemorrhagic chapters 1-3` or just `/worldsmith:review Hemorrhagic`.
- Pass the resolved manuscript path to the reviewer agent.

#### `/worldsmith:check [work-name | scope]`

**File:** `commands/check.md`

**Changes:**

- Same argument parsing as review.
- Consistency diagnostics always check against shared lore regardless of which work is scoped.
- Editorial/prose diagnostics scope to the specified work's manuscript files.
- Status diagnostics report all works.
- Cross-reference diagnostics check both within the scoped work and between works (e.g., does a character mentioned in the short story match their entry in the novel?).

#### `/worldsmith:change [description]`

**File:** `commands/change.md`

**Changes:** Minimal. The change command operates on canonical docs (lore) which are shared. When propagating a lore change to manuscript, it should check all works for affected passages, not just the primary work. Add a step: "For each work in `project.yaml`, grep its manuscript directory for references to the changed fact."

### 5. Agent Updates

#### Reviewer Orchestrator (`agents/reviewer.md`)

**Changes to Phase 1 (Comprehension):**

- Read `.worldsmith/project.yaml` if it exists.
- Identify which work is being reviewed (from the prompt or default to primary).
- In the structured understanding, add: **Work being reviewed** — name, type, manuscript path.
- Read only the scoped work's manuscript files, but read ALL shared lore docs.

**Changes to Phase 6 (Write Report):**

- Include work name in report directory: `.worldsmith/reviews/YYYY-MM-DD/[work-name]/` (or `.worldsmith/reviews/YYYY-MM-DD/` if single-work project for backward compatibility).
- Report header includes: `**Work**: [name] ([type])`.

#### Writer Orchestrator (`agents/writer.md`)

**Changes to Phase 1 (Comprehension):**

- Same project.yaml awareness.
- Determine which work is being written for (from the prompt or ask).
- Read that work's existing manuscript for continuity context.
- Read shared lore for canonical facts.

**Changes to Phase 7 (Output):**

- Write manuscript files to the correct work's directory, not hardcoded `chapters/`.

#### Specialist Agents (consistency-auditor, craft-auditor, voice-auditor, structure-auditor)

**No structural changes needed.** They receive `<manuscript>` via XML tags from the orchestrator. The orchestrator is responsible for scoping the manuscript content correctly. The specialists just audit what they're given.

Similarly, **scene-writer, lore-writer, character-developer** receive assignments from the writer orchestrator. No changes needed.

### 6. Methodology Skill Update

**File:** `skills/worldsmith-methodology/SKILL.md`

**Add a section:**

```markdown
## Multi-Work Projects

A universe can contain multiple works sharing the same canonical docs.
Configuration lives in `.worldsmith/project.yaml`.

When working in a multi-work project:

- **Lore is shared.** All works draw from the same canonical docs. A
  change to a character entry affects every work that character appears in.
- **Manuscripts are scoped.** Each work has its own manuscript directory.
  Reviews, diagnostics, and writing target one work at a time.
- **Propagation crosses works.** When a canonical doc changes, check ALL
  works' manuscripts for affected passages, not just the one you're
  currently editing.
- **Reviews are per-work.** A review of the short story does not review
  the novel. But consistency checks verify against shared lore.
```

### 7. Init-World Update

**File:** `commands/init-world.md`

**Changes:**

When scaffolding a new project or adopting an existing one:

- Ask whether this is a single-work or multi-work project.
- If multi-work, generate `project.yaml` with the declared works.
- If single-work, skip `project.yaml` (existing inference is sufficient).
- When adopting an existing project that already has multiple manuscript directories (e.g., both `chapters/` and `stories/`), detect this and suggest creating `project.yaml`.

## Implementation Order

1. **`project.yaml` schema and detection script** — Foundation. Everything else depends on this. Parse the config, export work metadata.
2. **Propagation reminder one-liner** — Add `stories/` to manuscript directory list. Trivial.
3. **Command argument parsing** — `/worldsmith:review` and `/worldsmith:check` accept work names.
4. **Reviewer orchestrator scoping** — Phase 1 reads project.yaml, scopes manuscript glob. Phase 6 includes work name in report path.
5. **Writer orchestrator scoping** — Phase 1 reads project.yaml, Phase 7 writes to correct directory.
6. **Methodology skill update** — Add multi-work section.
7. **Init-world update** — Multi-work scaffolding option.

Steps 1-2 are prerequisite. Steps 3-5 can be done in parallel. Steps 6-7 are documentation and can be done anytime.

## What This Does NOT Do

- **Cross-repo universe sharing.** All works must be in the same repo. A sequel novel in a separate repo would need its own lore copy (or symlinks). This is a future concern; no current project needs it.
- **Per-work lore overrides of shared lore.** Works can have local lore directories for work-specific docs, but local lore cannot override shared lore. A short story can't override the universe's timeline. Shared lore > local lore > manuscript.
- **Automatic work detection.** Worldsmith does not scan for manuscript directories and auto-populate `project.yaml`. The config is explicit. This prevents false positives and respects the user's organizational intent.
- **Build system integration.** `project.yaml` has a `master` field but worldsmith doesn't compile manuscripts. Build scripts are the user's responsibility (see `kdp/build.sh` in the-policy for an example).

## Testing

- Existing single-work projects (no `project.yaml`) must behave identically. Zero regression.
- Create a test project with `project.yaml` containing two works. Verify:
  - Detection script reports both works.
  - `/worldsmith:review WorkName` scopes correctly.
  - `/worldsmith:check` consistency mode checks shared lore.
  - Writer outputs to the correct manuscript directory.
  - Review reports land in work-scoped subdirectory.
