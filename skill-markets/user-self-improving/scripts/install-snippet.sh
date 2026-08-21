#!/usr/bin/env bash
# scripts/install-snippet.sh — 打印目标 agent 的 hook config 片段(由用户合并)
#                             (user-self-improving skill §3)
#
# 设计目的(2026-08-21):
#   每个 agent 的 hook config 格式不同,本脚本根据参数打印对应片段到 stdout,
#   用户重定向到目标文件即可。
#
#   注意 — 本脚本**不修改任何文件**(防止误覆盖用户已有配置)。
#   强制人工确认重定向目标。
#
# 用法(user-level 默认 — 个人路径):
#   bash scripts/install-snippet.sh trae-user              # Trae → ~/.trae-cn/hooks.json
#   bash scripts/install-snippet.sh claude-user           # Claude Code → ~/.claude/settings.json
#   bash scripts/install-snippet.sh codex-user            # Codex → ~/.codex/settings.json
#   bash scripts/install-snippet.sh trae-user > ~/.trae-cn/hooks.json
#
# 用法(project-level — 限定本项目):
#   bash scripts/install-snippet.sh trae-project          # Trae → .trae/hooks.json
#   bash scripts/install-snippet.sh claude-project       # Claude Code → .claude/settings.json
#   bash scripts/install-snippet.sh codex-project        # Codex → .codex/settings.json
#
# 用法(无 hook runtime):
#   bash scripts/install-snippet.sh copilot               # .github/copilot-instructions.md
#
# 跨平台: POSIX sh,无依赖。

set -u

agent="${1:-}"

# 个人技能路径用 ${userHome} (Trae) 或 ~/<dir> (Claude/Codex)
USER_PATH="${HOME}"

case "$agent" in
  trae-user)
    cat <<JSON
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "\${userHome}/.trae-cn/skills/user-self-improving/scripts/hook-self-check.sh",
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
            "command": "\${userHome}/.trae-cn/skills/user-self-improving/scripts/activator.sh",
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
            "command": "\${userHome}/.trae-cn/skills/user-self-improving/scripts/error-detector.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
JSON
    ;;
  trae-project)
    cat <<JSON
{
  "version": 1,
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/hook-self-check.sh",
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
            "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/activator.sh",
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
            "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/error-detector.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
JSON
    ;;
  claude-user)
    cat <<JSON
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "~/.claude/skills/user-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "~/.claude/skills/user-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
    ;;
  claude-project)
    cat <<JSON
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
    ;;
  codex-user)
    cat <<JSON
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "~/.codex/skills/user-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "~/.codex/skills/user-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
    ;;
  codex-project)
    cat <<JSON
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/activator.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "\${workspaceFolder}/skill-markets/user-self-improving/scripts/error-detector.sh" }
        ]
      }
    ]
  }
}
JSON
    ;;
  copilot|github-copilot)
    cat <<'MD'
# Add to .github/copilot-instructions.md (per-repo — note: Copilot has no
# user-level config so this is the closest equivalent for personal capture).

## User Self-Improving (personal experience ledger)

After completing tasks that involved:
- Debugging non-obvious issues
- Discovering workarounds
- Learning project-specific patterns
- Resolving unexpected errors

Consider logging the learning to `~/.user-self-improving/.learnings/`
(or `$HOME/.user-self-improving/.learnings/`) using the format from
the user-self-improving skill.

For personal style / machine gotchas / long-term reflection, write to
`~/.user-self-improving/{SOUL,TOOLS,MEMORY}.md` (opt-in).

Also review `~/.user-self-improving/.learnings/` for related entries
before starting a major task.
MD
    ;;
  *)
    cat >&2 <<EOF
Usage: $0 <agent>
  user-level (personal, recommended):
    trae-user         - Trae IDE → ~/.trae-cn/hooks.json
    claude-user       - Claude Code → ~/.claude/settings.json
    codex-user        - Codex CLI → ~/.codex/settings.json
  project-level (per-repo):
    trae-project      - Trae IDE → .trae/hooks.json
    claude-project    - Claude Code → .claude/settings.json
    codex-project     - Codex CLI → .codex/settings.json
  manual (no runtime):
    copilot           - GitHub Copilot → .github/copilot-instructions.md

NOTE: This script only PRINTS the snippet. It does NOT modify any file.
To install:
  bash $0 trae-user > ~/.trae-cn/hooks.json
  bash $0 claude-user > ~/.claude/settings.json
  bash $0 codex-user > ~/.codex/settings.json
  bash $0 copilot >> .github/copilot-instructions.md
EOF
    exit 1
    ;;
esac

exit 0