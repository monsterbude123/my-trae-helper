#!/usr/bin/env bash
# scripts/activator.sh — UserPromptSubmit / SessionStart 注入提醒
#                       (user-self-improving skill §3)
#
# 设计目的(2026-08-21):
#   在 UserPromptSubmit / SessionStart 事件触发时,向 agent 上下文注入一段紧凑的
#   提醒(~80 tokens),促使 agent 在每次响应前评估是否需要写
#   $HOME/.user-self-improving/.learnings/{LEARNINGS,ERRORS,FEATURE_REQUESTS}.md。
#
# 输出格式(stdout):
#   <user-self-improving-reminder>...</user-self-improving-reminder>
#
# 同时跑 hook-self-check.sh 子检查,如配置缺失 → 追加 remediation block。
#
# 跨平台: POSIX sh + grep,无 Python/Node 依赖。

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd 2>/dev/null || echo "$(dirname "$0")")"

cat <<'REMINDER'
<user-self-improving-reminder>
After completing tasks, evaluate if any learnings should be captured (personal, cross-project ledger):

**Log when:**
- User corrects you → `$HOME/.user-self-improving/.learnings/LEARNINGS.md` (category `correction`)
- Command/operation fails → `.../ERRORS.md`
- User wants missing capability → `.../FEATURE_REQUESTS.md`
- You discover your knowledge was wrong → `.../LEARNINGS.md` (category `knowledge_gap`)
- You find a better approach → `.../LEARNINGS.md` (category `best_practice`)
- Machine-specific quirk discovered → `$HOME/.user-self-improving/TOOLS.md` (opt-in)
- Personal style preference → `$HOME/.user-self-improving/SOUL.md` (opt-in)
- Long-term reflection → `$HOME/.user-self-improving/MEMORY.md` (opt-in)

**Promote only to personal files** (do not pollute AGENTS.md / CLAUDE.md unless you ALSO have
project-self-improving installed for project-shared patterns):
- Personal style/tool/long-term → SOUL.md / TOOLS.md / MEMORY.md
- Cross-project best practice → extract as new skill (see assets/SKILL-TEMPLATE.md)

Keep entries simple: date, title, what happened, what to do differently.
Format: see `skill-markets/user-self-improving/SKILL.md §5`.
</user-self-improving-reminder>
REMINDER

# 子检查
if [ -f "$SCRIPT_DIR/hook-self-check.sh" ]; then
  check_output=$(bash "$SCRIPT_DIR/hook-self-check.sh" 2>&1)
  check_exit=$?
  if [ "$check_exit" -ne 0 ]; then
    cat <<'NOTE'

<user-self-improving-hook-warning>
Hook not installed for the active agent. Reminders won't fire automatically.
Run: `bash skill-markets/user-self-improving/scripts/install-snippet.sh <agent>`
See: `skill-markets/user-self-improving/references/<agent>-integration.md`
</user-self-improving-hook-warning>
NOTE
  fi
fi

exit 0