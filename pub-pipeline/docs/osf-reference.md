# OSF API Reference

## Base URLs
- OSF API v2: `https://api.osf.io/v2/`
- WaterButler (file operations): `https://files.osf.io/v1/`
- OSF web interface: `https://osf.io/`

## Authentication
- Personal Access Token (PAT) via `OSF_TOKEN` environment variable
- Header: `Authorization: Bearer $OSF_TOKEN`
- Token creation: https://osf.io/settings/tokens
- Required scopes: `osf.full_read`, `osf.full_write`

## Content Type
- OSF API requests: `Content-Type: application/vnd.api+json`
- WaterButler uploads: `Content-Type: application/octet-stream`

## Preprint Providers
| Provider | ID | URL |
|----------|----|-----|
| OSF Preprints | `osf` | https://osf.io/preprints/ |
| MetaArXiv | `metaarxiv` | https://osf.io/preprints/metaarxiv |

## Correct Preprint Creation Workflow

**Critical**: Files must be uploaded to the **preprint's own storage**, not a project node. The OSF backend validates `file.target == preprint` in `set_primary_file`.

### Step 1: Create Preprint (Draft)

`POST /v2/preprints/` — minimal payload, no `primary_file`, no `is_published`:

```json
{
  "data": {
    "type": "preprints",
    "attributes": {"title": "...", "description": "...", "tags": ["..."]},
    "relationships": {
      "provider": {"data": {"type": "providers", "id": "metaarxiv"}}
    }
  }
}
```

### Step 2: Upload File to Preprint Storage

`PUT https://files.osf.io/v1/resources/{preprint_id}/providers/osfstorage/?kind=file&name=main.pdf`

Then resolve OSF file ID: `GET /v2/preprints/{preprint_id}/files/osfstorage/`

### Step 3: Set Primary File (PATCH)

`PATCH /v2/preprints/{preprint_id}/` — set primary_file, license, data_links:

```json
{
  "data": {
    "type": "preprints", "id": "{preprint_id}",
    "attributes": {"has_data_links": "available", "data_links": ["https://github.com/..."]},
    "relationships": {
      "primary_file": {"data": {"type": "primary_file", "id": "{file_id}"}},
      "license": {"data": {"type": "licenses", "id": "{license_node_id}"}}
    }
  }
}
```

## Provider License Validation

Query accepted licenses: `GET /v2/preprint_providers/{provider_id}/licenses/`

MetaArXiv accepts CC licenses but not MIT, GPL, etc.

## Common License Node IDs

| SPDX ID | OSF Node ID |
|---------|-------------|
| CC-BY-4.0 | `563c1cf88c5e4a3877f9e96a` |
| CC-BY-SA-4.0 | `563c1cf88c5e4a3877f9e96c` |
| CC0-1.0 | `563c1cf88c5e4a3877f9e965` |

## Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 400 "valid primary_file must be set" | `is_published` in creation payload | Omit `is_published` at creation |
| 400 "not a valid primary file" | File target != preprint | Upload to preprint, not a node |
| 400 "Invalid license" | Provider doesn't accept that license | Query provider licenses first |
| 401 | Token invalid | Regenerate at OSF settings |

## Important Notes
- **No node required**: Preprints have their own storage. Nodes are only for supplemental materials.
- **Subjects**: Cannot be set via API — add via web UI.
- **Relationship type**: Use `"primary_file"` (singular) for the primary_file relationship.
- **DOI**: Minted only after publishing (~24 hours to resolve).
- **CLI tool**: `osf-preprint-submit` at `~/.local/bin/` handles the full workflow.
