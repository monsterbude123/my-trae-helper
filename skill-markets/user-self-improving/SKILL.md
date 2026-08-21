---
name: user-self-improving
description: "Personal, machine-scoped experience ledger — captures learnings, errors, corrections, and feature requests in `$HOME/.user-self-improving/.learnings/` (default global path) or any custom `--home` override. Optional `SOUL.md` / `TOOLS.md` / `MEMORY.md` workspace files for personal expression. Use when (1) a command or operation fails unexpectedly, (2) user corrects the agent, (3) user requests a missing capability, (4) external API or tool fails, (5) the agent realizes knowledge is outdated or incorrect, (6) a better approach is discovered. Hook-configurable for Trae / Claude Code / Codex / Copilot. Includes mandatory `hook-self-check.sh` to surface misconfiguration early. This is a PERSONAL companion skill — opt-in by `add` and don't confuse with `project-self-improving` (project-scoped team-shared)."
version: 1.0.0
---

# User Self-Improving

A **personal, machine-scoped** companion skill. Lives entirely in your home
directory; survives repo clones, branch switches, and project churn. Every
machine you install it on keeps its own personal ledger.

## Quick Reference

| Situation                              | Action |
|---------------------------------------|--------|
| Command/operation fails               | Log to `$HOME/.user-self-improving/.learnings/ERRORS.md` |
| User corrects you                     | Log to `.../LEARNINGS.md` (category `correction`) |
| User wants missing feature            | Log to `.../FEATURE_REQUESTS.md` |
| API/external tool fails               | Log to `.../ERRORS.md` (with integration details) |
| Knowledge was outdated                | Log to `.../LEARNINGS.md` (category `knowledge_gap`) |
| Found better approach                 | Log to `.../LEARNINGS.md` (category `best_practice`) |
| Personal style / preference           | Log to `$HOME/.user-self-improving/SOUL.md` (opt-in) |
| Personal tool / workflow gotcha       | Log to `$HOME/.user-self-improving/TOOLS.md` (opt-in) |
| Long-term reflection                  | Log to `$HOME/.user-self-improving/MEMORY.md` (opt-in) |
| Hook not installed                    | Self-check runs automatically — alert user with remediation |

## §1 What This Skill Does (and Does Not)

**Does:**
- Provide a global, machine-scoped markdown ledger for cross-project learnings.
- Document how to wire **agent-native hooks** (Trae, Claude Code, Codex, Copilot)
  pointing at `~/.user-self-improving/` as default home.
- **Self-check** that the hook is installed and points at this skill; surface
  clear remediation if not.
- Offer **optional** `SOUL.md` / `TOOLS.md` / `MEMORY.md` workspace files for
  personal expression — these are NOT inherited from any openclaw-style runtime;
  they are simple markdown files in the same `.user-self-improving/` directory.

**Does NOT:**
- Bind to a specific vendor (no `clawdhub`, no `openclaw workspace`).
- Invent a hook protocol — only documents the **native** hook schema of each
  agent.
- Auto-create the home directory unless the user opts in (`scripts/install-snippet.sh`
  prints the snippet; the user runs it).
- Share data with `project-self-improving` (they have separate `.learnings/`
  paths — install one or the other per machine, or both with distinct homes).

## §2 Where Logs Live (default + override)

| Mode | Path | When to use |
|------|------|-------------|
| **Global home (default)** | `$HOME/.user-self-improving/.learnings/{LEARNINGS,ERRORS,FEATURE_REQUESTS}.md` | Per-machine, per-user. Survives project changes. |
| **Override** | `--home <path>` (passed to scripts) | Multi-machine sync, dotfiles repo, etc. |
| **Personal workspace (opt-in)** | `$HOME/.user-self-improving/{SOUL,TOOLS,MEMORY}.md` | Style / preference / long-term reflection. NOT promoted, NOT shared. |

> **Default `HOME` resolution:**
> - Linux / macOS: `$HOME` (or `$USER` if `$HOME` unset)
> - Windows Git Bash / MSYS: `$HOME` (typically `/c/Users/<you>`); WSL → Linux `$HOME`
> - All scripts accept `--home <abs-path>` to override
>
> **D-7 彻底废弃(2026-08-21):** 旧 env `SELF_IMPROVING_HOME` + 旧路径 `$HOME/.self-improving-agent` 不再被任何脚本接受。
> 旧数据如需访问,手动 `cp -r` 到 `$HOME/.user-self-improving/`。

## §3 Hook Protocol (agent-native, not invented)

Same matrix as `project-self-improving`. Document native hook config of each
target agent; do not ship a custom hook runtime.

| Agent | Hook config | See |
|-------|------------|-----|
| Trae IDE | `.trae/hooks.json` (`SessionStart` + `UserPromptSubmit` + `PostToolUse`) | [references/trae-integration.md](references/trae-integration.md) |
| Claude Code | `.claude/settings.json` (`UserPromptSubmit` + `PostToolUse`) | [references/claude-code-integration.md](references/claude-code-integration.md) |
| Codex CLI | `.codex/settings.json` (same schema) | [references/codex-integration.md](references/codex-integration.md) |
| GitHub Copilot | `.github/copilot-instructions.md` (no runtime) | [references/copilot-integration.md](references/copilot-integration.md) |

All shipped hook scripts are plain bash (cross-platform POSIX sh); they write
XML-style reminder blocks that each agent's hook protocol picks up verbatim.

## §4 Mandatory Hook Self-Check

Same protocol as `project-self-improving` §4. Run `scripts/hook-self-check.sh`
at session start. Three states:

| State | Meaning | Remediation |
|-------|---------|-------------|
| `INSTALLED` | Hook config references this skill (or its script path) | None. Continue |
| `MISSING_CONFIG_FILE` | No config file for active agent | `install-snippet.sh <agent>` then merge |
| `MISSING_HOOK_ENTRY` | Config exists, no entry for this skill | Merge block from `references/<agent>-integration.md` |

Output (stdout single-line + stderr detailed):

```
<user-self-improving-hook-state>STATE</user-self-improving-hook-state>
```

The script never edits config files — installation is the human's call.

## §5 Entry Format (`.learnings/*.md`)

Same as `project-self-improving` §5. Three file types:

- `LEARNINGS.md` — corrections, knowledge gaps, best practices
- `ERRORS.md` — command / API / tool failures
- `FEATURE_REQUESTS.md` — user-stated capability gaps

Entry schema:

```markdown
## [LRN|ERR|FEAT-YYYYMMDD-XXX] category

**Logged**: ISO-8601 timestamp
**Priority**: low | medium | high | critical
**Status**: pending | in_progress | resolved | wont_fix | promoted
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description

### Details
Full context

### Suggested Action / Fix
Concrete next step

### Metadata
- Source: conversation | error | user_feedback
- Related Files: path/to/file.ext
- Tags: tag1, tag2
- See Also: TYPE-YYYYMMDD-XXX (if related)

---
```

See [references/examples.md](references/examples.md) for the full set.

## §6 Personal Workspace Files (opt-in)

| File | Purpose | When to write | When NOT to write |
|------|---------|---------------|-------------------|
| `SOUL.md` | Personal style / tone / communication preferences | You notice an agent output tone you want to lock in | Team-shared conventions (use `AGENTS.md` instead) |
| `TOOLS.md` | Personal tool gotchas / env quirks on this machine | Specific machine has issues (e.g. WSL2 DNS weird) | Generic tool knowledge (use `CLAUDE.md` / `AGENTS.md` instead) |
| `MEMORY.md` | Long-term personal reflection / preferences | You want continuity across all projects on this machine | Project-specific decisions (use `AGENTS.md` / `.trae/rules/<topic>.md`) |

> **Critical:** These files are **personal expression**, not rules for the agent
> to follow. They tell the agent about *your* style. They do NOT replace
> `AGENTS.md` / `CLAUDE.md` / `.trae/rules/*.md` (those are rule files the
> agent loads at session start).
>
> Original inspiration: the `~/.openclaw/workspace/{SOUL,TOOLS,MEMORY}.md`
> pattern from openclaw-style runtimes. This skill uses the same **names** for
> ergonomic continuity but is **not** bound to openclaw — see
> [references/legacy-openclaw-handler.md](references/legacy-openclaw-handler.md)
> for the original handler.

## §7 ID Generation

Format: `TYPE-YYYYMMDD-XXX`
- `TYPE`: `LRN` / `ERR` / `FEAT`
- `YYYYMMDD`: current date
- `XXX`: sequential 3-digit or random 3 chars

## §8 Detection Triggers

When to log — same as `project-self-improving` §9:

- User corrections ("No, that's wrong...") → LRN
- Feature requests ("Can you also...") → FEAT
- Knowledge gaps (user provides info you didn't know) → LRN
- Command / API errors (non-zero exit / exceptions) → ERR

## §9 Priority / Area Tags

Same as `project-self-improving` §10 / §11.

## §10 Relationship with `project-self-improving`

| Aspect | `project-self-improving` | `user-self-improving` (this) |
|--------|-------------------------|----------------------------|
| Scope | Project-local (per-repo) | User-local (per-machine) |
| Default path | `<repo>/.learnings/` | `$HOME/.user-self-improving/.learnings/` |
| Sharing | Team-committed (if `.learnings/` not gitignored) | Personal only |
| Promotion | `AGENTS.md` / `CLAUDE.md` / `.trae/rules/*.md` | `SOUL.md` / `TOOLS.md` / `MEMORY.md` (personal) |
| Default install | Should be installed for most repos | Opt-in per machine |
| Use when | Working on a team repo with shared learnings | Want continuity across all repos on this machine |

**Recommendation:** install ONE of them per repo to avoid double-logging. If
both are installed, use distinct `--home` paths or use project-only inside
repos with `project-self-improving` and only the global home outside.

## §11 Multi-Agent Matrix

Same as `project-self-improving` §13. The four scripts (activator /
error-detector / hook-self-check / install-snippet) work for any agent; only
the hook config snippet differs. See [references/multi-agent-matrix.md](references/multi-agent-matrix.md)
for activation cost + cross-machine strategy.

## §12 Best Practices

Full list: [`references/best-practices.md`](references/best-practices.md). Top
5:

1. Log immediately (context freshest).
2. Self-check before complaining (`hook-self-check.sh`).
3. Keep `SOUL.md` / `TOOLS.md` small — personal, not encyclopedic.
4. Don't share personal workspace files via git.
5. Review monthly — promote cross-machine patterns to global `CLAUDE.md` if
   they generalize beyond personal style.

## §13 Files In This Package

Run `tree -L 2 skill-markets/user-self-improving/` for the live file tree, or
see [`assets/SKILL-TEMPLATE.md`](assets/SKILL-TEMPLATE.md) §"Required Files".

## §14 Skill Extraction

Same as `project-self-improving` §16 — a learning qualifies for extraction
when recurring + verified + non-obvious + broadly applicable + user-flagged.

Workflow + checklist: [assets/SKILL-TEMPLATE.md](assets/SKILL-TEMPLATE.md).

## §15 See Also

- [`references/hook-self-check.md`](references/hook-self-check.md) — self-check protocol deep-dive
- [`references/multi-agent-matrix.md`](references/multi-agent-matrix.md) — 4 agent 接入成本对比
- [`references/legacy-openclaw-handler.md`](references/legacy-openclaw-handler.md) — original OpenClaw handler (deprecated reference only)
- [`assets/SKILL-TEMPLATE.md`](assets/SKILL-TEMPLATE.md) — skill extraction template
- [`../project-self-improving/SKILL.md`](../project-self-improving/SKILL.md) — project-local companion skill
- `todos/task.md` — open items + migration notes from original `self-improving-agent`