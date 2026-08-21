---
name: project-self-improving
description: "Captures learnings, errors, corrections, and feature requests in `.learnings/` (or global `$HOME/.self-improving-agent/.learnings/`) for continuous improvement across coding agents. Use when (1) a command or operation fails unexpectedly, (2) user corrects the agent ('No, that's wrong...', 'Actually...'), (3) user requests a missing capability, (4) an external API or tool fails, (5) the agent realizes knowledge is outdated or incorrect, (6) a better approach is discovered for a recurring task. Promotes broadly-applicable learnings to project rules (`AGENTS.md` / `CLAUDE.md` / `.github/copilot-instructions.md` / `.trae/rules/*.md`). Also reviews learnings before major tasks. Includes mandatory hook self-check: every agent using this skill must verify its hook is installed and alert the user if missing."
version: 1.0.0
---

# Project Self-Improving

Agent-neutral experience ledger. Logs learnings, errors, and feature requests as
markdown entries; promotes broadly-applicable patterns to project rules. Designed
for the **coding-project workflow**: `.learnings/` lives next to your code, hooks
are documented (not invented), and the skill **self-checks its hook installation
at session start** so misconfiguration is caught early instead of silently
failing.

## Quick Reference

| Situation                              | Action |
|---------------------------------------|--------|
| Command/operation fails               | Log to `.learnings/ERRORS.md` |
| User corrects you                     | Log to `.learnings/LEARNINGS.md` (category `correction`) |
| User wants missing feature            | Log to `.learnings/FEATURE_REQUESTS.md` |
| API/external tool fails               | Log to `.learnings/ERRORS.md` (with integration details) |
| Knowledge was outdated                | Log to `.learnings/LEARNINGS.md` (category `knowledge_gap`) |
| Found better approach                 | Log to `.learnings/LEARNINGS.md` (category `best_practice`) |
| Similar to existing entry             | Link with `**See Also**`, consider priority bump |
| Broadly applicable learning           | Promote to `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or `.trae/rules/*.md` |
| Workflow / process improvement        | Promote to `AGENTS.md` |
| Tool / environment gotcha             | Promote to `CLAUDE.md` or `.github/copilot-instructions.md` |
| Behavioral pattern (tone, style)      | Promote to agent-native rules file (see §6) |
| Hook misconfigured / not installed    | **Self-check runs automatically** — alert user with remediation steps (§4) |

## §1 What This Skill Does (and Does Not)

**Does:**
- Provide a structured markdown format for LRN / ERR / FEAT entries.
- Document how to wire **agent-native hooks** (Trae, Claude Code, Codex, Copilot) so
  the skill auto-reminds at session start and auto-detects tool failures.
- **Self-check** that the hook is installed and configured for the current agent —
  if not, surface a clear remediation message instead of failing silently.
- Promote broadly-applicable learnings to whichever rule file the active agent
  actually reads (`AGENTS.md` / `CLAUDE.md` / `.trae/rules/*.md` /
  `.github/copilot-instructions.md`).

**Does NOT:**
- Bind to a specific vendor (no `clawdhub`, no `openclaw workspace/{SOUL,TOOLS,MEMORY}.md`).
- Invent hook protocols — only document the **native** hook schema of each agent.
- Auto-create `.learnings/` unless the user opts in (see §2).
- Run a `Skill` tool on itself — that would be recursive.

## §2 Where Logs Live (two modes, no judgment)

This skill does **not** assume one location. The user (or each agent) chooses
between two equivalent layouts:

| Mode | Path | When to use |
|------|------|-------------|
| **Project-local** | `<repo>/.learnings/{LEARNINGS,ERRORS,FEATURE_REQUESTS}.md` | Team-shared learnings (committed). Use `gitignore` only for personal noise (see §7). |
| **Global home**   | `$HOME/.self-improving-agent/.learnings/*.md` | Per-developer, machine-scoped. Survives repo clone / branch switch. |

Both modes are **first-class**. Helpers in `scripts/` accept `--home <path>` to
override the default. The default itself is `--home $HOME/.self-improving-agent`
(agent-installable via the `add`/`install` command of the local package manager;
see `references/<agent>-integration.md` for the install command of each agent).

> **Compatibility note:** this skill is a **fork-style rewrite** of the
> `self-improving-agent` reference. The reference skill is shipped alongside as a
> separately-installed "user-global companion" for individuals who want
> always-on personal experience capture across all projects. **Do not install both
> into the same agent home** — they will collide on `~/.learnings/`. See
> `todos/task.md` for the companion-skill TODO.

## §3 Hook Protocol (agent-native, not invented)

This skill does **not** ship a custom hook system. It documents the **native**
hook schema of each target agent, so installation is copy-paste from the
agent's docs, not from a black-box handler.

| Agent | Native hook config | See |
|-------|-------------------|-----|
| **Trae IDE** (recommended for this market) | `.trae/hooks.json` with `version: 1` + `hooks: { EventName: [...] }` | [references/trae-integration.md](references/trae-integration.md) |
| **Claude Code** | `.claude/settings.json` (project) or `~/.claude/settings.json` (user) | [references/claude-code-integration.md](references/claude-code-integration.md) |
| **Codex CLI** | `.codex/settings.json` | [references/codex-integration.md](references/codex-integration.md) |
| **GitHub Copilot** | No hooks — uses `.github/copilot-instructions.md` only | [references/copilot-integration.md](references/copilot-integration.md) |

All shipped hook scripts are plain bash (cross-platform via
`scripts/detect-python.sh` + `scripts/detect-node.sh`) — they **do not** depend
on any agent runtime. They write XML-style reminder blocks to stdout that each
agent's hook protocol picks up verbatim.

## §4 Mandatory Hook Self-Check (NEW in v1.0)

Every agent that has loaded this skill **MUST** run `scripts/hook-self-check.sh`
at session start. The script probes `.trae/hooks.json`, `.claude/settings.json`,
`.codex/settings.json` (in that order) and reports one of three states:

| State | Meaning | Remediation |
|-------|---------|-------------|
| `INSTALLED` | A hook referencing this skill (or its script path) is present in any of the three configs. | None. Continue. |
| `MISSING_CONFIG_FILE` | No hook config file exists for the active agent. | Run `scripts/install-snippet.sh <agent>` to print the snippet to merge, then add it manually. |
| `MISSING_HOOK_ENTRY` | Config file exists but contains no entry for this skill. | Open the config, copy the relevant block from `references/<agent>-integration.md`. |

The script writes a **single-line remediation block** to stdout when state is not
`INSTALLED`. Agents are expected to surface this block in chat (not silently
suppress it). The script never edits config files itself — installation is the
human's call.

This self-check is mandatory because the original skill suffered from "hooks
installed but pointing at the wrong path" / "agents forget to remind" / "user
never knows the skill is silent" — see
`skill-markets/agent-dev-control-kit/references/traps.md` for the trap entries.

## §5 Entry Format

### Learning entry (`.learnings/LEARNINGS.md`)

```markdown
## [LRN-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of what was learned

### Details
Full context: what happened, what was wrong, what's correct

### Suggested Action
Specific fix or improvement to make

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: LRN-20250110-001 (if related to existing entry)

---
```

### Error entry (`.learnings/ERRORS.md`)

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
Brief description of what failed

### Error
\`\`\`
Actual error message or output
\`\`\`

### Context
- Command/operation attempted
- Input or parameters used
- Environment details if relevant

### Suggested Fix
If identifiable, what might resolve this

### Metadata
- Reproducible: yes | no | unknown
- Related Files: path/to/file.ext
- See Also: ERR-20250110-001 (if recurring)

---
```

### Feature request entry (`.learnings/FEATURE_REQUESTS.md`)

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**Logged**: ISO-8601 timestamp
**Priority**: medium
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Requested Capability
What the user wanted to do

### User Context
Why they needed it, what problem they're solving

### Complexity Estimate
simple | medium | complex

### Suggested Implementation
How this could be built, what it might extend

### Metadata
- Frequency: first_time | recurring
- Related Features: existing_feature_name

---
```

## §6 Promotion Targets

When a learning is broadly applicable, promote it to whichever file the active
agent actually reads. **Never promote to files that the active agent does not
load** — this is the most common knowledge-pollution pattern.

| Target | What Belongs There | When To Promote |
|--------|-------------------|-----------------|
| `AGENTS.md` | Multi-agent workflows, delegation patterns, automation rules | Any agent reading `AGENTS.md` (Trae + many forks) |
| `CLAUDE.md` | Project facts, conventions, gotchas | Claude Code users |
| `.github/copilot-instructions.md` | Project context and conventions | GitHub Copilot users |
| `.trae/rules/<topic>.md` | Project-level Trae rules (gateway-routed) | Trae projects with custom rules |
| `.claude/rules/*.md` | Claude Code native rules | Claude Code projects with native rules |

> **Do not** promote to `SOUL.md`, `TOOLS.md`, `MEMORY.md` — those are
> agent-specific workspace files from openclaw-style runtimes and **are not
> part of any coding-project standard**. Promoting there is the canonical
> "knowledge pollution" trap this skill was rewritten to avoid.

### Promotion Decision Tree

**Project-specific?** → keep in `.learnings/`. **Behavioral?** → `AGENTS.md` /
`CLAUDE.md` / `copilot-instructions.md` (NOT openclaw-style workspace files).
**Tool-related?** → `CLAUDE.md` / `copilot-instructions.md` / `.trae/rules/`.
**Workflow?** → `AGENTS.md`.

## §7 Gitignore Options

| Strategy | `.gitignore` snippet | Notes |
|----------|---------------------|-------|
| Keep learnings local (per-developer) | `.learnings/` | Personal noise, no team value |
| Track learnings in repo (team-wide) | (none — commit them) | Shared knowledge base |
| Hybrid (track templates, ignore entries) | `.learnings/*.md` + `!.learnings/.gitkeep` | Templates committed, entries local |

## §8 ID Generation

Format: `TYPE-YYYYMMDD-XXX`
- `TYPE`: `LRN` (learning), `ERR` (error), `FEAT` (feature)
- `YYYYMMDD`: current date
- `XXX`: sequential 3-digit number or random 3 chars (e.g. `001`, `A7B`)

Examples: `LRN-20260821-001`, `ERR-20260821-A3F`, `FEAT-20260821-002`

## §9 Detection Triggers (when to log)

**Corrections** (→ LRN `correction`):
- "No, that's not right..."
- "Actually, it should be..."
- "You're wrong about..."
- "That's outdated..."

**Feature requests** (→ FEAT):
- "Can you also..."
- "I wish you could..."
- "Is there a way to..."
- "Why can't you..."

**Knowledge gaps** (→ LRN `knowledge_gap`):
- User provides information you didn't know
- Documentation you referenced is outdated
- API behavior differs from your understanding

**Errors** (→ ERR):
- Command returns non-zero exit code
- Exception or stack trace
- Unexpected output or behavior
- Timeout or connection failure

## §10 Priority Guidelines

| Priority | When to Use |
|----------|-------------|
| `critical` | Blocks core functionality, data loss risk, security issue |
| `high` | Significant impact, affects common workflows, recurring issue |
| `medium` | Moderate impact, workaround exists |
| `low` | Minor inconvenience, edge case, nice-to-have |

## §11 Area Tags

Use to filter by codebase region:

| Area | Scope |
|------|-------|
| `frontend` | UI, components, client-side code |
| `backend` | API, services, server-side code |
| `infra` | CI/CD, deployment, Docker, cloud |
| `tests` | Test files, testing utilities, coverage |
| `docs` | Documentation, comments, READMEs |
| `config` | Configuration files, environment, settings |

## §12 Periodic Review

Review `.learnings/` at natural breakpoints (before major task / after feature
/ weekly). Quick status check commands + review actions: see
[`references/periodic-review.md`](references/periodic-review.md).

## §13 Multi-Agent Matrix

This skill ships as agent-neutral. The same `scripts/` and `references/` work
for any of the four target agents; only the **hook config snippet** differs.

| Agent | Activation method | Auto-detect | See |
|-------|-------------------|-------------|-----|
| Trae IDE | `.trae/hooks.json` (`SessionStart` + `PostToolUse` bash command) | yes (via `hook-self-check.sh`) | [references/trae-integration.md](references/trae-integration.md) |
| Claude Code | `.claude/settings.json` (`UserPromptSubmit` + `PostToolUse`) | yes | [references/claude-code-integration.md](references/claude-code-integration.md) |
| Codex CLI | `.codex/settings.json` (same schema as Claude Code) | yes | [references/codex-integration.md](references/codex-integration.md) |
| GitHub Copilot | `.github/copilot-instructions.md` (no hook runtime) | no (manual review) | [references/copilot-integration.md](references/copilot-integration.md) |

## §14 Best Practices

Full list: [`references/best-practices.md`](references/best-practices.md). Top 5
by leverage:

1. Log immediately (context freshest).
2. Self-check before complaining (`hook-self-check.sh`).
3. Promote carefully — only to files the active agent reads (§6).
4. Don't bind to a single agent — `.learnings/` is portable.
5. Review regularly — stale learnings lose value.

## §15 Files In This Package

Run `tree -L 2 skill-markets/project-self-improving/` for the live file tree, or
see [`assets/SKILL-TEMPLATE.md`](assets/SKILL-TEMPLATE.md) §"Required Files" for
the contract each file should satisfy.

## §16 Skill Extraction (When a Learning Becomes a Skill)

A learning qualifies for extraction as a standalone skill when **any** of:

| Criterion | Description |
|-----------|-------------|
| Recurring | Has `See Also` links to 2+ similar issues |
| Verified | Status is `resolved` with working fix |
| Non-obvious | Required real debugging to discover |
| Broadly applicable | Not project-specific; useful across codebases |
| User-flagged | User says "save this as a skill" or similar |

Full workflow + checklist: [assets/SKILL-TEMPLATE.md](assets/SKILL-TEMPLATE.md)
§"Extraction Checklist" + [references/examples.md](references/examples.md)
§"Learning: Promoted to Skill (extraction)".

## §17 See Also

- [`references/hook-self-check.md`](references/hook-self-check.md) · [`references/multi-agent-matrix.md`](references/multi-agent-matrix.md) · [`assets/SKILL-TEMPLATE.md`](assets/SKILL-TEMPLATE.md) · `todos/task.md`