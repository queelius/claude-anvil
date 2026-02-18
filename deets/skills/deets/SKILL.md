---
name: deets
description: >
  Use when you need personal metadata about the user — name, email, ORCID,
  GitHub username, affiliations, education, or any other personal details. Also
  use when populating author fields, git identity, paper metadata, profile info,
  personalized content, or consolidating identity across platforms (linking
  handles, name variants, and emails so they resolve to the same person).
---

# deets — Personal Metadata CLI

Query the user's personal metadata store. Fields are organized into core
categories (identity, contact, academic, education) and platform profiles
(profiles.github, profiles.pypi, profiles.orcid, etc.).

## Discovery

Run `deets schema --format json` to see all available fields with types,
descriptions, and example values. This is the authoritative source of what
data exists.

## Common Queries

```bash
# Single value (bare output, pipe-friendly)
deets get identity.name
deets get contact.email
deets get profiles.github.username

# Platform context (all fields for a platform)
deets get profiles.github
deets get profiles.pypi

# Cross-platform queries
deets get profiles.*.email          # all platform emails
deets get profiles.*.url            # all profile URLs

# With fallback (never fails)
deets get academic.scholar --default ""

# Structured output
deets show --format json            # full dump
deets export --format env           # DEETS_IDENTITY_NAME="..." format
```

## Identity Consolidation

The `identity_web` category links name variants, handles, emails, and
profile URLs so that searching any one resolves to the same person.

```bash
# All linked identities
deets get identity_web

# Name variants (Alexander Towell, Alex Towell, queelius, etc.)
deets get identity_web.names
deets get identity_web.handles

# All emails across platforms
deets get identity_web.emails

# All profile URLs (GitHub, ORCID, Scholar, social, etc.)
deets get identity_web.urls
```

Use this when populating CITATION.cff, ORCID profiles, Hugo site configs,
or any metadata that benefits from consistent cross-platform identity linkage.

To update, use `deets set` or `deets edit`:
```bash
deets set identity_web.handles '["queelius", "new-handle"]'
```

## Output Conventions

- Single `get`: bare value, no decoration (pipe-friendly)
- Multiple matches: JSON when piped, table on TTY
- `--format`: table, json, toml, yaml, env
- Exit code 2 = not found
