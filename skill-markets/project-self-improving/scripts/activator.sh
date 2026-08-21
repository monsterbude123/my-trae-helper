#!/usr/bin/env bash
# scripts/activator.sh — Trae UserPromptSubmit / Claude Code UserPromptSubmit 注入提醒
#                       (project-self-improving skill §3)
#
# 设计目的(2026-08-21):
#   在 UserPromptSubmit / SessionStart 事件触发时,向 agent 上下文注入一段紧凑的
#   提醒(50~100 tokens overhead),促使 agent 在每次响应前评估是否需要写
#   .learnings/{LEARNINGS,ERRORS,FEATURE_REQUESTS}.md。
#
# 输出格式(stdout):
#   <self-improving-reminder>...</self-improving-reminder>
#
# 同时跑 hook-self-check.sh 子检查,如配置缺失 → 在 reminder 后追加 remediation block。
#
# 跨平台: POSIX sh + grep,无 Python/Node 依赖。
# 来源:本文件与 scripts/detect-python.sh / detect-node.sh 同款跨平台协议。

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd 2>/dev/null || echo "$(dirname "$0")")"

# 主 reminder block(精简,~80 tokens)
cat <<'REMINDER'
<self-improving-reminder>
After completing tasks, evaluate if any learnings should be captured:

**Log when:**
- User corrects you → `.learnings/LEARNINGS.md` (category `correction`)
- Command/operation fails → `.learnings/ERRORS.md`
- User wants missing capability → `.learnings/FEATURE_REQUESTS.md`
- You discover your knowledge was wrong → `.learnings/LEARNINGS.md` (category `knowledge_gap`)
- You find a better approach → `.learnings/LEARNINGS.md` (category `best_practice`)

**Promote when pattern is proven (only to files the active agent reads):**
- Workflow improvements → `AGENTS.md` (or `.trae/rules/<topic>.md` for Trae projects)
- Tool gotchas → `CLAUDE.md` or `.github/copilot-instructions.md`
- Behavioral style → `AGENTS.md` / `CLAUDE.md` (NOT `SOUL.md`/`TOOLS.md`)

Keep entries simple: date, title, what happened, what to do differently.
Format: see `skill-markets/project-self-improving/SKILL.md §5`.
</self-improving-reminder>
REMINDER

# 子检查:hook 是否安装 — 缺失则在 reminder 后追加单行告警
if [ -f "$SCRIPT_DIR/hook-self-check.sh" ]; then
  check_output=$(bash "$SCRIPT_DIR/hook-self-check.sh" 2>&1)
  check_exit=$?
  if [ "$check_exit" -ne 0 ]; then
    cat <<'NOTE'

<self-improving-hook-warning>
Hook not installed for the active agent. Reminders won't fire automatically.
Run: `bash skill-markets/project-self-improving/scripts/install-snippet.sh <agent>`
See: `skill-markets/project-self-improving/references/<agent>-integration.md`
</self-improving-hook-warning>
NOTE
  fi
fi

exit 0