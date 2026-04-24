---
name: repo-mirror
description: Wrapper around `repoindex ops mirror`. Pushes repos to configured redundancy targets. Dry run by default.
argument-hint: "[--to NAME] [--all] [--dirty | --language X | --tag T] [--force-real]"
allowed-tools:
  - Bash
  - Read
---

# /repo-mirror

Thin wrapper around `repoindex ops mirror`. Pushes every branch and tag (`git push --mirror`) to one or more redundancy targets configured in `~/.repoindex/config.yaml`.

**Safety**: Runs with `--dry-run` by default. The real push only happens if the user explicitly passes `--force-real` (this slash command translates that to dropping `--dry-run` when invoking the CLI).

## Arguments (forwarded)

Pick at least one target selector:

| Flag | Effect |
|------|--------|
| `--to codeberg` | Push to one named mirror (repeatable) |
| `--all` | Push to every configured mirror |

Repo filters (optional):

| Flag | Effect |
|------|--------|
| `--language python` | Only Python repos |
| `--tag work/active` | Only repos with this tag |
| `--recent 7d` | Only repos with recent commits |
| `--dirty` | Only repos with uncommitted changes (rare for mirroring) |

Special flags:

| Flag | Effect |
|------|--------|
| `--init` | For `file://` targets, init a bare repo at the destination if missing |
| `--force` | Bypass fast-forward check (overwrites diverged branches on the mirror) |
| `--force-real` | THIS COMMAND ONLY: drop the automatic `--dry-run` and actually push |

## Workflow

### Step 1: Check that mirrors are configured

Run:

```bash
repoindex config show 2>&1 | grep -A 20 "^mirrors:" || echo "NO_MIRRORS"
```

If there is no `mirrors:` section, stop and print a config template:

```yaml
mirrors:
  - name: codeberg
    url_template: "https://codeberg.org/queelius/{repo}.git"
  - name: gitea-gdrive
    url_template: "file:///mnt/gdrive/git-mirrors/{repo}.git"
```

Explain that `{repo}` is substituted with the repo name, and that SSH URLs (`git@codeberg.org:queelius/{repo}.git`) work too. Do not proceed to step 2.

### Step 2: Build the command

- Start with `repoindex ops mirror --json`.
- Append `--dry-run` unless the user passed `--force-real`.
- If `--force-real` is passed, strip it from the args before forwarding, and omit `--dry-run`.
- Forward everything else as-is.

### Step 3: Run and summarize

```bash
repoindex ops mirror <args>
```

Parse the JSONL output. For each repo x mirror combination, you will get a result with status (skipped, dry-run, pushed, failed).

Summarize:

```
Mirror run (dry-run: yes/no, mirrors: codeberg, nas-backup)

Targeted   N repos
Would push M repo x mirror combinations
Skipped    K (reason: no remote URL, etc)
Failed     F (show each: repo, mirror, error line)
```

### Step 4: Offer the follow-up

If it was a dry run and the preview looks good, suggest:

```
To actually push: /repo-mirror <same args> --force-real
```

If there were failures, suggest checking the mirror config or using `--init` for missing `file://` destinations.

## When to use

- Periodic redundancy push after a working session.
- Before a long trip or offline period, when you want a complete off-GitHub copy.
- Reason for this wrapper over direct CLI: the flag surface is large and the safety default matters. The dry-run-first contract is enforced here.
