#!/bin/bash
# scripts/init-publish.sh
# 环境检查 + publish config init 包装
# 用法：bash init-publish.sh [可选：.env 所在目录，默认 cwd]

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_DIR="${1:-$(pwd)}"

cd "$TARGET_DIR"

# ── 检查 .env ─
if [[ ! -f .env ]]; then
  echo "❌ 未找到 .env（当前目录：$TARGET_DIR）"
  echo ""
  echo "   cp $SKILL_DIR/references/.env.example .env"
  echo "   # 然后编辑 .env 填入你的真实值"
  exit 1
fi

# ── 检查 .gitignore ─
if [[ ! -f .gitignore ]] || ! grep -qE "^\.env$" .gitignore 2>/dev/null; then
  echo "⚠️  .gitignore 未包含 .env，强烈建议加入"
fi

# ── 检查 .env.example 是否还是模板 ─
EXAMPLE="$SKILL_DIR/references/.env.example"
if [[ -f "$EXAMPLE" ]]; then
  if grep -qE "(LTAI5[A-Za-z0-9]{12,}|AccessKeyId.*=.{20,})" "$EXAMPLE" 2>/dev/null; then
    echo "❌ $EXAMPLE 里检测到疑似真实 AccessKey 模式"
    echo "   .env.example 必须是模板，不允许有真实值"
    exit 1
  fi
fi

# ── 确保 publish 已安装 ─
if ! command -v publish &>/dev/null; then
  echo "⏳ publish 未安装，正在 pip install -e $SKILL_DIR ..."
  pip install -e "$SKILL_DIR" --quiet
fi

# ── 跑 publish config init ─
echo "📄 运行 publish config init..."
publish config init

echo ""
echo "🎉 初始化完成！"
echo "   下一步：publish deploy <name> -d <sub>.<domain> -w <dir> --ip <IP>"
