#!/usr/bin/env bash
# ──────────────────────────────────────────────
# check-env.sh — 检测 Node.js / npm / docsify-cli 环境
# ──────────────────────────────────────────────
set -euo pipefail

# 颜色（无 tty 时自动禁用）
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; NC=''
fi

echo -e "\n${CYAN}[环境检查] 检测 docsify-cli...${NC}"

# ── 检测 Node.js ──
if command -v node &>/dev/null; then
  node_ver=$(node --version)
  echo -e "  ${GREEN}✅ Node.js: ${node_ver}${NC}"
else
  echo -e "  ${RED}❌ Node.js 未安装！${NC}"
  echo ""
  echo -e "  ${YELLOW}── 安装指引 ──${NC}"
  echo "  1. 访问 https://nodejs.org/ 下载 LTS 版本"
  echo "  2. 安装后重新打开终端"
  echo "  3. 重新运行此脚本"
  echo -e "  ${YELLOW}──────────────${NC}"
  exit 1
fi

# ── 检测 npm ──
if command -v npm &>/dev/null; then
  npm_ver=$(npm --version)
  echo -e "  ${GREEN}✅ npm: ${npm_ver}${NC}"
else
  echo -e "  ${RED}❌ npm 未安装！${NC}"
  exit 1
fi

# ── 检测/安装 docsify-cli ──
if command -v docsify &>/dev/null; then
  docsify_ver=$(docsify --version 2>/dev/null || true)
  echo -e "  ${GREEN}✅ docsify-cli: ${docsify_ver}${NC}"
else
  echo -e "  ${YELLOW}⏳ docsify-cli 未安装，正在通过 npm 全局安装...${NC}"
  npm install -g docsify-cli
  if command -v docsify &>/dev/null; then
    docsify_ver=$(docsify --version 2>/dev/null || true)
    echo -e "  ${GREEN}✅ docsify-cli 安装成功: ${docsify_ver}${NC}"
  else
    echo -e "  ${RED}❌ 安装失败！请手动执行:${NC}"
    echo -e "     ${YELLOW}npm install -g docsify-cli${NC}"
    exit 1
  fi
fi

echo -e "\n${GREEN}[环境检查] 全部通过！${NC}"
