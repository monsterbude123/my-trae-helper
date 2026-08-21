#!/usr/bin/env bash
# scripts/hook-self-check.sh — Mandatory session-start hook self-check
#                            (project-self-improving skill §4)
#
# 设计目的(2026-08-21):
#   探测 4 类 agent 的 hook config 文件是否引用本 skill 的任意脚本,
#   报告 1 个 3 状态结果(INSTALLED / MISSING_CONFIG_FILE / MISSING_HOOK_ENTRY)。
#
# 探测顺序(按本仓库优先级):
#   1. .trae/hooks.json         — Trae IDE(本市场主)
#   2. .claude/settings.json    — Claude Code
#   3. .codex/settings.json     — Codex CLI
#   4. .github/copilot-instructions.md — Copilot(无 hook,期望 MISSING)
#
# 匹配规则(任一命中 → INSTALLED):
#   - 含字面 "project-self-improving"
#   - 含字面 "scripts/activator.sh" / "scripts/error-detector.sh" / "scripts/hook-self-check.sh"
#
# 输出格式(stdout 一行 + stderr 详细 remediation):
#   <self-improving-hook-state>STATE</self-improving-hook-state>
#
# 退出码:
#   0 = INSTALLED
#   1 = MISSING_CONFIG_FILE 或 MISSING_HOOK_ENTRY
#
# 跨平台: POSIX sh + grep + sed,无 Python/Node 依赖。
# 来源:本文件与 scripts/detect-python.sh 同款跨平台协议。

set -u

# 跨平台 EOL(BSD/GNU 兼容)
if echo | sed --version >/dev/null 2>&1; then
  _SED_INPLACE=(-i)
else
  _SED_INPLACE=(-i '')
fi

WORKSPACE="${PWD}"

# 任意路径包含本 skill 的脚本路径 → 视为 INSTALLED
_SCRIPT_SIGNATURES=(
  "project-self-improving"
  "scripts/activator.sh"
  "scripts/error-detector.sh"
  "scripts/hook-self-check.sh"
  "scripts/install-snippet.sh"
)

_probe_config_file() {
  local cfg="$1"
  local label="$2"
  # 1. 文件不存在 → MISSING_CONFIG_FILE(仅当此为最终回退时报)
  if [ ! -f "$cfg" ]; then
    return 1
  fi
  # 2. 文件存在但内容仅含空白(如 "" / "{}" / "{}\n") → 显式无 hooks = 合规
  #    因为空 hooks.json 是合法配置,不应被报告为 MISSING。
  #    用 grep -q 排除 — 只有"含字面签名"才算 MISSING_HOOK_ENTRY。
  local trimmed
  trimmed=$(tr -d '[:space:]' < "$cfg" 2>/dev/null | tr -d '{}')
  if [ -z "$trimmed" ]; then
    echo "INSTALLED"  # 空配置 = 显式无 hooks = 合规
    return 0
  fi
  # 3. 含任一 signature → INSTALLED
  for sig in "${_SCRIPT_SIGNATURES[@]}"; do
    if grep -q -F "$sig" "$cfg" 2>/dev/null; then
      echo "INSTALLED"
      return 0
    fi
  done
  # 4. 文件存在但无 hook 引用 → MISSING_HOOK_ENTRY(label 标注哪个 agent)
  echo "MISSING_HOOK_ENTRY:$label:$cfg"
  return 2
}

_main() {
  local state="MISSING_CONFIG_FILE"
  local detail="no config file for any target agent"
  local exit_code=1

  # 按优先级探测
  for cfg_label in \
    ".trae/hooks.json:trae" \
    ".claude/settings.json:claude-code" \
    ".codex/settings.json:codex"; do
    cfg="${cfg_label%%:*}"
    label="${cfg_label##*:}"
    result=$(_probe_config_file "$WORKSPACE/$cfg" "$label") || true
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
        # 不 break — 让更高优先级 agent 继续尝试(罕见边界:同一项目配多 agent)
        ;;
    esac
  done

  # 单独检查 Copilot(无 hook runtime,期望 MISSING_CONFIG_FILE)
  if [ "$state" = "MISSING_CONFIG_FILE" ]; then
    copilot_cfg="$WORKSPACE/.github/copilot-instructions.md"
    if [ -f "$copilot_cfg" ] && grep -q -F "project-self-improving" "$copilot_cfg" 2>/dev/null; then
      state="INSTALLED"
      detail=".github/copilot-instructions.md"
      exit_code=0
    fi
  fi

  # 输出主状态(单行,XML-style)
  echo "<self-improving-hook-state>$state</self-improving-hook-state>"

  # 详细 remediation(stderr — agent 应捕获并 surface 给用户)
  case "$state" in
    INSTALLED)
      : # 静默,不刷屏
      ;;
    MISSING_CONFIG_FILE)
      cat >&2 <<'EOF'
[self-improving] hook not installed (no config file found)
  remediation:
    bash skill-markets/project-self-improving/scripts/install-snippet.sh trae       # Trae IDE
    bash skill-markets/project-self-improving/scripts/install-snippet.sh claude-code # Claude Code
    bash skill-markets/project-self-improving/scripts/install-snippet.sh codex       # Codex CLI
    # Copilot 走 .github/copilot-instructions.md(无 hook runtime)
EOF
      ;;
    MISSING_HOOK_ENTRY)
      cat >&2 <<EOF
[self-improving] hook config exists but no entry for this skill
  config:   $detail
  fix:      merge snippet from skill-markets/project-self-improving/references/<agent>-integration.md
  alt:      bash skill-markets/project-self-improving/scripts/install-snippet.sh $(echo "$detail" | awk -F: '{print $2}')
EOF
      ;;
  esac

  exit "$exit_code"
}

_main "$@"