# Cliche Hook Scoping

**Date**: 2026-05-24
**Status**: Design
**Scope**: `hooks/scripts/check-fiction-cliches.sh` (one hook), plus tests and docs

## Motivation

`check-fiction-cliches.sh` currently gates only on file extension:

```bash
case "$file_path" in
  *.tex|*.md|*.mdx|*.txt) ;;
  *) exit 0 ;;
esac
```

If the project has `WORLDSMITH_PROJECT=1` and the file ends in one of those extensions, the cliche check runs. This is too broad. False positives in a real worldsmith project:

- `README.md` may contain "her heart raced when she opened the package"
- `CLAUDE.md` may quote prose examples that intentionally use the patterns
- `docs/plans/*.md` may quote bad prose as an example of what the hook catches
- Commit message buffers, scratch files, `TODO.txt`, changelog entries

The hook's purpose is prose-craft guardrails for manuscript text. Documents, plans, READMEs, and notes are not prose under craft. They should be exempt.

By contrast, `propagation-reminder.sh` is already scoped: it checks `dirname` and `dirpath` against known doc and manuscript directory patterns, and only fires when the file is in one of them. The cliche hook should adopt the same discipline.

### What breaks today

1. **Quoted examples trigger blocks.** A craft skill file or design plan that quotes "her heart raced" as an anti-pattern gets blocked from being saved.
2. **README prose gets nitpicked.** A README's promotional copy is not held to craft standards.
3. **CLAUDE.md prose gets nitpicked.** Onboarding text uses ordinary metaphors that the hook would flag.
4. **Plan-writing is friction-prone.** Writing a design plan about cliches means quoting cliches, which gets blocked.

### What already works

- The extension gate (`.tex|.md|.mdx|.txt`) correctly skips binary files and scripts.
- The plugin-self-exclusion (skip files inside `${CLAUDE_PLUGIN_ROOT}`) correctly skips the plugin's own skill files that document the cliche patterns.
- The phrase lists are well-tuned. No changes to detection rules.

## Design

### Manuscript classification

Add a new gate after the extension check, before the phrase scan: determine if the file lives in a manuscript directory. If not, exit silently.

Two modes, decided by env-var presence:

**Multi-work mode** (when `WORLDSMITH_WORK_COUNT` is set and > 0):

The detect script exports `WORLDSMITH_WORK_N_MANUSCRIPT` for each work (e.g., `WORLDSMITH_WORK_0_MANUSCRIPT=chapters/`, `WORLDSMITH_WORK_1_MANUSCRIPT=stories/hemorrhagic/`). The hook iterates these env vars, joins each with `$CLAUDE_PROJECT_DIR`, and checks whether `file_path` is inside any of them.

```bash
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
for i in $(seq 0 $((WORLDSMITH_WORK_COUNT - 1))); do
  ms_var="WORLDSMITH_WORK_${i}_MANUSCRIPT"
  ms_rel="${!ms_var:-}"
  [ -z "$ms_rel" ] && continue
  ms_abs="$PROJECT_DIR/${ms_rel%/}"
  case "$file_path" in
    "$ms_abs"|"$ms_abs"/*) is_manuscript=1; break ;;
  esac
done
```

**Single-work mode** (when no `WORLDSMITH_WORK_COUNT` env var):

Fall back to the same heuristics `propagation-reminder.sh` uses. This keeps behavior consistent across both hooks.

```bash
dirpath=$(dirname "$file_path")
dirname=$(basename "$dirpath")
case "$dirname" in
  chapters|manuscript|scenes|stories) is_manuscript=1 ;;
esac
if [ "$is_manuscript" = "0" ]; then
  case "$dirpath" in
    */chapters/*|*/manuscript/*|*/scenes/*|*/stories/*) is_manuscript=1 ;;
  esac
fi
```

The two-pass structure handles both "file directly in `chapters/`" (dirname check) and "file in `chapters/sub/`" (dirpath check). Identical to propagation-reminder.

### No opt-out env var

Considered providing `WORLDSMITH_CLICHE_SCOPE=all` to restore old behavior. Rejected:

- Old behavior is closer to a bug than a feature. Firing on README quotes is unhelpful, not opinionated.
- Users with prose in non-standard directories can add a custom hook in their project settings or move the file to a manuscript directory.
- Each opt-out env var is one more thing future maintainers must remember to handle and document. Stay minimal.

### Test harness

This is the first test harness in worldsmith. Lightweight: a bash script that pipes synthetic JSON to the hook and asserts exit codes.

```bash
tests/test-cliche-scoping.sh
```

Six test cases covering:
- manuscript paths with cliches (expect block, exit 2)
- manuscript paths without cliches (expect pass, exit 0)
- non-manuscript paths with cliches (expect skip, exit 0)
- the `stories/hemorrhagic/file.tex` nested-subdir case (expect block)

Multi-work-mode tests are deferred (they require setting many env vars in concert, and the single-work heuristics cover the high-value cases). Multi-work behavior gets verified by manual smoke test (e.g., editing a file in The Policy's `stories/hemorrhagic/`).

This is not a tested-vs-untested gating; it is regression protection. If a future change to the hook unexpectedly affects scoping, the test catches it.

### Why not extract a shared classifier?

The propagation hook has nearly-identical manuscript-classification logic. Extracting a `classify-fiction-path.sh` helper and refactoring both hooks would centralize the rules.

**Decision: do not extract in this change.** Reasons:

1. The user's stated improvement is "hook scoping" for the cliche hook. Extracting a helper changes two hooks, expanding scope beyond what was requested.
2. The propagation hook's logic is currently working; refactoring it introduces behavior-change risk.
3. The duplication is two case statements in two files. Maintenance cost is small.
4. If a third hook ever needs the same logic, extraction becomes obviously correct. Not yet.

Documenting this decision here so a future maintainer (likely me, weeks from now) knows it was considered and consciously deferred.

## Backward compatibility

This is a behavior change visible to users:

- Files that previously triggered the cliche hook will no longer trigger it unless they live in a manuscript directory.
- No files that the hook previously skipped will now be affected. (No new false positives.)
- The phrase lists do not change. Detection accuracy on actual manuscript prose is unchanged.

The change reduces false positives only. No user who depends on the broad scoping will be silently broken; they will simply notice the hook no longer fires on their `README.md` or planning notes, which is the goal.

## Versioning

Behavior change visible to users: bump 0.9.0 -> 0.10.0 (minor).
