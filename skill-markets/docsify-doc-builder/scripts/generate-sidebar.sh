#!/usr/bin/env bash
# ──────────────────────────────────────────────
# generate-sidebar.sh — 根据 docs/ 目录结构自动生成 _sidebar.md
#
# 特性:
#   - 支持嵌套目录（最多 4 层）
#   - 文件名中的数字前缀自动去除（如 "01-快速开始.md" → "快速开始"）
#   - README.md 排在每级目录首位，显示为"概览"
#   - 已有 _sidebar.md 会被完全覆盖
#   - 如果项目根有 README.md，自动添加"项目简介"链接
# ──────────────────────────────────────────────
set -euo pipefail

DOCS_DIR="$PWD/docs"
SIDEBAR_PATH="$DOCS_DIR/_sidebar.md"

# 颜色
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; WHITE='\033[0;37m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; WHITE=''; NC=''
fi

echo -e "\n${CYAN}[侧边栏生成] 开始...${NC}"
echo -e "  ${WHITE}扫描: ${DOCS_DIR}${NC}"

if [ ! -d "$DOCS_DIR" ]; then
  echo -e "  ${RED}❌ docs/ 目录不存在！请先运行 init-docs.sh${NC}"
  exit 1
fi

# ── 扫描所有 .md 文件（排除特殊文件） ──
# 收集文件并按目录+文件名排序
mapfile -t all_files < <(
  find "$DOCS_DIR" -type f -name "*.md" \
    ! -name "_sidebar.md" ! -name "_navbar.md" \
    | sort
)

file_count=${#all_files[@]}

if [ "$file_count" -eq 0 ]; then
  echo -e "  ${YELLOW}⚠️  docs/ 下没有 Markdown 文件，生成空侧边栏${NC}"
  cat > "$SIDEBAR_PATH" <<'EOF'
# 文档目录

* 暂无内容
EOF
  exit 0
fi

echo -e "  ${WHITE}发现 ${file_count} 个 Markdown 文件${NC}"

# ── 工具函数 ──
# 去除文件名中的数字前缀
strip_prefix() {
  local name="$1"
  # macOS 兼容: sed -E 代替 sed -r
  echo "$name" | sed -E 's/^[0-9]+[-_]//'
}

# 获取文件相对 docs/ 的路径（用 / 分隔）
get_relpath() {
  local fullpath="$1"
  local rel="${fullpath#$DOCS_DIR/}"
  echo "$rel"
}

# 获取文件所在目录相对 docs/ 的路径（/ 分隔）
get_reldir() {
  local fullpath="$1"
  dirname "$(get_relpath "$fullpath")"
}

# 清理路径中的 ./ 
clean_path() {
  local p="$1"
  echo "${p#.}" | sed 's|^/||'
}

# ── 构建侧边栏 ──
{
  echo "<!-- _sidebar.md — 由 generate-sidebar.sh 自动生成 -->"
  echo "<!-- 手动编辑后重新运行会基于最新文件结构重建 -->"
  echo ""
  echo "* [项目简介](README.md)"
  echo ""

  # 记录已渲染的目录层级
  declare -A rendered_dirs

  # 按目录分组文件
  current_dir=""
  for file in "${all_files[@]}"; do
    reldir=$(get_reldir "$file")
    relpath=$(get_relpath "$file")

    # 根级文件跳过（README.md 已处理）
    if [ "$reldir" = "." ]; then
      if [ "$(basename "$file")" = "README.md" ]; then
        continue
      fi
      # 根级非 README 文件也渲染
      name=$(basename "$file" .md)
      name=$(strip_prefix "$name")
      echo "  * [$name]($relpath)"
      continue
    fi

    # 处理目录层级变化
    if [ "$reldir" != "$current_dir" ]; then
      current_dir="$reldir"

      # 按 / 拆分层级，逐级渲染目录标题
      IFS='/' read -ra parts <<< "$reldir"
      acc=""
      depth=0
      for part in "${parts[@]}"; do
        if [ -z "$acc" ]; then
          acc="$part"
        else
          acc="$acc/$part"
        fi
        indent=$(printf '%*s' $((depth * 2)) '')
        if [ -z "${rendered_dirs[$acc]:-}" ]; then
          rendered_dirs[$acc]=1
          echo "${indent}* $part"
        fi
        depth=$((depth + 1))
      done
    fi

    # 渲染文件
    depth=$(echo "$reldir" | tr -cd '/' | wc -c)
    depth=$((depth + 1)) # 文件比目录多一层缩进
    indent=$(printf '%*s' $((depth * 2)) '')

    fname=$(basename "$file" .md)
    fname=$(strip_prefix "$fname")
    if [ "$(basename "$file")" = "README.md" ]; then
      fname="概览"
    fi
    echo "${indent}  * [$fname]($relpath)"
  done

  echo ""
} > "$SIDEBAR_PATH"

echo -e "  ${GREEN}✅ 写入 ${SIDEBAR_PATH}${NC}"

# 统计行数
line_count=$(wc -l < "$SIDEBAR_PATH" | tr -d ' ')
echo -e "  ${WHITE}共 ${line_count} 行${NC}"
echo -e "\n${GREEN}[侧边栏生成] 完成！${NC}"
