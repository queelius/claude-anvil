# OSF API Reference

## Base URLs
- OSF API v2: `https://api.osf.io/v2/`
- WaterButler (file operations): `https://files.osf.io/v1/`
- OSF web interface: `https://osf.io/`

## Authentication
- Personal Access Token (PAT) via `OSF_TOKEN` environment variable
- Header: `Authorization: Bearer $OSF_TOKEN`
- Token creation: https://osf.io/settings/tokens
- Required scope: `osf.full_write`

## Rate Limits
- Unauthenticated: 100 requests/hour
- Authenticated: 10,000 requests/day

## Content Type
- All requests use JSON:API format: `Content-Type: application/vnd.api+json`

## Preprint Providers
| Provider | ID | URL |
|----------|----|-----|
| OSF Preprints | `osf` | https://osf.io/preprints/ |
| MetaArXiv | `metaarxiv` | https://osf.io/preprints/metaarxiv |

## Key Endpoints

### Create Node (Project)
- Method: `POST /v2/nodes/`
- Required attributes: `title`, `category` ("project")
- Optional: `description`, `public` (boolean), `tags`
- Response: `.data.id` contains the node ID

### Upload File (WaterButler)
- Method: `PUT /v1/resources/{node_id}/providers/osfstorage/?kind=file&name={filename}`
- Body: raw binary file content
- Content-Type for PDFs: `application/pdf`
- Response contains file metadata including the file ID
- 409 Conflict if file with same name exists (upload new version instead)

### Create Preprint
- Method: `POST /v2/preprints/`
- Required attributes: `title`
- Optional attributes: `description`, `tags`, `is_published`, `doi`
- Required relationships: `node`, `primary_file`, `provider`
- Set `is_published: false` to create as draft

### Get Preprint
- Method: `GET /v2/preprints/{preprint_id}/`
- Returns full preprint metadata including links, DOI, review state

## Common Error Codes
| Code | Meaning | Fix |
|------|---------|-----|
| 400 | Bad request / malformed JSON | Check JSON:API format, ensure relationships are correct |
| 401 | Unauthorized | Token invalid, expired, or missing |
| 403 | Forbidden | Token lacks required scope (`osf.full_write`) |
| 404 | Not found | Check node/file/preprint ID |
| 409 | Conflict | Resource already exists (e.g., duplicate file upload) |
| 429 | Rate limited | Wait and retry |

## Response Parsing
- Node ID: `.data.id` from POST /v2/nodes/
- File ID: parse from WaterButler PUT response
- Preprint URL: `.data.links.html` from POST /v2/preprints/
- DOI: `.data.attributes.doi` (only after publishing)

## Important Notes
- JSON:API requires `"type"` field in all request data objects
- Relationships use nested `{"data": {"type": "...", "id": "..."}}` format
- WaterButler uses a different base URL than the main OSF API
- Preprint subjects (taxonomy) cannot be set via API — must be added manually
- License can be set via relationship to `/v2/licenses/` but is easier to set via web UI
