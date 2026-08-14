#!/usr/bin/env bash
# scripts/detect-python.sh — 跨平台 Python 探测 + 依赖自愈(供 Git Hook 复用)
#
# 设计原则(2026-08-14 第二轮蒸馏修正,第二轮再次修正):
#   1. 跨平台: 约定路径按 OS 动态生成(macOS/Linux 不掺 Windows 风格 /mnt/c/...)
#   2. 仅信 PATH + 平台典型安装位置,绝不写死具体路径
#   3. 能力校验失败 → 自动 `python -m pip install --user pytest pyyaml`(用户已允许)
#   4. 导出到 MY_TRAE_HELPER_PY 供子脚本拾取
#
# 用法(在 .husky/pre-commit / pre-push 头部):
#   # shellcheck disable=SC1091
#   . "$(dirname "$0")/../scripts/detect-python.sh" || exit 1
#
# 失败语义: 真找不到 → 打印明确错误 + exit 1
# 不静默降级到 stub(那是"假通过",违反 Gate 自验收铁律)

set -u

# 必须在已 source 进的 shell 中写回 $PY 与 $MY_TRAE_HELPER_PY
PY=""

# 平台典型 Python 候选路径(动态拼,避免硬编码具体文件名)
# - Windows(Git Bash / MSYS / Cygwin): /c/Users/$USER/AppData/Local/Programs/Python/Python*/python.exe
#                                       /c/ProgramData/miniconda3/python.exe
#                                       /c/Python*/python.exe
# - macOS:                /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3
# - Linux:                /usr/bin/python3 /usr/local/bin/python3
# 用 uname 判断 OS,绝不混搭
_candidates() {
  case "$(uname -s 2>/dev/null)" in
    MINGW*|MSYS*|CYGWIN*)
      # Windows Git Bash: 常见位置 — Python Launcher / miniconda / 官方安装包
      echo "/c/Users/$USER/AppData/Local/Programs/Python/Python3*/python.exe"
      echo "/c/ProgramData/miniconda3/python.exe"
      echo "/c/Python3*/python.exe"
      ;;
    Darwin)
      echo "/opt/homebrew/bin/python3"
      echo "/usr/local/bin/python3"
      echo "/usr/bin/python3"
      ;;
    Linux|*)
      echo "/usr/bin/python3"
      echo "/usr/local/bin/python3"
      ;;
  esac
}

# 守卫脚本真正用到的两个库 — 缺则自愈
_REQUIRED_MODS="pytest yaml"

_can_import() {
  local py="$1"
  "$py" -c "import pytest, yaml" 2>/dev/null
}

_try_bootstrap() {
  local py="$1"
  # pip 自举: 优先 python -m pip(避免 PATH 没 pip 的情况)
  if "$py" -m pip --version >/dev/null 2>&1; then
    # 日志落到项目 logs/,不污染 /tmp
    local log_dir="$(pwd)/logs"
    mkdir -p "$log_dir" 2>/dev/null || log_dir="/tmp"
    local log="$log_dir/mth-pip.log"
    echo "🔧 $py 缺 pytest/yaml,自动 pip install --user ..." >&2
    if "$py" -m pip install --user pytest pyyaml >"$log" 2>&1; then
      if _can_import "$py"; then
        echo "✅ 自愈成功" >&2
        return 0
      fi
    fi
    tail -5 "$log" >&2
  else
    echo "⚠️  $py 缺 pip,无法自愈。请手动: $py -m ensurepip --user" >&2
  fi
  return 1
}

# 第一轮: PATH 上的命令
for cand in python3 py python; do
  PY2="$(command -v "$cand" 2>/dev/null || true)"
  if [ -n "$PY2" ] && [ -x "$PY2" ]; then
    if _can_import "$PY2"; then
      PY="$PY2"; break
    elif _try_bootstrap "$PY2"; then
      PY="$PY2"; break
    fi
  fi
done

# 第二轮: 平台典型安装位置(glob 展开)
if [ -z "$PY" ]; then
  for pat in $(_candidates); do
    # shellcheck disable=SC2086
    for PY2 in $pat; do
      [ -x "$PY2" ] || continue
      if _can_import "$PY2"; then
        PY="$PY2"; break 2
      elif _try_bootstrap "$PY2"; then
        PY="$PY2"; break 2
      fi
    done
  done
fi

if [ -z "$PY" ]; then
  cat >&2 <<'EOF'
❌ 跨平台 Python 探测失败: PATH 和平台典型位置都找不到可用的 Python(或都缺 pytest/yaml 且自愈失败)

   解决方案:
   - macOS:  brew install python && python3 -m pip install --user pytest pyyaml
   - Linux:  sudo apt install python3 python3-pip && python3 -m pip install --user pytest pyyaml
   - Windows Git Bash: 装 Python(勾选 Add to PATH) + python -m pip install --user pytest pyyaml
EOF
  exit 1
fi

export MY_TRAE_HELPER_PY="$PY"

# 若不是 source 而是直接执行,打印结果(便于排错)
if [ "${BASH_SOURCE[0]:-$0}" = "${0}" ]; then
  echo "PY=$PY"
fi