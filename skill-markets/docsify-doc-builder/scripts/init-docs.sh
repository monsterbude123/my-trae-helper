#!/usr/bin/env bash
# ──────────────────────────────────────────────
# init-docs.sh — 初始化 docsify 文档目录结构和配置
#
# 用法:
#   PROJECT_NAME="MyProject" ./init-docs.sh
#   PROJECT_NAME="MyProject" PROJECT_DESCRIPTION="项目简介" ./init-docs.sh
#   ./init-docs.sh MyProject "可选项目简介"
#
# 支持从环境变量或参数指定 PROJECT_NAME / PROJECT_DESCRIPTION。
# ──────────────────────────────────────────────
set -euo pipefail

# ── 解析参数 ──
PROJECT_NAME="${1:-${PROJECT_NAME:-}}"
PROJECT_DESCRIPTION="${2:-${PROJECT_DESCRIPTION:-}}"

# 未指定项目名时使用当前目录名
if [ -z "$PROJECT_NAME" ]; then
  PROJECT_NAME=$(basename "$PWD")
  if [ -t 1 ]; then echo -e "  \033[0;33mℹ️ 未指定项目名，使用当前目录名: ${PROJECT_NAME}\033[0m"; fi
fi

# 颜色
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; WHITE='\033[0;37m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; WHITE=''; NC=''
fi

# ── 路径配置 ──
SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES_DIR="$SKILL_ROOT/templates"
DOCS_DIR="$PWD/docs"

echo -e "\n${CYAN}[文档初始化] 开始...${NC}"
echo -e "  ${WHITE}项目: ${PROJECT_NAME}${NC}"
echo -e "  ${WHITE}输出: ${DOCS_DIR}${NC}"

# ── 创建 docs 目录 ──
if [ -d "$DOCS_DIR" ]; then
  echo -e "  ${YELLOW}ℹ️ docs/ 目录已存在，将覆盖同名文件${NC}"
else
  mkdir -p "$DOCS_DIR"
  echo -e "  ${GREEN}✅ 创建 docs/ 目录${NC}"
fi

# ── 创建子目录结构 ──
subdirs=("基础篇" "进阶篇" "附录")
for dir in "${subdirs[@]}"; do
  mkdir -p "$DOCS_DIR/$dir"
done
echo -e "  ${GREEN}✅ 创建文档子目录: ${subdirs[*]}${NC}"

# ── 复制模板文件并替换变量 ──
template_files=("index.html" "README.md" "_sidebar.md" "_navbar.md" "custom.css" "logo.svg")
file_count=0
for file in "${template_files[@]}"; do
  src="$TEMPLATES_DIR/$file"
  dst="$DOCS_DIR/$file"
  if [ -f "$src" ]; then
    # 使用 sed 进行跨平台变量替换
    if command -v gsed &>/dev/null; then
      # macOS (GNU sed)
      gsed -e "s|{{PROJECT_NAME}}|${PROJECT_NAME}|g" \
           -e "s|{{PROJECT_DESCRIPTION}}|${PROJECT_DESCRIPTION}|g" \
           "$src" > "$dst"
    else
      # Linux / BSD
      sed -e "s|{{PROJECT_NAME}}|${PROJECT_NAME}|g" \
          -e "s|{{PROJECT_DESCRIPTION}}|${PROJECT_DESCRIPTION}|g" \
          "$src" > "$dst"
    fi
    file_count=$((file_count + 1))
  fi
done
echo -e "  ${GREEN}✅ 复制 ${file_count} 个模板文件${NC}"

# ── 创建示例文档 ──
# 为了跨平台兼容，使用独立的 write_doc 函数
write_doc() {
  local path="$1"; shift
  mkdir -p "$(dirname "$path")"
  if [ ! -f "$path" ]; then
    printf '%s\n' "$@" > "$path"
  fi
}

write_doc "$DOCS_DIR/基础篇/快速开始.md" \
  "# 快速开始" \
  "" \
  "## 安装" \
  "" \
  '```bash' \
  "# 安装命令" \
  '```' \
  "" \
  "## 使用" \
  "" \
  '```bash' \
  "# 使用命令" \
  '```'

write_doc "$DOCS_DIR/基础篇/核心概念.md" \
  "# 核心概念" \
  "" \
  "## 概念一" \
  "" \
  "..." \
  "" \
  "## 概念二" \
  "" \
  "..."

write_doc "$DOCS_DIR/进阶篇/配置详解.md" \
  "# 配置详解" \
  "" \
  "## 配置项" \
  "" \
  "..."

write_doc "$DOCS_DIR/基础篇/安装指南.md" \
  "# 安装指南" \
  "" \
  "## 环境要求" \
  "" \
  "- 要求一" \
  "- 要求二" \
  "" \
  "## 安装步骤" \
  "" \
  "1. 步骤一" \
  "2. 步骤二"

write_doc "$DOCS_DIR/进阶篇/API参考.md" \
  "# API 参考" \
  "" \
  "## 接口一览" \
  "" \
  "| 方法 | 路径 | 说明 |" \
  "|------|------|------|" \
  "| GET | /api/v1/ | 接口说明 |" \
  "" \
  "## 请求示例" \
  "" \
  '```bash' \
  "curl https://api.example.com/v1/" \
  '```'

write_doc "$DOCS_DIR/附录/常见问题.md" \
  "# 常见问题 (FAQ)" \
  "" \
  "## Q1: 常见问题一" \
  "" \
  "..." \
  "" \
  "## Q2: 常见问题二" \
  "" \
  "..."

write_doc "$DOCS_DIR/附录/更新日志.md" \
  "# 更新日志" \
  "" \
  "## v0.1.0 (2024-01-01)" \
  "" \
  "### ✨ 新增" \
  "- 初始版本" \
  "" \
  "### 🐛 修复" \
  "- 无"

write_doc "$DOCS_DIR/附录/贡献指南.md" \
  "# 贡献指南" \
  "" \
  "## 如何参与" \
  "" \
  "1. Fork 本仓库" \
  "2. 创建特性分支" \
  "3. 提交变更" \
  "4. 发起 Pull Request"

echo -e "  ${GREEN}✅ 创建示例文档文件${NC}"
echo -e "\n${GREEN}[文档初始化] 完成！${NC}"
echo ""
echo -e "  ${CYAN}下一步操作：${NC}"
echo -e "  ${WHITE}1. 编辑 docs/ 下的 Markdown 文件完善文档内容${NC}"
echo -e "  ${WHITE}2. 运行 generate-sidebar.sh 生成侧边栏${NC}"
echo -e "  ${WHITE}3. 运行 serve.sh 启动预览服务器${NC}"
echo -e "  ${WHITE}4. 访问 http://localhost:3000 查看效果${NC}"
