#!/usr/bin/env bash
# archive-screenshot.sh — Playwright 截图归档脚本（V11.8.2 NEW Stage 6 Phase A，bash 跨平台）
#
# 用法:
#   bash scripts/bug-hunt/archive-screenshot.sh -Slug "BUG-017-fixed" -SubDir "bug-hunt"
#   bash scripts/bug-hunt/archive-screenshot.sh -Slug "BUG-017-fixed" -SubDir "bug-hunt" -DryRun
#
# 产物: docs/evidence/<YYYY-MM-DD>/<SubDir>/<Slug>.png
#
# 反 V11 §3.7 #2 反例: 手动 Copy-Item 7 次 → 归档脚本化。

set -euo pipefail

SLUG=""
SUBDIR="bug-hunt"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -Slug)    SLUG="$2"; shift 2;;
        -SubDir)  SUBDIR="$2"; shift 2;;
        -DryRun|--dry-run) DRY_RUN=true; shift;;
        *) echo "[WARN] 未知参数: $1"; shift;;
    esac
done

if [[ -z "$SLUG" ]]; then
    echo "[FATAL] 用法: bash $0 -Slug <slug> [-SubDir bug-hunt] [-DryRun]" >&2
    exit 1
fi

# 日期目录
DATE_DIR=$(TZ=Asia/Shanghai date +"%Y-%m-%d")
OUT_DIR="docs/evidence/${DATE_DIR}/${SUBDIR}"
OUT_FILE="${OUT_DIR}/${SLUG}.png"

# 查找 Downloads 下最近的 screenshot
DOWNLOADS="${HOME}/Downloads"
SCREENSHOT_FILE=""

if [[ -d "$DOWNLOADS" ]]; then
    # 找最新的 screenshot-*.png
    SCREENSHOT_FILE=$(ls -t "$DOWNLOADS"/screenshot-*.png 2>/dev/null | head -n 1 || true)
fi

if [[ -z "$SCREENSHOT_FILE" ]]; then
    echo "[FATAL] Downloads 下未找到 screenshot-*.png（先跑 playwright_screenshot）" >&2
    exit 1
fi

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRYRUN] mkdir -p $OUT_DIR"
    echo "[DRYRUN] cp $SCREENSHOT_FILE $OUT_FILE"
    echo "[DRYRUN] rm $SCREENSHOT_FILE"
    exit 0
fi

mkdir -p "$OUT_DIR"
cp "$SCREENSHOT_FILE" "$OUT_FILE"
rm "$SCREENSHOT_FILE"

echo "[OK] 归档: $SCREENSHOT_FILE → $OUT_FILE"