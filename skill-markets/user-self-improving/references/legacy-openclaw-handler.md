# Legacy OpenClaw Handler (DEPRECATED — reference only)

> **Status:** DEPRECATED as of 2026-08-21. The original `self-improving-agent`
> skill was tightly coupled to OpenClaw — a specific agent runtime with
> workspace files at `~/.openclaw/workspace/` and a custom hook protocol
> (`event.context.bootstrapFiles.push({virtual: true})`).
>
> This document preserves the **original handler implementation** as a
> historical reference. **Do not use it.** It will not work with any current
> agent (Trae / Claude Code / Codex / Copilot) without significant changes.

## Original Handler (preserved verbatim)

### `hooks/openclaw/HOOK.md`

```markdown
---
name: self-improvement
description: "Injects self-improvement reminder during agent bootstrap"
metadata: {"openclaw":{"emoji":"🧠","events":["agent:bootstrap"]}}
---

# Self-Improvement Hook

Injects a reminder to evaluate learnings during agent bootstrap.

## What It Does

- Fires on `agent:bootstrap` (before workspace files are injected)
- Adds a reminder block to check `.learnings/` for relevant entries
- Prompts the agent to log corrections, errors, and discoveries

## Configuration

No configuration needed. Enable with:

\`\`\`bash
openclaw hooks enable self-improvement
\`\`\`
```

### `hooks/openclaw/handler.ts`

```typescript
/**
 * Self-Improvement Hook for OpenClaw
 *
 * Injects a reminder to evaluate learnings during agent bootstrap.
 * Fires on agent:bootstrap event before workspace files are injected.
 */

import type { HookHandler } from 'openclaw/hooks';

const REMINDER_CONTENT = `## Self-Improvement Reminder

After completing tasks, evaluate if any learnings should have been captured:

**Log when:**
- User corrects you → \`.learnings/LEARNINGS.md\`
- Command/operation fails → \`.learnings/ERRORS.md\`
- User wants missing capability → \`.learnings/FEATURE_REQUESTS.md\`
- You discover your knowledge was wrong → \`.learnings/LEARNINGS.md\`
- You find a better approach → \`.learnings/LEARNINGS.md\`

**Promote when pattern is proven:**
- Behavioral patterns → \`SOUL.md\`
- Workflow improvements → \`AGENTS.md\`
- Tool gotchas → \`TOOLS.md\`

Keep entries simple: date, title, what happened, what to do differently.`;

const handler: HookHandler = async (event) => {
  if (!event || typeof event !== 'object') return;
  if (event.type !== 'agent' || event.action !== 'bootstrap') return;
  if (!event.context || typeof event.context !== 'object') return;
  const sessionKey = event.sessionKey || '';
  if (sessionKey.includes(':subagent:')) return;
  if (Array.isArray(event.context.bootstrapFiles)) {
    event.context.bootstrapFiles.push({
      path: 'SELF_IMPROVEMENT_REMINDER.md',
      content: REMINDER_CONTENT,
      virtual: true,
    });
  }
};

export default handler;
```

### `hooks/openclaw/handler.js` (CommonJS mirror)

Same logic as `handler.ts` but as plain JS for runtime without TS.

## Why It's Deprecated

| Aspect | Original (OpenClaw) | New (`user-self-improving`) |
|--------|--------------------|-------------------------|
| Hook protocol | `event.context.bootstrapFiles` (custom) | Native (`UserPromptSubmit` / `PostToolUse`) |
| Workspace files | `~/.openclaw/workspace/{AGENTS,SOUL,TOOLS,MEMORY}.md` | `$HOME/.user-self-improving/{SOUL,TOOLS,MEMORY}.md` (opt-in) |
| Agent binding | OpenClaw-only | Trae / Claude Code / Codex / Copilot |
| Self-check | none | `hook-self-check.sh` (3 states) |
| Path resolution | assumed `~/.openclaw/` | explicit `$HOME` resolution |

## Migration

If you were using the original skill with OpenClaw:

1. Uninstall OpenClaw hook: `openclaw hooks disable self-improvement`
2. Migrate `~/.openclaw/workspace/SOUL.md` → `~/.user-self-improving/SOUL.md`
3. Migrate `~/.openclaw/workspace/TOOLS.md` → `~/.user-self-improving/TOOLS.md`
4. Migrate `~/.openclaw/workspace/MEMORY.md` → `~/.user-self-improving/MEMORY.md`
5. Migrate `~/.openclaw/workspace/.learnings/` → `~/.user-self-improving/.learnings/`
6. Install the new skill: `node bin/cli.mjs add user-self-improving -a trae-cn`
7. Wire hook (see [references/trae-integration.md](trae-integration.md))
8. Run `bash <skill>/scripts/hook-self-check.sh` to verify

## File Locations

The original handlers lived in `skill-markets/user-self-improving/hooks/openclaw/`
prior to 2026-08-21. They've been **moved out** of the active skill directory
(this reference document replaces them). If you need to re-create them for an
OpenClaw environment, restore from git history:

```bash
git log --all --oneline -- skill-markets/user-self-improving/hooks/openclaw/
```

## See Also

- [SKILL.md §1 What This Skill Does (and Does Not)](../SKILL.md#1-what-this-skill-does-and-does-not)
- [SKILL.md §6 Personal Workspace Files](../SKILL.md#6-personal-workspace-files-opt-in) — explains the new "personal expression" framing
- [../project-self-improving/SKILL.md](../project-self-improving/SKILL.md) — the project-scoped companion