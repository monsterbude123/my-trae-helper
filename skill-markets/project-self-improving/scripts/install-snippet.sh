#!/usr/bin/env bash
# scripts/install-snippet.sh — 打印目标 agent 的 hook config 片段(由用户合并)
#                             (project-self-improving skill §3)
#
# 设计目的(2026-08-21):
#   每个 agent 的 hook config 格式不同,本脚本根据参数打印对应片段到 stdout,
#   用户重定向到目标文件(如 .trae/hooks.json)即可。
#
#   注意 — 本脚本**不修改任何文件**(防止误覆盖用户已有配置)。
#   强制人工确认重定向目标。
#
# 用法:
#   bash scripts/install-snippet.sh trae              # 打印 Trae .trae/hooks.json
#   bash scripts/install-snippet.sh trae > .trae/hooks.json   # 推荐:首次安装
#   bash scripts/install-snippet.sh claude-code       # 打印 Claude Code .claude/settings.json
#   bash scripts/install-snippet.sh codex             # 打印 Codex .codex/settings.json
#   bash scripts/install-snippet.sh copilot           # 打印 Copilot instructions
#
# 跨平台: POSIX sh,无依赖。

set -u

agent="${1:-}"

case "$agent" in
  trae|trae-ide)
    cat <<'JSON'
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/hook-self-check.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/error-detector.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
JSON
    ;;
  claude-code|claude)
    cat <<'JSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
    ;;
  codex)
    cat <<'JSON'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "${workspaceFolder}/skill-markets/project-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
    ;;
  copilot|github-copilot)
    cat <<'MD'
# Add to .github/copilot-instructions.md

## Self-Improvement (project-self-improving skill)

After completing tasks that involved:
- Debugging non-obvious issues
- Discovering workarounds
- Learning project-specific patterns
- Resolving unexpected errors

Consider logging the learning to `.learnings/` (or
`$HOME/.self-improving-agent/.learnings/` if global mode is active) using
the format from the project-self-improving skill.

For high-value learnings that would benefit other sessions, consider
**skill extraction** (see
`skill-markets/project-self-improving/assets/SKILL-TEMPLATE.md`).

Also review `.learnings/` for related issues before starting a major task.
MD
    ;;
  *)
    cat >&2 <<EOF
Usage: $0 <agent>
  agents:
    trae         - Trae IDE → .trae/hooks.json
    claude-code  - Claude Code → .claude/settings.json
    codex        - Codex CLI → .codex/settings.json
    copilot      - GitHub Copilot → .github/copilot-instructions.md

NOTE: This script only PRINTS the snippet. It does NOT modify any file.
To install:
  bash $0 trae > .trae/hooks.json           # Trae
  bash $0 claude-code > .claude/settings.json
  bash $0 codex > .codex/settings.json
  bash $0 copilot >> .github/copilot-instructions.md  # append
EOF
    exit 1
    ;;
esac

exit 0