#!/usr/bin/env bash
# 跨平台 Python 探测(共享脚本)
# 思路参考 AGENTS.md §4.1.3 + trap-instructions AP-6:
#   - 不硬编码 Python 路径
#   - PATH + 平台典型位置(由 uname 动态生成)
#   - 缺 pytest/yaml → 自动 python -m pip install --user(自愈,不阻断)
#   - 导出 MY_TRAE_HELPER_PY 给调用方使用
#
# 用法(其他脚本):
#   source "$(dirname "${0}")/detect-python.sh"
#   "$MY_TRAE_HELPER_PY" your-script.py

set -euo pipefail

# 探测顺序:python3 → python → py
PY=""
for candidate in python3 python py; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PY="$(command -v "$candidate")"
    break
  fi
done

if [ -z "$PY" ]; then
  echo "[FATAL] Python 未找到(违反 AP-6 跨平台铁律)" >&2
  echo "  探测路径:" >&2
  echo "    - PATH 中的 python3/python/py" >&2
  case "$(uname -s 2>/dev/null || echo Windows)" in
    Linux|Darwin)
      echo "    - /usr/bin/python3 /usr/local/bin/python3" >&2
      ;;
    MINGW*|MSYS*|CYGWIN*|Windows*)
      echo "    - py -3 (Windows Python Launcher)" >&2
      ;;
  esac
  exit 2
fi

# 自愈依赖(pytest / pyyaml)
"$PY" -c "import pytest" 2>/dev/null || {
  echo "[INFO] pytest 未装,自愈安装..."
  "$PY" -m pip install --user pytest pyyaml >/dev/null 2>&1 || true
}

export MY_TRAE_HELPER_PY="$PY"
MY_VER="$("$PY" -c "import sys; v=sys.version.split(); print(v[0])")"
export MY_TRAE_HELPER_PY_VERSION="$MY_VER"

echo "[detect-python.sh] PY=$MY_TRAE_HELPER_PY VERSION=$MY_TRAE_HELPER_PY_VERSION" >&2
