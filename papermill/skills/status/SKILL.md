---
name: status
description: >-
  This skill should be used when the user asks to "show paper status",
  "where am I on this paper", "what's the state of my paper", "papermill
  dashboard", or needs orientation on a paper project. Reads .papermill.md
  and presents a read-only dashboard showing stage, thesis, experiments,
  review history, venue, and suggested next actions.
---

# Status Dashboard

Present a concise project status dashboard for an academic paper managed by Papermill. This skill is **read-only** -- it does not modify any files.

## Step 1: Read the project file

Read `.papermill.md` from the repository root (Read tool).

If the file does not exist, stop and display:

> No `.papermill.md` found in this repository. Run `/papermill:init` to set up Papermill for this project.

Do not proceed further if the file is missing.

## Step 2: Parse the frontmatter and body

The file has YAML frontmatter (between `---` delimiters) and a markdown body below it. Parse both. The frontmatter contains structured project metadata. The body contains freeform notes and activity logs.

## Step 3: Present the dashboard

Display a dashboard with the following sections, using the exact headers shown. For any section where data is absent or empty in the frontmatter, show the fallback text indicated.

### Stage

Show the current `stage` value with a brief one-line description:

- **idea** -- Exploring research questions and directions
- **thesis** -- Refining the central claim and novelty
- **literature** -- Surveying prior work and identifying gaps
- **outlining** -- Structuring the argument and paper skeleton
- **drafting** -- Writing sections and producing content
- **review** -- Incorporating feedback and revising
- **submission** -- Final editing, formatting, and submission prep

If no stage is set, show: "No stage set. Run `/papermill:init` to configure."

### Thesis

Show the `thesis.claim` and `thesis.novelty` fields. Format as:

> **Claim:** [claim text]
> **Novelty:** [novelty text]

If the thesis fields are empty or not defined, show: "Not yet defined. Run `/papermill:thesis` to develop your central claim."

### Prior Art

Show a summary from the `prior_art` fields:

- **Key references**: count of entries in `key_references` (e.g., "12 key references")
- **Last survey date**: the `last_survey` date
- **Identified gaps**: the `gaps` text

If no prior art data exists, show: "No survey yet. Run `/papermill:prior-art` to begin."

### Experiments

If `experiments` contains entries, display a markdown table:

| Name | Type | Status | Last Run |
|------|------|--------|----------|
| ... | ... | ... | ... |

If the experiments list is empty, show: "None registered."

### Reviews

Show a summary from `review_history`:

- **Count**: number of reviews conducted
- **Last review date**: when the most recent review occurred
- **Unresolved findings**: count or brief summary of open issues

If no reviews exist, show: "No reviews yet."

### Venue

Show the `venue.target` field. If not set, show: "Not yet selected."

If `venue.candidates` has entries, list them as bullet points.

## Step 4: Suggest the next action

Based on the current project state, suggest exactly one next skill to run. Evaluate the conditions in order and use the first match:

1. If the thesis is not defined or empty --> "Consider running `/papermill:thesis` to define your research claim."
2. If the thesis is defined but no prior art data exists --> "Consider running `/papermill:prior-art` to survey related work."
3. If the markdown body does not contain a `## Outline` section and the stage is before `outlining` --> "Consider running `/papermill:outline` to structure the paper."
4. If the stage is `drafting` and there is written content --> "Consider running `/papermill:review` to get feedback on the current draft."
5. If reviews have been conducted and there are unresolved findings --> "Consider running `/papermill:review` to address open findings."
6. If reviews are done with no unresolved findings --> "Consider running `/papermill:polish` for final editing, or `/papermill:venue` to evaluate target venues."
7. Otherwise --> "The project is in good shape. Continue working on the current stage."

Display this under a **Suggested next step** heading.

## Step 5: Show recent activity

Read the last 10 non-empty, non-heading lines from the markdown body of `.papermill.md` (the content below the frontmatter). These typically contain timestamped notes or activity logs.

Display them under a **Recent activity** heading. If the body is empty or contains no notes, show: "No activity logged yet."

## Formatting rules

- Use plain markdown throughout. No HTML.
- Keep the dashboard compact. Each section should be a few lines at most.
- Do not editorialize or add commentary beyond what is specified above.
- Do not modify `.papermill.md` or any other file. This skill is read-only.
