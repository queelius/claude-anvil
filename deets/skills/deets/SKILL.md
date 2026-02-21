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

1. **Need multiple fields?** Start with `deets show --format json` — it's
   only ~2.7KB. One call, zero guessing. Parse what you need from the dump.
2. **Don't know the field path?** Run `deets search <query>` — it searches
   keys, values, and descriptions. More forgiving than guessing globs.
3. **Want the full schema?** Run `deets schema --format json` for
   all fields with types, descriptions, and examples.
4. **Know the exact path?** Use `deets get <path>` with `--default ""` so
   the command never fails.
5. **Quick existence check?** Use `deets get <path> --exists` — exit 0 if
   found, exit 2 if not. No output, no parsing.

## Querying

```bash
# Fuzzy discovery (searches keys, values, and descriptions)
deets search orcid
deets search university

# Exact single value (bare output, pipe-friendly)
deets get identity.name
deets get contact.email
deets get profiles.github.username

# Multiple paths in one call (returns structured output)
deets get identity.name contact.email academic.orcid

# Glob patterns — ALWAYS quote patterns containing * or ?
# The shell will expand unquoted globs to filenames before deets sees them
deets get 'profiles.*.email'         # one field across all platforms
deets get 'profiles.*.url'           # all profile URLs
deets get '*.orcid'                  # find key across categories
deets get profiles.github            # no glob chars, quoting optional

# With fallback (never fails, exit 0)
deets get academic.scholar --default ""

# Existence check (exit 0 if found, exit 2 if not, no output)
deets get identity.name --exists

# Structured output
deets show --format json             # full dump (~2.7KB, best first move)
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

- Single exact `get`: bare value, no decoration (pipe-friendly, even when piped)
- Multiple matches / multi-path / globs: JSON when piped, table on TTY
- `--format`: table, json, toml, yaml, env
- Exit code 0 = success, 2 = not found
