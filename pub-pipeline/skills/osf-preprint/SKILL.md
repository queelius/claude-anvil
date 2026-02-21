---
name: osf-preprint
description: "This skill should be used when the user asks to \"submit a preprint\", \"upload to OSF\", \"post on OSF Preprints\", \"MetaArXiv preprint\", \"preprint submission\", \"OSF preprint\", \"post preprint\", \"share preprint on OSF\", or mentions OSF/MetaArXiv preprint submission. It guides the complete workflow: extracting metadata from LaTeX, creating an OSF project node, uploading the PDF, and creating a draft preprint."
---

# OSF Preprint Submission

Guide the complete workflow for submitting a preprint to OSF Preprints or MetaArXiv. This skill extracts metadata from a LaTeX manuscript, creates an OSF project node, uploads the PDF, and creates a draft preprint ready for review and publication.

## Workflow

### 1. Load User Config

Read `.claude/pub-pipeline.local.md` if it exists (Read tool). Extract author metadata (`author.name`, `author.email`, `author.orcid`) from the YAML frontmatter to pre-populate submission fields.

If the file does not exist, offer to create one from the template at `${CLAUDE_PLUGIN_ROOT}/docs/user-config-template.md`.

### 2. Check Authentication

Verify that the OSF personal access token is available (Bash tool).

```bash
echo "${OSF_TOKEN:+set}" || echo "not set"
```

If `OSF_TOKEN` is not set:
1. Direct the user to https://osf.io/settings/tokens
2. The token requires the `osf.full_write` scope
3. Instruct the user to export it: `export OSF_TOKEN=your_token_here`

Do not proceed without a valid token.

### 3. Locate the Paper

Find the LaTeX source and compiled PDF (Glob tool).

Search for `.tex` files (exclude `archive/`, `deprecated/`, and auxiliary files):
- `paper/main.tex` (most common)
- `paper.tex`
- `main.tex`
- `**/*.tex` (broad search if the above fail)

Search for the corresponding PDF:
- Match the `.tex` basename (e.g., `main.tex` -> `main.pdf`)
- Check the same directory and `paper/` subdirectory

Common project structures:
```
paper/main.tex   ->  paper/main.pdf
paper.tex        ->  paper.pdf
main.tex         ->  main.pdf
```

If no PDF is found, offer to build it (Bash tool):
```bash
cd /path/to/paper && latexmk -pdf main.tex
```

If no `.tex` file is found, ask the user for the manuscript location.

### 4. Extract Metadata from LaTeX

Read the `.tex` file and extract submission metadata (Read tool).

**Fields to extract**:

| Field | LaTeX Pattern | Notes |
|-------|--------------|-------|
| Title | `\title{...}` | Handle nested braces (e.g., `\title{A {Bayesian} Approach}`) |
| Abstract | `\begin{abstract}...\end{abstract}` | May span multiple lines |
| Keywords | `\keywords{...}` or `\begin{keywords}...\end{keywords}` | Comma-separated list |
| Authors | `\author{...}` | May include `\and`, affiliations, footnotes |

**Get the GitHub repository URL** (Bash tool):
```bash
git remote get-url origin
```

Convert SSH URLs (`git@github.com:user/repo.git`) to HTTPS (`https://github.com/user/repo`).

**Handle extraction failures**: Nested braces, multi-line fields, and non-standard macros can break regex extraction. If any field cannot be reliably extracted, present what was found and ask the user to confirm or provide the missing values.

### 5. Choose Provider

Ask the user which preprint provider to use:

| Provider | ID | Notes |
|----------|----|-------|
| MetaArXiv | `metaarxiv` | Interdisciplinary, commonly used for statistics, social sciences, meta-science |
| OSF Preprints | `osf` | General-purpose OSF preprint server |

Default to **MetaArXiv** if the user does not specify a preference.

### 6. Confirm Metadata

Present all extracted metadata to the user for review before proceeding:

```
Title:    [extracted title]
Authors:  [extracted authors]
Abstract: [extracted abstract]
Keywords: [extracted keywords]
Provider: [selected provider]
GitHub:   [repository URL]
PDF:      [path to PDF file]
```

Allow the user to edit any field. Do not proceed until the user confirms the metadata is correct.

### 7. Create OSF Project Node

Create a new OSF project to host the preprint (Bash tool).

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

Extract the node ID from the response: `.data.id`

If the API returns an error, check the error handling table below.

### 8. Upload PDF to Node

Upload the compiled PDF to the OSF project node's file storage (Bash tool).

```bash
curl -s -X PUT \
  "https://files.osf.io/v1/resources/<NODE_ID>/providers/osfstorage/?kind=file&name=<PDF_FILENAME>" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/pdf" \
  --data-binary @/path/to/paper.pdf
```

Extract the file ID from the response for use in the preprint creation step.

**Handle 409 Conflict**: If a file with the same name already exists, the API returns 409. Offer the user the option to upload a new version instead of creating a duplicate.

### 9. Create Preprint

Create a draft preprint linking the node and uploaded PDF (Bash tool).

```bash
curl -s -X POST "https://api.osf.io/v2/preprints/" \
  -H "Authorization: Bearer $OSF_TOKEN" \
  -H "Content-Type: application/vnd.api+json" \
  -d '{
    "data": {
      "type": "preprints",
      "attributes": {
        "title": "<TITLE>",
        "description": "<ABSTRACT>",
        "tags": ["<KEYWORD1>", "<KEYWORD2>"],
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
            "type": "providers",
            "id": "<PROVIDER_ID>"
          }
        }
      }
    }
  }'
```

Extract the preprint URL from the response (`.data.links.html`).

The preprint is created as a **draft** (`is_published: false`) so the user can review it on OSF before making it public.

### 10. Report Results

Present the submission summary to the user:

```
Provider:     [MetaArXiv / OSF Preprints]
Title:        [preprint title]
OSF Node:     https://osf.io/<NODE_ID>/
Preprint URL: https://osf.io/preprints/<PROVIDER>/<PREPRINT_ID>/
Status:       Draft (not yet public)
```

**Next steps for the user**:
1. Review the preprint at the URL above
2. Add subjects/categories on OSF (cannot be set via API)
3. Set a license (e.g., CC-BY 4.0) on OSF
4. Click "Publish" on OSF to make the preprint public and receive a DOI
5. After publishing, the DOI will be minted by OSF and become resolvable within ~24 hours

**Record in user config**: If `.claude/pub-pipeline.local.md` exists, offer to add a `related_work` entry recording this preprint submission:

```yaml
related_work:
  - type: "preprint"
    doi: null  # fill in after DOI is minted
    path: null
    notes: "Submitted to <PROVIDER> via /osf-preprint on <DATE>. OSF node: <NODE_ID>"
```

This makes the preprint visible to other pub-pipeline skills (e.g., `joss-draft` can cite it, `r-pub-pipeline` can reference it in the assessment).

## Error Handling

| Error | Response |
|-------|----------|
| `OSF_TOKEN` not set | Guide user to https://osf.io/settings/tokens with `osf.full_write` scope |
| No `.tex` file found | Ask user for the manuscript file location |
| No `.pdf` file found | Offer to compile with `latexmk -pdf` |
| API 401 Unauthorized | Token is invalid or expired -- regenerate at OSF settings |
| API 403 Forbidden | Token lacks `osf.full_write` scope -- recreate with correct scope |
| API 409 Conflict on upload | File already exists -- offer to upload as new version |
| Metadata extraction fails | Present partial results and ask user to provide missing fields manually |

## Reference Files

For complete OSF API details, preprint provider options, and submission requirements:
- **`${CLAUDE_PLUGIN_ROOT}/docs/osf-reference.md`** -- OSF API v2 endpoints, authentication, preprint providers, metadata fields, and common error responses

## Important Notes

- **Draft by default**: Preprints are created with `is_published: false`. The user must review and click "Publish" on OSF to make the preprint public and receive a DOI.

- **Subjects and categories**: OSF subject taxonomies cannot be set via the API. The user must add subjects manually through the OSF web interface during review.

- **License selection**: The license (e.g., CC-BY 4.0, CC0) must be set on OSF during the review step before publishing. It cannot be reliably set via the preprint creation API.

- **DOI assignment**: A DOI is minted only after the preprint is published (not while in draft). The DOI becomes resolvable within approximately 24 hours of publication.

- **One preprint per node**: Each OSF project node can be associated with only one preprint. Do not attempt to create multiple preprints on the same node.

- **Updating a preprint**: To update a published preprint, upload a new version of the PDF to the same node (do not create a new preprint). The version history is preserved automatically.
