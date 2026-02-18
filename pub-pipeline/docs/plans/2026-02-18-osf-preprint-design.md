# OSF Preprint Skill Design

**Date:** 2026-02-18
**Status:** Approved

## Summary

Add an OSF preprint submission skill to the pub-pipeline plugin. The skill guides Claude through uploading a paper's compiled PDF to MetaArXiv or OSF Preprints via the OSF API v2, with metadata auto-extracted from LaTeX source.

## Architecture Decision

**Pure skill (no external scripts).** Claude handles LaTeX parsing natively and makes 3 curl calls against the OSF API. Zero dependencies beyond `curl` and `OSF_TOKEN` env var. This accommodates the user's varied paper repo structures without rigid code.

## Components

### 1. Skill: `skills/osf-preprint/SKILL.md`

Triggers: "upload preprint", "submit to OSF", "MetaArXiv", "preprint submission"

### 2. Command: `commands/osf-preprint.md`

Slash command `/osf-preprint` for direct invocation.

### 3. Router update: `skills/pub-pipeline/SKILL.md`

Add `.tex`/`.pdf` paper repo detection to route to `/osf-preprint`.

## Workflow

```
1. DETECT    — Find .tex and .pdf files in current repo
2. EXTRACT   — Parse title, abstract, keywords, authors from .tex
3. CONFIRM   — Show extracted metadata to user for approval/editing
4. CREATE    — POST /v2/nodes/ (create OSF project node)
5. UPLOAD    — PUT via WaterButler (upload PDF to node)
6. PUBLISH   — POST /v2/preprints/ (create preprint linking node, file, provider)
7. REPORT    — Display preprint URL and DOI
```

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Pure skill | Varied repo structures, only 3 API calls |
| Upload scope | PDF + GitHub link | Source lives on GitHub; OSF gets the rendered output |
| Metadata source | Auto-extract from .tex | Claude parses LaTeX natively; fills gaps interactively |
| Providers | MetaArXiv + OSF Preprints | Two most relevant; configurable per invocation |
| Auth | `OSF_TOKEN` env var | Standard OSF PAT pattern |

## Metadata Extraction

Parse from LaTeX (in order of precedence):
- `\title{...}` — title
- `\begin{abstract}...\end{abstract}` — abstract
- `\keywords{...}` or `\begin{keywords}...\end{keywords}` — keywords
- `\author{...}` — authors
- `git remote -v` — GitHub repo URL for description

Fallback: ask user for anything not found.

## OSF API Calls

### Create node
```
POST https://api.osf.io/v2/nodes/
Authorization: Bearer $OSF_TOKEN
Content-Type: application/vnd.api+json

{"data":{"type":"nodes","attributes":{"title":"<title>","category":"project","public":true}}}
```

### Upload PDF
```
PUT https://files.osf.io/v1/resources/<node_id>/providers/osfstorage/?kind=file&name=paper.pdf
Authorization: Bearer $OSF_TOKEN
Body: raw PDF binary
```

### Create preprint
```
POST https://api.osf.io/v2/preprints/
Authorization: Bearer $OSF_TOKEN
Content-Type: application/vnd.api+json

{"data":{
  "type":"preprints",
  "attributes":{"title":"...","description":"...","tags":[...],"is_published":true},
  "relationships":{
    "node":{"data":{"type":"nodes","id":"<node_id>"}},
    "primary_file":{"data":{"type":"files","id":"<file_id>"}},
    "provider":{"data":{"type":"preprint-providers","id":"metaarxiv"}}
  }
}}
```

## Error Handling

- Missing `OSF_TOKEN` → prompt user to create at https://osf.io/settings/tokens
- Missing PDF → offer to compile with `latexmk -pdf`
- API errors → display message, suggest fixes
- Duplicate title → warn, allow override

## Integration

Update `skills/pub-pipeline/SKILL.md` router table to detect paper repos (`.tex` + `.pdf`) and offer `/osf-preprint` as a publication option.
