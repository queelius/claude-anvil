# OSF Preprint Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an OSF preprint submission skill to pub-pipeline that uploads compiled PDFs to MetaArXiv or OSF Preprints with auto-extracted LaTeX metadata.

**Architecture:** Pure skill (Markdown only, no scripts). Claude parses LaTeX for metadata and makes 3 curl calls against the OSF API v2. Fits the existing pub-pipeline routing pattern.

**Tech Stack:** Markdown (skill + command), OSF API v2, curl, WaterButler

---

### Task 1: Create the OSF preprint skill

**Files:**
- Create: `skills/osf-preprint/SKILL.md`

**Step 1: Create the skill directory**

```bash
mkdir -p skills/osf-preprint
```

**Step 2: Write the skill file**

Create `skills/osf-preprint/SKILL.md` with the following exact content:

````markdown
---
name: osf-preprint
description: "This skill should be used when the user asks to \"upload preprint\", \"submit to OSF\", \"MetaArXiv\", \"preprint submission\", \"publish preprint\", \"OSF preprint\", \"upload to MetaArXiv\", or mentions preprint submission to OSF or MetaArXiv. It guides the complete workflow: detecting the paper, extracting metadata from LaTeX, uploading the PDF, and creating the preprint on OSF."
---

# OSF Preprint Submission

Guide the complete workflow for submitting a preprint to MetaArXiv or OSF Preprints via the OSF API v2. This skill detects the paper, extracts metadata from LaTeX source, uploads the compiled PDF, and creates the preprint.

## Prerequisites

- `OSF_TOKEN` environment variable set to an OSF Personal Access Token
- A compiled PDF of the paper
- `curl` available on the system

## Workflow

### 1. Check Authentication

Verify `OSF_TOKEN` is set (Bash tool):

```bash
[ -n "$OSF_TOKEN" ] && echo "OSF_TOKEN is set" || echo "OSF_TOKEN is NOT set"
```

If not set, instruct the user:
1. Go to https://osf.io/settings/tokens
2. Create a new token with scopes: `osf.full_write`
3. Set it: `export OSF_TOKEN="your-token-here"`
4. For persistence, add to `~/.bashrc` or `~/.zshrc`

Do not proceed until the token is set.

### 2. Locate the Paper

Search for LaTeX source and compiled PDF (Glob tool):

1. Search for `.tex` files: `**/*.tex` (exclude `archive/`, `deprecated/`)
2. Search for `.pdf` files: `**/*.pdf` (look for `main.pdf`, `paper.pdf`, or match the `.tex` basename)

Common structures to handle:
- `paper/main.tex` → `paper/main.pdf`
- `paper.tex` → `paper.pdf`
- `main.tex` → `main.pdf`

If multiple `.tex` files exist, look for the one containing `\documentclass` to identify the main file. If ambiguous, ask the user.

If no compiled PDF exists, offer to build it (Bash tool):

```bash
cd <paper_dir> && latexmk -pdf <main_tex>
```

### 3. Extract Metadata from LaTeX

Read the main `.tex` file (Read tool) and extract:

| Field | Pattern | Required |
|-------|---------|----------|
| Title | `\title{...}` | Yes |
| Abstract | `\begin{abstract}...\end{abstract}` | Yes |
| Keywords | `\keywords{...}` or `\begin{keywords}...\end{keywords}` | No |
| Authors | `\author{...}` | Yes |

Also extract the GitHub repo URL (Bash tool):

```bash
git remote get-url origin 2>/dev/null
```

Handle nested braces in `\title{}` (e.g., `\title{A {B}rief Title}`). For complex author blocks (e.g., `\author[1]{Name}` with affiliation macros), extract names only and present for confirmation.

If any required field cannot be extracted, ask the user to provide it.

### 4. Choose Provider

Ask the user which preprint provider to use:

| Provider | ID | Description |
|----------|----|-------------|
| MetaArXiv | `metaarxiv` | Interdisciplinary preprints (arXiv alternative) |
| OSF Preprints | `osf` | General OSF preprint server |

Default to MetaArXiv if the user doesn't specify.

### 5. Confirm Metadata

Present all extracted metadata to the user for review:

```
Title: [extracted title]
Abstract: [first 200 chars]...
Keywords: [extracted keywords]
Authors: [extracted authors]
Provider: MetaArXiv / OSF Preprints
GitHub: [repo URL]
PDF: [path to PDF]
```

Ask the user to confirm or edit any field before proceeding. The description field will be the abstract followed by a line with the GitHub repo link.

### 6. Create OSF Project Node

Create a new OSF project to host the preprint (Bash tool):

```bash
curl -s -X POST "https://api.osf.io/v2/nodes/" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "nodes",
      "attributes": {
        "title": "<TITLE>",
        "category": "project",
        "public": true,
        "description": "<ABSTRACT>\n\nSource code: <GITHUB_URL>"
      }
    }
  }'
```

Extract `node_id` from the response: `.data.id`

If the API returns an error, display it and stop. Common errors:
- 401: Token invalid or expired
- 403: Token lacks `osf.full_write` scope

### 7. Upload PDF to Node

Upload the compiled PDF via WaterButler (Bash tool):

```bash
curl -s -X PUT \
  "https://files.osf.io/v1/resources/<NODE_ID>/providers/osfstorage/?kind=file&name=<PDF_FILENAME>" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/pdf" \
  --data-binary @"<PATH_TO_PDF>"
```

Extract `file_id` from the response. The file ID is in the WaterButler response at `.data.id` or `.data.attributes.extra.hashes` path. Parse the response to find the file's OSF ID.

If upload fails with 409 (conflict), the file already exists. Offer to upload a new version or use the existing file.

### 8. Create Preprint

Create the preprint linking the node, file, and provider (Bash tool):

```bash
curl -s -X POST "https://api.osf.io/v2/preprints/" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "preprints",
      "attributes": {
        "title": "<TITLE>",
        "description": "<ABSTRACT>\n\nSource code: <GITHUB_URL>",
        "tags": [<KEYWORDS_AS_JSON_ARRAY>],
        "is_published": false
      },
      "relationships": {
        "node": {
          "data": {
            "type": "nodes",
            "id": "<NODE_ID>"
          }
        },
        "primary_file": {
          "data": {
            "type": "files",
            "id": "<FILE_ID>"
          }
        },
        "provider": {
          "data": {
            "type": "preprint-providers",
            "id": "<PROVIDER_ID>"
          }
        }
      }
    }
  }'
```

Note: `is_published` is set to `false` initially. This creates a draft. The user reviews it on OSF before publishing.

Extract the preprint URL from the response: `.data.links.html`

### 9. Report Results

Display the submission results to the user:

```
Preprint submitted successfully!

  Provider:    MetaArXiv / OSF Preprints
  Title:       [title]
  OSF Node:    https://osf.io/<NODE_ID>
  Preprint:    <PREPRINT_URL>
  Status:      Draft (review on OSF before publishing)

Next steps:
  1. Visit the preprint URL to review metadata and formatting
  2. Add subjects/categories on OSF (cannot be set via API)
  3. Set the license on OSF
  4. Click "Publish" when ready — this assigns a DOI
```

### 10. Load User Config

Read `.claude/pub-pipeline.local.md` if it exists (Read tool). Extract any OSF-specific fields from YAML frontmatter. If the file is missing, inform the user and offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

## Error Handling

| Error | Response |
|-------|----------|
| `OSF_TOKEN` not set | Guide user to create token at https://osf.io/settings/tokens |
| No `.tex` file found | Ask user for paper location |
| No `.pdf` file found | Offer to compile with `latexmk -pdf` |
| API 401/403 | Token invalid or wrong scope — guide user to regenerate |
| API 409 on upload | File exists — offer to update or use existing |
| Metadata extraction fails | Ask user to provide missing fields manually |

## Important Notes

- **Draft by default**: Preprints are created as drafts (`is_published: false`). The user must review and publish on OSF. This prevents accidental publication of unfinished work.

- **Subjects/categories**: OSF preprint subjects (taxonomy) cannot be set via the API easily. The user should add these manually on OSF after submission.

- **License**: Setting the license relationship via API requires knowing the license ID. The user should set this on OSF during review.

- **DOI assignment**: A DOI is assigned only after the preprint is published (not while in draft). The user publishes on OSF to get the DOI.

- **One preprint per node**: Each OSF node can have at most one preprint. Do not reuse an existing node that already has a preprint.

- **Updating a preprint**: To update a published preprint, upload a new version of the PDF file. Do not create a new preprint.

## Reference Files

- **`${CLAUDE_PLUGIN_ROOT}/docs/osf-reference.md`** — OSF API details, WaterButler endpoints, provider IDs, and common troubleshooting
````

**Step 3: Commit**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add skills/osf-preprint/SKILL.md && git commit -m "feat(osf-preprint): add OSF preprint submission skill"
```

---

### Task 2: Create the slash command

**Files:**
- Create: `commands/osf-preprint.md`

**Step 1: Write the command file**

Create `commands/osf-preprint.md` with the following exact content:

```markdown
---
description: "Submit a preprint to MetaArXiv or OSF Preprints"
---
Run the osf-preprint skill: detect paper, extract metadata from LaTeX, upload PDF, and create a preprint on MetaArXiv or OSF Preprints.
```

**Step 2: Commit**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add commands/osf-preprint.md && git commit -m "feat(osf-preprint): add /osf-preprint slash command"
```

---

### Task 3: Update the pub-pipeline router

**Files:**
- Modify: `skills/pub-pipeline/SKILL.md`

**Step 1: Update detection logic table**

In `skills/pub-pipeline/SKILL.md`, add a new row to the detection logic table after the book manuscript row:

| Check | Project Type | Route To |
|-------|-------------|----------|
| `.tex` + `.pdf` without `DESCRIPTION` or `pyproject.toml` | Academic paper | `/osf-preprint` (the `osf-preprint` skill) |

The key distinction: if `.tex` files exist but there's no `DESCRIPTION` (R) or `pyproject.toml` (Python), it's likely an academic paper, not a book manuscript. The router should offer `/osf-preprint` alongside `/kdp-publish` and let the user choose.

**Step 2: Update the detection step**

In Step 1 (Detect project type), add:
- `.tex` + `.pdf` without R/Python indicators → academic paper candidate

**Step 3: Update the supported ecosystems table**

Add a new row:

| **Academic preprints** | `osf-preprint` | `/osf-preprint` |

**Step 4: Commit**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add skills/pub-pipeline/SKILL.md && git commit -m "feat(pub-pipeline): route academic papers to /osf-preprint"
```

---

### Task 4: Create the OSF reference doc

**Files:**
- Create: `docs/osf-reference.md`

**Step 1: Write the reference doc**

Create `docs/osf-reference.md` with OSF API details:

- OSF API v2 base URL: `https://api.osf.io/v2/`
- WaterButler base URL: `https://files.osf.io/v1/`
- Authentication: Bearer token via `OSF_TOKEN`
- Token scopes needed: `osf.full_write`
- Token creation URL: https://osf.io/settings/tokens
- Provider IDs: `metaarxiv`, `osf`
- Rate limits: 100/hr unauthenticated, 10,000/day authenticated
- Common API error codes and their meanings
- JSON:API format requirements (`application/vnd.api+json`)
- WaterButler upload format (PUT with binary body)
- Response parsing: extracting node_id, file_id, preprint URL

**Step 2: Commit**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add docs/osf-reference.md && git commit -m "docs: add OSF API reference for preprint skill"
```

---

### Task 5: Update plugin manifest

**Files:**
- Modify: `.claude-plugin/plugin.json`

**Step 1: Update version and keywords**

Bump the version to `0.4.0` and add `"OSF"`, `"preprint"`, `"MetaArXiv"` to the keywords array.

**Step 2: Commit**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add .claude-plugin/plugin.json && git commit -m "chore: bump version to 0.4.0, add OSF keywords"
```

---

### Task 6: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the command-skill mapping table**

Add a new row:

| `commands/osf-preprint.md` | `skills/osf-preprint/` | Academic preprints |

**Step 2: Update the "What This Is" section**

Add `Academic preprints: OSF / MetaArXiv` to the ecosystem list.

**Step 3: Update the reference docs list**

Add `osf-reference.md` — OSF API details, WaterButler endpoints, provider IDs.

**Step 4: Commit**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add CLAUDE.md && git commit -m "docs: update CLAUDE.md with OSF preprint skill"
```

---

### Task 7: Validate the plugin

**Step 1: Run validation checks**

```bash
cd /home/spinoza/github/alex-claude-plugins/pub-pipeline

# All skill frontmatter has name and description
for f in skills/*/SKILL.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# All command frontmatter has description
for f in commands/*.md; do echo "=== $f ===" && head -5 "$f" && echo; done

# All ${CLAUDE_PLUGIN_ROOT} references point to existing files
grep -roh '\${CLAUDE_PLUGIN_ROOT}/[^`"]*' skills/ | sort -u | while read ref; do
  file="${ref/\$\{CLAUDE_PLUGIN_ROOT\}/\.}"
  [ -f "$file" ] && echo "OK: $ref" || echo "MISSING: $ref"
done
```

**Step 2: Fix any issues found**

**Step 3: Final commit if fixes were needed**

```bash
cd /home/spinoza/github/alex-claude-plugins && git add -A && git commit -m "fix: address validation issues in osf-preprint skill"
```
