#!/usr/bin/env bash
# scripts/hook-self-check.sh — Mandatory session-start hook self-check
#                            (user-self-improving skill §4)
#
# 设计目的(2026-08-21):
#   探测 4 类 agent 的 hook config 文件是否引用本 skill 的任意脚本,
#   报告 1 个 3 状态结果(INSTALLED / MISSING_CONFIG_FILE / MISSING_HOOK_ENTRY)。
#
# 探测顺序(按 user-level 优先,因为这是 personal skill):
#   1. ~/.trae-cn/hooks.json      — Trae user-level
#   2. .trae/hooks.json           — Trae project-level
#   3. ~/.claude/settings.json    — Claude Code user-level
#   4. .claude/settings.json      — Claude Code project-level
#   5. ~/.codex/settings.json     — Codex user-level
#   6. .codex/settings.json       — Codex project-level
#   7. ~/.user-self-improving/SOUL.md — fallback(若 SOUL/TOOLS/MEMORY 任意一个存在,
#                                          说明用户已主动初始化,视为 INSTALLED)
#
# 匹配规则:
#   - 含字面 "user-self-improving"
#   - 含字面 "scripts/activator.sh" / "scripts/error-detector.sh" /
#     "scripts/hook-self-check.sh" / "scripts/install-snippet.sh"
#
# 输出格式(stdout):
#   <user-self-improving-hook-state>STATE</user-self-improving-hook-state>
#
# 退出码:
#   0 = INSTALLED
#   1 = MISSING_CONFIG_FILE 或 MISSING_HOOK_ENTRY
#
# 跨平台: POSIX sh + grep + sed,无 Python/Node 依赖。

set -u

WORKSPACE="${PWD}"
USER_HOME="${HOME:-}"

_SCRIPT_SIGNATURES=(
  "user-self-improving"
  "scripts/activator.sh"
  "scripts/error-detector.sh"
  "scripts/hook-self-check.sh"
  "scripts/install-snippet.sh"
)

_probe_config_file() {
  local cfg="$1"
  local label="$2"
  if [ ! -f "$cfg" ]; then
    return 1
  fi
  local trimmed
  trimmed=$(tr -d '[:space:]' < "$cfg" 2>/dev/null | tr -d '{}')
  if [ -z "$trimmed" ]; then
    echo "INSTALLED"
    return 0
  fi
  for sig in "${_SCRIPT_SIGNATURES[@]}"; do
    if grep -q -F "$sig" "$cfg" 2>/dev/null; then
      echo "INSTALLED"
      return 0
    fi
  done
  echo "MISSING_HOOK_ENTRY:$label:$cfg"
  return 2
}

_main() {
  local state="MISSING_CONFIG_FILE"
  local detail="no config file for any target agent"
  local exit_code=1

  for cfg_label in \
    "$HOME/.trae-cn/hooks.json:trae-user" \
    ".trae/hooks.json:trae-project" \
    "$HOME/.claude/settings.json:claude-user" \
    ".claude/settings.json:claude-project" \
    "$HOME/.codex/settings.json:codex-user" \
    ".codex/settings.json:codex-project"; do
    cfg="${cfg_label%%:*}"
    label="${cfg_label##*:}"
    result=$(_probe_config_file "$cfg" "$label") || true
    case "$result" in
      INSTALLED)
        state="INSTALLED"
        detail="$cfg"
        exit_code=0
        break
        ;;
      MISSING_HOOK_ENTRY:*)
        state="MISSING_HOOK_ENTRY"
        detail="${result#MISSING_HOOK_ENTRY:}"
        exit_code=1
        ;;
    esac
  done

  # Fallback: 检查 SOUL/TOOLS/MEMORY 是否存在(用户主动初始化的信号)
  if [ "$state" != "INSTALLED" ] && [ -n "$USER_HOME" ]; then
    for ws in "$USER_HOME/.user-self-improving/SOUL.md" \
              "$USER_HOME/.user-self-improving/TOOLS.md" \
              "$USER_HOME/.user-self-improving/MEMORY.md"; do
      if [ -f "$ws" ]; then
        state="INSTALLED"
        detail="$ws"
        exit_code=0
        break
      fi
    done
  fi

  echo "<user-self-improving-hook-state>$state</user-self-improving-hook-state>"

  case "$state" in
    INSTALLED)
      : # 静默
      ;;
    MISSING_CONFIG_FILE)
      cat >&2 <<'EOF'
[user-self-improving] hook not installed (no config file found)
  remediation:
    bash skill-markets/user-self-improving/scripts/install-snippet.sh trae-user      # Trae user-level
    bash skill-markets/user-self-improving/scripts/install-snippet.sh trae-project   # Trae project-level
    bash skill-markets/user-self-improving/scripts/install-snippet.sh claude-user    # Claude Code user-level
    bash skill-markets/user-self-improving/scripts/install-snippet.sh claude-project # Claude Code project-level
    bash skill-markets/user-self-improving/scripts/install-snippet.sh codex-user     # Codex user-level
    bash skill-markets/user-self-improving/scripts/install-snippet.sh codex-project  # Codex project-level
    # Copilot 走 .github/copilot-instructions.md(无 hook runtime)
EOF
      ;;
    MISSING_HOOK_ENTRY)
      cat >&2 <<EOF
[user-self-improving] hook config exists but no entry for this skill
  config:   $detail
  fix:      merge snippet from skill-markets/user-self-improving/references/<agent>-integration.md
EOF
      ;;
  esac

  exit "$exit_code"
}

_main "$@"