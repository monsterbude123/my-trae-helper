#!/usr/bin/env bash
#
# fullstack4TraeV11 V11.8.7 — 跨项目 build cache 顶层脚本(POSIX 版)
#
# 职责:
#   1. 固定 NODE_OPTIONS=--max-old-space-size=8192(防 OOM)
#   2. 关闭 NEXT_TELEMETRY_DISABLED(加速 build)
#   3. 走 next build --turbo(启 Turbopack 缓存,复用 .next/cache)
#
# 详见 references/role-protocol.md §I+ + references/common-anti-patterns.md §22
# 详见 references/config.example.yaml build.* 字段
#
# 用法:
#   bash scripts/build-prod-warmup.sh
#   bash scripts/build-prod-warmup.sh --help
#
# 实测锚点:
#   ai-short-studio-monster 2026-08-18 每次 build 5min + OOM 重跑
#   本脚本启用后预期 5min → 1-2min(缓存命中),OOM 0 次

set -e

# 固定 NODE_OPTIONS(防 OOM)
export NODE_OPTIONS=--max-old-space-size=8192

# 关闭 Next.js telemetry(加速 build + 减少网络请求)
export NEXT_TELEMETRY_DISABLED=1

# 透传参数(支持 --help / 其他 next build 参数)
exec next build --turbo "$@"