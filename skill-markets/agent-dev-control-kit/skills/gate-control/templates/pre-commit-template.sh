#!/bin/bash

# L1 提交前门禁脚本（opt-in 模板）
# 用法: .husky/pre-commit
#
# 默认行为（保持与 husky fullstack 会话一致，避免分钟级延迟）：
#   - [1/4] Lint       — 强制跑
#   - [2/4] TypeCheck  — 强制跑
#   - [3/4] 单元测试   — 默认跳过；RUN_UNIT_TESTS_ON_COMMIT=1 时启用
#   - [4/4] 格式化检查 — 默认跳过；RUN_FORMAT_CHECK_ON_COMMIT=1 时启用
#
# 任何一步可用 `exit 1` 直接拦截提交，由调用方按需删除。

set -euo pipefail

echo "=== L1 提交前门禁 ==="

# 1. Lint 检查
echo "[1/4] Lint 检查..."
if ! npm run lint; then
    echo "❌ Lint 检查失败"
    exit 1
fi
echo "✅ Lint 通过"

# 2. TypeCheck 检查
echo "[2/4] TypeCheck 检查..."
if ! npm run typecheck; then
    echo "❌ TypeCheck 检查失败"
    exit 1
fi
echo "✅ TypeCheck 通过"

# 3. 单元测试（opt-in，默认跳过）
if [ "${RUN_UNIT_TESTS_ON_COMMIT:-0}" = "1" ]; then
    echo "[3/4] 单元测试..."
    if ! npm run test:unit; then
        echo "❌ 单元测试失败"
        exit 1
    fi
    echo "✅ 单元测试通过"
else
    echo "[3/4] 单元测试 — 跳过（设置 RUN_UNIT_TESTS_ON_COMMIT=1 启用）"
fi

# 4. 格式化检查（opt-in，默认跳过）
if [ "${RUN_FORMAT_CHECK_ON_COMMIT:-0}" = "1" ]; then
    echo "[4/4] 格式化检查..."
    if ! npm run format:check; then
        echo "❌ 格式化检查失败"
        echo "💡 尝试运行: npm run format:write"
        exit 1
    fi
    echo "✅ 格式化检查通过"
else
    echo "[4/4] 格式化检查 — 跳过（设置 RUN_FORMAT_CHECK_ON_COMMIT=1 启用）"
fi

echo ""
echo "=== L1 门禁全部通过 ==="
