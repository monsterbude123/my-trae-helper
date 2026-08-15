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
#
# 2026-08-15 修复: git 子进程 PATH 被精简(Git 自身只塞 %SystemRoot%\system32 + %ProgramFiles%\Git\cmd),
# `command -v python3` 只找到 MSYS 自带的 /usr/bin/python3(无 pip),无法自愈。
# 修复策略:
#   (a) Windows 加 `py -3` launcher(走注册表,不受 MSYS PATH 影响)
#   (b) Windows 加 `where.exe python`(cmd.exe 内建,通过 cmd.exe 拿 Windows 真实 PATH,翻译回 MSYS 路径)
#   (c) 遍历当前 PATH(即便精简)中的 python* 二进制
#   (d) 关键修复:Git for Windows 新版 MSYS 的 `uname -s` 返回 `Linux`(而非 MINGW*),
#       单纯信 uname 会走 Linux 分支漏掉 Windows Python。用"文件系统可达性"兜底:
#       若 /mnt/c/Windows/System32/cmd.exe 存在 → 必是 MSYS on Windows → 走 Windows 分支。
_is_windows_msys() {
  # MSYS on Windows 必有 /mnt/c/Windows/System32,且 /usr/bin/python3 是 MSYS 自带无 pip
  # macOS / Linux 上 /mnt/c 不存在 → 返回非零
  [ -x /mnt/c/Windows/System32/cmd.exe ] || [ -x /c/Windows/System32/cmd.exe ]
}
_candidates() {
  # 先用文件系统可达性判定(覆盖 Git for Windows 新版 uname 返回 Linux 的情况)
  if _is_windows_msys; then
    # Windows Git Bash: 常见位置 — Python Launcher / miniconda / 官方安装包
    echo "/mnt/c/Users/$USER/AppData/Local/Programs/Python/Python3*/python.exe"
    echo "/mnt/c/ProgramData/miniconda3/python.exe"
    echo "/mnt/c/Python3*/python.exe"
    echo "/c/Users/$USER/AppData/Local/Programs/Python/Python3*/python.exe"
    echo "/c/ProgramData/miniconda3/python.exe"
    echo "/c/Python3*/python.exe"
    # (c) 当前 PATH 中所有 python 候选(精简 PATH 内若意外存在优先)
    local IFS=':'
    for p in $PATH; do
      case "$p" in
        *python*|*Python*|*conda*|*anaconda*)
          echo "$p/python.exe"
          echo "$p/python3.exe"
          # Windows PATH 可能用 C:\foo 或 /c/foo 两种,加 /mnt 镜像
          case "$p" in
            /c/*) echo "/mnt$p/python.exe" ;;
            [A-Za-z]:\\*) echo "$(echo "$p" | sed 's|^\([A-Za-z]\):\\|/mnt/\L\1/|; s|\\|/|g')/python.exe" ;;
          esac
          ;;
      esac
    done
    # (b) cmd.exe 内建 where → MSYS 路径翻译(走 $MSYS_NO_PATHCONV=1 避免自动转换)
    local _where
    _where="$(MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' cmd.exe //c where python 2>/dev/null | tr -d '\r' | head -1)"
    if [ -n "$_where" ]; then
      # Windows 风格 C:\foo\python.exe → MSYS /mnt/c/foo/python.exe(Git for Windows)
      case "$_where" in
        [A-Za-z]:\\*) echo "$(echo "$_where" | sed 's|^\([A-Za-z]\):\\|/mnt/\L\1/|; s|\\|/|g')" ;;
        *) echo "$_where" ;;
      esac
    fi
    # (a) py launcher(走注册表,无 PATH 依赖)
    echo "py:-3"
    return 0
  fi

  # 真·Linux / macOS / BSD 用 uname 分流
  case "$(uname -s 2>/dev/null)" in
    Darwin)
      echo "/opt/homebrew/bin/python3"
      echo "/usr/local/bin/python3"
      echo "/usr/bin/python3"
      local IFS=':'
      for p in $PATH; do
        case "$p" in
          *python*|*conda*|*anaconda*)
            echo "$p/python3"
            ;;
        esac
      done
      ;;
    Linux|*)
      echo "/usr/bin/python3"
      echo "/usr/local/bin/python3"
      local IFS=':'
      for p in $PATH; do
        case "$p" in
          *python*|*conda*|*anaconda*)
            echo "$p/python3"
            ;;
        esac
      done
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

# 第一轮: PATH 上的命令 + Windows `py` launcher(走注册表,无 PATH 依赖)
for cand in python3 py python; do
  PY2="$(command -v "$cand" 2>/dev/null || true)"
  if [ -n "$PY2" ] && [ -x "$PY2" ]; then
    if _can_import "$PY2"; then
      PY="$PY2"; break
    fi
    # 探测过但不能 import:清空 PY,继续第二轮(MSYS 自带 /usr/bin/python3
    # 不能 import 也不带 pip,不该被视为命中)
    PY=""
    if _try_bootstrap "$PY2"; then
      PY="$PY2"; break
    fi
    PY=""
  fi
done

# 第一轮扩展: Windows py launcher(Python Install Manager,Windows 7+ 自带)
#   `py -3` 会从注册表读 PythonCore,不受 MSYS PATH 精简影响
if [ -z "$PY" ] && [ "$(uname -s 2>/dev/null)" = "MINGW"* ] || [ "$(uname -s 2>/dev/null)" = "MSYS"* ] || [ "$(uname -s 2>/dev/null)" = "CYGWIN"* ]; then
  if command -v py.exe >/dev/null 2>&1 || command -v py >/dev/null 2>&1; then
    # 让 py launcher 告诉我们真实 Python 路径
    PY2="$(py -3 -c 'import sys; print(sys.executable)' 2>/dev/null | tr -d '\r' || true)"
    if [ -n "$PY2" ] && [ -x "$PY2" ]; then
      if _can_import "$PY2"; then
        PY="$PY2"
      elif _try_bootstrap "$PY2"; then
        PY="$PY2"
      fi
    fi
  fi
fi

# 第二轮: 平台典型安装位置(glob 展开 + `py:-3` launcher 标记)
if [ -z "$PY" ]; then
  for pat in $(_candidates); do
    # launcher 标记: `py:-3` → 调 py -3 拿 sys.executable
    case "$pat" in
      py:*)
        # 注意:set -u 下未赋值变量会炸,先给默认
        _arg="${pat#py:}"
        _exe=""
        if command -v py >/dev/null 2>&1; then
          _exe="$(py "$_arg" -c 'import sys; print(sys.executable)' 2>/dev/null | tr -d '\r' || true)"
        fi
        if [ -n "${_exe:-}" ] && [ -x "$_exe" ]; then
          if _can_import "$_exe"; then
            PY="$_exe"; break
          elif _try_bootstrap "$_exe"; then
            PY="$_exe"; break
          fi
        fi
        continue
        ;;
    esac
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