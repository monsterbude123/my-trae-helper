#!/usr/bin/env bash
# scripts/detect-node.sh — 跨平台 Node.js 探测 + 能力校验(供 hook-self-check 复用)
#
# 设计原则(2026-08-21 user-self-improving 自带版本,与 project-self-improving 同款协议):
#   1. 跨平台: PATH + 平台典型位置(由 uname 动态生成),带能力校验
#   2. 仅信 PATH + 平台典型安装位置,绝不写死具体路径
#   3. 能力校验失败 → 报错并退出(不静默降级到 stub)
#   4. 导出到 MY_NODE 供子脚本拾取
#
# 用法:
#   . "$(dirname "$0")/detect-node.sh" || exit 1
#
# 失败语义: 真找不到 → 打印明确错误 + exit 1

# 必须在已 source 进的 shell 中写回 $MY_NODE
MY_NODE=""

_candidates() {
  if [ -x /mnt/c/Windows/System32/cmd.exe ] || [ -x /c/Windows/System32/cmd.exe ]; then
    echo "/mnt/c/ProgramData/nodejs/node.exe"
    echo "/mnt/c/Program Files/nodejs/node.exe"
    echo "/c/ProgramData/nodejs/node.exe"
    echo "/c/Program Files/nodejs/node.exe"
    local IFS=':'
    for p in $PATH; do
      case "$p" in
        *node*|*Node*)
          echo "$p/node.exe"
          case "$p" in
            /c/*) echo "/mnt$p/node.exe" ;;
            [A-Za-z]:\\*) echo "$(echo "$p" | sed 's|^\([A-Za-z]\):\\|/mnt/\L\1/|; s|\\|/|g')/node.exe" ;;
          esac
          ;;
      esac
    done
    return 0
  fi
  case "$(uname -s 2>/dev/null)" in
    Darwin)
      echo "/opt/homebrew/bin/node"
      echo "/usr/local/bin/node"
      echo "/usr/bin/node"
      ;;
    Linux|*)
      echo "/usr/bin/node"
      echo "/usr/local/bin/node"
      ;;
  esac
}

_can_run() {
  local node="$1"
  "$node" --version >/dev/null 2>&1
}

for cand in node node.exe; do
  NODE2="$(command -v "$cand" 2>/dev/null || true)"
  if [ -n "$NODE2" ] && [ -x "$NODE2" ] && _can_run "$NODE2"; then
    MY_NODE="$NODE2"
    break
  fi
done

if [ -z "$MY_NODE" ]; then
  for pat in $(_candidates); do
    # shellcheck disable=SC2086
    for NODE2 in $pat; do
      [ -x "$NODE2" ] || continue
      if _can_run "$NODE2"; then
        MY_NODE="$NODE2"
        break 2
      fi
    done
  done
fi

if [ -z "$MY_NODE" ]; then
  cat >&2 <<'EOF'
❌ 跨平台 Node.js 探测失败: PATH 和平台典型位置都找不到可用的 Node.js

   解决方案:
   - macOS:    brew install node
   - Linux:     sudo apt install nodejs  (或 nvm)
   - Windows:   装 Node.js LTS(https://nodejs.org),勾选 Add to PATH
EOF
  exit 1
fi

export MY_NODE

if [ "${BASH_SOURCE[0]:-$0}" = "${0}" ]; then
  echo "MY_NODE=$MY_NODE"
fi