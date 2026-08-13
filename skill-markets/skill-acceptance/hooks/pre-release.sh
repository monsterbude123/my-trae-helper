#!/bin/sh
# pre-release.sh — skill-acceptance pre-release hook (POSIX)
#
# 触发时机：git tag 推送 / release 创建 / GitHub Actions workflow_dispatch
# 调 verify.py 逐个跑 skill-markets/ 下每个 skill 的 6 项检查
#
# 用法：
#   pre-release.sh [--skill <name>]... [--force] [--help]
#
# 环境变量：
#   SKIP_SKILL_ACCEPTANCE=1  跳过校验（CI 调试用）
#   NO_COLOR=1              关闭 ANSI 颜色
#
# 退出码：
#   0  全部 PASS（最多 <3 WARN）
#   1  任意 skill BLOCK（阻断 release）
#   2  累计 ≥3 WARN（警告但不阻断；--force 可忽略）
#   3  参数错误 / verify.py 调用失败
#
# 依赖：python3、bash 仅用于 set -euo pipefail 兼容（实际逻辑用 POSIX sh）

set -eu

# ---------- 参数解析 ----------
SKILLS=""
FORCE=0
print_help() {
    cat <<'EOF'
pre-release.sh — skill-acceptance pre-release hook

用法:
    pre-release.sh [--skill <name>]... [--force] [--help]

参数:
    --skill <name>   指定要验收的 skill 名（可重复；默认扫描 skill-markets/ 全量）
    --force          强制忽略 WARN 阈值（不忽略 BLOCK）
    --help           显示本帮助

退出码:
    0  全部 PASS
    1  任意 BLOCK（阻断 release）
    2  ≥3 WARN（可用 --force 忽略）
    3  参数错误 / verify.py 缺失
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --skill)
            shift
            if [ -z "${1:-}" ]; then
                echo "ERROR: --skill 缺少值" >&2
                exit 3
            fi
            SKILLS="$SKILLS $1"
            shift
            ;;
        --force)
            FORCE=1
            shift
            ;;
        --help|-h)
            print_help
            exit 0
            ;;
        *)
            echo "ERROR: 未知参数: $1" >&2
            print_help >&2
            exit 3
            ;;
    esac
done

# ---------- 颜色（NO_COLOR 兜底） ----------
if [ -n "${NO_COLOR:-}" ]; then
    C_RED=""; C_GREEN=""; C_YELLOW=""; C_RESET=""
else
    C_RED="\033[31m"; C_GREEN="\033[32m"; C_YELLOW="\033[33m"; C_RESET="\033[0m"
fi

# ---------- SKIP 快速通道 ----------
if [ "${SKIP_SKILL_ACCEPTANCE:-0}" = "1" ]; then
    echo "${C_YELLOW}⏭ SKIP_SKILL_ACCEPTANCE=1,跳过 skill 验收${C_RESET}"
    exit 0
fi

# ---------- 路径定位 ----------
# 钩子位于 <skill-acceptance>/hooks/pre-release.sh
# skill-acceptance 根 = 上两级
HOOK_PATH=$(cd "$(dirname "$0")" && pwd)
SKILL_ROOT=$(cd "$HOOK_PATH/.." && pwd)
# 项目根 = skill-acceptance 上一级（即 skill-markets/ 的父级，即仓库根）
PROJECT_ROOT=$(cd "$SKILL_ROOT/.." && pwd)

VERIFY_PY="$SKILL_ROOT/scripts/verify.py"
if [ ! -f "$VERIFY_PY" ]; then
    echo "${C_RED}🛑 verify.py 不存在: $VERIFY_PY${C_RESET}" >&2
    echo "${C_RED}   请先实施 scripts/verify.py(本钩子不创建该文件)${C_RESET}" >&2
    exit 3
fi

# ---------- 收集 skill 列表 ----------
if [ -z "$SKILLS" ]; then
    # 扫描 PROJECT_ROOT/skill-markets/ 下所有 skill
    SKILLS_DIR="$PROJECT_ROOT/skill-markets"
    if [ ! -d "$SKILLS_DIR" ]; then
        echo "${C_RED}🛑 skill-markets/ 目录不存在: $SKILLS_DIR${C_RESET}" >&2
        exit 3
    fi
    for d in "$SKILLS_DIR"/*/; do
        [ -d "$d" ] || continue
        name=$(basename "$d")
        SKILLS="$SKILLS $name"
    done
fi

SKILLS=$(echo "$SKILLS" | awk '{$1=$1;print}')
TOTAL=0
PASS_COUNT=0
WARN_COUNT=0
BLOCK_COUNT=0
EXIT_CODE=0

echo "${C_GREEN}==================================================${C_RESET}"
echo "${C_GREEN} skill-acceptance pre-release${C_RESET}"
echo "${C_GREEN} target skills:${C_RESET}$SKILLS"
echo "${C_GREEN}==================================================${C_RESET}"

# ---------- 报告暂存 ----------
REPORT_DIR="$SKILL_ROOT/.reports"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/pre-release-$(date -u +%Y%m%dT%H%M%SZ).json"

# ---------- 逐 skill 调 verify.py ----------
for skill in $SKILLS; do
    TOTAL=$((TOTAL + 1))
    TARGET="$PROJECT_ROOT/skill-markets/$skill"
    echo ""
    echo "${C_GREEN}▶ [$TOTAL] $skill${C_RESET}"

    if [ ! -d "$TARGET" ]; then
        echo "${C_RED}  ✗ 目录不存在: $TARGET${C_RESET}"
        BLOCK_COUNT=$((BLOCK_COUNT + 1))
        EXIT_CODE=1
        continue
    fi

    # 调 verify.py 单一 skill
    set +e
    OUT=$(python3 "$VERIFY_PY" \
        --target "$skill" \
        --json \
        --report "$REPORT_FILE" \
        --project-root "$PROJECT_ROOT" 2>&1)
    RC=$?
    set -e

    # 解析退出码语义（verify.py 退出码 0=PASS / 1/2=WARN / 3+=BLOCK）
    case "$RC" in
        0)
            echo "${C_GREEN}  ✓ PASS${C_RESET}"
            PASS_COUNT=$((PASS_COUNT + 1))
            ;;
        1|2)
            WARN_COUNT=$((WARN_COUNT + 1))
            echo "${C_YELLOW}  ⚠ WARN (exit=$RC)${C_RESET}"
            [ -n "$OUT" ] && echo "$OUT" | sed 's/^/    /'
            ;;
        *)
            BLOCK_COUNT=$((BLOCK_COUNT + 1))
            EXIT_CODE=1
            echo "${C_RED}  ✗ BLOCK (exit=$RC)${C_RESET}"
            [ -n "$OUT" ] && echo "$OUT" | sed 's/^/    /'
            ;;
    esac
done

# ---------- 阈值判断 ----------
if [ "$WARN_COUNT" -ge 3 ] && [ "$FORCE" -eq 0 ]; then
    if [ "$EXIT_CODE" -eq 0 ]; then
        EXIT_CODE=2
    fi
fi
if [ "$FORCE" -eq 1 ] && [ "$EXIT_CODE" -eq 2 ]; then
    echo ""
    echo "${C_YELLOW}⚠ --force:忽略 WARN 阈值警告${C_RESET}"
    EXIT_CODE=0
fi

# ---------- 报告 ----------
echo ""
echo "${C_GREEN}==================================================${C_RESET}"
echo "${C_GREEN} 验收报告${C_RESET}"
printf "  total : %d\n" "$TOTAL"
printf "  ${C_GREEN}PASS${C_RESET}  : %d\n" "$PASS_COUNT"
printf "  ${C_YELLOW}WARN${C_RESET}  : %d\n" "$WARN_COUNT"
printf "  ${C_RED}BLOCK${C_RESET} : %d\n" "$BLOCK_COUNT"
echo "  report: $REPORT_FILE"
echo "${C_GREEN}==================================================${C_RESET}"

exit "$EXIT_CODE"
