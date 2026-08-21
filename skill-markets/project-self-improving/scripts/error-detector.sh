#!/usr/bin/env bash
# scripts/error-detector.sh — Trae / Claude Code PostToolUse (Bash) 错误捕获
#                            (project-self-improving skill §3)
#
# 设计目的(2026-08-21):
#   在 PostToolUse: Bash 事件触发时,检查工具输出中是否含失败信号
#   (non-zero exit code / 常见错误关键词),若有 → 输出 reminder
#   提示用户/agent 考虑写一条 ERR entry。
#
# 输入约定:
#   Trae/Claude Code 把工具输出以 stdin/CLAUDE_TOOL_OUTPUT 环境变量传入。
#   本脚本同时支持 stdin 与环境变量(Trae 可能用其中之一)。
#
# 输出格式(stdout):与 activator 同 一,XML-style reminder block。
#
# 跨平台: POSIX sh + grep,无 Python/Node 依赖。

set -u

# 优先级: stdin > CLAUDE_TOOL_OUTPUT > TRAE_TOOL_OUTPUT > TOOL_OUTPUT
INPUT_SOURCE="stdin"
PAYLOAD=""
if [ -n "${CLAUDE_TOOL_OUTPUT:-}" ]; then
  PAYLOAD="$CLAUDE_TOOL_OUTPUT"
  INPUT_SOURCE="CLAUDE_TOOL_OUTPUT"
elif [ -n "${TRAE_TOOL_OUTPUT:-}" ]; then
  PAYLOAD="$TRAE_TOOL_OUTPUT"
  INPUT_SOURCE="TRAE_TOOL_OUTPUT"
elif [ ! -t 0 ]; then
  PAYLOAD="$(cat)"
  INPUT_SOURCE="stdin"
else
  # 无输入,直接退出(非错误)
  exit 0
fi

# 失败信号检测(规则集 — 与项目侧 scripts/self-improving-agent.mjs §2 一致)
ERROR_PATTERNS=(
  '\[FATAL_ERROR\]'
  'command not found'
  'enoent'
  'eacces'
  'eperm'
  'syntax error'
  'permission denied'
  'timed out'
  'connection refused'
  'no such file'
)

FOUND=""
for pat in "${ERROR_PATTERNS[@]}"; do
  if echo "$PAYLOAD" | grep -q -F "$pat" 2>/dev/null; then
    FOUND="$pat"
    break
  fi
done

# 也检测 exit code 模式(独立 grep,因为含空格)
if [ -z "$FOUND" ]; then
  if echo "$PAYLOAD" | grep -E -q 'exit(ed)? (with code )?(1|2|127|128|130|137|139|143)\b' 2>/dev/null; then
    FOUND="exit-code"
  fi
fi

# 未发现失败 → 静默退出
if [ -z "$FOUND" ]; then
  exit 0
fi

# 输出 reminder
cat <<REMINDER
<self-improving-error-detected>
Source: $INPUT_SOURCE
Signal: $FOUND
</self-improving-error-detected>

<self-improving-error-reminder>
Tool output contained an error signal. Consider logging it to `.learnings/ERRORS.md`:

\`\`\`markdown
## [ERR-\$(date -u +%Y%m%d)-XXX] <command_name>

**Logged**: \$(date -u +%Y-%m-%dT%H:%M:%SZ)
**Priority**: high
**Status**: pending
**Area**: <frontend|backend|infra|tests|docs|config>

### Summary
<one-line description>

### Error
\\\`\\\`\\\`
<output snippet>
\\\`\\\`\\\`

### Context
- Command: <what was run>
- Source: $INPUT_SOURCE
- Signal: $FOUND

### Suggested Fix
<what might resolve this>

### Metadata
- Reproducible: <yes|no|unknown>
- Source: post_tool_error_detector
- Tags: auto-captured
\`\`\`

See `skill-markets/project-self-improving/SKILL.md §5` for the full format.
</self-improving-error-reminder>
REMINDER

exit 0