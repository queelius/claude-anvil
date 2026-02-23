---
name: osf-preprint
description: "This skill should be used when the user asks to \"submit a preprint\", \"upload to OSF\", \"post on OSF Preprints\", \"MetaArXiv preprint\", \"preprint submission\", \"OSF preprint\", \"post preprint\", \"share preprint on OSF\", or mentions OSF/MetaArXiv preprint submission. It delegates to the `osf-preprint-submit` CLI tool."
---

# OSF Preprint Submission

Guide the complete workflow for submitting a preprint to OSF Preprints or MetaArXiv using the `osf-preprint-submit` CLI tool. The tool merges metadata from `.zenodo.json`, `CITATION.cff`, and LaTeX source, then drives the OSF v2 API.

## Prerequisites

The `osf-preprint-submit` script must be installed at `~/.local/bin/osf-preprint-submit`. If missing, inform the user it lives at `~/github/tools/osf-preprint-submit/osf_preprint_submit.py`.

## Workflow

### 1. Check Authentication

Verify that `OSF_TOKEN` is set (Bash tool):

```bash
echo "${OSF_TOKEN:+set}" || echo "not set"
```

If not set:
1. Direct user to https://osf.io/settings/tokens
2. Token requires `osf.full_read` + `osf.full_write` scopes
3. Add to `~/.bashrc`: `export OSF_TOKEN=your_token_here`

### 2. Dry Run

Run the tool in dry-run mode to preview metadata and PDF detection (Bash tool):

```bash
osf-preprint-submit --dry-run
```

This shows:
- **Title**, **abstract**, **tags**, **license**, **repo URL** — each with its source (`.zenodo.json`, `CITATION.cff`, LaTeX, or git remote)
- **PDF path** — auto-detected from `submission/main.pdf`, `paper/main.pdf`, or `main.pdf`

### 3. Confirm with User

Present the dry-run output and ask the user to confirm. If any field needs correction, options are:

1. **Fix the source file** (`.zenodo.json`, `CITATION.cff`, etc.) and re-run
2. **Use CLI overrides**: `--title`, `--abstract`, `--tags`, `--license`
3. **Specify a different PDF**: pass the path as a positional argument
4. **Choose provider**: `--provider osf` (default is `metaarxiv`)

### 4. Submit

Run the tool without `--dry-run` (Bash tool):

```bash
osf-preprint-submit [--provider metaarxiv|osf] [path/to/paper.pdf]
```

The tool performs three API calls:
1. **Create preprint** (draft, no file) on the chosen provider
2. **Upload PDF** to the preprint's own osfstorage
3. **PATCH preprint** to set primary file, license (if valid for provider), and data links (repo URL)

### 5. Report Results

The tool prints the preprint URL. Present this to the user along with next steps:

1. Visit the preprint edit page on OSF
2. **Add subjects** (required — cannot be set via API)
3. **Verify license** (auto-set if the provider accepts it, otherwise choose manually)
4. **Review metadata** (contributors, description, etc.)
5. Click **Submit** / **Publish** when ready
6. DOI is minted after publication (~24 hours to resolve)

### 6. Record Submission (Optional)

If `.papermill.md` exists in the repo, offer to update the submission status (e.g., add the preprint URL/DOI).

## CLI Reference

```
osf-preprint-submit [OPTIONS] [PDF_PATH]

Options:
  --provider TEXT     metaarxiv (default) or osf
  --title TEXT        Override title
  --abstract TEXT     Override abstract
  --tags TEXT         Override tags (comma-separated)
  --license TEXT      Override license SPDX id
  --publish           Publish immediately (default: draft)
  --dry-run           Show metadata, don't submit
  --dir PATH          Paper directory (default: cwd)
```

## Metadata Sources (Priority Order)

| Field | Source 1 | Source 2 | Source 3 |
|-------|----------|----------|----------|
| Title | `.zenodo.json` | `CITATION.cff` | LaTeX `\title` |
| Abstract | `.zenodo.json` | LaTeX `\begin{abstract}` | — |
| Keywords | `.zenodo.json` | `CITATION.cff` | LaTeX `\begin{keyword}` |
| License | `CITATION.cff` | `.zenodo.json` | — |
| Repo URL | `CITATION.cff` `repository-code` | `git remote` | — |

CLI flags (`--title`, etc.) always override all sources.

## Error Handling

| Error | Response |
|-------|----------|
| `OSF_TOKEN` not set | Guide user to https://osf.io/settings/tokens |
| No PDF found | User must provide path or place PDF in standard location |
| API 401 | Token invalid — regenerate at OSF settings |
| API 403 "Invalid license" | License not accepted by provider — set manually on OSF |
| Missing title/abstract | Add metadata to `.zenodo.json` or `CITATION.cff` |

## Important Notes

- **Draft by default**: The tool creates an unpublished preprint. The user must review and publish on OSF.
- **Subjects**: Cannot be set via API. Must be added on the OSF web interface.
- **No node created**: The tool uploads directly to the preprint's storage (not a separate project node).
- **Data links**: If a `repository-code` URL is found, it's automatically set as the public data link.
- **License validation**: The tool queries the provider's accepted licenses and skips invalid ones with a warning.
