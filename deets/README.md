# deets — Claude Code Plugin

Personal metadata queries for Claude Code. Look up identity, contact, academic,
education, and cross-platform profile information using the deets CLI.

**Requires**: [deets](https://github.com/queelius/deets) CLI installed and on PATH.

## Components

| Type | Name | Purpose |
|------|------|---------|
| Skill | `deets` | CLI reference — query strategies, output conventions, field discovery |
| Command | `/deets` | Explicit invocation (skill also auto-triggers on metadata needs) |

## Install

```bash
# From the marketplace
/plugin install deets@queelius
```

## How It Works

The skill auto-triggers when Claude needs personal metadata — author fields,
git identity, ORCID, profile URLs, and similar. It teaches Claude to use the
deets CLI efficiently:

- **Bulk queries**: `deets show --format json` dumps everything (~2.7KB)
- **Targeted lookups**: `deets get identity.name contact.email`
- **Discovery**: `deets search` for fuzzy matching, `deets schema` for introspection

Other plugins (papermill, pub-pipeline) depend on deets for author metadata.

## License

MIT
