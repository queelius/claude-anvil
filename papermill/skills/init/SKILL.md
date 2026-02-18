---
name: init
description: >-
  This skill should be used when the user asks to "initialize a paper",
  "start a new paper project", "set up papermill", "onboard this repo",
  "refresh papermill", "update papermill state", or needs to create or
  update the .papermill.md state file. On new repos: discovers structure,
  infers format, gathers author info, creates state file. On existing
  repos: offers refresh mode that adds missing schema fields and new
  context without overwriting existing data.
---

# Papermill Init

Initialize a paper repository for use with papermill. Follow every step below in order. Be thorough in discovery but conservative in action -- never overwrite existing state.

---

## Step 1: Check for Existing State

Look for a file called `.papermill.md` in the repository root (Read tool).

- **If `.papermill.md` does not exist**: Continue to Step 2 (fresh initialization).
- **If `.papermill.md` exists**: Read it, display a summary (title, stage, format, authors), then offer refresh:

  > This repository is already initialized. Current state is shown above.
  >
  > Would you like to **refresh** the state file? This will:
  > - Add any missing YAML fields from the current schema (preserving all existing data)
  > - Re-discover repo structure for new files or assets
  > - Ask about anything not yet captured (e.g., related papers)
  >
  > Nothing will be overwritten or removed. Or use `/papermill:status` for a quick look.

  If the user declines refresh, stop here. If they accept, proceed to **Refresh Mode** below.

---

## Refresh Mode

Refresh is **additive only** -- it fills gaps without touching existing data. Run through each check below, report what was found, and apply changes only with user confirmation.

### 1. Schema migration

Compare the existing YAML frontmatter against the current schema (shown in Step 7). For each field in the schema that is missing from the file, add it with its default value. Common cases:

- Missing `thesis` block → add with empty `claim`, `novelty`, `refined: null`
- Missing `prior_art` block → add with empty defaults
- Missing `experiments` → add as `[]`
- Missing `venue` block → add with `target: null`, `candidates: []`
- Missing `review_history` → add as `[]`
- Missing `authors[].orcid` → add as `""`

Report what was added: "Added N missing fields to bring the state file up to the current schema." If nothing is missing, say so.

### 2. Re-discover repo structure

Run the same discovery as Step 2 (format detection, asset scan). Compare against what the state file already records. Report any new findings:

- New `.bib` files since initialization
- New code directories (`research/`, `scripts/`, etc.)
- Format change (e.g., repo now has `.Rmd` files but format says `latex`)

For format mismatches, ask the user: "The state file says `latex` but I also found `.Rmd` files. Should I update the format?" Only update with confirmation.

### 3. Fill in missing context

Check for content that the current init flow captures but older versions may not have asked about:

- **Related work and software (Step 6)**: If the Notes section does not contain a `## Related Work` heading, run the related-work question from Step 6. If the user provides context, append it to the notes.
- **Author ORCID**: If `authors[].orcid` is empty, check `deets` and offer to fill it in.
- **Title**: If `title` is empty or looks like a placeholder, re-run title inference from Step 4.

### 4. Report and finish

Display what changed:

> **Refresh complete.**
>
> | Action | Details |
> |--------|---------|
> | Schema fields added | N (list them) |
> | New assets discovered | (list or "none") |
> | Context updated | (what was added or "nothing new") |

Append a timestamped note to the markdown body:

```
- YYYY-MM-DD (init refresh): Refreshed state file. [brief summary of changes].
```

Do NOT modify existing field values (stage, thesis, prior_art content, experiments, reviews, venue selections) unless the user explicitly asks. Those are managed by their respective skills.

---

## Step 2: Discover Repository Structure

Search the repository to understand what kind of paper project this is (Glob tool). Look for all of the following and report what you find:

### Format detection (check in this order)

1. **LaTeX**: Search for `*.tex` files (Glob tool). If found, set `format: latex`.
2. **R Markdown**: Search for `*.Rmd` files (Glob tool). If found, set `format: rmarkdown`.
3. **Markdown**: Search for `paper.md`, `manuscript.md`, or any markdown file that looks like a JOSS-style paper (contains `title:` in YAML frontmatter) (Glob/Grep tools). If found, set `format: markdown`.
4. If none of the above are found, ask the user what format they plan to use. Default to `format: latex` if they are unsure.

### Additional assets

- `*.bib` files (bibliography)
- `research/` or `code/` or `scripts/` or `analysis/` directories (computational work)
- `CITATION.cff` (citation metadata)
- `figures/` or `img/` or `images/` directories (graphics)
- `Makefile`, `latexmkrc`, or build configuration files
- `README.md` or `CLAUDE.md` (project documentation)

Report a brief inventory of what was found, for example:

> **Discovered structure:**
> - Format: latex (found `paper/main.tex`)
> - Bibliography: `paper/references.bib` (12 entries)
> - Research code: `research/` directory present
> - Figures: `figures/` directory with 3 PDF files
> - Build system: `latexmk` configuration found

---

## Step 3: Get Author Information

Try to obtain the primary author's identity using the `deets` CLI tool, which manages personal metadata (Bash tool).

Run these commands (each may fail if deets is not installed -- that is fine):

```bash
deets get identity.name
deets get contact.email
deets get academic.orcid
```

- **If `deets` is available** and returns values: Use them as the primary author. Show the user what was found and ask for confirmation.
- **If `deets` is not available** or returns errors: Ask the user directly:
  > I could not find author information via `deets`. Please provide:
  > 1. Your full name (as it appears on papers)
  > 2. Your email address
  > 3. Your ORCID (optional, e.g., 0000-0002-1234-5678)

Also check for author info in existing files (Read/Grep/Bash tools):
- `\author{}` blocks in `.tex` files
- `CITATION.cff` author fields
- Git config (`git config user.name`, `git config user.email`)

If multiple sources conflict, prefer: deets > tex file > CITATION.cff > git config. Always confirm with the user.

---

## Step 4: Infer the Paper Title

Attempt to extract the title automatically (Grep/Read tools):

- **LaTeX**: Search for `\title{...}` in `.tex` files. Handle multiline titles and macro-containing titles.
- **Markdown/R Markdown**: Look for the first `# heading` or a `title:` field in YAML frontmatter.
- **CITATION.cff**: Check the `title:` field.

If a title is found, show it to the user and ask for confirmation. If no title is found, ask:

> I could not detect a paper title. What is the working title for this paper?

---

## Step 5: Infer the Current Stage

Determine the project stage based on what exists in the repository:

| Condition | Stage |
|-----------|-------|
| No paper content files exist (empty or new repo) | `idea` |
| Only outline/notes exist, minimal prose | `outlining` |
| Substantial paper content exists (multiple sections with prose) | `drafting` |
| Paper appears complete with abstract, conclusion, references | `review` |

Use your judgment. When in doubt, default to `drafting` if paper content exists, or `idea` if the repo is new or nearly empty. Tell the user what stage you inferred and why.

---

## Step 6: Ask About Related Work and Software

Ask the user whether this paper connects to any of their other projects or software:

> Is this paper related to any of your other work? For example:
> - Part of a series (e.g., "Part II of...")
> - Builds on a foundation paper you wrote
> - A companion covering a different angle of the same research
> - Has an associated software package (CRAN, PyPI, GitHub, etc.)
> - Uses results or software from another project
>
> If so, briefly describe the relationships. If not, just say "standalone" and we'll move on.

This step is optional — if the user says "standalone" or skips it, proceed without adding anything. Do not press for detail.

If the user describes relationships or software, note them verbatim for inclusion in the Notes section of `.papermill.md` (Step 7). Do not create structured YAML fields for this — freeform notes are sufficient. Claude Code will read these notes in future sessions and use them as context for thesis refinement, prior-art surveys, review, and polish (code availability statements, DOI references).

Also check for clues already in the repo (Read/Glob/Grep tools):
- CLAUDE.md, README.md for mentions of related papers or packages
- Bibliography for self-citations or references to sibling projects
- DESCRIPTION file (R package), setup.py/pyproject.toml (Python package), or package.json (Node) — these indicate associated software
- CITATION.cff for software DOIs

If any are found, mention them: "I noticed this repo contains a DESCRIPTION file for an R package called `foo` — is the paper about this package? I also see references to [X] in the bibliography — is that related work of yours?"

---

## Step 7: Create `.papermill.md`

Create the file `.papermill.md` in the repository root with the following structure (Write tool). Fill in all values gathered from the previous steps. Use the exact YAML schema shown below.

```markdown
---
title: "<title from Step 4>"
stage: <stage from Step 5>
format: <format from Step 2>
authors:
  - name: "<name from Step 3>"
    email: "<email from Step 3>"
    orcid: "<orcid from Step 3, or empty string if not available>"

thesis:
  claim: ""
  novelty: ""
  refined: null

prior_art:
  last_survey: null
  key_references: []
  gaps: ""

experiments: []

venue:
  target: null
  candidates: []

review_history: []
---

## Notes

Initialized by papermill on <today's date in YYYY-MM-DD format>.
```

If the user described related papers or software in Step 6, append them to the Notes section as a natural-language entry:

```markdown
## Related Work and Software

<whatever the user said, in their words -- e.g., "This is Part II of the
reliability series. Part I is in ../reliability-foundations/ and covers the
asymptotic theory. This paper extends those results to finite samples.
The R package `reliabilitytools` on CRAN implements the methods from both
papers. DOI: 10.5281/zenodo.XXXXXXX">
```

**Schema notes:**
- `stage` must be one of: `idea`, `thesis`, `literature`, `outlining`, `drafting`, `review`, `submission`
- `format` must be one of: `latex`, `markdown`, `rmarkdown`
- `orcid` should be the bare identifier (e.g., `0000-0002-1234-5678`), not a URL
- `thesis.refined` starts as `null` and is set to `true` by the thesis skill
- `prior_art.last_survey` is a date string (`YYYY-MM-DD`) or `null`
- Leave empty fields as empty strings `""`, not `null`, unless the schema above specifies `null`

**List field structures** (populated by their respective skills — empty at init):

```yaml
# Each entry in experiments[] (added by experiment/simulation skills):
experiments:
  - name: "descriptive-name"
    type: "simulation | benchmark | case-study | ablation"
    hypothesis: "Expected outcome in one sentence"
    status: "planned | running | completed | failed"
    script: "path/to/script.R"
    last_run: null  # YYYY-MM-DD when last executed

# Each entry in review_history[] (added by review skill):
review_history:
  - date: "YYYY-MM-DD"
    type: "self-review"
    findings_major: 0
    findings_minor: 0
    recommendation: "ready | minor-revision | major-revision | not-ready"
    notes: "Brief summary of key findings"

# Each entry in venue.candidates[] (added by venue skill):
venue:
  candidates:
    - name: "Journal or Conference Name"
      fit: "high | good | moderate"
      deadline: "YYYY-MM-DD or rolling"
```

---

## Step 8: Report and Suggest Next Steps

After creating `.papermill.md`, display a summary:

> **Papermill initialized.**
>
> | Field   | Value              |
> |---------|--------------------|
> | Title   | <title>            |
> | Stage   | <stage>            |
> | Format  | <format>           |
> | Author  | <name> (<email>)   |
>
> State file: `.papermill.md`

Then suggest the next skill based on the inferred stage:

| Stage | Suggestion |
|-------|------------|
| `idea` | "Run `/papermill:thesis` to develop your core claim and novelty statement." |
| `thesis` | "Run `/papermill:thesis` to refine your thesis, or `/papermill:prior-art` to survey related work." |
| `literature` | "Run `/papermill:prior-art` to survey related work and identify gaps." |
| `outlining` | "Run `/papermill:outline` to structure your paper sections." |
| `drafting` | "Run `/papermill:thesis` to articulate your core claim, or `/papermill:status` to review your progress." |
| `review` | "Run `/papermill:review` to get feedback on your draft." |
| `submission` | "Run `/papermill:status` to review submission readiness." |

---

## Error Handling

- If the repository root cannot be determined, ask the user which directory to use.
- If file creation fails due to permissions, report the error clearly.
- Never silently skip steps. If any inference fails, ask the user explicitly.
- If the user interrupts or provides corrections during any step, incorporate them before proceeding.
