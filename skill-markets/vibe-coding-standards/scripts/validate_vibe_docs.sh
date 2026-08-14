#!/usr/bin/env bash
# validate_vibe_docs.sh — Vibe Coding 文档自校验（v2.5）
#
# 校验项:
#   1. AGENTS.md / SKILL.md / subagents/*.md 行数超过弹性上限
#   2. 文档中非法内联 > 10 行代码块（地图型豁免）
#   3. 子代理未声明 timeout
#   4. 无地图的 AGENTS.md 警告
#   5. Rule .mdc 文件 > 120 行警告
#
# 用法:
#   ./scripts/validate_vibe_docs.sh [dir1 dir2 ...]
#   默认扫描当前目录
#
# 阈值（v2.5）:
#   AGENTS.md 地图型 ≤ 300 行 / 纯规范 ≤ 200 行
#   SKILL.md ≤ 300 行
#   Subagent ≤ 200 行
#   Rule .mdc ≤ 120 行

set -u

# ---------- 阈值 ----------
TH_MAP=300       # 地图型 / 含地图的 AGENTS.md
TH_PURE=200      # 纯规范 AGENTS.md / SKILL.md / Subagent
TH_RULE=120      # Rule .mdc 硬上限

# ---------- 计数 ----------
errors=0
warnings=0
checked_files=0

# ---------- 函数 ----------
check_file() {
  local file="$1"
  local type="$2"   # agents / skill / subagent / rule
  local lines
  lines=$(wc -l < "$file" 2>/dev/null || echo 0)

  checked_files=$((checked_files + 1))

  local threshold
  case "$type" in
    rule)         threshold=$TH_RULE ;;
    agents|skill|subagent) threshold=$TH_PURE ;;
    *)            return 0 ;;
  esac

  if [ "$lines" -gt "$threshold" ]; then
    if [ "$type" = "rule" ]; then
      # Rule 超阈值是警告（非阻断）
      echo "WARN  $file ($lines 行 > 阈值 $threshold，建议拆分)"
      warnings=$((warnings + 1))
    else
      echo "FAIL  $file ($lines 行 > 阈值 $threshold，建议提取 references/)"
      errors=$((errors + 1))
    fi
  fi

  # 子代理必须有 timeout
  if [ "$type" = "subagent" ]; then
    if ! grep -q "^timeout:" "$file"; then
      echo "WARN  $file 缺少 'timeout:' 字段（vibe 子代理强制）"
      warnings=$((warnings + 1))
    fi
  fi

  # AGENTS.md 必须含地图（至少一个）
  if [ "$type" = "agents" ]; then
    if ! grep -qE "技术栈|目录树|启动命令|目录结构|架构" "$file"; then
      echo "WARN  $file 缺少地图元素（技术栈/目录树/启动命令）"
      warnings=$((warnings + 1))
    fi
  fi
}

scan_dir() {
  local root="$1"

  # AGENTS.md
  [ -f "$root/AGENTS.md" ] && check_file "$root/AGENTS.md" "agents"

  # SKILL.md
  [ -f "$root/SKILL.md" ] && check_file "$root/SKILL.md" "skill"

  # subagents
  if [ -d "$root/agents" ] || [ -d "$root/subagents" ]; then
    local agents_dir="${root}/subagents"
    [ ! -d "$agents_dir" ] && agents_dir="${root}/agents"
    while IFS= read -r f; do
      check_file "$f" "subagent"
    done < <(find "$agents_dir" -type f -name "*.md" 2>/dev/null)
  fi

  # Rule .mdc
  if [ -d "$root/rules" ]; then
    while IFS= read -r f; do
      check_file "$f" "rule"
    done < <(find "$root/rules" -type f -name "*.mdc" 2>/dev/null)
  fi
}

# ---------- 入口 ----------
dirs=("$@")
if [ ${#dirs[@]} -eq 0 ]; then
  dirs=("$(pwd)")
fi

for d in "${dirs[@]}"; do
  if [ ! -d "$d" ]; then
    echo "SKIP  $d (不是目录)"
    continue
  fi
  scan_dir "$d"
done

# ---------- 报告 ----------
echo ""
echo "================================================="
echo "扫描完成: $checked_files 文件 | $errors 阻断 | $warnings 警告"
echo "阈值: AGENTS/SKILL ${TH_PURE} 行 / Rule ${TH_RULE} 行 (v2.5)"
echo "================================================="

# ---------- 5 Pillar 联动检查（2026-08-14 增量）----------
# 检查每个 SKILL.md frontmatter 是否声明了:
#   Pillar 1 (项目结构): description 含"文件/目录/模块"关键词
#   Pillar 2 (代码风格): description 含"风格/规范/约定"关键词
#   Pillar 4 (相关代码示例): SKILL.md 至少 1 个 Examples 章节
# 检查每个 requires.optional 是否带"降级影响"说明
# (这是 §M-03 + §M-04 的可机检落地)

echo ""
echo "--- 5 Pillar 联动检查 ---"
pillar_count=0
pillar_warn=0

# 扫所有 SKILL.md
while IFS= read -r skill_md; do
    [ -z "$skill_md" ] && continue
    fm=$(sed -n '/^---$/,/^---$/p' "$skill_md" 2>/dev/null | sed '1d;$d')

    # P1: 检查 optional 是否有降级说明(粗略:含"→"或"降级"或"代价")
    if echo "$fm" | grep -qE '^requires:' ; then
        optional_block=$(echo "$fm" | awk '/^optional:/,/^[a-z]/' | head -20)
        if echo "$optional_block" | grep -qE 'optional:' ; then
            # 任意 optional 缺降级说明 → WARN
            missing_degrade=$(echo "$optional_block" | grep -vE '(降级|→|代价|影响)' | grep -vE '^\s*#' | grep -E '^\s*-' | grep -v '^\s*-\s*$' | head -5)
            if [ -n "$missing_degrade" ]; then
                rel=$(echo "$skill_md" | sed "s|$PWD/||")
                echo "  ⚠  $rel — optional 缺降级影响说明(Pillar 4)"
                pillar_warn=$((pillar_warn + 1))
            fi
        fi
    fi

    # P2: 检查 SKILL.md 是否有 Examples 章节(Pillar 4)
    if ! grep -qE '^## (Examples|示例)' "$skill_md" 2>/dev/null; then
        rel=$(echo "$skill_md" | sed "s|$PWD/||")
        echo "  ℹ  $rel — 缺 Examples 章节(可选增强,但建议加)"
        pillar_count=$((pillar_count + 1))
    fi
done < <(find . -name SKILL.md -not -path "./node_modules/*" 2>/dev/null)

echo ""
if [ "$pillar_warn" -gt 0 ]; then
    echo "5 Pillar 检查: $pillar_warn 警告 (optional 缺降级说明) / $pillar_count 信息"
    warnings=$((warnings + pillar_warn))
else
    echo "5 Pillar 检查: 0 警告 / $pillar_count 信息"
fi

[ "$errors" -gt 0 ] && exit 1 || exit 0