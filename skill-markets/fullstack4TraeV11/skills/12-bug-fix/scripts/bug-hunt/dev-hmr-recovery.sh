#!/usr/bin/env bash
# dev-hmr-recovery.sh — HMR stale 4 步恢复（V11.8.2 NEW Stage 6 Phase A）
#
# 跨平台: macOS / Linux / Git Bash on Windows
#
# 用法:
#   bash scripts/bug-hunt/dev-hmr-recovery.sh -DryRun  # 先打印 4 步命令
#   bash scripts/bug-hunt/dev-hmr-recovery.sh          # 真恢复
#
# 反 V11-BH5 反例: 连续 3 次重 navigate 未恢复仍在手动 retry（浪费 5 min/次）。
#
# 4 步:
#   1. kill 占端口 3000/3001 进程
#   2. 删 .next/cache 清除 HMR 缓存
#   3. 杀残留 next-server / worker / watchdog / bull-board
#   4. 重启 npm run dev（detached, log 写 .next/dev.log）

set -euo pipefail

DRY_RUN=false
for arg in "$@"; do
    case "$arg" in
        -DryRun|--dry-run) DRY_RUN=true ;;
        *) echo "[WARN] 未知参数: $arg";;
    esac
done

if [[ "$DRY_RUN" == "true" ]]; then
    echo "[DRYRUN] kill 占端口 3000 / 3001 进程（lsof / fuser）"
    # scan-whitelist:CMD_RM_RF - HMR 恢复必须删 .next/cache（V11.8.2 真实业务必需）
    echo "[DRYRUN] rm -rf .next/cache"
    echo "[DRYRUN] 杀残留 next-server / worker / watchdog / bull-board"
    echo "[DRYRUN] npm run dev（detached, log 写 .next/dev.log）"
    exit 0
fi

# 1. kill 占端口进程
echo "[STEP 1/4] kill 占端口 3000 / 3001 进程"
if command -v lsof > /dev/null 2>&1; then
    lsof -ti:3000 | xargs -r kill -9 2>/dev/null || true
    lsof -ti:3001 | xargs -r kill -9 2>/dev/null || true
elif command -v fuser > /dev/null 2>&1; then
    fuser -k 3000/tcp 2>/dev/null || true
    fuser -k 3001/tcp 2>/dev/null || true
else
    echo "[WARN] lsof / fuser 均无, 跳过端口 kill（Windows Git Bash 常见）"
fi

# 2. 删 .next/cache
echo "[STEP 2/4] rm -rf .next/cache"
rm -rf .next/cache

# 3. 杀残留
echo "[STEP 3/4] 杀残留 next-server / worker / watchdog / bull-board"
pkill -f "next-server" 2>/dev/null || true
pkill -f "tsx watch" 2>/dev/null || true
pkill -f "bull-board" 2>/dev/null || true

# 4. 重启 dev server
echo "[STEP 4/4] npm run dev（detached, log 写 .next/dev.log）"
mkdir -p .next
nohup npm run dev > .next/dev.log 2>&1 &
echo "[OK] dev server 启动中, 等 Ready 输出: tail -f .next/dev.log"

# 5. 等 Ready
echo "[WAIT] 轮询 dev server Ready（最多 30s）"
for i in $(seq 1 30); do
    if grep -q "✓ Ready in" .next/dev.log 2>/dev/null; then
        echo "[OK] dev server Ready"
        exit 0
    fi
    sleep 1
done

echo "[WARN] 30s 内未检测到 Ready 输出, 请手动检查: tail -f .next/dev.log"
exit 1