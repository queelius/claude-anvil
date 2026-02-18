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

## Strategy

1. **Don't know the field path?** Run `deets search <query>` — it searches
   keys, values, and descriptions. More forgiving than guessing globs.
2. **Want to see what's available?** Run `deets schema --format json` for
   all fields with types, descriptions, and examples.
3. **Know the exact path?** Use `deets get <path>` with `--default ""` so
   the command never fails.

## Querying

```bash
# Fuzzy discovery (searches keys, values, and descriptions)
deets search orcid
deets search university

# Exact single value (bare output, pipe-friendly)
deets get identity.name
deets get contact.email
deets get profiles.github.username

# Glob patterns
deets get profiles.github            # all fields for a platform
deets get profiles.*.email           # one field across all platforms
deets get profiles.*.url             # all profile URLs

# With fallback (never fails, exit 0)
deets get academic.scholar --default ""

# Structured output
deets show --format json             # full dump
deets export --format env            # DEETS_IDENTITY_NAME="..." format
```

## Identity Consolidation

The `identity_web` category links name variants, handles, emails, and
profile URLs so that searching any one resolves to the same person.

```bash
deets get identity_web               # everything
deets get identity_web.names          # name variants
deets get identity_web.handles        # platform handles
deets get identity_web.emails         # all emails
deets get identity_web.urls           # all profile URLs
```

Use this when populating CITATION.cff, ORCID profiles, Hugo site configs,
or any metadata that benefits from consistent cross-platform identity linkage.

## Local vs Global

deets merges two files: global (`~/.deets/me.toml`) and local
(`.deets/me.toml` in the current project, discovered by walking up from cwd).
Local fields override global at key-level granularity. Use `deets which` to
see which files are active. Most of the time only the global file exists.

## Missing Data

If expected fields are empty or `deets get` returns exit code 2 (not found),
suggest the user run `deets populate` to auto-harvest from external sources:

```bash
deets populate --git      # from git config
deets populate --github   # from GitHub API (needs gh CLI)
deets populate --orcid    # from ORCID public API
deets populate --all      # all sources
```

Do not run populate without the user's explicit request — it modifies the
data store and hits external APIs.

## Output Conventions

- Single `get`: bare value, no decoration (pipe-friendly)
- Multiple matches: JSON when piped, table on TTY
- `--format`: table, json, toml, yaml, env
- Exit code 0 = success, 2 = not found
