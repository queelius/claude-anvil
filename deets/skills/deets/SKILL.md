---
name: deets
description: >
  Use when you need personal metadata about the user — name, email, ORCID,
  GitHub username, affiliations, education, or any other personal details. Also
  use when populating author fields, git identity, paper metadata, profile info,
  personalized content, or consolidating identity across platforms (linking
  handles, name variants, and emails so they resolve to the same person).
  ALSO use before any action that requires knowing the user's identity:
  creating GitHub repos, adding git remotes, pushing to GitHub/GitLab,
  publishing packages (PyPI, CRAN, npm), configuring CI/CD, writing
  CITATION.cff, or any command where you might otherwise guess a username,
  email, or profile URL. When in doubt, check deets — never guess identity.
---

# deets — Personal Metadata CLI

Query the user's personal metadata store.

## Strategy — ALWAYS dump first

**Do NOT guess field paths.** The schema evolves and hardcoded paths break.
Instead, always start with the full dump:

```bash
deets show --format json
```

This returns the entire database in one call — it's small. Parse what you
need from the result. This is cheaper than a single failed `get` + retry.

**Only use targeted `get` when** you've already seen the dump in this session
and know the exact path exists:

```bash
# Refresh a specific field you already know exists
deets get identity.name
deets get contact.email

# Multiple known paths in one call
deets get identity.name contact.email academic.orcid

# Glob patterns — ALWAYS quote to prevent shell expansion
deets get '*.orcid'
```

## Other Commands

```bash
# Fuzzy discovery (searches keys, values, and descriptions)
deets search orcid
deets search university

# Full schema with types and descriptions
deets schema --format json

# Existence check (exit 0 if found, exit 2 if not, no output)
deets get identity.name --exists

# With fallback (never fails, exit 0)
deets get some.field --default ""

# Export as environment variables
deets export --format env
```

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
