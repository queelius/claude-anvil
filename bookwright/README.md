# bookwright

A Claude Code plugin for documentation-first technical-textbook writing. The Bernoulli-textbook approach: **the design spec and per-chapter plans drive the manuscript**, with multi-agent drafting, math-correctness auditing, cross-reference integrity, and per-Part integration checks.

Sibling to `worldsmith` (fiction) and `papermill` (academic papers); bookwright owns the long-form non-fiction technical book.

## Philosophy

- **Specs first, manuscript second.** Master design spec, per-Part design specs, per-chapter implementation plans, per-section drafts. Update the spec when a structural decision changes, then propagate to the prose.
- **Path A discipline per section.** Implementer subagent, then spec-compliance review, then quality review, then fix loop. Per-task subagent dispatch protects main context and catches issues at the section grain.
- **Notebooks are empirical verifiers.** A chapter with a paired notebook must execute end-to-end with numerical-sanity targets that match prose claims. Broken notebook means broken chapter.
- **Running threads tracked explicitly.** The design spec names threads (e.g., the BSC, the Bloom filter); each chapter carries its share; integration checks verify the inventory.
- **Cross-reference integrity is mechanical.** Every section file has a header comment block documenting label resolution. The cross-ref auditor verifies the inventory.

## Installation

From a Claude Code session:

```
/plugin marketplace add queelius/claude-anvil
/plugin install bookwright@queelius
```

Or, if you have the monorepo cloned locally and want to install from the working tree:

```
/plugin marketplace add ~/github/alex-claude-plugins
/plugin install bookwright@queelius
```

(The marketplace name is `queelius` regardless of how you added it.)

**Required co-installation:** the `soul` plugin from the same marketplace, for the soul-voice hook (banned-phrase enforcement). The marketplace does not auto-install dependencies, so install `soul` explicitly. The macro-leak hook ships with bookwright itself.

## What's Included

### Commands (9)

| Command | Purpose |
|---------|---------|
| `/bookwright:init [book-name]` | Scaffold a fresh book project (LaTeX + notebooks + spec/plan dirs) |
| `/bookwright:design [part]` | Write master or per-Part design spec via Socratic dialogue |
| `/bookwright:plan [chapter]` | Write per-chapter implementation plan from the relevant design spec |
| `/bookwright:draft [chapter\|section]` | Launch the writer orchestrator for prose drafting |
| `/bookwright:notebook [chapter]` | Draft and execute the paired notebook for a chapter |
| `/bookwright:check [scope]` | Fast mechanical diagnostics (build, labels, page counts, threads, soul-voice) |
| `/bookwright:review [scope]` | Heavy multi-agent editorial review (4 specialists in parallel) |
| `/bookwright:integrate [scope]` | Per-Part or full-book integration check plus integration-pass record |
| `/bookwright:help` | Quick reference for commands, agents, and skills |

### Agents (9 in v0.1)

**Orchestrators (2):** `writer`, `reviewer`. v0.2 adds `rewriter` and `iterator`.

**Drafting specialists (3):** `section-writer`, `notebook-author`, `source-reformulator`.

**Review specialists (4):** `spec-auditor`, `quality-auditor`, `math-auditor`, `cross-ref-auditor`.

The `math-auditor` deserves a callout: in the Bernoulli textbook session, it would have caught arithmetic errors in chapter 5 §5.2, chapter 5 §5.4, chapter 6 §6.1, and chapter 10 §10.4 that escaped generic quality review. Worth a separate auditor.

### Skills (3, auto-triggered)

| Skill | Triggers when... |
|-------|------------------|
| `bookwright:textbook-methodology` | Drafting prose for a bookwright project |
| `bookwright:cross-reference-discipline` | Writing cross-referenced sections |
| `bookwright:notebook-paired-with-prose` | Drafting or executing a paired notebook |

### Hooks (2)

| Hook | Source |
|------|--------|
| Soul-voice (banned-phrase enforcement) | `soul` plugin dependency |
| LaTeX-macro-leak | Ships with bookwright |

## What "bookwright" Is Not For

- Fiction (use `worldsmith`).
- Single-paper academic submissions (use `papermill`).
- Memoir, popular trade, journalism (different prose conventions; not in scope).
- Multi-author collaboration workflows (not in v0.1).
- ISBN registration and KDP submission (use the `kdp` plugin).

## License

MIT.
