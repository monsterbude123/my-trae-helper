#!/usr/bin/env bash
# ──────────────────────────────────────────────
# serve.sh — 启动 docsify 开发服务器
#
# 在 docs/ 目录上启动 docsify serve，默认端口 3000。
# 支持通过环境变量 DOCSIFY_PORT 自定义端口。
# 支持通过 --no-open 禁用自动打开浏览器。
#
# 用法:
#   ./serve.sh                  # 默认端口 3000，自动打开浏览器
#   DOCSIFY_PORT=4000 ./serve.sh
#   ./serve.sh 8080             # 指定端口 8080
#   ./serve.sh 8080 --no-open   # 指定端口，不自动打开浏览器
# ──────────────────────────────────────────────
set -euo pipefail

DOCS_DIR="$PWD/docs"
PORT="${DOCSIFY_PORT:-3000}"
OPEN_BROWSER=1

# ── 解析参数 ──
for arg in "$@"; do
  case "$arg" in
    --no-open)
      OPEN_BROWSER=0
      ;;
    ''|*[!0-9]*)
      # 非数字参数忽略
      ;;
    *)
      # 数字参数作为端口号
      PORT="$arg"
      ;;
  esac
done

# ── 验证端口号 ──
if [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
  PORT=3000
fi

# 颜色
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; WHITE='\033[0;37m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; WHITE=''; NC=''
fi

# ── 检查 docs/ 目录 ──
if [ ! -d "$DOCS_DIR" ]; then
  echo -e "  ${RED}❌ docs/ 目录不存在！请先运行 init-docs.sh${NC}"
  exit 1
fi

# ── 检查 docsify-cli ──
if ! command -v docsify &>/dev/null; then
  echo -e "  ${RED}❌ docsify-cli 未安装！请先运行 check-env.sh${NC}"
  exit 1
fi

# ── 启动服务器 ──
echo -e "\n${CYAN}[文档服务] 启动中...${NC}"
echo -e "  ${WHITE}目录: ${DOCS_DIR}${NC}"
echo -e "  ${WHITE}端口: ${PORT}${NC}"
echo -e "  ${WHITE}热更新: 已启用（编辑 .md 文件后浏览器自动刷新）${NC}"
echo ""

# 跨平台打开浏览器
open_browser_os() {
  local url="$1"
  case "$(uname -s)" in
    Darwin)
      open "$url" ;;
    Linux)
      if command -v xdg-open &>/dev/null; then
        xdg-open "$url"
      elif command -v wslview &>/dev/null; then
        wslview "$url"
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)
      start "$url" ;;
    *)
      # 通用尝试
      if command -v xdg-open &>/dev/null; then
        xdg-open "$url"
      elif command -v open &>/dev/null; then
        open "$url"
      fi
      ;;
  esac
}

if [ "$OPEN_BROWSER" -eq 1 ]; then
  url="http://localhost:${PORT}"
  open_browser_os "$url" 2>/dev/null || true
  echo -e "  🌐 浏览器已自动打开: ${url}" 2>/dev/null || \
  echo "  browser open: ${url}"
fi

echo -e "  ${YELLOW}按 Ctrl+C 停止服务器${NC}"
echo ""

# 启动 docsify serve
docsify serve "$DOCS_DIR" --port "$PORT"
