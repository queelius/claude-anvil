---
name: triage
description: Intelligent journal cleanup — cross-references open tasks and ideas with git history, codebase state, and project activity to suggest what's done, stale, or abandoned
argument-hint: "[tag or project name]"
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
---

# /jot triage - Intelligent Journal Cleanup

Cross-reference open journal entries with external signals (git history, codebase, PRs) to identify entries that are likely finished, abandoned, or need attention. Present a triage list with actionable recommendations.

## Step 1: Gather Candidates

Determine scope:
- If an argument is provided, use it as the tag filter: `jot list --tags=<arg> --json`
- If no argument, detect project context from `basename "$PWD"` via `jot tags --fuzzy <basename> --json`, then filter by that tag
- If no project context, use all open entries: `jot list --status=open --json` and `jot list --status=in_progress --json`

Also gather stale entries: `jot stale --days 30 --json` (scoped to tag if available).

## Step 2: Cross-Reference with Git History

For each candidate entry, search git history for related work:

```bash
# Search commit messages for keywords from the entry title
git log --oneline --since="$(entry.created)" --grep="<keyword>" 2>/dev/null

# Check recent commits touching files related to the entry's tags/content
git log --oneline --since="$(entry.created)" -- "*<keyword>*" 2>/dev/null
```

Extract 2-3 keywords from each entry title (drop stopwords like "the", "a", "fix", "add", "implement"). Search for each keyword independently and look for overlapping commits.

**Signals that work is DONE:**
- Multiple commits mentioning the task keywords after the entry was created
- Recent commits in directories/files matching the entry's tags
- Entry title closely matches a commit message (e.g., "Fix auth bug" ↔ "fix: auth bug in login handler")

**Signals that work is ABANDONED:**
- Entry is 60+ days old with zero matching commits
- No recent git activity in related files/directories
- Entry tags correspond to a project with no recent commits

**Signals to KEEP OPEN:**
- Recent matching commits but task appears partially complete
- Entry is a plan or idea (type=plan/idea) that hasn't been started — these may be intentionally deferred
- Entry has high priority or upcoming due date

## Step 3: Check Additional Signals (if available)

If in a git repo with a remote:
```bash
# Check for merged PRs mentioning the task
gh pr list --state merged --search "<keywords>" --limit 5 2>/dev/null || true
```

Check if files referenced in the entry content exist or were recently modified:
```bash
# Look for files matching entry keywords
git diff --stat HEAD~50..HEAD -- "*<keyword>*" 2>/dev/null
```

## Step 4: Present Triage Report

Organize findings into three categories:

### Likely Done
Entries where git history strongly suggests the work was completed. For each:
- Entry title and slug
- Evidence: matching commits (show 1-2 most relevant)
- Recommendation: `jot status <slug> done`

### Likely Abandoned
Entries that are old with no related activity. For each:
- Entry title, slug, and age
- Evidence: no matching commits, last modified date
- Recommendation: `jot status <slug> archived` or suggest revisiting

### Needs Attention
Entries that are stale, blocked, or partially complete. For each:
- Entry title and slug
- What was found: partial work, blocked status, approaching deadline
- Recommendation: specific next action

### Still Active
Briefly list entries that appear to still be relevant (recent activity, not stale). No action needed — just acknowledge them.

## Step 5: Offer Bulk Actions

After presenting the report, offer to execute recommendations:

- "Mark N entries as done?" → Run `jot status <slug> done` for each
- "Archive N abandoned entries?" → Run `jot status <slug> archived` for each
- "Apply all recommendations?" → Execute all suggested changes

Always confirm before modifying entries. Show the full list of changes before executing.

## Important Notes

- Always use `--json` when querying jot for programmatic parsing.
- Be conservative: when unsure, classify as "Needs Attention" rather than "Likely Done".
- For ideas and plans (type=idea/plan), use a higher threshold before suggesting archive — ideas may be intentionally deferred.
- Show your evidence. Never recommend closing an entry without explaining what git/codebase signal supports it.
- If `gh` CLI is not available, skip PR checks gracefully.
- If not in a git repo, skip git checks and fall back to date-based triage only (essentially `jot stale` with better presentation).
