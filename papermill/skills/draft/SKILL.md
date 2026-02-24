---
name: draft
description: >-
  This skill should be used when the user asks to "draft my paper",
  "write the paper", "bootstrap a draft", "generate a manuscript",
  "write the first draft", "create a paper draft", or needs to produce
  a full or partial manuscript draft. Launches a multi-agent writing
  system with specialist writers for literature, formal content,
  methodology, and results, orchestrated by a lead author agent.
  Produces a manuscript draft and section-level artifacts in
  .papermill/drafts/. Updates .papermill/state.md.
---

# Multi-Agent Paper Drafting

Launch a multi-agent system to draft a research paper. The writing system uses specialist writers for different content types (related work, mathematical content, methodology, results), coordinated by a lead author who plans the paper, integrates sections, and writes the bookend sections (abstract, introduction, conclusion).

## Step 1: Read Context

Read `.papermill/state.md` (Read tool) for:
- **Thesis**: The central claim and novelty (required — the draft serves the thesis)
- **Outline**: Section structure (strongly recommended — guides section assignment)
- **Venue**: Target venue and format
- **Prior art**: Key references and gaps
- **Experiments**: Any registered experiments and their status
- **Format**: Paper format (latex, markdown, rmarkdown)

If `.papermill/state.md` does not exist, warn the user:

> I can draft without a state file, but results will be much better if you first run:
> 1. `/papermill:init` — to set up the project
> 2. `/papermill:thesis` — to crystallize the central claim
> 3. `/papermill:outline` — to design the paper structure
>
> Want to proceed anyway, or set up the project first?

If no **outline** exists but a thesis does, the writer orchestrator will create an outline as its first step — but an author-approved outline produces better results.

## Step 2: Identify Existing Content

Scan the project for existing materials:

1. **Manuscript files** (Glob: `*.tex`, `*.md`, `*.Rmd`) — is there already a partial draft?
2. **Bibliography** (Glob: `*.bib`) — existing references
3. **Code and data** (Glob: `code/`, `scripts/`, `data/`, `results/`) — evidence to incorporate
4. **Figures** (Glob: `images/`, `figures/`, `fig/`, `*.png`, `*.pdf` in paper directories)

Summarize what exists to the user:

> **Project inventory:**
> - Thesis: [yes/no — quote if yes]
> - Outline: [yes/no — summarize sections if yes]
> - Existing draft: [yes/no — describe what exists]
> - Bibliography: [N entries in file.bib]
> - Code/data: [brief description]
> - Figures: [N figures available]

## Step 3: Determine Scope

Ask the user what they want drafted:

> I can draft:
> 1. **Full paper** — all sections from abstract to conclusion
> 2. **Specific sections** — choose which sections to write
> 3. **Extension** — add new sections/content to an existing draft
>
> Which approach? And is there anything specific I should know about the paper's direction?

If the user chooses specific sections, note which ones. If they choose extension, identify what already exists and what needs adding.

## Step 4: Launch the Writer Orchestrator

Launch the **writer** agent (Task tool with `subagent_type: "papermill:writer"`).

Pass the agent:
- Path to `.papermill/state.md` (if it exists)
- Paths to existing manuscript files
- Paths to bibliography, code, data, and figures
- The drafting scope (full paper / specific sections / extension)
- Any user preferences or instructions about direction
- The thesis statement and target venue (if known)

The agent will:
1. Read all context and produce a comprehension summary
2. Create a writing plan with section assignments
3. Spawn literature scouts in parallel for field context
4. Spawn specialist writers in parallel for assigned sections
5. Integrate section drafts into a unified manuscript
6. Write bookend sections (abstract, introduction, conclusion)
7. Verify the manuscript builds cleanly
8. Write the manuscript and section artifacts to the project

## Step 5: Present Results

After the agent completes, read the manuscript file (Read tool).

Present a summary to the user:

> **Draft Complete**
>
> **Manuscript**: [path to main file]
> **Sections drafted**: [list of sections with specialist who wrote each]
> **Word/page count**: [approximate]
> **Build status**: [compiles cleanly / has N warnings / needs fixes]
>
> **Section drafts and writing plan**: `.papermill/drafts/YYYY-MM-DD/`
>
> The draft is a starting point, not a final product. Key areas to review:
> 1. [Most important thing to check — e.g., "Proof in Section 4 may need verification"]
> 2. [Second priority — e.g., "Results section has placeholders for experimental data"]
> 3. [Third priority — e.g., "Related work positioning could be sharpened"]

Then ask: "Would you like to review specific sections, or run `/papermill:review` for a systematic evaluation?"

## Step 6: Update State File

Update `.papermill/state.md` (Edit tool):

- Set `stage` to `drafting` or `draft-complete`
- Append a timestamped note documenting the draft:

```
- YYYY-MM-DD (draft): Multi-agent draft complete. Sections: [list]. Specialists used: [list]. Placeholders: [count if any].
```

## Step 7: Suggest Next Steps

Based on the draft's state, suggest the most relevant next step:

- **Draft has placeholders** (missing data/results) → "Run experiments to fill the placeholders, then re-draft those sections."
- **Draft is complete but unreviewed** → `/papermill:review` for systematic multi-agent evaluation
- **Draft needs specific section work** → "You can re-run `/papermill:draft` targeting specific sections, or edit directly."
- **Draft is near-complete** → `/papermill:polish` for pre-submission preparation
- **Proofs need verification** → `/papermill:proof` to check mathematical content
